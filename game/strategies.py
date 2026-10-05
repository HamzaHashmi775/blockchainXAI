"""Strategy space and report construction (protocol section 5).

G = (N, S, U): N = the agents, S_i = STRATEGIES, U = agent payoff (see
experiments/energy.py). Strategies change the agent's *report* only; the
observation x is never modified.
"""
import numpy as np

from evaluation.metrics import observed_level
from xai.shap_explainer import bottom_k_features, top_k_features

STRATEGIES = ("honest", "strategic", "misattributing", "overclaiming", "manipulative")
TRUTHFUL, FALSIFIED = "truthful", "falsified"
MISATTRIBUTED, OVERCLAIMED = "misattributed", "overclaimed"   # protocol amendment 1
STYLES = (TRUTHFUL, MISATTRIBUTED, OVERCLAIMED, FALSIFIED)


def truthful_explanation(phi, k):
    """Top-k |SHAP| features with their true signs."""
    return [(int(f), int(np.sign(phi[f]))) for f in top_k_features(phi, k)]


def falsified_explanation(phi, k):
    """False attribution: the k least important features, signs flipped."""
    return [(int(f), int(-np.sign(phi[f]))) for f in bottom_k_features(phi, k)]


def misattributed_explanation(phi, k):
    """Partial false attribution: the true top k-1 features, then the least important
    feature with its sign flipped."""
    kept = truthful_explanation(phi, k - 1)
    used = {f for f, _ in kept}
    filler = next(int(f) for f in bottom_k_features(phi, len(phi)) if int(f) not in used)
    return kept + [(filler, int(-np.sign(phi[filler])))]


def overclaimed_evidence(explanation, x, thresholds):
    """Partially unsupported evidence: every claim true except the last one."""
    claims = truthful_evidence(explanation, x, thresholds)
    return claims[:-1] + unsupported_evidence(explanation[-1:], x, thresholds)


def build_report_content(style, phi, x, thresholds, k):
    """(explanation, evidence claims) for a report style."""
    if style == TRUTHFUL:
        explanation = truthful_explanation(phi, k)
        return explanation, truthful_evidence(explanation, x, thresholds)
    if style == MISATTRIBUTED:
        explanation = misattributed_explanation(phi, k)
        return explanation, truthful_evidence(explanation, x, thresholds)
    if style == OVERCLAIMED:
        explanation = truthful_explanation(phi, k)
        return explanation, overclaimed_evidence(explanation, x, thresholds)
    if style == FALSIFIED:
        explanation = falsified_explanation(phi, k)
        return explanation, unsupported_evidence(explanation, x, thresholds)
    raise ValueError(f"unknown report style {style!r}")


def truthful_evidence(explanation, x, thresholds):
    return [(f, observed_level(x[f], thresholds[0, f], thresholds[1, f])) for f, _ in explanation]


def unsupported_evidence(explanation, x, thresholds):
    """Unsupported evidence: claim "high", or "low" when the observation is high."""
    claims = []
    for f, _ in explanation:
        truth = observed_level(x[f], thresholds[0, f], thresholds[1, f])
        claims.append((f, "low" if truth == "high" else "high"))
    return claims


# strategies that vote like "strategic" and differ only in the explanation they attach
STRATEGIC_STYLES = {"strategic": TRUTHFUL, "misattributing": MISATTRIBUTED,
                    "overclaiming": OVERCLAIMED}


def choose_report(strategy, proba, preferred, utilities, deviation_threshold=0.25,
                  inflation=0.3):
    """(vote, confidence, explanation style) for one agent in one round."""
    model_vote = int(np.argmax(proba))
    if strategy == "honest":
        return model_vote, float(proba[model_vote]), TRUTHFUL
    if strategy in STRATEGIC_STYLES:
        style = STRATEGIC_STYLES[strategy]
        gain = utilities[preferred] - utilities[model_vote]
        if preferred != model_vote and gain >= deviation_threshold:
            return int(preferred), float(min(1.0, proba[preferred] + inflation)), style
        return model_vote, float(proba[model_vote]), style
    if strategy == "manipulative":
        return int(preferred), 1.0, FALSIFIED
    raise ValueError(f"unknown strategy {strategy!r}")


def collusive_vote(utilities_i, utilities_j):
    """Joint vote of two colluders: argmax of their summed private utilities."""
    return int(np.argmax(np.asarray(utilities_i) + np.asarray(utilities_j)))
