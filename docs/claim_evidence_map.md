# Claim → evidence map (CLAUDE.md step 37)

Every claim the paper may make, with the file that supports it and the exact numbers. A
claim not listed here must not appear in the paper; the last section lists claims the
evidence does **not** allow. Verdict rules: protocol §7, §9, §11.5. Classical agents
n = 10 seeds; LLM agents (qwen2.5:7b) n = 5 (3 for LLM adversarial runs). Domains are never
pooled. Decision accuracy always means agreement with a *constructed* reference decision.

## Data and set-up

| # | Claim | Evidence | Numbers |
|---|---|---|---|
| D1 | Both case studies use real data; pharma = USAID/PEPFAR SCMS delivery history, energy = OptiREC energy community (Mendeley) | `tables/table1_datasets.md`, `data/metadata/datasets.json` | 10,324 shipment lines; 8,760 hours; SHA-256 recorded |
| D2 | The figshare file named in the plan has no observations; SCMS was adopted with the user's approval | `docs/dataset_audit.md` §1.2, protocol amendment 2 | 24 criteria × 0 observations |
| D3 | Pharma scenarios are constructed: three candidate sites per order (the data hold no competing offers) | Table 1; protocol §11.1 | 1,648 scenarios; the site used is a candidate in 83 % |
| D4 | Reference decisions are constructed in both domains, not observed choices | Table 1; protocol §3, §11.2 | pharma reference matches the site used in 35 % (chance 33 %) |
| D5 | Energy battery parameters are simulated assumptions | Table 1; protocol §3 | C-rate 0.5, efficiency 0.9, SOC 10–90 % |
| D6 | Preprocessing is deterministic and split without leakage | Table 1; `tests/`; clean rerun (Step 36) | processed files byte-identical in a fresh clone |

## Classical agents: main experiment (Table 2, Figure 3)

| # | Claim | Evidence | Numbers |
|---|---|---|---|
| M1 | **H1 supported in pharma**: fidelity improved | `tables/table2_baseline_vs_proposed.md`, `figures/fig3_*` | 0.510 → 0.936, +83.5 %, Holm p < 0.0001, d_z 5.43 |
| M2 | **H2 supported in pharma**: evidence support improved | Table 2 | 0.522 → 0.917, +75.7 %, Holm p < 0.0001 |
| M3 | **H3 supported in both domains**: manipulation reduced | Table 2 | pharma 0.392 → 0.119 (−69.7 %); energy 0.066 → 0.036 (−44.4 %); Holm p < 0.0001 and 0.0026 |
| M4 | **H1/H2 negligible in energy**: significant but below the pre-declared 5 % threshold | Table 2 | F +3.6 % (Holm p 0.0039), E +4.3 % (0.0039) |
| M5 | The energy baseline leaves little headroom (context, not a change of verdict) | Table 2 | baseline F 0.936, E 0.926 |
| M6 | Decision accuracy did not change detectably | Table 2 (secondary, unadjusted) | pharma +0.029 (p 0.20); energy +0.009 (p 0.054) |
| M7 | Manipulation success fell in both domains (secondary) | Table 2 | pharma −33.9 % (p 0.0002); energy −49.4 % (p 0.0015), unadjusted |
| M9 | Energy baseline is already near-honest; in pharma the incentive removes the profit of false explanations without making all-honest an equilibrium | `tables/energy_main.md`, `tables/pharma_main.md` (unilateral deviation) | energy: honest best response for 5/5 agents in every system; pharma: 0/5 baseline, 2/5 proposed, the other three best off with *strategic* (truthful explanation) |
| M8 | Explanation consistency rose (secondary) | Table 2, `tables/table3_*` | pharma +28.6 %; energy +8.6 %, unadjusted |

## Ablation and reputation (Table 4, Figure 6)

| # | Claim | Evidence | Numbers |
|---|---|---|---|
| A1 | The incentive alone (no reputation) produces most of the effect | `tables/table4_ablation.md`, `figures/fig6_*` | ablation vs baseline: pharma F +74.9 %, E +70.9 %, M −61.0 %, all improved; energy M −46.2 % improved |
| A2 | Reputation adds a small increment in pharma and none in energy (descriptive; not a pre-declared test) | Table 4, last block | pharma F +0.044, M −0.034; energy ≤ 0.004 on every metric |

## Robustness (Table 5, Figures 4–5)

| # | Claim | Evidence | Numbers |
|---|---|---|---|
| R1 | **H4 not supported**: the proposed system does not degrade less as malicious agents rise from 10 to 40 % | `tables/table5_malicious_agents.md`, `figures/fig5_*`, `tables/final_statistics.md` | pharma Δ +0.039 [−0.009, +0.087], p 0.10; energy Δ −0.020 [−0.043, +0.002], p 0.068 |
| R2 | Under attack, the proposed system keeps higher fidelity and evidence support than the baseline at every share (descriptive) | Table 5, `figures/fig4_*` | pharma at 40 %: F 0.556 vs 0.304 |
| R3 | Under collusion, the proposed reward takes the colluders' reward away and raises the honest agents' payoff (unadjusted) | Table 5 | colluders' reward −0.458 (pharma), −0.501 (energy); honest payoff +0.181, +0.216 |
| R4 | Collusion still raises manipulation success under the proposed system, but less than under the baseline | Table 5 | pharma +0.126 vs +0.380; energy +0.047 vs +0.155 |
| R5 | Collusion lowers pharma accuracy under the proposed system | Table 5 | −0.036, p 0.008 (unadjusted) |

## Provenance (Table 6, Figure 7)

| # | Claim | Evidence | Numbers |
|---|---|---|---|
| P1 | **H5 supported**: every tampered record was detected, with no false positives | `tables/table6_blockchain.md`, `figures/fig7_*` | 1,000/1,000 detected over 5 targets; 0 of 29,800 unchanged records flagged |
| P2 | Changes below the 10⁻⁶ storage resolution are not detected (by design) | Table 6 | 0 of 200 |
| P3 | Contract rules hold: no overwrite, no foreign write | Table 6 | 0 of 100 each |
| P4 | Overhead on a local node | Table 6 | ≈ 96k gas per record in batches of 100; 128 bytes on-chain per record |

## Cross-domain and sensitivity (Table 7, Figure 8)

| # | Claim | Evidence | Numbers |
|---|---|---|---|
| X1 | **H6 partly supported**: classical agents give the same verdict in both domains for manipulation only | `tables/table7_cross_domain.md`, `figures/fig8_*` | 1 of 3 |
| X2 | LLM agents give the same verdict in both domains for all three outcomes | Table 7 | 3 of 3 (F, E negligible; M improved) |
| S1 | Pharma verdicts are unchanged across β, ρ and ω | `tables/sensitivity_robustness.md` | β ∈ {0, 0.1, 0.25, 0.4}, ρ ∈ {0.5, 0.8, 0.95}, ω ∈ {0.25, 0.5, 0.75} |
| S2 | Energy verdicts are unchanged across β and ρ; for F and E they change across ω | `tables/sensitivity_robustness.md` | ω 0.75: F +27.8 %, E +28.6 % (improved) |
| S3 | The pharma fidelity gain does not depend on the fidelity weight β | `tables/pharma_sensitivity_beta.md` | +74.7 % at β = 0 |

## LLM agents (optional extension)

| # | Claim | Evidence | Numbers |
|---|---|---|---|
| L1 | With LLM agents, manipulation fell in both domains; fidelity and evidence did not change | `tables/pharma_llm.md`, `tables/energy_llm.md`, Table 7 | M −22.0 % and −12.6 % (Holm p < 0.0001); F, E negligible |
| L2 | The LLMs' lower stated confidence comes from the wording of the reward rules, not from the payoff applied (post hoc 2×2) | `tables/pharma_llm_factorial.md`, `tables/energy_llm_factorial.md` | wording −0.299 / −0.164 (Holm p < 0.0001); payoff not detected in either domain |
| L3 | The energy 2×2 replicates the pharma pattern under the rule frozen beforehand (amendment 8) | `tables/energy_llm_factorial.md` | replication rule met; interaction +0.006 detected in energy only |
| L4 | LLM fidelity is low in every system; sample replies show misread signs and levels | Table 3; `docs/research_log.md` (amendment 4 notes) | 0.446–0.461 |
| L5 | The LLM manipulation drop comes mostly from lower stated confidence | `results/summaries/{pharma,energy}_llm.json` (component comparisons) | confidence-inflation component −0.298/5 = −0.060 of ΔM −0.065 (pharma); −0.144/5 = −0.029 of −0.035 (energy) |

## Reproducibility

| # | Claim | Evidence |
|---|---|---|
| Q1 | All summaries, tables and figures are rebuilt from raw results by one command | `reproduce.py`; rebuild byte-identical (research log 2026-10-31) |
| Q2 | Classical experiments are deterministic | clean rerun in a fresh clone (research log, Step 36) |

## Claims the evidence does NOT allow

- **Any Nash-equilibrium claim.** Only unilateral deviations were computed; in pharma, honest
  play is the best response for 2 of 5 agents under the proposed system and 0 of 5 under the
  baseline (`tables/pharma_main.md`).
- **"Blockchain proves the explanations are true."** It shows that records were not changed
  after writing (integrity), nothing about truth.
- **"The mechanism improves explanation quality" without naming the domain.** It did so in
  pharma only (classical agents).
- **"The mechanism makes the system robust to malicious agents."** H4 was not supported;
  "not supported" means no difference was detected, not that none exists.
- **"Decision accuracy improved" or accuracy against real choices.** Accuracy is agreement
  with a constructed reference, and no improvement was detected.
- **"LLM agents became more honest because of the incentive payoff."** The confidence change
  is explained by the prompt wording (L2); LLM manipulation scores are not intent to deceive.
- **Generalisation to pharmaceutical supply chains in general, to other LLMs or to production
  blockchains.** One USAID programme's ARV and HIV-test deliveries, one 7B model, one local
  node.
- **Combining the LLM 2×2 results with the confirmatory family.** They were added post hoc
  (amendments 6–8) and are reported separately.
