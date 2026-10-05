"""Strategy space and report construction (protocol section 5).

G = (N, S, U): N = the agents, S_i = STRATEGIES, U = agent payoff (see
experiments/energy.py). Strategies change the agent's *report* only; the
observation x is never modified.
"""
import numpy as np

from evaluation.metrics import observed_level
from xai.shap_explainer import bottom_k_features, top_k_features

STRATEGIES = ("honest", "strategic", "manipulative")
TRUTHFUL, FALSIFIED = "truthful", "falsified"


def truthful_explanation(phi, k):
    """Top-k |SHAP| features with their true signs."""
    return [(int(f), int(np.sign(phi[f]))) for f in top_k_features(phi, k)]


def falsified_explanation(phi, k):
    """False attribution: the k least important features, signs flipped."""
    return [(int(f), int(-np.sign(phi[f]))) for f in bottom_k_features(phi, k)]


def truthful_evidence(explanation, x, thresholds):
    return [(f, observed_level(x[f], thresholds[0, f], thresholds[1, f])) for f, _ in explanation]


def unsupported_evidence(explanation, x, thresholds):
    """Unsupported evidence: claim "high", or "low" when the observation is high."""
    claims = []
    for f, _ in explanation:
        truth = observed_level(x[f], thresholds[0, f], thresholds[1, f])
        claims.append((f, "low" if truth == "high" else "high"))
    return claims


def choose_report(strategy, proba, preferred, utilities, deviation_threshold=0.25,
                  inflation=0.3):
    """(vote, confidence, explanation style) for one agent in one round."""
    model_vote = int(np.argmax(proba))
    if strategy == "honest":
        return model_vote, float(proba[model_vote]), TRUTHFUL
    if strategy == "strategic":
        gain = utilities[preferred] - utilities[model_vote]
        if preferred != model_vote and gain >= deviation_threshold:
            return int(preferred), float(min(1.0, proba[preferred] + inflation)), TRUTHFUL
        return model_vote, float(proba[model_vote]), TRUTHFUL
    if strategy == "manipulative":
        return int(preferred), 1.0, FALSIFIED
    raise ValueError(f"unknown strategy {strategy!r}")


def collusive_vote(utilities_i, utilities_j):
    """Joint vote of two colluders: argmax of their summed private utilities."""
    return int(np.argmax(np.asarray(utilities_i) + np.asarray(utilities_j)))
