# Table 6b — Hardened provenance: signatures, model registration, anchoring

Protocol amendment 9 (v1.9), added post hoc; descriptive. The external chain is simulated by a second local Anvil node; agent keys are deterministic test keys. Integrity, not truth: a signed, anchored record can still hold a false explanation.

## Honest run (false-positive check)

30,000 records (pharma_llm_main, energy_llm_main, seeds 0–4), 10 registered agents, 31 anchors (1 registration + one per 1,000 records).

| Check | Result |
|---|---|
| Per-record verification | VALID 30,000, TAMPERED 0, MISSING 0 |
| Registrations differing from anchor | 0 of 10 |
| Anchored roots differing | 0 of 30 |
| Records failing their inclusion proof | 0 |

## Forgery and replay (refused at write time)

100 attempts each, fresh record ids, records drawn at random.

| Attempt | Accepted | Outcome |
|---|---|---|
| valid_control | 100 of 100 | accepted: 100 |
| content_changed_after_signing | 0 of 100 | bad signature: 100 |
| other_agents_key | 0 of 100 | bad signature: 100 |
| unregistered_key | 0 of 100 | bad signature: 100 |
| replay_other_record_id | 0 of 100 | bad signature: 100 |
| replay_other_deployment | 0 of 100 | bad signature: 100 |
| model_substituted | 0 of 100 | model mismatch: 100 |
| non_owner_sender | 0 of 100 | not owner: 100 |

## History rewrite by the operator

200 records altered (40 per target) and the whole chain rebuilt on a fresh node, consistent with the altered off-chain store.

| Check | Amendment-5 contract | Hardened + anchors |
|---|---|---|
| Records flagged by per-record verification | 0 of 200 | 0 of 30,000 |
| Registrations differing from anchor (operator's own keys) | – | 10 of 10 |
| Anchored roots differing | – | 30 of 30 |
| Altered records failing their inclusion proof | – | 200 of 200 |
| Unaltered records failing their inclusion proof | – | 0 of 29,800 |

Altered records detected by anchor, per target: decision 40/40, explanation 40/40, evidence 40/40, reward 40/40, reputation 40/40.

## Overhead (local node: excludes consensus, block time and network delay)

| Batch size | Gas / record | Amendment 5 gas / record | Write ms / tx (median) | Sign ms / record | Verify ms / record |
|---|---|---|---|---|---|
| 1 | 155,479 | 121,429 | 159.3 | 15.3 | 17.8 |
| 10 | 130,121 | 98,575 | 215.6 | 20.8 | 17.7 |
| 100 | 126,005 | 95,912 | 1056.5 | 21.8 | 19.2 |

Deployment 814,359 gas; registering 10 agents 692,574 gas. Anchoring: 113,463 gas per anchor (1,000 records; 113 gas per record); tree of 1,000 leaves built in 7.4 ms; inclusion proof 320 bytes (max 320), verified in 61 µs. Full run: 300 transactions, 3,779,594,810 gas (125,986 per record), signing 527 s in total.
