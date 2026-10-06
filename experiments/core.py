"""Repeated game, metric aggregation and experiment runners shared by both case studies
(protocol sections 5-8).

`simulate` plays the repeated game for one system on a prepared set of rounds;
systems sharing a seed share the prepared rounds exactly, which gives the paired design.
"""
import json

import numpy as np

from evaluation.metrics import collective_decision, consistency, contributions
from experiments import register
from game.strategies import FALSIFIED, STRATEGIES, choose_report, collusive_vote
from incentives.mechanism import (ATTACKS, manipulation_components, manipulation_score,
                                  reward, utility, validate_weights)
from reputation.reputation import initial_reputation, update_reputation


def _malicious_count(rng, fraction, n_agents):
    expected = n_agents * fraction
    base = int(np.floor(expected + 1e-9))
    remainder = expected - base
    return base + int(remainder > 1e-9 and rng.random() < remainder)


def simulate(prep, system, seed, policy="adaptive", malicious_fraction=0.0, colluders=None):
    """Play the repeated game.

    policy: "adaptive" (epsilon-greedy bandits) or a list of one fixed strategy per agent.
    malicious_fraction: expected share of agents forced to play manipulative each round.
    colluders: optional pair of agent indices that vote jointly (protocol section 8).
    """
    game = prep["game"]
    weights = validate_weights(system["incentive_weights"])
    use_reputation = bool(system["components"].get("reputation"))
    rep_cfg = system.get("reputation", {})
    rho, omega = rep_cfg.get("rho", 0.8), game["omega"]
    degenerate = system.get("reward", {}).get("degenerate_value", 0.5)
    T = len(prep["reference"])
    n_agents, n_actions = prep["proba"].shape[1:]

    rng = np.random.default_rng([seed, 2])
    order = np.random.default_rng([seed, 3]).permutation(n_agents)
    q_values = np.full((n_agents, len(STRATEGIES)), float(game["q_init"]))
    reputation = initial_reputation(n_agents, rep_cfg.get("initial", 0.5))

    log = {key: np.zeros((T, n_agents)) for key in
           ("F", "E", "D", "C", "M", "U", "R", "payoff", "private", "strategy", "malicious",
            "deviates", "reputation", *ATTACKS)}
    collective = np.zeros(T, dtype=int)
    reported = [[None] * n_agents for _ in range(T)]

    for t in range(T):
        proba, util, pref = prep["proba"][t], prep["utilities"][t], prep["preferred"][t]
        malicious = np.zeros(n_agents, dtype=bool)
        malicious[order[:_malicious_count(rng, malicious_fraction, n_agents)]] = True
        strategies = np.zeros(n_agents, dtype=int)
        for i in range(n_agents):
            if malicious[i]:
                strategies[i] = STRATEGIES.index("manipulative")
            elif policy == "adaptive":
                if rng.random() < game["epsilon"]:
                    strategies[i] = rng.integers(len(STRATEGIES))
                else:
                    best = np.flatnonzero(q_values[i] == q_values[i].max())
                    strategies[i] = rng.choice(best)
            else:
                strategies[i] = STRATEGIES.index(policy[i])

        votes = np.zeros(n_agents, dtype=int)
        conf, F, E = np.zeros(n_agents), np.zeros(n_agents), np.zeros(n_agents)
        for i in range(n_agents):
            vote, confidence, style = choose_report(
                STRATEGIES[strategies[i]], proba[i], pref[i], util[i],
                game["deviation_threshold"], game["inflation"])
            if colluders is not None and i in colluders:
                a, b = colluders
                vote, confidence, style = collusive_vote(util[a], util[b]), 1.0, FALSIFIED
            votes[i], conf[i] = vote, confidence
            F[i] = prep["quality"][style]["F"][t, i, vote]
            E[i] = prep["quality"][style]["E"][t, i, vote]
            reported[t][i] = prep["explanations"][style][t][i][vote]

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

        if policy == "adaptive":
            learners = np.flatnonzero(~malicious)
            q_values[learners, strategies[learners]] += game["learning_rate"] * (
                payoff[learners] - q_values[learners, strategies[learners]])
        log["reputation"][t] = reputation
        if use_reputation:
            reputation = update_reputation(reputation, R, rho)

        collective[t] = decision
        for key, value in (("F", F), ("E", E), ("D", D), ("C", C), ("M", M), ("U", U), ("R", R),
                           ("payoff", payoff), ("private", private), ("strategy", strategies),
                           ("malicious", malicious), ("deviates", votes != model_votes)):
            log[key][t] = value
        for attack in ATTACKS:
            log[attack][t] = components[attack]
        log.setdefault("votes", np.zeros((T, n_agents), dtype=int))[t] = votes

    log["collective"] = collective
    log["reported"] = reported
    log["final_reputation"] = reputation if use_reputation else None
    return log


def _voted_view(view, votes):
    """Feature view per round; a per-action view (rounds, actions, features) is reduced to
    the row of the action the agent voted for."""
    view = np.asarray(view)
    return view if view.ndim == 2 else view[np.arange(len(view)), votes]


def summarise(prep, log, window=None):
    """Aggregate a simulation log over the evaluation window (default: last `eval_last`)."""
    T = len(prep["reference"])
    n_agents, n_actions = prep["proba"].shape[1:]
    window = window if window is not None else slice(T - prep["game"]["eval_last"], T)
    ref, collective = prep["reference"][window], log["collective"][window]
    wrong = collective != ref
    steered = (log["deviates"][window].astype(bool)
               & (log["votes"][window] == collective[:, None])).any(axis=1)
    strategies = log["strategy"][window].astype(int)
    honest_mask = ~log["malicious"][window].astype(bool)
    idx = np.arange(T)[window]
    per_agent_consistency = [
        consistency(_voted_view(prep["views"][i], log["votes"][:, i])[idx],
                    [log["reported"][t][i] for t in idx],
                    prep["game"]["consistency_neighbours"]) for i in range(n_agents)]

    def mean(key, mask=None):
        values = log[key][window]
        return float(values.mean() if mask is None else values[mask].mean()) if (
            mask is None or mask.any()) else float("nan")

    out = {
        "fidelity": mean("F"), "evidence_support": mean("E"), "manipulation": mean("M"),
        "decision_quality": mean("D"), "contribution": mean("C"), "utility": mean("U"),
        "reward": mean("R"), "payoff": mean("payoff"),
        "collective_utility": mean("private"),
        "collective_accuracy": float((collective == ref).mean()),
        "manipulation_success": float((wrong & steered).mean()),
        "consistency": float(np.mean(per_agent_consistency)),
        "fidelity_non_malicious": mean("F", honest_mask),
        "evidence_support_non_malicious": mean("E", honest_mask),
        "manipulation_non_malicious": mean("M", honest_mask),
        "strategy_share": {s: float((strategies[honest_mask] == j).mean()) if honest_mask.any()
                           else float("nan") for j, s in enumerate(STRATEGIES)},
        "attack_scores": {a: mean(a) for a in ATTACKS},
        "collective_action_share": {prep["actions"][a]: float((collective == a).mean())
                                    for a in range(n_actions)},
        "per_agent": {name: {"fidelity": float(log["F"][window][:, i].mean()),
                             "evidence_support": float(log["E"][window][:, i].mean()),
                             "manipulation": float(log["M"][window][:, i].mean()),
                             "reward": float(log["R"][window][:, i].mean()),
                             "private_utility": float(log["private"][window][:, i].mean()),
                             "payoff": float(log["payoff"][window][:, i].mean()),
                             "consistency": per_agent_consistency[i],
                             "final_reputation": (None if log["final_reputation"] is None
                                                  else float(log["final_reputation"][i]))}
                      for i, name in enumerate(prep["agents"])},
    }
    return out


def deviation_table(prep, system, seed):
    """Mean payoff of each agent under each of its strategies when the other four
    agents are honest (all rounds). Secondary analysis, protocol section 7."""
    everything = slice(0, len(prep["reference"]))
    n_agents = prep["proba"].shape[1]
    table = {}
    for i, name in enumerate(prep["agents"]):
        table[name] = {}
        for strategy in STRATEGIES:
            policy = ["honest"] * n_agents
            policy[i] = strategy
            log = simulate(prep, system, seed, policy=policy)
            table[name][strategy] = float(log["payoff"][everything][:, i].mean())
    return table


def _apply_parameter(prep, system, parameter, value):
    """Return (prep, system) with one sensitivity parameter overridden."""
    section, key = parameter.split(".")
    system = json.loads(json.dumps(system))
    if section == "game":
        prep = {**prep, "game": {**prep["game"], key: value}}
    elif section == "reputation":
        system.setdefault("reputation", {})[key] = value
    elif section == "incentive_weights":
        if system["components"].get("explanation_aware_incentive"):
            weights = system["incentive_weights"]
            scale = (sum(weights.values()) - value) / (sum(weights.values()) - weights[key])
            system["incentive_weights"] = {k: (value if k == key else w * scale)
                                           for k, w in weights.items()}
    else:
        raise ValueError(f"unknown sensitivity parameter {parameter!r}")
    return prep, system


def register_domain(domain, prepare):
    """Register the main, adversarial and sensitivity experiments of one case study.

    `prepare(config, seed)` builds everything that depends only on data and seed; see
    experiments/energy.py for the keys it must return.
    """

    def run_main(config, seed):
        prep = prepare(config, seed)
        log = simulate(prep, config, seed)
        return {"seed": seed, "system": config["system"], "n_rounds": len(prep["reference"]),
                "eval_last": prep["game"]["eval_last"], "model_val_accuracy": prep["val_accuracy"],
                "metrics": summarise(prep, log),
                "unilateral_deviation_payoff": deviation_table(prep, config, seed)}

    def run_adversarial(config, seed):
        prep = prepare(config, seed)
        agents, n_agents = prep["agents"], len(prep["agents"])
        adversarial = config["adversarial"]
        pair = tuple(int(i) for i in np.random.default_rng([seed, 4]).permutation(n_agents)[:2])
        everything = slice(0, len(prep["reference"]))
        out = {"seed": seed, "colluders": [agents[i] for i in pair], "systems": {}}
        for name, system in config["systems"].items():
            by_fraction = {
                str(p): summarise(prep, simulate(prep, system, seed, malicious_fraction=p))
                for p in adversarial["malicious_fractions"]}
            honest = ["honest"] * n_agents
            out["systems"][name] = {
                "malicious": by_fraction,
                "collusion": {
                    "without": summarise(prep, simulate(prep, system, seed, policy=honest),
                                         everything),
                    "with": summarise(prep, simulate(prep, system, seed, policy=honest,
                                                     colluders=pair), everything)}}
        return out

    def run_sensitivity(config, seed):
        """One-at-a-time sensitivity: rerun the systems with one parameter varied."""
        base_prep = prepare(config, seed)
        parameter = config["sensitivity"]["parameter"]
        out = {"seed": seed, "parameter": parameter, "values": {}}
        for value in config["sensitivity"]["values"]:
            out["values"][str(value)] = {}
            for name, base_system in config["systems"].items():
                prep, system = _apply_parameter(base_prep, base_system, parameter, value)
                out["values"][str(value)][name] = {
                    "metrics": summarise(prep, simulate(prep, system, seed)),
                    "unilateral_deviation_payoff": deviation_table(prep, system, seed),
                    "incentive_weights": system["incentive_weights"]}
        return out

    for system in ("baseline", "ablation", "proposed"):
        register(f"{domain}_{system}")(run_main)
    register(f"{domain}_adversarial")(run_adversarial)
    register(f"{domain}_sensitivity")(run_sensitivity)
