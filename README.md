# EvidenceLatch

EvidenceLatch is a standalone GenLayer intelligent contract that checks one public Markdown artifact against one fixed acceptance criterion. The criterion and evidence URL are frozen at deployment. A single `adjudicate()` write asks independent validators to inspect the same GitHub file pinned to a 40-character commit SHA, then permanently stores `SATISFIED`, `NOT_SATISFIED`, or `INDETERMINATE` in contract state.

The contract is intended as a small acceptance-decision primitive for public deliverables. It does **not** prove authorship, factual truth, legal compliance, or that work exists outside the linked document. It does not hold funds or release payment.

## Decision and state transition

| Before adjudication | Consensus result | Final state |
| --- | --- | --- |
| `resolved = false`, `verdict = PENDING` | `SATISFIED` | `resolved = true`, `verdict = SATISFIED` |
| `resolved = false`, `verdict = PENDING` | `NOT_SATISFIED` | `resolved = true`, `verdict = NOT_SATISFIED` |
| `resolved = false`, `verdict = PENDING` | `INDETERMINATE` | `resolved = true`, `verdict = INDETERMINATE` |
| `resolved = false`, `verdict = PENDING` | Fetch/model/consensus failure | No state change; retry is possible |
| `resolved = true` | Any later `adjudicate()` | Rejected with `ALREADY_RESOLVED` |

`SATISFIED` means the document explicitly establishes the whole criterion. `NOT_SATISFIED` means it explicitly contradicts a material part. `INDETERMINATE` means the document is silent, ambiguous, or incomplete. These are bounded classifications, not guarantees of semantic correctness.

The source must be a public `.md` file under `https://raw.githubusercontent.com/OWNER/REPO/COMMIT/PATH`, where `COMMIT` is a 40-character lowercase hexadecimal commit SHA. The contract rejects mutable branch references, other hosts, unsafe path segments, responses other than HTTP 200, empty or over-8-KiB files, invalid UTF-8, and malformed model output. The LLM receives JSON-escaped criterion and document text as untrusted data. Validators independently fetch and classify the same pinned URL, comparing only the three-value verdict. State changes only after consensus.

## Interface

| Method | Kind | Purpose |
| --- | --- | --- |
| constructor `(criterion: str, source_url: str)` | deployment | Freeze the question and evidence URL |
| `adjudicate() -> str` | write | Resolve the criterion once and store the verdict |
| `get_criterion() -> str` | view | Read the fixed criterion |
| `get_source_url() -> str` | view | Read the fixed evidence URL |
| `get_resolved() -> bool` | view | Read whether adjudication completed |
| `get_verdict() -> str` | view | Read the stored decision |

Source: [`contracts/evidence_latch.py`](contracts/evidence_latch.py). The public sample artifact is [`evidence/delivery-plan.md`](evidence/delivery-plan.md). The `Depends` header pins the Bradbury-compatible Python runner.

## Reproduce local tests

Use Python 3.12:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
GENVM_VERSION=v0.3.0-rc4 .venv/bin/pytest tests/ -q
```

The direct-mode tests mock web and model responses. They check control flow, state persistence/rollback, validator disagreement, response schema, URL restrictions, and one-shot behavior. They do not prove live network behavior or model accuracy. See [`SECURITY.md`](SECURITY.md) for limitations. Live deployment and transaction evidence will be documented in [`DEPLOYMENT.md`](DEPLOYMENT.md) once finalized.
