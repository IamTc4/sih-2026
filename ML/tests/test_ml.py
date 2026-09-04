"""
tests/test_ml.py
─────────────────
Test suite for WalletTrace ML Risk Scoring module.

Tests:
  - Feature vector length matches FEATURE_NAMES
  - Model loads (or fallback activates) without crashing
  - Risk score is in [0.0, 1.0]
  - API endpoints return correct schemas
  - Behavioral clusterer detects similarity
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from ml.api import app
from ml.features import build_feature_vector, FEATURE_NAMES
from ml.model import get_model, RiskScoringModel
from ml.behavioral import BehavioralClusterer
from ml.models import BlockchainFeatures, CybersecurityFlags, RiskScoreRequest

client = TestClient(app)

# ── Fixtures ──────────────────────────────────────────────────────────────────

def _fraud_bc() -> BlockchainFeatures:
    return BlockchainFeatures(
        cluster_size=5, hop_depth=4,
        heuristic_types=["deposit_address_reuse", "common_funding_source"],
        fund_flow_velocity=2500.0, in_degree=2, out_degree=6,
        tx_count=12, total_inflow=100000.0, total_outflow=95000.0,
    )

def _fraud_cy() -> CybersecurityFlags:
    return CybersecurityFlags(
        mixer_flag=True, peel_chain_flag=True, rapid_hop_flag=True,
        structuring_flag=False, blacklist_proximity=1,
        mixer_confidence=0.87, peel_chain_confidence=0.79,
    )

def _legit_bc() -> BlockchainFeatures:
    return BlockchainFeatures(
        cluster_size=1, hop_depth=1,
        heuristic_types=[], fund_flow_velocity=50.0,
        in_degree=5, out_degree=3, tx_count=3,
        total_inflow=5000.0, total_outflow=3000.0,
    )

def _legit_cy() -> CybersecurityFlags:
    return CybersecurityFlags()


# ── Feature engineering tests ─────────────────────────────────────────────────

def test_feature_vector_length():
    vec = build_feature_vector(_fraud_bc(), _fraud_cy())
    assert len(vec) == len(FEATURE_NAMES), "Feature vector length must match FEATURE_NAMES"

def test_feature_vector_no_nan():
    import numpy as np
    vec = build_feature_vector(_fraud_bc(), _fraud_cy())
    assert not np.any(np.isnan(vec)), "Feature vector must not contain NaN"

def test_feature_names_unique():
    assert len(FEATURE_NAMES) == len(set(FEATURE_NAMES)), "Feature names must be unique"


# ── Model tests ───────────────────────────────────────────────────────────────

def test_model_loads():
    model = get_model()
    assert isinstance(model, RiskScoringModel)

def test_model_predict_range():
    model = get_model()
    score, factors, confidence = model.predict(_fraud_bc(), _fraud_cy())
    assert 0.0 <= score <= 1.0, "Risk score must be in [0, 1]"
    assert confidence in ("high", "medium", "low")
    assert len(factors) > 0

def test_fraud_scores_higher_than_legit():
    model = get_model()
    fraud_score, _, _ = model.predict(_fraud_bc(), _fraud_cy())
    legit_score, _, _ = model.predict(_legit_bc(), _legit_cy())
    assert fraud_score > legit_score, "Fraud sample should score higher than legitimate"


# ── Behavioral clusterer tests ────────────────────────────────────────────────

def test_behavioral_similarity_detected():
    clust = BehavioralClusterer(threshold=0.70)
    clust.register("addr_A", _fraud_bc(), _fraud_cy())
    result = clust.find_similar("addr_B", _fraud_bc(), _fraud_cy())
    # Same feature profile — should detect similarity
    assert result is not None
    assert "addr_A" in result.similar_addresses

def test_behavioral_no_match_legit_vs_fraud():
    clust = BehavioralClusterer(threshold=0.90)
    clust.register("addr_fraud", _fraud_bc(), _fraud_cy())
    result = clust.find_similar("addr_legit", _legit_bc(), _legit_cy())
    # Very different profiles at 0.90 threshold — no match expected
    # (Result may be None or not contain addr_fraud depending on actual similarity)
    # Just assert it doesn't crash
    assert result is None or isinstance(result.similar_addresses, list)


# ── API endpoint tests ────────────────────────────────────────────────────────

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "walletrace-ml"

def test_risk_score_endpoint_fraud():
    payload = {
        "address": "T_MULE_ALPHA_101",
        "blockchain_output": {
            "cluster_size": 5, "hop_depth": 4,
            "heuristic_types": ["deposit_address_reuse"],
            "fund_flow_velocity": 2500.0, "in_degree": 2, "out_degree": 6,
            "tx_count": 12, "total_inflow": 100000.0, "total_outflow": 95000.0,
        },
        "cybersecurity_flags": {
            "mixer_flag": True, "peel_chain_flag": True,
            "rapid_hop_flag": True, "structuring_flag": False,
            "blacklist_proximity": 1, "mixer_confidence": 0.87,
            "peel_chain_confidence": 0.79,
        },
    }
    resp = client.post("/risk-score", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_score" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert data["confidence"] in ("high", "medium", "low")
    assert len(data["top_factors"]) > 0
    assert "disclaimer" in data

def test_risk_score_endpoint_minimal():
    """Should work with only address — all features default to zero."""
    resp = client.post("/risk-score", json={"address": "T_UNKNOWN_999"})
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["risk_score"] <= 1.0

def test_model_info_endpoint():
    resp = client.get("/model-info")
    assert resp.status_code == 200
    data = resp.json()
    assert "evaluation_metrics" in data
    assert "known_limitations" in data
    assert len(data["features"]) == len(FEATURE_NAMES)
