# Threats to Validity

Started 2026-10-05 (Phase 2). Updated as phases complete.

## Construct validity

- **The energy decision and its ground truth are constructed.** The dataset has no observed
  trades or storage dispatch. "Decision accuracy" means agreement with a perfect-foresight
  LP under assumed battery parameters (protocol §3, A1–A5), not agreement with real
  behaviour.
- **Derived variables.** Community load, PV output, net demand, price ranks and thermal
  total are computed from real columns; battery efficiency, C-rate, SOC window and daily
  cycle are simulated parameters. These reduce external validity.
- **Column meanings partly inferred.** The workbook has no data dictionary; the companion
  article (García-Muñoz et al. 2025) is paywalled and was not read. Units of prices and
  capacities, and the meaning of `BT`, are assumptions.
- **SHAP fidelity depends on the underlying model.** Fidelity is measured against each
  agent's own random forest. It says the report matches the model's attribution, not that
  the attribution is causally correct.
- **Manipulation score overlaps fidelity and evidence** (1 − F and 1 − E are two of its five
  components), so explanation quality is weighted more than β and γ alone suggest.

## Internal validity

- **Partial circularity.** Adaptive agents maximise a payoff that includes F and E in the
  proposed system. Improvement in F and E is therefore expected whenever the reward
  outweighs the private gain from manipulation; the informative quantities are the size of
  the effect, its sensitivity to weights (β, λ, ω), and behaviour under fixed malicious
  agents who do not respond to incentives.
- **Incentive weights affect behaviour.** α, β, γ, δ, λ, ω were fixed a priori, not derived
  from theory. Conclusions hold for the tested ranges only.
- **Reputation creates path dependence.** Early rewards shape later voting weights; results
  depend on round order (fixed chronological replay) and on ρ.
- **White-box audit assumption.** The mechanism recomputes SHAP and model probabilities. A
  real deployment with black-box agents could not measure F or confidence inflation this way.
- **Simple behavioural model.** ε-greedy bandits over three scripted strategies are not
  rational planners and cannot invent new attacks. No Nash-equilibrium claim is made.
- **Five agents make malicious shares coarse.** 10% and 30% are realised as time-averaged
  expectations, not as fixed head-counts.

- **Fidelity and evidence support are degenerate in the current strategy set** (found in
  the energy runs): truthful reports score 1/1 and falsified reports 0/0, so both metrics
  reduce to the share of non-falsified reports. They are not independent outcomes, and no
  graded explanation quality is exercised.
- **Baseline already favours honesty.** At ω = 0.5 the decision-quality reward makes honest
  the best unilateral response even without the explanation-aware terms; the measured
  benefit is a wider payoff gap that ε-greedy learners resolve more reliably, capped by the
  3.3% exploration floor.

## External validity

- **Energy data provenance.** The network is a modified IEEE European LV test feeder
  (repository abstract). Only 22 distinct demand shapes and 3 thermal shapes exist for 55
  users, and all users share one peak load. Whether the profiles are metered or modelled is
  unverified; the data must not be described as metered household observations until checked.
- **One community, one year, hourly resolution**, no network power flow.
- **Pharma case study not yet run.** The specified file is a list of 24 criteria names. The
  study's other tables give 4 suppliers × 4 criteria × 2 decision makers — not
  transaction-level, tiny, and able to support at most four criterion-based agents plus one
  on rating reliability. H6 (cross-domain) is untested.
- **Dataset-specific criteria constrain agent design** in both domains.

## Statistical conclusion validity

- Ten seeds; scenarios within a run are autocorrelated hours, so the seed is the unit of
  analysis. Seeds share the same year of data: variation across seeds reflects model,
  sampling and exploration randomness, not variation across communities.
- Small-n normality checks have low power; test choice is pre-declared (protocol §9).

## Blockchain layer (Phase 8, not yet built)

- Blockchain provides integrity and provenance, **not truth**: a faithfully recorded false
  explanation verifies as valid.
- A local hash-chain simulator's latency/storage figures may differ from production networks
  and include no consensus, networking or gas costs.

## Literature

- The gap assessment rests on a non-systematic review; several close works were read at
  abstract level only and one (Tian 2025) not at all (`docs/research_gap.md`).
