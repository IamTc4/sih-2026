"""
shared/schemas.py
Canonical Pydantic models for WalletTrace (SIH 2026 Problem Statement 26183)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── BLOCKCHAIN MODULE OUTPUTS (port 8000 / 8001) ───────────────────────────────

class GraphEdge(BaseModel):
    """One on-chain transfer edge in the transaction graph."""
    from_addr: str = Field(alias="from")
    to_addr:   str = Field(alias="to")
    amount:    float
    token:     str
    timestamp: str          # ISO-8601
    tx_hash:   str
    chain:     str = "tron"

    model_config = {"populate_by_name": True}


class HeuristicEvidence(BaseModel):
    """Evidence record for one deterministic heuristic merge."""
    addr_a:         str
    addr_b:         str
    heuristic_name: str     # "deposit_reuse" | "common_input_ownership"
    evidence_tx:    str


class Cluster(BaseModel):
    """Address cluster produced by the Blockchain module."""
    cluster_id:         str
    addresses:          List[str]
    heuristic_evidence: List[HeuristicEvidence] = []


class Attribution(BaseModel):
    """Exchange attribution result from the Blockchain module."""
    exchange_name:   Optional[str]   = None
    deposit_address: Optional[str]   = None
    confidence:      float           = 0.0
    attributed:      bool            = False


class TraceResponse(BaseModel):
    """Full response from GET /trace/{address}."""
    seed_address: str
    graph_edges:  List[Dict[str, Any]]
    clusters:     List[Cluster]
    attribution:  Attribution


# ── ML MODULE INPUTS & OUTPUTS (port 8002) ────────────────────────────────────

class BlockchainFeatures(BaseModel):
    """Blockchain-derived features fed into the ML risk-scoring model."""
    cluster_size:        int   = 1
    hop_depth:           int   = 0
    heuristic_types:     List[str] = []
    fund_flow_velocity:  float = 0.0
    in_degree:           int   = 0
    out_degree:          int   = 0
    tx_count:            int   = 0


class CybersecurityFlags(BaseModel):
    """Cybersecurity-derived pattern flags fed into the ML model."""
    mixer_flag:            bool  = False
    peel_chain_flag:       bool  = False
    rapid_hop_flag:        bool  = False
    structuring_flag:      bool  = False
    blacklist_proximity:   int   = -1
    mixer_confidence:      float = 0.0
    peel_chain_confidence: float = 0.0


class RiskScoreRequest(BaseModel):
    """Input to POST /risk-score on port 8002."""
    address:              str
    blockchain_output:    BlockchainFeatures   = Field(default_factory=BlockchainFeatures)
    cybersecurity_flags:  CybersecurityFlags   = Field(default_factory=CybersecurityFlags)


class RiskFactor(BaseModel):
    """One contributing factor to a risk score."""
    feature:      str
    contribution: float
    plain_text:   str


class BehavioralSimilarity(BaseModel):
    """Behavioral clustering signal."""
    similar_addresses: List[str] = []
    similarity_score:  float     = 0.0
    method:            str       = "cosine"


class RiskScoreResponse(BaseModel):
    """Output of POST /risk-score on port 8002."""
    address:              str
    risk_score:           float
    top_factors:          List[RiskFactor]
    confidence:           str
    behavioral_similarity: Optional[BehavioralSimilarity] = None
    model_version:        str = "xgboost-v1"


# ── CYBERSECURITY MODULE OUTPUTS (port 8003) ──────────────────────────────────

class PatternFlag(BaseModel):
    """One fraud-pattern flag from the Cybersecurity module."""
    signature:   str
    confidence:  float
    evidence:    List[str]


class PatternCheckRequest(BaseModel):
    """Input to POST /check-patterns on port 8003."""
    address:     str
    graph_edges: List[Dict[str, Any]]


class PatternCheckResponse(BaseModel):
    """Output of POST /check-patterns on port 8003."""
    address:     str
    flags:       List[PatternFlag]
    risk_signal: float


class BlacklistResult(BaseModel):
    """Output of GET /blacklist/{address} on port 8003."""
    address:     str
    match:       bool
    source_case: Optional[str] = None


class EvidenceEntry(BaseModel):
    """One entry in the tamper-evident hash-chain log."""
    entry_id:     str
    event_type:   str
    content_hash: str
    prev_hash:    str
    timestamp:    str
    logged:       bool = True


class LogEventRequest(BaseModel):
    """Input to POST /log-event on port 8003."""
    event_type: str
    payload:    Dict[str, Any]


class VerifyResponse(BaseModel):
    """Output of GET /verify/{entry_id} on port 8003."""
    entry_id:     str
    valid:        bool
    chain_intact: bool


# ── AGENT MODULE OUTPUTS (port 8001 / 8000) ────────────────────────────────────

class Citation(BaseModel):
    """One grounded citation in an agent response."""
    tool:    str
    summary: str


class AgentQueryRequest(BaseModel):
    """Input to POST /agent/query on port 8001."""
    session_id: Optional[str] = None
    message:    str


class AgentQueryResponse(BaseModel):
    """Output of POST /agent/query on port 8001."""
    session_id:     str
    response_text:  str
    citations:      List[Citation]
    draft_document: Optional[str] = None
