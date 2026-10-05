"""Five energy agents: private objectives and reference-predicting models.

Protocol section 4. Action index order is `environments.energy.preprocess.ACTIONS`
(idle, charge, discharge); argmax ties therefore resolve in that order.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from environments.energy.preprocess import ACTION_SIGN
from utils.seed import model_seed

AGENTS = ("producer", "consumer", "market", "grid", "storage")
FEATURE_VIEWS = {
    "producer": ["PG_max", "Temperature", "hour_of_day", "Price_SG", "sell_rank_day"],
    "consumer": ["load_mw", "thermal_total", "Temperature", "TL_Flex_Availability", "Price",
                 "hour_of_day"],
    "market": ["Price", "Price_SG", "Gas_Price", "price_rank_day", "spread"],
    "grid": ["net_demand_mw", "load_mw", "PG_max", "hour_of_day"],
    "storage": ["net_demand_mw", "ev_home", "hour_of_day", "price_rank_day", "PG_max"],
}
N_ACTIONS = len(ACTION_SIGN)


def raw_private_utilities(df, power):
    """u_i(a, t) for every agent; array of shape (n_hours, n_agents, n_actions)."""
    s = ACTION_SIGN[None, :]
    net = df["net_demand_mw"].to_numpy()[:, None]
    grid_exchange = net + power * s                      # import if positive
    price = df["Price"].to_numpy()[:, None]
    sell = df["Price_SG"].to_numpy()[:, None]
    surplus = net < 0
    storage = np.where(surplus, s == 1, s == 0).astype(float)
    per_agent = {
        "producer": -s * (sell - df["sell_day_median"].to_numpy()[:, None]),
        "consumer": -price * np.maximum(grid_exchange, 0.0),
        "market": -s * (price - df["price_day_median"].to_numpy()[:, None]),
        "grid": -np.abs(grid_exchange),
        "storage": storage,
    }
    return np.stack([per_agent[a] for a in AGENTS], axis=1)


def normalise_utilities(raw):
    """Min-max over the actions of each hour; 0.5 everywhere if all actions tie."""
    low = raw.min(axis=-1, keepdims=True)
    span = raw.max(axis=-1, keepdims=True) - low
    safe = np.where(span > 0, span, 1.0)
    return np.where(span > 0, (raw - low) / safe, 0.5)


def private_utilities(df, power):
    return normalise_utilities(raw_private_utilities(df, power))


def preferred_actions(utilities):
    """a*_i per hour and agent (ties: idle, charge, discharge)."""
    return utilities.argmax(axis=-1)


class EnergyAgent:
    def __init__(self, name, seed, n_estimators=100, max_depth=6):
        self.name = name
        self.features = FEATURE_VIEWS[name]
        self.model = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth,
            random_state=model_seed(seed, name), n_jobs=1)

    def fit(self, df):
        self.model.fit(df[self.features].to_numpy(), df["reference_action"].to_numpy())
        missing = set(range(N_ACTIONS)) - set(self.model.classes_)
        if missing:
            raise ValueError(f"training data lacks action classes {sorted(missing)}")
        return self

    def predict_proba(self, df):
        return self.model.predict_proba(df[self.features].to_numpy())

    def predict(self, df):
        return self.predict_proba(df).argmax(axis=1)


def train_agents(train_df, seed, **model_kwargs):
    return {name: EnergyAgent(name, seed, **model_kwargs).fit(train_df) for name in AGENTS}
