"""Energy environment, agents, SHAP and experiment-level tests (real data)."""
import copy
from pathlib import Path

import numpy as np
import pytest
import yaml

from agents.energy_agents import (AGENTS, FEATURE_VIEWS, normalise_utilities,
                                  preferred_actions, private_utilities, train_agents)
from environments.energy.preprocess import (ACTIONS, DERIVED, REAL, assign_split,
                                            battery_parameters, build_scenarios, solve_day)
from experiments.core import _apply_parameter, _malicious_count, deviation_table, simulate, summarise
from experiments.energy import prepare
from game.strategies import STRATEGIES
from utils import datasets as ds
from xai.shap_explainer import shap_values

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def raw():
    return ds.load_energy(["Buses", "Profiles", "EV_Parameters"])


@pytest.fixture(scope="module")
def scenarios(raw):
    return build_scenarios(data=raw)


@pytest.fixture(scope="module")
def small_config():
    cfg = yaml.safe_load((ROOT / "configs" / "energy_proposed.yaml").read_text())
    cfg["model"] = {"n_estimators": 15, "max_depth": 4}
    cfg["game"].update(n_rounds=80, eval_last=40)
    return cfg


@pytest.fixture(scope="module")
def prep(small_config):
    return prepare(small_config, seed=3)


# ---- preprocessing --------------------------------------------------------
def test_preprocessing_is_deterministic(raw, scenarios):
    again, battery = build_scenarios(data=raw)
    assert again.equals(scenarios[0]) and battery == scenarios[1]


def test_preprocessing_leaves_real_columns_untouched(raw, scenarios):
    df, _ = scenarios
    assert len(df) == 8760 and not df.isna().any().any()
    for col in REAL:
        assert (df[col].to_numpy() == raw["Profiles"][col].to_numpy()).all()
    assert set(DERIVED) <= set(df.columns)


def test_derived_variables(raw, scenarios):
    df, battery = scenarios
    assert np.allclose(df["net_demand_mw"], df["load_mw"] - df["pv_mw"])
    assert df["load_mw"].between(0.03, 0.2).all()
    assert df["price_rank_day"].between(0, 1).all()
    assert df.groupby("day")["price_rank_day"].max().eq(1.0).all()
    assert battery["capacity"] == pytest.approx(raw["Buses"]["BT"].sum())
    assert battery["power"] == pytest.approx(0.5 * battery["capacity"])


def test_split_has_no_leakage(scenarios):
    df, _ = scenarios
    assert set(df["split"]) == {"train", "val", "test"}
    # a week, and therefore a day, never straddles two partitions
    assert df.groupby(df["day"] // 7)["split"].nunique().max() == 1
    assert df.groupby("day")["split"].nunique().max() == 1
    hours = {s: set(g["Hour"]) for s, g in df.groupby("split")}
    assert not (hours["train"] & hours["test"]) and not (hours["train"] & hours["val"])
    assert assign_split(np.array([0, 20, 21, 27, 28, 34, 35])).tolist() == [
        "train", "train", "val", "val", "test", "test", "train"]


def test_reference_lp_respects_battery_limits():
    battery = battery_parameters(__import__("pandas").DataFrame({"BT": [0.1]}))
    price = np.r_[np.full(12, 10.0), np.full(12, 100.0)]
    net = np.full(24, 0.5)
    schedule = solve_day(net, price, price * 0.5, battery)
    assert np.abs(schedule).max() <= battery["power"] + 1e-9
    assert schedule[:12].sum() > 0 > schedule[12:].sum()      # buy cheap, use when dear
    eta = battery["round_trip_efficiency"] ** 0.5
    soc = 0.05 + np.cumsum(np.where(schedule > 0, schedule * eta, schedule / eta))
    assert soc.min() >= 0.01 - 1e-7 and soc.max() <= 0.09 + 1e-7
    assert soc[-1] == pytest.approx(0.05, abs=1e-7)


def test_reference_has_all_actions(scenarios):
    df, _ = scenarios
    shares = df["reference_action"].value_counts(normalize=True)
    assert set(shares.index) == {0, 1, 2} and shares.min() > 0.1
    assert ACTIONS == ("idle", "charge", "discharge")


# ---- agents ---------------------------------------------------------------
def test_feature_views_use_existing_columns(scenarios):
    df, _ = scenarios
    for name in AGENTS:
        assert set(FEATURE_VIEWS[name]) <= set(df.columns)
        assert "reference_action" not in FEATURE_VIEWS[name]
    assert len({tuple(v) for v in FEATURE_VIEWS.values()}) == 5


def test_private_utilities_are_normalised_and_distinct(scenarios):
    df, battery = scenarios
    util = private_utilities(df, battery["power"])
    assert util.shape == (8760, 5, 3)
    assert util.min() >= 0 and util.max() <= 1
    prefs = preferred_actions(util)
    for i in range(5):
        for j in range(i + 1, 5):
            assert (prefs[:, i] != prefs[:, j]).mean() > 0.05, (AGENTS[i], AGENTS[j])


def test_private_utility_rules(scenarios):
    df, battery = scenarios
    prefs = preferred_actions(private_utilities(df, battery["power"]))
    surplus = (df["net_demand_mw"] < 0).to_numpy()
    storage = prefs[:, AGENTS.index("storage")]
    assert (storage[surplus] == 1).all() and (storage[~surplus] == 0).all()
    market = prefs[:, AGENTS.index("market")]
    cheap = (df["Price"] < df["price_day_median"]).to_numpy()
    dear = (df["Price"] > df["price_day_median"]).to_numpy()
    assert (market[cheap] == 1).all() and (market[dear] == 2).all()


def test_normalise_utilities_tie_is_half():
    out = normalise_utilities(np.array([[[2.0, 2.0, 2.0], [0.0, 1.0, 3.0]]]))
    assert out[0, 0].tolist() == [0.5, 0.5, 0.5]
    assert out[0, 1] == pytest.approx([0.0, 1 / 3, 1.0])


def test_agents_train_predict_and_are_seeded(scenarios):
    df, _ = scenarios
    train, val = df[df["split"] == "train"], df[df["split"] == "val"]
    kwargs = {"n_estimators": 15, "max_depth": 4}
    a, b = train_agents(train, 1, **kwargs), train_agents(train, 1, **kwargs)
    c = train_agents(train, 2, **kwargs)
    majority = val["reference_action"].value_counts(normalize=True).max()
    for name in AGENTS:
        pa = a[name].predict_proba(val)
        assert pa.shape == (len(val), 3) and np.allclose(pa.sum(axis=1), 1)
        assert np.array_equal(pa, b[name].predict_proba(val))
        assert a[name].model.n_features_in_ == len(FEATURE_VIEWS[name])
        assert (a[name].predict(val) == val["reference_action"]).mean() > majority - 0.02
    assert any(not np.array_equal(a[n].predict_proba(val), c[n].predict_proba(val)) for n in AGENTS)


# ---- SHAP -----------------------------------------------------------------
def test_shap_shape_additivity_determinism(scenarios):
    df, _ = scenarios
    agents = train_agents(df[df["split"] == "train"], 1, n_estimators=15, max_depth=4)
    sample = df[df["split"] == "test"].iloc[:40]
    for name in ("market", "grid"):
        agent = agents[name]
        X = sample[agent.features].to_numpy()
        values, base = shap_values(agent.model, X)
        assert values.shape == (40, len(agent.features), 3) and base.shape == (3,)
        assert np.allclose(base + values.sum(axis=1), agent.model.predict_proba(X), atol=1e-6)
        again, _ = shap_values(agent.model, X)
        assert np.array_equal(values, again)


# ---- experiment -----------------------------------------------------------
def test_prepare_is_deterministic_and_paired(small_config, prep):
    baseline = copy.deepcopy(small_config)
    baseline["components"]["reputation"] = False
    baseline["incentive_weights"] = {"alpha": 0.75, "beta": 0, "gamma": 0, "delta": 0.25, "lambda": 0}
    other = prepare(baseline, seed=3)
    assert np.array_equal(other["hours"], prep["hours"])
    assert np.array_equal(other["proba"], prep["proba"])
    assert not np.array_equal(prepare(small_config, seed=4)["hours"], prep["hours"])
    assert (np.diff(prep["hours"]) > 0).all()                 # chronological replay


def test_honest_reports_score_perfectly_and_falsified_zero(prep):
    assert prep["quality"]["truthful"]["F"].min() == 1.0
    assert prep["quality"]["truthful"]["E"].min() == 1.0
    assert prep["quality"]["falsified"]["F"].max() == 0.0
    assert prep["quality"]["falsified"]["E"].max() == 0.0


def test_partial_styles_separate_fidelity_from_evidence(prep):
    mis, over = prep["quality"]["misattributed"], prep["quality"]["overclaimed"]
    assert mis["E"].min() == 1.0 and 0.0 < mis["F"].mean() < 1.0      # F degraded, E intact
    assert mis["F"].max() <= 1.0 and mis["F"].std() > 0                # graded, not binary
    assert over["F"].min() == 1.0 and (over["E"] == 0.5).all()         # E degraded, F intact


def test_fixed_partial_strategies(small_config, prep):
    log = simulate(prep, small_config, 3, policy=["misattributing"] * 5)
    assert log["E"].min() == 1.0 and log["F"].mean() < 1.0
    assert log["unsupported_evidence"].max() == 0.0 and log["false_attribution"].mean() > 0
    log = simulate(prep, small_config, 3, policy=["overclaiming"] * 5)
    assert log["F"].min() == 1.0 and (log["E"] == 0.5).all()


def test_sensitivity_parameter_overrides(small_config, prep):
    p2, s2 = _apply_parameter(prep, small_config, "game.omega", 0.9)
    assert p2["game"]["omega"] == 0.9 and prep["game"]["omega"] == 0.5
    _, s3 = _apply_parameter(prep, small_config, "reputation.rho", 0.5)
    assert s3["reputation"]["rho"] == 0.5 and small_config["reputation"]["rho"] == 0.8
    _, s4 = _apply_parameter(prep, small_config, "incentive_weights.beta", 0.4)
    w = s4["incentive_weights"]
    assert w["beta"] == 0.4 and sum(w.values()) == pytest.approx(1.0)
    assert w["alpha"] / w["lambda"] == pytest.approx(0.30 / 0.20)
    baseline = copy.deepcopy(small_config)
    baseline["components"]["explanation_aware_incentive"] = False
    _, s5 = _apply_parameter(prep, baseline, "incentive_weights.beta", 0.4)
    assert s5["incentive_weights"] == baseline["incentive_weights"]     # baseline untouched


def test_all_honest_simulation(small_config, prep):
    log = simulate(prep, small_config, 3, policy=["honest"] * 5)
    assert log["F"].min() == 1.0 and log["E"].min() == 1.0 and log["M"].max() == 0.0
    assert ((log["R"] >= 0) & (log["R"] <= 1)).all()
    assert ((log["reputation"] >= 0) & (log["reputation"] <= 1)).all()
    summary = summarise(prep, log)
    assert summary["manipulation_success"] == 0.0
    assert summary["strategy_share"]["honest"] == 1.0


def test_all_manipulative_simulation(small_config, prep):
    log = simulate(prep, small_config, 3, policy=["manipulative"] * 5)
    assert log["F"].max() == 0.0 and log["E"].max() == 0.0
    assert log["false_attribution"].min() == 1.0 and log["unsupported_evidence"].min() == 1.0
    assert log["M"].min() >= 0.4
    assert (log["votes"] == prep["preferred"]).all()


def test_simulation_is_reproducible(small_config, prep):
    a, b = simulate(prep, small_config, 3), simulate(prep, small_config, 3)
    for key in ("F", "M", "R", "strategy", "collective"):
        assert np.array_equal(a[key], b[key])
    assert summarise(prep, a) == summarise(prep, b)


def test_malicious_share_expectation_and_behaviour(small_config, prep):
    rng = np.random.default_rng(0)
    for fraction, expected in ((0.0, 0.0), (0.1, 0.5), (0.2, 1.0), (0.3, 1.5), (0.4, 2.0)):
        counts = [_malicious_count(rng, fraction, 5) for _ in range(4000)]
        assert np.mean(counts) == pytest.approx(expected, abs=0.05)
        assert set(counts) <= {int(np.floor(expected)), int(np.ceil(expected))}
    log = simulate(prep, small_config, 3, malicious_fraction=0.4)
    mal = log["malicious"].astype(bool)
    assert (mal.sum(axis=1) == 2).all()
    assert log["F"][mal].max() == 0.0
    assert mal.any(axis=0).sum() == 2                      # the same two agents throughout


def test_collusion_condition(small_config, prep):
    log = simulate(prep, small_config, 3, policy=["honest"] * 5, colluders=(0, 2))
    assert (log["votes"][:, 0] == log["votes"][:, 2]).all()
    assert log["F"][:, [1, 3, 4]].min() == 1.0 and log["F"][:, [0, 2]].max() == 0.0
    both_deviate = log["deviates"][:, 0].astype(bool) & log["deviates"][:, 2].astype(bool)
    assert (log["collusion"][both_deviate][:, [0, 2]] == 1).all()


def test_deviation_table_shape(small_config, prep):
    table = deviation_table(prep, small_config, 3)
    assert set(table) == set(AGENTS)
    assert all(set(row) == set(STRATEGIES) for row in table.values())
    assert all(0 <= v <= 1 for row in table.values() for v in row.values())
