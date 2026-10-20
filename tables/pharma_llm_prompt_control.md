# Prompt-only control (pharma, LLM agents) — added, post hoc experiment

Model `qwen2.5:7b`; n = 5 paired seeds; ω = 0.5; prompt style `raw`. A = baseline wording and payoff; B = proposed wording, baseline payoff; C = proposed wording and payoff. Audit checks shown in the round history in all three. Designed after the main results were known (amendment 6).
Model calls: 15000; unusable replies: 0; reports replaced by the tool's report: 0.

| Outcome | A | B | C |
|---|---|---|---|
| mean_confidence | 0.831 ± 0.002 | 0.534 ± 0.007 | 0.534 ± 0.006 |
| confidence_inflation | 0.323 ± 0.007 | 0.022 ± 0.001 | 0.022 ± 0.002 |
| votes_against_tool | 0.169 ± 0.010 | 0.133 ± 0.011 | 0.134 ± 0.007 |
| manipulation | 0.299 ± 0.005 | 0.225 ± 0.005 | 0.226 ± 0.005 |
| fidelity | 0.445 ± 0.015 | 0.458 ± 0.010 | 0.456 ± 0.011 |
| evidence_support | 0.598 ± 0.011 | 0.597 ± 0.010 | 0.597 ± 0.010 |
| collective_accuracy | 0.576 ± 0.018 | 0.589 ± 0.015 | 0.589 ± 0.026 |
| component_strategic_voting | 0.169 ± 0.010 | 0.133 ± 0.011 | 0.134 ± 0.007 |

## B vs A — wording

| Outcome | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|
| mean_confidence | -0.297 | [-0.305, -0.288] | -35.7% | paired t-test | 0.0000 | 0.0000 | lower |
| confidence_inflation (secondary) | -0.300 | [-0.309, -0.292] | -93.1% | paired t-test | 0.0000 | — | — |
| votes_against_tool (secondary) | -0.036 | [-0.039, -0.033] | -21.4% | paired t-test | 0.0000 | — | — |
| manipulation (secondary) | -0.073 | [-0.077, -0.069] | -24.5% | paired t-test | 0.0000 | — | — |
| fidelity (secondary) | +0.013 | [+0.009, +0.019] | +3.0% | Wilcoxon signed-rank | 0.0625 | — | — |
| evidence_support (secondary) | -0.001 | [-0.016, +0.014] | -0.2% | paired t-test | 0.8659 | — | — |
| collective_accuracy (secondary) | +0.013 | [-0.005, +0.031] | +2.3% | paired t-test | 0.1216 | — | — |
| component_strategic_voting (secondary) | -0.036 | [-0.039, -0.033] | -21.4% | paired t-test | 0.0000 | — | — |

## C vs B — payoff, given the proposed wording

| Outcome | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|
| mean_confidence | -0.001 | [-0.002, +0.000] | -0.1% | paired t-test | 0.1508 | 0.1508 | no detectable effect |
| confidence_inflation (secondary) | +0.000 | [-0.002, +0.002] | +0.4% | paired t-test | 0.9181 | — | — |
| votes_against_tool (secondary) | +0.001 | [-0.009, +0.010] | +0.6% | paired t-test | 0.8239 | — | — |
| manipulation (secondary) | +0.001 | [-0.004, +0.006] | +0.3% | paired t-test | 0.7219 | — | — |
| fidelity (secondary) | -0.002 | [-0.006, +0.001] | -0.5% | paired t-test | 0.1339 | — | — |
| evidence_support (secondary) | +0.000 | [-0.008, +0.008] | +0.0% | paired t-test | 1.0000 | — | — |
| collective_accuracy (secondary) | +0.000 | [-0.022, +0.022] | +0.0% | paired t-test | 1.0000 | — | — |
| component_strategic_voting (secondary) | +0.001 | [-0.009, +0.010] | +0.6% | paired t-test | 0.8239 | — | — |

## C vs A — wording and payoff together

| Outcome | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|
| mean_confidence | -0.298 | [-0.305, -0.290] | -35.8% | paired t-test | 0.0000 | 0.0000 | lower |
| confidence_inflation (secondary) | -0.300 | [-0.308, -0.293] | -93.1% | paired t-test | 0.0000 | — | — |
| votes_against_tool (secondary) | -0.035 | [-0.043, -0.028] | -20.9% | paired t-test | 0.0002 | — | — |
| manipulation (secondary) | -0.073 | [-0.077, -0.069] | -24.3% | paired t-test | 0.0000 | — | — |
| fidelity (secondary) | +0.011 | [+0.008, +0.015] | +2.4% | Wilcoxon signed-rank | 0.0625 | — | — |
| evidence_support (secondary) | -0.001 | [-0.014, +0.012] | -0.2% | paired t-test | 0.8462 | — | — |
| collective_accuracy (secondary) | +0.013 | [-0.008, +0.034] | +2.3% | paired t-test | 0.1588 | — | — |
| component_strategic_voting (secondary) | -0.035 | [-0.043, -0.028] | -20.9% | paired t-test | 0.0002 | — | — |

Reading (pre-declared rule): **wording: the stated rules lower confidence; the payoff adds no detectable effect**.
Share of the combined effect on mean_confidence that B already shows (mean(B − A) / mean(C − A)): 1.00 (descriptive).

Descriptive checks against the main run (same seeds and rounds):
- C_vs_original_proposed: mean_confidence Δ -0.000 (p 0.657); fidelity Δ +0.006 (p 0.020)
- A_vs_original_baseline: mean_confidence Δ +0.001 (p 0.062); fidelity Δ -0.013 (p 0.013)
