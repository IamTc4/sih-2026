"""
shared/schemas.py
─────────────────
Canonical Pydantic data models shared across ALL WalletTrace modules.

These schemas are the "locked field names" from Master PRD Section 7 Item 1.
Every module MUST import from here instead of defining its own — never redefine
these models locally.

Module port map:
  Agentic AI   — port 8000  (orchestration)
  Blockchain   — port 8001  (graph, clustering, attribution)
  ML           — port 8002  (risk scoring, behavioral clustering)
  Cybersecurity— port 8003  (patterns, blacklist, evidence trail)
  Dashboard    — port 3000  (web UI)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# BLOCKCHAIN MODULE OUTPUTS  (produced by port 8001)
# ─────────────────────────────────────────────────────────────────────────────

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
    """Full response from GET /trace/{address} on port 8001."""
    seed_address: str
    graph_edges:  List[Dict[str, Any]]  # GraphEdge.to_edge_dict() format
    clusters:     List[Cluster]
    attribution:  Attribution


# ─────────────────────────────────────────────────────────────────────────────
# ML MODULE INPUTS & OUTPUTS  (port 8002)
# ─────────────────────────────────────────────────────────────────────────────

class BlockchainFeatures(BaseModel):
    """Blockchain-derived features fed into the ML risk-scoring model."""
    cluster_size:        int   = 1
    hop_depth:           int   = 0
    heuristic_types:     List[str] = []    # e.g. ["deposit_reuse"]
    fund_flow_velocity:  float = 0.0       # total amount / time window (seconds)
    in_degree:           int   = 0
    out_degree:          int   = 0
    tx_count:            int   = 0


class CybersecurityFlags(BaseModel):
    """Cybersecurity-derived pattern flags fed into the ML model."""
    mixer_flag:          bool  = False
    peel_chain_flag:     bool  = False
    rapid_hop_flag:      bool  = False
    structuring_flag:    bool  = False
    blacklist_proximity: int   = -1        # hops to nearest blacklisted addr; -1 = not found
    mixer_confidence:    float = 0.0
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
    plain_text:   str    # human-readable explanation


class BehavioralSimilarity(BaseModel):
    """Behavioral clustering signal (lower-confidence than deterministic)."""
    similar_addresses: List[str] = []
    similarity_score:  float     = 0.0
    method:            str       = "cosine"


class RiskScoreResponse(BaseModel):
    """Output of POST /risk-score on port 8002."""
    address:              str
    risk_score:           float              # 0.0 (clean) – 1.0 (high risk)
    top_factors:          List[RiskFactor]
    confidence:           str               # "high" | "medium" | "low"
    behavioral_similarity: Optional[BehavioralSimilarity] = None
    model_version:        str = "xgboost-v1"


# ─────────────────────────────────────────────────────────────────────────────
# CYBERSECURITY MODULE OUTPUTS  (port 8003)
# ─────────────────────────────────────────────────────────────────────────────

class PatternFlag(BaseModel):
    """One fraud-pattern flag from the Cybersecurity module."""
    signature:   str           # "mixer" | "peel_chain" | "rapid_hop" | "structuring"
    confidence:  float         # 0.0 – 1.0
    evidence:    List[str]     # tx_hashes that triggered this flag


class PatternCheckRequest(BaseModel):
    """Input to POST /check-patterns on port 8003."""
    address:     str
    graph_edges: List[Dict[str, Any]]


class PatternCheckResponse(BaseModel):
    """Output of POST /check-patterns on port 8003."""
    address:     str
    flags:       List[PatternFlag]
    risk_signal: float       # aggregate 0–1 risk contribution


class BlacklistResult(BaseModel):
    """Output of GET /blacklist/{address} on port 8003."""
    address:     str
    match:       bool
    source_case: Optional[str] = None    # CBI/ED case reference


class EvidenceEntry(BaseModel):
    """One entry in the tamper-evident hash-chain log."""
    entry_id:     str
    event_type:   str
    content_hash: str        # SHA-256 of serialised payload
    prev_hash:    str        # SHA-256 of previous entry (chain link)
    timestamp:    str        # ISO-8601
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


# ─────────────────────────────────────────────────────────────────────────────
# AGENT MODULE OUTPUTS  (port 8000)
# ─────────────────────────────────────────────────────────────────────────────

class Citation(BaseModel):
    """One grounded citation in an agent response."""
    tool:    str
    summary: str


class AgentQueryRequest(BaseModel):
    """Input to POST /agent/query on port 8000."""
    session_id: Optional[str] = None
    message:    str


class AgentQueryResponse(BaseModel):
    """Output of POST /agent/query on port 8000."""
    session_id:     str
    response_text:  str
    citations:      List[Citation]
    draft_document: Optional[str] = None
