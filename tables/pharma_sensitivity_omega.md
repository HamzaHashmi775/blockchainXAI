# Sensitivity: game.omega

n = 10 seeds; mean ± SD. Exploratory (not pre-declared) values: ['0.9'].

## fidelity

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.958 ± 0.011 | 0.696 ± 0.113 | 0.953 ± 0.017 |
| 0.5 | 0.892 ± 0.033 | 0.510 ± 0.077 | 0.936 ± 0.020 |
| 0.75 | 0.674 ± 0.058 | 0.402 ± 0.108 | 0.864 ± 0.044 |
| 0.9 | 0.548 ± 0.066 | 0.438 ± 0.065 | 0.771 ± 0.057 |

## evidence_support

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.942 ± 0.027 | 0.657 ± 0.080 | 0.950 ± 0.008 |
| 0.5 | 0.892 ± 0.033 | 0.522 ± 0.070 | 0.917 ± 0.023 |
| 0.75 | 0.667 ± 0.053 | 0.361 ± 0.097 | 0.822 ± 0.032 |
| 0.9 | 0.506 ± 0.051 | 0.417 ± 0.050 | 0.752 ± 0.066 |

## manipulation

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.093 ± 0.012 | 0.295 ± 0.060 | 0.083 ± 0.020 |
| 0.5 | 0.153 ± 0.023 | 0.392 ± 0.038 | 0.119 ± 0.015 |
| 0.75 | 0.307 ± 0.039 | 0.475 ± 0.064 | 0.217 ± 0.023 |
| 0.9 | 0.398 ± 0.027 | 0.453 ± 0.039 | 0.266 ± 0.033 |

## collective_accuracy

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.595 ± 0.029 | 0.587 ± 0.035 | 0.625 ± 0.039 |
| 0.5 | 0.564 ± 0.052 | 0.578 ± 0.045 | 0.606 ± 0.033 |
| 0.75 | 0.560 ± 0.042 | 0.565 ± 0.031 | 0.592 ± 0.042 |
| 0.9 | 0.566 ± 0.030 | 0.571 ± 0.044 | 0.622 ± 0.039 |

## manipulation_success

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.224 ± 0.052 | 0.381 ± 0.052 | 0.166 ± 0.038 |
| 0.5 | 0.352 ± 0.065 | 0.398 ± 0.057 | 0.263 ± 0.032 |
| 0.75 | 0.413 ± 0.046 | 0.424 ± 0.032 | 0.374 ± 0.044 |
| 0.9 | 0.420 ± 0.032 | 0.422 ± 0.046 | 0.353 ± 0.032 |

## honest_share

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.25 | 0.505 ± 0.048 | 0.160 ± 0.056 | 0.554 ± 0.107 |
| 0.5 | 0.353 ± 0.082 | 0.095 ± 0.051 | 0.414 ± 0.072 |
| 0.75 | 0.171 ± 0.088 | 0.079 ± 0.036 | 0.152 ± 0.044 |
| 0.9 | 0.096 ± 0.035 | 0.070 ± 0.031 | 0.119 ± 0.061 |

## Proposed − baseline

| Value | Metric | Δ | 95% CI | Rel. | test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.25 | fidelity | +0.257 | [+0.178, +0.337] | +37.0% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.25 | evidence_support | +0.293 | [+0.240, +0.347] | +44.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.25 | manipulation | -0.212 | [-0.255, -0.170] | -72.0% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.5 | fidelity | +0.426 | [+0.370, +0.482] | +83.5% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.5 | evidence_support | +0.395 | [+0.345, +0.444] | +75.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.5 | manipulation | -0.273 | [-0.302, -0.243] | -69.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.75 | fidelity | +0.462 | [+0.390, +0.534] | +115.0% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.75 | evidence_support | +0.461 | [+0.383, +0.539] | +127.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.75 | manipulation | -0.259 | [-0.302, -0.216] | -54.5% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.9 | fidelity | +0.333 | [+0.287, +0.379] | +76.0% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.9 | evidence_support | +0.335 | [+0.269, +0.400] | +80.3% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.9 | manipulation | -0.187 | [-0.215, -0.159] | -41.3% | paired t-test | 0.0000 | 0.0000 | improved |

## Unilateral deviation from all-honest: gain of the best deviation (positive = deviating pays)

| Value | System | Agent | honest payoff | best deviation | gain | honest best in seeds |
|---|---|---|---|---|---|---|
| 0.25 | ablation | continuity | 0.559 | strategic | -0.138 | 10/10 |
| 0.25 | ablation | cost | 0.487 | strategic | +0.017 | 1/10 |
| 0.25 | ablation | lead_time | 0.515 | strategic | -0.035 | 10/10 |
| 0.25 | ablation | logistics | 0.525 | strategic | +0.066 | 0/10 |
| 0.25 | ablation | reliability | 0.463 | strategic | -0.033 | 10/10 |
| 0.25 | baseline | continuity | 0.559 | misattributing | -0.035 | 10/10 |
| 0.25 | baseline | cost | 0.487 | misattributing | +0.045 | 0/10 |
| 0.25 | baseline | lead_time | 0.515 | manipulative | -0.003 | 6/10 |
| 0.25 | baseline | logistics | 0.525 | misattributing | +0.089 | 0/10 |
| 0.25 | baseline | reliability | 0.463 | manipulative | +0.043 | 0/10 |
| 0.25 | proposed | continuity | 0.545 | strategic | -0.139 | 10/10 |
| 0.25 | proposed | cost | 0.497 | strategic | +0.020 | 0/10 |
| 0.25 | proposed | lead_time | 0.507 | strategic | -0.037 | 10/10 |
| 0.25 | proposed | logistics | 0.531 | strategic | +0.062 | 0/10 |
| 0.25 | proposed | reliability | 0.472 | strategic | -0.048 | 10/10 |
| 0.5 | ablation | continuity | 0.615 | strategic | -0.062 | 10/10 |
| 0.5 | ablation | cost | 0.465 | strategic | +0.035 | 0/10 |
| 0.5 | ablation | lead_time | 0.593 | strategic | -0.022 | 10/10 |
| 0.5 | ablation | logistics | 0.581 | strategic | +0.069 | 0/10 |
| 0.5 | ablation | reliability | 0.454 | strategic | +0.046 | 0/10 |
| 0.5 | baseline | continuity | 0.615 | manipulative | +0.016 | 0/10 |
| 0.5 | baseline | cost | 0.465 | manipulative | +0.058 | 0/10 |
| 0.5 | baseline | lead_time | 0.593 | manipulative | +0.025 | 0/10 |
| 0.5 | baseline | logistics | 0.581 | manipulative | +0.104 | 0/10 |
| 0.5 | baseline | reliability | 0.454 | manipulative | +0.150 | 0/10 |
| 0.5 | proposed | continuity | 0.589 | strategic | -0.061 | 10/10 |
| 0.5 | proposed | cost | 0.485 | strategic | +0.044 | 0/10 |
| 0.5 | proposed | lead_time | 0.575 | strategic | -0.026 | 10/10 |
| 0.5 | proposed | logistics | 0.591 | strategic | +0.065 | 0/10 |
| 0.5 | proposed | reliability | 0.471 | strategic | +0.019 | 0/10 |
| 0.75 | ablation | continuity | 0.671 | strategic | +0.015 | 3/10 |
| 0.75 | ablation | cost | 0.442 | strategic | +0.054 | 0/10 |
| 0.75 | ablation | lead_time | 0.671 | strategic | -0.009 | 10/10 |
| 0.75 | ablation | logistics | 0.636 | strategic | +0.073 | 0/10 |
| 0.75 | ablation | reliability | 0.445 | manipulative | +0.154 | 0/10 |
| 0.75 | baseline | continuity | 0.671 | manipulative | +0.068 | 0/10 |
| 0.75 | baseline | cost | 0.442 | manipulative | +0.123 | 0/10 |
| 0.75 | baseline | lead_time | 0.671 | manipulative | +0.054 | 0/10 |
| 0.75 | baseline | logistics | 0.636 | manipulative | +0.132 | 0/10 |
| 0.75 | baseline | reliability | 0.445 | manipulative | +0.257 | 0/10 |
| 0.75 | proposed | continuity | 0.633 | strategic | +0.016 | 3/10 |
| 0.75 | proposed | cost | 0.473 | strategic | +0.067 | 0/10 |
| 0.75 | proposed | lead_time | 0.643 | strategic | -0.014 | 10/10 |
| 0.75 | proposed | logistics | 0.651 | strategic | +0.068 | 0/10 |
| 0.75 | proposed | reliability | 0.470 | strategic | +0.086 | 0/10 |
| 0.9 | ablation | continuity | 0.704 | strategic | +0.061 | 0/10 |
| 0.9 | ablation | cost | 0.428 | manipulative | +0.119 | 0/10 |
| 0.9 | ablation | lead_time | 0.718 | manipulative | +0.030 | 1/10 |
| 0.9 | ablation | logistics | 0.670 | manipulative | +0.096 | 0/10 |
| 0.9 | ablation | reliability | 0.439 | manipulative | +0.280 | 0/10 |
| 0.9 | baseline | continuity | 0.704 | manipulative | +0.099 | 0/10 |
| 0.9 | baseline | cost | 0.428 | manipulative | +0.163 | 0/10 |
| 0.9 | baseline | lead_time | 0.718 | manipulative | +0.071 | 0/10 |
| 0.9 | baseline | logistics | 0.670 | manipulative | +0.148 | 0/10 |
| 0.9 | baseline | reliability | 0.439 | manipulative | +0.321 | 0/10 |
| 0.9 | proposed | continuity | 0.659 | strategic | +0.062 | 0/10 |
| 0.9 | proposed | cost | 0.465 | strategic | +0.082 | 0/10 |
| 0.9 | proposed | lead_time | 0.684 | strategic | -0.007 | 9/10 |
| 0.9 | proposed | logistics | 0.687 | strategic | +0.070 | 0/10 |
| 0.9 | proposed | reliability | 0.470 | strategic | +0.126 | 0/10 |

Agents (of 5) for whom honest is the best unilateral response:
- 0.25: {'ablation': 3, 'baseline': 2, 'proposed': 3}
- 0.5: {'ablation': 2, 'baseline': 0, 'proposed': 2}
- 0.75: {'ablation': 1, 'baseline': 0, 'proposed': 1}
- 0.9: {'ablation': 0, 'baseline': 0, 'proposed': 1}
