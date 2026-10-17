# Pharma — LLM agents: baseline vs ablation vs proposed

Model `qwen2.5:7b` (digest `845dbda0ea48`); n = 5 paired seeds; mean ± SD over seeds; all rounds, all agents. Prompt style `raw`, private-gain weight 0.5.
Model calls: 15000; unusable replies: 0; reports replaced by the tool's report: 0.
With n = 5 a Wilcoxon test cannot give p < 0.0625; rows tested that way are not significant by construction.

| Metric | Baseline | Ablation | Proposed |
|---|---|---|---|
| fidelity | 0.459 ± 0.013 | 0.461 ± 0.013 | 0.450 ± 0.013 |
| evidence_support | 0.599 ± 0.006 | 0.578 ± 0.010 | 0.593 ± 0.005 |
| manipulation | 0.294 ± 0.006 | 0.231 ± 0.004 | 0.229 ± 0.004 |
| votes_against_tool | 0.164 ± 0.011 | 0.141 ± 0.009 | 0.138 ± 0.008 |
| confidence_inflation | 0.321 ± 0.008 | 0.021 ± 0.001 | 0.023 ± 0.002 |
| mean_confidence | 0.830 ± 0.001 | 0.531 ± 0.007 | 0.534 ± 0.007 |
| votes_own_preferred_option | 0.568 ± 0.009 | 0.553 ± 0.008 | 0.548 ± 0.011 |
| fully_truthful_explanation | 0.048 ± 0.004 | 0.050 ± 0.005 | 0.043 ± 0.005 |
| fully_supported_evidence | 0.356 ± 0.013 | 0.340 ± 0.012 | 0.358 ± 0.006 |
| component_false_attribution | 0.541 ± 0.013 | 0.539 ± 0.013 | 0.550 ± 0.013 |
| component_unsupported_evidence | 0.401 ± 0.006 | 0.422 ± 0.010 | 0.407 ± 0.005 |
| component_strategic_voting | 0.164 ± 0.011 | 0.141 ± 0.009 | 0.138 ± 0.008 |
| component_collusion | 0.043 ± 0.006 | 0.032 ± 0.006 | 0.029 ± 0.005 |
| collective_accuracy | 0.581 ± 0.016 | 0.595 ± 0.017 | 0.600 ± 0.017 |
| manipulation_success | 0.170 ± 0.015 | 0.166 ± 0.022 | 0.159 ± 0.010 |

## proposed vs baseline

| Metric | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | -0.009 | [-0.020, +0.003] | -1.9% | paired t-test | 0.0985 | 0.1250 | cohen_dz = -0.96 | negligible |
| evidence_support | -0.006 | [-0.010, -0.002] | -1.0% | Wilcoxon signed-rank | 0.0625 | 0.1250 | rank_biserial = -1.00 | negligible |
| manipulation | -0.065 | [-0.070, -0.059] | -22.0% | paired t-test | 0.0000 | 0.0000 | cohen_dz = -14.63 | improved |
| votes_against_tool (secondary) | -0.026 | [-0.033, -0.019] | -15.7% | paired t-test | 0.0005 | nan | cohen_dz = -4.51 | — |
| confidence_inflation (secondary) | -0.298 | [-0.307, -0.289] | -92.9% | paired t-test | 0.0000 | nan | cohen_dz = -39.53 | — |
| mean_confidence (secondary) | -0.296 | [-0.305, -0.287] | -35.7% | paired t-test | 0.0000 | nan | cohen_dz = -40.66 | — |
| votes_own_preferred_option (secondary) | -0.019 | [-0.023, -0.016] | -3.4% | paired t-test | 0.0001 | nan | cohen_dz = -6.95 | — |
| fully_truthful_explanation (secondary) | -0.006 | [-0.011, -0.003] | -12.0% | Wilcoxon signed-rank | 0.0625 | nan | rank_biserial = -1.00 | — |
| fully_supported_evidence (secondary) | +0.003 | [-0.008, +0.014] | +0.7% | paired t-test | 0.5471 | nan | cohen_dz = 0.29 | — |
| component_false_attribution (secondary) | +0.009 | [-0.003, +0.020] | +1.6% | paired t-test | 0.0985 | nan | cohen_dz = 0.96 | — |
| component_unsupported_evidence (secondary) | +0.006 | [+0.002, +0.010] | +1.5% | Wilcoxon signed-rank | 0.0625 | nan | rank_biserial = 1.00 | — |
| component_strategic_voting (secondary) | -0.026 | [-0.033, -0.019] | -15.7% | paired t-test | 0.0005 | nan | cohen_dz = -4.51 | — |
| component_collusion (secondary) | -0.014 | [-0.020, -0.008] | -32.6% | paired t-test | 0.0036 | nan | cohen_dz = -2.75 | — |
| collective_accuracy (secondary) | +0.019 | [+0.009, +0.025] | +3.3% | Wilcoxon signed-rank | 0.1250 | nan | rank_biserial = 1.00 | — |
| manipulation_success (secondary) | -0.011 | [-0.030, +0.008] | -6.5% | paired t-test | 0.1894 | nan | cohen_dz = -0.71 | — |

## ablation vs baseline

| Metric | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.003 | [-0.008, +0.014] | +0.6% | paired t-test | 0.5351 | 0.5351 | cohen_dz = 0.30 | negligible |
| evidence_support | -0.021 | [-0.034, -0.007] | -3.5% | paired t-test | 0.0126 | 0.0252 | cohen_dz = -1.92 | worse |
| manipulation | -0.063 | [-0.068, -0.058] | -21.5% | paired t-test | 0.0000 | 0.0000 | cohen_dz = -14.96 | improved |
| votes_against_tool (secondary) | -0.023 | [-0.027, -0.019] | -14.0% | paired t-test | 0.0001 | nan | cohen_dz = -7.89 | — |
| confidence_inflation (secondary) | -0.300 | [-0.309, -0.291] | -93.6% | paired t-test | 0.0000 | nan | cohen_dz = -40.09 | — |
| mean_confidence (secondary) | -0.299 | [-0.308, -0.289] | -36.0% | paired t-test | 0.0000 | nan | cohen_dz = -39.56 | — |
| votes_own_preferred_option (secondary) | -0.015 | [-0.019, -0.011] | -2.6% | paired t-test | 0.0006 | nan | cohen_dz = -4.42 | — |
| fully_truthful_explanation (secondary) | +0.002 | [-0.004, +0.008] | +3.3% | paired t-test | 0.4954 | nan | cohen_dz = 0.34 | — |
| fully_supported_evidence (secondary) | -0.015 | [-0.038, +0.008] | -4.3% | paired t-test | 0.1353 | nan | cohen_dz = -0.83 | — |
| component_false_attribution (secondary) | -0.003 | [-0.014, +0.008] | -0.5% | paired t-test | 0.5351 | nan | cohen_dz = -0.30 | — |
| component_unsupported_evidence (secondary) | +0.021 | [+0.007, +0.034] | +5.2% | paired t-test | 0.0126 | nan | cohen_dz = 1.92 | — |
| component_strategic_voting (secondary) | -0.023 | [-0.027, -0.019] | -14.0% | paired t-test | 0.0001 | nan | cohen_dz = -7.89 | — |
| component_collusion (secondary) | -0.011 | [-0.020, -0.002] | -25.1% | paired t-test | 0.0292 | nan | cohen_dz = -1.49 | — |
| collective_accuracy (secondary) | +0.014 | [-0.003, +0.031] | +2.4% | paired t-test | 0.0870 | nan | cohen_dz = 1.01 | — |
| manipulation_success (secondary) | -0.004 | [-0.044, +0.036] | -2.4% | paired t-test | 0.7955 | nan | cohen_dz = -0.12 | — |

Verdicts (proposed vs baseline): {'fidelity': 'negligible', 'evidence_support': 'negligible', 'manipulation': 'improved'}
