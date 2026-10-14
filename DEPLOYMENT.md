# Bradbury deployment and live tests

Network: GenLayer Bradbury, chain ID `4221`, RPC `https://rpc-bradbury.genlayer.com`. Deployer: `0x5bb49021001200fe8156a81c7fcf097e535e7181`. All transactions below were sent on 14 October 2026.

The **submission contract** is [`0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9`](https://explorer-bradbury.genlayer.com/address/0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9). It fixes this criterion:

> The webhook design uses HMAC-SHA256 signatures and retries failed deliveries up to three times with exponential backoff.

Its evidence is the [Markdown source pinned to repository commit `3be9be9c360823e9a9479c1254098c5fd7d8f811`](https://github.com/Manablaq/evidence-latch/blob/3be9be9c360823e9a9479c1254098c5fd7d8f811/evidence/delivery-plan.md). The raw file's SHA-256 is `4d69f65ad6cda4574792aad9fb9b75dc928fc6f48fe88d54b34149e6fd9678d7`. Every corrected deployment returned source SHA-256 `f625b608d0838d86af222dd52ad32ddfe0d388b0a1313829acbdafb0349ea232`, matching [`contracts/evidence_latch.py`](contracts/evidence_latch.py).

## Corrected-source transaction matrix

An `ACCEPTED` transaction is provisional until Bradbury records `FINALIZED`. A successful verdict requires both consensus acceptance and a successful execution result; a finalized error is still an error. The status column below must be updated from live RPC before submission.

| Live case | Contract and transaction | Observed execution | Current finality |
| --- | --- | --- | --- |
| Submission deployment | [`0x312BA099…`](https://explorer-bradbury.genlayer.com/address/0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9), [deployment tx](https://explorer-bradbury.genlayer.com/tx/0x53e32b1fa627e7e2bd616b5b09794479083706c2f1553d112d2f2ad3b6dfecf6) | Constructor succeeded; four view methods and one nonpayable write method. | `ACCEPTED` at last check. |
| Criterion established | [submission contract](https://explorer-bradbury.genlayer.com/address/0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9), [verdict tx](https://explorer-bradbury.genlayer.com/tx/0xfaa48cc436096e8d9fa14868860e87062d52628792fd007693c0070531a1fb0e) | `SATISFIED`, successful return; three agree votes, two validator timeouts. Getter returned `SATISFIED` and `resolved = true`. | `ACCEPTED` at last check. |
| Explicit contradiction | [`0xfe7F06c9…`](https://explorer-bradbury.genlayer.com/address/0xfe7F06c984C91Fe281AAf729C06c2e523b625a53), [deployment tx](https://explorer-bradbury.genlayer.com/tx/0xbddda3fa8dd0f404012a07adb90f9af3ed1b751bdf3ee78158160812471e9605), [verdict tx](https://explorer-bradbury.genlayer.com/tx/0x8789f1c52d2578d86f7b6da59730504f759334601a4e6dd7b81b77ba5c57e5c6) | `NOT_SATISFIED`, successful return; four agree votes, one validator timeout. Getter returned the same verdict. | `ACCEPTED` at last check. |
| Missing detail | [`0xB3ccE22e…`](https://explorer-bradbury.genlayer.com/address/0xB3ccE22e00D5ffFa7f68131858402C135B29b562), [deployment tx](https://explorer-bradbury.genlayer.com/tx/0xfc447dadcd7ef7d4770c01244bfa14f3202698db35e22a3c56ca17098ab6c5a5), [verdict tx](https://explorer-bradbury.genlayer.com/tx/0x1fcc499b74577bd8d3ae9433f9d9e7ac1322861192f1a39b8384f6fc347aa8c0) | `INDETERMINATE`, successful return; five agree votes. Getter returned the same verdict. | `ACCEPTED` at last check. |
| Missing evidence file | [`0x32bCC557…`](https://explorer-bradbury.genlayer.com/address/0x32bCC557c9D229e051cBe53e4c6eB5F3B6cAac51), [deployment tx](https://explorer-bradbury.genlayer.com/tx/0x3d84322d1e3cf1a3d3df8ac4ff0fea9d4092511e29c663279828fe95f84d394f), [failed call](https://explorer-bradbury.genlayer.com/tx/0x46442e7b18ffc93ae35719d4963dd9db1b5b66c1b20ec6a88b0229de605c4223) | Agreed `SOURCE_HTTP` user error, not a verdict. Getter remained `PENDING` and `resolved = false`. | `ACCEPTED` at last check. |
| Duplicate adjudication | [submission contract](https://explorer-bradbury.genlayer.com/address/0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9), [failed call](https://explorer-bradbury.genlayer.com/tx/0x0db5475a7c298c5967232655d3f0bb8f47b32c40df2767de03caf36ddab1b6ea) | Agreed `ALREADY_RESOLVED` user error; did not overwrite the verdict. | `ACCEPTED` at last check. |

The negative criterion was “The design retries failed deliveries exactly ten times without any delay”; the document explicitly says up to three retries with exponential backoff. The indeterminate criterion was “The service encrypts stored delivery logs at rest using AES-256”; the document mentions retention but does not specify encryption.

## Failures found and corrected

The first audit build used source SHA-256 `be7fa842f7eef08a7c0277a4e40ccbdbdd06f0c4cc6f8541b93a397a622f0b17`. A live missing-file test at [`0x3156be7e…`](https://explorer-bradbury.genlayer.com/tx/0x3156be7e94490dfd6631d09ea39ef4306cec1077a171edd7cc7132399356c5de) became `UNDETERMINED`: v1 raised the fetch error inside the nondeterministic block, while its validator rejected leader errors. The v2 source returns a bounded error code through consensus and raises the user error only afterward. The corrected missing-file transaction above reached an accepted error result without changing state. **Do not submit the v1 addresses.**

The corrected submission contract also had one initial leader-timeout transaction, [`0xd09ab35c…`](https://explorer-bradbury.genlayer.com/tx/0xd09ab35cd062c0061c285ea7bbd561dc90cba20bf23a001f3d012de2c0a6c07d), before a later call succeeded. This is an availability limitation, not a valid verdict. A rapid intermediate retry reverted at the consensus contract before creating a GenLayer transaction; it is not evidence of contract execution. CLI output can call an accepted user error “successfully executed”; always inspect the execution result and trace.

## Reproducibility

The direct-mode suite passes **28 tests** with `genlayer-test==0.29.2` and the pinned `v0.2.16` SDK bundle. `genvm-linter==0.11.0` lint, semantic validation, and type checking pass under `GENVM_VERSION=v0.3.0-rc4`. CI runs these checks on the public repository. [`VERIFY.md`](VERIFY.md) gives read-only RPC checks for source hash, finality, execution, and state. [`SECURITY.md`](SECURITY.md) lists limitations that testing cannot remove.
