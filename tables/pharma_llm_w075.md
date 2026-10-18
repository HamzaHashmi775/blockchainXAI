# Pharma — LLM agents: baseline vs ablation vs proposed

Model `qwen2.5:7b` (digest `845dbda0ea48`); n = 5 paired seeds; mean ± SD over seeds; all rounds, all agents. Prompt style `raw`, private-gain weight 0.75.
Model calls: 15000; unusable replies: 0; reports replaced by the tool's report: 0.
With n = 5 a Wilcoxon test cannot give p < 0.0625; rows tested that way are not significant by construction.

| Metric | Baseline | Ablation | Proposed |
|---|---|---|---|
| fidelity | 0.456 ± 0.013 | 0.456 ± 0.009 | 0.450 ± 0.010 |
| evidence_support | 0.591 ± 0.013 | 0.574 ± 0.006 | 0.586 ± 0.011 |
| manipulation | 0.306 ± 0.004 | 0.242 ± 0.002 | 0.238 ± 0.003 |
| votes_against_tool | 0.186 ± 0.012 | 0.169 ± 0.007 | 0.160 ± 0.008 |
| confidence_inflation | 0.337 ± 0.007 | 0.026 ± 0.002 | 0.027 ± 0.002 |
| mean_confidence | 0.842 ± 0.002 | 0.532 ± 0.008 | 0.535 ± 0.006 |
| votes_own_preferred_option | 0.584 ± 0.013 | 0.573 ± 0.011 | 0.569 ± 0.011 |
| fully_truthful_explanation | 0.051 ± 0.002 | 0.050 ± 0.004 | 0.048 ± 0.005 |
| fully_supported_evidence | 0.347 ± 0.019 | 0.331 ± 0.004 | 0.346 ± 0.012 |
| component_false_attribution | 0.544 ± 0.013 | 0.544 ± 0.009 | 0.550 ± 0.010 |
| component_unsupported_evidence | 0.409 ± 0.013 | 0.426 ± 0.006 | 0.414 ± 0.011 |
| component_strategic_voting | 0.186 ± 0.012 | 0.169 ± 0.007 | 0.160 ± 0.008 |
| component_collusion | 0.053 ± 0.006 | 0.045 ± 0.009 | 0.038 ± 0.011 |
| collective_accuracy | 0.592 ± 0.020 | 0.608 ± 0.013 | 0.590 ± 0.017 |
| manipulation_success | 0.188 ± 0.027 | 0.197 ± 0.012 | 0.185 ± 0.016 |

## proposed vs baseline

| Metric | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | -0.007 | [-0.019, +0.006] | -1.4% | paired t-test | 0.2297 | 0.3144 | cohen_dz = -0.63 | negligible |
| evidence_support | -0.005 | [-0.013, +0.003] | -0.9% | paired t-test | 0.1572 | 0.3144 | cohen_dz = -0.78 | negligible |
| manipulation | -0.068 | [-0.072, -0.063] | -22.2% | paired t-test | 0.0000 | 0.0000 | cohen_dz = -18.33 | improved |
| votes_against_tool (secondary) | -0.026 | [-0.032, -0.022] | -13.9% | Wilcoxon signed-rank | 0.0625 | nan | rank_biserial = -1.00 | — |
| confidence_inflation (secondary) | -0.309 | [-0.316, -0.303] | -91.9% | paired t-test | 0.0000 | nan | cohen_dz = -57.34 | — |
| mean_confidence (secondary) | -0.307 | [-0.313, -0.301] | -36.5% | paired t-test | 0.0000 | nan | cohen_dz = -67.04 | — |
| votes_own_preferred_option (secondary) | -0.015 | [-0.020, -0.011] | -2.6% | paired t-test | 0.0007 | nan | cohen_dz = -4.22 | — |
| fully_truthful_explanation (secondary) | -0.003 | [-0.010, +0.004] | -5.5% | paired t-test | 0.3383 | nan | cohen_dz = -0.49 | — |
| fully_supported_evidence (secondary) | -0.000 | [-0.018, +0.017] | -0.1% | paired t-test | 0.9519 | nan | cohen_dz = -0.03 | — |
| component_false_attribution (secondary) | +0.007 | [-0.006, +0.019] | +1.2% | paired t-test | 0.2297 | nan | cohen_dz = 0.63 | — |
| component_unsupported_evidence (secondary) | +0.005 | [-0.003, +0.013] | +1.2% | paired t-test | 0.1572 | nan | cohen_dz = 0.78 | — |
| component_strategic_voting (secondary) | -0.026 | [-0.032, -0.022] | -13.9% | Wilcoxon signed-rank | 0.0625 | nan | rank_biserial = -1.00 | — |
| component_collusion (secondary) | -0.015 | [-0.025, -0.005] | -28.5% | paired t-test | 0.0136 | nan | cohen_dz = -1.88 | — |
| collective_accuracy (secondary) | -0.002 | [-0.028, +0.024] | -0.3% | paired t-test | 0.8425 | nan | cohen_dz = -0.09 | — |
| manipulation_success (secondary) | -0.003 | [-0.047, +0.041] | -1.6% | paired t-test | 0.8585 | nan | cohen_dz = -0.09 | — |

## ablation vs baseline

| Metric | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | -0.001 | [-0.013, +0.011] | -0.2% | paired t-test | 0.8718 | 0.8718 | cohen_dz = -0.08 | negligible |
| evidence_support | -0.017 | [-0.029, -0.006] | -2.9% | paired t-test | 0.0141 | 0.0283 | cohen_dz = -1.86 | worse |
| manipulation | -0.064 | [-0.069, -0.058] | -20.8% | paired t-test | 0.0000 | 0.0000 | cohen_dz = -14.51 | improved |
| votes_against_tool (secondary) | -0.017 | [-0.025, -0.010] | -9.4% | paired t-test | 0.0036 | nan | cohen_dz = -2.74 | — |
| confidence_inflation (secondary) | -0.311 | [-0.318, -0.303] | -92.2% | paired t-test | 0.0000 | nan | cohen_dz = -50.82 | — |
| mean_confidence (secondary) | -0.309 | [-0.317, -0.301] | -36.7% | paired t-test | 0.0000 | nan | cohen_dz = -49.97 | — |
| votes_own_preferred_option (secondary) | -0.011 | [-0.018, -0.003] | -1.8% | paired t-test | 0.0156 | nan | cohen_dz = -1.81 | — |
| fully_truthful_explanation (secondary) | -0.000 | [-0.007, +0.006] | -0.8% | paired t-test | 0.8746 | nan | cohen_dz = -0.08 | — |
| fully_supported_evidence (secondary) | -0.015 | [-0.038, +0.008] | -4.4% | paired t-test | 0.1371 | nan | cohen_dz = -0.83 | — |
| component_false_attribution (secondary) | +0.001 | [-0.011, +0.013] | +0.1% | paired t-test | 0.8718 | nan | cohen_dz = 0.08 | — |
| component_unsupported_evidence (secondary) | +0.017 | [+0.006, +0.029] | +4.2% | paired t-test | 0.0141 | nan | cohen_dz = 1.86 | — |
| component_strategic_voting (secondary) | -0.017 | [-0.025, -0.010] | -9.4% | paired t-test | 0.0036 | nan | cohen_dz = -2.74 | — |
| component_collusion (secondary) | -0.007 | [-0.015, +0.000] | -14.1% | paired t-test | 0.0556 | nan | cohen_dz = -1.20 | — |
| collective_accuracy (secondary) | +0.016 | [-0.002, +0.034] | +2.7% | paired t-test | 0.0723 | nan | cohen_dz = 1.08 | — |
| manipulation_success (secondary) | +0.009 | [-0.011, +0.021] | +4.8% | Wilcoxon signed-rank | 0.5625 | nan | rank_biserial = 0.33 | — |

Verdicts (proposed vs baseline): {'fidelity': 'negligible', 'evidence_support': 'negligible', 'manipulation': 'improved'}
