# Pharma — baseline vs ablation vs proposed

n = 10 paired seeds; mean ± SD over seeds; metrics averaged over agents and the evaluation window.

| Metric | Baseline | Ablation | Proposed |
|---|---|---|---|
| fidelity | 0.510 ± 0.077 | 0.892 ± 0.033 | 0.936 ± 0.020 |
| evidence_support | 0.522 ± 0.070 | 0.892 ± 0.033 | 0.917 ± 0.023 |
| manipulation | 0.392 ± 0.038 | 0.153 ± 0.023 | 0.119 ± 0.015 |
| collective_accuracy | 0.578 ± 0.045 | 0.564 ± 0.052 | 0.606 ± 0.033 |
| collective_utility | 0.602 ± 0.006 | 0.598 ± 0.007 | 0.599 ± 0.004 |
| decision_quality | 0.484 ± 0.007 | 0.485 ± 0.013 | 0.495 ± 0.016 |
| manipulation_success | 0.398 ± 0.057 | 0.352 ± 0.065 | 0.263 ± 0.032 |
| consistency | 0.617 ± 0.022 | 0.771 ± 0.014 | 0.793 ± 0.019 |

## proposed vs baseline

| Metric | Δ mean | 95% CI | Rel. impr. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.426 | [+0.370, +0.482] | +83.5% | paired t-test | 0.0000 | 0.0000 | cohen_dz = 5.43 | improved |
| evidence_support | +0.395 | [+0.345, +0.444] | +75.7% | paired t-test | 0.0000 | 0.0000 | cohen_dz = 5.71 | improved |
| manipulation | -0.273 | [-0.302, -0.243] | -69.7% | paired t-test | 0.0000 | 0.0000 | cohen_dz = -6.61 | improved |
| collective_accuracy | +0.029 | [-0.018, +0.076] | +5.0% | paired t-test | 0.2021 | nan | cohen_dz = 0.44 | — |
| collective_utility | -0.003 | [-0.009, +0.003] | -0.5% | paired t-test | 0.2905 | nan | cohen_dz = -0.36 | — |
| decision_quality | +0.011 | [-0.002, +0.023] | +2.2% | paired t-test | 0.0877 | nan | cohen_dz = 0.61 | — |
| manipulation_success | -0.135 | [-0.185, -0.085] | -33.9% | paired t-test | 0.0002 | nan | cohen_dz = -1.95 | — |
| consistency | +0.177 | [+0.156, +0.197] | +28.6% | paired t-test | 0.0000 | nan | cohen_dz = 6.14 | — |

## ablation vs baseline

| Metric | Δ mean | 95% CI | Rel. impr. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.382 | [+0.331, +0.433] | +74.9% | paired t-test | 0.0000 | 0.0000 | cohen_dz = 5.33 | improved |
| evidence_support | +0.370 | [+0.313, +0.427] | +70.9% | paired t-test | 0.0000 | 0.0000 | cohen_dz = 4.63 | improved |
| manipulation | -0.239 | [-0.266, -0.211] | -61.0% | paired t-test | 0.0000 | 0.0000 | cohen_dz = -6.24 | improved |
| collective_accuracy | -0.014 | [-0.047, +0.020] | -2.4% | paired t-test | 0.3823 | nan | cohen_dz = -0.29 | — |
| collective_utility | -0.004 | [-0.008, +0.000] | -0.6% | paired t-test | 0.0689 | nan | cohen_dz = -0.65 | — |
| decision_quality | +0.001 | [-0.008, +0.011] | +0.3% | paired t-test | 0.7499 | nan | cohen_dz = 0.10 | — |
| manipulation_success | -0.045 | [-0.086, -0.005] | -11.4% | paired t-test | 0.0328 | nan | cohen_dz = -0.80 | — |
| consistency | +0.154 | [+0.138, +0.171] | +25.1% | paired t-test | 0.0000 | nan | cohen_dz = 6.81 | — |

## Learned strategy shares (evaluation window)

| System | honest | strategic | misattributing | overclaiming | manipulative |
|---|---|---|---|---|---|
| baseline | 0.095 ± 0.051 | 0.137 ± 0.054 | 0.223 ± 0.070 | 0.135 ± 0.060 | 0.411 ± 0.077 |
| ablation | 0.353 ± 0.082 | 0.355 ± 0.105 | 0.136 ± 0.089 | 0.096 ± 0.048 | 0.060 ± 0.038 |
| proposed | 0.414 ± 0.072 | 0.351 ± 0.102 | 0.098 ± 0.057 | 0.107 ± 0.051 | 0.030 ± 0.007 |

## Unilateral deviation from all-honest (mean payoff over seeds)

| System | Agent | honest | strategic | misattributing | overclaiming | manipulative | best | honest best in seeds |
|---|---|---|---|---|---|---|---|---|
| baseline | continuity | 0.615 | 0.622 | 0.622 | 0.622 | 0.631 | manipulative | 0/10 |
| baseline | cost | 0.465 | 0.519 | 0.519 | 0.519 | 0.523 | manipulative | 0/10 |
| baseline | lead_time | 0.593 | 0.577 | 0.577 | 0.577 | 0.619 | manipulative | 0/10 |
| baseline | logistics | 0.581 | 0.665 | 0.665 | 0.665 | 0.685 | manipulative | 0/10 |
| baseline | reliability | 0.454 | 0.530 | 0.530 | 0.530 | 0.604 | manipulative | 0/10 |
| ablation | continuity | 0.615 | 0.553 | 0.502 | 0.496 | 0.423 | honest | 10/10 |
| ablation | cost | 0.465 | 0.500 | 0.393 | 0.399 | 0.304 | strategic | 0/10 |
| ablation | lead_time | 0.593 | 0.572 | 0.470 | 0.475 | 0.416 | honest | 10/10 |
| ablation | logistics | 0.581 | 0.650 | 0.536 | 0.544 | 0.426 | strategic | 0/10 |
| ablation | reliability | 0.454 | 0.500 | 0.417 | 0.419 | 0.399 | strategic | 0/10 |
| proposed | continuity | 0.589 | 0.528 | 0.472 | 0.466 | 0.377 | honest | 10/10 |
| proposed | cost | 0.485 | 0.529 | 0.385 | 0.391 | 0.203 | strategic | 0/10 |
| proposed | lead_time | 0.575 | 0.549 | 0.426 | 0.433 | 0.319 | honest | 10/10 |
| proposed | logistics | 0.591 | 0.656 | 0.514 | 0.524 | 0.342 | strategic | 0/10 |
| proposed | reliability | 0.471 | 0.490 | 0.380 | 0.382 | 0.261 | strategic | 0/10 |

Checkpoint verdicts (proposed vs baseline): {'fidelity': 'improved', 'evidence_support': 'improved', 'manipulation': 'improved'}; continue = True
