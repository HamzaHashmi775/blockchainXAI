# Research Log

## 2026-10-05 — Phase 0 (project setup) and Phase 1 (dataset acquisition and audit)

### Phase 0 — completed
- Repository structure from CLAUDE.md §2 created in the project root (plus `utils/`).
- `requirements.txt` pinned from the working environment (Python 3.12.10).
- `utils/seed.py`, `run_experiment.py` (`--config`), eight config stubs in `configs/`
  (pharma/energy × baseline/proposed/ablation/adversarial). Stubs carry seeds 0–9 and the
  component switches; incentive weights are `null` until the protocol is frozen.
- `run_experiment.py` refuses to emit results for an unimplemented experiment (writes a
  manifest with `status: not_implemented`, exit code 2) so no placeholder numbers can exist.
- **GATE 0 met:** structure exists, `pytest` runs, `run_experiment.py --help` works.

Deviations / environment notes:
- Drive C: had ~120 MB free; installing dependencies there failed with "No space left on
  device". The virtual environment lives at `D:\xai-incentive-env\venv` (pip cache and temp
  alongside it). Run everything with `D:\xai-incentive-env\venv\Scripts\python.exe`.
- Blockchain dependency not pinned yet: plan is a documented hash-chain simulator on
  `hashlib` (allowed by Phase 0 step 2); decided finally in Phase 8.

### Phase 1 — audit completed; GATE 1 waiting on a user decision
- Both primary datasets downloaded (figshare and Mendeley were reachable). Hashes match the
  repositories' checksums. Metadata in `data/metadata/`. Raw files marked read-only.
- Full audit in `docs/dataset_audit.md`. Loaders + schema tests in `utils/datasets.py`,
  `tests/test_datasets.py`.

Findings:
1. **Pharma (blocking, Gap P-1).** The specified file is a 24-row list of criteria *names*
   (Table 1 of Forghani et al. 2018). It has no suppliers, no numeric values, no decisions.
   The pharma environment cannot be built from it.
2. The same study's other tables (2–11, CC BY) were downloaded to
   `data/raw/pharma_paper_tables_candidate/` **only to characterise the gap**. They hold the
   study's real data: 34 questionnaire respondents × 24 criteria, and 4 suppliers × 4
   criteria × 2 decision makers (linguistic Z-number ratings), plus the Z-TOPSIS ranking and
   sensitivity tables. Not adopted.
3. **Energy.** Rich and complete (8760 h, 55 users, 206-bus feeder, no missing values).
   It is optimisation *input* data: no observed trades, clearing prices, or storage dispatch,
   so the energy ground truth will be a constructed reference. Only 22 distinct demand
   profiles and 3 distinct thermal profiles among 55 users. No data dictionary or units in
   the file; several column meanings are inferred and flagged.

Open questions (for the user):
- Q1. How to resolve Gap P-1: (A) adopt the paper's Tables 2–11; (B) a different real
  supplier-level pharma dataset; (C) run energy first and defer pharma.
- Q2. If (A): accept fewer than five real-variable pharma agents (delivery and compliance
  have no supplier-level data), or how else to define the fifth agent?

Not yet verified:
- Article text of Forghani et al. (2018) has not been read (the `F` rating label in Tables
  7–8 is absent from the Table 4 scale; MILP inputs may or may not be published).
- Companion paper of the energy dataset (units, column definitions, whether profiles are
  metered or modelled) has not been read.

Tests: `pytest -q` → 28 passed.

Next step: Phase 2 (literature matrix, research gap, protocol). The protocol cannot be
frozen until Q1/Q2 are answered.
