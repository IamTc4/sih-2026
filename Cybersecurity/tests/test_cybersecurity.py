import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app
from rules.engine import ThreatPatternEngine
from audit.hash_chain import AuditLedger

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "wallettrace-cybersecurity"
    assert "active_rules" in data

def test_blacklist_hit():
    resp = client.get("/blacklist/T_LAZARUS_MIXER_01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["match"] is True
    assert "OFAC-SDN" in data["source_case"]

def test_blacklist_clean():
    resp = client.get("/blacklist/T_CLEAN_BENIGN_WALLET_123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["match"] is False
    assert data["source_case"] is None

def test_pattern_mixer_detection():
    engine = ThreatPatternEngine()
    # High fan-in and high fan-out on T_HUB
    edges = [
        {"from": "T1", "to": "T_HUB", "amount": 1000, "tx_hash": "tx1"},
        {"from": "T2", "to": "T_HUB", "amount": 1000, "tx_hash": "tx2"},
        {"from": "T3", "to": "T_HUB", "amount": 1000, "tx_hash": "tx3"},
        {"from": "T_HUB", "to": "OUT1", "amount": 990, "tx_hash": "tx4"},
        {"from": "T_HUB", "to": "OUT2", "amount": 990, "tx_hash": "tx5"},
        {"from": "T_HUB", "to": "OUT3", "amount": 990, "tx_hash": "tx6"},
    ]
    res = engine.detect_mixer(edges)
    assert res is not None
    assert res.signature == "mixer"
    assert res.confidence >= 0.8

def test_pattern_peel_chain_detection():
    engine = ThreatPatternEngine()
    edges = [
        {"from": "A", "to": "B", "amount": 10000, "tx_hash": "tx1"},
        {"from": "B", "to": "C", "amount": 9200, "tx_hash": "tx2"},
        {"from": "C", "to": "D", "amount": 8400, "tx_hash": "tx3"},
    ]
    res = engine.detect_peel_chain(edges)
    assert res is not None
    assert res.signature == "peel_chain"
    assert res.confidence >= 0.85

def test_audit_hash_chain_logging_and_verification():
    ledger = AuditLedger()
    # Log an event
    evt = ledger.log_event("INVESTIGATION_START", {"wallet": "T_SUSPECT_01", "investigator_id": "OFFICER_44"})
    assert evt["logged"] is True
    assert evt["entry_hash"] is not None
    assert evt["prev_hash"] is not None

    # Verify event
    ver = ledger.verify_entry(evt["entry_id"])
    assert ver["valid"] is True
    assert ver["chain_intact"] is True

def test_api_check_patterns_endpoint():
    payload = {
        "address": "T_LAZARUS_MIXER_01",
        "graph_edges": [
            {"from": "T_LAZARUS_MIXER_01", "to": "T_HOP1", "amount": 9500, "tx_hash": "tx1"},
            {"from": "T_HOP1", "to": "T_HOP2", "amount": 8800, "tx_hash": "tx2"}
        ]
    }
    resp = client.post("/check-patterns", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_signal"] >= 0.8
    assert any(f["signature"] == "blacklist_match" for f in data["flags"])
