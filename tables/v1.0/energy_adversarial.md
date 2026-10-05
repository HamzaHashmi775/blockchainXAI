# Energy — robustness to malicious agents

n = 10 seeds; mean ± SD. Malicious agents always play *manipulative*; 10% and 30% are realised in expectation over rounds.

## collective_accuracy

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.745 ± 0.019 | 0.748 ± 0.012 | 0.744 ± 0.014 | 0.721 ± 0.028 | 0.675 ± 0.062 |
| proposed | 0.752 ± 0.020 | 0.759 ± 0.019 | 0.754 ± 0.016 | 0.745 ± 0.019 | 0.729 ± 0.023 |

## fidelity

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.908 ± 0.036 | 0.810 ± 0.033 | 0.718 ± 0.039 | 0.607 ± 0.054 | 0.529 ± 0.044 |
| proposed | 0.965 ± 0.005 | 0.865 ± 0.007 | 0.772 ± 0.004 | 0.673 ± 0.004 | 0.579 ± 0.003 |

## evidence_support

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.908 ± 0.036 | 0.810 ± 0.033 | 0.718 ± 0.039 | 0.607 ± 0.054 | 0.529 ± 0.044 |
| proposed | 0.965 ± 0.005 | 0.865 ± 0.007 | 0.772 ± 0.004 | 0.673 ± 0.004 | 0.579 ± 0.003 |

## manipulation

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.070 ± 0.020 | 0.137 ± 0.028 | 0.201 ± 0.036 | 0.286 ± 0.051 | 0.350 ± 0.056 |
| proposed | 0.034 ± 0.004 | 0.106 ± 0.013 | 0.169 ± 0.020 | 0.245 ± 0.026 | 0.313 ± 0.036 |

## manipulation_success

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.046 ± 0.017 | 0.060 ± 0.017 | 0.083 ± 0.022 | 0.129 ± 0.047 | 0.192 ± 0.079 |
| proposed | 0.021 ± 0.011 | 0.041 ± 0.016 | 0.043 ± 0.013 | 0.065 ± 0.011 | 0.072 ± 0.022 |

## collective_utility

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.625 ± 0.004 | 0.629 ± 0.006 | 0.634 ± 0.005 | 0.641 ± 0.007 | 0.646 ± 0.007 |
| proposed | 0.625 ± 0.003 | 0.627 ± 0.005 | 0.625 ± 0.003 | 0.628 ± 0.005 | 0.625 ± 0.007 |

## fidelity_non_malicious

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.908 ± 0.036 | 0.903 ± 0.035 | 0.898 ± 0.048 | 0.870 ± 0.078 | 0.882 ± 0.073 |
| proposed | 0.965 ± 0.005 | 0.965 ± 0.005 | 0.965 ± 0.005 | 0.964 ± 0.006 | 0.965 ± 0.005 |

## manipulation_non_malicious

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.070 ± 0.020 | 0.073 ± 0.025 | 0.079 ± 0.030 | 0.100 ± 0.048 | 0.098 ± 0.045 |
| proposed | 0.034 ± 0.004 | 0.039 ± 0.007 | 0.040 ± 0.009 | 0.043 ± 0.006 | 0.041 ± 0.008 |

## Accuracy degradation: accuracy(0%) − accuracy(p)

- baseline: 10%: -0.004 ± 0.011, 20%: +0.001 ± 0.018, 30%: +0.023 ± 0.035, 40%: +0.070 ± 0.062
- proposed: 10%: -0.007 ± 0.023, 20%: -0.002 ± 0.021, 30%: +0.007 ± 0.021, 40%: +0.023 ± 0.027
- Friedman across shares, baseline: χ² = 19.68, p = 0.0005779
- Friedman across shares, proposed: χ² = 13.75, p = 0.008151

## H4 primary: mean degradation over 10–40%, proposed − baseline

Δ = -0.0174 (95% CI [-0.0367, +0.0018]), paired t-test, p = 0.07043, cohen_dz = -0.65. Negative Δ = proposed degrades less.

| Share | Δ degradation | p | p (Holm) |
|---|---|---|---|
| 10% | -0.0034 | 0.6593 | 1 |
| 20% | -0.0028 | 0.657 | 1 |
| 30% | -0.0166 | 0.2149 | 0.6446 |
| 40% | -0.0470 | 0.0683 | 0.2732 |

## Collective accuracy, proposed − baseline at each share

| Share | Δ accuracy | 95% CI | test | p (unadjusted) |
|---|---|---|---|---|
| 0% | +0.0074 | [+0.0004, +0.0144] | paired t-test | 0.04144 |
| 10% | +0.0108 | [-0.0006, +0.0222] | paired t-test | 0.0609 |
| 20% | +0.0102 | [+0.0027, +0.0177] | paired t-test | 0.01316 |
| 30% | +0.0240 | [-0.0055, +0.0535] | paired t-test | 0.09891 |
| 40% | +0.0544 | [+0.0007, +0.1081] | paired t-test | 0.04759 |

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
