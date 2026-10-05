"""Manipulation score, explanation-aware utility and reward (protocol sections 6-7)."""
import numpy as np

WEIGHT_KEYS = ("alpha", "beta", "gamma", "delta", "lambda")
ATTACKS = ("false_attribution", "confidence_inflation", "unsupported_evidence",
           "strategic_voting", "collusion")


def collusion_flags(votes, model_votes):
    """1 for an agent that deviates from its model and shares its vote with another
    deviating agent."""
    votes, model_votes = np.asarray(votes), np.asarray(model_votes)
    deviates = votes != model_votes
    flags = np.zeros(len(votes))
    for i in np.flatnonzero(deviates):
        others = deviates & (votes == votes[i])
        others[i] = False
        flags[i] = float(others.any())
    return flags


def manipulation_components(fidelity, evidence, confidence, model_probability_of_vote,
                            votes, model_votes):
    """Audited per-attack scores in [0, 1]; arrays of shape (n_agents,)."""
    votes, model_votes = np.asarray(votes), np.asarray(model_votes)
    return {
        "false_attribution": 1.0 - np.asarray(fidelity, dtype=float),
        "confidence_inflation": np.clip(
            np.asarray(confidence, dtype=float) - np.asarray(model_probability_of_vote), 0.0, 1.0),
        "unsupported_evidence": 1.0 - np.asarray(evidence, dtype=float),
        "strategic_voting": (votes != model_votes).astype(float),
        "collusion": collusion_flags(votes, model_votes),
    }


def manipulation_score(components):
    """M_i = mean of the five audited components."""
    return np.mean([components[a] for a in ATTACKS], axis=0)


def validate_weights(weights):
    missing = [k for k in WEIGHT_KEYS if weights.get(k) is None]
    if missing:
        raise ValueError(f"incentive weights not set: {missing}")
    if any(weights[k] < 0 for k in WEIGHT_KEYS):
        raise ValueError("incentive weights must be non-negative")
    return {k: float(weights[k]) for k in WEIGHT_KEYS}


def utility(D, F, E, C, M, weights):
    """U_i = alpha*D + beta*F + gamma*E + delta*C - lambda*M (components in [0, 1])."""
    parts = [np.asarray(v, dtype=float) for v in (D, F, E, C, M)]
    for name, part in zip("DFECM", parts):
        if np.any(part < 0) or np.any(part > 1):
            raise ValueError(f"component {name} outside [0, 1]")
    D, F, E, C, M = parts
    w = weights
    return w["alpha"] * D + w["beta"] * F + w["gamma"] * E + w["delta"] * C - w["lambda"] * M


def reward(utilities, degenerate_value=0.5):
    """R_i = (U_i - U_min) / (U_max - U_min); `degenerate_value` if U_max == U_min."""
    u = np.asarray(utilities, dtype=float)
    low, high = u.min(), u.max()
    if high == low:
        return np.full(u.shape, float(degenerate_value))
    return (u - low) / (high - low)
