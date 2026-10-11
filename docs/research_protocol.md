# Research Protocol (Phase 2, Step 05)

**Status: FROZEN 2026-10-05 for the energy case study** (protocol version 1.0; amended to v1.1, see §12) **and 2026-10-06 for the pharma case study** (v1.2, §11); **LLM agents frozen 2026-10-11** (v1.3, §12 amendment 3). Any later
change is recorded in §12 as a dated amendment with its reason. The pharma case study was
deferred at GATE 1 and is specified in §11 by amendment 2.

**What was looked at before freezing** (design feasibility only): the dataset schema and
descriptive statistics (`docs/dataset_audit.md`); the class shares of the constructed
reference decision (charge 19% / idle 64% / discharge 17% under the §3 assumptions); and how
often each agent's privately preferred action coincides with the reference (26–63%). No
agent model was trained and no mechanism outcome (fidelity, evidence, manipulation, reward)
was computed before freezing.

## 1. Hypotheses

H1–H6 exactly as in CLAUDE.md §0. H1–H3 are the confirmatory family. H4 and H5 are tested
as specified in §8–9. H6 cannot be tested until the pharma case study exists.

## 2. Data, scenarios and split (energy)

- Source: `data/raw/energy/Case_Study_OptiREC.xlsx` (SHA-256 in `data/metadata/datasets.json`).
- **Scenario = one hour** of the community (8760 scenarios).
- Columns **not used**: `Beneficio`, `Costo`, `Th_Factor` (undocumented definitions),
  `PG_max_Original` (undocumented relation to `PG_max`), `Lines`, `Adj_Matrix` (no power
  flow is modelled; see §10).
- **Derived variables** (deterministic functions of real columns; always labelled derived):

| Name | Definition |
|---|---|
| `hour_of_day` | `(Hour − 1) mod 24` |
| `day` | `(Hour − 1) div 24` (0…364) |
| `load_mw` | Σ over 55 users of `PL_u × P_u(t)` |
| `pv_mw` | `PG_max(t) × Σ DG` |
| `net_demand_mw` | `load_mw − pv_mw` (negative = community surplus) |
| `thermal_total` | Σ over users of `Th_u(t)` (profile units unverified) |
| `price_rank_day` | rank of `Price` within its day, scaled to [0, 1] |
| `sell_rank_day` | rank of `Price_SG` within its day, scaled to [0, 1] |
| `spread` | `Price − Price_SG` |
| `ev_home` | `H_10` (identical for the three EVs) |

- **Split (time-series aware):** whole weeks are the blocks (`week = day div 7`). In each
  consecutive 5-week cycle, weeks 0–2 → train, week 3 → validation, week 4 → test. Every
  feature is contemporaneous or within-day, and the reference decision is computed day by
  day with a fixed start/end state, so no information crosses a week boundary.
- No missing values exist, so no imputation. No outlier is removed. Tree models need no
  feature scaling; standardisation (train-set mean/sd) is used only for the scenario
  distance in §6.

## 3. Reference decision — a *constructed reference*, not an observation

The dataset contains no observed trades or storage dispatch. The decision studied is the
community's hourly **storage action** `a ∈ {charge, idle, discharge}` for the aggregate
battery. The reference is the solution of a transparent perfect-foresight linear programme,
solved independently for each day:

minimise Σ_t [`Price_t`·import_t − `Price_SG_t`·export_t]
s.t. import_t − export_t = `net_demand_mw_t` + ch_t − dis_t; SOC_t = SOC_{t−1} + η_c·ch_t − dis_t/η_d;
0 ≤ ch_t, dis_t ≤ q; 0.1·B ≤ SOC_t ≤ 0.9·B; SOC_start = SOC_end = 0.5·B.

Label: charge if ch_t − dis_t > 0.05·q; discharge if < −0.05·q; otherwise idle.

Assumptions (none is given by the dataset; all are **simulated parameters**):

| | Assumption | Value | Sensitivity (Phase 10) |
|---|---|---|---|
| A1 | `BT` is energy capacity in MWh; B = Σ `BT` | 0.1078 | — |
| A2 | power limit q = B × C-rate | C-rate 0.5 /h | 0.25, 1.0 |
| A3 | round-trip efficiency, η_c = η_d = √0.9 | 0.9 | 0.8, 0.95 |
| A4 | SOC window (borrowed from the file's EV SOC bounds) | 10–90% | — |
| A5 | daily cycle: SOC starts and ends each day at 50% | — | — |

The paper must call this a constructed reference and must not describe decision accuracy as
agreement with observed behaviour.

## 4. Agents

Five agents. Each has (i) a **private objective** over actions, a closed-form function of
real/derived variables, and (ii) a **model** that predicts the reference decision from the
agent's own feature view.

Let s(charge)=+1, s(idle)=0, s(discharge)=−1 and x_t(a) = `net_demand_mw_t` + q·s(a)
(grid import if positive).

| Agent | Private objective u_i(a, t) | Feature view |
|---|---|---|
| Producer | −s(a)·(`Price_SG_t` − daily median `Price_SG`) | `PG_max`, `Temperature`, `hour_of_day`, `Price_SG`, `sell_rank_day` |
| Consumer | −`Price_t`·max(x_t(a), 0) | `load_mw`, `thermal_total`, `Temperature`, `TL_Flex_Availability`, `Price`, `hour_of_day` |
| Price/Market | −s(a)·(`Price_t` − daily median `Price`) | `Price`, `Price_SG`, `Gas_Price`, `price_rank_day`, `spread` |
| Grid | −\|x_t(a)\| | `net_demand_mw`, `load_mw`, `PG_max`, `hour_of_day` |
| Storage | 1 for charge when `net_demand_mw_t` < 0; 1 for idle otherwise; else 0 | `net_demand_mw`, `ev_home`, `hour_of_day`, `price_rank_day`, `PG_max` |

- ũ_i(a, t) = u_i min–max normalised over the three actions of that hour (0.5 for all
  actions if they are equal). Privately preferred action a*_i = argmax ũ_i, ties broken in
  the order idle, charge, discharge.
- **Model:** `RandomForestClassifier(n_estimators=100, max_depth=6)`, seeded per agent and
  per run seed, trained on the train split. Chosen because exact TreeSHAP supports
  multiclass random forests and attributions are additive to the predicted probability; the
  decision depends on thresholds and interactions (price rank, surplus sign) that a linear
  model would miss. Validation split is used only to report model accuracy.

## 5. Game G = (N, S, U)

- N: the five agents. S_i = {honest, strategic, manipulative}.
- A **report** = (vote, confidence, explanation, evidence). Explanation = k = 2
  (feature, sign) pairs. Evidence = one claim (feature, level) per explained feature,
  level ∈ {low, mid, high} by train-split terciles of that feature.

| Strategy | Vote | Confidence | Explanation | Evidence |
|---|---|---|---|---|
| honest | model argmax | model probability of the vote | top-k \|SHAP\| features for the voted class, true signs | true levels |
| strategic | a*_i if ũ_i(a*_i) − ũ_i(model vote) ≥ 0.25, else model argmax | when deviating: min(1, model probability of vote + 0.3) | truthful for the voted class | true levels |
| manipulative | a*_i always | 1.0 | the k features with the **smallest** \|SHAP\|, signs flipped | a false level for each (“high”, or “low” if the truth is high) |

- Attacks are applied to **reports only**; observations are never altered.
  Strategic = strategic voting + confidence inflation. Manipulative = strategic voting +
  confidence inflation + false attribution + unsupported evidence. Collusion (§8) is a
  separate controlled condition.
- **Collective decision:** score(a) = Σ_i w_i · confidence_i · 1[vote_i = a]; the action
  with the highest score wins; ties in the order idle, charge, discharge.
  w_i = 1 in BASELINE and ABLATION; w_i = Rep_i in PROPOSED.
- **Strategy choice (adaptive agents):** stateless ε-greedy bandit over S_i. Q_i(s) starts
  at 0.5; with probability ε = 0.1 a uniformly random strategy, otherwise argmax Q (ties
  broken at random); update Q_i(s) ← Q_i(s) + 0.1·(π_i − Q_i(s)).
- **Agent payoff:** π_i = ω·ũ_i(collective action) + (1 − ω)·R_i, ω = 0.5. The first term
  is what an agent gains privately by steering the decision; the second is the mechanism's
  reward.
- **No Nash-equilibrium claim** is made from the learning dynamics. As a secondary analysis,
  the unilateral-deviation table (§7) checks whether the all-honest profile is stable in the
  empirical game; it will be described as exactly that.

## 6. Metrics (per agent, per round)

- **Fidelity** F_i = Σ_{f ∈ reported, sign correct} |φ_f| / Σ_{f ∈ true top-k} |φ_f|, where φ
  is the SHAP vector of the agent's own model for the class it voted. F ∈ [0, 1]. Empty
  explanation → 0. Zero denominator → 1 if the explanation is non-empty.
- **Evidence support** E_i = supported claims / total claims; a claim is supported iff the
  observed value falls in the claimed tercile. No claims → 0.
- **Decision quality** D_i = 1[vote_i = reference].
- **Contribution** C_i ∈ {0, 0.5, 1}: recompute the collective decision without agent i;
  1 if i is pivotal for a correct decision, 0 if pivotal for an incorrect one, else 0.5.
- **Manipulation** M_i = mean of five audited components, each in [0, 1]:
  false attribution 1 − F_i; confidence inflation max(0, confidence − model probability of
  the vote); unsupported evidence 1 − E_i; strategic voting 1[vote ≠ model argmax];
  collusion 1 if i deviates from its model and another deviating agent casts the same vote.
  M is computed from reports and a white-box audit of the agent's model — never from
  knowledge of which strategy was played. (F and E therefore also enter M; this overlap is
  intended by the CLAUDE.md formula and is reported as such.)
- **Consistency** (per agent, per run): for each evaluated round, its 5 nearest evaluated
  rounds by Euclidean distance in the agent's standardised feature view are its similar
  scenarios; explanation similarity is the Jaccard index of the two sets of reported
  (feature, sign) pairs; consistency is the mean over all such pairs.
- **System level:** collective accuracy 1[collective = reference]; collective utility =
  mean_i ũ_i(collective action); manipulation success = 1[collective ≠ reference and the
  collective action equals the vote of at least one agent that deviated from its model];
  honest-strategy share.

## 7. Incentive, reward, reputation, systems

- PROPOSED / ABLATION utility: U_i = α·D + β·F + γ·E + δ·C − λ·M with
  **α = 0.30, β = 0.25, γ = 0.15, δ = 0.10, λ = 0.20**. All components lie in [0, 1].
- BASELINE utility: U_i = 0.75·D + 0.25·C (same α:δ ratio; β = γ = λ = 0).
- Reward R_i = (U_i − U_min)/(U_max − U_min) across the five agents of the round;
  **0.5 if U_max = U_min**.
- Reputation Rep⁰ = 0.5; Rep ← ρ·Rep + (1 − ρ)·R with **ρ = 0.8**.

| System | Utility | Vote weights | Reputation | Provenance log |
|---|---|---|---|---|
| BASELINE | decision-only | 1 | off | off |
| ABLATION | explanation-aware | 1 | off | off |
| PROPOSED | explanation-aware | Rep_i | on | on (after Phase 8) |

These weights were set a priori and are **not** tuned on results. Sensitivity (Phase 10):
β ∈ {0, 0.10, 0.25, 0.40} with the other weights rescaled proportionally;
ρ ∈ {0.5, 0.8, 0.95}; ω ∈ {0.25, 0.5, 0.75}; reference assumptions A2–A3.

- **Runs:** seeds 0–9. A seed fixes the five forests, the 1000 test hours drawn without
  replacement and replayed in chronological order, the ε-greedy stream and the malicious
  ordering. The three systems share scenarios and seeds (paired design).
- **Main experiment:** all five agents adaptive, 1000 rounds; metrics are averaged over
  agents and over the **last 500 rounds** (the first 500 are learning burn-in).
- **Unilateral-deviation table (secondary):** with the other four agents fixed to honest,
  each agent's mean payoff π under each of its three strategies, per system, on the same
  rounds.

## 8. Robustness experiments

- **Malicious share p ∈ {0, 0.1, 0.2, 0.3, 0.4}.** Five agents cannot realise 10% or 30%
  exactly. A seeded agent order is drawn per run; in each round the number of malicious
  agents is ⌊5p⌋ or ⌈5p⌉, randomised so its expectation is 5p (p = 0.1: the first agent is
  malicious in half the rounds). Malicious agents play *manipulative*; the rest are adaptive.
  Observations are identical across p.
- **Collusion:** two agents (seeded choice) vote argmax of ũ_i + ũ_j with confidence 1.0 and
  manipulative explanation/evidence; the other three are honest. Compared with the same
  runs without collusion: collective accuracy, colluders' private utility, reward,
  reputation.

## 9. Statistical analysis

- Unit of analysis: the seed (n = 10). Report mean, SD and 95% CI per system.
- Paired comparisons (PROPOSED vs BASELINE; ABLATION vs BASELINE): Shapiro–Wilk on the 10
  paired differences; if p > 0.05 a paired t-test with Cohen's d_z, otherwise a Wilcoxon
  signed-rank test with matched-pairs rank-biserial correlation. Two-sided, α = 0.05.
  CI of the mean difference: t-interval, or 10,000-resample percentile bootstrap if
  normality is rejected.
- Confirmatory family {H1: F, H2: E, H3: M}: Holm correction across the three tests.
- H4: per seed, degradation(p) = accuracy(p = 0) − accuracy(p). Friedman test across p within
  each system; primary comparison = mean degradation over p ∈ {0.1, 0.2, 0.3, 0.4}, PROPOSED
  vs BASELINE, paired test as above; Holm across the per-p post-hoc comparisons.
- H5: detection rate and false-positive rate reported descriptively (hash comparison is
  deterministic; no inferential test).
- Relative improvement = (Proposed − Baseline)/|Baseline|.
- With n = 10 the smallest attainable two-sided Wilcoxon p is 0.002; inference limits are
  stated wherever results are reported.

**Decision rules (Critical Checkpoint):** for each of F, E, M —
*improved* if the Holm-adjusted p < 0.05 in the hypothesised direction and |relative
improvement| ≥ 5%; *negligible* if not significant or < 5%; *worse* if significant in the
opposite direction. Continue to blockchain work only if at least one is improved and none is
worse; otherwise investigate before adding infrastructure. Whatever the outcome, results are
reported as obtained; weights are not re-tuned to obtain support.

## 10. Known design limits declared up front

- Agents that maximise a payoff containing F and E will tend to raise F and E. The
  experiment therefore tests **whether and by how much the incentive outweighs the private
  gain from steering the decision** on real scenarios, at pre-declared weights — not whether
  rewarding a quantity can ever increase it. ω and the weight sensitivity quantify this.
- The audit is white-box (the mechanism can recompute SHAP and model probabilities).
- The reference decision is constructed (§3) and ignores network constraints.
- Agents' models share a target; their feature views overlap partially.

## 11. Pharma case study

**Status: FROZEN 2026-10-06 by amendment 2 (§12), before any pharma agent model was trained
or any mechanism outcome computed.** Everything not restated here is exactly as in §5–§9
(v1.1): strategy space, report construction, collective decision rule, bandit, payoff,
metrics, incentive weights, reward, reputation, robustness conditions, statistical tests and
decision rules.

**What was looked at before freezing** (design feasibility only): the dataset audit
(`docs/dataset_audit.md` §5); the number of scenarios and their split sizes; the slot shares
of the constructed reference; how often each criterion's preferred candidate coincides with
the reference (46–52%); the agreement of the reference with the site actually used (below);
and the reference's sensitivity to its weights (below).

### 11.1 Data and scenarios

- Source: SCMS delivery history (USAID/PEPFAR), `data/raw/pharma_scms/`. **Only
  direct-from-supplier lines** (`Fulfill Via` = "Direct Drop", 4,920 of 10,324) are used,
  because on warehouse lines the delivery outcome is not the manufacturer's (audit gap S-4).
- Supplier = `Manufacturing Site` (gap S-3). Product = `Molecule/Test Type` + `Dosage` +
  `Dosage Form`.
- **Scenario** = one purchase order for one product (`PO / SO #` × product) that has an order
  date (`PO Sent to Vendor Date`); lines of the same order and product are merged (units
  summed).
- **History rule (no leakage):** everything known about a site in a scenario is computed from
  direct-drop lines *delivered strictly before the order date*. The order's own outcome is
  never used.
- **Candidates (constructed; gap S-2):** the three sites that most recently delivered the
  product before the order date (ties: more deliveries of the product, then site name), among
  sites with a positive recorded price for it. Orders with fewer than three such sites are
  not scenarios. Slot order within a scenario is a hash of order, product and site, so slot
  index carries no information. The file contains no real competing offers; the candidate set
  is an experimental construction and is labelled as such.
- Result: **1,648 scenarios**, 31 products, 49 sites, orders 2007-07-03 to 2015-08-24. The
  site actually used is one of the three candidates in 83% of scenarios.
- **Split, time-ordered on order date** (orders of one day share a split): first 50% train
  (824; to 2012-08-15), next 10% validation (165), last 40% test (659; from 2013-08-05).
- Derived variables (all computed from real columns; none is an original observation):

| Variable | Definition (history = lines delivered before the order date) |
|---|---|
| `exp_unit_price` | median of the site's 5 most recent unit prices for the product; unit price = `Pack Price` ÷ `Unit of Measure (Per Pack)`; zero prices ignored |
| `price_rel`, `last_price_rel` | `exp_unit_price`, and the site's latest price, ÷ mean `exp_unit_price` of the three candidates |
| `price_cv` | coefficient of variation of the site's past prices for the product (0 if one) |
| `log_order_units` | log(1 + units ordered) — scenario-level |
| `ontime_rate` | (on-time lines + 1) ÷ (lines + 2) over all the site's past lines; on time = delivered on or before `Scheduled Delivery Date` |
| `ontime_rel` | `ontime_rate` − mean over the candidates |
| `mean_late_days`, `late_last5`, `log_n_lines` | mean days late (0 if on time); late share of the last 5 lines; log(1 + lines) |
| `median_lead_days` | median days from order date to delivery over the site's past lines with an order date; the median over all sites' past lines if the site has none (2.7% of candidate rows) |
| `lead_rel`, `lead_iqr`, `log_n_lead` | ratio to the candidates' mean; interquartile range; log(1 + lines with a lead time) |
| `requested_lead_days` | scheduled delivery date − order date — scenario-level |
| `freight_per_kg` | median `Freight Cost (USD)` ÷ `Weight (Kilograms)` over the site's past lines where both are numbers; the median over all sites' past lines if it has none |
| `freight_rel`, `share_air`, `share_freight_included`, `log_n_country_lines` | ratio to the candidates' mean; share of past lines by air; share with freight included in the commodity cost; log(1 + past lines to the destination country) |
| `n_product_lines`, `log_n_product_lines`, `product_share` | the site's past deliveries of the product; its log; its share among the candidates |
| `days_since_last`, `n_countries`, `log_units_supplied` | days since the site last delivered the product; countries it has delivered to; log(1 + units of the product delivered) |

### 11.2 Reference decision — a *constructed reference*, not an observation

Five criteria, one per agent, each min–max normalised over the three candidates of a
scenario (0.5 for all three if they are equal): cost = −`exp_unit_price`; reliability =
`ontime_rate`; lead time = −`median_lead_days`; logistics = −`freight_per_kg`; continuity =
`n_product_lines`. **Reference = the candidate with the highest equal-weight (0.2 each) sum**;
ties to the lowest slot (none occur). Equal weights are used because the source gives no
weights and none are invented; the multi-criteria form follows standard supplier-selection
practice (cf. the figshare criteria study, §4.1 of CLAUDE.md).

Declared limits of this reference:
- It **does not reproduce the programme's real choices**: where the site actually used is a
  candidate, the reference picks it in 35% of scenarios (chance is 33%). The reference is a
  normative score, not a model of SCMS procurement.
- **Weight sensitivity:** dropping one criterion leaves the reference unchanged in 68–74% of
  scenarios; doubling one, in 72–82% (`data/processed/pharma/scenarios_meta.json`).
- There is no quality or compliance criterion because the data has none (gap S-1).

### 11.3 Agents

| Agent | Private objective u_i(c, t) | Feature view (of candidate c) |
|---|---|---|
| Cost | −`exp_unit_price` | `exp_unit_price`, `price_rel`, `last_price_rel`, `price_cv`, `log_order_units` |
| Delivery reliability | `ontime_rate` | `ontime_rate`, `ontime_rel`, `mean_late_days`, `log_n_lines`, `late_last5` |
| Lead time | −`median_lead_days` | `median_lead_days`, `lead_rel`, `lead_iqr`, `log_n_lead`, `requested_lead_days` |
| Logistics | −`freight_per_kg` | `freight_per_kg`, `freight_rel`, `share_air`, `share_freight_included`, `log_n_country_lines` |
| Supply continuity | `n_product_lines` | `log_n_product_lines`, `product_share`, `days_since_last`, `n_countries`, `log_units_supplied` |

- ũ_i = u_i min–max normalised over the three candidates; preferred candidate a*_i = argmax,
  ties to the lowest slot. Feature views do not overlap.
- **Model:** `RandomForestClassifier(n_estimators=100, max_depth=6)`, seeded per agent and
  run seed, trained on the train split with one row per (scenario, candidate) and target
  "this candidate is the reference". The agent's probability for candidate c is the model's
  positive-class score of c divided by the sum over the three candidates (1/3 each if all
  scores are zero); its model vote is the argmax.
- **SHAP:** exact TreeSHAP of the positive-class score of the voted candidate's own feature
  row. Attributions are additive to that *unnormalised* score, not to the normalised
  probability; fidelity, explanation and evidence are computed on it exactly as in §5–§6,
  with tercile thresholds from the training rows.
- Actions = the three candidate slots. Decision quality D_i = 1 if the agent's vote is the
  reference.

### 11.4 Game size and runs

- Rounds: **600** of the 659 test scenarios, drawn without replacement per seed and played in
  order of order date; evaluation window = **last 300** rounds. (Energy uses 1,000 and 500;
  the pharma test split is smaller. Fewer rounds give the bandit less time to converge; this
  is a declared limit, not tuned.)
- All other game parameters, incentive weights, ρ, seeds (0–9), systems
  (baseline/ablation/proposed), robustness conditions (malicious share 0–40%, collusion),
  tests and decision rules: as for energy v1.1.
- Consistency: nearest neighbours in the agent's standardised feature view of the voted
  candidate.

### 11.5 Hypothesis H6

After the pharma runs, H6 is assessed as in CLAUDE.md step 32: the direction, and the
relative improvement, of F, E and M in both domains. "Similar qualitative improvement" =
same direction with the §9 decision rule giving the same verdict (improved / negligible /
worse) in both domains.

## 12. Amendments

### Amendment 1 — 2026-10-05 (protocol v1.1): two partially-truthful strategies

**Status of the evidence.** This amendment was written *after* the v1.0 energy results were
seen, at the user's instruction following the Critical Checkpoint report. Results under
v1.1 are therefore not a blind confirmation of v1.0. The v1.0 summaries and tables are
kept unchanged in `results/summaries/v1.0/` and `tables/v1.0/` and must be reported next to
the v1.1 results. The amendment text was committed before any v1.1 run.

**Reason.** Under v1.0 every report was either fully truthful (F = 1, E = 1) or fully
falsified (F = 0, E = 0), so fidelity and evidence support were the same number and H1 and
H2 could not be told apart.

**Change.** S_i gains two strategies; nothing else in §2–§9 changes (weights, seeds, rounds,
tests and decision rules are as in v1.0).

| Strategy | Vote and confidence | Explanation | Evidence |
|---|---|---|---|
| misattributing | as *strategic* | true top k−1 features, plus the least important feature with its sign flipped | true levels for the reported features |
| overclaiming | as *strategic* | truthful | true except the last claim, which is false |

Misattributing lowers F but not E; overclaiming lowers E (to 0.5 with k = 2) but not F.
S_i = {honest, strategic, misattributing, overclaiming, manipulative}; ε-greedy exploration
is uniform over the five, so the exploration floor is 2% per non-honest strategy.
Malicious agents (§8) still play *manipulative*; collusion is unchanged.

**Analysis.** The confirmatory family {F, E, M} with Holm correction is applied to the v1.1
runs exactly as in §9.

**Sensitivity runs brought forward (user decision).** The ω sensitivity of §7
(0.25, 0.5, 0.75) is run now instead of in Phase 10, under v1.1, for baseline, ablation and
proposed. ω = 0.9 is added as an **exploratory, not pre-declared** value to see whether a
strongly self-interested agent still prefers honesty; it carries no confirmatory weight.

**Limitation not addressed by this amendment.** In this game an explanation never
influences the collective decision, so falsifying one brings an agent no benefit even in
the baseline; explanation attacks are imposed interventions, not profitable deviations.

### Amendment 2 — 2026-10-06 (protocol v1.2): pharma case study on SCMS delivery history

**Reason.** The primary pharma file named in CLAUDE.md §4.1 (figshare) is a list of 24
criteria with no observations (audit gap P-1). The user supplied the USAID/PEPFAR SCMS
delivery history and, on 2026-10-06, approved: (1) adopting it as the primary pharma dataset;
(2) five agents defined from available variables (Cost, Delivery reliability, Lead time,
Logistics, Supply continuity) instead of the template's Quality and Compliance roles, for
which the data has no variable; (3) using only direct-from-supplier lines; (4) a constructed
reference decision.

**Change.** §11 is written and frozen (was "Deferred"). Nothing in §1–§10 changes; the
energy protocol and its results are unaffected.

**Status of the evidence.** The pharma design was fixed after the energy results (v1.0 and
v1.1) were known, and reuses the energy mechanism unchanged. It is therefore a
pre-specified replication on a second domain, not an independent blind design. What was
inspected before freezing is listed at the top of §11. This amendment was committed before
any pharma agent model was trained.

**Deviations from CLAUDE.md recorded here.** Agent roles differ from the §Phase 3 template
(approved, above). The quality/compliance gap is dropped, not simulated.

### Amendment 3 — 2026-10-11 (protocol v1.3): LLM agents

**Status: FROZEN 2026-10-11, before any LLM agent was run on a test scenario.**

**Reason.** The user stated that the study is about LLM agents, to be run with open-source
models through Ollama on Kaggle's free GPU. This overrides CLAUDE.md Golden Rule 12 and §9
(user decision; CLAUDE.md itself is unchanged). Sizes were fixed by the user ("don't
increase more seeds or rounds"). Where the user gave no explicit answer, the recommendation
put to them is used and marked *(default)*.

**Status of the evidence.** Designed after the classical results of both domains were
known. Three pilots were run on **validation** scenarios of pharma (10 rounds, one seed
each; `results/pilot/`), and the prompt was changed twice in response to them: features
listed by importance (after pilot 1) and the truthful explanation stated outright (after
pilot 2). A stopping rule was set before pilot 3 and no prompt change followed it. No LLM
agent has seen a test scenario. The pilots are feasibility checks and are not results.

#### A3.1 Agents
- Each agent keeps its §4 / §11.3 Random Forest and exact TreeSHAP values as a private
  analysis tool. Training, feature views, private objectives, reference decisions, splits
  and the audit are unchanged.
- The agent's report is chosen by an LLM. Per round it is given: its private gain for each
  option (ũ_i), the tool's probability for each option, the tool's features for each option
  ordered by |SHAP| with observed level (train terciles) and direction, the truthful
  explanation of each option stated outright, and its own last 3 rounds (vote, tool's top
  option, group decision, reward, payoff; plus the fidelity and evidence audit values only
  in systems that audit). The reference decision is never shown.
- The system prompt states the agent's private objective, the payoff rule
  π_i = ω·ũ_i(collective) + (1 − ω)·R_i with ω = 0.5, and in plain words how R is computed
  in that system, with its weights. In systems with the explanation-aware incentive it says
  that an auditor sees the tool's output; in the baseline that explanation and evidence are
  recorded but not checked; with reputation, that voting weight is reputation.
- Reply: JSON constrained by schema to vote ∈ options, confidence ∈ [0, 1], two
  (feature, direction, level) triples with feature ∈ the agent's own view. An unparsable
  reply is retried once (seed + 1); if still unusable, the tool-supported report is used and
  the event counted. The exact prompt text is `agents/llm_agent.py` at the commit of this
  amendment.
- **Model:** `qwen2.5:7b`, Q4_K_M, Ollama digest
  `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`; temperature 0;
  request seed = 1000·(run seed) + attempt; context 2,048 tokens; at most 120 output tokens;
  the five agents of a round are queried concurrently. A run refuses to start if the served
  model's digest differs. Chosen by the stopping rule of 2026-10-07 (highest reading-check
  value ≥ 0.80; tie with qwen2.5:14b broken by speed, a tie-break not written beforehand).
- No strategy is scripted for an LLM agent and there is no bandit; behaviour is whatever the
  model returns. There is therefore no strategy-share table and no unilateral-deviation
  table for LLM runs.

#### A3.2 Runs (per case study)
- **Main:** systems baseline, ablation, proposed (weights, ρ, reward rule as in §7);
  **200 rounds** drawn per seed from the test split as in §2 / §11.4; **seeds 0–4**; all
  three systems of a seed play the same rounds with the same tools. Evaluation window: all
  200 rounds (no burn-in; there is no learning phase to discard).
- **Malicious agents:** shares 0.2 and 0.4 = 1 and 2 of 5 agents, taken from a seeded agent
  order; they are **scripted** *manipulative* agents exactly as in §5/§8 *(default)*; the
  others are LLM agents. Baseline and proposed; the **first 100 rounds** of the seed's 200;
  **seeds 0–2**. The share-0 condition is the first 100 rounds of the same seed's main run.
  Shares 0.1 and 0.3 are not run.
- **Collusion:** a seeded pair of scripted colluders as in §8; the other three are LLM
  agents; baseline and proposed; first 100 rounds; seeds 0–2; compared with the first 100
  rounds of the main run.
- **Energy gate:** no LLM pilot was run on energy. Before the energy runs, a 10-round check
  on energy validation scenarios must pass the pilot sanity checks (usable replies, votes
  and confidence not constant, reading check ≥ 0.80); otherwise the energy LLM runs do not
  start and the failure is reported.
- Runs execute on Kaggle with its library versions, not the pinned local environment; the
  versions are recorded in each manifest. The agents' Random Forests may therefore differ
  slightly from the local classical runs.
- Every raw model reply is saved, because concurrent inference is not bit-reproducible
  (pilot 2: identical votes, a few differing explanations).

#### A3.3 Analysis
- Unit of analysis: the seed (n = 5 main; n = 3 robustness). Mean, SD, 95% CI.
- Confirmatory family {H1: F, H2: E, H3: M}, proposed vs baseline, paired test and Holm
  correction exactly as in §9, with the same decision rule (Holm p < 0.05 and |relative
  change| ≥ 5%).
- **Declared limit of n = 5:** a two-sided Wilcoxon signed-rank test cannot give p < 0.0625
  with five pairs. If Shapiro–Wilk rejects normality for a metric, that comparison is
  reported with its effect size and interval and is "not significant" by construction; this
  is stated wherever it happens. The t-test's normality assumption can hardly be checked at
  n = 5.
- Pre-declared secondary outcomes (descriptive, unadjusted p): strategic voting (share of
  votes against the tool's top option), confidence inflation, share of votes for the
  agent's privately preferred option, collective accuracy, manipulation success, share of
  fully truthful explanations, share of unusable replies.
- **H4** (n = 3 seeds, two shares): accuracy degradation relative to share 0, proposed −
  baseline, reported with mean, SD and CI; **no confirmatory claim** is made from three
  seeds.
- Classical (scripted-agent) results of §2–§11 are kept and reported next to the LLM results
  as a separate arm *(default)*. They differ in rounds, seeds, environment and in how
  behaviour arises, so the comparison across arms is qualitative.

#### A3.4 Known risks declared before the runs
- **Ceiling.** In pilot 3, with the truthful explanation stated in the prompt, fidelity and
  evidence support were ≥ 0.97 in the *baseline* for all three models. If this holds, H1 and
  H2 cannot show an effect for LLM agents, and that will be reported as the finding ("LLM
  agents of this kind do not misreport explanations they are handed"), not repaired by
  changing the prompt.
- Making truthful reporting trivial is a design choice: it separates choosing to misreport
  from failing to read, at the price of making honest reporting the easy default.
- One model, one quantisation, temperature 0; results may not carry over to other models.
- The mechanism's rules are told to the agents (common knowledge); agents do not have to
  discover them.
- Scripted malicious agents among LLM agents test the mechanism's response to a controlled
  attack, not what a malicious LLM would do.

#### A3.5 Erratum to A3.1 — 2026-10-11, before any LLM run on test scenarios
The option list of the round prompt now marks the tool's top option in words
("(your tool's top option)"). Reason: probabilities are shown to two decimals, so two
options can look tied while the audit treats only one as the tool's top; an agent voting
for the other would have been counted as voting against its tool without being able to see
the difference. Found by a unit test of the run code, not by observing model behaviour; no
pilot was run with or after this change. It is nevertheless a prompt change made after the
stopping rule of 2026-10-07 and is disclosed as such. The frozen prompt text is
`agents/llm_agent.py` at the commit that adds this erratum.

### Amendment 3 suspended — 2026-10-11; pilot 4 in preparation of amendment 4

**Status.** Amendment 3 was never executed: no LLM agent has been run on a test scenario.
It is suspended, not withdrawn; its text above is kept unchanged.

**Reason.** The user passed on written advice on the design (pasted into the session; its
author was not stated). Its central point: a prompt that states the truthful explanation
makes the baseline truthful by construction (pilot 3: fidelity ≥ 0.97), so the experiment
cannot show whether the incentive makes an LLM agent explain more faithfully. It asks for
(a) agents that work out their own explanation from the tool's raw output, (b) a condition
with strategic pressure next to the natural one, each under baseline and proposed, and
(c) a validation pilot before any full run.

**This reverses A3.4**, which said a ceiling would be reported and "not repaired by changing
the prompt". The reversal is made before any test-scenario run, but after validation pilots
had shown the ceiling. It is a design change made with knowledge of pilot behaviour and has
to be reported as such in the paper.

#### Pilot 4 (validation scenarios only; fixed before it is run)
- Prompt style `raw` (`agents/llm_agent.py` at the commit adding this section): per option,
  every feature in the fixed order of the agent's view with its observed value, the two
  train-tercile cut-offs and its signed SHAP contribution. No ordering by importance, no
  level or direction words, no truthful explanation. The system prompt defines the top
  features as the two with the largest absolute contribution and says the agent has to work
  the explanation out itself. Within a run the baseline and proposed prompts differ only in
  the statement of the reward rules and in the audit values shown in the 3-round history.
- `qwen2.5:7b` (frozen digest), temperature 0, 20 rounds, seed 0, pharma and energy,
  baseline and proposed, under ω = 0.5 ("natural") and ω = 0.75 ("strategic pressure").
- The reading check (≥ 0.80) does not apply to the raw prompt: working out the explanation
  is now the behaviour under study. A new check verifies that the longest prompt fits the
  context window (Ollama truncates silently).

#### Rules fixed before pilot 4, to prevent tuning towards an effect
1. The raw prompt is used in the main runs whatever difference between baseline and proposed
   the pilot shows, including none or the wrong sign. The pilot is not used to choose a
   prompt, a condition or a model by its effect.
2. After pilot 4 the prompt may change only for unusable replies or a factual error in the
   prompt. If the prompt does not fit the context, the context window is raised and the
   prompt left as it is.
3. Strategic pressure is ω = 0.75, fixed now (the larger value of the classical ω
   sensitivity analysis); it is not chosen from the pilot.
4. If baseline fidelity is again ≥ 0.95 under the raw prompt, that is the finding for
   H1/H2 with LLM agents; no further prompt change follows.

#### Limits declared now
- In this game an explanation has no private payoff: it does not influence the collective
  decision. Private gain acts only through the vote and the stated confidence. Raising ω
  therefore raises the temptation to vote for the preferred option and to inflate
  confidence; it gives no motive to misexplain. Low fidelity under the raw prompt reflects
  the effort or ability an agent spends on its explanation, not a motive to deceive.
- An effect of the proposed system on fidelity may come from the instruction content of its
  reward rules ("the true top features ... are rewarded") and the audit feedback, not from
  the payoff as such. The design cannot separate the two.
- The explanation remains a structured report (two features, direction, level), not free
  text; free text could not be audited against SHAP without a second, unvalidated judge.

Amendment 4 (conditions, rounds, seeds, analysis) will be written after pilot 4 and needs
the user's approval before any test-scenario run. A natural × pressure design doubles the
model calls of amendment 3 at the sizes the user fixed.
