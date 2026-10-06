"""Energy case study (protocol sections 2-4): data-dependent preparation.

`prepare` builds everything that depends only on the data and the seed (models,
sampled rounds, SHAP, per-class explanation quality). The game itself is in
experiments/core.py.
"""
import functools
import json

import numpy as np

from agents.energy_agents import AGENTS, N_ACTIONS, private_utilities, train_agents
from environments.energy.preprocess import ACTIONS, build_scenarios
from evaluation.metrics import evidence_support, fidelity, tercile_thresholds
from experiments.core import register_domain
from game.strategies import STYLES, build_report_content
from xai.shap_explainer import shap_values

N_AGENTS = len(AGENTS)
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
    test = df[df["split"] == game.get("round_split", "test")]
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
    views, val_accuracy, audit = [], {}, []
    for i, name in enumerate(AGENTS):
        agent = agents[name]
        X = rounds[agent.features].to_numpy()
        train_X = train[agent.features].to_numpy()
        thresholds = tercile_thresholds(train_X)
        proba[:, i, :] = agent.predict_proba(rounds)
        phi, _ = shap_values(agent.model, X)                      # (T, features, actions)
        sd = train_X.std(axis=0)
        views.append((X - train_X.mean(axis=0)) / np.where(sd > 0, sd, 1.0))
        # same layout as pharma: (rounds, actions, features); the hour's features are shared
        audit.append({"features": agent.features, "phi": phi.transpose(0, 2, 1),
                      "X": np.repeat(X[:, None, :], N_ACTIONS, axis=1),
                      "thresholds": thresholds})
        val_accuracy[name] = float((agent.predict(val) == val["reference_action"]).mean())
        for t in range(T):
            for c in range(N_ACTIONS):
                for style in STYLES:
                    explanation, claims = build_report_content(style, phi[t, :, c], X[t],
                                                               thresholds, k)
                    quality[style]["F"][t, i, c] = fidelity(explanation, phi[t, :, c], k)
                    quality[style]["E"][t, i, c] = evidence_support(claims, X[t], thresholds)
                    explanations[style][t][i][c] = frozenset(explanation)
    return {"agents": AGENTS, "actions": ACTIONS, "game": game, "battery": battery,
            "hours": rounds["Hour"].to_numpy(),
            "reference": rounds["reference_action"].to_numpy(), "utilities": util,
            "preferred": util.argmax(axis=-1), "proba": proba, "quality": quality,
            "explanations": explanations, "views": views, "val_accuracy": val_accuracy,
            "audit": audit}


register_domain("energy", prepare)
