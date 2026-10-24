# 2×2 wording × payoff (pharma, LLM agents) — added, post hoc experiment

n = 5 paired seeds; ω = 0.5; audit checks shown in all cells. A, B, C from one Kaggle session; D from a later session (amendment 7). Model calls: 20000; unusable replies: 0.

| Outcome | A (base words, base pay) | B (prop. words, base pay) | C (prop. words, prop. pay) | D (base words, prop. pay) |
|---|---|---|---|---|
| mean_confidence | 0.831 ± 0.002 | 0.534 ± 0.007 | 0.534 ± 0.006 | 0.834 ± 0.002 |
| confidence_inflation | 0.323 ± 0.007 | 0.022 ± 0.001 | 0.022 ± 0.002 | 0.326 ± 0.007 |
| votes_against_tool | 0.169 ± 0.010 | 0.133 ± 0.011 | 0.134 ± 0.007 | 0.168 ± 0.010 |
| manipulation | 0.299 ± 0.005 | 0.225 ± 0.005 | 0.226 ± 0.005 | 0.299 ± 0.007 |
| fidelity | 0.445 ± 0.015 | 0.458 ± 0.010 | 0.456 ± 0.011 | 0.446 ± 0.016 |
| evidence_support | 0.598 ± 0.011 | 0.597 ± 0.010 | 0.597 ± 0.010 | 0.594 ± 0.014 |
| collective_accuracy | 0.576 ± 0.018 | 0.589 ± 0.015 | 0.589 ± 0.026 | 0.580 ± 0.012 |
| brier | 0.339 ± 0.004 | 0.226 ± 0.005 | 0.227 ± 0.007 | 0.340 ± 0.005 |
| overconfidence | 0.304 ± 0.008 | 0.011 ± 0.016 | 0.008 ± 0.015 | 0.309 ± 0.012 |
| share_votes_correct | 0.527 ± 0.009 | 0.524 ± 0.011 | 0.526 ± 0.010 | 0.525 ± 0.013 |

## Factorial effects on mean_confidence (confirmatory family of amendment 7)

| Effect | Δ | 95% CI | Test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|
| wording (main effect) | -0.299 | [-0.306, -0.291] | paired t-test | 0.0000 | 0.0000 | lower |
| payoff (main effect) | +0.001 | [+0.000, +0.002] | paired t-test | 0.0491 | 0.0971 | no detectable effect |
| interaction | -0.004 | [-0.008, -0.000] | paired t-test | 0.0485 | 0.0971 | not detected |

D − A on mean_confidence: 95% CI [+0.000, +0.006]; pre-declared bound ±0.030 (10 % of the wording effect B − A): CI within the bound.

## Simple contrasts and factorial effects, all outcomes (secondary, unadjusted)

| Outcome | Contrast | Δ | 95% CI | p |
|---|---|---|---|---|
| mean_confidence | D_vs_A (payoff, baseline wording) | +0.003 | [+0.000, +0.006] | 0.0421 |
| mean_confidence | C_vs_B (payoff, proposed wording) | -0.001 | [-0.002, +0.000] | 0.1508 |
| mean_confidence | B_vs_A (wording, baseline payoff) | -0.297 | [-0.305, -0.288] | 0.0000 |
| mean_confidence | C_vs_D (wording, proposed payoff) | -0.301 | [-0.308, -0.293] | 0.0000 |
| mean_confidence | wording (main effect) | -0.299 | [-0.306, -0.291] | 0.0000 |
| mean_confidence | payoff (main effect) | +0.001 | [+0.000, +0.002] | 0.0491 |
| mean_confidence | interaction | -0.004 | [-0.008, -0.000] | 0.0485 |
| confidence_inflation | D_vs_A (payoff, baseline wording) | +0.003 | [-0.001, +0.007] | 0.0895 |
| confidence_inflation | C_vs_B (payoff, proposed wording) | +0.000 | [-0.002, +0.002] | 0.9181 |
| confidence_inflation | B_vs_A (wording, baseline payoff) | -0.300 | [-0.309, -0.292] | 0.0000 |
| confidence_inflation | C_vs_D (wording, proposed payoff) | -0.303 | [-0.310, -0.296] | 0.0000 |
| confidence_inflation | wording (main effect) | -0.302 | [-0.310, -0.294] | 0.0000 |
| confidence_inflation | payoff (main effect) | +0.002 | [-0.001, +0.004] | 0.1530 |
| confidence_inflation | interaction | -0.003 | [-0.007, +0.001] | 0.0955 |
| votes_against_tool | D_vs_A (payoff, baseline wording) | -0.001 | [-0.007, +0.005] | 0.6864 |
| votes_against_tool | C_vs_B (payoff, proposed wording) | +0.001 | [-0.009, +0.010] | 0.8239 |
| votes_against_tool | B_vs_A (wording, baseline payoff) | -0.036 | [-0.039, -0.033] | 0.0000 |
| votes_against_tool | C_vs_D (wording, proposed payoff) | -0.034 | [-0.042, -0.026] | 0.0003 |
| votes_against_tool | wording (main effect) | -0.035 | [-0.039, -0.032] | 0.0000 |
| votes_against_tool | payoff (main effect) | -0.000 | [-0.006, +0.006] | 0.9674 |
| votes_against_tool | interaction | +0.002 | [-0.008, +0.011] | 0.6327 |
| manipulation | D_vs_A (payoff, baseline wording) | +0.001 | [-0.003, +0.004] | 0.6552 |
| manipulation | C_vs_B (payoff, proposed wording) | +0.001 | [-0.004, +0.006] | 0.7219 |
| manipulation | B_vs_A (wording, baseline payoff) | -0.073 | [-0.077, -0.069] | 0.0000 |
| manipulation | C_vs_D (wording, proposed payoff) | -0.073 | [-0.080, -0.067] | 0.0000 |
| manipulation | wording (main effect) | -0.073 | [-0.078, -0.069] | 0.0000 |
| manipulation | payoff (main effect) | +0.001 | [-0.002, +0.004] | 0.5916 |
| manipulation | interaction | +0.000 | [-0.006, +0.006] | 0.9690 |
| fidelity | D_vs_A (payoff, baseline wording) | +0.001 | [-0.006, +0.008] | 0.7376 |
| fidelity | C_vs_B (payoff, proposed wording) | -0.002 | [-0.006, +0.001] | 0.1339 |
| fidelity | B_vs_A (wording, baseline payoff) | +0.013 | [+0.009, +0.019] | 0.0625 |
| fidelity | C_vs_D (wording, proposed payoff) | +0.010 | [+0.001, +0.019] | 0.0368 |
| fidelity | wording (main effect) | +0.012 | [+0.004, +0.019] | 0.0112 |
| fidelity | payoff (main effect) | -0.001 | [-0.004, +0.002] | 0.5700 |
| fidelity | interaction | -0.003 | [-0.012, +0.006] | 0.3788 |
| evidence_support | D_vs_A (payoff, baseline wording) | -0.004 | [-0.015, +0.007] | 0.3563 |
| evidence_support | C_vs_B (payoff, proposed wording) | +0.000 | [-0.008, +0.008] | 1.0000 |
| evidence_support | B_vs_A (wording, baseline payoff) | -0.001 | [-0.016, +0.014] | 0.8659 |
| evidence_support | C_vs_D (wording, proposed payoff) | +0.003 | [-0.016, +0.022] | 0.6750 |
| evidence_support | wording (main effect) | +0.001 | [-0.015, +0.017] | 0.8638 |
| evidence_support | payoff (main effect) | -0.002 | [-0.009, +0.005] | 0.4552 |
| evidence_support | interaction | +0.004 | [-0.010, +0.018] | 0.4505 |
| collective_accuracy | D_vs_A (payoff, baseline wording) | +0.004 | [-0.019, +0.027] | 0.6541 |
| collective_accuracy | C_vs_B (payoff, proposed wording) | +0.000 | [-0.022, +0.022] | 1.0000 |
| collective_accuracy | B_vs_A (wording, baseline payoff) | +0.013 | [-0.005, +0.031] | 0.1216 |
| collective_accuracy | C_vs_D (wording, proposed payoff) | +0.009 | [-0.014, +0.032] | 0.3380 |
| collective_accuracy | wording (main effect) | +0.011 | [-0.002, +0.024] | 0.0858 |
| collective_accuracy | payoff (main effect) | +0.002 | [-0.014, +0.018] | 0.7444 |
| collective_accuracy | interaction | -0.004 | [-0.036, +0.028] | 0.7444 |
| brier | D_vs_A (payoff, baseline wording) | +0.002 | [-0.002, +0.005] | 0.2117 |
| brier | C_vs_B (payoff, proposed wording) | +0.001 | [-0.002, +0.004] | 0.5085 |
| brier | B_vs_A (wording, baseline payoff) | -0.112 | [-0.119, -0.105] | 0.0000 |
| brier | C_vs_D (wording, proposed payoff) | -0.113 | [-0.119, -0.107] | 0.0625 |
| brier | wording (main effect) | -0.113 | [-0.118, -0.108] | 0.0625 |
| brier | payoff (main effect) | +0.001 | [-0.001, +0.003] | 0.1988 |
| brier | interaction | -0.001 | [-0.005, +0.003] | 0.5294 |
| overconfidence | D_vs_A (payoff, baseline wording) | +0.005 | [-0.001, +0.011] | 0.0687 |
| overconfidence | C_vs_B (payoff, proposed wording) | -0.003 | [-0.006, +0.000] | 0.0570 |
| overconfidence | B_vs_A (wording, baseline payoff) | -0.293 | [-0.304, -0.282] | 0.0000 |
| overconfidence | C_vs_D (wording, proposed payoff) | -0.302 | [-0.306, -0.298] | 0.0000 |
| overconfidence | wording (main effect) | -0.297 | [-0.305, -0.290] | 0.0000 |
| overconfidence | payoff (main effect) | +0.001 | [-0.002, +0.004] | 0.3658 |
| overconfidence | interaction | -0.008 | [-0.015, -0.001] | 0.0326 |
| share_votes_correct | D_vs_A (payoff, baseline wording) | -0.002 | [-0.008, +0.004] | 0.3648 |
| share_votes_correct | C_vs_B (payoff, proposed wording) | +0.002 | [-0.001, +0.006] | 0.1609 |
| share_votes_correct | B_vs_A (wording, baseline payoff) | -0.003 | [-0.007, +0.000] | 0.0624 |
| share_votes_correct | C_vs_D (wording, proposed payoff) | +0.001 | [-0.003, +0.005] | 0.5538 |
| share_votes_correct | wording (main effect) | -0.001 | [-0.002, -0.000] | 0.1250 |
| share_votes_correct | payoff (main effect) | +0.000 | [-0.003, +0.003] | 1.0000 |
| share_votes_correct | interaction | +0.004 | [-0.003, +0.012] | 0.1848 |

## Calibration of the amendment-4 main runs (descriptive)

| Run | System | Brier | Overconfidence | Share of votes correct |
|---|---|---|---|---|
| pharma_llm_main | baseline | 0.334 ± 0.006 | 0.303 ± 0.009 | 0.527 ± 0.009 |
| pharma_llm_main | proposed | 0.228 ± 0.005 | 0.004 ± 0.012 | 0.530 ± 0.008 |
| pharma_llm_main | Δ Brier (proposed − baseline) | -0.107 [-0.112, -0.101], p 0.0000 | | |
| energy_llm_main | baseline | 0.218 ± 0.015 | 0.153 ± 0.019 | 0.720 ± 0.020 |
| energy_llm_main | proposed | 0.181 ± 0.015 | 0.005 ± 0.028 | 0.729 ± 0.029 |
| energy_llm_main | Δ Brier (proposed − baseline) | -0.036 [-0.041, -0.032], p 0.0000 | | |
| pharma_llm_main_w075 | baseline | 0.343 ± 0.007 | 0.316 ± 0.011 | 0.526 ± 0.010 |
| pharma_llm_main_w075 | proposed | 0.227 ± 0.006 | 0.007 ± 0.017 | 0.527 ± 0.012 |
| pharma_llm_main_w075 | Δ Brier (proposed − baseline) | -0.116 [-0.127, -0.105], p 0.0000 | | |
