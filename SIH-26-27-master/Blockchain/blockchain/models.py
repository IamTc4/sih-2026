"""
blockchain/models.py
─────────────────────
Shared Pydantic data models used across all layers of the module.
These are the canonical schemas — all layers read/write these objects.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Normalised transaction (output of ingestion layer) ───────────────────────
class NormalizedTx(BaseModel):
    """
    One on-chain transaction, normalised to a chain-agnostic schema.
    Field names match the contract spec from the PRD — do not rename.
    """
    tx_hash:   str
    from_addr: str   = Field(alias="from")
    to_addr:   str   = Field(alias="to")
    amount:    float
    token:     str
    timestamp: str   # ISO-8601 e.g. "2024-10-15T08:23:11Z"
    chain:     str   = "tron"

    model_config = {"populate_by_name": True}

    def to_edge_dict(self) -> dict:
        """Return the dict shape required by the GET /trace/{address} response."""
        return {
            "from":      self.from_addr,
            "to":        self.to_addr,
            "amount":    self.amount,
            "token":     self.token,
            "timestamp": self.timestamp,
            "tx_hash":   self.tx_hash,
            "chain":     self.chain,
        }


# ── Clustering ────────────────────────────────────────────────────────────────
class HeuristicEvidence(BaseModel):
    addr_a:         str
    addr_b:         str
    heuristic_name: str
    evidence_tx:    str


class Cluster(BaseModel):
    cluster_id:         str
    addresses:          List[str]
    heuristic_evidence: List[HeuristicEvidence] = []


# ── Attribution ───────────────────────────────────────────────────────────────
class Attribution(BaseModel):
    exchange_name:   Optional[str]   = None
    deposit_address: Optional[str]   = None
    confidence:      float           = 0.0
    attributed:      bool            = False


# ── Full trace response (GET /trace/{address}) ────────────────────────────────
class TraceResponse(BaseModel):
    seed_address: str
    graph_edges:  List[dict]          # list of NormalizedTx.to_edge_dict()
    clusters:     List[Cluster]
    attribution:  Attribution
