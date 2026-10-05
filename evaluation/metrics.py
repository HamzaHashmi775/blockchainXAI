"""Explanation and decision metrics (protocol section 6).

An explanation is a list of (feature_index, sign) pairs with sign in {-1, 0, +1}.
An evidence claim is a (feature_index, level) pair with level in LEVELS.
"""
import numpy as np

from xai.shap_explainer import top_k_features

LEVELS = ("low", "mid", "high")


def fidelity(explanation, phi, k):
    """Share of the true top-k |SHAP| mass covered by correctly signed reported features."""
    phi = np.asarray(phi, dtype=float)
    if len(explanation) == 0:
        return 0.0
    denominator = float(np.abs(phi[top_k_features(phi, k)]).sum())
    if denominator == 0.0:
        return 1.0
    covered = 0.0
    for feature in {f for f, _ in explanation}:
        signs = {s for f, s in explanation if f == feature}
        if len(signs) == 1 and np.sign(phi[feature]) == next(iter(signs)):
            covered += abs(phi[feature])
    return float(min(1.0, covered / denominator))


def tercile_thresholds(train_values):
    """Per-feature (33.3%, 66.7%) quantiles of the training split; shape (2, n_features)."""
    return np.quantile(np.asarray(train_values, dtype=float), [1 / 3, 2 / 3], axis=0)


def observed_level(value, low_cut, high_cut):
    """Documented criterion: low if value <= lower tercile, high if > upper, else mid."""
    if value <= low_cut:
        return "low"
    if value > high_cut:
        return "high"
    return "mid"


def evidence_support(claims, x, thresholds):
    """supported_claims / total_claims; 0 when no claim is made."""
    if len(claims) == 0:
        return 0.0
    supported = sum(
        observed_level(x[f], thresholds[0, f], thresholds[1, f]) == level for f, level in claims)
    return supported / len(claims)


def jaccard(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def consistency(X_standardised, explanations, n_neighbours=5):
    """Mean explanation similarity (Jaccard) between each scenario and its nearest
    scenarios (Euclidean distance in the standardised feature view)."""
    X = np.asarray(X_standardised, dtype=float)
    n = len(X)
    if n < 2:
        return float("nan")
    k = min(n_neighbours, n - 1)
    sq = (X ** 2).sum(axis=1)
    dist = sq[:, None] + sq[None, :] - 2.0 * X @ X.T
    np.fill_diagonal(dist, np.inf)
    neighbours = np.argsort(dist, axis=1, kind="stable")[:, :k]
    sims = [jaccard(explanations[i], explanations[j]) for i in range(n) for j in neighbours[i]]
    return float(np.mean(sims))


def collective_decision(votes, confidences, weights, n_actions):
    """Weighted confidence vote; ties resolve to the lowest action index."""
    scores = np.zeros(n_actions)
    np.add.at(scores, np.asarray(votes), np.asarray(weights, dtype=float) * np.asarray(confidences))
    return int(scores.argmax())


def contributions(votes, confidences, weights, n_actions, reference):
    """C_i: 1 if agent i is pivotal for a correct decision, 0 if pivotal for an
    incorrect one, 0.5 otherwise (leave-one-out)."""
    votes, confidences = np.asarray(votes), np.asarray(confidences, dtype=float)
    weights = np.asarray(weights, dtype=float)
    correct = collective_decision(votes, confidences, weights, n_actions) == reference
    out = np.full(len(votes), 0.5)
    for i in range(len(votes)):
        keep = np.arange(len(votes)) != i
        without = collective_decision(votes[keep], confidences[keep], weights[keep],
                                      n_actions) == reference
        if correct and not without:
            out[i] = 1.0
        elif not correct and without:
            out[i] = 0.0
    return out
