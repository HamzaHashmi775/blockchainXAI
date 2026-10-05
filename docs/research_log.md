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

### 2026-10-05 — fix after first commit
- `statistics/__init__.py` made the project folder shadow Python's standard-library
  `statistics` module. Removed the `__init__.py` (folder kept, see `statistics/README.md`);
  importable analysis code will live in `evaluation/`. Regression test added.
- Tests: `pytest -q` → 29 passed.

## 2026-10-05 — GATE 1 decision (user)

Asked the user about Gap P-1. Answers:
- **Q1 → "Energy first, pharma later."** The energy case study is run first; pharma is
  deferred. This is a **deviation from the CLAUDE.md phase order**: Phases 3–8 (pharma) are
  postponed and the Phase 4–8 machinery (game, XAI, metrics, manipulation, incentive, reward,
  reputation, checkpoint) is developed on the energy data. The Critical Checkpoint (Phase 6)
  will be evaluated on energy.
- **Q2 → "4 criteria + reliability."** If/when the source study's Tables 2–11 are used for
  pharma, the five agents are Cost (product price), Quality (product quality), Service (CRM),
  Record/Risk (past record documentation) and a fifth agent on the Z-number reliability
  labels. No Logistics or Compliance agent (no supplier-level data). Whether to adopt those
  tables is still to be confirmed when pharma is taken up.
- GATE 1 satisfied: audit complete, gaps documented, user informed and decided.

## 2026-10-05 — Phase 2 (literature, gap, protocol) completed

- `docs/literature_matrix.csv`: 26 sources, each verified to exist via Crossref or the arXiv
  API (verification channel recorded per row). Rows read only at abstract/metadata level are
  marked; Tian (2025, Sci. Rep.) is metadata-only and must be read before being cited.
- `docs/research_gap.md`: gap is defensible only as "to our knowledge, among works reviewed".
  Closest prior work: MEA (faithfulness as a reward; no strategic agents) and DART
  (blockchain reputation/incentives for LLM agents; no explanation fidelity). The review is
  not systematic.
- `docs/research_protocol.md` v1.0 **frozen** for the energy case study; pharma section
  deferred. `docs/threats_to_validity.md` started.
- Energy companion article (García-Muñoz, Farriol & Eichman 2025, SEGAN,
  doi:10.1016/j.segan.2025.101755) is paywalled; only the repository abstract was read. It
  states the network is a modified IEEE European LV test feeder. Units, column definitions
  and whether profiles are metered remain unverified.
- Design decisions recorded in the protocol: the decision is the community's hourly storage
  action; its ground truth is a constructed reference (daily perfect-foresight LP under
  simulated battery parameters A1–A5); 10%/30% malicious shares are realised in expectation
  because five agents cannot realise them exactly.
- GATE 2 met.

## 2026-10-05 — Energy pipeline implemented (Steps 25–28 and 13–16 on energy)

- `environments/energy/preprocess.py` (features, reference LP, weekly blocked split;
  output `data/processed/energy/`), `agents/energy_agents.py` (five random-forest agents and
  private objectives), `xai/shap_explainer.py` (TreeSHAP), `evaluation/metrics.py`
  (fidelity, evidence, consistency, collective decision, contribution),
  `game/strategies.py`, `incentives/mechanism.py` (five attack scores, utility, reward),
  `reputation/reputation.py`, `experiments/energy.py` (runner, adversarial, collusion,
  unilateral-deviation table). Energy configs carry the frozen protocol values.
- Validation-split accuracy of the agents' models (seed 0): 0.71–0.80 against a majority
  share of about 0.64 — the single-view models are modest predictors of the reference.
- By construction and confirmed by test: truthful reports score F = 1, E = 1; falsified
  reports score F = 0, E = 0. Fidelity/evidence in results therefore mostly reflect *how
  often* agents falsify, not graded explanation quality.
- Tests: `pytest -q` → 74 passed.
