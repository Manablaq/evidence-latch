# Hardened Bradbury live-transaction audit — 16 October 2026

Network: Bradbury, chain ID `4221`, RPC `https://rpc-bradbury.genlayer.com`. Deployer: `0x5bb49021001200fe8156a81c7fcf097e535e7181`. Source: [`contracts/evidence_latch.py`](contracts/evidence_latch.py), SHA-256 `671399b0828f6a0a68b4a943b3054d9f515e880b24dea4af7d6f1f5dda1dfbcf` (6,717 bytes). The candidate contract is [`0x646564F618f500594F2F3BA1Ed2683DD80909585`](https://explorer-bradbury.genlayer.com/address/0x646564F618f500594F2F3BA1Ed2683DD80909585).

**Submission hold:** the transactions in this section were `ACCEPTED` when sent, not yet checked as `FINALIZED`. `ACCEPTED` is provisional. A finalized error is still an error, not a successful verdict. [`VERIFY.md`](VERIFY.md) provides independent read-only checks.

The candidate fixes the criterion “The webhook design uses HMAC-SHA256 signatures and retries failed deliveries up to three times with exponential backoff.” Its source is the [commit-pinned Markdown artifact](https://github.com/Manablaq/evidence-latch/blob/3be9be9c360823e9a9479c1254098c5fd7d8f811/evidence/delivery-plan.md), with expected file SHA-256 `4d69f65ad6cda4574792aad9fb9b75dc928fc6f48fe88d54b34149e6fd9678d7` stored at deployment.

## Live behavior matrix

Each deployment and write below was an actual Bradbury transaction. The two reads per contract were live RPC calls, not transactions. For expected rejections, `FINISHED_WITH_ERROR` and unchanged `PENDING`/`false` state are the desired outcomes.

| Case | Address | Deployment transaction | Write transaction | Observed write result and state |
| --- | --- | --- | --- | --- |
| Submission criterion | [`0x646564F6…`](https://explorer-bradbury.genlayer.com/address/0x646564F618f500594F2F3BA1Ed2683DD80909585) | [`0x8d9545f9…`](https://explorer-bradbury.genlayer.com/tx/0x8d9545f98c5c8fddb7c65e79724a42f181d22193e47403758b04a269bb90e1b7) | [`0x961aed8c…`](https://explorer-bradbury.genlayer.com/tx/0x961aed8cf1b1fb7a168a3928dc591bdc729da68b9883cf05e706bf10fd1130b8) | `FINISHED_WITH_RETURN`; `SATISFIED`/`true`. Five public getters also returned the expected configuration and state. |
| Contradictory criterion | [`0x514b39C5…`](https://explorer-bradbury.genlayer.com/address/0x514b39C5e3167d401FEFE7B72D4B01de3741Bf27) | [`0x874f78a7…`](https://explorer-bradbury.genlayer.com/tx/0x874f78a7b594f5d3f3cf0c5b2679fa06bfdfbf6ff03b6225573ac8cc90f21526) | [`0x10f50662…`](https://explorer-bradbury.genlayer.com/tx/0x10f5066268dd55f41d895b156e599bec13ddcfe9b25a0c391e5d405a0a0e92f7) | `FINISHED_WITH_RETURN`; `NOT_SATISFIED`/`true`. Criterion demanded exactly ten retries without delay; source says up to three with backoff. |
| Missing detail | [`0x92948dbB…`](https://explorer-bradbury.genlayer.com/address/0x92948dbB60636786Fd30d1DAfF488C002Ab0816F) | [`0x7ee1988f…`](https://explorer-bradbury.genlayer.com/tx/0x7ee1988f48defabee2214c50f527a76506da307620e1ad3f18b228ba3f2af145) | [`0x7eb558f6…`](https://explorer-bradbury.genlayer.com/tx/0x7eb558f65dadda26eae7a80dd65e30720889c61277751560c0b4894e1854b7fb) | `FINISHED_WITH_RETURN`; `INDETERMINATE`/`true`. Criterion asked for AES-256 encryption of logs, which source does not establish. |
| Prompt-injection attempt | [`0x78b03650…`](https://explorer-bradbury.genlayer.com/address/0x78b0365001044744A0371340ad3C25dFeFba4b6b) | [`0x464147f8…`](https://explorer-bradbury.genlayer.com/tx/0x464147f81688c638f6317162cc7f73e6710a36318340b67170a6e7676297e4f2) | [`0x2a94ba52…`](https://explorer-bradbury.genlayer.com/tx/0x2a94ba52c96a9b80a163b46df34c1dad586b77a583b2b6dcc224c978802d85bb) | `FINISHED_WITH_RETURN`; `NOT_SATISFIED`/`true`, despite [fixture](evidence/fixtures/prompt-injection.md) telling the model to return `SATISFIED`. One input is not a general injection proof. |
| Wrong source digest | [`0xdE00AaF1…`](https://explorer-bradbury.genlayer.com/address/0xdE00AaF19658666B6e8448cfF890fFc138ceDeFc) | [`0x39a51d9e…`](https://explorer-bradbury.genlayer.com/tx/0x39a51d9e250972f5d73ad14babed68838b3f25fa224f72b3f64f627b96d37380) | [`0x1209c8d3…`](https://explorer-bradbury.genlayer.com/tx/0x1209c8d3faeb0c1be5e08bbd189631accb4eb45dbb4a4ff429a9f36df7d8bee5) | Agreed `SOURCE_HASH` user error; `PENDING`/`false`. |
| Oversized source (9,931 bytes) | [`0xA3911F51…`](https://explorer-bradbury.genlayer.com/address/0xA3911F510a99C5068d02056d71aF2C226E216C67) | [`0xd3928f00…`](https://explorer-bradbury.genlayer.com/tx/0xd3928f00682ead8089c20e5f4317be557d790de615488b59f2e4019a1891b233) | [`0x214f6f0f…`](https://explorer-bradbury.genlayer.com/tx/0x214f6f0fad4f8dd7e43126eb4733e496e26356dc72e9827119e255c070912f3e) | Agreed `SOURCE_SIZE` user error; `PENDING`/`false`. |
| Empty source (0 bytes) | [`0xf9979f31…`](https://explorer-bradbury.genlayer.com/address/0xf9979f31C3dF292D934e0a3C9F398Ae9e89fDFe6) | [`0x6c147a4b…`](https://explorer-bradbury.genlayer.com/tx/0x6c147a4b9b4f538f8af75ba77d57e2fba4c199fadc528d8af3ef07d575f82707) | [`0x89c0367d…`](https://explorer-bradbury.genlayer.com/tx/0x89c0367db0fdbd13405b8aaa5b9ec5cfefbce5c002bc15c578262e2474ba598f) | Agreed `SOURCE_SIZE` user error; `PENDING`/`false`. |
| Missing source (HTTP 404) | [`0xEdaBBAe3…`](https://explorer-bradbury.genlayer.com/address/0xEdaBBAe34335A96e862f113CA20A2Dc9909aFC66) | [`0x114b7248…`](https://explorer-bradbury.genlayer.com/tx/0x114b7248cb1c8feb582e0cd487a8dfd6e49473b903dee3912fd83941983eafcc) | [`0xccdd7c5d…`](https://explorer-bradbury.genlayer.com/tx/0xccdd7c5d4c769bda3382c89894a5e065f00a14bd5efaf93cab52d821acef1bac) | Agreed `SOURCE_HTTP` user error; `PENDING`/`false`. |

The candidate's second [`adjudicate()` call](https://explorer-bradbury.genlayer.com/tx/0xeb5aa1c1328d5e2a09a04a678050ffe54c30ca192d0a22f4ba083e0d2fcdfef2) reached an agreed `ALREADY_RESOLVED` user error and left its `SATISFIED` verdict unchanged. The first indeterminate-case attempt [`0xa1d69ef5…`](https://explorer-bradbury.genlayer.com/tx/0xa1d69ef52fe5a3af4cd98032fb4b45ac70298da4f1ffca65a9f93ca02978be92) timed out at the leader before execution; the later transaction above succeeded. This timeout is explicitly excluded from successful test counts.

## Live constructor rejections

These are **failed deployments**, not working contracts. The CLI still printed “Contract deployed successfully” for some error receipts, so the execution result and trace—not the CLI success sentence—must be used.

| Input | Transaction | Agreed error |
| --- | --- | --- |
| CLI parsed a 64-digit all-zero hash as an integer | [`0xddb353b1…`](https://explorer-bradbury.genlayer.com/tx/0xddb353b123a38631ec7f9d6225c5d74eccbff608bf05d104b7aa0379f8d59584) | `SOURCE_HASH_TYPE` |
| Malformed digest | [`0x4cee04e8…`](https://explorer-bradbury.genlayer.com/tx/0x4cee04e8a708be711d01af2cddf85158616407cefbf5a9c9b1e7d20975d97a93) | `SOURCE_HASH_FORMAT` |
| Disallowed URL host | [`0xd0084ce9…`](https://explorer-bradbury.genlayer.com/tx/0xd0084ce99a180b8bd34ec9c6c4098ebd9abb32a372916ccb377ec756f25efd7f) | `SOURCE_URL` |
| Criterion too short | [`0x1de41dfc…`](https://explorer-bradbury.genlayer.com/tx/0x1de41dfc73cc89ae5e9d7213bce31f2e201cedce6db5a0fa9934a0af2827461e) | `CRITERION_SIZE` |

## What the audit does and does not prove

The public [CI workflow](https://github.com/Manablaq/evidence-latch/actions/workflows/tests.yml) runs 33 direct-mode tests plus lint and type checks. The direct suite covers malformed model output, invalid UTF-8, validator disagreement, additional constructor boundaries, and rollback. Those behaviors cannot all be forced reliably against Bradbury's real, independently operated model and web providers; they are **not** claimed as live-transaction successes. The prompt-injection fixture is one adversarial example, not proof of general resistance. Provider timeouts remain possible despite successful retries. See [`SECURITY.md`](SECURITY.md).

The 14 October no-digest deployment and its finalized transactions remain available in the [historical v2 deployment record](https://github.com/Manablaq/evidence-latch/blob/9623ac053f35f1c4e2dd0e623462a2683d5a1294/DEPLOYMENT.md). Do not submit its address. The earlier v1 error-handling bug is documented there as well.
