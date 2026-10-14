# Independent verification

These checks are read-only; they do not sign a transaction or require testnet GEN. Use the submission address `0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9` on Bradbury (chain ID `4221`). The expected contract-source SHA-256 is `f625b608d0838d86af222dd52ad32ddfe0d388b0a1313829acbdafb0349ea232`.

## Compare deployed and repository source

From the repository root on macOS, with `curl`, `jq`, `base64`, and `shasum`:

```sh
shasum -a 256 contracts/evidence_latch.py

curl -fsS --max-time 15 https://rpc-bradbury.genlayer.com \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"gen_getContractCode","params":[{"address":"0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9","status":"finalized"}]}' \
  | jq -er '.result' | base64 -D | shasum -a 256
```

Both hashes must match the expected value. On Linux, replace `base64 -D` with `base64 -d`. A null result, RPC error, or decoding failure is not a successful check. The pinned evidence file can be checked independently:

```sh
shasum -a 256 evidence/delivery-plan.md
curl -fsS --max-time 15 \
  https://raw.githubusercontent.com/Manablaq/evidence-latch/3be9be9c360823e9a9479c1254098c5fd7d8f811/evidence/delivery-plan.md \
  | shasum -a 256
```

Both evidence hashes should be `4d69f65ad6cda4574792aad9fb9b75dc928fc6f48fe88d54b34149e6fd9678d7`.

## Check finality and execution

For the submission contract's successful adjudication:

```sh
curl -fsS --max-time 15 https://rpc-bradbury.genlayer.com \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"gen_getTransactionReceipt","params":[{"txId":"0xfaa48cc436096e8d9fa14868860e87062d52628792fd007693c0070531a1fb0e"}]}' \
  | jq -e '{status: .result.status, execution: .result.txExecutionResult, recipient: .result.recipient, error: .error}'
```

On Bradbury, `status: 7` means `FINALIZED` and `execution: 1` means a successful return. The recipient must be the submission contract and the RPC error must be null. For the deliberately missing-file transaction `0x46442e7b18ffc93ae35719d4963dd9db1b5b66c1b20ec6a88b0229de605c4223`, the expected execution code is `2` (error), even if its consensus status becomes finalized. A finalized error is not a verdict. See [the full transaction matrix](DEPLOYMENT.md) and the [Bradbury explorer verdict trace](https://explorer-bradbury.genlayer.com/tx/0xfaa48cc436096e8d9fa14868860e87062d52628792fd007693c0070531a1fb0e).

If the GenLayer CLI is installed, the stored verdict can be read without sending a write:

```sh
genlayer network set testnet-bradbury
genlayer call 0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9 get_verdict --rpc https://rpc-bradbury.genlayer.com
genlayer call 0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9 get_resolved --rpc https://rpc-bradbury.genlayer.com
```

The expected values are `SATISFIED` and `true`. A CLI read may use an accepted rather than a finalized state snapshot; check transaction finality separately before treating the values as durable. GenLayer's RPC documentation defines [`gen_getContractCode`](https://docs.genlayer.com/api-references/genlayer-node/gen/gen_getContractCode) and [`gen_getTransactionReceipt`](https://docs.genlayer.com/api-references/genlayer-node/gen/gen_getTransactionReceipt).
