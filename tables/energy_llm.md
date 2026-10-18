# Energy — LLM agents: baseline vs ablation vs proposed

Model `qwen2.5:7b` (digest `845dbda0ea48`); n = 5 paired seeds; mean ± SD over seeds; all rounds, all agents. Prompt style `raw`, private-gain weight 0.5.
Model calls: 15000; unusable replies: 0; reports replaced by the tool's report: 0.
With n = 5 a Wilcoxon test cannot give p < 0.0625; rows tested that way are not significant by construction.

| Metric | Baseline | Ablation | Proposed |
|---|---|---|---|
| fidelity | 0.446 ± 0.013 | 0.452 ± 0.008 | 0.461 ± 0.003 |
| evidence_support | 0.521 ± 0.019 | 0.512 ± 0.013 | 0.519 ± 0.015 |
| manipulation | 0.276 ± 0.003 | 0.241 ± 0.007 | 0.241 ± 0.005 |
| votes_against_tool | 0.111 ± 0.009 | 0.093 ± 0.011 | 0.102 ± 0.011 |
| confidence_inflation | 0.177 ± 0.004 | 0.031 ± 0.005 | 0.033 ± 0.005 |
| mean_confidence | 0.873 ± 0.001 | 0.734 ± 0.003 | 0.734 ± 0.004 |
| votes_own_preferred_option | 0.397 ± 0.018 | 0.395 ± 0.021 | 0.404 ± 0.020 |
| fully_truthful_explanation | 0.073 ± 0.007 | 0.077 ± 0.008 | 0.074 ± 0.007 |
| fully_supported_evidence | 0.286 ± 0.017 | 0.272 ± 0.010 | 0.280 ± 0.016 |
| component_false_attribution | 0.554 ± 0.013 | 0.548 ± 0.008 | 0.539 ± 0.003 |
| component_unsupported_evidence | 0.479 ± 0.019 | 0.488 ± 0.013 | 0.481 ± 0.015 |
| component_strategic_voting | 0.111 ± 0.009 | 0.093 ± 0.011 | 0.102 ± 0.011 |
| component_collusion | 0.058 ± 0.007 | 0.045 ± 0.011 | 0.051 ± 0.011 |
| collective_accuracy | 0.776 ± 0.034 | 0.773 ± 0.030 | 0.769 ± 0.032 |
| manipulation_success | 0.041 ± 0.016 | 0.034 ± 0.016 | 0.043 ± 0.018 |

## proposed vs baseline

| Metric | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.015 | [+0.002, +0.029] | +3.4% | paired t-test | 0.0365 | 0.0730 | cohen_dz = 1.38 | negligible |
| evidence_support | -0.002 | [-0.019, +0.016] | -0.3% | paired t-test | 0.8122 | 0.8122 | cohen_dz = -0.11 | negligible |
| manipulation | -0.035 | [-0.038, -0.031] | -12.6% | paired t-test | 0.0000 | 0.0000 | cohen_dz = -12.34 | improved |
| votes_against_tool (secondary) | -0.010 | [-0.018, -0.002] | -8.8% | paired t-test | 0.0244 | nan | cohen_dz = -1.58 | — |
| confidence_inflation (secondary) | -0.144 | [-0.151, -0.137] | -81.1% | paired t-test | 0.0000 | nan | cohen_dz = -26.61 | — |
| mean_confidence (secondary) | -0.140 | [-0.143, -0.136] | -16.0% | paired t-test | 0.0000 | nan | cohen_dz = -50.03 | — |
| votes_own_preferred_option (secondary) | +0.007 | [+0.001, +0.012] | +1.7% | paired t-test | 0.0249 | nan | cohen_dz = 1.56 | — |
| fully_truthful_explanation (secondary) | +0.001 | [-0.005, +0.007] | +0.8% | paired t-test | 0.7927 | nan | cohen_dz = 0.13 | — |
| fully_supported_evidence (secondary) | -0.006 | [-0.018, +0.003] | -2.0% | Wilcoxon signed-rank | 0.6250 | nan | rank_biserial = -0.33 | — |
| component_false_attribution (secondary) | -0.015 | [-0.029, -0.002] | -2.8% | paired t-test | 0.0365 | nan | cohen_dz = -1.38 | — |
| component_unsupported_evidence (secondary) | +0.002 | [-0.016, +0.019] | +0.3% | paired t-test | 0.8122 | nan | cohen_dz = 0.11 | — |
| component_strategic_voting (secondary) | -0.010 | [-0.018, -0.002] | -8.8% | paired t-test | 0.0244 | nan | cohen_dz = -1.58 | — |
| component_collusion (secondary) | -0.007 | [-0.015, +0.002] | -11.4% | paired t-test | 0.0934 | nan | cohen_dz = -0.98 | — |
| collective_accuracy (secondary) | -0.007 | [-0.017, +0.003] | -0.9% | paired t-test | 0.1347 | nan | cohen_dz = -0.84 | — |
| manipulation_success (secondary) | +0.002 | [-0.002, +0.005] | +4.9% | Wilcoxon signed-rank | 0.6250 | nan | rank_biserial = 0.50 | — |

## ablation vs baseline

| Metric | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Effect | Verdict |
|---|---|---|---|---|---|---|---|---|
| fidelity | +0.006 | [-0.009, +0.021] | +1.4% | paired t-test | 0.3089 | 0.4228 | cohen_dz = 0.52 | negligible |
| evidence_support | -0.009 | [-0.025, +0.008] | -1.7% | paired t-test | 0.2114 | 0.4228 | cohen_dz = -0.66 | negligible |
| manipulation | -0.035 | [-0.041, -0.030] | -12.7% | paired t-test | 0.0001 | 0.0002 | cohen_dz = -7.90 | improved |
| votes_against_tool (secondary) | -0.019 | [-0.029, -0.012] | -16.7% | Wilcoxon signed-rank | 0.0625 | nan | rank_biserial = -1.00 | — |
| confidence_inflation (secondary) | -0.146 | [-0.153, -0.139] | -82.4% | paired t-test | 0.0000 | nan | cohen_dz = -24.92 | — |
| mean_confidence (secondary) | -0.139 | [-0.142, -0.136] | -15.9% | paired t-test | 0.0000 | nan | cohen_dz = -54.89 | — |
| votes_own_preferred_option (secondary) | -0.002 | [-0.013, +0.009] | -0.5% | paired t-test | 0.6433 | nan | cohen_dz = -0.22 | — |
| fully_truthful_explanation (secondary) | +0.003 | [-0.005, +0.011] | +4.6% | paired t-test | 0.3048 | nan | cohen_dz = 0.53 | — |
| fully_supported_evidence (secondary) | -0.014 | [-0.030, +0.002] | -4.9% | paired t-test | 0.0763 | nan | cohen_dz = -1.06 | — |
| component_false_attribution (secondary) | -0.006 | [-0.021, +0.009] | -1.1% | paired t-test | 0.3089 | nan | cohen_dz = -0.52 | — |
| component_unsupported_evidence (secondary) | +0.009 | [-0.008, +0.025] | +1.8% | paired t-test | 0.2114 | nan | cohen_dz = 0.66 | — |
| component_strategic_voting (secondary) | -0.019 | [-0.029, -0.012] | -16.7% | Wilcoxon signed-rank | 0.0625 | nan | rank_biserial = -1.00 | — |
| component_collusion (secondary) | -0.013 | [-0.020, -0.009] | -22.8% | Wilcoxon signed-rank | 0.0625 | nan | rank_biserial = -1.00 | — |
| collective_accuracy (secondary) | -0.003 | [-0.022, +0.016] | -0.4% | paired t-test | 0.6827 | nan | cohen_dz = -0.20 | — |
| manipulation_success (secondary) | -0.007 | [-0.016, +0.002] | -17.1% | paired t-test | 0.1079 | nan | cohen_dz = -0.92 | — |

Verdicts (proposed vs baseline): {'fidelity': 'negligible', 'evidence_support': 'negligible', 'manipulation': 'improved'}

## Robustness (n = 3 seeds, first 100 rounds; descriptive only)

Scripted malicious agents among LLM agents. Share 0 = same rounds of the main run.

| System | acc. at 0.0 | acc. at 0.2 | acc. at 0.4 |
|---|---|---|---|
| baseline | 0.813 ± 0.080 | 0.800 ± 0.056 | 0.783 ± 0.055 |
| proposed | 0.820 ± 0.075 | 0.823 ± 0.065 | 0.800 ± 0.056 |

H4: mean degradation, proposed − baseline = -0.013 (95% CI [-0.064, +0.037], paired t-test, p = 0.3715). Negative = proposed degrades less. Three seeds: no confirmatory claim.

### LLM agents' own reports under attack

| System | Share | Fidelity | Evidence | Manipulation |
|---|---|---|---|---|
| baseline | 0.2 | 0.450 ± 0.020 | 0.533 ± 0.040 | 0.277 ± 0.005 |
| baseline | 0.4 | 0.500 ± 0.024 | 0.489 ± 0.030 | 0.279 ± 0.008 |
| proposed | 0.2 | 0.456 ± 0.019 | 0.520 ± 0.022 | 0.244 ± 0.006 |
| proposed | 0.4 | 0.506 ± 0.031 | 0.488 ± 0.026 | 0.244 ± 0.004 |

### Collusion (2 scripted colluders + 3 LLM agents)

| System | Quantity | Value |
|---|---|---|
| baseline | accuracy_without | 0.813 ± 0.080 |
| baseline | accuracy_with | 0.787 ± 0.038 |
| baseline | manipulation_success_with | 0.127 ± 0.025 |
| baseline | colluders_reward | 0.383 ± 0.016 |
| baseline | colluders_payoff | 0.527 ± 0.016 |
| baseline | colluders_private_utility | 0.671 ± 0.046 |
| baseline | llm_agents_reward | 0.639 ± 0.004 |
| baseline | llm_agents_payoff | 0.646 ± 0.010 |
| proposed | accuracy_without | 0.820 ± 0.075 |
| proposed | accuracy_with | 0.790 ± 0.062 |
| proposed | manipulation_success_with | 0.080 ± 0.010 |
| proposed | colluders_reward | 0.071 ± 0.033 |
| proposed | colluders_payoff | 0.342 ± 0.025 |
| proposed | colluders_private_utility | 0.614 ± 0.021 |
| proposed | llm_agents_reward | 0.749 ± 0.010 |
| proposed | llm_agents_payoff | 0.712 ± 0.008 |
| proposed | colluders_final_reputation | 0.044 ± 0.062 |
