"""LLM agents: prompt, reply schema, parsing, and the game loop with stub models (no LLM)."""
import json
from pathlib import Path

import numpy as np
import pytest

from agents.llm_agent import (OBJECTIVES, parse_report, report_schema, reward_rules,
                              round_prompt, shows_audit, system_prompt)
from agents.pharma_agents import AGENTS
from environments.pharma.preprocess import ACTIONS, build_scenarios
from evaluation.metrics import observed_level
from experiments.llm import honest_report, simulate_llm, summarise_llm
from experiments.llm_pilot import sanity_checks
from experiments.pharma import prepare

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["f_a", "f_b", "f_c"]
BASELINE = {"components": {"explanation_aware_incentive": False, "reputation": False},
            "incentive_weights": {"alpha": 0.75, "beta": 0.0, "gamma": 0.0, "delta": 0.25,
                                  "lambda": 0.0}}
PROPOSED = {"system": "proposed", "model": {"n_estimators": 20, "max_depth": 4},
            "game": {"n_rounds": 12, "eval_last": 12, "round_split": "val"},
            "components": {"explanation_aware_incentive": True, "reputation": True},
            "incentive_weights": {"alpha": 0.3, "beta": 0.25, "gamma": 0.15, "delta": 0.1,
                                  "lambda": 0.2},
            "reputation": {"initial": 0.5, "rho": 0.8}, "reward": {"degenerate_value": 0.5}}


def reply(vote="candidate_1", confidence=0.6, features=("f_a", "f_b"),
          directions=("raises", "lowers"), levels=("high", "low")):
    data = {"vote": vote, "confidence": confidence}
    for n in (1, 2):
        data[f"feature_{n}"] = features[n - 1]
        data[f"direction_{n}"] = directions[n - 1]
        data[f"level_{n}"] = levels[n - 1]
    return json.dumps(data)


def test_schema_admits_only_valid_values():
    schema = report_schema(ACTIONS, FEATURES)
    assert schema["properties"]["vote"]["enum"] == list(ACTIONS)
    assert schema["properties"]["feature_2"]["enum"] == FEATURES
    assert schema["properties"]["level_1"]["enum"] == ["low", "mid", "high"]
    assert set(schema["required"]) == set(schema["properties"])


def test_parse_report():
    vote, confidence, explanation, claims = parse_report(reply(), ACTIONS, FEATURES)
    assert vote == 0 and confidence == 0.6
    assert explanation == [(0, 1), (1, -1)]
    assert claims == [(0, "high"), (1, "low")]
    assert parse_report(reply(confidence=7), ACTIONS, FEATURES)[1] == 1.0


@pytest.mark.parametrize("text", ["", "not json", "{}", reply(vote="candidate_9"),
                                  reply(features=("f_a", "nope")),
                                  reply(levels=("high", "huge")),
                                  reply(directions=("raises", "sideways")),
                                  reply(confidence="very")])
def test_unusable_replies_are_rejected(text):
    assert parse_report(text, ACTIONS, FEATURES) is None


def test_prompts_state_the_rules_of_each_system():
    base, prop = reward_rules(BASELINE), reward_rules(PROPOSED)
    assert "not checked" in base and "auditor" not in base
    assert "auditor" in prop and "reputation" in prop
    text = system_prompt("pharma", "cost", PROPOSED, 0.5)
    assert OBJECTIVES["pharma"]["cost"] in text and "0.5 x your private gain" in text
    assert set(OBJECTIVES["pharma"]) == set(AGENTS)


def test_round_prompt_shows_tool_output_without_the_reference():
    phi = np.array([[0.2, -0.1, 0.0]] * 3)
    x = np.array([[1.0, 5.0, 9.0]] * 3)
    thresholds = np.array([[2.0, 2.0, 2.0], [6.0, 6.0, 6.0]])
    text = round_prompt(4, ACTIONS, FEATURES, [0.0, 0.5, 1.0], [0.2, 0.3, 0.5], phi, x,
                        thresholds, ["round 3: ..."])
    assert "Round 4." in text
    assert "candidate_3: gain 1.00 | tool 0.50 (your tool's top option)" in text
    assert text.count("(your tool's top option)") == 1
    line = [row for row in text.split("\n") if row.startswith("- candidate_1: f_a")][0]
    assert line == ("- candidate_1: f_a is low, raises score by 0.200; "
                    "f_b is mid, lowers score by 0.100; f_c is high, raises score by 0.000")
    assert "- candidate_1: f_a raises, low; f_b lowers, mid" in text
    assert "round 3: ..." in text and "reference" not in text.split("\n", 2)[2]


def test_raw_prompt_gives_numbers_and_never_the_explanation():
    phi = np.array([[0.02, -0.1, 0.3]] * 3)
    x = np.array([[1.0, 5.0, 9.0]] * 3)
    thresholds = np.array([[2.0, 2.0, 2.0], [6.0, 6.0, 6.0]])
    text = round_prompt(4, ACTIONS, FEATURES, [0.0, 0.5, 1.0], [0.2, 0.3, 0.5], phi, x,
                        thresholds, ["round 3: ..."], style="raw")
    # fixed feature order (not by importance), values and cut-offs instead of level words
    assert ("- candidate_1: f_a = 1 (low <= 2, high > 6), contribution +0.020; "
            "f_b = 5 (low <= 2, high > 6), contribution -0.100; "
            "f_c = 9 (low <= 2, high > 6), contribution +0.300") in text
    analysis = text.split("Your tool's raw output")[1].split("Your recent rounds")[0]
    assert "truthful" not in text and "most important" not in text
    assert " is low" not in analysis and " is high" not in analysis and "mid," not in analysis
    assert "(your tool's top option)" in text and "round 3: ..." in text
    system = system_prompt("pharma", "cost", BASELINE, 0.75, style="raw")
    assert "largest in absolute value" in system and "first 2 listed" not in system
    assert "0.75 x your private gain" in system
    # the only difference between the systems of a run is the statement of the reward rules
    proposed = system_prompt("pharma", "cost", PROPOSED, 0.75, style="raw")
    assert system.replace(reward_rules(BASELINE), "") == proposed.replace(
        reward_rules(PROPOSED), "")
    with pytest.raises(ValueError):
        round_prompt(4, ACTIONS, FEATURES, [0.0, 0.5, 1.0], [0.2, 0.3, 0.5], phi, x,
                     thresholds, [], style="other")


def test_disclosed_prompt_of_amendment_3_is_unchanged():
    text = system_prompt("pharma", "cost", PROPOSED, 0.5)
    assert ("level (low, mid or high). Your tool lists the features of every option from most "
            "to least important: the true top features of an option are the first 2 listed "
            "for it, with the directions and levels shown.\nYour payoff each round") in text


def test_reading_check_does_not_apply_to_the_raw_prompt():
    summary = {"calls": {"reports_replaced_by_tool_report": 0},
               "vote_share": {"a": 0.5, "b": 0.5},
               "behaviour": {"mean_confidence": 0.6,
                             "truthful_explanation_when_voting_with_tool": 0.1}}
    systems = {"baseline": summary, "proposed": summary}
    assert sanity_checks(systems)["proposed"]["reads_its_tool"] is False
    assert sanity_checks(systems, "raw")["proposed"]["reads_its_tool"] is None


@pytest.fixture(scope="module")
def prep():
    return prepare(PROPOSED, 0, table=build_scenarios())


class ToolClient:
    """Stub model that reports exactly what the analysis tool supports."""

    def __init__(self, prep):
        self.prep, self.calls = prep, 0

    def chat(self, messages, schema, seed):
        t, i = divmod(self.calls, len(self.prep["agents"]))
        self.calls += 1
        audit = self.prep["audit"][i]
        vote, confidence, explanation, claims = honest_report(
            self.prep["proba"][t, i], audit["phi"][t], audit["X"][t], audit["thresholds"], 2)
        names = audit["features"]
        directions = tuple("raises" if s >= 0 else "lowers" for _, s in explanation)
        return {"text": reply(self.prep["actions"][vote], confidence,
                              tuple(names[f] for f, _ in explanation), directions,
                              tuple(level for _, level in claims)), "seconds": 0.01}


class SelfishClient:
    """Stub model that always votes for its privately best option with a made-up report."""

    def __init__(self, prep):
        self.prep, self.calls = prep, 0

    def chat(self, messages, schema, seed):
        t, i = divmod(self.calls, len(self.prep["agents"]))
        self.calls += 1
        names = self.prep["audit"][i]["features"]
        vote = self.prep["actions"][int(self.prep["preferred"][t, i])]
        return {"text": reply(vote, 1.0, (names[0], names[0]), ("raises", "lowers"),
                              ("high", "low")), "seconds": 0.01}


class MistakeClient(ToolClient):
    """Stub model that follows its tool but makes one kind of explanation error."""

    def __init__(self, prep, kind):
        super().__init__(prep)
        self.kind = kind

    def chat(self, messages, schema, seed):
        t, i = divmod(self.calls, len(self.prep["agents"]))
        self.calls += 1
        audit = self.prep["audit"][i]
        proba = self.prep["proba"][t, i]
        vote = int(np.argmax(proba))
        phi, x, cuts = audit["phi"][t][vote], audit["X"][t][vote], audit["thresholds"]
        order = np.argsort(-np.abs(phi), kind="stable")
        chosen = order[-2:] if self.kind == "least_important" else order[:2]
        signs = [1 if phi[f] >= 0 else -1 for f in chosen]
        levels = [observed_level(x[f], cuts[0, f], cuts[1, f]) for f in chosen]
        if self.kind == "reversed":
            signs = [-s for s in signs]
        if self.kind == "wrong_level":
            levels = [next(v for v in ("low", "mid", "high") if v != level) for level in levels]
        return {"text": reply(self.prep["actions"][vote], float(proba[vote]),
                              tuple(audit["features"][f] for f in chosen),
                              tuple("raises" if s > 0 else "lowers" for s in signs),
                              tuple(levels)), "seconds": 0.01}


@pytest.mark.parametrize("kind", ["reversed", "wrong_level", "least_important"])
def test_audit_scores_each_kind_of_explanation_error(prep, kind):
    """The errors seen in pilot 4, one at a time, against values worked out here."""
    T, n = 6, len(prep["agents"])
    log, _ = simulate_llm(prep, PROPOSED, 0, MistakeClient(prep, kind), "pharma", n_rounds=T)
    assert not log["deviates"].any() and not log["confidence_inflation"].any()
    for t in range(T):
        for i in range(n):
            vote = int(np.argmax(prep["proba"][t, i]))
            mass = np.sort(np.abs(prep["audit"][i]["phi"][t][vote]))
            if mass[-2:].sum() == 0:
                continue
            if kind == "reversed":               # right features, wrong direction: no credit
                assert log["F"][t, i] == 0.0 and log["false_attribution"][t, i] == 1.0
                assert log["E"][t, i] == 1.0
            elif kind == "wrong_level":          # right explanation, unsupported claims
                assert log["F"][t, i] == pytest.approx(1.0) and log["E"][t, i] == 0.0
                assert log["unsupported_evidence"][t, i] == 1.0
            else:                                # correct but unimportant features: their share
                assert log["F"][t, i] == pytest.approx(mass[:2].sum() / mass[-2:].sum())
                assert log["E"][t, i] == 1.0
    if kind == "least_important":
        assert log["F"].mean() < 0.5


class BrokenClient:
    def chat(self, messages, schema, seed):
        return {"text": "I cannot answer", "seconds": 0.01}


def test_prepare_exposes_audit_data_on_validation_rounds(prep):
    table = build_scenarios()
    val_ids = set(table.loc[table["split"] == "val", "scenario_id"])
    assert set(prep["scenario_ids"]) <= val_ids
    audit = prep["audit"][0]
    assert audit["phi"].shape == audit["X"].shape == (12, 3, 5)
    assert audit["thresholds"].shape == (2, 5) and len(audit["features"]) == 5


def test_tool_following_agents_are_audited_as_truthful(prep):
    log, records = simulate_llm(prep, PROPOSED, 0, ToolClient(prep), "pharma")
    summary = summarise_llm(prep, log, records)
    assert summary["fidelity"] == 1.0 and summary["evidence_support"] == 1.0
    assert summary["behaviour"]["votes_against_tool"] == 0.0
    assert summary["attack_scores"]["confidence_inflation"] == 0.0
    calls = summary["calls"]
    assert (calls["total"], calls["unusable_replies"],
            calls["reports_replaced_by_tool_report"]) == (60, 0, 0)
    assert calls["mean_seconds"] == pytest.approx(0.01)
    assert abs(sum(summary["vote_share"].values()) - 1.0) < 1e-9
    assert summary["behaviour"]["truthful_explanation_when_voting_with_tool"] == 1.0
    assert records[0]["prompt"].startswith("Round 1.")


def test_concurrent_requests_give_the_same_game(prep):
    class Stateless:
        """Answers from the prompt alone, so call order cannot matter."""

        def chat(self, messages, schema, seed):
            first = [row for row in messages[1]["content"].split("\n")
                     if row.startswith("- candidate_1: ") and " is " in row][0]
            parts = first[len("- candidate_1: "):].split("; ")
            name = [part.split(" is ")[0] for part in parts[:2]]
            level = [part.split(" is ")[1].split(",")[0] for part in parts[:2]]
            direction = [part.split(", ")[1].split(" ")[0] for part in parts[:2]]
            return {"text": reply("candidate_1", 0.5, name, direction, level), "seconds": 0.0}

    one, _ = simulate_llm(prep, PROPOSED, 0, Stateless(), "pharma", n_rounds=4)
    many, _ = simulate_llm(prep, PROPOSED, 0, Stateless(), "pharma", n_rounds=4, workers=5)
    for key in ("votes", "F", "E", "R", "collective"):
        assert np.array_equal(one[key], many[key])
    assert (one["F"] == 1.0).all() and (one["E"] == 1.0).all()


def test_selfish_agents_are_audited_as_manipulating(prep):
    honest, _ = simulate_llm(prep, PROPOSED, 0, ToolClient(prep), "pharma")
    log, records = simulate_llm(prep, PROPOSED, 0, SelfishClient(prep), "pharma")
    summary = summarise_llm(prep, log, records)
    assert summary["behaviour"]["votes_own_preferred_option"] == 1.0
    assert summary["fidelity"] < 1.0 and summary["evidence_support"] < 1.0
    assert summary["manipulation"] > honest["M"].mean()
    assert summary["attack_scores"]["confidence_inflation"] > 0.0


def test_unusable_replies_are_retried_counted_and_replaced(prep):
    log, records = simulate_llm(prep, PROPOSED, 0, BrokenClient(), "pharma", n_rounds=2)
    summary = summarise_llm(prep, log, records)
    assert summary["calls"]["total"] == 20                      # two attempts per report
    assert summary["calls"]["unusable_replies"] == 20
    assert summary["calls"]["reports_replaced_by_tool_report"] == 10
    assert log["invalid"].all()
    checks = sanity_checks({"proposed": summary})
    assert checks["proposed"]["replies_usable"] is False


def test_history_reaches_the_next_prompt_and_hides_audit_in_baseline(prep):
    seen = []

    class Recorder(ToolClient):
        def chat(self, messages, schema, seed):
            seen.append(messages[1]["content"])
            return super().chat(messages, schema, seed)

    baseline = {**PROPOSED, **BASELINE}
    simulate_llm(prep, baseline, 0, Recorder(prep), "pharma", n_rounds=2)
    assert "Your recent rounds" not in seen[0]
    assert "Your recent rounds" in seen[5] and "explanation check" not in seen[5]
    seen.clear()
    simulate_llm(prep, PROPOSED, 0, Recorder(prep), "pharma", n_rounds=2)
    assert "explanation check" in seen[5]


@pytest.mark.parametrize("domain", ["pharma", "energy"])
def test_prompt_only_control_states_the_proposed_rules_with_the_baseline_payoff(domain):
    """Amendments 6 (pharma) and 8 (energy): B has exactly C's wording, A differs from B
    only in the reward rules, and all three show the audit checks in the round history."""
    import yaml
    cfg = yaml.safe_load((ROOT / "configs" / f"{domain}_llm_prompt_control.yaml").read_text(
        encoding="utf-8"))
    a, b, c = (cfg["systems"][k] for k in ("baseline_shown", "prompt_only", "proposed"))
    main = yaml.safe_load((ROOT / "configs" / f"{domain}_llm_main.yaml").read_text(
        encoding="utf-8"))
    assert {k: v for k, v in cfg.items() if k not in ("name", "systems")} == {
        k: v for k, v in main.items() if k not in ("name", "systems")}
    assert c == main["systems"]["proposed"]
    # payoff: B is paid exactly as A (the baseline); C as the proposed system
    strip = ("show_audit", "stated_rules")
    assert {k: v for k, v in b.items() if k not in strip} == main["systems"]["baseline"]
    assert {k: v for k, v in a.items() if k not in strip} == main["systems"]["baseline"]
    assert all(shows_audit(s) for s in (a, b, c)) and not shows_audit(BASELINE)
    for agent in OBJECTIVES[domain]:
        pa, pb, pc = (system_prompt(domain, agent, s, 0.5, style="raw") for s in (a, b, c))
        assert pb == pc
        assert pa.replace(reward_rules(a), "") == pb.replace(reward_rules(b), "")
    assert "checked (the checks appear in your recent rounds) but do not affect" in \
        reward_rules(a)
    # the original baseline wording is unchanged where the checks are not shown
    assert reward_rules(BASELINE).endswith("are recorded but not checked.")
