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
- **Pharma data is one programme's procurement, not the pharmaceutical supply chain.** The
  case study uses USAID/PEPFAR SCMS shipment lines (protocol §11): antiretrovirals and HIV
  test kits, one buyer, 2007–2015, direct-from-supplier lines only (48% of the file). The
  originally specified figshare file is a list of 24 criteria names with no observations.
  The file's identity with the publisher's copy could not be checked (publisher site
  offline); its licence is taken from a catalogue mirror.
- **The pharma choice set and ground truth are constructed.** The data records the supplier
  that was used, never the offers it was compared with. Candidates are the three sites that
  most recently delivered the product; the reference is an equal-weight score of five
  history-based criteria. That reference agrees with the site actually used in only 35% of
  scenarios (chance 33%) and changes in 18–32% of scenarios when one criterion's weight is
  doubled or dropped. Pharma "decision accuracy" is agreement with this normative score, not
  with real procurement decisions or real outcomes.
- **No quality or compliance evidence in pharma.** The data has no inspection, rejection or
  audit variable, so the template's Quality and Compliance agents were replaced by Lead-time
  and Supply-continuity agents (user-approved). Claims about "quality" cannot be made.
- **All pharma agent features are derived** from a site's earlier shipments (prices,
  on-time record, lead times, freight per kg, volumes). Some histories are short; missing
  lead-time or freight history is filled with the all-site median of the time.
- **Late-delivery share drifts by year**, and the pharma test period (2013–2015) differs from
  the training period (2007–2012); models are evaluated out of time by design.
- **Pharma was designed after the energy results were known** and reuses the mechanism
  unchanged; it is a replication on a second domain, not an independent blind test. Its game
  has 600 rounds (energy 1,000), so strategy learning has less time to settle.
- **Dataset-specific criteria constrain agent design** in both domains.

## Statistical conclusion validity

- Ten seeds; scenarios within a run are autocorrelated hours, so the seed is the unit of
  analysis. Seeds share the same year of data: variation across seeds reflects model,
  sampling and exploration randomness, not variation across communities.
- Small-n normality checks have low power; test choice is pre-declared (protocol §9).

## Blockchain layer (Phase 8, protocol amendment 5)

- Blockchain provides integrity and provenance, **not truth**: a faithfully recorded false
  explanation verifies as valid.
- One local Anvil node run by the experimenter, with instant mining: latency figures exclude
  consensus, block time and network delay and are not production estimates. Gas is a
  property of the EVM and transfers to other EVM chains; its price does not.
- The design detects changes to off-chain artifacts after recording. It does not protect
  against an actor who controls the chain or who records false artifacts in the first place.
- Reward and reputation are stored with six decimals; smaller changes are invisible by design.
- Recorded artifacts are the saved LLM runs, recorded after the fact rather than during the
  game; the hashes and verification are the same either way, but recording latency was not
  part of the agents' decision loop.

## Literature

- The gap assessment rests on a non-systematic review; several close works were read at
  abstract level only and one (Tian 2025) not at all (`docs/research_gap.md`).
