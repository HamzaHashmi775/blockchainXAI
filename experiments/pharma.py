"""Pharma case study (protocol section 11): data-dependent preparation.

Same contract as experiments/energy.py. Rounds are purchase-order scenarios of the test
split, played in order of order date; actions are the three candidate slots.
"""
import functools
import json

import numpy as np

from agents.pharma_agents import AGENTS, N_ACTIONS, private_utilities, train_agents
from environments.pharma.preprocess import ACTIONS, build_scenarios
from evaluation.metrics import evidence_support, fidelity, tercile_thresholds
from experiments.core import register_domain
from game.strategies import STYLES, build_report_content
from xai.shap_explainer import shap_values

N_AGENTS = len(AGENTS)
GAME_DEFAULTS = {"n_rounds": 600, "eval_last": 300, "top_k": 2, "deviation_threshold": 0.25,
                 "inflation": 0.3, "epsilon": 0.1, "learning_rate": 0.1, "q_init": 0.5,
                 "omega": 0.5, "consistency_neighbours": 5}


@functools.lru_cache(maxsize=4)
def _scenarios(reference_json):
    return build_scenarios(json.loads(reference_json))


def _reference(table):
    return table.loc[table["slot"] == 0, "reference_slot"].to_numpy()


def prepare(config, seed, table=None):
    game = {**GAME_DEFAULTS, **config.get("game", {})}
    if table is None:
        table = _scenarios(json.dumps(config.get("reference", {}), sort_keys=True))
    train, val = table[table["split"] == "train"], table[table["split"] == "val"]
    test = table[table["split"] == "test"]
    agents = train_agents(train, seed, **config.get("model", {}))

    test_ids = test["scenario_id"].unique()                       # already in order-date order
    rng = np.random.default_rng([seed, 1])
    chosen = np.sort(rng.choice(len(test_ids), size=game["n_rounds"], replace=False))
    rounds = test[test["scenario_id"].isin(test_ids[chosen])]
    T, k = len(chosen), game["top_k"]

    util = private_utilities(rounds)                              # (T, agents, candidates)
    proba = np.zeros((T, N_AGENTS, N_ACTIONS))
    quality = {s: {"F": np.zeros((T, N_AGENTS, N_ACTIONS)), "E": np.zeros((T, N_AGENTS, N_ACTIONS))}
               for s in STYLES}
    explanations = {s: [[[None] * N_ACTIONS for _ in range(N_AGENTS)] for _ in range(T)]
                    for s in STYLES}
    views, val_accuracy = [], {}
    for i, name in enumerate(AGENTS):
        agent = agents[name]
        flat = rounds[agent.features].to_numpy()
        X = flat.reshape(T, N_ACTIONS, -1)
        train_X = train[agent.features].to_numpy()
        thresholds = tercile_thresholds(train_X)
        proba[:, i, :] = agent.predict_proba(rounds)
        values, _ = shap_values(agent.model, flat)                # (T*candidates, features, 2)
        phi = values[:, :, 1].reshape(T, N_ACTIONS, -1)           # positive-class score
        sd = train_X.std(axis=0)
        views.append((X - train_X.mean(axis=0)) / np.where(sd > 0, sd, 1.0))
        val_accuracy[name] = float((agent.predict(val) == _reference(val)).mean())
        for t in range(T):
            for c in range(N_ACTIONS):
                for style in STYLES:
                    explanation, claims = build_report_content(style, phi[t, c], X[t, c],
                                                               thresholds, k)
                    quality[style]["F"][t, i, c] = fidelity(explanation, phi[t, c], k)
                    quality[style]["E"][t, i, c] = evidence_support(claims, X[t, c], thresholds)
                    explanations[style][t][i][c] = frozenset(explanation)
    return {"agents": AGENTS, "actions": ACTIONS, "game": game,
            "scenario_ids": test_ids[chosen], "reference": _reference(rounds),
            "utilities": util, "preferred": util.argmax(axis=-1), "proba": proba,
            "quality": quality, "explanations": explanations, "views": views,
            "val_accuracy": val_accuracy}


register_domain("pharma", prepare)
