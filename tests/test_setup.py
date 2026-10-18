import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from run_experiment import load_config, main
from utils.seed import model_seed, seed_everything

ROOT = Path(__file__).resolve().parents[1]
# agent-experiment configs; provenance.yaml (Phase 8) records saved runs and has no agents
CONFIGS = sorted(p for p in (ROOT / "configs").glob("*.yaml") if p.stem != "provenance")


def test_seed_everything_is_deterministic():
    rng_a = seed_everything(7)
    a = (random.random(), np.random.rand(), rng_a.random())
    rng_b = seed_everything(7)
    b = (random.random(), np.random.rand(), rng_b.random())
    assert a == b
    seed_everything(8)
    assert random.random() != a[0]


@pytest.mark.parametrize("bad", [-1, 1.5, "3", True, None])
def test_seed_everything_rejects_invalid_seed(bad):
    with pytest.raises(ValueError):
        seed_everything(bad)


def test_model_seed_is_stable_and_name_dependent():
    assert model_seed(1, "cost") == model_seed(1, "cost")
    assert model_seed(1, "cost") != model_seed(1, "quality")
    assert model_seed(1, "cost") != model_seed(2, "cost")


def test_required_config_stubs_exist():
    names = {p.name for p in CONFIGS}
    assert {"pharma_baseline.yaml", "pharma_proposed.yaml", "pharma_adversarial.yaml",
            "energy_proposed.yaml"} <= names


@pytest.mark.parametrize("path", CONFIGS, ids=lambda p: p.name)
def test_config_loads_and_is_paired(path):
    cfg = load_config(path)
    assert cfg["name"] == path.stem
    reference = load_config(ROOT / "configs" / f"{cfg['domain']}_baseline.yaml")
    if "_llm_" in path.stem:
        # protocol amendment 3: 5 seeds (main) or 3 (robustness), a prefix of the others
        expected = 3 if path.stem.endswith("adversarial") else 5
        assert cfg["seeds"] == reference["seeds"][:expected]
    else:
        assert len(cfg["seeds"]) >= 5
        # paired comparison: every classical config of a domain uses the same seeds
        assert cfg["seeds"] == reference["seeds"]
    systems = cfg["systems"].values() if "systems" in cfg else [cfg]
    for system in systems:
        assert set(system["incentive_weights"]) == {"alpha", "beta", "gamma", "delta", "lambda"}
    for rel in cfg["dataset_files"]:
        assert (ROOT / rel).is_file()


def test_baseline_has_no_incentive():
    for domain in ("pharma", "energy"):
        comp = load_config(ROOT / "configs" / f"{domain}_baseline.yaml")["components"]
        assert comp["explanation_aware_incentive"] is False
        assert comp["reputation"] is False and comp["blockchain"] is False


def test_cli_help():
    out = subprocess.run([sys.executable, "run_experiment.py", "--help"], cwd=ROOT,
                         capture_output=True, text=True)
    assert out.returncode == 0 and "--config" in out.stdout


def test_unimplemented_experiment_produces_no_results(tmp_path):
    config = tmp_path / "unregistered.yaml"
    config.write_text("name: unregistered\nexperiment: not_registered\nseeds: [0]\n"
                      "dataset_files: ['data/raw/pharma/Table 1.xls']\n")
    code = main(["--config", str(config), "--output-dir", str(tmp_path)])
    assert code == 2
    files = sorted(p.name for p in (tmp_path / "unregistered").iterdir())
    assert files == ["manifest.json"]
    manifest = json.loads((tmp_path / "unregistered" / "manifest.json").read_text())
    assert manifest["status"] == "not_implemented"
    assert manifest["dataset_sha256"]


def test_missing_config_key_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: x\nseeds: [1]\n")
    with pytest.raises(ValueError):
        load_config(bad)


def test_stdlib_statistics_is_not_shadowed():
    import statistics

    assert hasattr(statistics, "mean")
    assert not (ROOT / "statistics" / "__init__.py").exists()
