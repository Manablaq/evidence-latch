import json
from pathlib import Path

import pytest


CONTRACT = Path(__file__).resolve().parents[1] / "contracts" / "evidence_latch.py"
URL = (
    "https://raw.githubusercontent.com/Manablaq/evidence-latch/"
    + "a" * 40
    + "/evidence/delivery-plan.md"
)
CRITERION = "The design uses signed webhooks and capped retries with backoff."
SOURCE = (
    "The service sends signed webhooks. Failed deliveries retry up to three "
    "times with exponential backoff. Delivery logs are kept for 30 days."
)


def deploy(direct_vm, direct_deploy, criterion=CRITERION, source_url=URL):
    direct_vm.strict_mocks = True
    direct_vm.check_pickling = True
    return direct_deploy(str(CONTRACT), criterion, source_url, sdk_version="v0.2.16")


def mock_source_and_verdict(direct_vm, verdict, body=SOURCE):
    direct_vm.mock_web(r"raw\.githubusercontent\.com", {"status": 200, "body": body})
    direct_vm.mock_llm(
        r"(?s).*EVIDENCE_LATCH_V1.*", json.dumps({"verdict": verdict})
    )


def test_initial_state_and_immutable_configuration(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    assert contract.get_criterion() == CRITERION
    assert contract.get_source_url() == URL
    assert contract.get_resolved() is False
    assert contract.get_verdict() == "PENDING"


@pytest.mark.parametrize("verdict", ["SATISFIED", "NOT_SATISFIED", "INDETERMINATE"])
def test_all_verdicts_persist_after_consensus(direct_vm, direct_deploy, verdict):
    contract = deploy(direct_vm, direct_deploy)
    mock_source_and_verdict(direct_vm, verdict)

    assert contract.adjudicate() == verdict
    assert contract.get_resolved() is True
    assert contract.get_verdict() == verdict
    assert len(direct_vm._captured_validators) == 1
    assert direct_vm.run_validator() is True

    with direct_vm.expect_revert("ALREADY_RESOLVED"):
        contract.adjudicate()
    assert contract.get_verdict() == verdict


def test_validator_rejects_disagreement(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    mock_source_and_verdict(direct_vm, "SATISFIED")
    assert contract.adjudicate() == "SATISFIED"
    assert direct_vm.run_validator(leader_result="NOT_SATISFIED") is False
    assert direct_vm.run_validator(leader_result="INVALID") is False
    assert direct_vm.run_validator(leader_error=ValueError("failed")) is False
    direct_vm.clear_mocks()
    mock_source_and_verdict(direct_vm, "NOT_SATISFIED")
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize(
    "payload,error",
    [
        ({"verdict": "ALLOW"}, "MODEL_VERDICT"),
        ({"verdict": None}, "MODEL_VERDICT"),
        ({"verdict": []}, "MODEL_VERDICT"),
        ({"verdict": "SATISFIED", "reason": "extra"}, "MODEL_KEYS"),
        (["SATISFIED"], "MODEL_NOT_OBJECT"),
    ],
)
def test_invalid_model_output_rolls_back(direct_vm, direct_deploy, payload, error):
    contract = deploy(direct_vm, direct_deploy)
    direct_vm.mock_web(r"raw\.githubusercontent\.com", {"status": 200, "body": SOURCE})
    direct_vm.mock_llm(r"(?s).*EVIDENCE_LATCH_V1.*", json.dumps(payload))

    with direct_vm.expect_revert(error):
        contract.adjudicate()
    assert contract.get_resolved() is False
    assert contract.get_verdict() == "PENDING"


@pytest.mark.parametrize(
    "status,body,error",
    [
        (404, "not found", "SOURCE_HTTP"),
        (200, "", "SOURCE_SIZE"),
        (200, "x" * 8193, "SOURCE_SIZE"),
        (200, b"\xff", "SOURCE_UTF8"),
    ],
)
def test_unavailable_or_invalid_source_rolls_back(
    direct_vm, direct_deploy, status, body, error
):
    contract = deploy(direct_vm, direct_deploy)
    direct_vm.mock_web(r"raw\.githubusercontent\.com", {"status": status, "body": body})
    with direct_vm.expect_revert(error):
        contract.adjudicate()
    assert contract.get_resolved() is False
    assert contract.get_verdict() == "PENDING"


@pytest.mark.parametrize(
    "criterion,error",
    [
        ("short", "CRITERION_SIZE"),
        ("x" * 257, "CRITERION_SIZE"),
        (" " + CRITERION, "CRITERION_WHITESPACE"),
        (CRITERION + "\n", "CRITERION_WHITESPACE"),
        ("A criterion with\ta tab must be rejected.", "CRITERION_CONTROL"),
        ("A criterion with\u202ea format mark is rejected.", "CRITERION_CONTROL"),
    ],
)
def test_rejects_invalid_criterion(direct_vm, direct_deploy, criterion, error):
    with direct_vm.expect_revert(error):
        deploy(direct_vm, direct_deploy, criterion=criterion)


@pytest.mark.parametrize(
    "source_url,error",
    [
        ("http://raw.githubusercontent.com/x/y/z/file.md", "SOURCE_URL"),
        ("https://example.com/a.md", "SOURCE_URL"),
        ("https://raw.githubusercontent.com/owner/repo/main/file.md", "SOURCE_COMMIT"),
        ("https://raw.githubusercontent.com/owner/repo/" + "a" * 40, "SOURCE_PATH"),
        ("https://raw.githubusercontent.com/owner/repo/" + "a" * 40 + "/../x.md", "SOURCE_SEGMENT"),
        (URL + "?token=secret", "SOURCE_SEGMENT"),
        (URL.replace(".md", ".txt"), "SOURCE_EXTENSION"),
        (URL.replace("githubusercontent.com", "githubusercontent.com@evil.example"), "SOURCE_URL"),
    ],
)
def test_rejects_unsafe_or_mutable_source_url(direct_vm, direct_deploy, source_url, error):
    with direct_vm.expect_revert(error):
        deploy(direct_vm, direct_deploy, source_url=source_url)
