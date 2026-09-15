"""
CryptoSentinel Cybersecurity API Router
Threat Intelligence · Evidence Trail · RBAC · Fraud Pattern Analysis · UPI Bridge
"""
from fastapi import APIRouter, HTTPException, Path as APIPath, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from rules.engine import ThreatPatternEngine
from audit.hash_chain import AuditLedger
from fraud_detector.detector import FraudDetector, DetectorConfig
from fraud_detector.patterns import TransactionGraph
from evidence_trail.service import EvidenceTrailService
# evidence_trail.api uses create_app() pattern, not APIRouter — we expose its service via inline endpoints below
from policy.rbac import RBACEnforcer, get_current_user, UserContext, require_role
from policy.models import UserRole, DataClassification

router = APIRouter()

# ── Singleton services ────────────────────────────────────────────────────────
threat_engine = ThreatPatternEngine()
audit_ledger = AuditLedger()
fraud_detector = FraudDetector()
evidence_service = EvidenceTrailService(db_path="evidence_trail_main.db")
rbac = RBACEnforcer()




# ════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ════════════════════════════════════════════════════════════════

class PatternCheckRequest(BaseModel):
    address: str = Field(..., description="Target wallet address")
    graph_edges: List[Dict[str, Any]] = Field(default_factory=list,
        description="List of traced transfer edges [{tx_hash, from, to, amount, timestamp}]")

class LogEventRequest(BaseModel):
    event_type: str = Field(..., description="e.g. TRACE_EXECUTED, NOTICE_DRAFTED, CLUSTER_FORMED")
    payload: Dict[str, Any] = Field(default_factory=dict)

class FraudGraphRequest(BaseModel):
    """Submit a raw transaction list for advanced graph-based fraud pattern analysis."""
    transactions: List[Dict[str, Any]] = Field(..., description="""
        List of transactions: [{
            tx_hash: str, from_address: str, to_address: str,
            amount: float, timestamp: float, token: str
        }]
    """)
    blacklist: Optional[List[str]] = Field(default=None,
        description="Optional known bad addresses to check proximity against")

class UPIBridgeRequest(BaseModel):
    """Map a UPI fraud complaint to crypto leads."""
    complaint_text: str = Field(..., description="Raw FIR / NCRP complaint text")
    upi_ids: Optional[List[str]] = Field(default=None, description="Known UPI IDs from complaint")
    victim_phone: Optional[str] = Field(default=None, description="Victim phone (for P2P exchange correlation)")
    amount_inr: Optional[float] = Field(default=None, description="Fraud amount in INR")
    fir_number: Optional[str] = Field(default=None, description="FIR or NCRP complaint number")

class ThreatIntelRequest(BaseModel):
    addresses: List[str] = Field(..., description="List of wallet addresses to screen")

class AccessCheckRequest(BaseModel):
    field_name: str = Field(..., description="Data field to classify")


# ════════════════════════════════════════════════════════════════
# SYSTEM
# ════════════════════════════════════════════════════════════════

@router.get("/health", summary="Health Check", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "cryptosentinel-cybersecurity",
        "version": "2.0.0",
        "modules": {
            "threat_rules": "active",
            "fraud_detector": f"active — {len(fraud_detector.get_pattern_names())} patterns",
            "evidence_trail": "active (SQLite hash-chain)",
            "rbac": "active (5 roles, 4 classification levels)",
            "threat_intel": "active (OFAC + CryptoScamDB)",
            "upi_bridge": "active",
        },
        "active_patterns": fraud_detector.get_pattern_names(),
        "total_audit_blocks": len(audit_ledger.chain),
    }


# ════════════════════════════════════════════════════════════════
# THREAT INTELLIGENCE (Legacy + Graph-Based)
# ════════════════════════════════════════════════════════════════

@router.post("/check-patterns", summary="Legacy: Scan rules-based fraud patterns", tags=["Threat Intelligence"])
async def check_patterns(req: PatternCheckRequest):
    """Evaluates transaction graph against threat rules: Mixers, Peel Chains, Rapid Hops, Structuring."""
    result = threat_engine.analyze(req.address, req.graph_edges)
    # Also log to evidence trail
    evidence_service.log_event("pattern_check", {
        "address": req.address,
        "flags": result.get("flags", []),
        "risk_level": result.get("risk_level", "unknown")
    })
    return result

@router.post("/fraud/analyze", summary="Advanced: Graph-based fraud pattern analysis", tags=["Threat Intelligence"])
async def analyze_fraud_patterns(req: FraudGraphRequest):
    """
    Runs all 5 advanced fraud detectors (MixerTumbler, PeelChain, RapidHopping,
    ScamClusterProximity, Structuring) on a transaction graph.
    Returns ranked DetectionResults with evidence tx hashes and confidence scores.
    """
    # Build TransactionGraph
    graph = TransactionGraph()
    for tx in req.transactions:
        graph.add_transaction(
            tx_hash=tx.get("tx_hash", ""),
            from_addr=tx.get("from_address", tx.get("from", "")),
            to_addr=tx.get("to_address", tx.get("to", "")),
            amount=float(tx.get("amount", 0)),
            timestamp=float(tx.get("timestamp", 0)),
            token=tx.get("token", "USDT"),
        )

    # Update blacklist if provided
    if req.blacklist:
        fraud_detector.update_scam_blacklist(set(req.blacklist))

    results = fraud_detector.detect(graph)

    # Sort by confidence descending
    results_sorted = sorted(results, key=lambda r: r.confidence, reverse=True)

    serialized = []
    for r in results_sorted:
        serialized.append({
            "pattern": r.signature,
            "confidence": round(r.confidence, 4),
            "evidence_tx_hashes": r.evidence[:10],  # cap for response size
            "metadata": r.metadata,
        })

    # Log to evidence trail
    evidence_service.log_event("fraud_graph_analysis", {
        "tx_count": len(req.transactions),
        "patterns_detected": [r["pattern"] for r in serialized if r["confidence"] > 0.5],
        "highest_confidence": serialized[0]["confidence"] if serialized else 0.0,
    })

    return {
        "total_transactions_analyzed": len(req.transactions),
        "patterns_detected": len([r for r in serialized if r["confidence"] > 0.5]),
        "results": serialized,
        "summary": _fraud_summary(serialized),
    }


def _fraud_summary(results: list) -> dict:
    high = [r for r in results if r["confidence"] >= 0.8]
    medium = [r for r in results if 0.5 <= r["confidence"] < 0.8]
    return {
        "high_confidence_flags": [r["pattern"] for r in high],
        "medium_confidence_flags": [r["pattern"] for r in medium],
        "overall_fraud_risk": "HIGH" if high else ("MEDIUM" if medium else "LOW"),
        "recommendation": (
            "IMMEDIATE INVESTIGATION REQUIRED — high-confidence fraud patterns detected."
            if high else
            "FLAG FOR REVIEW — moderate indicators present."
            if medium else
            "LOW RISK — no significant fraud patterns detected."
        )
    }


@router.get("/blacklist/{address}", summary="Check address against watchlists", tags=["Threat Intelligence"])
async def check_blacklist(address: str = APIPath(..., description="Wallet address")):
    """Queries law enforcement / OFAC / CryptoScamDB blacklists."""
    result = threat_engine.check_blacklist(address)
    return result

@router.post("/threat-intel/screen", summary="Screen multiple addresses against live threat feeds", tags=["Threat Intelligence"])
async def screen_addresses(req: ThreatIntelRequest, background_tasks: BackgroundTasks):
    """
    Screens a list of wallet addresses against:
    - OFAC SDN sanctions list (live)
    - CryptoScamDB community blacklist (live)
    - Internal law enforcement watchlist
    Returns per-address hit results with source provenance.
    """
    try:
        from threat_intel.feed import ThreatIntelFeed
        feed = ThreatIntelFeed()
        results = []
        for addr in req.addresses:
            hit = feed.check_address(addr)
            results.append({
                "address": addr,
                "hit": hit is not None,
                "source": hit.source if hit else None,
                "category": hit.category if hit else None,
                "confidence": hit.confidence if hit else 0.0,
                "description": hit.description if hit else "No hit in threat intelligence feeds",
            })

        # Background: log to evidence trail
        background_tasks.add_task(
            evidence_service.log_event,
            "threat_intel_screen",
            {"addresses": req.addresses[:20], "hits": sum(1 for r in results if r["hit"])}
        )
        return {"screened": len(results), "hits": sum(1 for r in results if r["hit"]), "results": results}
    except ImportError:
        # Threat intel module not yet initialized
        return {"screened": len(req.addresses), "hits": 0,
                "results": [{"address": a, "hit": False, "source": None, "description": "Feed not yet loaded"} for a in req.addresses],
                "note": "Threat intel feed initializing — retry in 60 seconds"}


# ════════════════════════════════════════════════════════════════
# EVIDENCE TRAIL (Legacy endpoints kept for backward compatibility)
# ════════════════════════════════════════════════════════════════

@router.post("/log-event", summary="Append event to hash-chain audit ledger", tags=["Evidence Vault"])
async def log_event(req: LogEventRequest):
    """Cryptographically anchors event payload to SHA-256 block hash chain."""
    # Log to both legacy audit_ledger AND new SQLite evidence_service
    legacy_result = audit_ledger.log_event(req.event_type, req.payload)
    new_entry = evidence_service.log_event(req.event_type, req.payload)
    return {
        "legacy_entry": legacy_result,
        "chain_entry": {
            "entry_id": new_entry.entry_id,
            "chain_hash": new_entry.chain_hash,
            "timestamp": new_entry.timestamp,
        }
    }

@router.get("/verify/{entry_id}", summary="Verify cryptographic integrity of an audit entry", tags=["Evidence Vault"])
async def verify_entry(entry_id: str = APIPath(..., description="Audit entry ID")):
    """Verifies block hash matches payload and chain link is intact."""
    try:
        entry_id_int = int(entry_id.replace("EVT-", "").replace("ENTRY-", ""))
        res = evidence_service.verify_entry(entry_id_int)
        return res
    except (ValueError, TypeError):
        res = audit_ledger.verify_entry(entry_id)
        if not res.get("valid") and "error" in res:
            raise HTTPException(status_code=404, detail=res["error"])
        return res

@router.get("/audit-trail", summary="Fetch full audit ledger", tags=["Evidence Vault"])
async def get_audit_trail(limit: int = 100, offset: int = 0):
    """Returns all blocks in evidence hash chain for courtroom transparency."""
    entries = evidence_service.get_entries(limit=limit, offset=offset)
    return {
        "total_returned": len(entries),
        "entries": [e.to_dict() for e in entries],
    }

@router.get("/evidence/chain/verify", summary="Verify entire hash-chain integrity", tags=["Evidence Vault"])
async def verify_full_chain():
    """Verifies every link in the hash chain — use to demonstrate tamper-evidence to court."""
    result = evidence_service.verify_chain()
    return result

@router.post("/evidence/export", summary="Export evidence chain as JSON for court submission", tags=["Evidence Vault"])
async def export_evidence_chain():
    """Exports the complete chain with all hashes for external verification or court submission."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    evidence_service.export_chain(path)
    with open(path, "r") as f:
        data = f.read()
    os.unlink(path)
    import json
    return json.loads(data)


# ════════════════════════════════════════════════════════════════
# RBAC & POLICY
# ════════════════════════════════════════════════════════════════

@router.post("/policy/check-access", summary="Check field access for a role", tags=["RBAC & Policy"])
async def check_access(req: AccessCheckRequest, user: UserContext = Depends(get_current_user)):
    """Returns whether the authenticated user can read/write a given data field."""
    classification = rbac.get_field_classification(req.field_name)
    can_read = user.can_access(classification)
    can_write = user.can_write(classification)
    return {
        "field": req.field_name,
        "classification": classification.value,
        "user_role": user.role.value,
        "can_read": can_read,
        "can_write": can_write,
        "access_denied_reason": None if can_read else f"Role '{user.role.value}' cannot access '{classification.value}' data",
    }

@router.get("/policy/roles", summary="List all RBAC roles and their access levels", tags=["RBAC & Policy"])
async def list_roles():
    """Returns the full RBAC matrix — useful for the dashboard login selector."""
    from policy.models import ROLE_FIELD_ACCESS, ROLE_HIERARCHY
    return {
        "roles": [
            {
                "role": role.value,
                "level": ROLE_HIERARCHY[role],
                "accessible_classifications": [c.value for c in access_set],
                "description": _role_description(role),
            }
            for role, access_set in ROLE_FIELD_ACCESS.items()
        ]
    }

def _role_description(role: UserRole) -> str:
    return {
        UserRole.VIEWER: "Read-only public data (graphs, risk scores)",
        UserRole.ANALYST: "Read public + internal data, write analysis notes",
        UserRole.INVESTIGATOR: "Full access including victim PII and legal notices",
        UserRole.ADMIN: "Full access + user management and system config",
        UserRole.SYSTEM: "Service-to-service full access",
    }.get(role, "Unknown")


# ════════════════════════════════════════════════════════════════
# UPI → CRYPTO BRIDGE (Indian Law Enforcement Intake)
# ════════════════════════════════════════════════════════════════

@router.post("/intake/upi-bridge", summary="Map UPI fraud complaint to crypto investigation leads", tags=["Intake & Triage"])
async def upi_to_crypto_bridge(req: UPIBridgeRequest, background_tasks: BackgroundTasks):
    """
    Parses an Indian banking fraud complaint (FIR/NCRP text) and generates
    actionable crypto investigation leads by correlating UPI IDs and phone numbers
    against known P2P-to-crypto exchange corridors (Binance P2P, WazirX, CoinDCX).
    """
    try:
        from intake.upi_bridge import UPIBridge
        bridge = UPIBridge()
        report = bridge.analyze(
            complaint_text=req.complaint_text,
            upi_ids=req.upi_ids or [],
            phone=req.victim_phone,
            amount_inr=req.amount_inr,
            fir_number=req.fir_number,
        )
        background_tasks.add_task(
            evidence_service.log_event,
            "upi_bridge_intake",
            {"fir": req.fir_number, "leads_found": len(report.get("crypto_leads", []))}
        )
        return report
    except ImportError:
        return _mock_upi_bridge_response(req)


def _mock_upi_bridge_response(req: UPIBridgeRequest) -> dict:
    """Structured mock response when bridge module is loading."""
    return {
        "fir_number": req.fir_number,
        "amount_inr": req.amount_inr,
        "complaint_summary": req.complaint_text[:200] + "..." if len(req.complaint_text) > 200 else req.complaint_text,
        "extracted_upi_ids": req.upi_ids or [],
        "p2p_corridor_analysis": {
            "likely_corridor": "Binance P2P / WazirX",
            "confidence": 0.72,
            "reasoning": "High-frequency small UPI transfers consistent with P2P crypto on-ramp activity"
        },
        "crypto_leads": [
            {
                "lead_type": "suspected_p2p_offramp",
                "exchange": "Binance P2P",
                "confidence": 0.71,
                "action": "Request KYC from Binance India compliance under PMLA Section 12AA",
                "note": "Auto-generated lead — requires investigator verification"
            }
        ],
        "recommended_next_steps": [
            "File Section 91 BNSS requisition to Binance India compliance",
            "Request UPI transaction logs from victim's payment service provider",
            "Check if UPI VPA is linked to crypto exchange KYC",
        ],
        "status": "mock_mode"
    }


# ════════════════════════════════════════════════════════════════
# NCRP & SAHYOG INTEGRATION GATEWAY (SIH26183 Requirement 1.2)
# ════════════════════════════════════════════════════════════════
from intake.ncrp_sahyog_gateway import (
    get_ncrp_sahyog_gateway, NCRPComplaintPayload, NCRPIngestResponse,
    SahyogSyncRequest, SahyogSyncResponse
)

@router.post("/intake/ncrp/webhook", response_model=NCRPIngestResponse, summary="NCRP Automated Webhook Ingestion", tags=["NCRP / SAHYOG Gateway"])
async def ingest_ncrp_webhook(payload: NCRPComplaintPayload, bg: BackgroundTasks):
    """
    Direct MHA NCRP / 1930 Portal Integration Endpoint.
    Ingests live NCRP complaints, generates SHA-256 evidence token, and triages suspect leads.
    """
    gateway = get_ncrp_sahyog_gateway()
    res = gateway.ingest_ncrp_complaint(payload)
    bg.add_task(
        evidence_service.log_event,
        "ncrp_complaint_ingested",
        {"ticket_id": payload.ticket_id, "evidence_hash": res.evidence_hash, "amount": payload.reported_fraud_amount_inr}
    )
    return res

@router.get("/intake/ncrp/ticket/{ticket_id}", summary="Query NCRP Ticket Status", tags=["NCRP / SAHYOG Gateway"])
async def get_ncrp_ticket(ticket_id: str = APIPath(..., description="NCRP Ticket ID (e.g. NCRP-2026-MH-9812)")):
    """Queries verified complaint data and current triage state from NCRP gateway."""
    gateway = get_ncrp_sahyog_gateway()
    ticket = gateway.get_ncrp_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"NCRP ticket '{ticket_id}' not found in gateway cache")
    return ticket

@router.get("/intake/ncrp/tickets", summary="List Active NCRP Complaints", tags=["NCRP / SAHYOG Gateway"])
async def list_ncrp_tickets():
    """Lists recent incoming NCRP cyber fraud complaints ready for forensic trace."""
    gateway = get_ncrp_sahyog_gateway()
    return gateway.list_recent_tickets()

@router.post("/intake/sahyog/sync", response_model=SahyogSyncResponse, summary="Synchronize Freeze with MHA SAHYOG", tags=["NCRP / SAHYOG Gateway"])
async def sync_sahyog_clearinghouse(req: SahyogSyncRequest, bg: BackgroundTasks):
    """
    Dispatches emergency account/wallet freeze requisition to central MHA SAHYOG clearinghouse.
    Notifies NPCI and target VASP nodal officers under Section 91 & 102 BNSS.
    """
    gateway = get_ncrp_sahyog_gateway()
    res = gateway.sync_to_sahyog(req)
    bg.add_task(
        evidence_service.log_event,
        "sahyog_freeze_broadcast",
        {"sahyog_id": res.sahyog_case_id, "target": req.target_wallet_or_vpa, "vasp": req.target_vasp_name}
    )
    return res


# ════════════════════════════════════════════════════════════════
# LEA INTEGRATION: CCTNS, ICJS & GOV SSO (SIH26183 Requirement 5.6)
# ════════════════════════════════════════════════════════════════
from policy.lea_gateway import (
    get_lea_gateway, CCTNSCaseDiaryExportRequest,
    CCTNSExportResponse, GovSSORequest, GovSSOResponse
)

@router.post("/lea/cctns/export", response_model=CCTNSExportResponse, summary="Export CCTNS Form-II Case Diary (XML & JSON)", tags=["LEA / CCTNS Integration"])
async def export_cctns_diary(req: CCTNSCaseDiaryExportRequest, bg: BackgroundTasks):
    """
    Generates standardized CCTNS Case Diary Part-II (Form II) technical evidence report
    in NCRB CCTNS XML standard with ICJS SHA-256 tamper-evident digital seal.
    """
    gateway = get_lea_gateway()
    res = gateway.export_cctns_diary(req)
    bg.add_task(
        evidence_service.log_event,
        "cctns_diary_exported",
        {"dispatch_id": res.cctns_dispatch_id, "fir": req.fir_number, "icjs_seal": res.icjs_sha256_seal}
    )
    return res

@router.post("/auth/gov-sso/authenticate", response_model=GovSSOResponse, summary="National Gov SSO Authentication (Parichay / MeriPehchan)", tags=["LEA / CCTNS Integration"])
async def authenticate_gov_sso(req: GovSSORequest):
    """
    Police Intranet OAuth2/OIDC Single Sign-On adapter for verified police officers.
    Grants RBAC role tokens with automated departmental and security clearance verification.
    """
    gateway = get_lea_gateway()
    return gateway.authenticate_gov_sso(req)


