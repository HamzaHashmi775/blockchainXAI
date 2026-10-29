# Final statistics: all hypotheses

Assembled from `results/summaries/`; no test is run here. Verdict rules are the pre-declared ones (protocol §7, §9, §11.5). Domains are never pooled.

## H1–H3, proposed vs baseline

| Agents | Domain | n | H1 fidelity | H2 evidence | H3 manipulation |
|---|---|---|---|---|---|
| classical | pharma | 10 | improved (+83.5%, Holm p < 0.0001) | improved (+75.7%, Holm p < 0.0001) | improved (-69.7%, Holm p < 0.0001) |
| classical | energy | 10 | negligible (+3.6%, Holm p 0.0039) | negligible (+4.3%, Holm p 0.0039) | improved (-44.4%, Holm p 0.0026) |
| llm | pharma | 5 | negligible (-1.9%, Holm p 0.1250) | negligible (-1.0%, Holm p 0.1250) | improved (-22.0%, Holm p < 0.0001) |
| llm | energy | 5 | negligible (+3.4%, Holm p 0.0730) | negligible (-0.3%, Holm p 0.8122) | improved (-12.6%, Holm p < 0.0001) |

## H4, robustness to 10–40 % malicious agents

Primary: mean accuracy degradation over shares 0.1–0.4, proposed − baseline (negative = proposed degrades less).

| Agents | Domain | n | Δ [95% CI] | test | p | Verdict |
|---|---|---|---|---|---|---|
| classical | pharma | 10 | +0.0390 [-0.0095, +0.0875] | paired t-test | 0.1021 | not supported |
| classical | energy | 10 | -0.0203 [-0.0426, +0.0019] | paired t-test | 0.0684 | not supported |
| llm | pharma | 3 | +0.0100 [-0.1639, +0.1839] | paired t-test | 0.8277 | no confirmatory claim (3 seeds) |
| llm | energy | 3 | -0.0133 [-0.0635, +0.0369] | paired t-test | 0.3715 | no confirmatory claim (3 seeds) |

## H5, tamper detection (descriptive)

Detection rate 1.000 over all targets (decision 1.000, explanation 1.000, evidence 1.000, reward 1.000, reputation 1.000); false-positive rate 0.000 over 29,800 unchanged records; changes below the 10⁻⁶ resolution detected: 0 (invisible by design). 30,000 records on a local chain. Integrity, not truth.

## H6, same verdict in both domains (proposed vs baseline)

- classical: 1 of 3 (manipulation)
- llm: 3 of 3 (fidelity, evidence_support, manipulation)

## Sensitivity: are the H1–H3 verdicts unchanged at every pre-declared value?

| Run | fidelity | evidence | manipulation |
|---|---|---|---|
| energy_sensitivity_beta | yes | yes | yes |
| energy_sensitivity_omega | **no** | **no** | yes |
| energy_sensitivity_rho | yes | yes | yes |
| pharma_sensitivity_beta | yes | yes | yes |
| pharma_sensitivity_omega | yes | yes | yes |
| pharma_sensitivity_rho | yes | yes | yes |

## Limits of inference

- n = 10 seeds (classical) and 5 (LLM; 3 for LLM adversarial runs); the tests measure variation across seeds on one dataset per domain, not generalisation to other datasets.
- Decision accuracy is agreement with a constructed reference decision.
- H4 'not supported' means no difference was detected, not that there is none.
- LLM 2×2 wording × payoff results (amendments 7–8) are post hoc and reported separately (`tables/*_llm_factorial.md`).
