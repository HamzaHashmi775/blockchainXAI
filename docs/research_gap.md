# Research-Gap Validation (Phase 2, Step 04)

Date: 2026-10-05. Basis: the 26 sources in `docs/literature_matrix.csv`, each verified to
exist through Crossref or the arXiv API. **This is a targeted scoping review, not a
systematic review**: 3 web searches plus known anchor papers. Full texts were not read for
several entries (marked in the matrix); for those, statements below rest on abstracts only.

## What the literature establishes

1. **Explanations can be measured.** SHAP (Lundberg & Lee 2017; Lundberg et al. 2020) gives
   additive attributions; fidelity/infidelity-type metrics exist (Yeh et al. 2019; Zhou et
   al. 2021). These evaluate an explanation *method*.
2. **Explanations can be manipulated.** Slack et al. (2020), Dombrowski et al. (2019), Heo
   et al. (2019) and Aïvodji et al. (2019) show that a model owner can produce misleading
   explanations. These papers demonstrate the attack surface; none of them proposes an
   incentive that makes misleading explanations unprofitable.
3. **Truthful reporting can be incentivised** in other settings: Bayesian truth serum
   (Prelec 2004), peer prediction (Miller et al. 2005), and incentive mechanisms for
   federated learning (Zhan et al. 2021). The rewarded object is a report or a
   data/compute contribution, not a model explanation.
4. **Reputation and blockchain provenance are mature building blocks** (Jøsang et al. 2007;
   Kamvar et al. 2003; Liang et al. 2017), and combining blockchain with XAI has been
   proposed conceptually (Nassar et al. 2019).
5. **P2P energy trading** has an extensive game-theoretic and blockchain literature (Tushar
   et al. 2018, 2020; Mengelkamp et al. 2018; Sousa et al. 2019) with no explanation
   component in the works reviewed.

## Closest prior work

- **MEA (Cheng et al., arXiv 2610.02480, Oct 2026)** optimises an explanation-producing
  agent against a faithfulness reward. This means **"explanation faithfulness as a reward
  signal" is not new.** Per its abstract it is a cooperative two-agent pipeline trained with
  that reward: no strategic or malicious agents, no evidence-support term, no reputation, no
  provenance.
- **DART (Kumala et al., arXiv 2609.05529, Sep 2026)** combines reputation, multi-factor
  incentives and blockchain governance for LLM multi-agent collaboration. Per its abstract
  the incentives concern task success, output quality and behaviour, not explanation
  fidelity or evidence support.
- **Tian (Scientific Reports, 2025)**, "Blockchain-enhanced incentive-compatible mechanisms
  for multi-agent reinforcement learning systems": only the title and metadata were
  verified. **Its content is unknown to this review** and it could overlap with the proposed
  contribution. It must be read before any novelty claim is made.

## Assessment of the gap

Supported by the reviewed sources: we found no work that (i) places **both explanation
fidelity and evidence support as explicit terms in the utility of strategically behaving
agents**, (ii) evaluates whether that changes the agents' incentive to manipulate
explanations under controlled attacks, and (iii) anchors decisions, explanations, rewards
and reputation in a tamper-evident log.

How strongly this can be claimed:

- "To the best of our knowledge, among the works reviewed" — defensible.
- "First" / "no prior work" — **not defensible** on this evidence: the review is not
  systematic, two of the three closest works were read at abstract level only, and one was
  not read at all.
- The novelty is the **combination and the strategic setting**, not any single ingredient.
  Faithfulness-as-reward (MEA), blockchain + reputation + incentives for agents (DART), and
  blockchain for XAI (Nassar et al.) each already exist.

## Actions before paper writing (Phase 11)

1. Read the full texts of Tian (2025), DART, MEA and Nassar et al. (2019).
2. Run a systematic search (stated databases, query strings, date) and record it.
3. Re-phrase the contribution if any of these turn out to cover (i)–(iii).
