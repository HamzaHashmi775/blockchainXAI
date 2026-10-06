"""Repeated game played by LLM agents.

Same rounds, collective decision rule, audit, utility, reward and reputation as
experiments/core.py; the only difference is where a report comes from. `client` is any
object with `chat(messages, schema, seed) -> {"text": ...}` (agents/llm_agent.OllamaClient,
or a stub in tests).
"""
from collections import deque

import numpy as np

from agents.llm_agent import parse_report, report_schema, round_prompt, system_prompt
from evaluation.metrics import (collective_decision, contributions, evidence_support, fidelity,
                                observed_level)
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


def simulate_llm(prep, system, seed, client, domain, n_rounds=None):
    """Play `n_rounds` (default: all prepared rounds). Returns (log, call records)."""
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

    reputation = initial_reputation(n_agents, rep_cfg.get("initial", 0.5))
    prompts = [system_prompt(domain, name, system, omega) for name in agents]
    schemas = [report_schema(actions, prep["audit"][i]["features"]) for i in range(n_agents)]
    history = [deque(maxlen=HISTORY_LENGTH) for _ in range(n_agents)]
    log = {key: np.zeros((T, n_agents)) for key in
           ("F", "E", "D", "C", "M", "U", "R", "payoff", "private", "confidence", "deviates",
            "votes_preferred", "invalid", "reputation", *ATTACKS)}
    log["votes"] = np.zeros((T, n_agents), dtype=int)
    collective, records = np.zeros(T, dtype=int), []

    for t in range(T):
        proba, util = prep["proba"][t], prep["utilities"][t]
        votes = np.zeros(n_agents, dtype=int)
        conf, F, E = np.zeros(n_agents), np.zeros(n_agents), np.zeros(n_agents)
        invalid = np.zeros(n_agents)
        for i in range(n_agents):
            audit = prep["audit"][i]
            phi, x, thresholds = audit["phi"][t], audit["X"][t], audit["thresholds"]
            messages = [{"role": "system", "content": prompts[i]},
                        {"role": "user", "content": round_prompt(
                            t + 1, actions, audit["features"], util[i], proba[i], phi, x,
                            thresholds, history[i])}]
            report = None
            for attempt in range(MAX_ATTEMPTS):
                reply = client.chat(messages, schemas[i], seed * 1000 + attempt)
                report = parse_report(reply["text"], actions, audit["features"])
                records.append({"round": t, "agent": agents[i], "attempt": attempt,
                                "valid": report is not None, **reply})
                if report is not None:
                    break
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
    votes = log["votes"][window]
    return {
        "n_rounds": int(len(collective)),
        "fidelity": mean("F"), "evidence_support": mean("E"), "manipulation": mean("M"),
        "decision_quality": mean("D"), "reward": mean("R"), "payoff": mean("payoff"),
        "collective_utility": mean("private"),
        "collective_accuracy": float((collective == ref).mean()),
        "manipulation_success": float((wrong & steered).mean()),
        "attack_scores": {a: mean(a) for a in ATTACKS},
        "behaviour": {
            "votes_against_tool": mean("deviates"),
            "votes_own_preferred_option": mean("votes_preferred"),
            "fully_truthful_explanation": float((log["F"][window] == 1.0).mean()),
            "fully_supported_evidence": float((log["E"][window] == 1.0).mean()),
            "mean_confidence": mean("confidence"),
        },
        "vote_share": {prep["actions"][a]: float((votes == a).mean())
                       for a in range(prep["proba"].shape[2])},
        "calls": {"total": len(records),
                  "unusable_replies": int(sum(not r["valid"] for r in records)),
                  "reports_replaced_by_tool_report": int(log["invalid"][window].sum()),
                  "mean_seconds": float(np.mean(seconds)) if seconds else None,
                  "median_seconds": float(np.median(seconds)) if seconds else None},
        "per_agent": {name: {"fidelity": float(log["F"][window][:, i].mean()),
                             "evidence_support": float(log["E"][window][:, i].mean()),
                             "votes_against_tool": float(log["deviates"][window][:, i].mean()),
                             "payoff": float(log["payoff"][window][:, i].mean())}
                      for i, name in enumerate(prep["agents"])},
    }
