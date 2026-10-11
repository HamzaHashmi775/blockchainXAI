"""Repeated game played by LLM agents.

Same rounds, collective decision rule, audit, utility, reward and reputation as
experiments/core.py; the only difference is where a report comes from. `client` is any
object with `chat(messages, schema, seed) -> {"text": ...}` (agents/llm_agent.OllamaClient,
or a stub in tests).
"""
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from agents.llm_agent import parse_report, report_schema, round_prompt, system_prompt
from evaluation.metrics import (collective_decision, contributions, evidence_support, fidelity,
                                observed_level)
from game.strategies import FALSIFIED, choose_report, collusive_vote
from incentives.mechanism import (ATTACKS, manipulation_components, manipulation_score, reward,
                                  utility, validate_weights)
from reputation.reputation import initial_reputation, update_reputation
from xai.shap_explainer import top_k_features

HISTORY_LENGTH = 3
MAX_ATTEMPTS = 2


def honest_report(proba, phi, x, thresholds, k):
    """The report the analysis tool itself supports; used only when a reply is unusable."""
    vote = int(np.argmax(proba))
    top = top_k_features(phi[vote], k)
    explanation = [(int(f), int(np.sign(phi[vote, f]))) for f in top]
    claims = [(int(f), observed_level(x[vote, f], thresholds[0, f], thresholds[1, f]))
              for f in top]
    return vote, float(proba[vote]), explanation, claims


def _history_line(round_number, actions, vote, model_vote, decision, F, E, R, payoff, audited):
    line = (f"round {round_number}: you voted {actions[vote]} (tool's top: "
            f"{actions[model_vote]}), group chose {actions[decision]}, ")
    if audited:
        line += f"explanation check {F:.2f}, evidence check {E:.2f}, "
    return line + f"reward {R:.2f}, payoff {payoff:.2f}"


def _ask(client, messages, schema, seed, actions, features):
    """One agent's report for one round: (report or None, call records)."""
    calls = []
    for attempt in range(MAX_ATTEMPTS):
        reply = client.chat(messages, schema, seed * 1000 + attempt)
        report = parse_report(reply["text"], actions, features)
        calls.append({"attempt": attempt, "valid": report is not None, **reply})
        if report is not None:
            return report, calls
    return None, calls


def simulate_llm(prep, system, seed, client, domain, n_rounds=None, workers=1,
                 malicious=(), colluders=None, prompt_style="disclosed"):
    """Play `n_rounds` (default: all prepared rounds). Returns (log, call records).

    Agents report simultaneously, so with `workers` > 1 the requests of a round are sent
    concurrently; results are always stored in agent order.
    malicious: indices of agents that are scripted *manipulative* agents (protocol A3.2).
    colluders: optional pair of indices that are scripted colluders. Scripted agents make
    no model call; every other agent is an LLM agent.
    """
    game = prep["game"]
    weights = validate_weights(system["incentive_weights"])
    audited = bool(system["components"].get("explanation_aware_incentive"))
    use_reputation = bool(system["components"].get("reputation"))
    rep_cfg = system.get("reputation", {})
    rho, omega, k = rep_cfg.get("rho", 0.8), game["omega"], game["top_k"]
    degenerate = system.get("reward", {}).get("degenerate_value", 0.5)
    agents, actions = prep["agents"], prep["actions"]
    n_agents, n_actions = prep["proba"].shape[1:]
    T = len(prep["reference"]) if n_rounds is None else int(n_rounds)
    scripted = set(int(i) for i in malicious) | set(int(i) for i in (colluders or ()))

    reputation = initial_reputation(n_agents, rep_cfg.get("initial", 0.5))
    prompts = [system_prompt(domain, name, system, omega, prompt_style) for name in agents]
    schemas = [report_schema(actions, prep["audit"][i]["features"]) for i in range(n_agents)]
    history = [deque(maxlen=HISTORY_LENGTH) for _ in range(n_agents)]
    log = {key: np.zeros((T, n_agents)) for key in
           ("F", "E", "D", "C", "M", "U", "R", "payoff", "private", "confidence", "deviates",
            "votes_preferred", "invalid", "reputation", "scripted", *ATTACKS)}
    log["scripted"][:, sorted(scripted)] = 1.0
    log["votes"] = np.zeros((T, n_agents), dtype=int)
    collective, records = np.zeros(T, dtype=int), []

    for t in range(T):
        proba, util = prep["proba"][t], prep["utilities"][t]
        votes = np.zeros(n_agents, dtype=int)
        conf, F, E = np.zeros(n_agents), np.zeros(n_agents), np.zeros(n_agents)
        invalid = np.zeros(n_agents)
        requests, asked = [], []
        for i in range(n_agents):
            if i in scripted:
                pref = prep["preferred"][t, i]
                vote, confidence, style = choose_report(
                    "manipulative", proba[i], pref, util[i], game["deviation_threshold"],
                    game["inflation"])
                if colluders is not None and i in colluders:
                    a, b = colluders
                    vote, confidence, style = collusive_vote(util[a], util[b]), 1.0, FALSIFIED
                votes[i], conf[i] = vote, confidence
                F[i] = prep["quality"][style]["F"][t, i, vote]
                E[i] = prep["quality"][style]["E"][t, i, vote]
                continue
            asked.append(i)
            audit = prep["audit"][i]
            messages = [{"role": "system", "content": prompts[i]},
                        {"role": "user", "content": round_prompt(
                            t + 1, actions, audit["features"], util[i], proba[i],
                            audit["phi"][t], audit["X"][t], audit["thresholds"], history[i],
                            prompt_style)}]
            requests.append((client, messages, schemas[i], seed, actions, audit["features"]))
        if workers > 1 and requests:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                answers = list(pool.map(lambda r: _ask(*r), requests))
        else:
            answers = [_ask(*r) for r in requests]
        for n, (i, (report, calls)) in enumerate(zip(asked, answers)):
            audit = prep["audit"][i]
            phi, x, thresholds = audit["phi"][t], audit["X"][t], audit["thresholds"]
            records.extend({"round": t, "agent": agents[i], **call} for call in calls)
            if t == 0:
                records[-1]["prompt"] = requests[n][1][1]["content"]
            if report is None:
                invalid[i] = 1.0
                report = honest_report(proba[i], phi, x, thresholds, k)
            votes[i], conf[i], explanation, claims = report
            F[i] = fidelity(explanation, phi[votes[i]], k)
            E[i] = evidence_support(claims, x[votes[i]], thresholds)

        model_votes = proba.argmax(axis=1)
        vote_weights = reputation if use_reputation else np.ones(n_agents)
        decision = collective_decision(votes, conf, vote_weights, n_actions)
        ref = prep["reference"][t]
        D = (votes == ref).astype(float)
        C = contributions(votes, conf, vote_weights, n_actions, ref)
        components = manipulation_components(F, E, conf, proba[np.arange(n_agents), votes],
                                             votes, model_votes)
        M = manipulation_score(components)
        U = utility(D, F, E, C, M, weights)
        R = reward(U, degenerate)
        private = util[np.arange(n_agents), decision]
        payoff = omega * private + (1.0 - omega) * R

        log["reputation"][t] = reputation
        if use_reputation:
            reputation = update_reputation(reputation, R, rho)
        collective[t] = decision
        log["votes"][t] = votes
        for key, value in (("F", F), ("E", E), ("D", D), ("C", C), ("M", M), ("U", U), ("R", R),
                           ("payoff", payoff), ("private", private), ("confidence", conf),
                           ("deviates", votes != model_votes), ("invalid", invalid),
                           ("votes_preferred", votes == prep["preferred"][t])):
            log[key][t] = value
        for attack in ATTACKS:
            log[attack][t] = components[attack]
        for i in range(n_agents):
            history[i].append(_history_line(t + 1, actions, votes[i], model_votes[i], decision,
                                            F[i], E[i], R[i], payoff[i], audited))

    log["collective"] = collective
    log["final_reputation"] = reputation if use_reputation else None
    return log, records


def _share(values, mask):
    return float(values[mask].mean()) if mask.any() else None


def summarise_llm(prep, log, records, window=None):
    T = len(log["collective"])
    window = window if window is not None else slice(0, T)
    ref, collective = prep["reference"][:T][window], log["collective"][window]
    wrong = collective != ref
    steered = (log["deviates"][window].astype(bool)
               & (log["votes"][window] == collective[:, None])).any(axis=1)

    def mean(key):
        return float(log[key][window].mean())

    seconds = [r["seconds"] for r in records if r.get("seconds") is not None]
    prompt_tokens = [r["prompt_tokens"] for r in records if r.get("prompt_tokens") is not None]
    votes = log["votes"][window]
    llm = ~log["scripted"][window].astype(bool)

    def llm_mean(key):
        return _share(log[key][window].astype(float), llm)

    return {
        "n_rounds": int(len(collective)),
        "fidelity": mean("F"), "evidence_support": mean("E"), "manipulation": mean("M"),
        "decision_quality": mean("D"), "reward": mean("R"), "payoff": mean("payoff"),
        "collective_utility": mean("private"),
        "collective_accuracy": float((collective == ref).mean()),
        "manipulation_success": float((wrong & steered).mean()),
        "attack_scores": {a: mean(a) for a in ATTACKS},
        # the same quantities over LLM agents only (differs when some agents are scripted)
        "llm_agents": {"fidelity": llm_mean("F"), "evidence_support": llm_mean("E"),
                       "manipulation": llm_mean("M"), "reward": llm_mean("R"),
                       "payoff": llm_mean("payoff")},
        "scripted_agents": {"reward": _share(log["R"][window], ~llm),
                            "payoff": _share(log["payoff"][window], ~llm),
                            "private_utility": _share(log["private"][window], ~llm),
                            "final_reputation": (
                                None if log["final_reputation"] is None or llm.all() else float(
                                    log["final_reputation"][~llm[0]].mean()))},
        "behaviour": {
            "votes_against_tool": llm_mean("deviates"),
            "votes_own_preferred_option": llm_mean("votes_preferred"),
            "fully_truthful_explanation": _share(log["F"][window] == 1.0, llm),
            "fully_supported_evidence": _share(log["E"][window] == 1.0, llm),
            "confidence_inflation": llm_mean("confidence_inflation"),
            # reading check: a report that follows the tool's vote has nothing to gain from
            # a wrong explanation, so a low value here means the model misreads its tool
            "truthful_explanation_when_voting_with_tool": _share(
                log["F"][window] == 1.0, ~log["deviates"][window].astype(bool) & llm),
            "mean_confidence": llm_mean("confidence"),
        },
        "vote_share": {prep["actions"][a]: float((votes[llm] == a).mean())
                       for a in range(prep["proba"].shape[2])},
        "calls": {"total": len(records),
                  "unusable_replies": int(sum(not r["valid"] for r in records)),
                  "reports_replaced_by_tool_report": int(log["invalid"][window].sum()),
                  "max_prompt_tokens": int(max(prompt_tokens)) if prompt_tokens else None,
                  "mean_seconds": float(np.mean(seconds)) if seconds else None,
                  "median_seconds": float(np.median(seconds)) if seconds else None},
        "per_agent": {name: {"fidelity": float(log["F"][window][:, i].mean()),
                             "evidence_support": float(log["E"][window][:, i].mean()),
                             "votes_against_tool": float(log["deviates"][window][:, i].mean()),
                             "payoff": float(log["payoff"][window][:, i].mean())}
                      for i, name in enumerate(prep["agents"])},
    }
