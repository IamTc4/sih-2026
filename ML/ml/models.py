"""
ml/models.py
─────────────
Pydantic schemas for the WalletTrace ML Risk Scoring API.

These align with the blockchain schemas/models.py field names so that
the Dashboard and Agent can consume both without translation.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Input schemas ─────────────────────────────────────────────────────────────

class BlockchainFeatures(BaseModel):
    """
    Blockchain-derived features extracted from the POST /trace response.
    The API caller (Agent or Dashboard) assembles these from the blockchain output.
    """
    cluster_size:       int   = Field(1,   description="Number of addresses in the cluster")
    hop_depth:          int   = Field(0,   description="Number of hops in primary trace path")
    heuristic_types:    List[str] = Field(default_factory=list,
                                          description="Names of heuristics that fired (e.g. deposit_address_reuse)")
    fund_flow_velocity: float = Field(0.0, description="Total USDT / elapsed seconds between first and last tx")
    in_degree:          int   = Field(0,   description="Number of unique incoming wallet edges")
    out_degree:         int   = Field(0,   description="Number of unique outgoing wallet edges")
    tx_count:           int   = Field(0,   description="Total transactions in graph for this address")
    total_inflow:       float = Field(0.0, description="Total USDT received")
    total_outflow:      float = Field(0.0, description="Total USDT sent")


class CybersecurityFlags(BaseModel):
    """
    Fraud-pattern flags from the Cybersecurity module (port 8003).
    Set to defaults when the Cybersecurity module is not yet available.
    """
    mixer_flag:               bool  = Field(False, description="Mixer/tumbler pattern detected")
    peel_chain_flag:          bool  = Field(False, description="Peel-chain layering pattern detected")
    rapid_hop_flag:           bool  = Field(False, description="Rapid multi-hop (velocity) detected")
    structuring_flag:         bool  = Field(False, description="Sub-threshold structuring detected")
    blacklist_proximity:      int   = Field(-1,    description="Hops to nearest blacklisted address; -1 = not found")
    mixer_confidence:         float = Field(0.0,   description="Mixer detection confidence 0-1")
    peel_chain_confidence:    float = Field(0.0,   description="Peel-chain detection confidence 0-1")


class RiskScoreRequest(BaseModel):
    """Input to POST /risk-score."""
    address:             str
    blockchain_output:   BlockchainFeatures  = Field(default_factory=BlockchainFeatures)
    cybersecurity_flags: CybersecurityFlags  = Field(default_factory=CybersecurityFlags)


# ── Output schemas ────────────────────────────────────────────────────────────

class RiskFactor(BaseModel):
    """One contributing factor in the risk score explanation."""
    feature:      str   = Field(..., description="Feature name (matches training feature column)")
    contribution: float = Field(..., description="SHAP-style contribution to final score")
    plain_text:   str   = Field(..., description="Human-readable explanation for the dashboard")


class BehavioralSimilarity(BaseModel):
    """Behavioral clustering signal — lower confidence than deterministic heuristics."""
    similar_addresses: List[str] = Field(default_factory=list,
                                         description="Addresses with similar behavioral fingerprints")
    similarity_score:  float     = Field(0.0, description="Cosine similarity 0-1")
    method:            str       = Field("cosine", description="Algorithm used")
    note:              str       = Field(
        "LOWER CONFIDENCE than deterministic clustering — treat as investigative lead only",
        description="Disclaimer, always shown in UI"
    )


class FraudTypology(BaseModel):
    """Classified cyber fraud typology according to SIH26183 problem statement"""
    typology_name:           str       = Field(..., description="e.g. 'Task-Based Fraud / Job Scam', 'P2P Crypto Corridor / Mule Ring'")
    typology_code:           str       = Field(..., description="Standard code e.g. 'TASK_FRAUD', 'INVESTMENT_SCAM', 'P2P_MULE', 'MIXER_LAUNDERING'")
    confidence:              float     = Field(..., ge=0.0, le=1.0, description="Confidence in typology classification")
    indicators:              List[str] = Field(default_factory=list, description="Forensic indicators triggered")
    modus_operandi:          str       = Field(..., description="Summary of scam operation pattern")
    recommended_legal_action: str      = Field(..., description="Statutory action recommended under BNSS / PMLA")


class RiskScoreResponse(BaseModel):
    """Output of POST /risk-score — consumed by Agent's get_risk_score tool and Dashboard."""
    address:               str
    risk_score:            float              = Field(..., ge=0.0, le=1.0,
                                                     description="Calibrated risk score 0 (clean) to 1 (high risk)")
    top_factors:           List[RiskFactor]
    confidence:            str               = Field(..., description="'high' | 'medium' | 'low'")
    behavioral_similarity: Optional[BehavioralSimilarity] = None
    fraud_typology:        Optional[FraudTypology]        = None
    model_version:         str               = Field("xgboost-v1", description="Trained model identifier")
    disclaimer:            str               = Field(
        "Score produced by an XGBoost model trained on public fraud datasets. "
        "Not a legal determination. Requires investigator review.",
        description="Always shown in UI"
    )


class ModelInfoResponse(BaseModel):
    """Output of GET /model-info — model card for transparency."""
    model_version:      str
    algorithm:          str
    training_data:      str
    labels:             Dict[str, Any]
    evaluation_metrics: Dict[str, Any]
    features:           List[str]
    known_limitations:  List[str]
    last_trained:       str
