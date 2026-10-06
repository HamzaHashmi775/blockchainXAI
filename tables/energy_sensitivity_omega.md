# Sensitivity: game.omega

n = 10 seeds; mean ± SD. Exploratory (not pre-declared) values: ['0.9'].

## fidelity

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.972 ± 0.003 | 0.940 ± 0.025 | 0.972 ± 0.003 |
| 0.5 | 0.970 ± 0.003 | 0.936 ± 0.024 | 0.970 ± 0.004 |
| 0.75 | 0.943 ± 0.020 | 0.745 ± 0.095 | 0.951 ± 0.012 |
| 0.9 | 0.622 ± 0.064 | 0.547 ± 0.055 | 0.820 ± 0.056 |

## evidence_support

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.969 ± 0.003 | 0.934 ± 0.027 | 0.968 ± 0.003 |
| 0.5 | 0.967 ± 0.004 | 0.926 ± 0.031 | 0.966 ± 0.004 |
| 0.75 | 0.933 ± 0.025 | 0.731 ± 0.095 | 0.940 ± 0.014 |
| 0.9 | 0.592 ± 0.054 | 0.519 ± 0.030 | 0.816 ± 0.054 |

## manipulation

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.032 ± 0.002 | 0.054 ± 0.015 | 0.032 ± 0.002 |
| 0.5 | 0.035 ± 0.004 | 0.066 ± 0.017 | 0.036 ± 0.005 |
| 0.75 | 0.081 ± 0.037 | 0.247 ± 0.075 | 0.072 ± 0.016 |
| 0.9 | 0.420 ± 0.047 | 0.455 ± 0.031 | 0.252 ± 0.083 |

## collective_accuracy

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.750 ± 0.016 | 0.748 ± 0.015 | 0.756 ± 0.016 |
| 0.5 | 0.753 ± 0.016 | 0.744 ± 0.019 | 0.754 ± 0.013 |
| 0.75 | 0.739 ± 0.020 | 0.666 ± 0.069 | 0.751 ± 0.014 |
| 0.9 | 0.480 ± 0.076 | 0.477 ± 0.063 | 0.674 ± 0.070 |

## manipulation_success

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.020 ± 0.006 | 0.033 ± 0.009 | 0.018 ± 0.008 |
| 0.5 | 0.022 ± 0.008 | 0.050 ± 0.017 | 0.025 ± 0.012 |
| 0.75 | 0.065 ± 0.041 | 0.198 ± 0.088 | 0.047 ± 0.016 |
| 0.9 | 0.468 ± 0.083 | 0.477 ± 0.075 | 0.190 ± 0.110 |

## honest_share

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.898 ± 0.011 | 0.842 ± 0.035 | 0.900 ± 0.020 |
| 0.5 | 0.883 ± 0.037 | 0.775 ± 0.045 | 0.876 ± 0.032 |
| 0.75 | 0.725 ± 0.093 | 0.447 ± 0.087 | 0.735 ± 0.061 |
| 0.9 | 0.173 ± 0.060 | 0.158 ± 0.044 | 0.340 ± 0.171 |

## Proposed − baseline

| Value | Metric | Δ | 95% CI | Rel. | test | p | p (Holm) |
|---|---|---|---|---|---|---|---|
| 0.25 | fidelity | +0.031 | [+0.020, +0.047] | +3.3% | Wilcoxon signed-rank | 0.0020 | 0.0039 |
| 0.25 | evidence_support | +0.034 | [+0.015, +0.054] | +3.7% | paired t-test | 0.0031 | 0.0039 |
| 0.25 | manipulation | -0.022 | [-0.032, -0.012] | -41.2% | paired t-test | 0.0007 | 0.0021 |
| 0.5 | fidelity | +0.034 | [+0.021, +0.050] | +3.6% | Wilcoxon signed-rank | 0.0020 | 0.0039 |
| 0.5 | evidence_support | +0.040 | [+0.017, +0.063] | +4.3% | paired t-test | 0.0033 | 0.0039 |
| 0.5 | manipulation | -0.029 | [-0.043, -0.016] | -44.4% | paired t-test | 0.0009 | 0.0026 |
| 0.75 | fidelity | +0.207 | [+0.160, +0.269] | +27.8% | Wilcoxon signed-rank | 0.0020 | 0.0020 |
| 0.75 | evidence_support | +0.209 | [+0.145, +0.274] | +28.6% | paired t-test | 0.0000 | 0.0001 |
| 0.75 | manipulation | -0.175 | [-0.220, -0.130] | -71.0% | paired t-test | 0.0000 | 0.0000 |
| 0.9 | fidelity | +0.273 | [+0.214, +0.333] | +50.0% | paired t-test | 0.0000 | 0.0000 |
| 0.9 | evidence_support | +0.297 | [+0.254, +0.340] | +57.2% | paired t-test | 0.0000 | 0.0000 |
| 0.9 | manipulation | -0.202 | [-0.263, -0.142] | -44.5% | paired t-test | 0.0000 | 0.0000 |

## Unilateral deviation from all-honest: gain of the best deviation (positive = deviating pays)

| Value | System | Agent | honest payoff | best deviation | gain | honest best in seeds |
|---|---|---|---|---|---|---|
| 0.25 | ablation | consumer | 0.490 | strategic | -0.181 | 10/10 |
| 0.25 | ablation | grid | 0.544 | strategic | -0.190 | 10/10 |
| 0.25 | ablation | market | 0.527 | strategic | -0.189 | 10/10 |
| 0.25 | ablation | producer | 0.528 | strategic | -0.174 | 10/10 |
| 0.25 | ablation | storage | 0.622 | strategic | -0.088 | 10/10 |
| 0.25 | baseline | consumer | 0.490 | misattributing | -0.163 | 10/10 |
| 0.25 | baseline | grid | 0.544 | misattributing | -0.173 | 10/10 |
| 0.25 | baseline | market | 0.527 | manipulative | -0.157 | 10/10 |
| 0.25 | baseline | producer | 0.528 | manipulative | -0.150 | 10/10 |
| 0.25 | baseline | storage | 0.622 | manipulative | -0.079 | 10/10 |
| 0.25 | proposed | consumer | 0.489 | strategic | -0.183 | 10/10 |
| 0.25 | proposed | grid | 0.543 | strategic | -0.194 | 10/10 |
| 0.25 | proposed | market | 0.528 | strategic | -0.194 | 10/10 |
| 0.25 | proposed | producer | 0.529 | strategic | -0.181 | 10/10 |
| 0.25 | proposed | storage | 0.622 | strategic | -0.089 | 10/10 |
| 0.5 | ablation | consumer | 0.520 | strategic | -0.120 | 10/10 |
| 0.5 | ablation | grid | 0.578 | strategic | -0.124 | 10/10 |
| 0.5 | ablation | market | 0.540 | strategic | -0.121 | 10/10 |
| 0.5 | ablation | producer | 0.539 | strategic | -0.103 | 10/10 |
| 0.5 | ablation | storage | 0.669 | strategic | -0.053 | 10/10 |
| 0.5 | baseline | consumer | 0.520 | misattributing | -0.108 | 10/10 |
| 0.5 | baseline | grid | 0.578 | misattributing | -0.113 | 10/10 |
| 0.5 | baseline | market | 0.540 | manipulative | -0.098 | 10/10 |
| 0.5 | baseline | producer | 0.539 | manipulative | -0.086 | 10/10 |
| 0.5 | baseline | storage | 0.669 | manipulative | -0.042 | 10/10 |
| 0.5 | proposed | consumer | 0.518 | strategic | -0.124 | 10/10 |
| 0.5 | proposed | grid | 0.576 | strategic | -0.129 | 10/10 |
| 0.5 | proposed | market | 0.542 | strategic | -0.128 | 10/10 |
| 0.5 | proposed | producer | 0.541 | strategic | -0.113 | 10/10 |
| 0.5 | proposed | storage | 0.668 | strategic | -0.053 | 10/10 |
| 0.75 | ablation | consumer | 0.551 | strategic | -0.060 | 10/10 |
| 0.75 | ablation | grid | 0.612 | strategic | -0.058 | 10/10 |
| 0.75 | ablation | market | 0.553 | strategic | -0.052 | 10/10 |
| 0.75 | ablation | producer | 0.549 | strategic | -0.032 | 10/10 |
| 0.75 | ablation | storage | 0.716 | strategic | -0.018 | 10/10 |
| 0.75 | baseline | consumer | 0.551 | misattributing | -0.054 | 10/10 |
| 0.75 | baseline | grid | 0.612 | manipulative | -0.052 | 10/10 |
| 0.75 | baseline | market | 0.553 | manipulative | -0.039 | 10/10 |
| 0.75 | baseline | producer | 0.549 | manipulative | -0.022 | 10/10 |
| 0.75 | baseline | storage | 0.716 | manipulative | -0.006 | 9/10 |
| 0.75 | proposed | consumer | 0.547 | strategic | -0.065 | 10/10 |
| 0.75 | proposed | grid | 0.610 | strategic | -0.065 | 10/10 |
| 0.75 | proposed | market | 0.556 | strategic | -0.062 | 10/10 |
| 0.75 | proposed | producer | 0.552 | strategic | -0.044 | 10/10 |
| 0.75 | proposed | storage | 0.714 | strategic | -0.017 | 10/10 |
| 0.9 | ablation | consumer | 0.569 | strategic | -0.023 | 10/10 |
| 0.9 | ablation | grid | 0.633 | strategic | -0.018 | 10/10 |
| 0.9 | ablation | market | 0.560 | strategic | -0.011 | 10/10 |
| 0.9 | ablation | producer | 0.555 | strategic | +0.010 | 0/10 |
| 0.9 | ablation | storage | 0.744 | strategic | +0.004 | 2/10 |
| 0.9 | baseline | consumer | 0.569 | manipulative | -0.020 | 10/10 |
| 0.9 | baseline | grid | 0.633 | manipulative | -0.015 | 10/10 |
| 0.9 | baseline | market | 0.560 | manipulative | -0.003 | 9/10 |
| 0.9 | baseline | producer | 0.555 | manipulative | +0.016 | 0/10 |
| 0.9 | baseline | storage | 0.744 | manipulative | +0.016 | 0/10 |
| 0.9 | proposed | consumer | 0.564 | strategic | -0.030 | 10/10 |
| 0.9 | proposed | grid | 0.630 | strategic | -0.026 | 10/10 |
| 0.9 | proposed | market | 0.564 | strategic | -0.022 | 10/10 |
| 0.9 | proposed | producer | 0.559 | strategic | -0.003 | 8/10 |
| 0.9 | proposed | storage | 0.742 | strategic | +0.005 | 1/10 |

Agents (of 5) for whom honest is the best unilateral response:
- 0.25: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.5: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.75: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.9: {'ablation': 3, 'baseline': 3, 'proposed': 4}
