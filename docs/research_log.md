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

## 2026-10-05 — Energy main experiment, ablation, robustness; CRITICAL CHECKPOINT

Runs (10 paired seeds each, protocol v1.0, no parameter changed after freezing):
`energy_baseline`, `energy_ablation`, `energy_proposed`, `energy_adversarial`.
Raw results in `results/raw/` (git-ignored; regenerate with `run_experiment.py`), summaries
in `results/summaries/energy_main.json`, `energy_adversarial.json`, tables in `tables/`.
Two seeds of the proposed run were re-executed and matched the saved files exactly.

### Main result (proposed vs baseline; mean over seeds; Holm-adjusted p for F, E, M)
| | Baseline | Ablation | Proposed | Δ (prop − base) | p (Holm) |
|---|---|---|---|---|---|
| Fidelity | 0.908 | 0.964 | 0.965 | +0.057 (+6.3%) | 0.0015 |
| Evidence support | 0.908 | 0.964 | 0.965 | +0.057 (+6.3%) | 0.0015 |
| Manipulation score | 0.070 | 0.035 | 0.034 | −0.036 (−51%) | 0.0015 |
| Collective accuracy | 0.745 | 0.749 | 0.752 | +0.007 | 0.041 (unadjusted, secondary) |

Pre-declared decision rule: F, E, M each "improved" → **continue = True**.

### What these results do and do not show (must accompany any use of the numbers)
1. **Fidelity and evidence support are the same number.** A truthful report scores F = 1 and
   E = 1; a falsified one scores F = 0 and E = 0; no strategy produces anything in between.
   Both metrics equal "1 − share of falsified reports". H1 and H2 are therefore **one**
   finding, not two independent ones.
2. **Honesty was already the best response in the baseline.** In the unilateral-deviation
   table, honest gives the highest mean payoff for every agent in all 10 seeds in *all three*
   systems. The decision-quality reward alone outweighs the private gain from steering the
   vote at ω = 0.5. The experiment did not put the incentive up against a manipulation that
   actually pays.
3. **The measured gain is mostly faster/cleaner learning.** With ε = 0.1 exploration, 3.3% of
   reports are manipulative by chance. Ablation/proposed sit at that floor (3.5–3.6%
   manipulative; F ≈ 0.965 is essentially the ceiling). The baseline is at 9.2% because its
   payoff gap between honest and manipulative is smaller (≈ 0.09 vs ≈ 0.24), so the bandits
   separate the strategies less reliably. The effect is real under the protocol but small in
   absolute terms and bounded by the behavioural model.
4. **Reputation adds nothing measurable in the main experiment:** proposed ≈ ablation on
   every metric. The improvement comes from the explanation-aware utility.
5. Collective accuracy and collective utility are essentially unchanged.

### Robustness (Phase 7 on energy; ran in the same batch)
- Malicious share: collective accuracy at 40% is 0.729 (proposed) vs 0.675 (baseline);
  fidelity of non-malicious agents stays 0.965 vs 0.87–0.90.
- **H4 primary test is not significant:** mean accuracy degradation over 10–40%, proposed −
  baseline = −0.017, 95% CI [−0.037, +0.002], paired t, p = 0.070. No per-share comparison
  survives Holm correction. **H4 is not supported at α = 0.05** (direction as hypothesised).
- Collusion (2 colluders + 3 honest): in the baseline, colluders raise their private utility
  (+0.092) and cut collective accuracy by 3.0 points; in the proposed system their
  reputation falls to 0.012, their private gain disappears (−0.007) and accuracy is
  unchanged (−0.7 points, p = 0.47). This is the one place reputation shows an effect. It
  was compared against the baseline only, not against the ablation.

### Hypothesis status (energy only)
- H1/H2: supported by the pre-declared test, as a single finding, with caveats 1–3.
- H3: supported by the pre-declared test (manipulation score −51%), same caveats.
- H4: **not supported** (p = 0.070).
- H5: not yet tested (blockchain not built). H6: untestable (no pharma study).

### Checkpoint decision
By the pre-declared rule the mechanism passes. Reported to the user with caveats 1–4 before
any blockchain work, as CLAUDE.md requires. Open questions for the user are in the
session report. No weights were re-tuned.

Tests: `pytest -q` (see commit).

## 2026-10-05 — User decisions after the checkpoint; protocol amendment 1; new pharma file

User decisions (verbatim: "recommend strengthening first", "fidelity and evidence support be
made separable"):
1. Strengthen the test before any blockchain work → ω sensitivity brought forward.
2. Make F and E separable → **protocol amendment 1 (v1.1)**: strategies *misattributing*
   (lowers F only) and *overclaiming* (lowers E only) added. Committed before any v1.1 run.
   v1.0 summaries/tables archived in `results/summaries/v1.0/`, `tables/v1.0/`.
   v1.1 results are post hoc relative to v1.0 and must be presented as such.
3. A new pharma file, `pharma-data.csv`, was supplied together with a pasted assessment
   recommending it and a five-agent design (Demand, Pricing, Distribution, Market, Product).

### Audit of `pharma-data.csv` (details: `docs/dataset_audit.md` §4)
- 254,082 monthly sales lines, 18 columns, no missing values; copied read-only to
  `data/raw/pharma_sales/` (hash recorded; not in git).
- **Source, licence and citation unknown** (one web search found nothing).
- **Strong signs of synthetic or masked data:** Faker-style company names, invented product
  names, one constant price per product across four years, sales reps assigned uniformly at
  random, and near-zero association between product class, channel, distributor, country and
  sales rep (Cramér's V ≤ 0.011). Channel, sub-channel, product class and sales rep explain
  ≈ 0% of quantity; distributor explains 12%.
- Consequence: the pasted five-agent design is not supported (Pricing has a constant; Market
  and Product agents would have no signal; there is no outcome from which to judge a
  distributor). The file does not satisfy Golden Rule 1 as it stands.
- **Nothing was built on it. Waiting for the user** (CLAUDE.md §10: variable absent /
  ambiguity): source URL and licence; and whether to (a) use it explicitly labelled as a
  synthetic benchmark with a constructed demand-allocation reference, (b) use the source
  study's real but tiny Tables 2–11, or (c) find another real dataset.

## 2026-10-06 — Disk incident; v1.1 reruns; new pharma candidate (SCMS delivery history)

- Drive C: filled during the v1.1 runs; the ω sensitivity run failed while writing. Freed
  space by deleting the project's duplicate of `pharma-data.csv` (original intact, same
  SHA-256; audit and metadata updated). The rerun was then cut off when the session ended
  (5 of 10 seeds) and was restarted from scratch on 2026-10-06.
- v1.1 baseline, proposed, ablation and adversarial runs completed (10 seeds each).
  Robustness, v1.1, post hoc relative to v1.0: H4 primary test Δ degradation = −0.020
  (95% CI [−0.043, +0.002]), p = 0.068 → **H4 still not supported**. Details:
  `tables/energy_adversarial.md`.
- User proposed https://www.kaggle.com/datasets/apoorvwatsky/supply-chain-shipment-pricing-data
  and supplied the Kaggle archive. Copied unchanged to `data/raw/pharma_scms/` (read-only),
  hash and provenance in `data/metadata/datasets.json`, full audit in
  `docs/dataset_audit.md` §5, loader + 4 schema tests added.
  - Real USAID/PEPFAR SCMS shipment lines: 10,324 × 33, deliveries 2006–2015, 88
    manufacturing sites, 11.5% of lines late.
  - Not verified: identity with the publisher's copy (data.usaid.gov unreachable); the
    licence text on the Kaggle page (login). Licence taken from a catalogue mirror: CC BY-ND.
  - Gaps S-1…S-9 (audit §5.5). The two that force a design change: **no quality or
    compliance variable**, and **no competing offers** (reference decision must be
    constructed).
- **Open, waiting for the user** (CLAUDE.md §10: needed variables absent): approve replacing
  the figshare criteria list as primary pharma dataset (protocol amendment 2), the five-agent
  mapping, and the handling of S-2 and S-4. No preprocessing, agents or scenarios built yet.

## 2026-10-06 (later) — Energy v1.1 verdicts and ω sensitivity; pharma amendment 2 and pipeline

### Energy v1.1 (post hoc relative to v1.0) — verdicts by the pre-declared rule
From `tables/energy_main.md`, proposed vs baseline, n = 10:
- Fidelity +0.034 (+3.6%), Holm p = 0.004 → **negligible** (significant, but below the 5%
  relative-improvement threshold). Evidence support +0.040 (+4.3%), Holm p = 0.004 →
  **negligible**. Manipulation −0.029 (−44.4%), Holm p = 0.003 → **improved**.
- So under v1.1 **H1 and H2 do not meet the pre-declared rule; H3 does.** Under v1.0 the
  rule had been met for all three. Cause visible in the table: the baseline is already 78%
  honest at ω = 0.5, leaving F and E little room. Not re-tuned.
- Ablation ≈ proposed on F, E, M: the effect comes from the incentive, not from reputation.
- H4 unchanged: not supported (p = 0.068).

### ω sensitivity (energy, v1.1; `tables/energy_sensitivity_omega.md`)
Rerun completed (10 seeds). Proposed − baseline: ω = 0.25: F +3.3%, E +3.7%, M −41%;
ω = 0.5: as above; ω = 0.75: F +27.8%, E +28.6%, M −71% (all Holm p ≤ 0.002);
ω = 0.9 (exploratory, not pre-declared): F +50%, E +57%, M −45%. The incentive matters more
the more an agent weighs its private gain; at the pre-declared ω = 0.5 the F and E effects
are below the 5% threshold. At ω = 0.9 honesty collapses in every system (honest share
0.16–0.34).

### Pharma: user decisions (2026-10-06, verbatim: "ok go a head with your recommendation")
Approved: (1) SCMS delivery history replaces the figshare criteria list as primary pharma
dataset; (2) agents Cost, Delivery reliability, Lead time, Logistics, Supply continuity
(no Quality/Compliance — no variable); (3) direct-from-supplier lines only; (4) a
constructed reference decision with sensitivity analysis.

### Protocol amendment 2 (v1.2) — committed before any pharma model was trained
`docs/research_protocol.md` §11 and §12. Design choices made by me within the approved
recommendations (flagged for the user):
- Scenario = purchase order × product; three candidates = sites that most recently delivered
  the product before the order date; slot order hashed.
- Reference = equal-weight sum of five min–max-normalised criteria.
- Time-ordered split 50/10/40; 600 rounds, evaluation on the last 300.
- Mechanism parameters identical to energy v1.1.

Feasibility figures seen before freezing: 1,648 scenarios (824/165/659), 31 products, 49
sites; reference = site actually used in 35% of scenarios where it is a candidate (chance
33%); reference unchanged in 68–82% of scenarios under weight changes; criterion-preferred
candidate = reference in 46–52%.

### Steps 06–16 for pharma
- `environments/pharma/preprocess.py`, `agents/pharma_agents.py`, `experiments/pharma.py`,
  seven `configs/pharma_*.yaml` (derived from the energy configs; only data-dependent keys
  differ).
- The game, metric aggregation and runners moved unchanged from `experiments/energy.py` to
  `experiments/core.py` so both domains share them. Checked: energy_proposed seed 0
  reproduces the stored result byte for byte.
- `data/processed/pharma/scenarios.csv` is git-ignored (CC BY-ND: no redistribution of
  processed data); `scenarios_meta.json` is committed.
- Tests: 21 new pharma tests, including a rebuild-from-past-lines test that shows no future
  information enters a scenario. Full suite passes.
