"""Offline checks for the read-only Bradbury audit's RPC encoding."""

import pytest

from scripts import verify_bradbury


def test_view_call_encoding_matches_live_rpc() -> None:
    assert verify_bradbury.read_call_data("get_verdict") == (
        "0xd6940e066d6574686f645c6765745f7665726469637400"
    )
    assert verify_bradbury.read_call_data("get_resolved") == (
        "0xd7950e066d6574686f64646765745f7265736f6c76656400"
    )


@pytest.mark.parametrize(
    ("expected", "wire_data"),
    [("SATISFIED", "4c534154495346494544"), (True, "10"), (False, "08")],
)
def test_finalized_getter_must_return_expected_value(
    monkeypatch: pytest.MonkeyPatch, expected: str | bool, wire_data: str
) -> None:
    def fake_rpc(method: str, request: dict) -> dict:
        assert method == "gen_call"
        assert request["status"] == "finalized"
        assert request["type"] == "read"
        return {"status": {"code": 0}, "data": wire_data}

    monkeypatch.setattr(verify_bradbury, "rpc", fake_rpc)
    verify_bradbury.assert_read("0x" + "0" * 40, "get_verdict", expected)


def test_finalized_getter_rejects_wrong_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        verify_bradbury,
        "rpc",
        lambda _method, _request: {"status": {"code": 0}, "data": "08"},
    )
    with pytest.raises(RuntimeError, match="unexpected finalized return"):
        verify_bradbury.assert_read("0x" + "0" * 40, "get_resolved", True)
