# Explanation-Aware Incentive Mechanism for Trustworthy Multi-Agent AI with Blockchain Provenance

Research code. The execution plan is in `CLAUDE.md`; progress and decisions are in
`docs/research_log.md`. **Status: Phases 0–1 done; no experiment has been run yet.**

## Environment

Python 3.12, dependencies pinned in `requirements.txt`.

```bash
python -m venv <venv-dir>
<venv-dir>/Scripts/python -m pip install -r requirements.txt
```

## Data

Raw files live in `data/raw/` and are never modified. Sources, licences, citations and
SHA-256 hashes are in `data/metadata/datasets.json`; the audit is `docs/dataset_audit.md`.

| Dataset | File | SHA-256 |
|---|---|---|
| Pharma (figshare 6971474) | `data/raw/pharma/Table 1.xls` | `7f389937757bacdda8c72890980a8bc6eb465ac7c738531881b362e755eaa470` |
| Energy (Mendeley bvp4vrn9gc v1) | `data/raw/energy/Case_Study_OptiREC.xlsx` | `b61c6049fca02d9e58ca280f3484ff7c9c83219ba08db6d6485e20d0817ed09a` |

## Commands

```bash
pytest -q
python run_experiment.py --config configs/pharma_baseline.yaml
```

`run_experiment.py` writes per-seed results and a manifest (config, seeds, dataset hashes)
to `results/raw/<config name>/`. Experiments that are not implemented yet exit with code 2
and produce no result files.
