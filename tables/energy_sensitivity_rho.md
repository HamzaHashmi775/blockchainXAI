# Sensitivity: reputation.rho

n = 10 seeds; mean ± SD. Exploratory (not pre-declared) values: none.

## fidelity

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.970 ± 0.003 | 0.936 ± 0.024 | 0.971 ± 0.003 |
| 0.8 | 0.970 ± 0.003 | 0.936 ± 0.024 | 0.970 ± 0.004 |
| 0.95 | 0.970 ± 0.003 | 0.936 ± 0.024 | 0.970 ± 0.003 |

## evidence_support

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.967 ± 0.004 | 0.926 ± 0.031 | 0.967 ± 0.004 |
| 0.8 | 0.967 ± 0.004 | 0.926 ± 0.031 | 0.966 ± 0.004 |
| 0.95 | 0.967 ± 0.004 | 0.926 ± 0.031 | 0.965 ± 0.005 |

## manipulation

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.035 ± 0.004 | 0.066 ± 0.017 | 0.037 ± 0.003 |
| 0.8 | 0.035 ± 0.004 | 0.066 ± 0.017 | 0.036 ± 0.005 |
| 0.95 | 0.035 ± 0.004 | 0.066 ± 0.017 | 0.038 ± 0.006 |

## collective_accuracy

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.753 ± 0.016 | 0.744 ± 0.019 | 0.752 ± 0.014 |
| 0.8 | 0.753 ± 0.016 | 0.744 ± 0.019 | 0.754 ± 0.013 |
| 0.95 | 0.753 ± 0.016 | 0.744 ± 0.019 | 0.752 ± 0.014 |

## manipulation_success

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.022 ± 0.008 | 0.050 ± 0.017 | 0.028 ± 0.011 |
| 0.8 | 0.022 ± 0.008 | 0.050 ± 0.017 | 0.025 ± 0.012 |
| 0.95 | 0.022 ± 0.008 | 0.050 ± 0.017 | 0.026 ± 0.014 |

## honest_share

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.883 ± 0.037 | 0.775 ± 0.045 | 0.865 ± 0.032 |
| 0.8 | 0.883 ± 0.037 | 0.775 ± 0.045 | 0.876 ± 0.032 |
| 0.95 | 0.883 ± 0.037 | 0.775 ± 0.045 | 0.860 ± 0.053 |

## Proposed − baseline

| Value | Metric | Δ | 95% CI | Rel. | test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.5 | fidelity | +0.034 | [+0.017, +0.052] | +3.7% | paired t-test | 0.0016 | 0.0033 | negligible |
| 0.5 | evidence_support | +0.041 | [+0.018, +0.064] | +4.4% | paired t-test | 0.0029 | 0.0033 | negligible |
| 0.5 | manipulation | -0.029 | [-0.041, -0.017] | -44.1% | paired t-test | 0.0004 | 0.0011 | improved |
| 0.8 | fidelity | +0.034 | [+0.021, +0.050] | +3.6% | Wilcoxon signed-rank | 0.0020 | 0.0039 | negligible |
| 0.8 | evidence_support | +0.040 | [+0.017, +0.063] | +4.3% | paired t-test | 0.0033 | 0.0039 | negligible |
| 0.8 | manipulation | -0.029 | [-0.043, -0.016] | -44.4% | paired t-test | 0.0009 | 0.0026 | improved |
| 0.95 | fidelity | +0.034 | [+0.017, +0.051] | +3.6% | paired t-test | 0.0014 | 0.0029 | negligible |
| 0.95 | evidence_support | +0.039 | [+0.017, +0.061] | +4.2% | paired t-test | 0.0030 | 0.0030 | negligible |
| 0.95 | manipulation | -0.028 | [-0.039, -0.017] | -42.8% | paired t-test | 0.0003 | 0.0009 | improved |

## Unilateral deviation from all-honest: gain of the best deviation (positive = deviating pays)

| Value | System | Agent | honest payoff | best deviation | gain | honest best in seeds |
|---|---|---|---|---|---|---|
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
| 0.5 | proposed | consumer | 0.517 | strategic | -0.123 | 10/10 |
| 0.5 | proposed | grid | 0.576 | strategic | -0.128 | 10/10 |
| 0.5 | proposed | market | 0.543 | strategic | -0.127 | 10/10 |
| 0.5 | proposed | producer | 0.542 | strategic | -0.114 | 10/10 |
| 0.5 | proposed | storage | 0.666 | strategic | -0.049 | 10/10 |
| 0.8 | ablation | consumer | 0.520 | strategic | -0.120 | 10/10 |
| 0.8 | ablation | grid | 0.578 | strategic | -0.124 | 10/10 |
| 0.8 | ablation | market | 0.540 | strategic | -0.121 | 10/10 |
| 0.8 | ablation | producer | 0.539 | strategic | -0.103 | 10/10 |
| 0.8 | ablation | storage | 0.669 | strategic | -0.053 | 10/10 |
| 0.8 | baseline | consumer | 0.520 | misattributing | -0.108 | 10/10 |
| 0.8 | baseline | grid | 0.578 | misattributing | -0.113 | 10/10 |
| 0.8 | baseline | market | 0.540 | manipulative | -0.098 | 10/10 |
| 0.8 | baseline | producer | 0.539 | manipulative | -0.086 | 10/10 |
| 0.8 | baseline | storage | 0.669 | manipulative | -0.042 | 10/10 |
| 0.8 | proposed | consumer | 0.518 | strategic | -0.124 | 10/10 |
| 0.8 | proposed | grid | 0.576 | strategic | -0.129 | 10/10 |
| 0.8 | proposed | market | 0.542 | strategic | -0.128 | 10/10 |
| 0.8 | proposed | producer | 0.541 | strategic | -0.113 | 10/10 |
| 0.8 | proposed | storage | 0.668 | strategic | -0.053 | 10/10 |
| 0.95 | ablation | consumer | 0.520 | strategic | -0.120 | 10/10 |
| 0.95 | ablation | grid | 0.578 | strategic | -0.124 | 10/10 |
| 0.95 | ablation | market | 0.540 | strategic | -0.121 | 10/10 |
| 0.95 | ablation | producer | 0.539 | strategic | -0.103 | 10/10 |
| 0.95 | ablation | storage | 0.669 | strategic | -0.053 | 10/10 |
| 0.95 | baseline | consumer | 0.520 | misattributing | -0.108 | 10/10 |
| 0.95 | baseline | grid | 0.578 | misattributing | -0.113 | 10/10 |
| 0.95 | baseline | market | 0.540 | manipulative | -0.098 | 10/10 |
| 0.95 | baseline | producer | 0.539 | manipulative | -0.086 | 10/10 |
| 0.95 | baseline | storage | 0.669 | manipulative | -0.042 | 10/10 |
| 0.95 | proposed | consumer | 0.520 | strategic | -0.125 | 10/10 |
| 0.95 | proposed | grid | 0.578 | strategic | -0.131 | 10/10 |
| 0.95 | proposed | market | 0.541 | strategic | -0.126 | 10/10 |
| 0.95 | proposed | producer | 0.540 | strategic | -0.111 | 10/10 |
| 0.95 | proposed | storage | 0.669 | strategic | -0.054 | 10/10 |

Agents (of 5) for whom honest is the best unilateral response:
- 0.5: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.8: {'ablation': 5, 'baseline': 5, 'proposed': 5}
- 0.95: {'ablation': 5, 'baseline': 5, 'proposed': 5}
