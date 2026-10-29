# Sensitivity: reputation.rho

n = 10 seeds; mean ± SD. Exploratory (not pre-declared) values: none.

## fidelity

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.892 ± 0.033 | 0.510 ± 0.077 | 0.945 ± 0.010 |
| 0.8 | 0.892 ± 0.033 | 0.510 ± 0.077 | 0.936 ± 0.020 |
| 0.95 | 0.892 ± 0.033 | 0.510 ± 0.077 | 0.941 ± 0.012 |

## evidence_support

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.892 ± 0.033 | 0.522 ± 0.070 | 0.933 ± 0.022 |
| 0.8 | 0.892 ± 0.033 | 0.522 ± 0.070 | 0.917 ± 0.023 |
| 0.95 | 0.892 ± 0.033 | 0.522 ± 0.070 | 0.908 ± 0.028 |

## manipulation

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.153 ± 0.023 | 0.392 ± 0.038 | 0.110 ± 0.032 |
| 0.8 | 0.153 ± 0.023 | 0.392 ± 0.038 | 0.119 ± 0.015 |
| 0.95 | 0.153 ± 0.023 | 0.392 ± 0.038 | 0.129 ± 0.024 |

## collective_accuracy

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.564 ± 0.052 | 0.578 ± 0.045 | 0.611 ± 0.029 |
| 0.8 | 0.564 ± 0.052 | 0.578 ± 0.045 | 0.606 ± 0.033 |
| 0.95 | 0.564 ± 0.052 | 0.578 ± 0.045 | 0.603 ± 0.043 |

## manipulation_success

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.352 ± 0.065 | 0.398 ± 0.057 | 0.233 ± 0.059 |
| 0.8 | 0.352 ± 0.065 | 0.398 ± 0.057 | 0.263 ± 0.032 |
| 0.95 | 0.352 ± 0.065 | 0.398 ± 0.057 | 0.295 ± 0.070 |

## honest_share

| Value | ablation | baseline | proposed |
|---|---|---|---|
| 0.5 | 0.353 ± 0.082 | 0.095 ± 0.051 | 0.448 ± 0.135 |
| 0.8 | 0.353 ± 0.082 | 0.095 ± 0.051 | 0.414 ± 0.072 |
| 0.95 | 0.353 ± 0.082 | 0.095 ± 0.051 | 0.376 ± 0.081 |

## Proposed − baseline

| Value | Metric | Δ | 95% CI | Rel. | test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.5 | fidelity | +0.435 | [+0.380, +0.489] | +85.2% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.5 | evidence_support | +0.411 | [+0.368, +0.453] | +78.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.5 | manipulation | -0.282 | [-0.316, -0.247] | -71.9% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.8 | fidelity | +0.426 | [+0.370, +0.482] | +83.5% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.8 | evidence_support | +0.395 | [+0.345, +0.444] | +75.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.8 | manipulation | -0.273 | [-0.302, -0.243] | -69.7% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.95 | fidelity | +0.431 | [+0.379, +0.482] | +84.4% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.95 | evidence_support | +0.386 | [+0.328, +0.445] | +74.0% | paired t-test | 0.0000 | 0.0000 | improved |
| 0.95 | manipulation | -0.263 | [-0.294, -0.231] | -67.0% | paired t-test | 0.0000 | 0.0000 | improved |

## Unilateral deviation from all-honest: gain of the best deviation (positive = deviating pays)

| Value | System | Agent | honest payoff | best deviation | gain | honest best in seeds |
|---|---|---|---|---|---|---|
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
| 0.5 | proposed | continuity | 0.574 | strategic | -0.054 | 10/10 |
| 0.5 | proposed | cost | 0.496 | strategic | +0.043 | 0/10 |
| 0.5 | proposed | lead_time | 0.564 | strategic | -0.026 | 10/10 |
| 0.5 | proposed | logistics | 0.588 | strategic | +0.063 | 0/10 |
| 0.5 | proposed | reliability | 0.482 | strategic | +0.012 | 0/10 |
| 0.8 | ablation | continuity | 0.615 | strategic | -0.062 | 10/10 |
| 0.8 | ablation | cost | 0.465 | strategic | +0.035 | 0/10 |
| 0.8 | ablation | lead_time | 0.593 | strategic | -0.022 | 10/10 |
| 0.8 | ablation | logistics | 0.581 | strategic | +0.069 | 0/10 |
| 0.8 | ablation | reliability | 0.454 | strategic | +0.046 | 0/10 |
| 0.8 | baseline | continuity | 0.615 | manipulative | +0.016 | 0/10 |
| 0.8 | baseline | cost | 0.465 | manipulative | +0.058 | 0/10 |
| 0.8 | baseline | lead_time | 0.593 | manipulative | +0.025 | 0/10 |
| 0.8 | baseline | logistics | 0.581 | manipulative | +0.104 | 0/10 |
| 0.8 | baseline | reliability | 0.454 | manipulative | +0.150 | 0/10 |
| 0.8 | proposed | continuity | 0.589 | strategic | -0.061 | 10/10 |
| 0.8 | proposed | cost | 0.485 | strategic | +0.044 | 0/10 |
| 0.8 | proposed | lead_time | 0.575 | strategic | -0.026 | 10/10 |
| 0.8 | proposed | logistics | 0.591 | strategic | +0.065 | 0/10 |
| 0.8 | proposed | reliability | 0.471 | strategic | +0.019 | 0/10 |
| 0.95 | ablation | continuity | 0.615 | strategic | -0.062 | 10/10 |
| 0.95 | ablation | cost | 0.465 | strategic | +0.035 | 0/10 |
| 0.95 | ablation | lead_time | 0.593 | strategic | -0.022 | 10/10 |
| 0.95 | ablation | logistics | 0.581 | strategic | +0.069 | 0/10 |
| 0.95 | ablation | reliability | 0.454 | strategic | +0.046 | 0/10 |
| 0.95 | baseline | continuity | 0.615 | manipulative | +0.016 | 0/10 |
| 0.95 | baseline | cost | 0.465 | manipulative | +0.058 | 0/10 |
| 0.95 | baseline | lead_time | 0.593 | manipulative | +0.025 | 0/10 |
| 0.95 | baseline | logistics | 0.581 | manipulative | +0.104 | 0/10 |
| 0.95 | baseline | reliability | 0.454 | manipulative | +0.150 | 0/10 |
| 0.95 | proposed | continuity | 0.598 | strategic | -0.065 | 10/10 |
| 0.95 | proposed | cost | 0.480 | strategic | +0.037 | 0/10 |
| 0.95 | proposed | lead_time | 0.581 | strategic | -0.028 | 10/10 |
| 0.95 | proposed | logistics | 0.588 | strategic | +0.074 | 0/10 |
| 0.95 | proposed | reliability | 0.467 | strategic | +0.017 | 0/10 |

Agents (of 5) for whom honest is the best unilateral response:
- 0.5: {'ablation': 2, 'baseline': 0, 'proposed': 2}
- 0.8: {'ablation': 2, 'baseline': 0, 'proposed': 2}
- 0.95: {'ablation': 2, 'baseline': 0, 'proposed': 2}
