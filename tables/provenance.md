# Blockchain provenance (H5) — local EVM

30000 records (pharma_llm_main, energy_llm_main, seeds 0–4, all systems); contract Solidity 0.8.28 on anvil (Foundry v1.8.5). Descriptive only; the chain shows integrity, not truth.

| Group | Records | VALID | TAMPERED | MISSING | Rate |
|---|---|---|---|---|---|
| decision | 200 | 0 | 200 | 0 | detected 1.000 |
| explanation | 200 | 0 | 200 | 0 | detected 1.000 |
| evidence | 200 | 0 | 200 | 0 | detected 1.000 |
| reward | 200 | 0 | 200 | 0 | detected 1.000 |
| reputation | 200 | 0 | 200 | 0 | detected 1.000 |
| control_untouched | 1000 | 1000 | 0 | 0 | false positive 0.000 |
| control_reserialised | 1000 | 1000 | 0 | 0 | false positive 0.000 |
| below_resolution | 200 | 200 | 0 | 0 | detected 0.000 |
| all_untouched | 27800 | 27800 | 0 | 0 | false positive 0.000 |

Never-written record: MISSING. Overwrite attempts accepted: 0 of 100; writes from another account accepted: 0 of 100.

## Overhead (local node; excludes consensus and network delay)

| Batch size | Txs | Gas / record | Write ms / record | Verify ms / record |
|---|---|---|---|---|
| 1 | 1000 | 121,429 | 131.78 | 11.84 |
| 10 | 100 | 98,575 | 4236.64 | 12.53 |
| 100 | 10 | 95,912 | 2.29 | 8.46 |

Deployment gas: 536,073. On-chain storage: 128 bytes per record (4 slots); off-chain artifacts: 402 bytes per record (canonical JSON).
Full run: 300 transactions, 2,876,842,332 gas, 79.3 s.
