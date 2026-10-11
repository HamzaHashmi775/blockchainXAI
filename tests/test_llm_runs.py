"""LLM-agent experiment runners and their statistics, with a stub model (no LLM)."""
import importlib.util
import json
import re
from pathlib import Path

import numpy as np
import pytest
import yaml

from experiments import REGISTRY
from experiments.llm_runs import make_client, register_llm_domain
from run_experiment import main

ROOT = Path(__file__).resolve().parents[1]


ITEM = re.compile(r"(\w+) = (\S+) \(low <= (\S+), high > (\S+)\), contribution ([+-]\d+\.\d+)")


class ReadNumbers:
    """Stub model: votes for the tool's top option and works the explanation out of the
    numbers of the raw prompt (two largest absolute contributions, sign, level)."""

    def chat(self, messages, schema, seed):
        rows = messages[1]["content"].split("\n")
        assert not any("truthful" in r for r in rows)
        tool = {r.split(":")[0][2:]: float(r.split("| tool ")[1].split(" ")[0])
                for r in rows if "| tool" in r}
        vote = next(r for r in rows if r.endswith("(your tool's top option)")).split(":")[0][2:]
        line = next(r for r in rows if r.startswith(f"- {vote}: ") and "contribution" in r)
        items = sorted(ITEM.findall(line), key=lambda m: -abs(float(m[4])))[:2]
        data = {"vote": vote, "confidence": tool[vote]}
        for n, (name, value, low, high, contribution) in enumerate(items, start=1):
            level = ("low" if float(value) <= float(low)
                     else "high" if float(value) > float(high) else "mid")
            data.update({f"feature_{n}": name, f"level_{n}": level,
                         f"direction_{n}": "raises" if float(contribution) >= 0 else "lowers"})
        return {"text": json.dumps(data), "seconds": 0.0}


def stub_factory(llm):
    return ReadNumbers(), {"model": llm["model"], "digest": llm["digest"]}


@pytest.fixture(scope="module")
def results(tmp_path_factory):
    out = tmp_path_factory.mktemp("llm")
    register_llm_domain("pharma", client_factory=stub_factory)
    try:
        for kind, seeds in (("main", [0, 1, 2]), ("adversarial", [0, 1, 2])):
            cfg = yaml.safe_load((ROOT / "configs" / f"pharma_llm_{kind}.yaml").read_text("utf-8"))
            cfg["seeds"] = seeds
            cfg["model"] = {"n_estimators": 10, "max_depth": 3}
            cfg["game"] = {**cfg["game"], "n_rounds": 8, "eval_last": 8}
            if kind == "adversarial":
                cfg["adversarial"]["rounds"] = 4
            path = out / f"{kind}.yaml"
            path.write_text(yaml.safe_dump(cfg))
            assert main(["--config", str(path), "--output-dir", str(out)]) == 0
    finally:
        register_llm_domain("pharma")
    return out


def test_frozen_configs_match_the_protocol():
    for domain in ("pharma", "energy"):
        cfg = yaml.safe_load((ROOT / "configs" / f"{domain}_llm_main.yaml").read_text("utf-8"))
        assert cfg["seeds"] == [0, 1, 2, 3, 4] and cfg["game"]["n_rounds"] == 200
        assert list(cfg["systems"]) == ["baseline", "ablation", "proposed"]
        assert cfg["llm"]["model"] == "qwen2.5:7b" and cfg["llm"]["temperature"] == 0.0
        assert cfg["llm"]["digest"].startswith("845dbda0ea48")
        classical = yaml.safe_load((ROOT / "configs" / f"{domain}_proposed.yaml").read_text())
        assert cfg["systems"]["proposed"]["incentive_weights"] == classical["incentive_weights"]
        adv = yaml.safe_load((ROOT / "configs" / f"{domain}_llm_adversarial.yaml").read_text())
        assert adv["seeds"] == [0, 1, 2] and adv["adversarial"]["rounds"] == 100
        assert adv["adversarial"]["malicious_fractions"] == [0.2, 0.4]
        assert f"{domain}_llm_main" in REGISTRY and f"{domain}_llm_adversarial" in REGISTRY
        # amendment 4: raw prompt everywhere; natural condition at omega 0.5
        assert cfg["llm"]["prompt_style"] == adv["llm"]["prompt_style"] == "raw"
        assert cfg["game"]["omega"] == adv["game"]["omega"] == 0.5
    main_cfg = yaml.safe_load((ROOT / "configs" / "pharma_llm_main.yaml").read_text("utf-8"))
    higher = yaml.safe_load((ROOT / "configs" / "pharma_llm_main_w075.yaml").read_text("utf-8"))
    assert higher["game"]["omega"] == 0.75 and higher["experiment"] == "pharma_llm_main"
    # the higher-private-gain run differs from the main run in omega and name only
    higher["game"]["omega"], higher["name"] = 0.5, "pharma_llm_main"
    assert higher == main_cfg
    assert not (ROOT / "configs" / "energy_llm_main_w075.yaml").exists()


def test_a_wrong_model_digest_is_refused(monkeypatch):
    monkeypatch.setattr("agents.llm_agent.OllamaClient.describe",
                        lambda self: {"model": "qwen2.5:7b", "digest": "something-else"})
    with pytest.raises(RuntimeError, match="refusing to run"):
        make_client({"model": "qwen2.5:7b", "digest": "845d", "temperature": 0.0,
                     "num_predict": 120, "num_ctx": 2048})


def test_main_run_saves_metrics_rounds_and_every_reply(results):
    run = json.loads((results / "pharma_llm_main" / "seed_0.json").read_text())
    assert set(run["systems"]) == {"baseline", "ablation", "proposed"}
    assert run["prompt_style"] == "raw" and run["omega"] == 0.5
    assert set(run["environment"]) >= {"python", "numpy", "sklearn", "shap"}
    for system in run["systems"].values():
        assert len(system["calls"]) == 8 * 5 and len(system["rounds"]["collective"]) == 8
        assert np.array(system["rounds"]["votes"]).shape == (8, 5)
        assert len(system["first_round_prompts"]) == 5
        assert system["metrics"]["fidelity"] > 0.98
        assert "truthful" not in system["first_round_prompts"][0]
        assert system["metrics"]["behaviour"]["votes_against_tool"] == 0.0
    # all systems of a seed play the same rounds
    refs = [s["rounds"]["reference"] for s in run["systems"].values()]
    assert refs[0] == refs[1] == refs[2]
    manifest = json.loads((results / "pharma_llm_main" / "manifest.json").read_text())
    assert manifest["status"] == "completed"


def test_adversarial_run_scripts_the_attackers_only(results):
    run = json.loads((results / "pharma_llm_adversarial" / "seed_0.json").read_text())
    for system in run["systems"].values():
        one, two = system["malicious"]["0.2"], system["malicious"]["0.4"]
        assert len(one["malicious_agents"]) == 1 and len(two["malicious_agents"]) == 2
        assert one["malicious_agents"][0] == two["malicious_agents"][0]
        assert len(one["calls"]) == 4 * 4 and len(two["calls"]) == 4 * 3
        assert one["metrics"]["llm_agents"]["fidelity"] > 0.98
        # the scripted agent falsifies
        assert one["metrics"]["fidelity"] < one["metrics"]["llm_agents"]["fidelity"]
        assert len(system["collusion"]["calls"]) == 4 * 3
        assert system["collusion"]["metrics"]["scripted_agents"]["reward"] is not None
    assert len(run["colluders"]) == 2
    proposed = run["systems"]["proposed"]["collusion"]["metrics"]["scripted_agents"]
    assert proposed["final_reputation"] is not None


def test_resume_skips_finished_seeds(results):
    path = results / "main.yaml"
    before = (results / "pharma_llm_main" / "seed_1.json").stat().st_mtime_ns
    register_llm_domain("pharma", client_factory=stub_factory)
    try:
        assert main(["--config", str(path), "--output-dir", str(results), "--resume"]) == 0
    finally:
        register_llm_domain("pharma")
    assert (results / "pharma_llm_main" / "seed_1.json").stat().st_mtime_ns == before


def test_analysis_runs_on_saved_results(results, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "analyze_llm", ROOT / "statistics" / "analyze_llm.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def load(name):
        folder = results / name
        return {int(p.stem.split("_")[1]): json.loads(p.read_text())
                for p in folder.glob("seed_*.json")}

    monkeypatch.setattr(module, "load", load)
    res = module.analyse("pharma")
    assert res["main"]["n_seeds"] == 3 and res["main"]["calls"]["unusable_replies"] == 0
    assert set(res["main"]["verdicts"]) == {"fidelity", "evidence_support", "manipulation"}
    adv = res["adversarial"]
    assert adv["shares"] == ["0.2", "0.4"] and adv["rounds"] == 4
    assert set(adv["collusion"]) == {"baseline", "proposed"}
    text = module.to_markdown("pharma", res)
    assert "LLM agents" in text and "Collusion" in text and "no confirmatory claim" in text
