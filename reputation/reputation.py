"""Reputation: Rep^0 = 0.5, Rep^(t+1) = rho * Rep^t + (1 - rho) * R^t."""
import numpy as np


def initial_reputation(n_agents, initial=0.5):
    if not 0.0 <= initial <= 1.0:
        raise ValueError("initial reputation must lie in [0, 1]")
    return np.full(n_agents, float(initial))


def update_reputation(reputation, rewards, rho=0.8):
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0, 1]")
    rewards = np.asarray(rewards, dtype=float)
    if np.any(rewards < 0) or np.any(rewards > 1):
        raise ValueError("rewards must lie in [0, 1]")
    return rho * np.asarray(reputation, dtype=float) + (1.0 - rho) * rewards
