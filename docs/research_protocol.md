# Research Protocol (Phase 2, Step 05)

**Status: FROZEN 2026-10-05 for the energy case study** (protocol version 1.0; amended to v1.1, see §12). Any later
change is recorded in §12 as a dated amendment with its reason. The pharma case study is
deferred by user decision (research log, GATE 1); its protocol section (§11) will be frozen
by amendment before any pharma experiment is run.

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

Deferred. To be specified and frozen by amendment before any pharma experiment.

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
