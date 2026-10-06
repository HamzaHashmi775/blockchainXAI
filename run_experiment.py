"""Run one experiment from a YAML config.

    python run_experiment.py --config configs/pharma_baseline.yaml

Loads the config, seeds every RNG, runs the registered experiment once per
seed and writes results plus a manifest (config, seeds, dataset hashes) to
`results/raw/<name>/`.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

import experiments.energy  # noqa: F401  (registers the energy experiments)
import experiments.pharma  # noqa: F401  (registers the pharma experiments)
from experiments import REGISTRY
from utils.seed import seed_everything

ROOT = Path(__file__).resolve().parent


def load_config(path):
    with open(path, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    for key in ("name", "experiment", "seeds"):
        if key not in config:
            raise ValueError(f"config {path} is missing required key '{key}'")
    if not config["seeds"]:
        raise ValueError("config must list at least one seed")
    return config


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True, help="path to a YAML config")
    parser.add_argument("--output-dir", default=str(ROOT / "results" / "raw"),
                        help="directory for raw results (default: results/raw)")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    out_dir = Path(args.output_dir) / config["name"]
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": config["name"],
        "experiment": config["experiment"],
        "config_path": str(args.config),
        "config": config,
        "seeds": config["seeds"],
        "dataset_sha256": {p: sha256_file(ROOT / p) for p in config.get("dataset_files", [])},
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }

    runner = REGISTRY.get(config["experiment"])
    if runner is None:
        manifest["status"] = "not_implemented"
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        print(f"experiment '{config['experiment']}' is not implemented yet; "
              f"no results were produced (manifest: {out_dir / 'manifest.json'})", file=sys.stderr)
        return 2

    for seed in config["seeds"]:
        seed_everything(seed)
        result = runner(config, seed)
        (out_dir / f"seed_{seed}.json").write_text(json.dumps(result, indent=2, sort_keys=True))
    manifest["status"] = "completed"
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"wrote {len(config['seeds'])} seed result(s) to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
