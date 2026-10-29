# Sensitivity: are the main verdicts robust?

Proposed vs baseline, section 9 verdict per value (Holm over F, E, M within each value; |rel| ≥ 5 % for 'improved'). 'Robust' = the verdict at every pre-declared value equals the main run's; exploratory values (marked *) are shown but not counted. One parameter varied at a time, 10 seeds per value.

## pharma_sensitivity_beta (`incentive_weights.beta`)

| Value | fidelity | evidence_support | manipulation |
|---|---|---|---|
| main run | improved | improved | improved |
| 0.0 | improved (+74.7%) | improved (+75.5%) | improved (-65.4%) |
| 0.1 | improved (+77.3%) | improved (+76.2%) | improved (-64.6%) |
| 0.25 | improved (+83.5%) | improved (+75.7%) | improved (-69.7%) |
| 0.4 | improved (+86.0%) | improved (+74.5%) | improved (-67.3%) |

Robust: fidelity yes, evidence_support yes, manipulation yes

## pharma_sensitivity_rho (`reputation.rho`)

| Value | fidelity | evidence_support | manipulation |
|---|---|---|---|
| main run | improved | improved | improved |
| 0.5 | improved (+85.2%) | improved (+78.7%) | improved (-71.9%) |
| 0.8 | improved (+83.5%) | improved (+75.7%) | improved (-69.7%) |
| 0.95 | improved (+84.4%) | improved (+74.0%) | improved (-67.0%) |

Robust: fidelity yes, evidence_support yes, manipulation yes

## pharma_sensitivity_omega (`game.omega`)

| Value | fidelity | evidence_support | manipulation |
|---|---|---|---|
| main run | improved | improved | improved |
| 0.25 | improved (+37.0%) | improved (+44.7%) | improved (-72.0%) |
| 0.5 | improved (+83.5%) | improved (+75.7%) | improved (-69.7%) |
| 0.75 | improved (+115.0%) | improved (+127.7%) | improved (-54.5%) |
| 0.9* | improved (+76.0%) | improved (+80.3%) | improved (-41.3%) |

Robust: fidelity yes, evidence_support yes, manipulation yes

## energy_sensitivity_beta (`incentive_weights.beta`)

| Value | fidelity | evidence_support | manipulation |
|---|---|---|---|
| main run | negligible | negligible | improved |
| 0.0 | negligible (+3.4%) | negligible (+4.4%) | improved (-43.0%) |
| 0.1 | negligible (+3.7%) | negligible (+4.4%) | improved (-46.3%) |
| 0.25 | negligible (+3.6%) | negligible (+4.3%) | improved (-44.4%) |
| 0.4 | negligible (+3.7%) | negligible (+4.3%) | improved (-44.4%) |

Robust: fidelity yes, evidence_support yes, manipulation yes

## energy_sensitivity_rho (`reputation.rho`)

| Value | fidelity | evidence_support | manipulation |
|---|---|---|---|
| main run | negligible | negligible | improved |
| 0.5 | negligible (+3.7%) | negligible (+4.4%) | improved (-44.1%) |
| 0.8 | negligible (+3.6%) | negligible (+4.3%) | improved (-44.4%) |
| 0.95 | negligible (+3.6%) | negligible (+4.2%) | improved (-42.8%) |

Robust: fidelity yes, evidence_support yes, manipulation yes

## energy_sensitivity_omega (`game.omega`)

| Value | fidelity | evidence_support | manipulation |
|---|---|---|---|
| main run | negligible | negligible | improved |
| 0.25 | negligible (+3.3%) | negligible (+3.7%) | improved (-41.2%) |
| 0.5 | negligible (+3.6%) | negligible (+4.3%) | improved (-44.4%) |
| 0.75 | improved (+27.8%) | improved (+28.6%) | improved (-71.0%) |
| 0.9* | improved (+50.0%) | improved (+57.2%) | improved (-44.5%) |

Robust: fidelity no, evidence_support no, manipulation yes

