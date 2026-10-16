# Security model and limitations

EvidenceLatch narrows the trust boundary: it accepts only a public GitHub raw Markdown URL pinned to a commit SHA, requires the fetched bytes to match a deployment-time SHA-256 digest, bounds the document to 8 KiB, validates a three-value JSON verdict, and requires validators to independently fetch and classify the source. Its state is immutable after one successful adjudication. It has no payments, privileged owner, upgrades, arbitrary URL host, or cross-contract call.

These controls cannot establish zero weaknesses. In particular:

1. **Correlated model mistakes:** Several validators can agree on a wrong answer. Subtle criteria, incomplete documents, multilingual phrasing, and model updates can change outcomes. `INDETERMINATE` is a requested behavior, not a guarantee.
2. **Prompt injection:** The criterion and fetched Markdown are untrusted. JSON escaping and explicit instructions lower accidental instruction-following risk but cannot eliminate it, especially if validators share model weaknesses.
3. **Source authenticity:** The new digest check binds the decision to exact file bytes; it does not prove that the author or claims in those bytes are trustworthy. The supplied digest itself is chosen by the deployer, not signed by an external authority. A commit-pinned URL can become unavailable if its repository is deleted or made private. The contract does not verify a signed commit.
4. **Availability and fees:** GitHub, the Bradbury RPC, validators, and LLM providers can fail, disagree, or time out. Failed writes can still cost testnet GEN. An unavailable fetch fails without permanently storing `INDETERMINATE`.
5. **Public data:** The criterion and URL are public deployment data; the verdict is public state. Do not use private documents or secrets.
6. **One-shot finality:** A finalized verdict cannot be changed or appealed by a contract method. Use a new deployment for a revised criterion or source. Protocol-level appeal/finality is separate from the contract's one-shot rule.
7. **No off-chain truth guarantee:** This is document-to-criterion classification, not proof of real-world delivery, legal compliance, authorship, or source correctness. Do not use it alone for financial, legal, safety-critical, or identity decisions.
8. **Version coupling:** The pinned runner and CLI target the Bradbury environment used for deployment. Network or tooling upgrades may require a new deployment or new client code.
9. **No formal audit:** Tests and live receipts cannot prove absence of all vulnerabilities.

Report suspected vulnerabilities privately to the repository owner, preferably through a GitHub security advisory if enabled. Do not post exploit details publicly before coordination.
