# Independent verification

These checks are read-only; they do not sign a transaction or require testnet GEN. Use the hardened candidate address `0x646564F618f500594F2F3BA1Ed2683DD80909585` on Bradbury (chain ID `4221`). The expected contract-source SHA-256 is `671399b0828f6a0a68b4a943b3054d9f515e880b24dea4af7d6f1f5dda1dfbcf`. **Do not submit while [`SUBMISSION.md`](SUBMISSION.md) says hold.**

## Compare deployed and repository source

From the repository root on macOS, with `curl`, `jq`, `base64`, and `shasum`:

```sh
shasum -a 256 contracts/evidence_latch.py

curl -fsS --max-time 15 https://rpc-bradbury.genlayer.com \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"gen_getContractCode","params":[{"address":"0x646564F618f500594F2F3BA1Ed2683DD80909585","status":"finalized"}]}' \
  | jq -er '.result' | base64 -D | shasum -a 256
```

Both hashes must match the expected value. On Linux, replace `base64 -D` with `base64 -d`. A null result, RPC error, or decoding failure is not a successful check. The pinned evidence file can be checked independently; its digest must also equal `get_source_sha256()` on the deployed contract:

```sh
shasum -a 256 evidence/delivery-plan.md
curl -fsS --max-time 15 \
  https://raw.githubusercontent.com/Manablaq/evidence-latch/3be9be9c360823e9a9479c1254098c5fd7d8f811/evidence/delivery-plan.md \
  | shasum -a 256
```

Both evidence hashes should be `4d69f65ad6cda4574792aad9fb9b75dc928fc6f48fe88d54b34149e6fd9678d7`.

## Check finality and execution

For the candidate contract's successful adjudication:

```sh
curl -fsS --max-time 15 https://rpc-bradbury.genlayer.com \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"gen_getTransactionReceipt","params":[{"txId":"0x961aed8cf1b1fb7a168a3928dc591bdc729da68b9883cf05e706bf10fd1130b8"}]}' \
  | jq -e '{status: .result.status, execution: .result.txExecutionResult, recipient: .result.recipient, error: .error}'
```

On Bradbury, `status: 7` means `FINALIZED` and `execution: 1` means a successful return. The recipient must be the candidate contract and the RPC error must be null. For the deliberately wrong-hash transaction `0x1209c8d3faeb0c1be5e08bbd189631accb4eb45dbb4a4ff429a9f36df7d8bee5`, the expected execution code is `2` (error), even if its consensus status becomes finalized. A finalized error is not a verdict. See [the full transaction matrix](LIVE_AUDIT_2026-10-16.md) and the [Bradbury explorer verdict trace](https://explorer-bradbury.genlayer.com/tx/0x961aed8cf1b1fb7a168a3928dc591bdc729da68b9883cf05e706bf10fd1130b8).

If the GenLayer CLI is installed, the stored verdict can be read without sending a write:

```sh
genlayer network set testnet-bradbury
genlayer call 0x646564F618f500594F2F3BA1Ed2683DD80909585 get_source_sha256 --rpc https://rpc-bradbury.genlayer.com
genlayer call 0x646564F618f500594F2F3BA1Ed2683DD80909585 get_verdict --rpc https://rpc-bradbury.genlayer.com
genlayer call 0x646564F618f500594F2F3BA1Ed2683DD80909585 get_resolved --rpc https://rpc-bradbury.genlayer.com
```

The expected values are `4d69f65ad6cda4574792aad9fb9b75dc928fc6f48fe88d54b34149e6fd9678d7`, `SATISFIED`, and `true`. A CLI read may use an accepted rather than a finalized state snapshot; check transaction finality separately before treating the values as durable. GenLayer's RPC documentation defines [`gen_getContractCode`](https://docs.genlayer.com/api-references/genlayer-node/gen/gen_getContractCode) and [`gen_getTransactionReceipt`](https://docs.genlayer.com/api-references/genlayer-node/gen/gen_getTransactionReceipt).
