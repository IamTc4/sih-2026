"""Cybersecurity API Router"""
from fastapi import APIRouter, HTTPException, Path as APIPath
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from rules.engine import ThreatPatternEngine
from audit.hash_chain import AuditLedger

router = APIRouter()
threat_engine = ThreatPatternEngine()
audit_ledger = AuditLedger()

class PatternCheckRequest(BaseModel):
    address: str = Field(..., description="Target wallet address")
    graph_edges: List[Dict[str, Any]] = Field(default_factory=list, description="List of traced transfer edges")

class LogEventRequest(BaseModel):
    event_type: str = Field(..., description="Event classification (e.g. TRACE_EXECUTED, NOTICE_DRAFTED)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event data to be hashed")

@router.get("/health", summary="Health check", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "wallettrace-cybersecurity",
        "version": "1.0.0",
        "total_audit_blocks": len(audit_ledger.chain),
        "active_rules": ["mixer_detection", "peel_chain", "rapid_hopping", "structuring", "blacklist_lookup"]
    }

@router.post("/check-patterns", summary="Scan for fraud patterns & threat signatures", tags=["Threat Intelligence"])
async def check_patterns(req: PatternCheckRequest):
    """Evaluates transaction graph against threat rules: Mixers, Peel Chains, Rapid Hops, Structuring"""
    return threat_engine.analyze(req.address, req.graph_edges)

@router.get("/blacklist/{address}", summary="Check address against law enforcement watchlists", tags=["Threat Intelligence"])
async def check_blacklist(address: str = APIPath(..., description="Wallet address to look up")):
    """Queries law enforcement / OFAC / CBI / ED blacklists"""
    return threat_engine.check_blacklist(address)

@router.post("/log-event", summary="Append event to immutable hash-chain audit ledger", tags=["Evidence Vault"])
async def log_event(req: LogEventRequest):
    """Cryptographically anchors event payload to previous SHA-256 block hash"""
    return audit_ledger.log_event(req.event_type, req.payload)

@router.get("/verify/{entry_id}", summary="Verify cryptographic integrity of an audit entry", tags=["Evidence Vault"])
async def verify_entry(entry_id: str = APIPath(..., description="Audit entry ID (e.g. EVT-0001)")):
    """Verifies that block hash matches payload and chain link is intact"""
    res = audit_ledger.verify_entry(entry_id)
    if not res.get("valid") and "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/audit-trail", summary="Fetch complete audit ledger history", tags=["Evidence Vault"])
async def get_audit_trail():
    """Returns all blocks in the evidence hash chain for courtroom transparency"""
    return audit_ledger.get_all_entries()
