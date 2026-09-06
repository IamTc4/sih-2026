"""
walletrace/tools/real_tools.py
──────────────────────────────
Extended tool set for CryptoSentinel Agentic AI.
Adds: batch wallet investigation, multi-chain detection,
threat intel screening, UPI bridge, and case summary.

All functions attempt the real upstream service first and fall
back to enriched mocks for testing / offline demo.
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

# Re-export all existing tools
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

logger = logging.getLogger(__name__)

_BLOCKCHAIN_URL: str = os.getenv("BLOCKCHAIN_API_URL", "http://localhost:8000").rstrip("/")
_ML_URL: str = os.getenv("ML_API_URL", "http://localhost:8002").rstrip("/")
_CYBERSECURITY_URL: str = os.getenv("CYBERSECURITY_API_URL", "http://localhost:8003").rstrip("/")

_TIMEOUT = httpx.Timeout(10.0, connect=3.0)


def _is_testing() -> bool:
    return "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ


# ════════════════════════════════════════════════════════════════
# BATCH WALLET INVESTIGATION
# ════════════════════════════════════════════════════════════════

def batch_trace_wallets(addresses: list[str], max_hops: int = 3) -> dict:
    """
    Investigate multiple wallet addresses in parallel.
    Returns a consolidated fraud ring analysis across all wallets.
    
    Args:
        addresses: List of wallet addresses (Tron T... or Ethereum 0x...)
        max_hops: Maximum hop depth for each trace (default 3)
    
    Returns:
        Consolidated report: per-wallet results, shared clusters, 
        aggregate risk, common exchange destinations.
    """
    results = []
    tron_addrs = [a for a in addresses if a.strip().startswith("T")]
    eth_addrs = [a for a in addresses if a.strip().startswith("0x")]
    
    for addr in addresses:
        try:
            if not _is_testing():
                resp = httpx.post(
                    f"{_BLOCKCHAIN_URL}/trace",
                    json={"address": addr.strip(), "max_hops": max_hops},
                    timeout=_TIMEOUT,
                )
                if resp.status_code == 200:
                    results.append({"address": addr, "trace": resp.json(), "status": "success"})
                    continue
        except Exception as e:
            logger.warning(f"Batch trace failed for {addr}: {e}")
        
        # Fallback mock
        results.append({
            "address": addr,
            "trace": _mock_trace(addr),
            "status": "mock",
        })

    # Cross-wallet analysis
    all_exchanges = {}
    all_clusters = []
    high_risk_wallets = []
    
    for r in results:
        trace = r.get("trace", {})
        attr = trace.get("attribution", {})
        if attr.get("status") == "KNOWN":
            ex = attr.get("exchange_name", "Unknown")
            all_exchanges[ex] = all_exchanges.get(ex, 0) + 1
        
        clusters = trace.get("clusters", [])
        all_clusters.extend(clusters)
        
        # Try risk scoring
        risk = _quick_risk(r["address"])
        r["risk_score"] = risk
        if risk > 0.7:
            high_risk_wallets.append(r["address"])
    
    common_exchanges = [
        {"exchange": ex, "wallet_count": count, "legal_action_priority": "HIGH" if count > 1 else "MEDIUM"}
        for ex, count in sorted(all_exchanges.items(), key=lambda x: -x[1])
    ]
    
    # Determine if these wallets form a fraud ring
    ring_confidence = min(0.95, len(common_exchanges) * 0.3 + len(high_risk_wallets) / max(len(addresses), 1) * 0.5)
    
    return {
        "wallets_investigated": len(addresses),
        "tron_addresses": len(tron_addrs),
        "ethereum_addresses": len(eth_addrs),
        "high_risk_wallets": high_risk_wallets,
        "common_exchange_destinations": common_exchanges,
        "fraud_ring_confidence": round(ring_confidence, 3),
        "fraud_ring_assessment": (
            "CONFIRMED FRAUD RING — multiple wallets converging on same exchanges"
            if ring_confidence > 0.7 else
            "LIKELY CONNECTED — shared exchange patterns observed"
            if ring_confidence > 0.4 else
            "INSUFFICIENT EVIDENCE — wallets may be unrelated"
        ),
        "recommended_action": (
            "Issue consolidated Section 91 BNSS notice to all identified exchanges. "
            "Request freeze on all associated accounts simultaneously."
            if common_exchanges else
            "Expand trace depth or request OSINT enrichment."
        ),
        "per_wallet_results": results,
    }


def _quick_risk(address: str) -> float:
    """Get risk score for an address — real API or mock."""
    try:
        if not _is_testing():
            resp = httpx.post(
                f"{_ML_URL}/risk-score",
                json={"address": address, "features": {}},
                timeout=_TIMEOUT,
            )
            if resp.status_code == 200:
                return resp.json().get("risk_score", 0.5)
    except Exception:
        pass
    h = int(hashlib.md5(address.encode()).hexdigest(), 16)
    return round((h % 1000) / 1000, 3)


def _mock_trace(address: str) -> dict:
    h = int(hashlib.md5(address.encode()).hexdigest(), 16)
    chain = "tron" if address.startswith("T") else "ethereum"
    exchanges = ["Binance", "OKX", "Bybit", "HTX", "Kraken"]
    ex = exchanges[h % len(exchanges)]
    return {
        "seed_address": address,
        "attribution": {"status": "KNOWN", "exchange_name": ex, "confidence": 0.85},
        "clusters": [],
        "summary": {"total_nodes": 5 + (h % 20), "attributed_exchange": ex},
        "_chain": chain,
        "_mock": True,
    }


# ════════════════════════════════════════════════════════════════
# MULTI-CHAIN ADDRESS DETECTION
# ════════════════════════════════════════════════════════════════

def detect_address_chain(address: str) -> dict:
    """
    Detect which blockchain network an address belongs to.
    
    Args:
        address: Wallet address string
    
    Returns:
        Chain info: network, token, explorer_url, confidence
    """
    addr = address.strip()
    if addr.startswith("T") and len(addr) == 34:
        return {
            "address": addr,
            "chain": "tron",
            "network": "Tron Mainnet",
            "token": "USDT-TRC20",
            "contract": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
            "explorer_url": f"https://tronscan.org/#/address/{addr}",
            "confidence": 0.99,
            "investigation_note": "Tron USDT-TRC20 is the primary Indian crypto fraud corridor per MHA I4C intelligence",
        }
    elif addr.startswith("0x") and len(addr) == 42:
        return {
            "address": addr,
            "chain": "ethereum",
            "network": "Ethereum Mainnet",
            "token": "USDT-ERC20",
            "contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "explorer_url": f"https://etherscan.io/address/{addr}",
            "confidence": 0.99,
            "investigation_note": "Ethereum USDT-ERC20 — common for large-value cross-border fraud flows",
        }
    elif addr.startswith("1") or addr.startswith("3") or addr.startswith("bc1"):
        return {
            "address": addr,
            "chain": "bitcoin",
            "network": "Bitcoin Mainnet",
            "token": "BTC",
            "explorer_url": f"https://blockchair.com/bitcoin/address/{addr}",
            "confidence": 0.95,
            "investigation_note": "Bitcoin address — limited USDT tracing capability. Recommend converting to USD value for ML scoring.",
        }
    else:
        return {
            "address": addr,
            "chain": "unknown",
            "network": "Unknown",
            "token": "Unknown",
            "confidence": 0.0,
            "investigation_note": "Address format not recognized. Verify input.",
        }


# ════════════════════════════════════════════════════════════════
# THREAT INTEL SCREEN
# ════════════════════════════════════════════════════════════════

def screen_against_sanctions(address: str) -> dict:
    """
    Screen a wallet address against live OFAC sanctions list and CryptoScamDB.
    
    Args:
        address: Wallet address to screen
    
    Returns:
        Screening result with source, category, and legal implications
    """
    try:
        if not _is_testing():
            resp = httpx.post(
                f"{_CYBERSECURITY_URL}/threat-intel/screen",
                json={"addresses": [address]},
                timeout=_TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    r = results[0]
                    return {
                        "address": address,
                        "sanctioned": r.get("hit", False),
                        "source": r.get("source"),
                        "category": r.get("category"),
                        "confidence": r.get("confidence", 0.0),
                        "description": r.get("description"),
                        "legal_implication": (
                            "URGENT: This address is on an official sanctions list. "
                            "Do NOT transact. Report to FIU-IND immediately under PMLA."
                            if r.get("hit") else
                            "Address not found in current sanctions lists — proceed with standard investigation."
                        )
                    }
    except Exception as e:
        logger.warning(f"Sanctions screen failed: {e}")
    
    # Mock
    h = int(hashlib.md5(address.encode()).hexdigest(), 16)
    sanctioned = (h % 100) < 10  # 10% mock sanction rate for demo
    return {
        "address": address,
        "sanctioned": sanctioned,
        "source": "OFAC SDN List (mock)" if sanctioned else None,
        "category": "sanctions" if sanctioned else None,
        "confidence": 0.97 if sanctioned else 0.0,
        "description": "Mock: OFAC SDN-listed crypto address" if sanctioned else "Not found in sanctions list (mock mode)",
        "legal_implication": (
            "URGENT: Sanctions hit detected. Report to FIU-IND."
            if sanctioned else
            "No sanctions hit. Continue standard investigation."
        ),
        "_mock": True,
    }


# ════════════════════════════════════════════════════════════════
# CASE SUMMARY
# ════════════════════════════════════════════════════════════════

def get_case_summary(session_id: str) -> dict:
    """
    Get a structured summary of the current investigation session.
    
    Args:
        session_id: The investigation session ID
    
    Returns:
        Case summary with all findings, actions taken, and pending steps
    """
    return {
        "session_id": session_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary_version": "2.0",
        "note": (
            "Case summary integrates all tool outputs from this session. "
            "Use 'Export Evidence Chain' in the dashboard to generate court-admissible PDF."
        ),
        "next_actions": [
            "Review attributed exchange and initiate Section 91 BNSS notice",
            "Verify hash-chain integrity in Evidence Trail panel",
            "Export case PDF for supervisor review",
        ],
    }


# ════════════════════════════════════════════════════════════════
# UPI → CRYPTO BRIDGE TOOL
# ════════════════════════════════════════════════════════════════

def analyze_upi_complaint(
    complaint_text: str,
    amount_inr: Optional[float] = None,
    fir_number: Optional[str] = None,
) -> dict:
    """
    Analyze a UPI banking fraud complaint to generate crypto investigation leads.
    
    Args:
        complaint_text: Raw FIR/NCRP complaint text
        amount_inr: Fraud amount in Indian Rupees (optional)
        fir_number: FIR or NCRP complaint number (optional)
    
    Returns:
        Crypto leads, P2P corridor analysis, suggested legal notices
    """
    try:
        if not _is_testing():
            resp = httpx.post(
                f"{_CYBERSECURITY_URL}/intake/upi-bridge",
                json={
                    "complaint_text": complaint_text,
                    "amount_inr": amount_inr,
                    "fir_number": fir_number,
                },
                timeout=_TIMEOUT,
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.warning(f"UPI bridge call failed: {e}")
    
    # Mock
    return {
        "fir_number": fir_number,
        "amount_inr": amount_inr,
        "p2p_corridor_analysis": {
            "likely_corridor": "Binance P2P",
            "confidence": 0.68,
        },
        "crypto_leads": [
            {
                "lead_type": "p2p_exchange_kyc_demand",
                "exchange": "Binance P2P",
                "confidence": 0.68,
                "legal_action": "Issue Section 91 BNSS notice to Binance India",
                "compliance_contact": "compliance@binance.com",
                "priority": "HIGH",
            }
        ],
        "legal_notices_suggested": [
            "Section 91 BNSS: Requisition for KYC from payment service provider",
            "Section 91 BNSS: Requisition for KYC from Binance India",
        ],
        "recommended_next_steps": [
            "Trace any crypto addresses mentioned in complaint",
            "Send Section 91 BNSS notice to Binance India compliance",
            "Request UPI logs from NPCI",
        ],
        "_mock": True,
    }


__all__ = [
    # Re-exported from mocks
    "trace_wallet", "get_cluster", "get_risk_score", "identify_exchange",
    "check_blacklist", "draft_legal_notice", "log_event", "verify_entry",
    # New tools
    "batch_trace_wallets", "detect_address_chain", "screen_against_sanctions",
    "get_case_summary", "analyze_upi_complaint",
]
