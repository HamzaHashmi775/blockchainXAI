"""Energy case-study experiments (protocol sections 5-8).

`prepare` builds everything that depends only on the data and the seed (models,
sampled rounds, SHAP, per-class explanation quality). `simulate` plays the
repeated game for one system. Systems sharing a seed share `prepare` exactly,
which gives the paired design.
"""
import functools
import json

import numpy as np

from agents.energy_agents import AGENTS, N_ACTIONS, private_utilities, train_agents
from environments.energy.preprocess import ACTIONS, build_scenarios
from evaluation.metrics import (collective_decision, consistency, contributions,
                                evidence_support, fidelity, tercile_thresholds)
from experiments import register
from game.strategies import (FALSIFIED, STRATEGIES, TRUTHFUL, choose_report, collusive_vote,
                             falsified_explanation, truthful_evidence, truthful_explanation,
                             unsupported_evidence)
from incentives.mechanism import (ATTACKS, manipulation_components, manipulation_score,
                                  reward, utility, validate_weights)
from reputation.reputation import initial_reputation, update_reputation
from xai.shap_explainer import shap_values

N_AGENTS = len(AGENTS)
STYLES = (TRUTHFUL, FALSIFIED)
GAME_DEFAULTS = {"n_rounds": 1000, "eval_last": 500, "top_k": 2, "deviation_threshold": 0.25,
                 "inflation": 0.3, "epsilon": 0.1, "learning_rate": 0.1, "q_init": 0.5,
                 "omega": 0.5, "consistency_neighbours": 5}


@functools.lru_cache(maxsize=4)
def _scenarios(reference_json):
    return build_scenarios(json.loads(reference_json))


def prepare(config, seed):
    game = {**GAME_DEFAULTS, **config.get("game", {})}
    df, battery = _scenarios(json.dumps(config.get("reference", {}), sort_keys=True))
    train, val = df[df["split"] == "train"], df[df["split"] == "val"]
    test = df[df["split"] == "test"]
    agents = train_agents(train, seed, **config.get("model", {}))

    rng = np.random.default_rng([seed, 1])
    chosen = np.sort(rng.choice(len(test), size=game["n_rounds"], replace=False))
    rounds = test.iloc[chosen]
    T, k = len(rounds), game["top_k"]

    util = private_utilities(rounds, battery["power"])            # (T, agents, actions)
    proba = np.zeros((T, N_AGENTS, N_ACTIONS))
    quality = {s: {"F": np.zeros((T, N_AGENTS, N_ACTIONS)), "E": np.zeros((T, N_AGENTS, N_ACTIONS))}
               for s in STYLES}
    explanations = {s: [[[None] * N_ACTIONS for _ in range(N_AGENTS)] for _ in range(T)]
                    for s in STYLES}
    views, val_accuracy = [], {}
    for i, name in enumerate(AGENTS):
        agent = agents[name]
        X = rounds[agent.features].to_numpy()
        train_X = train[agent.features].to_numpy()
        thresholds = tercile_thresholds(train_X)
        proba[:, i, :] = agent.predict_proba(rounds)
        phi, _ = shap_values(agent.model, X)                      # (T, features, actions)
        sd = train_X.std(axis=0)
        views.append((X - train_X.mean(axis=0)) / np.where(sd > 0, sd, 1.0))
        val_accuracy[name] = float((agent.predict(val) == val["reference_action"]).mean())
        for t in range(T):
            for c in range(N_ACTIONS):
                truthful = truthful_explanation(phi[t, :, c], k)
                falsified = falsified_explanation(phi[t, :, c], k)
                reports = {TRUTHFUL: (truthful, truthful_evidence(truthful, X[t], thresholds)),
                           FALSIFIED: (falsified, unsupported_evidence(falsified, X[t], thresholds))}
                for style, (explanation, claims) in reports.items():
                    quality[style]["F"][t, i, c] = fidelity(explanation, phi[t, :, c], k)
                    quality[style]["E"][t, i, c] = evidence_support(claims, X[t], thresholds)
                    explanations[style][t][i][c] = frozenset(explanation)
    return {"game": game, "battery": battery, "hours": rounds["Hour"].to_numpy(),
            "reference": rounds["reference_action"].to_numpy(), "utilities": util,
            "preferred": util.argmax(axis=-1), "proba": proba, "quality": quality,
            "explanations": explanations, "views": views, "val_accuracy": val_accuracy}


def _malicious_count(rng, fraction):
    expected = N_AGENTS * fraction
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

    rng = np.random.default_rng([seed, 2])
    order = np.random.default_rng([seed, 3]).permutation(N_AGENTS)
    q_values = np.full((N_AGENTS, len(STRATEGIES)), float(game["q_init"]))
    reputation = initial_reputation(N_AGENTS, rep_cfg.get("initial", 0.5))

    log = {key: np.zeros((T, N_AGENTS)) for key in
           ("F", "E", "D", "C", "M", "U", "R", "payoff", "private", "strategy", "malicious",
            "deviates", "reputation", *ATTACKS)}
    collective = np.zeros(T, dtype=int)
    reported = [[None] * N_AGENTS for _ in range(T)]

    for t in range(T):
        proba, util, pref = prep["proba"][t], prep["utilities"][t], prep["preferred"][t]
        malicious = np.zeros(N_AGENTS, dtype=bool)
        malicious[order[:_malicious_count(rng, malicious_fraction)]] = True
        strategies = np.zeros(N_AGENTS, dtype=int)
        for i in range(N_AGENTS):
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

        votes = np.zeros(N_AGENTS, dtype=int)
        conf, F, E = np.zeros(N_AGENTS), np.zeros(N_AGENTS), np.zeros(N_AGENTS)
        for i in range(N_AGENTS):
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
        vote_weights = reputation if use_reputation else np.ones(N_AGENTS)
        decision = collective_decision(votes, conf, vote_weights, N_ACTIONS)
        ref = prep["reference"][t]
        D = (votes == ref).astype(float)
        C = contributions(votes, conf, vote_weights, N_ACTIONS, ref)
        components = manipulation_components(F, E, conf, proba[np.arange(N_AGENTS), votes],
                                             votes, model_votes)
        M = manipulation_score(components)
        U = utility(D, F, E, C, M, weights)
        R = reward(U, degenerate)
        private = util[np.arange(N_AGENTS), decision]
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
        log.setdefault("votes", np.zeros((T, N_AGENTS), dtype=int))[t] = votes

    log["collective"] = collective
    log["reported"] = reported
    log["final_reputation"] = reputation if use_reputation else None
    return log


def summarise(prep, log, window=None):
    """Aggregate a simulation log over the evaluation window (default: last `eval_last`)."""
    T = len(prep["reference"])
    window = window if window is not None else slice(T - prep["game"]["eval_last"], T)
    ref, collective = prep["reference"][window], log["collective"][window]
    wrong = collective != ref
    steered = (log["deviates"][window].astype(bool)
               & (log["votes"][window] == collective[:, None])).any(axis=1)
    strategies = log["strategy"][window].astype(int)
    honest_mask = ~log["malicious"][window].astype(bool)
    idx = np.arange(T)[window]
    per_agent_consistency = [
        consistency(prep["views"][i][idx], [log["reported"][t][i] for t in idx],
                    prep["game"]["consistency_neighbours"]) for i in range(N_AGENTS)]

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
        "collective_action_share": {ACTIONS[a]: float((collective == a).mean())
                                    for a in range(N_ACTIONS)},
        "per_agent": {name: {"fidelity": float(log["F"][window][:, i].mean()),
                             "evidence_support": float(log["E"][window][:, i].mean()),
                             "manipulation": float(log["M"][window][:, i].mean()),
                             "reward": float(log["R"][window][:, i].mean()),
                             "private_utility": float(log["private"][window][:, i].mean()),
                             "payoff": float(log["payoff"][window][:, i].mean()),
                             "consistency": per_agent_consistency[i],
                             "final_reputation": (None if log["final_reputation"] is None
                                                  else float(log["final_reputation"][i]))}
                      for i, name in enumerate(AGENTS)},
    }
    return out


def deviation_table(prep, system, seed):
    """Mean payoff of each agent under each of its strategies when the other four
    agents are honest (all rounds). Secondary analysis, protocol section 7."""
    everything = slice(0, len(prep["reference"]))
    table = {}
    for i, name in enumerate(AGENTS):
        table[name] = {}
        for strategy in STRATEGIES:
            policy = ["honest"] * N_AGENTS
            policy[i] = strategy
            log = simulate(prep, system, seed, policy=policy)
            table[name][strategy] = float(log["payoff"][everything][:, i].mean())
    return table


def _run_main(config, seed):
    prep = prepare(config, seed)
    log = simulate(prep, config, seed)
    return {"seed": seed, "system": config["system"], "n_rounds": len(prep["reference"]),
            "eval_last": prep["game"]["eval_last"], "model_val_accuracy": prep["val_accuracy"],
            "metrics": summarise(prep, log),
            "unilateral_deviation_payoff": deviation_table(prep, config, seed)}


for _name in ("energy_baseline", "energy_ablation", "energy_proposed"):
    register(_name)(_run_main)


@register("energy_adversarial")
def run_adversarial(config, seed):
    prep = prepare(config, seed)
    adversarial = config["adversarial"]
    pair = tuple(int(i) for i in np.random.default_rng([seed, 4]).permutation(N_AGENTS)[:2])
    everything = slice(0, len(prep["reference"]))
    out = {"seed": seed, "colluders": [AGENTS[i] for i in pair], "systems": {}}
    for name, system in config["systems"].items():
        by_fraction = {str(p): summarise(prep, simulate(prep, system, seed, malicious_fraction=p))
                       for p in adversarial["malicious_fractions"]}
        honest = ["honest"] * N_AGENTS
        out["systems"][name] = {
            "malicious": by_fraction,
            "collusion": {
                "without": summarise(prep, simulate(prep, system, seed, policy=honest), everything),
                "with": summarise(prep, simulate(prep, system, seed, policy=honest,
                                                 colluders=pair), everything)}}
    return out
