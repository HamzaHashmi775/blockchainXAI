# Sensitivity: incentive_weights.beta

n = 10 seeds; mean ± SD. Exploratory (not pre-declared) values: none.

## fidelity

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.837 ± 0.049 | 0.510 ± 0.077 | 0.891 ± 0.017 |
| 0.1 | 0.879 ± 0.043 | 0.510 ± 0.077 | 0.905 ± 0.037 |
| 0.25 | 0.892 ± 0.033 | 0.510 ± 0.077 | 0.936 ± 0.020 |
| 0.4 | 0.934 ± 0.030 | 0.510 ± 0.077 | 0.949 ± 0.006 |

## evidence_support

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.876 ± 0.034 | 0.522 ± 0.070 | 0.916 ± 0.023 |
| 0.1 | 0.882 ± 0.053 | 0.522 ± 0.070 | 0.920 ± 0.034 |
| 0.25 | 0.892 ± 0.033 | 0.522 ± 0.070 | 0.917 ± 0.023 |
| 0.4 | 0.896 ± 0.025 | 0.522 ± 0.070 | 0.910 ± 0.032 |

## manipulation

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.177 ± 0.036 | 0.392 ± 0.038 | 0.136 ± 0.024 |
| 0.1 | 0.159 ± 0.041 | 0.392 ± 0.038 | 0.139 ± 0.027 |
| 0.25 | 0.153 ± 0.023 | 0.392 ± 0.038 | 0.119 ± 0.015 |
| 0.4 | 0.127 ± 0.028 | 0.392 ± 0.038 | 0.128 ± 0.022 |

## collective_accuracy

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.578 ± 0.044 | 0.578 ± 0.045 | 0.615 ± 0.028 |
| 0.1 | 0.561 ± 0.046 | 0.578 ± 0.045 | 0.608 ± 0.035 |
| 0.25 | 0.564 ± 0.052 | 0.578 ± 0.045 | 0.606 ± 0.033 |
| 0.4 | 0.579 ± 0.049 | 0.578 ± 0.045 | 0.596 ± 0.040 |

## manipulation_success

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.346 ± 0.055 | 0.398 ± 0.057 | 0.269 ± 0.057 |
| 0.1 | 0.360 ± 0.068 | 0.398 ± 0.057 | 0.296 ± 0.025 |
| 0.25 | 0.352 ± 0.065 | 0.398 ± 0.057 | 0.263 ± 0.032 |
| 0.4 | 0.317 ± 0.079 | 0.398 ± 0.057 | 0.288 ± 0.068 |

## honest_share

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.300 ± 0.083 | 0.095 ± 0.051 | 0.401 ± 0.071 |
| 0.1 | 0.340 ± 0.141 | 0.095 ± 0.051 | 0.369 ± 0.117 |
| 0.25 | 0.353 ± 0.082 | 0.095 ± 0.051 | 0.414 ± 0.072 |
| 0.4 | 0.422 ± 0.109 | 0.095 ± 0.051 | 0.365 ± 0.100 |

## Proposed − baseline

| Value | Metric | Δ | 95% CI | Rel. | test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.0 | fidelity | +0.381 | [+0.323, +0.427] | +74.7% | Wilcoxon signed-rank | 0.0020 | 0.0020 | improved |
| 0.0 | evidence_support | +0.394 | [+0.347, +0.441] | +75.5% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.0 | manipulation | -0.256 | [-0.288, -0.224] | -65.4% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.1 | fidelity | +0.395 | [+0.328, +0.461] | +77.3% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.1 | evidence_support | +0.398 | [+0.344, +0.451] | +76.2% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.1 | manipulation | -0.253 | [-0.286, -0.220] | -64.6% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.25 | fidelity | +0.426 | [+0.370, +0.482] | +83.5% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.25 | evidence_support | +0.395 | [+0.345, +0.444] | +75.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.25 | manipulation | -0.273 | [-0.302, -0.243] | -69.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.4 | fidelity | +0.439 | [+0.385, +0.493] | +86.0% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.4 | evidence_support | +0.389 | [+0.343, +0.434] | +74.5% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.4 | manipulation | -0.264 | [-0.282, -0.242] | -67.3% | Wilcoxon signed-rank | 0.0020 | 0.0020 | improved |

## Unilateral deviation from all-honest: gain of the best deviation (positive = deviating pays)

| Value | System | Agent | honest payoff | best deviation | gain | honest best in seeds |
|---|---|---|---|---|---|---|
| 0.0 | ablation | continuity | 0.615 | strategic | -0.062 | 10/10 |
| 0.0 | ablation | cost | 0.465 | strategic | +0.035 | 0/10 |
| 0.0 | ablation | lead_time | 0.593 | strategic | -0.022 | 10/10 |
| 0.0 | ablation | logistics | 0.581 | strategic | +0.069 | 0/10 |
| 0.0 | ablation | reliability | 0.454 | strategic | +0.046 | 0/10 |
| 0.0 | baseline | continuity | 0.615 | manipulative | +0.016 | 0/10 |
| 0.0 | baseline | cost | 0.465 | manipulative | +0.058 | 0/10 |
| 0.0 | baseline | lead_time | 0.593 | manipulative | +0.025 | 0/10 |
| 0.0 | baseline | logistics | 0.581 | manipulative | +0.104 | 0/10 |
| 0.0 | baseline | reliability | 0.454 | manipulative | +0.150 | 0/10 |
| 0.0 | proposed | continuity | 0.589 | strategic | -0.061 | 10/10 |
| 0.0 | proposed | cost | 0.485 | strategic | +0.044 | 0/10 |
| 0.0 | proposed | lead_time | 0.575 | strategic | -0.026 | 10/10 |
| 0.0 | proposed | logistics | 0.591 | strategic | +0.065 | 0/10 |
| 0.0 | proposed | reliability | 0.471 | strategic | +0.019 | 0/10 |
| 0.1 | ablation | continuity | 0.615 | strategic | -0.062 | 10/10 |
| 0.1 | ablation | cost | 0.465 | strategic | +0.035 | 0/10 |
| 0.1 | ablation | lead_time | 0.593 | strategic | -0.022 | 10/10 |
| 0.1 | ablation | logistics | 0.581 | strategic | +0.069 | 0/10 |
| 0.1 | ablation | reliability | 0.454 | strategic | +0.046 | 0/10 |
| 0.1 | baseline | continuity | 0.615 | manipulative | +0.016 | 0/10 |
| 0.1 | baseline | cost | 0.465 | manipulative | +0.058 | 0/10 |
| 0.1 | baseline | lead_time | 0.593 | manipulative | +0.025 | 0/10 |
| 0.1 | baseline | logistics | 0.581 | manipulative | +0.104 | 0/10 |
| 0.1 | baseline | reliability | 0.454 | manipulative | +0.150 | 0/10 |
| 0.1 | proposed | continuity | 0.589 | strategic | -0.061 | 10/10 |
| 0.1 | proposed | cost | 0.485 | strategic | +0.044 | 0/10 |
| 0.1 | proposed | lead_time | 0.575 | strategic | -0.026 | 10/10 |
| 0.1 | proposed | logistics | 0.591 | strategic | +0.065 | 0/10 |
| 0.1 | proposed | reliability | 0.471 | strategic | +0.019 | 0/10 |
| 0.25 | ablation | continuity | 0.615 | strategic | -0.062 | 10/10 |
| 0.25 | ablation | cost | 0.465 | strategic | +0.035 | 0/10 |
| 0.25 | ablation | lead_time | 0.593 | strategic | -0.022 | 10/10 |
| 0.25 | ablation | logistics | 0.581 | strategic | +0.069 | 0/10 |
| 0.25 | ablation | reliability | 0.454 | strategic | +0.046 | 0/10 |
| 0.25 | baseline | continuity | 0.615 | manipulative | +0.016 | 0/10 |
| 0.25 | baseline | cost | 0.465 | manipulative | +0.058 | 0/10 |
| 0.25 | baseline | lead_time | 0.593 | manipulative | +0.025 | 0/10 |
| 0.25 | baseline | logistics | 0.581 | manipulative | +0.104 | 0/10 |
| 0.25 | baseline | reliability | 0.454 | manipulative | +0.150 | 0/10 |
| 0.25 | proposed | continuity | 0.589 | strategic | -0.061 | 10/10 |
| 0.25 | proposed | cost | 0.485 | strategic | +0.044 | 0/10 |
| 0.25 | proposed | lead_time | 0.575 | strategic | -0.026 | 10/10 |
| 0.25 | proposed | logistics | 0.591 | strategic | +0.065 | 0/10 |
| 0.25 | proposed | reliability | 0.471 | strategic | +0.019 | 0/10 |
| 0.4 | ablation | continuity | 0.615 | strategic | -0.062 | 10/10 |
| 0.4 | ablation | cost | 0.465 | strategic | +0.035 | 0/10 |
| 0.4 | ablation | lead_time | 0.593 | strategic | -0.022 | 10/10 |
| 0.4 | ablation | logistics | 0.581 | strategic | +0.069 | 0/10 |
| 0.4 | ablation | reliability | 0.454 | strategic | +0.046 | 0/10 |
| 0.4 | baseline | continuity | 0.615 | manipulative | +0.016 | 0/10 |
| 0.4 | baseline | cost | 0.465 | manipulative | +0.058 | 0/10 |
| 0.4 | baseline | lead_time | 0.593 | manipulative | +0.025 | 0/10 |
| 0.4 | baseline | logistics | 0.581 | manipulative | +0.104 | 0/10 |
| 0.4 | baseline | reliability | 0.454 | manipulative | +0.150 | 0/10 |
| 0.4 | proposed | continuity | 0.589 | strategic | -0.061 | 10/10 |
| 0.4 | proposed | cost | 0.485 | strategic | +0.044 | 0/10 |
| 0.4 | proposed | lead_time | 0.575 | strategic | -0.026 | 10/10 |
| 0.4 | proposed | logistics | 0.591 | strategic | +0.065 | 0/10 |
| 0.4 | proposed | reliability | 0.471 | strategic | +0.019 | 0/10 |

Agents (of 5) for whom honest is the best unilateral response:
- 0.0: {'ablation': 2, 'baseline': 0, 'proposed': 2}
- 0.1: {'ablation': 2, 'baseline': 0, 'proposed': 2}
- 0.25: {'ablation': 2, 'baseline': 0, 'proposed': 2}
- 0.4: {'ablation': 2, 'baseline': 0, 'proposed': 2}
