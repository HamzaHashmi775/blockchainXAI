# Table 6 — Blockchain provenance: tamper detection and overhead (H5)

Protocol amendment 5 (v1.5). Descriptive results; the records are not independent replications of the agent experiment, and the chain shows integrity, not truth.

## Set-up

| Item | Value |
|---|---|
| Contract | `ProvenanceRegistry.sol`, Solidity 0.8.28, optimiser 200 runs |
| Contract source SHA-256 | `a61e91c69de598880eeebb482dc0cc969a01962b8633a567cbb31cd8f286cc67` |
| Creation bytecode SHA-256 | `a926f4f86b1a146a0d17f10a88dfc3476374cde1382187767db2af6255a50a33` |
| Node | anvil/v1.8.5 (single local node), chain id 31337, hard fork Bpo1 |
| Blocks | instant (a block per transaction); block gas limit 30,000,000; base fee 1,000,000,000 wei |
| Note | contract fingerprint and node settings captured on 2026-10-18 after the run, from the same contract source, solc and anvil binaries (the run itself did not record them) |
| Client | web3.py, Python 3.12.10 |
| On-chain per record | record id; SHA-256 of decision, explanation and evidence; reward and reputation × 10⁶ (uint32); block timestamp |
| Off-chain per record | decision, explanation, evidence, reward, reputation as canonical JSON |
| Rules | append-only (a record id is written once); only the deploying account writes |
| Records | 30,000 = pharma_llm_main, energy_llm_main, seeds 0–4, 3 systems, 200 rounds, 5 agents; batches of 100 |

## Procedure

1. All 30,000 records written to a fresh deployment; the off-chain store saved to disk.
2. 1,000 records drawn at random (seed 0), 200 per target, each changed in one field of the off-chain store: decision = vote moved to another option; explanation = direction of feature 1 reversed; evidence = level of feature 1 changed; reward and reputation = +10⁻⁶ (one storage unit).
3. Controls: 1,000 untouched records and 1,000 re-serialised ones (keys reversed, indented JSON, same values). Declared limit: 200 rewards changed by 1e-09.
4. The store is read back from disk; each record's hashes and scaled values are recomputed and compared with the chain (VALID / TAMPERED / MISSING).
5. Contract rules: 100 overwrite attempts and 100 writes from a second account.
6. Overhead: the first 1,000 records of pharma seed 0, on a fresh deployment for each batch size (1, 10, 100).

## Tamper detection

| Group | Records | VALID | TAMPERED | MISSING | Rate |
|---|---|---|---|---|---|
| decision | 200 | 0 | 200 | 0 | detected 1.000 |
| explanation | 200 | 0 | 200 | 0 | detected 1.000 |
| evidence | 200 | 0 | 200 | 0 | detected 1.000 |
| reward | 200 | 0 | 200 | 0 | detected 1.000 |
| reputation | 200 | 0 | 200 | 0 | detected 1.000 |
| control_untouched | 1,000 | 1,000 | 0 | 0 | false positive 0.000 |
| control_reserialised | 1,000 | 1,000 | 0 | 0 | false positive 0.000 |
| below_resolution | 200 | 200 | 0 | 0 | detected 0.000 |
| all_untouched | 27,800 | 27,800 | 0 | 0 | false positive 0.000 |

Never-written record: MISSING. Overwrite attempts accepted: 0 of 100; writes from another account accepted: 0 of 100. Below-resolution changes are invisible by design (rounding to the nearest 10⁻⁶).

## Overhead (local node: excludes consensus, block time and network delay)

| Batch size | Txs | Gas / record | Gas / tx (median) | Write ms / record (mean) | Write ms / tx (median) | Verify ms / record |
|---|---|---|---|---|---|---|
| 1 | 1,000 | 121,429 | 121,417 | 131.8 | 139.3 | 11.8 |
| 10 | 100 | 98,575 | 985,583 | 4236.6 | 167.4 | 12.5 |
| 100 | 10 | 95,912 | 9,589,494 | 2.3 | 211.3 | 8.5 |

Deployment: 536,073 gas. Storage: 128 bytes on-chain per record (4 storage slots) against 402 bytes of off-chain artifact. Full run: 300 transactions, 2,876,842,332 gas (95,895 per record), 79.3 s.

Write latency is wall-clock time from sending a transaction to receiving its receipt and is dominated by the client's receipt polling; gas is the figure that transfers to other EVM chains.

Note: Batch size 10: the mean write latency (declared statistic, 4237 ms per record) includes a one-off stall of about 70 minutes spread over a few transactions; the median transaction took 167 ms. Per-transaction times were not saved in this run, so the stall cannot be located; cause unknown. A diagnostic rerun of this step (not part of the frozen experiment; two repetitions on fresh nodes) took 14.5 s per 1,000 records, median 146 ms and maximum 180 ms per transaction.
