# Pharma — robustness to malicious agents

n = 10 seeds; mean ± SD. Malicious agents always play *manipulative*; 10% and 30% are realised in expectation over rounds.

## collective_accuracy

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.578 ± 0.045 | 0.598 ± 0.033 | 0.583 ± 0.035 | 0.577 ± 0.030 | 0.570 ± 0.042 |
| proposed | 0.606 ± 0.033 | 0.588 ± 0.057 | 0.569 ± 0.060 | 0.558 ± 0.057 | 0.572 ± 0.055 |

## fidelity

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.510 ± 0.077 | 0.497 ± 0.039 | 0.457 ± 0.103 | 0.366 ± 0.066 | 0.304 ± 0.084 |
| proposed | 0.936 ± 0.020 | 0.845 ± 0.018 | 0.758 ± 0.015 | 0.665 ± 0.014 | 0.556 ± 0.016 |

## evidence_support

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.522 ± 0.070 | 0.469 ± 0.059 | 0.437 ± 0.086 | 0.340 ± 0.057 | 0.290 ± 0.085 |
| proposed | 0.917 ± 0.023 | 0.847 ± 0.014 | 0.735 ± 0.044 | 0.648 ± 0.027 | 0.522 ± 0.038 |

## manipulation

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.392 ± 0.038 | 0.413 ± 0.027 | 0.436 ± 0.051 | 0.488 ± 0.033 | 0.528 ± 0.051 |
| proposed | 0.119 ± 0.015 | 0.180 ± 0.011 | 0.250 ± 0.023 | 0.292 ± 0.023 | 0.382 ± 0.024 |

## manipulation_success

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.398 ± 0.057 | 0.384 ± 0.041 | 0.398 ± 0.043 | 0.408 ± 0.034 | 0.418 ± 0.042 |
| proposed | 0.263 ± 0.032 | 0.329 ± 0.043 | 0.362 ± 0.064 | 0.364 ± 0.071 | 0.385 ± 0.049 |

## collective_utility

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.602 ± 0.006 | 0.604 ± 0.004 | 0.602 ± 0.005 | 0.599 ± 0.003 | 0.597 ± 0.006 |
| proposed | 0.599 ± 0.004 | 0.597 ± 0.006 | 0.594 ± 0.009 | 0.593 ± 0.007 | 0.595 ± 0.005 |

## fidelity_non_malicious

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.510 ± 0.077 | 0.552 ± 0.043 | 0.571 ± 0.129 | 0.521 ± 0.093 | 0.506 ± 0.140 |
| proposed | 0.936 ± 0.020 | 0.938 ± 0.017 | 0.947 ± 0.018 | 0.948 ± 0.018 | 0.927 ± 0.026 |

## manipulation_non_malicious

| System | 0% | 10% | 20% | 30% | 40% |
|---|---|---|---|---|---|
| baseline | 0.392 ± 0.038 | 0.384 ± 0.029 | 0.375 ± 0.073 | 0.399 ± 0.045 | 0.406 ± 0.075 |
| proposed | 0.119 ± 0.015 | 0.126 ± 0.014 | 0.146 ± 0.024 | 0.125 ± 0.034 | 0.170 ± 0.039 |

## Accuracy degradation: accuracy(0%) − accuracy(p)

- baseline: 10%: -0.021 ± 0.060, 20%: -0.006 ± 0.058, 30%: +0.001 ± 0.052, 40%: +0.008 ± 0.056
- proposed: 10%: +0.019 ± 0.045, 20%: +0.038 ± 0.041, 30%: +0.048 ± 0.059, 40%: +0.034 ± 0.055
- Friedman across shares, baseline: χ² = 2.97, p = 0.5629
- Friedman across shares, proposed: χ² = 6.04, p = 0.1962

## H4 primary: mean degradation over 10–40%, proposed − baseline

Δ = +0.0390 (95% CI [-0.0095, +0.0875]), paired t-test, p = 0.1021, cohen_dz = 0.58. Negative Δ = proposed degrades less.

| Share | Δ degradation | p | p (Holm) |
|---|---|---|---|
| 10% | +0.0393 | 0.1305 | 0.4192 |
| 20% | +0.0433 | 0.1128 | 0.4192 |
| 30% | +0.0470 | 0.1048 | 0.4192 |
| 40% | +0.0263 | 0.4283 | 0.4283 |

## Collective accuracy, proposed − baseline at each share

| Share | Δ accuracy | 95% CI | test | p (unadjusted) |
|---|---|---|---|---|
| 0% | +0.0287 | [-0.0185, +0.0758] | paired t-test | 0.2021 |
| 10% | -0.0107 | [-0.0661, +0.0448] | paired t-test | 0.6738 |
| 20% | -0.0147 | [-0.0699, +0.0406] | paired t-test | 0.5628 |
| 30% | -0.0183 | [-0.0740, +0.0373] | paired t-test | 0.475 |
| 40% | +0.0023 | [-0.0558, +0.0605] | paired t-test | 0.9296 |

## Collusion (2 colluders + 3 honest) vs no collusion

| System | Quantity | Without | With | Δ | p (unadjusted) |
|---|---|---|---|---|---|
| baseline | collective_accuracy | 0.573 | 0.553 | -0.020 | 0.3437 |
| baseline | collective_utility | 0.604 | 0.590 | -0.014 | 0.004391 |
| baseline | manipulation_success | 0.000 | 0.380 | +0.380 | 3.68e-08 |
| baseline | colluders_private_utility | 0.626 | 0.787 | +0.161 | 0.001953 |
| baseline | honest_agents_private_utility | 0.590 | 0.458 | -0.132 | 0.00151 |
| baseline | colluders_reward | 0.474 | 0.484 | +0.009 | 0.496 |
| baseline | honest_agents_reward | 0.481 | 0.495 | +0.013 | 0.4922 |
| baseline | colluders_payoff | 0.550 | 0.635 | +0.085 | 0.001953 |
| baseline | honest_agents_payoff | 0.536 | 0.477 | -0.059 | 0.007755 |
| proposed | collective_accuracy | 0.607 | 0.570 | -0.036 | 0.007883 |
| proposed | collective_utility | 0.606 | 0.596 | -0.009 | 0.00431 |
| proposed | manipulation_success | 0.000 | 0.126 | +0.126 | 0.001953 |
| proposed | colluders_private_utility | 0.623 | 0.619 | -0.003 | 0.749 |
| proposed | honest_agents_private_utility | 0.594 | 0.581 | -0.013 | 0.1413 |
| proposed | colluders_reward | 0.475 | 0.017 | -0.458 | 1.85e-14 |
| proposed | honest_agents_reward | 0.481 | 0.856 | +0.375 | 1.477e-11 |
| proposed | colluders_payoff | 0.549 | 0.318 | -0.231 | 1.452e-11 |
| proposed | honest_agents_payoff | 0.538 | 0.718 | +0.181 | 1.626e-12 |
| proposed | colluders_final_reputation | 0.399 | 0.018 | -0.381 | 0.000127 |
