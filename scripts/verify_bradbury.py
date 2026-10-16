"""Read-only finality, execution, source, and state verification for v3.

Run after Bradbury finalization:
    python3 scripts/verify_bradbury.py

This script never signs or sends a transaction. A nonzero exit means the
submission evidence has not passed the full live-network check.
"""

import base64
import hashlib
import json
import sys
import urllib.error
import urllib.request


RPC = "https://rpc-bradbury.genlayer.com"
SOURCE_SHA256 = "671399b0828f6a0a68b4a943b3054d9f515e880b24dea4af7d6f1f5dda1dfbcf"
EVIDENCE_SHA256 = "4d69f65ad6cda4574792aad9fb9b75dc928fc6f48fe88d54b34149e6fd9678d7"
CRITERION = (
    "The webhook design uses HMAC-SHA256 signatures and retries failed "
    "deliveries up to three times with exponential backoff."
)
EVIDENCE_URL = (
    "https://raw.githubusercontent.com/Manablaq/evidence-latch/"
    "3be9be9c360823e9a9479c1254098c5fd7d8f811/evidence/delivery-plan.md"
)

# Finalized protocol receipt execution codes: 1 = return, 2 = agreed user error.
TRANSACTIONS = {
    "primary deployment": ("0x8d9545f98c5c8fddb7c65e79724a42f181d22193e47403758b04a269bb90e1b7", 1),
    "primary verdict": ("0x961aed8cf1b1fb7a168a3928dc591bdc729da68b9883cf05e706bf10fd1130b8", 1),
    "duplicate rejection": ("0xeb5aa1c1328d5e2a09a04a678050ffe54c30ca192d0a22f4ba083e0d2fcdfef2", 2),
    "injection deployment": ("0x464147f81688c638f6317162cc7f73e6710a36318340b67170a6e7676297e4f2", 1),
    "injection verdict": ("0x2a94ba52c96a9b80a163b46df34c1dad586b77a583b2b6dcc224c978802d85bb", 1),
    "negative deployment": ("0x874f78a7b594f5d3f3cf0c5b2679fa06bfdfbf6ff03b6225573ac8cc90f21526", 1),
    "negative verdict": ("0x10f5066268dd55f41d895b156e599bec13ddcfe9b25a0c391e5d405a0a0e92f7", 1),
    "indeterminate deployment": ("0x7ee1988f48defabee2214c50f527a76506da307620e1ad3f18b228ba3f2af145", 1),
    "indeterminate verdict": ("0x7eb558f65dadda26eae7a80dd65e30720889c61277751560c0b4894e1854b7fb", 1),
    "wrong-digest deployment": ("0x39a51d9e250972f5d73ad14babed68838b3f25fa224f72b3f64f627b96d37380", 1),
    "wrong-digest rejection": ("0x1209c8d3faeb0c1be5e08bbd189631accb4eb45dbb4a4ff429a9f36df7d8bee5", 2),
    "oversize deployment": ("0xd3928f00682ead8089c20e5f4317be557d790de615488b59f2e4019a1891b233", 1),
    "oversize rejection": ("0x214f6f0fad4f8dd7e43126eb4733e496e26356dc72e9827119e255c070912f3e", 2),
    "empty deployment": ("0x6c147a4b9b4f538f8af75ba77d57e2fba4c199fadc528d8af3ef07d575f82707", 1),
    "empty rejection": ("0x89c0367db0fdbd13405b8aaa5b9ec5cfefbce5c002bc15c578262e2474ba598f", 2),
    "missing deployment": ("0x114b7248cb1c8feb582e0cd487a8dfd6e49473b903dee3912fd83941983eafcc", 1),
    "missing rejection": ("0xccdd7c5d4c769bda3382c89894a5e065f00a14bd5efaf93cab52d821acef1bac", 2),
    "hash-type rejection": ("0xddb353b123a38631ec7f9d6225c5d74eccbff608bf05d104b7aa0379f8d59584", 2),
    "hash-format rejection": ("0x4cee04e8a708be711d01af2cddf85158616407cefbf5a9c9b1e7d20975d97a93", 2),
    "URL rejection": ("0xd0084ce99a180b8bd34ec9c6c4098ebd9abb32a372916ccb377ec756f25efd7f", 2),
    "criterion rejection": ("0x1de41dfc73cc89ae5e9d7213bce31f2e201cedce6db5a0fa9934a0af2827461e", 2),
}

CONTRACTS = {
    "primary": "0x646564F618f500594F2F3BA1Ed2683DD80909585",
    "injection": "0x78b0365001044744A0371340ad3C25dFeFba4b6b",
    "negative": "0x514b39C5e3167d401FEFE7B72D4B01de3741Bf27",
    "indeterminate": "0x92948dbB60636786Fd30d1DAfF488C002Ab0816F",
    "wrong-digest": "0xdE00AaF19658666B6e8448cfF890fFc138ceDeFc",
    "oversize": "0xA3911F510a99C5068d02056d71aF2C226E216C67",
    "empty": "0xf9979f31C3dF292D934e0a3C9F398Ae9e89fDFe6",
    "missing": "0xEdaBBAe34335A96e862f113CA20A2Dc9909aFC66",
}

EXPECTED_STATES = {
    "primary": ("SATISFIED", True),
    "injection": ("NOT_SATISFIED", True),
    "negative": ("NOT_SATISFIED", True),
    "indeterminate": ("INDETERMINATE", True),
    "wrong-digest": ("PENDING", False),
    "oversize": ("PENDING", False),
    "empty": ("PENDING", False),
    "missing": ("PENDING", False),
}


def uleb128(value: int) -> bytes:
    encoded = bytearray()
    while value >= 128:
        encoded.append((value & 127) | 128)
        value >>= 7
    encoded.append(value)
    return bytes(encoded)


def encode_string(value: str) -> bytes:
    data = value.encode("utf-8")
    return uleb128((len(data) << 3) | 4) + data


def read_call_data(method: str) -> str:
    # GenLayer calldata map {"method": method}, RLP-wrapped with leaderOnly=false.
    calldata = bytes((0x0E, 0x06)) + b"method" + encode_string(method)
    if len(calldata) >= 56:
        raise ValueError("unexpectedly long read method")
    wrapped = bytes((0xC2 + len(calldata), 0x80 + len(calldata))) + calldata + b"\x00"
    return "0x" + wrapped.hex()


def assert_read(address: str, method: str, expected: str | bool) -> None:
    result = rpc("gen_call", {
        "type": "read",
        "from": "0x0000000000000000000000000000000000000000",
        "to": address,
        "data": read_call_data(method),
        "status": "finalized",
    })
    if result["status"]["code"] != 0:
        raise RuntimeError(f"{address} {method}: read failed: {result['status']}")
    expected_data = (
        encode_string(expected) if isinstance(expected, str)
        else (b"\x10" if expected else b"\x08")
    )
    if result["data"].removeprefix("0x") != expected_data.hex():
        raise RuntimeError(f"{address} {method}: unexpected finalized return: {result['data']}")


def rpc(method: str, request: dict) -> object:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": [request]}).encode()
    http = urllib.request.Request(
        RPC,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "curl/8.7.1"},
    )
    with urllib.request.urlopen(http, timeout=20) as response:
        decoded = json.load(response)
    if decoded.get("error") is not None or decoded.get("result") is None:
        raise RuntimeError(f"{method} failed: {decoded.get('error')}")
    return decoded["result"]


def main() -> None:
    for label, (tx_id, expected_execution) in TRANSACTIONS.items():
        receipt = rpc("gen_getTransactionReceipt", {"txId": tx_id})
        if receipt["status"] != 7 or receipt["txExecutionResult"] != expected_execution:
            raise RuntimeError(
                f"{label}: status={receipt['status']}, execution={receipt['txExecutionResult']}; "
                f"expected FINALIZED/7 and execution {expected_execution}"
            )
        print(f"OK receipt: {label}")

    for label, address in CONTRACTS.items():
        code = rpc("gen_getContractCode", {"address": address, "status": "finalized"})
        digest = hashlib.sha256(base64.b64decode(code, validate=True)).hexdigest()
        if digest != SOURCE_SHA256:
            raise RuntimeError(f"{label}: deployed source digest mismatch: {digest}")
        verdict, resolved = EXPECTED_STATES[label]
        assert_read(address, "get_verdict", verdict)
        assert_read(address, "get_resolved", resolved)
        print(f"OK code and finalized getters: {label}")

    assert_read(CONTRACTS["primary"], "get_criterion", CRITERION)
    assert_read(CONTRACTS["primary"], "get_source_url", EVIDENCE_URL)
    assert_read(CONTRACTS["primary"], "get_source_sha256", EVIDENCE_SHA256)

    with urllib.request.urlopen(EVIDENCE_URL, timeout=20) as response:
        evidence_digest = hashlib.sha256(response.read()).hexdigest()
    if evidence_digest != EVIDENCE_SHA256:
        raise RuntimeError(f"pinned evidence digest mismatch: {evidence_digest}")
    print(f"PASS: {len(TRANSACTIONS)} finalized receipts, {len(CONTRACTS)} source/state checks, evidence digest")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, RuntimeError, urllib.error.URLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
