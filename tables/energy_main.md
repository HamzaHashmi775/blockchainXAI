# Energy — baseline vs ablation vs proposed

n = 10 paired seeds; mean ± SD over seeds; metrics averaged over agents and the evaluation window.

| Metric | Baseline | Ablation | Proposed |
|---|---|---|---|
| fidelity | 0.936 ± 0.024 | 0.970 ± 0.003 | 0.970 ± 0.004 |
| evidence_support | 0.926 ± 0.031 | 0.967 ± 0.004 | 0.966 ± 0.004 |
| manipulation | 0.066 ± 0.017 | 0.035 ± 0.004 | 0.036 ± 0.005 |
| collective_accuracy | 0.744 ± 0.019 | 0.753 ± 0.016 | 0.754 ± 0.013 |
| collective_utility | 0.626 ± 0.004 | 0.624 ± 0.003 | 0.624 ± 0.003 |
| decision_quality | 0.672 ± 0.018 | 0.694 ± 0.014 | 0.691 ± 0.012 |
| manipulation_success | 0.050 ± 0.017 | 0.022 ± 0.008 | 0.025 ± 0.012 |
| consistency | 0.560 ± 0.021 | 0.610 ± 0.014 | 0.608 ± 0.010 |

## proposed vs baseline

| Metric | Δ mean | 95% CI | Rel. impr. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.034 | [+0.021, +0.050] | +3.6% | Wilcoxon signed-rank | 0.0020 | 0.0039 | rank_biserial = 1.00 | negligible |
| evidence_support | +0.040 | [+0.017, +0.063] | +4.3% | paired t-test | 0.0033 | 0.0039 | cohen_dz = 1.25 | negligible |
| manipulation | -0.029 | [-0.043, -0.016] | -44.4% | paired t-test | 0.0009 | 0.0026 | cohen_dz = -1.55 | improved |
| collective_accuracy | +0.009 | [-0.000, +0.019] | +1.2% | paired t-test | 0.0541 | nan | cohen_dz = 0.70 | — |
| collective_utility | -0.003 | [-0.004, -0.001] | -0.4% | paired t-test | 0.0063 | nan | cohen_dz = -1.12 | — |
| decision_quality | +0.019 | [+0.009, +0.028] | +2.8% | paired t-test | 0.0017 | nan | cohen_dz = 1.39 | — |
| manipulation_success | -0.025 | [-0.037, -0.012] | -49.4% | paired t-test | 0.0015 | nan | cohen_dz = -1.42 | — |
| consistency | +0.048 | [+0.031, +0.065] | +8.6% | paired t-test | 0.0001 | nan | cohen_dz = 2.05 | — |

## ablation vs baseline

| Metric | Δ mean | 95% CI | Rel. impr. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.033 | [+0.016, +0.050] | +3.5% | paired t-test | 0.0018 | 0.0037 | cohen_dz = 1.38 | negligible |
| evidence_support | +0.041 | [+0.017, +0.064] | +4.4% | paired t-test | 0.0033 | 0.0037 | cohen_dz = 1.25 | negligible |
| manipulation | -0.030 | [-0.043, -0.018] | -46.2% | paired t-test | 0.0004 | 0.0013 | cohen_dz = -1.70 | improved |
| collective_accuracy | +0.009 | [-0.003, +0.020] | +1.2% | paired t-test | 0.1171 | nan | cohen_dz = 0.55 | — |
| collective_utility | -0.002 | [-0.004, -0.000] | -0.3% | paired t-test | 0.0279 | nan | cohen_dz = -0.83 | — |
| decision_quality | +0.022 | [+0.013, +0.032] | +3.3% | paired t-test | 0.0004 | nan | cohen_dz = 1.76 | — |
| manipulation_success | -0.029 | [-0.043, -0.014] | -57.0% | paired t-test | 0.0015 | nan | cohen_dz = -1.41 | — |
| consistency | +0.050 | [+0.034, +0.066] | +8.9% | paired t-test | 0.0001 | nan | cohen_dz = 2.18 | — |

## Learned strategy shares (evaluation window)

| System | honest | strategic | misattributing | overclaiming | manipulative |
|---|---|---|---|---|---|
| baseline | 0.775 ± 0.045 | 0.075 ± 0.023 | 0.049 ± 0.025 | 0.054 ± 0.019 | 0.047 ± 0.026 |
| ablation | 0.883 ± 0.037 | 0.044 ± 0.034 | 0.028 ± 0.007 | 0.024 ± 0.005 | 0.021 ± 0.002 |
| proposed | 0.876 ± 0.032 | 0.054 ± 0.028 | 0.024 ± 0.006 | 0.025 ± 0.005 | 0.021 ± 0.003 |

## Unilateral deviation from all-honest (mean payoff over seeds)

| System | Agent | honest | strategic | misattributing | overclaiming | manipulative | best | honest best in seeds |
|---|---|---|---|---|---|---|---|---|
| baseline | consumer | 0.520 | 0.412 | 0.412 | 0.412 | 0.406 | honest | 10/10 |
| baseline | grid | 0.578 | 0.465 | 0.465 | 0.465 | 0.464 | honest | 10/10 |
| baseline | market | 0.540 | 0.440 | 0.440 | 0.440 | 0.442 | honest | 10/10 |
| baseline | producer | 0.539 | 0.450 | 0.450 | 0.450 | 0.453 | honest | 10/10 |
| baseline | storage | 0.669 | 0.619 | 0.619 | 0.619 | 0.626 | honest | 10/10 |
| ablation | consumer | 0.520 | 0.400 | 0.345 | 0.346 | 0.292 | honest | 10/10 |
| ablation | grid | 0.578 | 0.454 | 0.393 | 0.397 | 0.328 | honest | 10/10 |
| ablation | market | 0.540 | 0.419 | 0.394 | 0.386 | 0.293 | honest | 10/10 |
| ablation | producer | 0.539 | 0.435 | 0.405 | 0.402 | 0.300 | honest | 10/10 |
| ablation | storage | 0.669 | 0.616 | 0.452 | 0.449 | 0.397 | honest | 10/10 |
| proposed | consumer | 0.518 | 0.394 | 0.337 | 0.338 | 0.281 | honest | 10/10 |
| proposed | grid | 0.576 | 0.447 | 0.384 | 0.387 | 0.319 | honest | 10/10 |
| proposed | market | 0.542 | 0.414 | 0.389 | 0.380 | 0.285 | honest | 10/10 |
| proposed | producer | 0.541 | 0.428 | 0.396 | 0.394 | 0.288 | honest | 10/10 |
| proposed | storage | 0.668 | 0.615 | 0.439 | 0.437 | 0.376 | honest | 10/10 |

Checkpoint verdicts (proposed vs baseline): {'fidelity': 'negligible', 'evidence_support': 'negligible', 'manipulation': 'improved'}; continue = True
