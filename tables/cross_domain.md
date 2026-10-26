# Cross-domain comparison (H6)

Relative improvement = (treatment − baseline)/|baseline|, per domain, from the saved summaries; for manipulation a negative value is the improvement. Verdicts use the section 9 decision rule within each domain (Holm over F, E, M; |rel| ≥ 5 %). Domains are not pooled. H6 holds for an outcome when both domains give the same verdict.

## classical agents — proposed vs baseline (n = 10 pharma / 10 energy seeds)

| Outcome | Pharma rel. | Pharma Δ [95% CI] | Pharma verdict | Energy rel. | Energy Δ [95% CI] | Energy verdict | Same verdict |
|---|---|---|---|---|---|---|---|
| fidelity | +83.5% | +0.426 [+0.370, +0.482] | improved | +3.6% | +0.034 [+0.021, +0.050] | negligible | no |
| evidence_support | +75.7% | +0.395 [+0.345, +0.444] | improved | +4.3% | +0.040 [+0.017, +0.063] | negligible | no |
| manipulation | -69.7% | -0.273 [-0.302, -0.243] | improved | -44.4% | -0.029 [-0.043, -0.016] | improved | yes |
| collective_accuracy | +5.0% | +0.029 [-0.018, +0.076] | — (secondary) | +1.2% | +0.009 [-0.000, +0.019] | — (secondary) | — |
| manipulation_success | -33.9% | -0.135 [-0.185, -0.085] | — (secondary) | -49.4% | -0.025 [-0.037, -0.012] | — (secondary) | — |

H6 holds for: manipulation (1 of 3).

## classical agents — ablation vs baseline (n = 10 pharma / 10 energy seeds)

| Outcome | Pharma rel. | Pharma Δ [95% CI] | Pharma verdict | Energy rel. | Energy Δ [95% CI] | Energy verdict | Same verdict |
|---|---|---|---|---|---|---|---|
| fidelity | +74.9% | +0.382 [+0.331, +0.433] | improved | +3.5% | +0.033 [+0.016, +0.050] | negligible | no |
| evidence_support | +70.9% | +0.370 [+0.313, +0.427] | improved | +4.4% | +0.041 [+0.017, +0.064] | negligible | no |
| manipulation | -61.0% | -0.239 [-0.266, -0.211] | improved | -46.2% | -0.030 [-0.043, -0.018] | improved | yes |
| collective_accuracy | -2.4% | -0.014 [-0.047, +0.020] | — (secondary) | +1.2% | +0.009 [-0.003, +0.020] | — (secondary) | — |
| manipulation_success | -11.4% | -0.045 [-0.086, -0.005] | — (secondary) | -57.0% | -0.029 [-0.043, -0.014] | — (secondary) | — |

H6 holds for: manipulation (1 of 3).

## llm agents — proposed vs baseline (n = 5 pharma / 5 energy seeds)

| Outcome | Pharma rel. | Pharma Δ [95% CI] | Pharma verdict | Energy rel. | Energy Δ [95% CI] | Energy verdict | Same verdict |
|---|---|---|---|---|---|---|---|
| fidelity | -1.9% | -0.009 [-0.020, +0.003] | negligible | +3.4% | +0.015 [+0.002, +0.029] | negligible | yes |
| evidence_support | -1.0% | -0.006 [-0.010, -0.002] | negligible | -0.3% | -0.002 [-0.019, +0.016] | negligible | yes |
| manipulation | -22.0% | -0.065 [-0.070, -0.059] | improved | -12.6% | -0.035 [-0.038, -0.031] | improved | yes |
| collective_accuracy | +3.3% | +0.019 [+0.009, +0.025] | — (secondary) | -0.9% | -0.007 [-0.017, +0.003] | — (secondary) | — |
| manipulation_success | -6.5% | -0.011 [-0.030, +0.008] | — (secondary) | +4.9% | +0.002 [-0.002, +0.005] | — (secondary) | — |

H6 holds for: fidelity, evidence_support, manipulation (3 of 3).

## llm agents — ablation vs baseline (n = 5 pharma / 5 energy seeds)

| Outcome | Pharma rel. | Pharma Δ [95% CI] | Pharma verdict | Energy rel. | Energy Δ [95% CI] | Energy verdict | Same verdict |
|---|---|---|---|---|---|---|---|
| fidelity | +0.6% | +0.003 [-0.008, +0.014] | negligible | +1.4% | +0.006 [-0.009, +0.021] | negligible | yes |
| evidence_support | -3.5% | -0.021 [-0.034, -0.007] | worse | -1.7% | -0.009 [-0.025, +0.008] | negligible | no |
| manipulation | -21.5% | -0.063 [-0.068, -0.058] | improved | -12.7% | -0.035 [-0.041, -0.030] | improved | yes |
| collective_accuracy | +2.4% | +0.014 [-0.003, +0.031] | — (secondary) | -0.4% | -0.003 [-0.022, +0.016] | — (secondary) | — |
| manipulation_success | -2.4% | -0.004 [-0.044, +0.036] | — (secondary) | -17.1% | -0.007 [-0.016, +0.002] | — (secondary) | — |

H6 holds for: fidelity, manipulation (2 of 3).

