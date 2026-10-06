"""Five pharma agents: private objectives and reference-predicting models.

Protocol section 11.3. An agent scores each candidate site of a scenario from its own
feature view; actions are the candidate slots of
`environments.pharma.preprocess.ACTIONS`, and argmax ties resolve to the lowest slot.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from environments.pharma.preprocess import CRITERIA, FEATURES, N_CANDIDATES, criterion_utilities
from utils.seed import model_seed

AGENTS = CRITERIA                      # cost, reliability, lead_time, logistics, continuity
FEATURE_VIEWS = FEATURES
N_ACTIONS = N_CANDIDATES


def private_utilities(table):
    """Normalised u_i(c, t); array of shape (n_scenarios, n_agents, n_candidates)."""
    return criterion_utilities(table)


def normalise_scores(scores):
    """Scores per candidate -> probabilities over the candidates (uniform if all zero)."""
    total = scores.sum(axis=1, keepdims=True)
    return np.where(total > 0, scores / np.where(total > 0, total, 1.0), 1.0 / scores.shape[1])


class PharmaAgent:
    def __init__(self, name, seed, n_estimators=100, max_depth=6):
        self.name = name
        self.features = FEATURE_VIEWS[name]
        self.model = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth,
            random_state=model_seed(seed, name), n_jobs=1)

    def fit(self, table):
        """One training row per (scenario, candidate); target: candidate is the reference."""
        self.model.fit(table[self.features].to_numpy(), table["is_reference"].to_numpy())
        if list(self.model.classes_) != [0, 1]:
            raise ValueError("training data must contain reference and non-reference candidates")
        return self

    def scores(self, table):
        """Positive-class score of every candidate; shape (n_scenarios, n_candidates)."""
        positive = self.model.predict_proba(table[self.features].to_numpy())[:, 1]
        return positive.reshape(-1, N_CANDIDATES)

    def predict_proba(self, table):
        return normalise_scores(self.scores(table))

    def predict(self, table):
        return self.predict_proba(table).argmax(axis=1)


def train_agents(train_table, seed, **model_kwargs):
    return {name: PharmaAgent(name, seed, **model_kwargs).fit(train_table) for name in AGENTS}
