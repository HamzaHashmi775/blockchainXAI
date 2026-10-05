# Energy — baseline vs ablation vs proposed

n = 10 paired seeds; mean ± SD over seeds; metrics averaged over agents and the evaluation window.

| Metric | Baseline | Ablation | Proposed |
|---|---|---|---|
| fidelity | 0.908 ± 0.036 | 0.964 ± 0.004 | 0.965 ± 0.005 |
| evidence_support | 0.908 ± 0.036 | 0.964 ± 0.004 | 0.965 ± 0.005 |
| manipulation | 0.070 ± 0.020 | 0.035 ± 0.004 | 0.034 ± 0.004 |
| collective_accuracy | 0.745 ± 0.019 | 0.749 ± 0.015 | 0.752 ± 0.020 |
| collective_utility | 0.625 ± 0.004 | 0.624 ± 0.003 | 0.625 ± 0.003 |
| decision_quality | 0.684 ± 0.015 | 0.699 ± 0.012 | 0.698 ± 0.013 |
| manipulation_success | 0.046 ± 0.017 | 0.025 ± 0.009 | 0.021 ± 0.011 |
| consistency | 0.575 ± 0.028 | 0.622 ± 0.010 | 0.625 ± 0.011 |

## proposed vs baseline

| Metric | Δ mean | 95% CI | Rel. impr. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.057 | [+0.032, +0.082] | +6.3% | paired t-test | 0.0006 | 0.0015 | cohen_dz = 1.64 | improved |
| evidence_support | +0.057 | [+0.032, +0.082] | +6.3% | paired t-test | 0.0006 | 0.0015 | cohen_dz = 1.64 | improved |
| manipulation | -0.036 | [-0.051, -0.020] | -51.0% | paired t-test | 0.0005 | 0.0015 | cohen_dz = -1.67 | improved |
| collective_accuracy | +0.007 | [+0.000, +0.014] | +1.0% | paired t-test | 0.0414 | nan | cohen_dz = 0.75 | — |
| collective_utility | -0.000 | [-0.002, +0.001] | -0.1% | paired t-test | 0.6118 | nan | cohen_dz = -0.17 | — |
| decision_quality | +0.014 | [+0.005, +0.023] | +2.1% | paired t-test | 0.0066 | nan | cohen_dz = 1.11 | — |
| manipulation_success | -0.026 | [-0.040, -0.011] | -55.4% | paired t-test | 0.0027 | nan | cohen_dz = -1.29 | — |
| consistency | +0.050 | [+0.031, +0.068] | +8.6% | paired t-test | 0.0002 | nan | cohen_dz = 1.88 | — |

## ablation vs baseline

| Metric | Δ mean | 95% CI | Rel. impr. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.057 | [+0.031, +0.082] | +6.3% | paired t-test | 0.0007 | 0.0015 | cohen_dz = 1.60 | improved |
| evidence_support | +0.057 | [+0.031, +0.082] | +6.3% | paired t-test | 0.0007 | 0.0015 | cohen_dz = 1.60 | improved |
| manipulation | -0.035 | [-0.050, -0.020] | -50.2% | paired t-test | 0.0005 | 0.0015 | cohen_dz = -1.68 | improved |
| collective_accuracy | +0.004 | [-0.003, +0.011] | +0.5% | paired t-test | 0.2126 | nan | cohen_dz = 0.42 | — |
| collective_utility | -0.001 | [-0.003, +0.001] | -0.2% | paired t-test | 0.1377 | nan | cohen_dz = -0.52 | — |
| decision_quality | +0.015 | [+0.005, +0.024] | +2.1% | paired t-test | 0.0064 | nan | cohen_dz = 1.12 | — |
| manipulation_success | -0.021 | [-0.038, -0.005] | -45.9% | paired t-test | 0.0164 | nan | cohen_dz = -0.93 | — |
| consistency | +0.047 | [+0.026, +0.067] | +8.1% | paired t-test | 0.0006 | nan | cohen_dz = 1.63 | — |

## Learned strategy shares (evaluation window)

| System | honest | strategic | manipulative |
|---|---|---|---|
| baseline | 0.823 ± 0.061 | 0.085 ± 0.044 | 0.092 ± 0.036 |
| ablation | 0.885 ± 0.032 | 0.080 ± 0.032 | 0.036 ± 0.004 |
| proposed | 0.893 ± 0.029 | 0.072 ± 0.029 | 0.035 ± 0.005 |

## Unilateral deviation from all-honest (mean payoff over seeds)

| System | Agent | honest | strategic | manipulative | best | honest best in seeds |
|---|---|---|---|---|---|---|
| baseline | consumer | 0.520 | 0.412 | 0.406 | honest | 10/10 |
| baseline | grid | 0.578 | 0.465 | 0.464 | honest | 10/10 |
| baseline | market | 0.540 | 0.440 | 0.442 | honest | 10/10 |
| baseline | producer | 0.539 | 0.450 | 0.453 | honest | 10/10 |
| baseline | storage | 0.669 | 0.619 | 0.626 | honest | 10/10 |
| ablation | consumer | 0.520 | 0.400 | 0.292 | honest | 10/10 |
| ablation | grid | 0.578 | 0.454 | 0.328 | honest | 10/10 |
| ablation | market | 0.540 | 0.419 | 0.293 | honest | 10/10 |
| ablation | producer | 0.539 | 0.435 | 0.300 | honest | 10/10 |
| ablation | storage | 0.669 | 0.616 | 0.397 | honest | 10/10 |
| proposed | consumer | 0.518 | 0.394 | 0.281 | honest | 10/10 |
| proposed | grid | 0.576 | 0.447 | 0.319 | honest | 10/10 |
| proposed | market | 0.542 | 0.414 | 0.285 | honest | 10/10 |
| proposed | producer | 0.541 | 0.428 | 0.288 | honest | 10/10 |
| proposed | storage | 0.668 | 0.615 | 0.376 | honest | 10/10 |

Checkpoint verdicts (proposed vs baseline): {'fidelity': 'improved', 'evidence_support': 'improved', 'manipulation': 'improved'}; continue = True
