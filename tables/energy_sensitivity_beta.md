# Sensitivity: incentive_weights.beta

n = 10 seeds; mean ± SD. Exploratory (not pre-declared) values: none.

## fidelity

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.969 ± 0.004 | 0.936 ± 0.024 | 0.968 ± 0.005 |
| 0.1 | 0.971 ± 0.003 | 0.936 ± 0.024 | 0.971 ± 0.003 |
| 0.25 | 0.970 ± 0.003 | 0.936 ± 0.024 | 0.970 ± 0.004 |
| 0.4 | 0.971 ± 0.003 | 0.936 ± 0.024 | 0.971 ± 0.003 |

## evidence_support

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.966 ± 0.005 | 0.926 ± 0.031 | 0.967 ± 0.003 |
| 0.1 | 0.967 ± 0.004 | 0.926 ± 0.031 | 0.966 ± 0.006 |
| 0.25 | 0.967 ± 0.004 | 0.926 ± 0.031 | 0.966 ± 0.004 |
| 0.4 | 0.964 ± 0.007 | 0.926 ± 0.031 | 0.966 ± 0.005 |

## manipulation

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.037 ± 0.005 | 0.066 ± 0.017 | 0.037 ± 0.004 |
| 0.1 | 0.036 ± 0.005 | 0.066 ± 0.017 | 0.035 ± 0.005 |
| 0.25 | 0.035 ± 0.004 | 0.066 ± 0.017 | 0.036 ± 0.005 |
| 0.4 | 0.037 ± 0.006 | 0.066 ± 0.017 | 0.036 ± 0.004 |

## collective_accuracy

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.752 ± 0.019 | 0.744 ± 0.019 | 0.753 ± 0.015 |
| 0.1 | 0.748 ± 0.015 | 0.744 ± 0.019 | 0.753 ± 0.015 |
| 0.25 | 0.753 ± 0.016 | 0.744 ± 0.019 | 0.754 ± 0.013 |
| 0.4 | 0.750 ± 0.012 | 0.744 ± 0.019 | 0.755 ± 0.014 |

## manipulation_success

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.027 ± 0.017 | 0.050 ± 0.017 | 0.025 ± 0.012 |
| 0.1 | 0.029 ± 0.014 | 0.050 ± 0.017 | 0.025 ± 0.011 |
| 0.25 | 0.022 ± 0.008 | 0.050 ± 0.017 | 0.025 ± 0.012 |
| 0.4 | 0.027 ± 0.015 | 0.050 ± 0.017 | 0.023 ± 0.010 |

## honest_share

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.0 | 0.862 ± 0.041 | 0.775 ± 0.045 | 0.868 ± 0.038 |
| 0.1 | 0.870 ± 0.040 | 0.775 ± 0.045 | 0.878 ± 0.031 |
| 0.25 | 0.883 ± 0.037 | 0.775 ± 0.045 | 0.876 ± 0.032 |
| 0.4 | 0.869 ± 0.049 | 0.775 ± 0.045 | 0.875 ± 0.027 |

## Proposed − baseline

| Value | Metric | Δ | 95% CI | Rel. | test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.0 | fidelity | +0.031 | [+0.018, +0.047] | +3.4% | Wilcoxon signed-rank | 0.0020 | 0.0039 | negligible |
| 0.0 | evidence_support | +0.041 | [+0.025, +0.062] | +4.4% | Wilcoxon signed-rank | 0.0020 | 0.0039 | negligible |
| 0.0 | manipulation | -0.028 | [-0.039, -0.017] | -43.0% | paired t-test | 0.0003 | 0.0008 | improved |
| 0.1 | fidelity | +0.035 | [+0.017, +0.052] | +3.7% | paired t-test | 0.0017 | 0.0033 | negligible |
| 0.1 | evidence_support | +0.040 | [+0.018, +0.063] | +4.4% | paired t-test | 0.0031 | 0.0033 | negligible |
| 0.1 | manipulation | -0.030 | [-0.043, -0.018] | -46.3% | paired t-test | 0.0003 | 0.0010 | improved |
| 0.25 | fidelity | +0.034 | [+0.021, +0.050] | +3.6% | Wilcoxon signed-rank | 0.0020 | 0.0039 | negligible |
| 0.25 | evidence_support | +0.040 | [+0.017, +0.063] | +4.3% | paired t-test | 0.0033 | 0.0039 | negligible |
| 0.25 | manipulation | -0.029 | [-0.043, -0.016] | -44.4% | paired t-test | 0.0009 | 0.0026 | improved |
| 0.4 | fidelity | +0.035 | [+0.017, +0.053] | +3.7% | paired t-test | 0.0015 | 0.0030 | negligible |
| 0.4 | evidence_support | +0.040 | [+0.016, +0.064] | +4.3% | paired t-test | 0.0044 | 0.0044 | negligible |
| 0.4 | manipulation | -0.029 | [-0.041, -0.017] | -44.4% | paired t-test | 0.0003 | 0.0009 | improved |

## Unilateral deviation from all-honest: gain of the best deviation (positive = deviating pays)

| Value | System | Agent | honest payoff | best deviation | gain | honest best in seeds |
|---|---|---|---|---|---|---|
| 0.0 | ablation | consumer | 0.520 | strategic | -0.120 | 10/10 |
| 0.0 | ablation | grid | 0.578 | strategic | -0.124 | 10/10 |
| 0.0 | ablation | market | 0.540 | strategic | -0.121 | 10/10 |
| 0.0 | ablation | producer | 0.539 | strategic | -0.103 | 10/10 |
| 0.0 | ablation | storage | 0.669 | strategic | -0.053 | 10/10 |
| 0.0 | baseline | consumer | 0.520 | misattributing | -0.108 | 10/10 |
| 0.0 | baseline | grid | 0.578 | misattributing | -0.113 | 10/10 |
| 0.0 | baseline | market | 0.540 | manipulative | -0.098 | 10/10 |
| 0.0 | baseline | producer | 0.539 | manipulative | -0.086 | 10/10 |
| 0.0 | baseline | storage | 0.669 | manipulative | -0.042 | 10/10 |
| 0.0 | proposed | consumer | 0.518 | strategic | -0.124 | 10/10 |
| 0.0 | proposed | grid | 0.576 | strategic | -0.129 | 10/10 |
| 0.0 | proposed | market | 0.542 | strategic | -0.128 | 10/10 |
| 0.0 | proposed | producer | 0.541 | strategic | -0.113 | 10/10 |
| 0.0 | proposed | storage | 0.668 | strategic | -0.053 | 10/10 |
| 0.1 | ablation | consumer | 0.520 | strategic | -0.120 | 10/10 |
| 0.1 | ablation | grid | 0.578 | strategic | -0.124 | 10/10 |
| 0.1 | ablation | market | 0.540 | strategic | -0.121 | 10/10 |
| 0.1 | ablation | producer | 0.539 | strategic | -0.103 | 10/10 |
| 0.1 | ablation | storage | 0.669 | strategic | -0.053 | 10/10 |
| 0.1 | baseline | consumer | 0.520 | misattributing | -0.108 | 10/10 |
| 0.1 | baseline | grid | 0.578 | misattributing | -0.113 | 10/10 |
| 0.1 | baseline | market | 0.540 | manipulative | -0.098 | 10/10 |
| 0.1 | baseline | producer | 0.539 | manipulative | -0.086 | 10/10 |
| 0.1 | baseline | storage | 0.669 | manipulative | -0.042 | 10/10 |
| 0.1 | proposed | consumer | 0.518 | strategic | -0.124 | 10/10 |
| 0.1 | proposed | grid | 0.576 | strategic | -0.129 | 10/10 |
| 0.1 | proposed | market | 0.542 | strategic | -0.128 | 10/10 |
| 0.1 | proposed | producer | 0.541 | strategic | -0.113 | 10/10 |
| 0.1 | proposed | storage | 0.668 | strategic | -0.053 | 10/10 |
| 0.25 | ablation | consumer | 0.520 | strategic | -0.120 | 10/10 |
| 0.25 | ablation | grid | 0.578 | strategic | -0.124 | 10/10 |
| 0.25 | ablation | market | 0.540 | strategic | -0.121 | 10/10 |
| 0.25 | ablation | producer | 0.539 | strategic | -0.103 | 10/10 |
| 0.25 | ablation | storage | 0.669 | strategic | -0.053 | 10/10 |
| 0.25 | baseline | consumer | 0.520 | misattributing | -0.108 | 10/10 |
| 0.25 | baseline | grid | 0.578 | misattributing | -0.113 | 10/10 |
| 0.25 | baseline | market | 0.540 | manipulative | -0.098 | 10/10 |
| 0.25 | baseline | producer | 0.539 | manipulative | -0.086 | 10/10 |
| 0.25 | baseline | storage | 0.669 | manipulative | -0.042 | 10/10 |
| 0.25 | proposed | consumer | 0.518 | strategic | -0.124 | 10/10 |
| 0.25 | proposed | grid | 0.576 | strategic | -0.129 | 10/10 |
| 0.25 | proposed | market | 0.542 | strategic | -0.128 | 10/10 |
| 0.25 | proposed | producer | 0.541 | strategic | -0.113 | 10/10 |
| 0.25 | proposed | storage | 0.668 | strategic | -0.053 | 10/10 |
| 0.4 | ablation | consumer | 0.520 | strategic | -0.120 | 10/10 |
| 0.4 | ablation | grid | 0.578 | strategic | -0.124 | 10/10 |
| 0.4 | ablation | market | 0.540 | strategic | -0.121 | 10/10 |
| 0.4 | ablation | producer | 0.539 | strategic | -0.103 | 10/10 |
| 0.4 | ablation | storage | 0.669 | strategic | -0.053 | 10/10 |
| 0.4 | baseline | consumer | 0.520 | misattributing | -0.108 | 10/10 |
| 0.4 | baseline | grid | 0.578 | misattributing | -0.113 | 10/10 |
| 0.4 | baseline | market | 0.540 | manipulative | -0.098 | 10/10 |
| 0.4 | baseline | producer | 0.539 | manipulative | -0.086 | 10/10 |
| 0.4 | baseline | storage | 0.669 | manipulative | -0.042 | 10/10 |
| 0.4 | proposed | consumer | 0.518 | strategic | -0.124 | 10/10 |
| 0.4 | proposed | grid | 0.576 | strategic | -0.129 | 10/10 |
| 0.4 | proposed | market | 0.542 | strategic | -0.128 | 10/10 |
| 0.4 | proposed | producer | 0.541 | strategic | -0.113 | 10/10 |
| 0.4 | proposed | storage | 0.668 | strategic | -0.053 | 10/10 |

Agents (of 5) for whom honest is the best unilateral response:
- 0.0: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.1: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.25: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.4: {'ablation': 5, 'baseline': 5, 'proposed': 5}
