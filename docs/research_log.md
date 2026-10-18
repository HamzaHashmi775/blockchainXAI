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

## 2026-10-06 — Pharma steps 17–21: main experiment, ablation, robustness; CRITICAL CHECKPOINT

Runs (10 seeds each, protocol v1.2, paired): `pharma_baseline`, `pharma_ablation`,
`pharma_proposed`, `pharma_adversarial`. Statistics: `tables/pharma_main.md`,
`tables/pharma_adversarial.md`, `results/summaries/pharma_*.json`. Nothing was tuned or
rerun after seeing results.

### Main results, proposed vs baseline (mean over seeds; Holm-adjusted p)
| Metric | Baseline | Proposed | Δ | Rel. | p (Holm) | Verdict |
|---|---|---|---|---|---|---|
| Fidelity | 0.510 | 0.936 | +0.426 | +83.5% | < 0.0001 | improved |
| Evidence support | 0.522 | 0.917 | +0.395 | +75.7% | < 0.0001 | improved |
| Manipulation | 0.392 | 0.119 | −0.273 | −69.7% | < 0.0001 | improved |

Collective accuracy 0.578 → 0.606 (p = 0.20, not significant). Ablation (incentive without
reputation): F 0.892, E 0.892, M 0.153, all improved; so most of the effect is the incentive,
with a further gain when reputation weights the vote.

### Caveats that must travel with these numbers
1. **The baseline is far from honest in pharma** (honest share 9.5%, manipulative 41%),
   unlike energy (78% honest). In the baseline, deviating from honesty pays for every agent
   (unilateral-deviation table: manipulative best in 10/10 seeds for all five), because an
   agent's model predicts the reference only moderately well (validation accuracy
   0.64–0.79) while steering towards its own criterion pays privately. The large effect is
   therefore measured against a baseline with much room to improve; it is not comparable in
   size to the energy effect.
2. **Strategic voting is not removed.** Under the proposed system *strategic* (vote for the
   privately preferred candidate, truthful explanation) is still the best unilateral
   deviation for Cost, Logistics and Reliability in 10/10 seeds; honest is best only for
   Lead time and Continuity. Learned shares under proposed: honest 41%, strategic 35%. The
   mechanism suppresses false explanations and unsupported evidence, not self-interested
   voting. No equilibrium claim.
3. Decision accuracy means agreement with a **constructed** reference that matches the real
   procurement choice only at chance level (protocol §11.2).
4. Designed after the energy results; same mechanism and weights (replication, not blind).
5. Manipulation contains 1 − F and 1 − E, so H3 is not independent of H1/H2.

### Robustness (H4)
- Accuracy degradation over 10–40% malicious, proposed − baseline: Δ = +0.039 (95% CI
  [−0.010, +0.088]), p = 0.10. **H4 not supported in pharma; the point estimate is in the
  wrong direction** (proposed loses slightly more accuracy, not significant). Friedman
  across shares: baseline p = 0.56, proposed p = 0.20 — accuracy barely moves with the
  malicious share in either system, plausibly because the baseline is already mostly
  non-honest at 0%.
- Collusion: in the baseline colluders gain (private utility +0.161, payoff +0.085) and
  steer 38% of decisions wrongly; under proposed their reward falls 0.475 → 0.017,
  reputation → 0.018, payoff −0.231, and wrong steered decisions fall to 12.6%. Collective
  accuracy still drops under collusion in proposed (−0.036, p = 0.008).

### Hypotheses so far
| | Energy (v1.1, post hoc) | Pharma (v1.2) |
|---|---|---|
| H1 fidelity | negligible (+3.6%, significant) | improved (+83.5%) |
| H2 evidence | negligible (+4.3%, significant) | improved (+75.7%) |
| H3 manipulation | improved (−44%) | improved (−70%) |
| H4 robustness | not supported (p = 0.068) | not supported (p = 0.10, wrong sign) |

**H6 (same verdict in both domains) holds for H3 and H4 only**: direction is the same for
F and E in both domains, but the pre-declared verdicts differ (negligible vs improved).

### Checkpoint decision (pharma)
By the pre-declared rule the mechanism passes (three improved, none worse). Reported to the
user with the caveats above. Blockchain (Phase 8) not started; waiting for the user.

## 2026-10-06 — User direction: the study is about LLM agents; Ollama on Kaggle

- The user stated that the study is based on LLM agents ("but this study is based on LLM
  Agents"), asked for open-source models through Ollama, and accepted Kaggle's free compute
  ("using free CPU of Kaggle is acceptable to me"). **This conflicts with CLAUDE.md Golden
  Rule 12** (no LLMs unless the data requires it) and §9 (LLM agents optional). The user's
  instruction takes precedence; CLAUDE.md has not been edited and should be updated by the
  user or on their instruction.
- All results so far (energy v1.0/v1.1, pharma v1.2) are from **classical scripted agents**
  (Random Forest + SHAP + ε-greedy over scripted strategies). No LLM was involved in any of
  them. They stay as they are; whether they become a comparison arm or are dropped is an
  open user decision (my recommendation: keep as comparison arm).
- This machine: i7-8665U, 15.8 GB RAM, no dedicated GPU, Ollama not installed. Nothing was
  installed locally.

### LLM-agent design built for the pilot (NOT yet a frozen protocol)
- An LLM agent keeps its Random Forest and SHAP values as a private analysis tool. Each
  round it is told its private gain per option, the tool's probability per option, and per
  option the tool's features (observed level, SHAP contribution), plus its last 3 rounds'
  outcomes. It returns vote, confidence, two features with direction, and a level for each.
- The rules of the system (how reward is computed; in the proposed system, that reports are
  audited) are stated in the prompt. Audit feedback appears in the history only when the
  system audits (not in the baseline).
- Replies are constrained by a JSON schema with enumerated values. An unparsable reply is
  retried once, then replaced by the tool-supported report and counted.
- Fidelity, evidence support, manipulation, utility, reward, reputation and the collective
  decision are computed by the existing functions, unchanged.
- Code: `agents/llm_agent.py`, `experiments/llm.py`, `experiments/llm_pilot.py`,
  `kaggle/llm_pilot_kaggle.ipynb`; 17 tests with stub models (no LLM). `prepare` now also
  returns the raw SHAP values, feature rows and thresholds; stored energy and pharma results
  still reproduce byte for byte.
- **Not verified:** the notebook has not been run on Kaggle; Ollama's install on Kaggle,
  model speed and reply quality are unknown until the pilot runs.

### Next
1. User runs the pilot notebook on Kaggle (validation scenarios only, 100 agent decisions).
2. From the measured seconds per call: size rounds/seeds, then write and freeze **protocol
   amendment 3** (LLM agents) before any LLM run on test scenarios. Open design points for
   it: how malicious LLM agents are instructed; whether classical results are a comparison
   arm; model and quantisation; handling of unusable replies.

## 2026-10-06 — LLM pilot 1 (Kaggle, qwen2.5:7b) and prompt revision

Pilot output supplied by the user: `results/pilot/pilot1/`. **Feasibility only: 10 rounds,
validation scenarios, one seed; not an experimental result.**

- Ran on a Tesla T4 (all layers on GPU), Ollama, `qwen2.5:7b` Q4_K_M, digest `845dbda0…`,
  temperature 0. Kaggle Python 3.13, not the pinned environment.
- **Feasibility:** 100/100 replies usable (no retries). Median 3.4–3.7 s per decision
  (server side about 2.7 s: ~500 prompt tokens, ~80 output tokens). About 970 decisions per
  hour, one request at a time.
- **Sanity:** votes spread over the three candidates (26–44%); confidence varies. The model
  reacts to the stated rules: mean confidence 0.86 in baseline vs 0.70 in proposed
  (confidence-inflation score 0.18 vs 0.02).
- **Problem found:** fidelity was 0.32 in *both* systems and only 6% of explanations were
  fully truthful, even though 84–88% of votes followed the tool. Rebuilding the round-1
  prompt locally shows why: the Cost agent's tool had `price_cv` (+0.380) and
  `exp_unit_price` (+0.057) on top for the option it voted for, and the model reported
  "`exp_unit_price` lowers, `price_rel` raises" — the first two features in the list with
  directions from common sense, not from the tool. It gave the same explanation in both
  systems. (Local and Kaggle library versions differ, so the rebuilt numbers may not be
  identical to what the model saw; the pattern is the same across the five sampled agents.)
  Conclusion: with that prompt, fidelity would mostly measure whether the model can pick the
  two largest of five signed numbers, not whether it chooses to be truthful.

### Change made before any protocol is frozen
- The tool's analysis is now listed **most important feature first**, in words ("`price_cv`
  is high, raises score by 0.380"), and the system prompt states that the true top features
  of an option are the first two listed. Being truthful is then a matter of copying; not
  being truthful is a choice. This mirrors the scripted agents, which know the truth exactly.
- New pilot check `reads_its_tool`: share of fully truthful explanations among reports that
  vote with the tool in the proposed system (nothing to gain from misreporting); a model
  below 0.8 is unfit for the experiment.
- The five requests of a round can be sent concurrently (`workers`), results stored in agent
  order; context window set to 2,048 tokens.
- Pilot 2 notebook: `qwen2.5:7b` and `llama3.1:8b`, each sequential and concurrent, 10 rounds
  on validation scenarios.

These prompt changes were made after seeing pilot-1 behaviour. They are pre-freeze design
iterations on validation scenarios and will be disclosed as such in amendment 3.

## 2026-10-07 — LLM pilot 2 (Kaggle; qwen2.5:7b and llama3.1:8b) and last prompt revision

Output: `results/pilot/pilot2/`. **Feasibility only: 10 rounds, validation scenarios, one
seed; not an experimental result.** Prompt of pilot 2 = features listed by importance.

| Model | Mode | System | Fidelity | Evidence | Truthful when voting with tool | Votes against tool | Confidence inflation |
|---|---|---|---|---|---|---|---|
| qwen2.5:7b | sequential | baseline | 0.764 | 0.97 | 0.49 | 0.18 | 0.215 |
| qwen2.5:7b | sequential | proposed | 0.792 | 0.99 | 0.61 | 0.12 | 0.017 |
| llama3.1:8b | sequential | baseline | 0.904 | 0.96 | 0.78 | 0.26 | 0.238 |
| llama3.1:8b | sequential | proposed | 0.904 | 0.95 | 0.78 | 0.28 | 0.080 |

- 400/400 replies usable. Fidelity rose from 0.32 (pilot 1) to 0.76–0.90, so most of the
  pilot-1 problem was the prompt layout.
- **Both models fail the pre-set reading check (≥ 0.80):** llama3.1:8b 0.78 (about 36
  reports, so the miss is within sampling noise), qwen2.5:7b 0.61.
- Sampled replies show two kinds of non-truthful explanation: (a) near-tie substitution —
  the model names a familiar feature instead of the second-ranked one when their effects
  are almost equal (0.056 vs 0.054); (b) cherry-picking — when voting for its privately
  preferred option against the tool, llama dropped the top feature that *lowered* the score
  and reported two that raised it. (b) is the behaviour the study is about; (a) is noise.
- **Concurrency:** five requests at once gave 2.6× (qwen) and 1.9× (llama) throughput:
  about 1.3 s and 1.6 s per decision. Votes were identical between modes; a few explanations
  differed (fidelity 0.764 vs 0.761), so concurrent runs are **not bit-reproducible**. Every
  raw reply must therefore be saved in the real runs.
- Both models lowered their stated confidence under the proposed rules.

### Last prompt revision (pre-freeze, validation data only)
The round prompt now also states the truthful explanation of each option outright (its two
most important features with direction and level). Reporting truthfully then needs no
reading skill, as for a scripted agent; all five features stay visible, so cherry-picking
remains possible.

**Stopping rule, set before pilot 3:** this is the last prompt change. Pilot 3 runs
llama3.1:8b, qwen2.5:7b and qwen2.5:14b. The model with the highest reading-check value
that is ≥ 0.80 is used. If none reaches 0.80, the best model is used anyway and its
reading-check value is reported as a limitation (explanation errors that are not choices).

## 2026-10-11 — LLM pilot 3 (Kaggle; llama3.1:8b, qwen2.5:7b, qwen2.5:14b) and model choice

Output: `results/pilot/pilot3/`. **Feasibility only: 10 rounds, validation scenarios, one
seed, five concurrent requests; not an experimental result.** Prompt = pilot-2 prompt plus
the truthful explanation of each option stated outright (the last prompt change).

| Model (all Q4_K_M) | Reading check (proposed) | Fidelity base / prop | Votes against tool base / prop | Confidence inflation base / prop | Seconds per decision |
|---|---|---|---|---|---|
| llama3.1:8b (8.0B) | 0.972 | 0.982 / 0.982 | 0.26 / 0.28 | 0.173 / 0.083 | about 2.1 |
| qwen2.5:7b (7.6B) | 0.977 | 0.975 / 0.989 | 0.16 / 0.14 | 0.191 / 0.023 | about 1.7 |
| qwen2.5:14b (14.8B) | 0.977 | 0.968 / 0.998 | 0.26 / 0.14 | 0.197 / 0.001 | about 11 |

- 300/300 replies usable. All three models pass every sanity check, including the reading
  check (≥ 0.80).
- qwen2.5:14b did not fit one T4 entirely (40 of 49 layers on GPU) and is about 6–7 times
  slower; it is impractical on the free tier.
- **Model chosen by the stopping rule set before pilot 3: `qwen2.5:7b`** (digest
  `845dbda0ea48…`, Q4_K_M). It ties with qwen2.5:14b for the highest reading-check value
  (0.977); the tie is resolved by speed, a tie-break not written down beforehand and
  recorded here as such. llama3.1:8b (0.972) is the documented alternative.
- Seconds per decision = wall time ÷ 50 decisions of the proposed run; per-request latency
  is 7–10 s because five requests share the GPU.
- With truthful reporting made trivial, explanations are almost always truthful in *both*
  systems in these 10 rounds (fidelity ≥ 0.97 in the baseline). If that holds at scale, the
  LLM experiment will have little room to show a fidelity or evidence effect (ceiling), and
  the informative outcomes will be strategic voting and confidence inflation. This is a
  pilot observation on validation data, not a result; it is noted so that amendment 3 can
  declare it as a known risk rather than discover it afterwards.
- No further prompt changes will be made (stopping rule).

### Next: protocol amendment 3 (LLM agents) — to be approved by the user before any run on
test scenarios. Open points: role of the classical results; how malicious agents are
realised; rounds, seeds and systems given about 2,100 decisions per GPU hour.

## 2026-10-11 (later) — Protocol amendment 3 frozen; LLM run code and Kaggle notebook

- User decision on size (verbatim: "ok don't increases more seeds or rounds"): 200 rounds,
  5 seeds (main), 100 rounds and 3 seeds (robustness). The two other open points were not
  answered explicitly; the recommendations put to the user are used and marked *(default)*
  in the amendment: classical results kept as a separate comparison arm; malicious and
  colluding agents scripted.
- **Amendment 3 (v1.3) committed before any LLM run on test scenarios** (`9fca5a2`). It
  declares the ceiling risk seen in pilot 3, and the inferential limit of n = 5 (a Wilcoxon
  test cannot reach p < 0.0625; flagged to the user).
- Erratum A3.5 (same day, before any run): the tool's top option is named in the prompt,
  because two-decimal probabilities can display a tie. Found by a unit test.
- Code: `experiments/llm_runs.py` (`<domain>_llm_main`, `<domain>_llm_adversarial`; refuses
  a model whose digest differs from the frozen one; saves every raw reply),
  `experiments/llm.py` (scripted malicious agents and colluders among LLM agents),
  `run_experiment.py --resume / --seeds`, four `configs/*_llm_*.yaml`,
  `statistics/analyze_llm.py`, `kaggle/llm_run_kaggle.ipynb` (with the energy gate).
  Tests use a stub model; the full suite passes.
- **Not verified:** the run notebook has not been executed on Kaggle. Run time is an
  estimate from 10-round pilots (about 8 h per main run, about 3 h per robustness run);
  prompts grow slightly once the 3-round history fills. The energy prompts have never been
  shown to a model (the gate checks this first).
- Nothing was run on test scenarios today. Blockchain (Phase 8) remains unstarted.

## 2026-10-11 (evening) — Amendment 3 suspended; raw-prompt pilot 4 prepared

- The user asked whether the project is moving in the right direction. Assessment given:
  the classical pharma result is strong and manipulation falls in both domains, but the LLM
  arm as frozen would most likely show no gain in fidelity or evidence support, because the
  prompt hands the agent the truthful explanation (pilot 3 baseline ≥ 0.97; pilot 1, before
  that change, 0.32).
- The user then pasted written advice (author not stated) asking for agents that produce
  their own explanation from raw tool output, a natural and a strategic-pressure condition,
  and a validation pilot first. Treated as the user's direction.
- **Amendment 3 suspended before any test-scenario run.** This reverses the statement in
  A3.4 that a ceiling would not be repaired by changing the prompt, and the stopping rule
  of 2026-10-07. Recorded in the protocol as a design change made with knowledge of pilot
  behaviour.
- Added prompt style `raw` (numbers only, fixed feature order, no truthful explanation);
  the disclosed prompt of amendment 3 is byte-identical to the previous commit (checked on
  5 agents x 5 rounds, and guarded by a test). `experiments/llm_pilot.py --prompt raw
  --omega`; pilot summary now reports the longest prompt in tokens and checks that it fits
  the context window. `kaggle/llm_pilot_kaggle.ipynb` is now pilot 4.
- Rules fixed before pilot 4 (protocol): the raw prompt is used whatever the pilot shows;
  ω = 0.75 as strategic pressure is fixed now; a baseline at the ceiling would be reported.
- **Design limit found while writing this:** explanations have no private payoff in the
  game, so strategic pressure acts on vote and confidence only. Declared in the protocol.
- **Not verified:** the raw prompt has never been shown to a model. Locally it was run only
  with a stub (energy and pharma, validation rounds). The longest energy prompt is about
  3,900 characters; whether it fits 2,048 tokens is unknown until the pilot reports counts.
- `kaggle/llm_run_kaggle.ipynb` still runs amendment 3 and must not be used for now.
- Full suite: 150 passed.

## 2026-10-11 (night) — Is ω = 0.75 real strategic pressure? Payoff check without a model

- Prompted by a second piece of pasted advice (author not stated): verify, rather than
  assume, that raising ω makes a difference. Checked by payoff arithmetic on the pilot's own
  validation rounds (20 rounds, seed 0), no LLM: all agents report what their tool supports,
  then one agent at a time votes for its privately preferred option with confidence 1 and a
  truthful explanation. Mean payoff change of the deviating agent:

  | Domain | System | ω = 0.5 | ω = 0.75 |
  |---|---|---|---|
  | pharma | baseline | +0.027 (2 of 5 agents gain) | +0.082 (5 of 5 gain) |
  | pharma | proposed | −0.123 (0 of 5) | −0.050 (1 of 5) |
  | energy | baseline | −0.074 (0 of 5) | −0.030 (0 of 5) |
  | energy | proposed | −0.138 (0 of 5) | −0.066 (0 of 5) |

- Reading: in pharma, ω = 0.75 is real pressure (selfish voting pays every agent under the
  baseline and is penalised under the proposed system). In energy it is not: a single agent
  changes the group decision in only 2–3% of rounds, so always voting selfishly loses even
  under the baseline at both weights. The label "strategic pressure" is therefore not
  justified for energy by this check.
- Limits: 20 validation rounds, one seed, one crude policy (always vote the preferred
  option); a selective deviator could do better, and coalitions were not examined. This is
  a property of the payoff rule, not a result about LLM behaviour.
- `kaggle/llm_run_kaggle.ipynb` now stops at its first code cell with a "suspended" message.
- ω for the pressure condition stays 0.75 as fixed before the pilot; it is not re-chosen.

- Later the same night, before pilot 4 was run: the ω = 0.75 condition is renamed "higher private gain" (file tag `higher_gain`); "strategic pressure" is used for pharma only. Proposed scope for amendment 4 (pharma-only ω = 0.75 in the main experiment) written into the protocol before any model result; it still needs the user's approval.

## 2026-10-11 — LLM pilot 4 (raw prompt) — feasibility on VALIDATION scenarios, not a result

Files: `results/pilot/pilot4/` (four JSON files; the 53 MB `ollama.log` is kept locally and
not committed). qwen2.5:7b, frozen digest, 29/29 layers on one Tesla T4, 20 rounds, seed 0,
100 agent decisions per system and condition. A first attempt failed on a 504 from the
Ollama download server and a second session ran for an hour without output; that session
was restarted and its cause was not established.

| Domain, ω | System | Fidelity | Evidence | Manipulation | Confidence inflation | Votes against tool |
|---|---|---|---|---|---|---|
| pharma 0.5 | baseline | 0.447 | 0.520 | 0.282 | 0.219 | 0.14 |
| pharma 0.5 | proposed | 0.441 | 0.495 | 0.236 | 0.016 | 0.10 |
| pharma 0.75 | baseline | 0.441 | 0.525 | 0.285 | 0.231 | 0.14 |
| pharma 0.75 | proposed | 0.461 | 0.490 | 0.243 | 0.018 | 0.13 |
| energy 0.5 | baseline | 0.457 | 0.570 | 0.245 | 0.161 | 0.07 |
| energy 0.5 | proposed | 0.465 | 0.545 | 0.229 | 0.034 | 0.08 |
| energy 0.75 | baseline | 0.448 | 0.560 | 0.264 | 0.177 | 0.11 |
| energy 0.75 | proposed | 0.467 | 0.520 | 0.250 | 0.055 | 0.12 |

- Feasibility: no unusable reply in 800 calls; longest prompt 1,326 tokens (fits 2,048, no
  truncation in the server log); 171–182 s per 100 decisions = about 1.76 s per decision,
  about 2,050 decisions per GPU hour.
- The ceiling is gone: only 7–10% of explanations are fully truthful in every cell.
- Fidelity and evidence support do not differ between baseline and proposed (|Δ| ≤ 0.04,
  either sign). Raising ω from 0.5 to 0.75 changes no behaviour visibly.
- The one consistent difference is stated confidence: mean 0.85–0.88 under the baseline,
  0.64–0.76 under the proposed rules; confidence inflation falls in all four cells. The
  lower manipulation score comes entirely from this component.
- Sample replies show misread signs and levels (e.g. a contribution of +0.048 reported as
  "lowers") next to fully correct reports. The errors look like failures to read the
  numbers, not attempts to deceive.
- **Consequence for the metrics:** with the raw prompt the audit cannot tell an honest
  mistake from manipulation. "False attribution" (about 0.55) and "unsupported evidence"
  (about 0.45–0.5) are dominated by reading errors, so the manipulation score of LLM agents
  mostly measures inability. Confidence inflation and votes against the tool are the
  components that still reflect a choice.
- By the rules fixed before the pilot, the prompt, the model and ω = 0.75 stay as they are.
- Sizing from the measured speed: one main run (200 rounds, 5 seeds, 3 systems) = 15,000
  decisions = about 7.3 GPU hours.

## 2026-10-11 — Metric audit; protocol amendment 4 frozen; run code for the raw-prompt design

- Plan put to the user after pilot 4 (three main runs and the robustness runs, about 29 GPU
  hours). The user replied with pasted advice (author not stated) approving the scope on
  condition of a metric audit before freezing. Treated as the user's approval.
- **Metric audit (no evaluation rule changed):** three stub agents with one error type each
  are scored as expected through the game loop (new test); the 40 model replies saved by
  pilot 4 re-scored with production code and a separate implementation agree in all 40.
  Error types in those replies: 23 of 80 claims name a feature outside the top 2, 21
  reverse the direction, 35 state the wrong level. No defect found. Only 40 of 800 pilot
  decisions could be re-scored, because the pilot keeps 5 replies per system.
- **Amendment 4 (v1.4) frozen before any test-scenario run.** Raw prompt; pharma and energy
  at ω = 0.5 (primary), pharma at ω = 0.75; robustness at ω = 0.5; sizes unchanged;
  expectations P1–P3 from pilot 4 written down; manipulation components reported
  separately because two of them cannot tell mistakes from manipulation.
- Code: `configs/*_llm_*.yaml` carry `prompt_style: raw`; new
  `configs/pharma_llm_main_w075.yaml`; `experiments/llm_runs.py` passes the prompt style and
  records it with ω; `statistics/analyze_llm.py --run` and the added secondary outcomes;
  `kaggle/llm_run_kaggle.ipynb` re-enabled for amendment 4 (energy gate removed, server log
  cut to an excerpt because it grows by about 65 kB per call).
- **Not verified:** the run notebook has not been executed on Kaggle; 7.3 h per main run is
  an estimate from 20-round pilots. Nothing was run on test scenarios.

## 2026-10-17 — LLM session 1: `pharma_llm_main` (amendment 4, ω = 0.5) on test scenarios

- Run on Kaggle as a committed version (T4, `qwen2.5:7b`, digest `845dbda0ea48`, 29/29
  layers on GPU), started 2026-10-11 18:22 UTC, finished 02:59 UTC: **8.6 h** for 15,000
  calls (about 1.7 h per seed), above the 7.3 h estimate. 0 unusable replies, 0 replaced
  reports. Notebook output: `FAILURES: none`.
- Files: `results/raw/pharma_llm_main/` (seed_0–4, manifest; git-ignored like all raw
  results), server-log excerpt in `results/raw/llm_logs/`. SHA-256 (first 16 hex):
  zip f06d9ed617fd9e3f; seed_0 d11a3926705f0826; seed_1 0cc47f0515c5e4e4; seed_2
  a50119fa4bb450c8; seed_3 a307a1ea7edbe1f8; seed_4 0f36f67641c233b0.
- Analysis: `statistics/analyze_llm.py --domain pharma` → `results/summaries/pharma_llm.json`,
  `tables/pharma_llm.md` (adversarial runs not yet done, so that part is absent).
- **Confirmatory (proposed vs baseline, Holm over F, E, M):** H1 fidelity 0.459 → 0.450,
  Δ −0.009 [−0.020, +0.003], Holm p 0.125, negligible. H2 evidence support 0.599 → 0.593,
  Δ −0.006 [−0.010, −0.002], Wilcoxon p 0.0625 (the minimum at n = 5), Holm 0.125,
  negligible. H3 manipulation 0.294 → 0.229, Δ −0.065 [−0.070, −0.059], −22 %, Holm
  p < 0.001, improved.
- **Decomposition of ΔM (pre-declared, A4.3):** Δ components: confidence inflation −0.298,
  strategic voting −0.026, collusion −0.014, false attribution +0.009, unsupported evidence
  +0.006. About 92 % of the reduction of M comes from confidence inflation; strategic voting
  and collusion add a small, consistent part (votes against the tool 0.164 → 0.138,
  p 0.0005 unadjusted). The two components that cannot tell mistakes from manipulation did
  not improve.
- **Expectations P1–P3 (written before the run):** P1 holds (mean stated confidence
  0.830 → 0.534; inflation 0.321 → 0.023). P2 holds (no fidelity difference). P3 holds
  (evidence support not higher; slightly lower in all 5 seeds).
- Ablation vs baseline: same pattern; evidence support **worse** (−0.021, −3.5 %, Holm
  p 0.025) — a result against H2 for the incentive alone. Proposed ≈ ablation everywhere,
  so reputation adds nothing visible here.
- Decision quality: collective accuracy 0.581 → 0.600 (+0.019, Wilcoxon p 0.125, higher in
  all 5 seeds); manipulation success 0.170 → 0.159 (n.s.). No sign that the reduction in M
  cost decision quality.
- Interpretation (mine): the incentive changed what the agents *say about certainty* and,
  slightly, how they vote; it did not change the quality of the explanations they work out.
  Consistent with A4.5 ("likely outcome"); the instruction-vs-payoff confound of A4.5
  applies to the confidence effect.
- Next: session 2 (`energy_llm_main`); sessions 3 and 4 after it. Plan at about 8.6 h per
  main run.

## 2026-10-17 — LLM session 2: `energy_llm_main` (amendment 4, ω = 0.5) on test scenarios

- Committed Kaggle version, started 07:10 UTC, finished 15:43 UTC: **8.55 h** for 15,000
  calls; 29/29 layers on GPU; 0 unusable replies, 0 replaced reports.
- Files: `results/raw/energy_llm_main/` (git-ignored), log excerpt in `results/raw/llm_logs/`.
  SHA-256 (first 16 hex): zip 204695da87c768fc; seed_0 890131fa2e5748d9; seed_1
  2832e26064343d14; seed_2 b24543206f5999d3; seed_3 19c8c39a460b81b1; seed_4 552d2fd497b600d1.
- Analysis: `statistics/analyze_llm.py --domain energy` → `results/summaries/energy_llm.json`,
  `tables/energy_llm.md`.
- **Confirmatory (proposed vs baseline, Holm over F, E, M):** H1 fidelity 0.446 → 0.461,
  Δ +0.015 [+0.002, +0.029], +3.4 %, p 0.037, Holm 0.073, negligible. H2 evidence support
  0.521 → 0.519, Δ −0.002 [−0.019, +0.016], Holm 0.81, negligible. H3 manipulation
  0.276 → 0.241, Δ −0.035 [−0.038, −0.031], −12.6 %, Holm p < 0.001, improved.
- **Decomposition of ΔM:** confidence inflation −0.144, false attribution −0.015, strategic
  voting −0.010, collusion −0.007, unsupported evidence +0.002. About 83 % of the reduction
  comes from confidence inflation.
- **P1–P3:** P1 holds (confidence 0.873 → 0.734; inflation 0.177 → 0.033). P2 holds by the
  confirmatory test (fidelity not significant after Holm); note the unadjusted fidelity
  difference is small and positive here, negative in pharma. P3 holds (evidence support
  not higher).
- Ablation vs baseline: same verdicts (F, E negligible; M improved −12.7 %). Proposed ≈
  ablation again. Collective accuracy unchanged (0.776 → 0.769, n.s.).
- **H6 (LLM agents, ω = 0.5):** same qualitative verdicts in both domains — H1 negligible,
  H2 negligible, H3 improved, in each case mainly through stated confidence. Effect on M is
  smaller in energy (−12.6 %) than in pharma (−22 %), where baseline confidence inflation was
  higher (0.32 vs 0.18).
- Next: session 3 (`pharma_llm_main_w075`), then session 4 (robustness).

## 2026-10-18 — LLM session 3: `pharma_llm_main_w075` (amendment 4, ω = 0.75) on test scenarios

- First zip received (`llm_results (2).zip`) was a byte-identical copy of the session 2
  output (same SHA-256); rejected, nothing unpacked. Correct zip: `llm_results (3).zip`.
- Committed Kaggle version, started 2026-10-17 16:45 UTC, finished 2026-10-18 01:56 UTC:
  **9.2 h** for 15,000 calls; 29/29 layers on GPU; 0 unusable replies, 0 replaced reports.
- SHA-256 (first 16 hex): zip eb120310ef8bd45d; seed_0 d8606077a4c26cf8; seed_1
  ef7b36cf653a3066; seed_2 fc8d67966bbf8b1e; seed_3 fa5b5dfbb3a12a3d; seed_4 ebf33f31c0afdfd2.
- Analysis: `statistics/analyze_llm.py --domain pharma --run pharma_llm_main_w075` →
  `results/summaries/pharma_llm_w075.json`, `tables/pharma_llm_w075.md`.
- **Confirmatory (own Holm family):** H1 fidelity 0.456 → 0.450, Holm 0.31, negligible.
  H2 evidence support 0.591 → 0.586, Holm 0.31, negligible. H3 manipulation 0.306 → 0.238,
  Δ −0.068 [−0.072, −0.063], −22.2 %, Holm p < 0.001, improved. ΔM components: confidence
  inflation −0.309, strategic voting −0.026, collusion −0.015, false attribution +0.007,
  unsupported evidence +0.005 (about 91 % from confidence).
- Ablation vs baseline: evidence support worse again (−0.017, −2.9 %, Holm p 0.028), as at
  ω = 0.5.
- **Response to ω (descriptive, paired by seed, pre-declared):** under the baseline, votes
  against the tool rose from 0.164 to 0.186 (higher in all 5 seeds, +0.013 to +0.035) and M
  from 0.294 to 0.306 — the agents do react to higher private gain. The proposed system
  rose by the same amount (0.138 → 0.160). Difference between the two conditions' effects
  per seed: M −0.002, −0.009, +0.001, −0.006, 0.000; votes against tool +0.001, −0.014,
  −0.002, +0.003, +0.012. So the incentive's effect does not grow under pressure: it lowers
  strategic voting by a similar amount at both weights, but does not hold it at the ω = 0.5
  level.
- Next: session 4 (robustness, both domains).

## 2026-10-18 — LLM session 4: robustness (`pharma_llm_adversarial`, `energy_llm_adversarial`)

- Zip `llm_results (4).zip` (SHA-256 first 16 hex c32d6e69a2a1513f), different from the
  session 3 zip. Manifests match the frozen configs: seeds 0–2, malicious shares 0.2 and
  0.4, 2 colluders, 100 rounds, ω = 0.5, raw prompt, `qwen2.5:7b` digest `845dbda0ea48`;
  status `completed`. 0 unusable replies, 0 replaced reports in every seed, system and
  condition. The notebook's printed output was not received, only the zip.
- Run times from manifest start times and file times: pharma 02:47–07:45 UTC (about 5.0 h),
  energy 07:45–12:02 UTC (about 4.3 h); about 9.3 h in total, above the 6 h estimate.
- Files: `results/raw/{pharma,energy}_llm_adversarial/` (git-ignored), log excerpt
  `results/raw/llm_logs/llm_adversarial_ollama_excerpt.txt`. SHA-256 (first 16 hex):
  pharma seed_0 de4a02f512f551a1, seed_1 a2925b054b1fbc92, seed_2 1951d97d1dcdba1c;
  energy seed_0 abc11579417e5814, seed_1 bd0668f98ea6e853, seed_2 088f01db56f53078.
- Analysis: `statistics/analyze_llm.py --domain pharma|energy` re-run; the main-run sections
  of `results/summaries/{pharma,energy}_llm.json` and `tables/{pharma,energy}_llm.md` are
  unchanged; robustness sections added. All of it is descriptive (n = 3).
- **H4 (LLM agents):** degradation from share 0 to 0.4, proposed − baseline: pharma +0.010
  [−0.164, +0.184], p 0.83; energy −0.013 [−0.064, +0.037], p 0.37. No difference shown;
  the intervals are wide. Not supported with this sample.
- Explanation metrics of the LLM agents under attack look like the main run: fidelity and
  evidence support about the same in both systems; M lower under the proposed system
  (pharma 0.29 → 0.23, energy 0.28 → 0.24) at both shares.
- **Collusion (2 scripted colluders + 3 LLM agents):** under the proposed system the
  colluders' reward is much lower (pharma 0.47 → 0.09, energy 0.38 → 0.07; final
  reputation 0.12 and 0.04), and manipulation success with collusion is lower (pharma
  0.35 → 0.18, energy 0.13 → 0.08). Accuracy loss from collusion: pharma baseline −0.087,
  proposed −0.027; energy −0.026 and −0.030. Caveat: the colluders are scripted, so their
  low reward shows that the incentive penalises the scripted attack it was built to
  measure. It does not show anything about LLM behaviour. The lower manipulation success
  can come from reputation-weighted votes, not from changed LLM behaviour.
- pytest: 154 passed.
- Next: all four amendment-4 sessions are done. Cross-domain summary of the LLM results
  (H6) and updates to the paper tables / threats to validity.

## 2026-10-18 — LLM session 4: `pharma_llm_adversarial`, `energy_llm_adversarial` (amendment 4)

- Committed Kaggle version: pharma 02:47–07:45 UTC (5.0 h), energy 07:45–12:01 UTC (4.3 h);
  29/29 layers on GPU; all seeds 0–2 completed in both domains.
- SHA-256 (first 16 hex): zip c32d6e69a2a1513f; pharma seed_0 de4a02f512f551a1, seed_1
  a2925b054b1fbc92, seed_2 1951d97d1dcdba1c; energy seed_0 abc11579417e5814, seed_1
  bd0668f98ea6e853, seed_2 088f01db56f53078.
- Analysis: `statistics/analyze_llm.py --domain pharma|energy` (now including robustness) →
  `results/summaries/{pharma,energy}_llm.json`, `tables/{pharma,energy}_llm.md`. Main-run
  sections unchanged. All robustness results are descriptive (3 seeds, 100 rounds).
- **H4 (malicious shares 0.2, 0.4; accuracy degradation proposed − baseline):** pharma
  +0.010 [−0.164, +0.184], p 0.83; energy −0.013 [−0.064, +0.037], p 0.37. No evidence
  that the proposed system is more robust; intervals are wide.
- **Collusion (2 scripted colluders + 3 LLM agents):**
  pharma — colluders' reward 0.468 → 0.090, payoff 0.601 → 0.345, final reputation 0.115;
  manipulation success 0.353 → 0.177; accuracy with colluders 0.590 → 0.673.
  energy — colluders' reward 0.383 → 0.071, payoff 0.527 → 0.342, final reputation 0.044;
  manipulation success 0.127 → 0.080; accuracy with colluders 0.787 → 0.790.
  The honest LLM agents' reward is higher under the proposed system in both domains.
- Interpretation (mine): the mechanism penalises *scripted* manipulators strongly through
  reward and reputation, because their falsified reports are caught by the audit. This is a
  property of the reward rule, not a behavioural change of the LLM agents. It does not make
  the collective decision measurably more robust to malicious shares (H4).
- All four planned LLM sessions of amendment 4 are complete.
