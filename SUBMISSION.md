# Portal submission — Intelligent Contract

**Hold submission until Bradbury finality checks pass.** The corrected-source transactions have successful consensus decisions, but `ACCEPTED` is provisional. The signed-in Portal's exact required fields and steward decision cannot be verified from public pages.

Suggested contribution date: `14/10/2026`. Suggested title: **EvidenceLatch — Consensus-Gated Review of Immutable Public Evidence**.

## Paste-ready description (under 1,000 characters)

> EvidenceLatch is a standalone GenLayer Intelligent Contract on Bradbury. It fixes one acceptance criterion and a GitHub Markdown file pinned to a commit SHA at deployment. Validators independently fetch the same public file, classify whether it satisfies, contradicts, or lacks enough information for the criterion, and agree on a bounded verdict. A successful adjudication permanently changes contract state from PENDING to SATISFIED, NOT_SATISFIED, or INDETERMINATE; duplicate adjudication is rejected. The public repo includes source, 28 direct-mode tests, CI lint/type checks, deployed-source verification, live transactions for all three verdicts and error paths, and candid security limits. The contract holds no funds and does not prove off-chain truth or legal compliance.

## Four evidence URLs

1. Public repository: https://github.com/Manablaq/evidence-latch
2. Submission contract: https://explorer-bradbury.genlayer.com/address/0x312BA09952d43cB6BDa054D29b1A1474fCbB90F9
3. Live successful verdict: https://explorer-bradbury.genlayer.com/tx/0xfaa48cc436096e8d9fa14868860e87062d52628792fd007693c0070531a1fb0e
4. Full deployment and test evidence: https://github.com/Manablaq/evidence-latch/blob/main/DEPLOYMENT.md

Do not submit any v1 audit address. Do not describe an accepted but unfinalized transaction as final, an error as a verdict, or the AI classification as proof of the real-world claims in the document. See [`SECURITY.md`](SECURITY.md) and [`VERIFY.md`](VERIFY.md).
