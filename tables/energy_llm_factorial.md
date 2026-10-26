# 2×2 wording × payoff (energy, LLM agents) — added, post hoc experiment

n = 5 paired seeds; ω = 0.5; audit checks shown in all cells. A, B, C from one Kaggle session; D from a later session (amendment 8). Model calls: 20000; unusable replies: 0.

| Outcome | A (base words, base pay) | B (prop. words, base pay) | C (prop. words, prop. pay) | D (base words, prop. pay) |
|---|---|---|---|---|
| mean_confidence | 0.898 ± 0.003 | 0.730 ± 0.004 | 0.734 ± 0.004 | 0.895 ± 0.002 |
| confidence_inflation | 0.203 ± 0.005 | 0.031 ± 0.001 | 0.032 ± 0.003 | 0.200 ± 0.004 |
| votes_against_tool | 0.117 ± 0.012 | 0.104 ± 0.007 | 0.098 ± 0.007 | 0.115 ± 0.012 |
| manipulation | 0.281 ± 0.004 | 0.243 ± 0.004 | 0.241 ± 0.004 | 0.276 ± 0.007 |
| fidelity | 0.459 ± 0.005 | 0.457 ± 0.005 | 0.458 ± 0.006 | 0.468 ± 0.009 |
| evidence_support | 0.519 ± 0.019 | 0.517 ± 0.011 | 0.514 ± 0.013 | 0.524 ± 0.013 |
| collective_accuracy | 0.782 ± 0.023 | 0.782 ± 0.035 | 0.772 ± 0.033 | 0.771 ± 0.024 |
| brier | 0.229 ± 0.016 | 0.179 ± 0.014 | 0.181 ± 0.015 | 0.226 ± 0.016 |
| overconfidence | 0.181 ± 0.020 | 0.000 ± 0.024 | 0.003 ± 0.028 | 0.174 ± 0.019 |
| share_votes_correct | 0.717 ± 0.022 | 0.730 ± 0.027 | 0.731 ± 0.029 | 0.720 ± 0.020 |

## Factorial effects on mean_confidence (confirmatory family of amendment 8)

| Effect | Δ | 95% CI | Test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|
| wording (main effect) | -0.164 | [-0.167, -0.161] | paired t-test | 0.0000 | 0.0000 | lower |
| payoff (main effect) | -0.000 | [-0.002, +0.002] | paired t-test | 0.9884 | 0.9884 | no detectable effect |
| interaction | +0.006 | [+0.004, +0.009] | paired t-test | 0.0023 | 0.0046 | detected |

D − A on mean_confidence: 95% CI [-0.005, -0.002]; pre-declared bound ±0.017 (10 % of the wording effect B − A): CI within the bound.

Replication of the pharma pattern (rule of amendment 8): **the pharma pattern replicates**.

Descriptive checks against energy_llm_main (same seeds and rounds):
- C_vs_original_proposed: mean_confidence Δ -0.000 (p 0.981); fidelity Δ -0.003 (p 0.221)
- A_vs_original_baseline: mean_confidence Δ +0.025 (p 0.000); fidelity Δ +0.013 (p 0.030)

## Simple contrasts and factorial effects, all outcomes (secondary, unadjusted)

| Outcome | Contrast | Δ | 95% CI | p |
|---|---|---|---|---|
| mean_confidence | D_vs_A (payoff, baseline wording) | -0.003 | [-0.005, -0.002] | 0.0034 |
| mean_confidence | C_vs_B (payoff, proposed wording) | +0.003 | [+0.001, +0.006] | 0.0251 |
| mean_confidence | B_vs_A (wording, baseline payoff) | -0.167 | [-0.170, -0.165] | 0.0000 |
| mean_confidence | C_vs_D (wording, proposed payoff) | -0.161 | [-0.165, -0.157] | 0.0000 |
| mean_confidence | wording (main effect) | -0.164 | [-0.167, -0.161] | 0.0000 |
| mean_confidence | payoff (main effect) | -0.000 | [-0.002, +0.002] | 0.9884 |
| mean_confidence | interaction | +0.006 | [+0.004, +0.009] | 0.0023 |
| confidence_inflation | D_vs_A (payoff, baseline wording) | -0.003 | [-0.005, -0.002] | 0.0070 |
| confidence_inflation | C_vs_B (payoff, proposed wording) | +0.001 | [-0.004, +0.005] | 0.6085 |
| confidence_inflation | B_vs_A (wording, baseline payoff) | -0.172 | [-0.179, -0.166] | 0.0000 |
| confidence_inflation | C_vs_D (wording, proposed payoff) | -0.168 | [-0.171, -0.165] | 0.0000 |
| confidence_inflation | wording (main effect) | -0.170 | [-0.174, -0.166] | 0.0000 |
| confidence_inflation | payoff (main effect) | -0.001 | [-0.003, +0.000] | 0.0568 |
| confidence_inflation | interaction | +0.004 | [-0.002, +0.011] | 0.1312 |
| votes_against_tool | D_vs_A (payoff, baseline wording) | -0.002 | [-0.010, +0.006] | 0.5371 |
| votes_against_tool | C_vs_B (payoff, proposed wording) | -0.005 | [-0.009, -0.002] | 0.0138 |
| votes_against_tool | B_vs_A (wording, baseline payoff) | -0.013 | [-0.024, -0.003] | 0.0233 |
| votes_against_tool | C_vs_D (wording, proposed payoff) | -0.017 | [-0.023, -0.011] | 0.0014 |
| votes_against_tool | wording (main effect) | -0.015 | [-0.022, -0.008] | 0.0041 |
| votes_against_tool | payoff (main effect) | -0.004 | [-0.008, +0.001] | 0.0779 |
| votes_against_tool | interaction | -0.003 | [-0.013, +0.006] | 0.3644 |
| manipulation | D_vs_A (payoff, baseline wording) | -0.005 | [-0.009, -0.000] | 0.0391 |
| manipulation | C_vs_B (payoff, proposed wording) | -0.002 | [-0.005, +0.002] | 0.2654 |
| manipulation | B_vs_A (wording, baseline payoff) | -0.038 | [-0.042, -0.034] | 0.0000 |
| manipulation | C_vs_D (wording, proposed payoff) | -0.035 | [-0.041, -0.029] | 0.0001 |
| manipulation | wording (main effect) | -0.037 | [-0.041, -0.032] | 0.0000 |
| manipulation | payoff (main effect) | -0.003 | [-0.007, +0.000] | 0.0683 |
| manipulation | interaction | +0.003 | [-0.000, +0.006] | 0.0535 |
| fidelity | D_vs_A (payoff, baseline wording) | +0.009 | [+0.003, +0.016] | 0.0189 |
| fidelity | C_vs_B (payoff, proposed wording) | +0.001 | [-0.003, +0.005] | 0.4856 |
| fidelity | B_vs_A (wording, baseline payoff) | -0.002 | [-0.013, +0.009] | 0.7013 |
| fidelity | C_vs_D (wording, proposed payoff) | -0.010 | [-0.022, +0.003] | 0.0928 |
| fidelity | wording (main effect) | -0.006 | [-0.017, +0.006] | 0.2306 |
| fidelity | payoff (main effect) | +0.005 | [+0.001, +0.010] | 0.0329 |
| fidelity | interaction | -0.008 | [-0.015, -0.002] | 0.0263 |
| evidence_support | D_vs_A (payoff, baseline wording) | +0.005 | [-0.005, +0.016] | 0.2332 |
| evidence_support | C_vs_B (payoff, proposed wording) | -0.002 | [-0.012, +0.007] | 0.5157 |
| evidence_support | B_vs_A (wording, baseline payoff) | -0.003 | [-0.016, +0.011] | 0.6369 |
| evidence_support | C_vs_D (wording, proposed payoff) | -0.010 | [-0.019, -0.001] | 0.0337 |
| evidence_support | wording (main effect) | -0.006 | [-0.014, +0.001] | 0.0668 |
| evidence_support | payoff (main effect) | +0.001 | [-0.003, +0.006] | 0.4325 |
| evidence_support | interaction | -0.008 | [-0.026, +0.010] | 0.2994 |
| collective_accuracy | D_vs_A (payoff, baseline wording) | -0.011 | [-0.020, -0.002] | 0.0295 |
| collective_accuracy | C_vs_B (payoff, proposed wording) | -0.010 | [-0.027, +0.007] | 0.1778 |
| collective_accuracy | B_vs_A (wording, baseline payoff) | -0.000 | [-0.021, +0.021] | 1.0000 |
| collective_accuracy | C_vs_D (wording, proposed payoff) | +0.001 | [-0.012, +0.014] | 0.8466 |
| collective_accuracy | wording (main effect) | +0.001 | [-0.014, +0.015] | 0.9264 |
| collective_accuracy | payoff (main effect) | -0.010 | [-0.019, -0.002] | 0.0277 |
| collective_accuracy | interaction | +0.001 | [-0.020, +0.022] | 0.9023 |
| brier | D_vs_A (payoff, baseline wording) | -0.003 | [-0.007, +0.000] | 0.0712 |
| brier | C_vs_B (payoff, proposed wording) | +0.001 | [-0.002, +0.005] | 0.3363 |
| brier | B_vs_A (wording, baseline payoff) | -0.050 | [-0.057, -0.043] | 0.0000 |
| brier | C_vs_D (wording, proposed payoff) | -0.045 | [-0.049, -0.041] | 0.0000 |
| brier | wording (main effect) | -0.047 | [-0.052, -0.042] | 0.0000 |
| brier | payoff (main effect) | -0.001 | [-0.004, +0.002] | 0.3907 |
| brier | interaction | +0.005 | [+0.001, +0.009] | 0.0354 |
| overconfidence | D_vs_A (payoff, baseline wording) | -0.007 | [-0.012, -0.001] | 0.0258 |
| overconfidence | C_vs_B (payoff, proposed wording) | +0.002 | [-0.003, +0.008] | 0.3127 |
| overconfidence | B_vs_A (wording, baseline payoff) | -0.181 | [-0.187, -0.174] | 0.0000 |
| overconfidence | C_vs_D (wording, proposed payoff) | -0.172 | [-0.184, -0.159] | 0.0000 |
| overconfidence | wording (main effect) | -0.176 | [-0.185, -0.167] | 0.0000 |
| overconfidence | payoff (main effect) | -0.002 | [-0.005, +0.001] | 0.1245 |
| overconfidence | interaction | +0.009 | [+0.000, +0.017] | 0.0459 |
| share_votes_correct | D_vs_A (payoff, baseline wording) | +0.003 | [-0.002, +0.009] | 0.1502 |
| share_votes_correct | C_vs_B (payoff, proposed wording) | +0.001 | [-0.003, +0.005] | 0.4975 |
| share_votes_correct | B_vs_A (wording, baseline payoff) | +0.013 | [+0.005, +0.022] | 0.0127 |
| share_votes_correct | C_vs_D (wording, proposed payoff) | +0.011 | [-0.003, +0.025] | 0.1022 |
| share_votes_correct | wording (main effect) | +0.012 | [+0.001, +0.023] | 0.0380 |
| share_votes_correct | payoff (main effect) | +0.002 | [+0.000, +0.004] | 0.0269 |
| share_votes_correct | interaction | -0.002 | [-0.011, +0.006] | 0.4744 |
