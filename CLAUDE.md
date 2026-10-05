# CLAUDE.md — Explanation-Aware Incentive Mechanism for Trustworthy Multi-Agent AI

> Step-by-step execution guide for Claude Code. Read this file fully at the start of every session.
> Work through the phases **in order**. Do not skip a phase gate. Log progress in `docs/research_log.md`.

---

## 0. Project Summary

**Title:** Explanation-Aware Incentive Mechanism for Trustworthy Multi-Agent AI with Blockchain Provenance

**Central research question:** Can an explanation-aware game-theoretic incentive mechanism encourage multiple AI agents to produce more faithful and evidence-supported explanations while reducing strategic manipulation, with blockchain providing tamper-evident provenance of decisions and explanations?

**Core novelty:** the explanation-aware incentive (fidelity + evidence become part of agent utility). Blockchain is only a provenance/integrity layer, **not** the primary contribution.

**Two case studies (real data first):**
1. Pharmaceutical supplier selection
2. Peer-to-peer (P2P) energy trading / allocation

### Research questions
- RQ1: Do explanation-aware incentives improve explanation fidelity?
- RQ2: Do they improve evidence support?
- RQ3: Do they reduce strategic explanation manipulation?
- RQ4: Does the mechanism stay robust as the malicious-agent share increases?
- RQ5: Can blockchain reliably detect modification of recorded decisions/explanations?
- RQ6: Does the mechanism generalize across pharma and energy?

### Hypotheses (never assume support; conclusions come only from results)
- H1: Proposed mechanism improves explanation fidelity vs. baseline.
- H2: It improves evidence support.
- H3: It reduces strategic manipulation.
- H4: It is more robust to increasing malicious-agent percentages.
- H5: Blockchain hash verification detects post-record modification.
- H6: Similar qualitative improvements appear in both case studies.

---

## 1. Golden Rules (apply to every step)

1. **Real data is the primary evidence.** Never replace the real datasets with fully synthetic data because it is easier.
2. **Dataset-first.** Inspect the actual schema before designing agents. **Never invent columns.**
3. **Controlled perturbations only for attacks/stress tests** (manipulation, missing values). They modify agent behavior or explanation outputs, **never** the underlying real observation. Label them as experimental interventions.
4. **Label derived/simulated variables clearly.** Never present them as original observations. Document every such variable and why it is scientifically justified.
5. **Never modify original downloaded files.** `data/raw/` is read-only after download.
6. **Never fabricate numbers, p-values, citations, or significance.** If something wasn't run, say so.
7. **Never claim exact Nash equilibrium** unless actually computed and justified.
8. **Do not call TRACE-X-Bench real-world observational data** (it is a benchmark/synthetic environment).
9. **Blockchain proves integrity, not truth.** It shows an artifact wasn't changed after recording; it does not prove the explanation was truthful.
10. **Determinism:** fixed seeds, deterministic preprocessing, every seed and config saved.
11. **Do not build elaborate infrastructure around an unvalidated mechanism.** Obey the Critical Checkpoint (Phase 6).
12. **Start simple:** interpretable models (RF / GBM / Logistic Regression / Decision Tree). No deep learning or LLMs unless the data genuinely requires it.
13. **Test as you go.** Every module gets pytest tests before moving on.
14. **If something is ambiguous or a variable is missing, stop, document the gap in `docs/research_log.md`, and ask the user** before inventing a workaround.

---

## 2. Repository Structure

Create this structure in Phase 0:

```
research-project/
├── data/
│   ├── raw/                # original downloads, never modified
│   ├── processed/
│   └── metadata/           # hashes, versions, download dates, licenses
├── agents/
├── environments/
│   ├── pharma/
│   └── energy/
├── game/
├── xai/
├── incentives/
├── reputation/
├── blockchain/
├── experiments/
├── evaluation/
├── statistics/
├── configs/
├── results/
│   ├── raw/
│   ├── processed/
│   └── summaries/
├── figures/
├── tables/
├── tests/
├── docs/
│   ├── dataset_audit.md
│   ├── literature_matrix.csv
│   ├── research_gap.md
│   ├── research_protocol.md
│   ├── threats_to_validity.md
│   └── research_log.md
├── README.md
├── CLAUDE.md
└── run_experiment.py
```

---

## 3. Architecture (pipeline to implement)

```
REAL DATASET
  → Preprocessing
  → Scenario Construction
  → 5 Specialized AI Agents
  → Game-Theoretic Interaction
  → Collective Decision
  → XAI / SHAP
  → Explanation Evaluation (fidelity, evidence, consistency)
  → Explanation-Aware Incentive
  → Reward
  → Reputation
  → Blockchain Provenance
  → Verification
```

**Compared systems**

| System | Components |
|---|---|
| **BASELINE** | Game + XAI (no explanation-aware incentive) |
| **PROPOSED** | Game + XAI + Explanation-Aware Incentive + Reputation + Blockchain Provenance |
| **ABLATION** | Game + XAI vs. Game + XAI + Explanation-Aware Incentive (blockchain/reputation excluded if needed to isolate the incentive effect) |

Use **identical real-data scenarios and identical random seeds** for paired comparison.

---

## 4. Primary Datasets

### 4.1 Pharmaceutical — Supplier Selection Criteria in Pharmaceutical Companies
- Dataset: https://figshare.com/articles/dataset/Supplier_selection_criteria_in_pharmaceutical_companies_/6971474
- Published study: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0201604
- ⚠️ Do **not** describe it as a large transaction-level dataset. Inspect its exact structure first and adapt the environment to the variables actually available.

### 4.2 Energy — Operational Data of an Energy Community Under P2P Trading and Flexibility Markets
- Dataset: https://data.mendeley.com/datasets/bvp4vrn9gc/1
- Expected (to verify, not assume): hourly demand, PV generation, DER information.

### 4.3 Optional supplementary (only AFTER the core experiment succeeds; must not delay it)
- TRACE-X-Bench (pharma supply-chain/counterfeit benchmark; synthetic/benchmark, label accordingly)
- P2P Electricity Markets code/data: https://github.com/d-vf/P2PEnergyTrading
- Cardiff P2P energy-trading datasets

> **Environment note:** the sandbox may not be able to reach figshare.com / data.mendeley.com. If a download fails, check the `x-deny-reason` header, tell the user, and ask them to place the files in `data/raw/` manually or adjust network settings. Do not substitute synthetic data.

---

## 5. Execution Plan (step by step)

Each phase ends with a **GATE**. Do not proceed until the gate is satisfied. After each phase: update `docs/research_log.md`, run `pytest`, and commit.

---

### PHASE 0 — Project setup

1. Create the repository structure from §2.
2. Create a Python environment (3.10+). Pin dependencies in `requirements.txt` (suggested: `numpy`, `pandas`, `scikit-learn`, `shap`, `scipy`, `statsmodels`, `matplotlib`, `pyyaml`, `pytest`, `openpyxl`, and a local-chain library such as `web3` + `eth-tester`/Ganache, or a clearly documented hash-chain simulator).
3. Create a global seeding utility (`utils/seed.py`) that seeds `random`, `numpy`, and any model RNGs.
4. Create `run_experiment.py` with a `--config` argument that loads a YAML config, seeds, runs the experiment, and writes results to `results/`.
5. Create initial config stubs in `configs/`:
   - `pharma_baseline.yaml`
   - `pharma_proposed.yaml`
   - `pharma_adversarial.yaml`
   - `energy_proposed.yaml`
   - (add `energy_baseline.yaml` and ablation configs as needed)
6. Initialize `docs/research_log.md` with a dated entry.

**GATE 0:** repo structure exists, `pytest` runs (even with zero tests), `run_experiment.py --help` works.

---

### PHASE 1 — Dataset acquisition and audit (Steps 01–02)

1. Download both primary datasets into `data/raw/`. Do not modify them.
2. Record in `data/metadata/`: source URL, version, download date, SHA-256 file hash, license, citation text.
3. For **each** dataset, inspect and document:
   - every column (name, dtype)
   - categorical vs. numerical variables
   - missing values (counts and %)
   - duplicates
   - outliers
   - the **unit of observation** (supplier-level / company-level / transaction-level / household-level / time-series)
   - licensing and citation requirements
4. Write `docs/dataset_audit.md` with the complete audit. **Do not invent columns.**
5. Explicitly document what the dataset **lacks** relative to the mechanism's needs (e.g., missing cost/quality/delivery/compliance variables, missing storage/grid variables). For each gap, record whether it will be (a) dropped, (b) mapped to an available variable, or (c) derived/simulated — and justify (c) scientifically.

**GATE 1:** `docs/dataset_audit.md` complete for both datasets; gap list documented; user informed of any gap that forces a design change.

---

### PHASE 2 — Literature review and research-gap validation (Steps 03–05)

1. Build `docs/literature_matrix.csv` with columns such as: `citation, year, domain, method, uses_game_theory, uses_xai, uses_incentive, uses_blockchain, explanation_quality_in_utility, dataset, limitations`.
   - Cover: multi-agent incentive design/mechanism design, XAI fidelity (SHAP), explanation manipulation/adversarial explanations, reputation systems, blockchain provenance for AI, pharma supplier selection, P2P energy trading.
   - Only include sources you can verify. **Never fabricate citations.** If search is unavailable, say so and ask the user for sources.
2. Write `docs/research_gap.md`: validate whether the gap (explanation fidelity + evidence support inside agent utility, with provenance) is genuinely unaddressed. Phrase claims only as strongly as the literature supports.
3. Write `docs/research_protocol.md`: freeze the hypotheses, metrics, parameters, seeds, statistical tests, and decision rules **before** running experiments. Include the pre-declared analysis plan.
4. Start `docs/threats_to_validity.md` (see §8 for the required limitations).

**GATE 2:** literature matrix, research gap, and protocol written. Protocol frozen (changes afterward must be logged as amendments).

---

### PHASE 3 — Pharmaceutical environment (Steps 06–08)

**Step 06 — Preprocessing**
1. Create raw/processed/metadata flow; write processed files to `data/processed/pharma/`.
2. Handle missing values with a documented method; normalize where required; encode categoricals appropriately.
3. Keep preprocessing **deterministic**.
4. Create train/validation/test partitions where applicable; **prevent leakage** between related observations.

**Step 07 — Ground truth**
1. Use the published decision methodology and/or a transparent optimization/scoring formulation as the reference decision.
2. If the source study provides rankings/optimization results, **reproduce them** rather than inventing weights.
3. If a ground truth must be constructed, run a **sensitivity analysis over the weights** and label it clearly as a *constructed reference*.
4. Document the exact method in `docs/research_protocol.md`.

**Step 08 — Five agents (map after inspecting data)**
Conceptual roles (templates only — replace with formulas from actual variables):

| Agent | Template utility |
|---|---|
| Cost Agent | `U_cost = -Cost` |
| Quality Agent | `U_quality = Quality` |
| Logistics/Service Agent | `U_logistics = -DeliveryTime / ServicePenalty` |
| Risk/Reliability Agent | `U_risk = -Risk` |
| Compliance/Regulatory Agent | `U_compliance = Compliance` |

1. Create the exact mapping of dataset variables → agent objectives; document it in the audit/protocol.
2. Each agent has a **distinct objective** derived from real variables.
3. Agent model: lightweight and SHAP-compatible (Random Forest, Gradient Boosting, Logistic Regression, or Decision Tree). Choose after inspecting the data; justify the choice.
4. Write unit tests for agent behavior.

**GATE 3:** pharma preprocessing deterministic and tested; ground truth documented; 5 agents train and predict; tests pass.

---

### PHASE 4 — Pharmaceutical baseline, game, XAI, metrics (Steps 09–12)

**Step 09 — Baseline**
- Implement: Agents 1–5 → game/strategic interaction → collective decision → XAI. **No explanation-aware incentive.**

**Step 10 — Game-theoretic interaction**
- Formalize `G = (N, S, U)` with N = agents, S = strategy space, U = utility.
- Keep strategies simple and measurable: **honest, strategic, manipulative**.
- Define the collective decision rule (e.g., weighted/majority vote — document it).
- Do not claim Nash equilibrium unless computed and justified.

**Step 11 — SHAP / XAI**
- Use SHAP on the **actual trained model** and **actual dataset features**.
- Record: feature contributions, feature ranks, direction/sign, selected explanation features.
- Unit-test SHAP outputs (shape, additivity, determinism under fixed seed).

**Step 12 — Explanation metrics**

*Explanation fidelity* `F_i ∈ [0,1]` (starting formulation; finalize after inspecting data/model and validate with unit tests):
```
F_i = Σ |SHAP contribution| over explained important features
      ─────────────────────────────────────────────────────────
      Σ |SHAP contribution| over reference important features
```

*Evidence support:*
```
E_i = supported_claims / total_claims
```
A claim (e.g., "supplier has high quality") is supported only if the underlying observed value satisfies a **documented criterion**.

*Explanation consistency:*
- Build pairs/groups of similar real-data scenarios.
- Define **scenario similarity** and **explanation similarity** explicitly.
- Measure whether explanations stay reasonably consistent across similar scenarios.

*Also compute:* decision accuracy/quality, collective utility.

Write unit tests for fidelity (edge cases: empty explanation, perfect match, zero-SHAP denominator), evidence support, and consistency.

**GATE 4:** baseline runs end-to-end on real pharma scenarios with ≥5 seeds; fidelity/evidence/consistency validated by tests.

---

### PHASE 5 — Manipulation, incentive, reward, reputation (Steps 13–16)

**Step 13 — Manipulation model (controlled attacks)**
Implement:
1. False feature attribution
2. Confidence inflation
3. Unsupported evidence
4. Strategic voting
5. Collusion

Rule: attacks change **agent behavior or explanation outputs only**. The real observation is never altered. Define `M_i` (manipulation score) measurably for each attack and unit-test it.

**Step 14 — Explanation-aware utility**
```
U_i = α·D_i + β·F_i + γ·E_i + δ·C_i − λ·M_i
```
- D = decision quality, F = explanation fidelity, E = evidence support, C = contribution/cooperation, M = manipulation.
- **Normalize all components.** Keep α, β, γ, δ, λ **configurable** in YAML.

**Step 15 — Reward**
```
R_i = (U_i − U_min) / (U_max − U_min)
```
- **Handle `U_max == U_min` explicitly** (e.g., return a defined constant such as 0.5) and unit-test it.

**Step 16 — Reputation**
```
Rep_i^0 = 0.5
Rep_i^(t+1) = ρ·Rep_i^t + (1 − ρ)·R_i^t        # start with ρ = 0.8 (configurable)
```
- Unit-test the update rule and bounds.
- Plan sensitivity analysis over ρ (run in Phase 9).

**GATE 5:** all five attacks implemented and tested; utility/reward/reputation unit tests pass; configs expose all weights.

---

### PHASE 6 — Pharma main experiment + ablation + CRITICAL CHECKPOINT (Steps 17–18)

**Step 17 — Baseline vs. Proposed**
- BASELINE = Game + XAI. PROPOSED = Game + XAI + Incentive + Reputation (+ blockchain later).
- Use identical scenarios and seeds (paired). ≥5 seeds, preferably 10.
- Run: `python run_experiment.py --config configs/pharma_baseline.yaml` and `--config configs/pharma_proposed.yaml`.

**Step 18 — Incentive ablation**
- Game + XAI **vs.** Game + XAI + Explanation-Aware Incentive.
- Exclude blockchain and reputation if needed to isolate the incentive effect.

**🛑 CRITICAL CHECKPOINT — STOP AND INSPECT RESULTS**
After baseline, proposed, and ablation:
- If the incentive improves explanation quality and/or reduces manipulation → **continue**.
- If the improvement is negligible → **analyze why before adding blockchain complexity** (check metric definitions, weights, attack strength, data limits).
- If the mechanism fails → **report the failure honestly and investigate scientifically.**
- Do **not** build elaborate infrastructure around an unvalidated mechanism.

Write the checkpoint outcome in `docs/research_log.md` and **report to the user before proceeding.**

**GATE 6:** checkpoint decision recorded and communicated.

---

### PHASE 7 — Pharma robustness experiments (Steps 19–21)

**Step 19 — Malicious-agent experiment**
- Test **0%, 10%, 20%, 30%, 40%** malicious agents.
- Use controlled attack policies and identical real observations across conditions.
- Measure: decision quality, explanation fidelity, evidence support, manipulation success, collective utility, decision degradation under attack.
- Config: `configs/pharma_adversarial.yaml`.

**Step 20 — Collusion experiment**
- Two colluding agents + remaining honest.
- Test whether colluders can influence decisions, explanations, rewards, or reputation.

**Step 21 — Statistical analysis** (see §7 for the full list)

**GATE 7:** all robustness results saved in `results/raw/` with seeds and configs; stats computed without fabricated values.

---

### PHASE 8 — Blockchain provenance (Steps 22–24)

Only proceed if Phase 6 checkpoint supports continuing.

**Step 22 — Implementation**
- Store compact metadata + hashes only (never full explanations or raw datasets). Record schema:
```
record_id, agent_id, round_id,
decision_hash, explanation_hash, evidence_hash,
reward, reputation, timestamp
```
- Hashes: `H_D = SHA-256(Decision)`, `H_E = SHA-256(Explanation)`, `H_V = SHA-256(Evidence)`. Use canonical serialization (e.g., sorted-key JSON) so hashes are deterministic.
- Verification: `CurrentHash == BlockchainHash → VALID`; `CurrentHash != BlockchainHash → TAMPERED`.
- Use a local chain (or documented hash-chain simulator); state which in the paper.

**Step 23 — Tampering experiment**
1. Record the original decision/explanation; compute and store the hash.
2. Modify the artifact; compute a new hash; compare; record detection.
3. `DetectionRate = DetectedTampering / TotalTamperingAttempts`.
4. Vary tampering targets (decision, explanation, evidence, reward/reputation fields) and include non-tampered controls to check for false positives.

**Step 24 — Overhead**
- Measure: verification latency, transaction latency, transaction count, storage overhead, gas usage (where meaningful).
- Report as an **overhead/trade-off**, and note that local-chain overhead may differ from production networks.

**GATE 8:** hashing/verification unit tests pass; tampering detection measured; overhead reported.

---

### PHASE 9 — Energy case study (Steps 25–31)

Repeat the pipeline for energy using the **verified schema** of the Mendeley dataset.

1. **Step 25 — Preprocessing:** deterministic; time-series-aware train/val/test splits (**avoid temporal leakage**); document handling of missing values and normalization.
2. **Step 26 — Five agents.** Conceptual roles: Producer, Consumer, Price/Market, Grid, Storage. Map them to actual variables after inspection; if the dataset lacks a variable (e.g., price, grid constraints), document the gap and only derive/simulate if justified and **labeled as derived**.
3. **Step 27 — Baseline** (Game + XAI).
4. **Step 28 — Game + XAI:** same strategy space and SHAP workflow as pharma.
5. **Step 29 — Incentive experiment:** baseline vs. proposed vs. ablation.
6. **Step 30 — Adversarial experiment:** 0–40% malicious, plus collusion.
7. **Step 31 — Blockchain verification:** reuse the Phase 8 module; run tampering + overhead.
8. Run: `python run_experiment.py --config configs/energy_proposed.yaml` (and the corresponding baseline/adversarial configs).

**GATE 9:** energy pipeline reproduces the full set of pharma experiments with ≥5 seeds.

---

### PHASE 10 — Cross-domain, sensitivity, final stats (Steps 32–34)

**Step 32 — Cross-domain analysis**
- Compare **relative improvements**, not raw scores:
```
Relative improvement = (Proposed − Baseline) / |Baseline|
```
- Discuss whether the same mechanism yields consistent *qualitative* improvements (H6).

**Step 33 — Sensitivity analysis**
- At minimum vary: the **explanation-fidelity weight (β)** and the **reputation decay (ρ)**. Optionally vary α, γ, δ, λ and ground-truth weights (pharma).
- Report whether the main conclusions stay robust.

**Step 34 — Final statistics** (see §7).

**GATE 10:** cross-domain, sensitivity, and final stats complete and saved to `results/summaries/`.

---

### PHASE 11 — Figures, tables, reproducibility, paper (Steps 35–38)

**Step 35 — Tables** (save to `tables/`)
1. Table 1 — Dataset characteristics and preprocessing
2. Table 2 — Baseline vs. Proposed
3. Table 3 — Explanation fidelity / evidence / consistency
4. Table 4 — Incentive ablation
5. Table 5 — Malicious-agent robustness
6. Table 6 — Blockchain verification and overhead
7. Table 7 — Cross-domain comparison

**Step 35 — Figures** (save to `figures/`)
1. Overall framework architecture
2. Explanation-aware incentive mechanism
3. Baseline vs. proposed explanation fidelity
4. Explanation quality vs. malicious-agent percentage
5. Decision performance vs. malicious-agent percentage
6. Incentive ablation
7. Blockchain tampering detection
8. Cross-domain comparison

**Step 36 — Reproducibility package**
- README with exact commands, environment, dataset hashes, seeds, and configs.
- One-command reruns for each config; results regenerate tables/figures.

**Step 37 — Paper evidence**
- Compile a claim → evidence map: every claim in the paper links to a table/figure/result file. Remove any claim that lacks evidence.

**Step 38 — Paper writing**
- Phrase the contribution **according to what the literature and experiments actually demonstrate**. If H1–H6 are not all supported, report that plainly.

**GATE 11:** all tables/figures generated from saved results; reproducibility package verified by a clean rerun.

---

## 6. Testing (pytest) — required coverage

Create tests under `tests/` for:
- Dataset loading and schema validation
- Preprocessing (determinism, no leakage)
- Agent behavior
- Utility calculation
- SHAP outputs
- Fidelity
- Evidence support
- Consistency
- Manipulation
- Reward (including `U_max == U_min`)
- Reputation
- Hashing (determinism, canonical serialization)
- Blockchain verification (VALID / TAMPERED)
- Evaluation metrics

Run `pytest` at the end of every phase. Do not proceed with failing tests.

---

## 7. Statistical Analysis (never fabricate p-values or significance)

- Seeds: **≥5, preferably 10**. Save every seed and configuration.
- Report mean and standard deviation.
- 95% confidence intervals.
- Paired t-test **or** Wilcoxon signed-rank (check normality/assumptions; state which and why).
- Omnibus tests (e.g., repeated-measures ANOVA / Friedman) for multi-group comparisons (e.g., malicious-agent percentages).
- Effect sizes (e.g., Cohen's d / rank-biserial).
- Multiple-comparison correction when required (e.g., Holm/Bonferroni).
- With few seeds, state the limits of inference honestly.

---

## 8. Limitations to Report (`docs/threats_to_validity.md`)

- Synthetic or derived variables (if any) may reduce external validity.
- The pharma dataset may not be transaction-level.
- Dataset-specific criteria may constrain the exact agent design.
- SHAP fidelity depends on the underlying model.
- Incentive weights affect behavior.
- Reputation can create path dependence.
- Blockchain provides integrity/provenance, not truth.
- Local blockchain overhead may differ from production networks.

---

## 9. Optional Extensions (only after the core real-data experiment succeeds)

- TRACE-X-Bench as a pharma robustness/scale benchmark (label as benchmark/synthetic).
- P2P Electricity Markets dataset/code as extra energy validation.
- Local/open-source LLM agents; comparison of classical vs. LLM agents.

These must **not** delay the core experiment.

---

## 10. Session Protocol for Claude Code

At the **start** of each session:
1. Read this file and `docs/research_log.md`.
2. Identify the current phase and the next unfinished step.

At the **end** of each step:
1. Run `pytest`.
2. Append to `docs/research_log.md`: date, step completed, decisions made, deviations, open questions.
3. Commit with a message like `phase-3 step-08: implement five pharma agents`.

**Stop and ask the user when:**
- A needed variable is absent from a dataset.
- A dataset can't be downloaded.
- The Critical Checkpoint (Phase 6) is reached.
- Results contradict a hypothesis (report it; do not tune until it "works").
- A literature claim can't be verified.

---

## 11. Quick Command Reference

```bash
# Environment
pip install -r requirements.txt

# Tests
pytest -q

# Pharma
python run_experiment.py --config configs/pharma_baseline.yaml
python run_experiment.py --config configs/pharma_proposed.yaml
python run_experiment.py --config configs/pharma_adversarial.yaml

# Energy
python run_experiment.py --config configs/energy_proposed.yaml
```

---

## 12. Final Execution Checklist

- [ ] 01 Identify and download primary datasets
- [ ] 02 Dataset audit
- [ ] 03 Literature review
- [ ] 04 Research-gap validation
- [ ] 05 Research protocol
- [ ] 06 Pharma preprocessing
- [ ] 07 Pharma ground truth
- [ ] 08 Five pharma agents
- [ ] 09 Pharma baseline
- [ ] 10 Pharma game-theoretic interaction
- [ ] 11 Pharma SHAP/XAI
- [ ] 12 Fidelity / evidence / consistency metrics
- [ ] 13 Manipulation model
- [ ] 14 Incentive mechanism
- [ ] 15 Reward
- [ ] 16 Reputation
- [ ] 17 Pharma baseline vs. proposed
- [ ] 18 Incentive ablation  → **CHECKPOINT**
- [ ] 19 Malicious-agent experiments
- [ ] 20 Collusion
- [ ] 21 Statistical analysis
- [ ] 22 Blockchain implementation
- [ ] 23 Tampering experiment
- [ ] 24 Blockchain overhead
- [ ] 25 Energy preprocessing
- [ ] 26 Five energy agents
- [ ] 27 Energy baseline
- [ ] 28 Energy game/XAI
- [ ] 29 Energy incentive experiment
- [ ] 30 Energy adversarial experiment
- [ ] 31 Energy blockchain verification
- [ ] 32 Cross-domain analysis
- [ ] 33 Sensitivity analysis
- [ ] 34 Final statistics
- [ ] 35 Figures and tables
- [ ] 36 Reproducibility package
- [ ] 37 Paper evidence
- [ ] 38 Paper writing

---

## 13. Final Research Contribution (phrase only if supported)

If supported by the experiments, the paper can argue for an explanation-aware incentive mechanism in which explanation fidelity and evidence support become explicit components of agent utility, encouraging trustworthy behavior while blockchain provides tamper-evident provenance of decisions, explanations, rewards, and reputation. **The final contribution must be phrased according to what the literature and experiments actually demonstrate.**
