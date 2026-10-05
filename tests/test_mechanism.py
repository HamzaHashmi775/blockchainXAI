"""Unit tests: metrics, strategies, manipulation, utility, reward, reputation."""
import numpy as np
import pytest

from evaluation.metrics import (collective_decision, consistency, contributions,
                                evidence_support, fidelity, jaccard, observed_level,
                                tercile_thresholds)
from game.strategies import (FALSIFIED, TRUTHFUL, choose_report, collusive_vote,
                             falsified_explanation, truthful_evidence, truthful_explanation,
                             unsupported_evidence)
from incentives.mechanism import (ATTACKS, collusion_flags, manipulation_components,
                                  manipulation_score, reward, utility, validate_weights)
from reputation.reputation import initial_reputation, update_reputation

PHI = np.array([0.5, -0.3, 0.05, 0.0, -0.15])
WEIGHTS = {"alpha": 0.30, "beta": 0.25, "gamma": 0.15, "delta": 0.10, "lambda": 0.20}


# ---- fidelity -------------------------------------------------------------
def test_fidelity_perfect_match():
    assert fidelity(truthful_explanation(PHI, 2), PHI, 2) == 1.0


def test_fidelity_empty_explanation_is_zero():
    assert fidelity([], PHI, 2) == 0.0


def test_fidelity_zero_shap_denominator():
    zeros = np.zeros(4)
    assert fidelity([(0, 0)], zeros, 2) == 1.0
    assert fidelity([], zeros, 2) == 0.0


def test_fidelity_partial_and_wrong_sign():
    assert fidelity([(0, 1), (4, -1)], PHI, 2) == pytest.approx(0.65 / 0.8)
    assert fidelity([(0, -1), (1, -1)], PHI, 2) == pytest.approx(0.3 / 0.8)   # sign of f0 wrong
    assert fidelity([(0, 1), (0, -1)], PHI, 2) == 0.0                          # contradictory


def test_fidelity_bounded_and_falsified_is_zero():
    assert fidelity(falsified_explanation(PHI, 2), PHI, 2) == 0.0
    rng = np.random.default_rng(0)
    for _ in range(200):
        phi = rng.normal(size=6)
        feats = rng.choice(6, size=3, replace=False)
        expl = [(int(f), int(rng.choice([-1, 1]))) for f in feats]
        assert 0.0 <= fidelity(expl, phi, 2) <= 1.0


# ---- evidence support -----------------------------------------------------
def test_tercile_levels_and_evidence_support():
    train = np.arange(1, 10, dtype=float).reshape(-1, 1)       # terciles at 3.67 and 6.33
    cuts = tercile_thresholds(train)
    assert observed_level(2.0, cuts[0, 0], cuts[1, 0]) == "low"
    assert observed_level(5.0, cuts[0, 0], cuts[1, 0]) == "mid"
    assert observed_level(9.0, cuts[0, 0], cuts[1, 0]) == "high"
    x = np.array([9.0])
    assert evidence_support([(0, "high")], x, cuts) == 1.0
    assert evidence_support([(0, "low")], x, cuts) == 0.0
    assert evidence_support([(0, "high"), (0, "mid")], x, cuts) == 0.5
    assert evidence_support([], x, cuts) == 0.0


def test_truthful_and_unsupported_evidence():
    train = np.arange(30, dtype=float).reshape(10, 3)
    cuts = tercile_thresholds(train)
    x = np.array([0.0, 14.0, 29.0])
    expl = [(0, 1), (2, -1)]
    assert evidence_support(truthful_evidence(expl, x, cuts), x, cuts) == 1.0
    false_claims = unsupported_evidence(expl, x, cuts)
    assert false_claims == [(0, "high"), (2, "low")]
    assert evidence_support(false_claims, x, cuts) == 0.0


# ---- consistency ----------------------------------------------------------
def test_jaccard():
    assert jaccard({1, 2}, {1, 2}) == 1.0
    assert jaccard({1, 2}, {3}) == 0.0
    assert jaccard({1, 2}, {2, 3}) == pytest.approx(1 / 3)
    assert jaccard(set(), set()) == 1.0


def test_consistency_identical_and_disjoint():
    X = np.array([[0.0], [0.1], [5.0], [5.1]])
    same = [frozenset({(0, 1)})] * 4
    assert consistency(X, same, n_neighbours=1) == 1.0
    # nearest neighbours are (0,1) and (2,3); explanations differ within each pair
    differ = [frozenset({(0, 1)}), frozenset({(1, 1)}), frozenset({(0, 1)}), frozenset({(1, 1)})]
    assert consistency(X, differ, n_neighbours=1) == 0.0
    grouped = [frozenset({(0, 1)}), frozenset({(0, 1)}), frozenset({(1, 1)}), frozenset({(1, 1)})]
    assert consistency(X, grouped, n_neighbours=1) == 1.0
    assert np.isnan(consistency(X[:1], same[:1]))


# ---- collective decision and contribution ---------------------------------
def test_collective_decision_weighting_and_ties():
    assert collective_decision([1, 1, 2], [0.4, 0.4, 0.9], [1, 1, 1], 3) == 2
    assert collective_decision([1, 1, 2], [0.5, 0.5, 0.9], [1, 1, 1], 3) == 1
    assert collective_decision([1, 2], [0.5, 0.5], [1, 1], 3) == 1        # tie -> lower index
    assert collective_decision([1, 2], [0.5, 0.5], [0.2, 1.0], 3) == 2    # reputation weight
    assert collective_decision([1, 2], [0.5, 0.5], [0, 0], 3) == 0        # no weight -> idle


def test_contributions_pivotal_cases():
    # agent 2 alone carries the correct decision (action 2)
    c = contributions([1, 0, 2], [0.3, 0.2, 0.9], [1, 1, 1], 3, reference=2)
    assert c.tolist() == [0.5, 0.5, 1.0]
    # agent 2 forces a wrong decision; without it action 1 (correct) wins
    c = contributions([1, 0, 2], [0.3, 0.2, 0.9], [1, 1, 1], 3, reference=1)
    assert c.tolist() == [0.5, 0.5, 0.0]


# ---- strategies -----------------------------------------------------------
def test_honest_report_is_model_output():
    proba = np.array([0.2, 0.7, 0.1])
    assert choose_report("honest", proba, 2, np.array([0, 0, 1.0])) == (1, 0.7, TRUTHFUL)


def test_strategic_deviates_only_above_threshold():
    proba = np.array([0.2, 0.7, 0.1])
    assert choose_report("strategic", proba, 2, np.array([0.0, 0.9, 1.0])) == (1, 0.7, TRUTHFUL)
    vote, conf, style = choose_report("strategic", proba, 2, np.array([0.0, 0.5, 1.0]))
    assert (vote, style) == (2, TRUTHFUL) and conf == pytest.approx(0.4)
    vote, conf, _ = choose_report("strategic", np.array([0.1, 0.1, 0.8]), 1, np.array([0, 1.0, 0]))
    assert vote == 1 and conf == pytest.approx(0.4)


def test_manipulative_report_and_unknown_strategy():
    assert choose_report("manipulative", np.array([0.2, 0.7, 0.1]), 2,
                         np.array([0, 0, 1.0])) == (2, 1.0, FALSIFIED)
    with pytest.raises(ValueError):
        choose_report("random", np.array([1.0, 0, 0]), 0, np.zeros(3))


def test_explanations_never_touch_the_observation():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    before = x.copy()
    cuts = tercile_thresholds(np.arange(50, dtype=float).reshape(10, 5))
    expl = falsified_explanation(PHI, 2)
    unsupported_evidence(expl, x, cuts)
    truthful_evidence(truthful_explanation(PHI, 2), x, cuts)
    assert (x == before).all()
    assert [f for f, _ in expl] == [3, 2]            # the two smallest |SHAP|
    assert expl[1][1] == -1                          # sign of feature 2 flipped


def test_collusive_vote():
    assert collusive_vote([0.0, 1.0, 0.4], [0.0, 0.2, 1.0]) == 2
    assert collusive_vote([1.0, 0.0, 0.0], [0.0, 1.0, 0.0]) == 0     # tie -> lower index


# ---- manipulation ---------------------------------------------------------
def test_collusion_flags():
    assert collusion_flags([2, 2, 1, 0], [1, 0, 1, 0]).tolist() == [1, 1, 0, 0]
    assert collusion_flags([2, 1, 1, 0], [1, 1, 1, 0]).tolist() == [0, 0, 0, 0]   # lone deviator
    assert collusion_flags([2, 1, 0], [1, 2, 0]).tolist() == [0, 0, 0]            # different votes


def test_manipulation_components_per_attack():
    comp = manipulation_components(
        fidelity=[1.0, 0.0, 1.0], evidence=[1.0, 0.0, 1.0], confidence=[0.7, 1.0, 0.9],
        model_probability_of_vote=[0.7, 0.1, 0.6], votes=[1, 2, 2], model_votes=[1, 1, 1])
    assert set(comp) == set(ATTACKS)
    assert comp["false_attribution"].tolist() == [0, 1, 0]
    assert comp["unsupported_evidence"].tolist() == [0, 1, 0]
    assert comp["confidence_inflation"] == pytest.approx([0, 0.9, 0.3])
    assert comp["strategic_voting"].tolist() == [0, 1, 1]
    assert comp["collusion"].tolist() == [0, 1, 1]
    M = manipulation_score(comp)
    assert M[0] == 0.0 and M[1] == pytest.approx((1 + 0.9 + 1 + 1 + 1) / 5)
    assert ((M >= 0) & (M <= 1)).all()


# ---- utility --------------------------------------------------------------
def test_utility_formula_and_bounds():
    u = utility([1, 0], [1, 0], [1, 0], [1, 0.5], [0, 1], WEIGHTS)
    assert u[0] == pytest.approx(0.80) and u[1] == pytest.approx(0.05 - 0.20)
    with pytest.raises(ValueError):
        utility([1.2], [0], [0], [0], [0], WEIGHTS)


def test_weights_validation():
    assert validate_weights(WEIGHTS) == WEIGHTS
    with pytest.raises(ValueError):
        validate_weights({**WEIGHTS, "beta": None})
    with pytest.raises(ValueError):
        validate_weights({**WEIGHTS, "lambda": -0.1})


# ---- reward ---------------------------------------------------------------
def test_reward_min_max():
    assert reward([0.2, 0.5, 0.8]) == pytest.approx([0.0, 0.5, 1.0])
    assert reward([-0.2, 0.8]).tolist() == [0.0, 1.0]


def test_reward_degenerate_case():
    assert reward([0.3, 0.3, 0.3]).tolist() == [0.5, 0.5, 0.5]
    assert reward([0.3, 0.3], degenerate_value=0.0).tolist() == [0.0, 0.0]
    assert reward([0.7]).tolist() == [0.5]


# ---- reputation -----------------------------------------------------------
def test_reputation_update_rule():
    rep = initial_reputation(3)
    assert rep.tolist() == [0.5, 0.5, 0.5]
    rep = update_reputation(rep, [1.0, 0.0, 0.5], rho=0.8)
    assert rep == pytest.approx([0.6, 0.4, 0.5])


def test_reputation_bounds_and_convergence():
    rep = initial_reputation(2)
    for _ in range(200):
        rep = update_reputation(rep, [1.0, 0.0], rho=0.8)
        assert ((rep >= 0) & (rep <= 1)).all()
    assert rep == pytest.approx([1.0, 0.0], abs=1e-9)
    assert update_reputation([0.3], [0.9], rho=1.0).tolist() == [0.3]
    assert update_reputation([0.3], [0.9], rho=0.0).tolist() == [0.9]


def test_reputation_rejects_invalid_input():
    with pytest.raises(ValueError):
        update_reputation([0.5], [1.5])
    with pytest.raises(ValueError):
        update_reputation([0.5], [0.5], rho=1.2)
    with pytest.raises(ValueError):
        initial_reputation(2, initial=-0.1)
