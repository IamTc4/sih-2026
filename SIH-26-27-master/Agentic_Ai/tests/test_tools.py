"""
tests/test_tools.py
────────────────────
Unit tests for every mocked tool stub.
Validates that each function returns exactly the contracted schema with the
correct types so that teammate integration is a drop-in swap.
"""

import pytest
from walletrace.tools.mocks import (
    trace_wallet,
    get_cluster,
    get_risk_score,
    identify_exchange,
    check_blacklist,
    draft_legal_notice,
    log_event,
    verify_entry,
)


ETH_ADDR = "0xABCDEF1234567890ABCDEF1234567890ABCDEF15"  # ends in 5 → attributed


class TestTraceWallet:
    def test_returns_required_keys(self):
        result = trace_wallet(ETH_ADDR)
        assert "graph_edges" in result
        assert "seed_address" in result

    def test_seed_address_echoed(self):
        result = trace_wallet(ETH_ADDR)
        assert result["seed_address"] == ETH_ADDR

    def test_edge_schema(self):
        result = trace_wallet(ETH_ADDR)
        for edge in result["graph_edges"]:
            assert "from" in edge
            assert "to" in edge
            assert isinstance(edge["amount"], float)
            assert "token" in edge
            assert "timestamp" in edge
            assert "tx_hash" in edge
            assert "chain" in edge

    def test_at_least_one_edge(self):
        result = trace_wallet(ETH_ADDR)
        assert len(result["graph_edges"]) >= 1


class TestGetCluster:
    def test_returns_required_keys(self):
        result = get_cluster(ETH_ADDR)
        assert "cluster_id" in result
        assert "addresses" in result
        assert "heuristic_evidence" in result

    def test_seed_in_addresses(self):
        result = get_cluster(ETH_ADDR)
        assert ETH_ADDR in result["addresses"]

    def test_heuristic_evidence_schema(self):
        result = get_cluster(ETH_ADDR)
        for ev in result["heuristic_evidence"]:
            assert "addr_a" in ev
            assert "addr_b" in ev
            assert "heuristic_name" in ev
            assert "evidence_tx" in ev


class TestGetRiskScore:
    def test_returns_required_keys(self):
        result = get_risk_score(ETH_ADDR)
        assert "risk_score" in result
        assert "top_factors" in result
        assert "confidence" in result

    def test_score_in_range(self):
        result = get_risk_score(ETH_ADDR)
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_factor_schema(self):
        result = get_risk_score(ETH_ADDR)
        for factor in result["top_factors"]:
            assert "feature" in factor
            assert "contribution" in factor
            assert isinstance(factor["contribution"], float)

    def test_cluster_scores_higher(self):
        score_addr = get_risk_score(ETH_ADDR)["risk_score"]
        score_cluster = get_risk_score("CLU_ABCDEF")["risk_score"]
        assert score_cluster > score_addr


class TestIdentifyExchange:
    def test_attributed_address_schema(self):
        # Address ending in 5 → attributed=True in mock
        addr = ETH_ADDR
        result = identify_exchange(addr)
        assert result["attributed"] is True
        assert result["exchange_name"] is not None
        assert result["deposit_address"] is not None
        assert 0.0 <= result["confidence"] <= 1.0

    def test_unattributed_nulls_enforced(self):
        # Address ending in a letter → attributed=False, nulls must be enforced
        addr = "0xABCDEF1234567890ABCDEF1234567890ABCDEFaa"
        result = identify_exchange(addr)
        assert result["attributed"] is False
        # CONTRACT: nulls must be None when not attributed
        assert result["exchange_name"] is None, (
            "exchange_name MUST be None when attributed=False"
        )
        assert result["deposit_address"] is None, (
            "deposit_address MUST be None when attributed=False"
        )

    def test_confidence_field_present(self):
        result = identify_exchange(ETH_ADDR)
        assert "confidence" in result


class TestCheckBlacklist:
    def test_blacklisted_address(self):
        result = check_blacklist("0xEXCHANGE_DEPOSIT_abcdef")
        assert result["match"] is True
        assert result["source_case"] is not None

    def test_clean_address(self):
        result = check_blacklist("0xCLEAN_ADDRESS_123")
        assert result["match"] is False
        assert result["source_case"] is None


class TestDraftLegalNotice:
    def test_required_keys(self):
        result = draft_legal_notice("CASE-001", "TestExchange", "Some evidence here")
        assert "draft_text" in result
        assert "watermark" in result

    def test_watermark_exact(self):
        result = draft_legal_notice("CASE-001", "TestExchange", "evidence")
        assert result["watermark"] == "DRAFT - REQUIRES INVESTIGATOR REVIEW"

    def test_draft_contains_case_id(self):
        result = draft_legal_notice("MY-CASE-42", "ExchangeX", "evidence")
        assert "MY-CASE-42" in result["draft_text"]

    def test_draft_contains_exchange_name(self):
        result = draft_legal_notice("CASE-001", "CryptoExIndia", "evidence")
        assert "CryptoExIndia" in result["draft_text"]

    def test_draft_contains_evidence(self):
        evidence = "Risk score 0.87, cluster CLU_ABC"
        result = draft_legal_notice("CASE-001", "TestEx", evidence)
        assert evidence in result["draft_text"]


class TestLogEvent:
    def test_required_keys(self):
        result = log_event("test_event", {"key": "value"})
        assert "entry_hash" in result
        assert "logged" in result

    def test_logged_true(self):
        result = log_event("test_event", {})
        assert result["logged"] is True

    def test_entry_hash_is_string(self):
        result = log_event("test_event", {"foo": "bar"})
        assert isinstance(result["entry_hash"], str)
        assert len(result["entry_hash"]) == 64  # SHA-256 hex


class TestVerifyEntry:
    def test_valid_entry(self):
        result = verify_entry("some-entry-hash-abc123")
        assert result["valid"] is True
        assert result["chain_intact"] is True

    def test_empty_entry_invalid(self):
        result = verify_entry("")
        assert result["valid"] is False
        assert result["chain_intact"] is False
