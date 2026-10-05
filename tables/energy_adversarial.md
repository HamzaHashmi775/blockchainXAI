# Energy — robustness to malicious agents

n = 10 seeds; mean ± SD. Malicious agents always play *manipulative*; 10% and 30% are realised in expectation over rounds.

## collective_accuracy

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.744 ± 0.019 | 0.748 ± 0.021 | 0.737 ± 0.026 | 0.698 ± 0.030 | 0.679 ± 0.049 |
| proposed | 0.754 ± 0.013 | 0.756 ± 0.016 | 0.752 ± 0.019 | 0.745 ± 0.025 | 0.729 ± 0.026 |

## fidelity

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.936 ± 0.024 | 0.841 ± 0.015 | 0.739 ± 0.032 | 0.616 ± 0.043 | 0.546 ± 0.026 |
| proposed | 0.970 ± 0.004 | 0.872 ± 0.006 | 0.775 ± 0.006 | 0.675 ± 0.004 | 0.582 ± 0.004 |

## evidence_support

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.926 ± 0.031 | 0.829 ± 0.022 | 0.728 ± 0.022 | 0.609 ± 0.037 | 0.540 ± 0.038 |
| proposed | 0.966 ± 0.004 | 0.868 ± 0.007 | 0.771 ± 0.008 | 0.673 ± 0.005 | 0.579 ± 0.005 |

## manipulation

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.066 ± 0.017 | 0.129 ± 0.016 | 0.205 ± 0.034 | 0.294 ± 0.035 | 0.344 ± 0.053 |
| proposed | 0.036 ± 0.005 | 0.105 ± 0.014 | 0.175 ± 0.024 | 0.249 ± 0.035 | 0.319 ± 0.041 |

## manipulation_success

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.050 ± 0.017 | 0.061 ± 0.014 | 0.096 ± 0.033 | 0.158 ± 0.038 | 0.189 ± 0.074 |
| proposed | 0.025 ± 0.012 | 0.043 ± 0.015 | 0.048 ± 0.017 | 0.065 ± 0.021 | 0.077 ± 0.036 |

## collective_utility

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.626 ± 0.004 | 0.630 ± 0.004 | 0.636 ± 0.006 | 0.643 ± 0.007 | 0.650 ± 0.011 |
| proposed | 0.624 ± 0.003 | 0.628 ± 0.005 | 0.624 ± 0.005 | 0.625 ± 0.005 | 0.626 ± 0.007 |

## fidelity_non_malicious

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.936 ± 0.024 | 0.938 ± 0.014 | 0.924 ± 0.040 | 0.883 ± 0.062 | 0.911 ± 0.044 |
| proposed | 0.970 ± 0.004 | 0.972 ± 0.003 | 0.968 ± 0.008 | 0.968 ± 0.005 | 0.970 ± 0.007 |

## manipulation_non_malicious

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.066 ± 0.017 | 0.065 ± 0.011 | 0.082 ± 0.027 | 0.109 ± 0.037 | 0.089 ± 0.033 |
| proposed | 0.036 ± 0.005 | 0.038 ± 0.007 | 0.047 ± 0.011 | 0.047 ± 0.023 | 0.049 ± 0.024 |

## Accuracy degradation: accuracy(0%) − accuracy(p)

- baseline: 10%: -0.004 ± 0.017, 20%: +0.007 ± 0.033, 30%: +0.046 ± 0.041, 40%: +0.065 ± 0.055
- proposed: 10%: -0.003 ± 0.019, 20%: +0.002 ± 0.021, 30%: +0.009 ± 0.030, 40%: +0.025 ± 0.029
- Friedman across shares, baseline: χ² = 21.12, p = 0.0002998
- Friedman across shares, proposed: χ² = 7.15, p = 0.1283

## H4 primary: mean degradation over 10–40%, proposed − baseline

Δ = -0.0203 (95% CI [-0.0426, +0.0019]), paired t-test, p = 0.06837, cohen_dz = -0.65. Negative Δ = proposed degrades less.

| Share | Δ degradation | p | p (Holm) |
|---|---|---|---|
| 10% | +0.0012 | 0.8299 | 0.938 |
| 20% | -0.0054 | 0.469 | 0.938 |
| 30% | -0.0370 | 0.03155 | 0.1262 |
| 40% | -0.0402 | 0.08718 | 0.2616 |

## Collective accuracy, proposed − baseline at each share

| Share | Δ accuracy | 95% CI | test | p (unadjusted) |
|---|---|---|---|---|
| 0% | +0.0092 | [-0.0002, +0.0186] | paired t-test | 0.05406 |
| 10% | +0.0080 | [-0.0066, +0.0226] | paired t-test | 0.2476 |
| 20% | +0.0146 | [+0.0040, +0.0276] | Wilcoxon signed-rank | 0.02539 |
| 30% | +0.0462 | [+0.0185, +0.0739] | paired t-test | 0.004371 |
| 40% | +0.0494 | [+0.0029, +0.0959] | paired t-test | 0.03958 |

## Collusion (2 colluders + 3 honest) vs no collusion

| System | Quantity | Without | With | Δ | p (unadjusted) |
|---|---|---|---|---|---|
| baseline | collective_accuracy | 0.763 | 0.734 | -0.030 | 0.0001851 |
| baseline | collective_utility | 0.623 | 0.649 | +0.026 | 4.348e-05 |
| baseline | manipulation_success | 0.000 | 0.155 | +0.155 | 1.345e-10 |
| baseline | colluders_private_utility | 0.612 | 0.704 | +0.092 | 7.412e-07 |
| baseline | honest_agents_private_utility | 0.630 | 0.612 | -0.018 | 0.02924 |
| baseline | colluders_reward | 0.510 | 0.377 | -0.134 | 1.279e-05 |
| baseline | honest_agents_reward | 0.519 | 0.621 | +0.102 | 0.000152 |
| baseline | colluders_payoff | 0.561 | 0.540 | -0.021 | 0.001953 |
| baseline | honest_agents_payoff | 0.574 | 0.616 | +0.042 | 0.0002443 |
| proposed | collective_accuracy | 0.771 | 0.764 | -0.007 | 0.4727 |
| proposed | collective_utility | 0.622 | 0.622 | -0.001 | 0.9219 |
| proposed | manipulation_success | 0.000 | 0.047 | +0.047 | 4.625e-05 |
| proposed | colluders_private_utility | 0.612 | 0.605 | -0.007 | 0.009766 |
| proposed | honest_agents_private_utility | 0.629 | 0.633 | +0.003 | 0.01311 |
| proposed | colluders_reward | 0.510 | 0.010 | -0.501 | 3.128e-13 |
| proposed | honest_agents_reward | 0.519 | 0.948 | +0.429 | 0.001953 |
| proposed | colluders_payoff | 0.561 | 0.307 | -0.254 | 1.625e-12 |
| proposed | honest_agents_payoff | 0.574 | 0.791 | +0.216 | 0.001953 |
| proposed | colluders_final_reputation | 0.542 | 0.012 | -0.531 | 2.284e-08 |
