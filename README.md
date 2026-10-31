# Explanation-Aware Incentive Mechanism for Trustworthy Multi-Agent AI with Blockchain Provenance

Research code for one question: **can a game-theoretic incentive that pays agents for
faithful, evidence-supported explanations (and penalises manipulation) make multiple AI agents
explain themselves more honestly, with a blockchain recording decisions and explanations so
that later tampering can be detected?**

The core contribution is the incentive. The blockchain is only a provenance and integrity
layer: it shows that a record was not changed after it was written, **not** that the
explanation was true.

## Status

| Phase | Content | Status |
|---|---|---|
| 0–2 | Setup, dataset audit, literature matrix, research gap, frozen protocol | done |
| 3–7 | Pharma: preprocessing, 5 agents, game + SHAP, metrics, attacks, incentive, main experiment, ablation, malicious-agent and collusion experiments | done |
| 8 | Blockchain provenance: tamper detection and overhead | done |
| 9 | Energy: the full pharma pipeline repeated | done |
| — | Optional extension: LLM agents (qwen2.5:7b) in both domains, incl. a 2×2 wording × payoff experiment | done |
| 10 | Cross-domain comparison (H6), sensitivity analysis (β, ρ, ω), final statistics | done |
| 11 | Tables 1–7, figures 1–8, reproducibility package (verified by a clean rerun), claim–evidence map, manuscript draft (`paper/`) | done |

## Pipeline

```
real dataset → preprocessing → scenarios → 5 specialised agents → game (strategy choice, vote)
  → collective decision → SHAP explanations → fidelity / evidence / consistency
  → explanation-aware utility → reward → reputation → hash records on a local chain → verification
```

Utility of agent *i*: `U_i = α·D_i + β·F_i + γ·E_i + δ·C_i − λ·M_i` (decision quality, fidelity,
evidence support, cooperation, manipulation; all in [0, 1]), with α 0.30, β 0.25, γ 0.15,
δ 0.10, λ 0.20. Reward `R_i = (U_i − U_min)/(U_max − U_min)` (0.5 when all are equal);
reputation `Rep ← ρ·Rep + (1 − ρ)·R`, ρ 0.8, starting at 0.5.

| System | Components |
|---|---|
| Baseline | game + XAI; utility 0.75·D + 0.25·C (no explanation terms) |
| Ablation | + explanation-aware incentive |
| Proposed | + incentive + reputation (blockchain recorded separately, Phase 8) |

All systems use identical real-data scenarios and identical seeds (paired comparisons).
Agents choose among honest, strategic, misattributing, overclaiming and manipulative
strategies; attacks (false attribution, confidence inflation, unsupported evidence,
strategic voting, collusion) change agent outputs only, never the real observations.

## Data

Raw files in `data/raw/` are never modified. Sources, licences, citations and SHA-256 hashes
are in `data/metadata/datasets.json`; the full audit is in `docs/dataset_audit.md`.

| Case study | Dataset | File | SHA-256 | Licence |
|---|---|---|---|---|
| Pharma (used) | USAID/PEPFAR SCMS Delivery History, extract 2015-09-29 (via Kaggle) | `data/raw/pharma_scms/SCMS_Delivery_History_Dataset_20150929.csv` | `9cffdb4a…3578a` | CC BY-ND 4.0 (per catalogue mirror) |
| Energy | Garcia-Munoz (2025), *Operational Data of an Energy Community Under P2P Trading and Flexibility Market Models*, Mendeley Data V1, doi:10.17632/bvp4vrn9gc.1 | `data/raw/energy/Case_Study_OptiREC.xlsx` | `b61c6049…ed09a` | CC BY 4.0 |
| Pharma (audited, not used) | Forghani et al. (2018), figshare 6971474 | `data/raw/pharma/Table 1.xls` | `7f389937…aa470` | CC BY 4.0 |

The figshare file named in the original plan lists 24 supplier-selection criteria and has no
observations, so it cannot drive agents. With the user's approval (protocol amendment 2) the
SCMS delivery history is the pharma dataset: five agents (cost, delivery reliability, lead
time, logistics, supply continuity) built from its variables, direct-from-supplier lines
only, against a **constructed** reference decision. The energy battery parameters (C-rate,
efficiency, SOC window) are not in the dataset and are labelled simulated assumptions
(protocol §3). Decision accuracy means agreement with the constructed reference, not with
observed behaviour.

## Main results (classical agents, 10 seeds)

Verdicts follow the pre-declared rule (protocol §9): *improved* = Holm-adjusted p < 0.05 in
the hypothesised direction **and** |relative change| ≥ 5 %. Relative change = (proposed −
baseline)/|baseline|.

| Hypothesis | Pharma | Energy |
|---|---|---|
| H1 fidelity | improved, +83.5 % (0.51 → 0.94) | negligible, +3.6 % (0.94 → 0.97; significant but < 5 %) |
| H2 evidence support | improved, +75.7 % | negligible, +4.3 % |
| H3 manipulation | improved, −69.7 % | improved, −44.4 % |
| H4 robustness to 10–40 % malicious agents | not supported: Δ degradation +0.039, p 0.10 | not supported: Δ −0.020, p 0.07 |
| H6 same verdict in both domains | holds for manipulation only (1 of 3) | |

- **H5 (blockchain):** 1,000 tampered records (decision, explanation, evidence, reward,
  reputation): all detected. 0 false positives in 2,000 controls and 27,800 untouched
  records. Changes below the 10⁻⁶ storage resolution are invisible by design. Local node
  (anvil); overhead ≈ 96k gas per record in batches of 100 (`tables/provenance.md`).
- **Hardened provenance** (amendment 9, added post hoc, descriptive;
  `tables/provenance_hardened.md`): with agent signatures, model registration and Merkle
  anchors on a second (simulated external) chain, the contract refused all forged or
  replayed writes and substituted models (0 of 100 accepted for each of 7 attacks; 100/100
  valid controls accepted). When the operator rebuilt the whole history with 200 altered
  records, the anchors found all 200 and flagged none of the other 29,800; the original
  per-record check found none. Cost ≈ 126k gas per record (+113 gas for anchoring).
- **Ceiling in energy:** the energy baseline already reaches F 0.94 / E 0.93, so there is
  little room for a 5 % gain. This is reported, not used to change any verdict.
- **Sensitivity** (`tables/sensitivity_robustness.md`): pharma verdicts unchanged at every
  value of β ∈ {0, 0.1, 0.25, 0.4}, ρ ∈ {0.5, 0.8, 0.95}, ω ∈ {0.25, 0.5, 0.75}. Energy
  verdicts unchanged across β and ρ. Across ω, energy F and E change from negligible to
  improved at ω = 0.75 (+28 %), so they are not robust there. Pharma fidelity still improves
  +74.7 % at β = 0: the gain does not depend on the fidelity weight itself.

## LLM agents (optional extension; qwen2.5:7b via Ollama, 5 seeds, 200 rounds)

- Proposed vs baseline: manipulation improved in both domains (−22.0 % pharma, −12.6 %
  energy); fidelity and evidence negligible in both. H6 holds for all three outcomes.
- 2×2 wording × payoff experiment (amendments 7–8): the drop in stated confidence comes
  from **how the reward rules are worded in the prompt**, not from the payoff applied.
  Wording main effect −0.299 (pharma) and −0.164 (energy), both Holm p < 0.0001; payoff
  main effect not detected in either domain. A small wording × payoff interaction was
  detected in energy only (+0.006).
- LLM runs ran on Kaggle (2 × T4); the notebook is generated from `kaggle/llm_run_kaggle.py`.

All numbers above come from `tables/` and `results/summaries/`; the full tables, with
confidence intervals, tests and effect sizes, are there.

## Repository layout

| Path | Content |
|---|---|
| `run_experiment.py` | entry point: `--config <yaml>`; `--resume` skips seeds already written |
| `configs/` | one YAML per experiment (baseline, proposed, ablation, adversarial, sensitivity, LLM, provenance) |
| `environments/{pharma,energy}/` | deterministic preprocessing and scenario construction |
| `agents/` | the five agents per domain (random forests) and the LLM agent |
| `game/` | strategy space (honest, strategic, misattributing, overclaiming, manipulative) |
| `xai/` | SHAP explainer |
| `incentives/`, `reputation/` | utility, reward, manipulation score and attacks; reputation update |
| `evaluation/` | fidelity, evidence support, consistency; statistical tests |
| `experiments/` | game loop per domain, LLM runs, provenance experiment, experiment registry |
| `utils/` | seeding and dataset loading |
| `blockchain/` | `ProvenanceRegistry.sol` and its web3 client; hardened `ProvenanceRegistryV2.sol` (agent signatures, model registration), `AnchorRegistry.sol` and `hardened.py` (Merkle anchoring) |
| `statistics/` | analysis scripts (run by path; see `statistics/README.md`) |
| `kaggle/` | notebook for the GPU LLM runs |
| `results/summaries/`, `tables/`, `figures/` | analysed results, paper tables 1–7 and figures 1–8 (committed); raw per-seed results in `results/raw/` (git-ignored) |
| `reproduce.py` | one command to rebuild analyses, tables and figures |
| `tests/` | pytest suite |
| `docs/` | audit, literature matrix, research gap, protocol, threats to validity, log |

## Reproducing

Python 3.12.10, dependencies pinned in `requirements.txt`.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # Windows; .venv/bin/python elsewhere
python -m pytest -q
```

**One command** rebuilds every summary, table and figure from the raw results:

```bash
python reproduce.py                  # analyses -> results/summaries/, tables/, figures/
python reproduce.py --experiments    # first rerun the 14 classical experiments (CPU, ~1-2 h)
python reproduce.py --compare <other checkout>   # per-seed results must be byte-identical
```

**Verified (2026-10-31):** in a fresh clone, `reproduce.py --experiments` reran all 14
classical experiments; all 140 per-seed result files were byte-identical to the originals,
and the rebuilt summaries, tables and figures (70 files) were byte-identical to the
committed ones.

`--experiments` runs, with seeds 0–9 fixed in each config:
`{pharma,energy}_{baseline,ablation,proposed,adversarial}` and
`{pharma,energy}_sensitivity_{beta,rho,omega}`. A single experiment is
`python run_experiment.py --config configs/<name>.yaml` (`--resume` skips seeds already
written). Each run writes per-seed results and a manifest (config, seeds, dataset hashes,
status) to `results/raw/<config name>/`; raw results are git-ignored.

Not rerun by `reproduce.py`:
- **LLM experiments** need Ollama with `qwen2.5:7b` (digest `845dbda0…`) and a GPU; they ran
  on Kaggle (`kaggle/`). Their analyses run only when `results/raw/<run>/` is present;
  otherwise the committed summaries are used.
- **Provenance** (`configs/provenance.yaml`, `configs/provenance_hardened.yaml`) needs a
  local `anvil` node and `solc`: `python experiments/provenance.py` and
  `python experiments/provenance_hardened.py` (about 50 min).

## Limitations (summary)

Constructed reference decisions in both domains; simulated battery parameters in energy;
SHAP fidelity depends on the underlying models; results depend on the incentive weights;
reputation can create path dependence; n = 10 seeds (classical) and 5 (LLM); the LLM 2×2
was added post hoc; local-chain overhead differs from production networks; the chain shows
integrity, not truth; the anchor chain was simulated by a second local node, and the system
was not evaluated against network attacks, stolen keys, Sybil identities or adaptive
attackers (threat model in `docs/threats_to_validity.md`). No exact Nash equilibrium is claimed: unilateral-deviation payoffs are
reported instead. Details in `docs/threats_to_validity.md`.
