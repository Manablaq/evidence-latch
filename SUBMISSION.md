# Portal submission — Intelligent Contract

**Submission on hold as of 16 October 2026.** The hardened candidate is deployed at `0x646564F618f500594F2F3BA1Ed2683DD80909585`, but its live-test transactions must be finalized and independently checked before the address is recommended. One indeterminate-case attempt hit a leader timeout before a later retry succeeded. Do not use the older address or paste-ready text below until this page is updated. No finite test set can certify zero model errors, prompt-injection risk, or future network timeouts. The signed-in Portal's private rules and a steward's decision also cannot be guaranteed from public evidence.

Proposed contribution date after verification: `16/10/2026`. Suggested title: **EvidenceLatch — Consensus-Gated Review of Hash-Pinned Public Evidence**.

## Paste-ready description (under 1,000 characters)

> EvidenceLatch is a standalone GenLayer Intelligent Contract on Bradbury. It fixes one acceptance criterion, a GitHub Markdown URL pinned to a commit, and the exact file's SHA-256 digest at deployment. Validators independently fetch and hash the file, then classify whether it satisfies, contradicts, or lacks enough information for the criterion. A successful adjudication permanently changes state from PENDING to SATISFIED, NOT_SATISFIED, or INDETERMINATE; duplicate adjudication is rejected. The public repo includes source, 33 direct-mode tests, CI lint/type checks, live transactions for all three verdicts and several error paths, and candid security limits. It holds no funds and does not prove off-chain truth or legal compliance.

## Four evidence URLs

1. Public repository: https://github.com/Manablaq/evidence-latch
2. Candidate contract (not yet submission-approved): https://explorer-bradbury.genlayer.com/address/0x646564F618f500594F2F3BA1Ed2683DD80909585
3. Candidate live verdict (finality pending): https://explorer-bradbury.genlayer.com/tx/0x961aed8cf1b1fb7a168a3928dc591bdc729da68b9883cf05e706bf10fd1130b8
4. Full deployment and test evidence: https://github.com/Manablaq/evidence-latch/blob/main/LIVE_AUDIT_2026-10-16.md

Do not submit any v1 or v2 audit address. Do not describe an accepted but unfinalized transaction as final, an error as a verdict, or the AI classification as proof of the real-world claims in the document. See [`SECURITY.md`](SECURITY.md) and [`VERIFY.md`](VERIFY.md).
