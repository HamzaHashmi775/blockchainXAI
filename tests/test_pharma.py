"""Pharma case study: preprocessing, constructed reference, agents, SHAP, game."""
import numpy as np
import pandas as pd
import pytest

from agents.pharma_agents import (AGENTS, FEATURE_VIEWS, N_ACTIONS, normalise_scores,
                                  private_utilities, train_agents)
from environments.pharma.preprocess import (ACTIONS, CRITERIA, CRITERION_COLUMNS, FEATURES,
                                            N_CANDIDATES, assign_split, build_scenarios,
                                            clean_lines, criterion_utilities,
                                            normalise_utilities, reference_sensitivity,
                                            reference_slots)
from experiments.core import simulate, summarise
from experiments.pharma import prepare
from game.strategies import STRATEGIES
from xai.shap_explainer import shap_values

FEATURE_COLUMNS = [f for view in FEATURES.values() for f in view]
SMALL = {"system": "proposed", "model": {"n_estimators": 20, "max_depth": 4},
         "game": {"n_rounds": 80, "eval_last": 40},
         "components": {"explanation_aware_incentive": True, "reputation": True},
         "incentive_weights": {"alpha": 0.3, "beta": 0.25, "gamma": 0.15, "delta": 0.1,
                               "lambda": 0.2},
         "reputation": {"initial": 0.5, "rho": 0.8}, "reward": {"degenerate_value": 0.5}}


@pytest.fixture(scope="module")
def lines():
    return clean_lines()


@pytest.fixture(scope="module")
def table(lines):
    return build_scenarios(lines=lines)


@pytest.fixture(scope="module")
def prep(table):
    return prepare(SMALL, 0, table=table)


def test_only_direct_drop_lines_are_used(lines):
    assert len(lines) == 4920
    assert lines["delivered"].is_monotonic_increasing
    assert lines["delivered"].notna().all() and lines["scheduled"].notna().all()
    assert int(lines["po_date"].notna().sum()) == 4592


def test_scenario_table_shape(table):
    assert table["scenario_id"].nunique() == 1648
    assert (table.groupby("scenario_id").size() == N_CANDIDATES).all()
    assert (table["slot"].to_numpy().reshape(-1, N_CANDIDATES) == np.arange(N_CANDIDATES)).all()
    assert (table.groupby("scenario_id")["site"].nunique() == N_CANDIDATES).all()
    assert not table[FEATURE_COLUMNS].isna().any().any()
    assert np.isfinite(table[FEATURE_COLUMNS].to_numpy()).all()
    assert len(ACTIONS) == N_CANDIDATES and len(AGENTS) == 5


def test_feature_views_do_not_overlap():
    assert len(FEATURE_COLUMNS) == len(set(FEATURE_COLUMNS))
    assert all(len(view) == 5 for view in FEATURE_VIEWS.values())


def test_candidates_delivered_the_product_before_the_order(table, lines):
    sample = table.iloc[::97]
    for row in sample.itertuples():
        earlier = lines[(lines["site"] == row.site) & (lines["product"] == row.product)
                        & (lines["delivered"] < row.po_date) & lines["unit_price"].notna()]
        assert len(earlier) == row.n_product_lines > 0


def test_no_future_information_enters_a_scenario(table, lines):
    # Rebuilding from only the lines delivered before a cut-off date must reproduce every
    # scenario ordered up to that date exactly.
    cutoff = table["po_date"].sort_values().iloc[len(table) // 6]
    past = lines[(lines["delivered"] < cutoff)
                 | ((lines["po_date"] <= cutoff) & lines["po_date"].notna())]
    # lines ordered by the cut-off are kept so that the orders themselves exist; their own
    # delivery dates are after the order date and so cannot enter their history
    rebuilt = build_scenarios(lines=past.reset_index(drop=True))
    expected = table[table["po_date"] <= cutoff]
    got = rebuilt[rebuilt["po_date"] <= cutoff]
    assert len(expected) > 100 and len(got) == len(expected)
    columns = ["po", "product", "site", "slot", "reference_slot", *FEATURE_COLUMNS]
    pd.testing.assert_frame_equal(got[columns].reset_index(drop=True),
                                  expected[columns].reset_index(drop=True))


def test_preprocessing_is_deterministic(table, lines):
    early = lines[lines["delivered"] < pd.Timestamp("2010-01-01")].reset_index(drop=True)
    a, b = build_scenarios(lines=early), build_scenarios(lines=early)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) > 0


def test_split_is_time_ordered(table):
    first = table[table["slot"] == 0]
    spans = first.groupby("split")["po_date"].agg(["min", "max"])
    assert spans.loc["train", "max"] < spans.loc["val", "min"]
    assert spans.loc["val", "max"] < spans.loc["test", "min"]
    assert first["split"].value_counts().to_dict() == {"train": 824, "test": 659, "val": 165}


def test_assign_split_keeps_same_day_orders_together():
    dates = pd.to_datetime(["2010-01-01"] * 3 + ["2010-01-02"] * 3 + ["2010-01-03"] * 4)
    split = assign_split(dates, {"train": 0.5, "val": 0.1})
    assert list(split) == ["train"] * 6 + ["test"] * 4 or list(split) == (
        ["train"] * 6 + ["val"] * 4)
    for day in dates.unique():
        assert len(set(split[dates == day])) == 1


def test_normalise_utilities_edge_cases():
    out = normalise_utilities(np.array([[1.0, 3.0, 2.0], [4.0, 4.0, 4.0]]))
    assert out[0].tolist() == [0.0, 1.0, 0.5]
    assert out[1].tolist() == [0.5, 0.5, 0.5]


def test_criterion_utilities_follow_the_documented_signs(table):
    util = criterion_utilities(table)
    assert util.shape == (1648, len(CRITERIA), N_CANDIDATES)
    assert util.min() >= 0.0 and util.max() <= 1.0
    for i, criterion in enumerate(CRITERIA):
        column, sign = CRITERION_COLUMNS[criterion]
        raw = sign * table[column].to_numpy().reshape(-1, N_CANDIDATES)
        varied = raw.max(axis=1) > raw.min(axis=1)
        assert (util[varied, i, :].argmax(axis=1) == raw[varied].argmax(axis=1)).all()
    assert np.array_equal(private_utilities(table), util)


def test_reference_is_the_equal_weight_argmax(table):
    util = criterion_utilities(table)
    reference = table.loc[table["slot"] == 0, "reference_slot"].to_numpy()
    assert np.array_equal(reference, np.round(util.mean(axis=1), 12).argmax(axis=1))
    assert np.array_equal(reference, reference_slots(util, {c: 3.0 for c in CRITERIA}))
    assert (table.groupby("scenario_id")["is_reference"].sum() == 1).all()


def test_slot_order_is_uninformative(table):
    shares = table.loc[table["slot"] == 0, "reference_slot"].value_counts(normalize=True)
    assert shares.min() > 0.30 and shares.max() < 0.37


def test_reference_sensitivity_is_reported_for_every_criterion(table):
    result = reference_sensitivity(table)
    assert set(result) == {f"{m}_{c}" for m in ("drop", "double") for c in CRITERIA}
    assert all(0.5 < v < 1.0 for v in result.values())


def test_normalise_scores():
    out = normalise_scores(np.array([[0.2, 0.2, 0.4], [0.0, 0.0, 0.0]]))
    assert np.allclose(out[0], [0.25, 0.25, 0.5])
    assert np.allclose(out[1], 1 / 3)


@pytest.fixture(scope="module")
def trained(table):
    return train_agents(table[table["split"] == "train"], 0, n_estimators=20, max_depth=4)


def test_agents_predict_a_distribution_over_candidates(table, trained):
    val = table[table["split"] == "val"]
    for name in AGENTS:
        proba = trained[name].predict_proba(val)
        assert proba.shape == (165, N_ACTIONS)
        assert np.allclose(proba.sum(axis=1), 1.0)
        assert set(np.unique(trained[name].predict(val))) <= set(range(N_ACTIONS))


def test_agents_are_deterministic_and_distinct(table, trained):
    train, val = table[table["split"] == "train"], table[table["split"] == "val"]
    again = train_agents(train, 0, n_estimators=20, max_depth=4)
    other = train_agents(train, 1, n_estimators=20, max_depth=4)
    for name in AGENTS:
        assert np.array_equal(trained[name].scores(val), again[name].scores(val))
    assert any(not np.array_equal(trained[n].scores(val), other[n].scores(val)) for n in AGENTS)
    votes = np.stack([trained[n].predict(val) for n in AGENTS])
    assert len({tuple(v) for v in votes}) == len(AGENTS)


def test_shap_is_additive_to_the_candidate_score(table, trained):
    val = table[table["split"] == "val"].head(60)
    for name in AGENTS:
        agent = trained[name]
        X = val[agent.features].to_numpy()
        values, base = shap_values(agent.model, X)
        assert values.shape == (60, 5, 2)
        assert np.allclose(base[1] + values[:, :, 1].sum(axis=1),
                           agent.scores(val).reshape(-1), atol=1e-8)


def test_prepare_contract(prep):
    T = 80
    assert prep["proba"].shape == (T, 5, N_ACTIONS)
    assert np.allclose(prep["proba"].sum(axis=2), 1.0)
    assert prep["utilities"].shape == (T, 5, N_ACTIONS)
    assert (np.diff(prep["scenario_ids"]) > 0).all()
    assert set(prep["reference"]) <= set(range(N_ACTIONS))
    for style, q in prep["quality"].items():
        assert q["F"].min() >= 0 and q["F"].max() <= 1 and q["E"].min() >= 0 and q["E"].max() <= 1
    assert np.allclose(prep["quality"]["truthful"]["F"], 1.0)
    assert np.allclose(prep["quality"]["truthful"]["E"], 1.0)
    assert np.allclose(prep["quality"]["falsified"]["E"], 0.0)
    assert prep["views"][0].shape == (T, N_ACTIONS, 5)


def test_rounds_come_only_from_the_test_split(prep, table):
    test_ids = set(table.loc[table["split"] == "test", "scenario_id"])
    assert set(prep["scenario_ids"]) <= test_ids


def test_game_runs_and_is_reproducible(prep):
    log = simulate(prep, SMALL, 0)
    again = simulate(prep, SMALL, 0)
    assert np.array_equal(log["collective"], again["collective"])
    assert np.array_equal(log["R"], again["R"])
    metrics = summarise(prep, log)
    for key in ("fidelity", "evidence_support", "manipulation", "collective_accuracy",
                "consistency", "manipulation_success"):
        assert 0.0 <= metrics[key] <= 1.0
    assert set(metrics["per_agent"]) == set(AGENTS)
    assert set(metrics["collective_action_share"]) == set(ACTIONS)
    assert abs(sum(metrics["strategy_share"].values()) - 1.0) < 1e-9


def test_all_honest_reports_are_truthful_and_all_manipulative_are_not(prep):
    everything = slice(0, len(prep["reference"]))
    honest = summarise(prep, simulate(prep, SMALL, 0, policy=["honest"] * 5), everything)
    assert honest["fidelity"] == 1.0 and honest["evidence_support"] == 1.0
    assert honest["attack_scores"]["strategic_voting"] == 0.0
    bad = summarise(prep, simulate(prep, SMALL, 0, policy=["manipulative"] * 5), everything)
    assert bad["evidence_support"] == 0.0 and bad["fidelity"] < honest["fidelity"]
    assert bad["manipulation"] > honest["manipulation"]
    assert STRATEGIES[0] == "honest"
