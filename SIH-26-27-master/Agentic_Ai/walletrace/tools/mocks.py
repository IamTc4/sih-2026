"""
walletrace/tools/mocks.py
─────────────────────────
External tool wrappers for the WalletTrace agent.

Each function first attempts to call the real upstream service if its
environment variable URL is configured, then falls back to a deterministic
mock so the Agentic AI module works in complete isolation for testing.

Service URL env vars:
  BLOCKCHAIN_API_URL     → http://localhost:8000  (Blockchain module)
  ML_API_URL             → http://localhost:8002  (ML Risk Scoring module)
  CYBERSECURITY_API_URL  → http://localhost:8003  (Cybersecurity module)

Contract owner  │ Tool function           │ Replacing module
────────────────┼─────────────────────────┼──────────────────────────
Blockchain team │ trace_wallet            │ POST /trace  (port 8000)
Blockchain team │ get_cluster             │ GET  /cluster/{address}
Blockchain team │ identify_exchange       │ GET  /attribution/{address}
ML / Risk team  │ get_risk_score          │ POST /risk-score (port 8002) ✅ wired
Cyber team      │ check_blacklist         │ GET  /blacklist/{address} (port 8003)
Agent / Legal   │ draft_legal_notice      │ Template engine (this repo)
Agent / Logging │ log_event               │ POST /log-event (port 8003)
Agent / Logging │ verify_entry            │ GET  /verify/{id} (port 8003)

All mock fallbacks are deterministic for the same `address`.
"""

import hashlib
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

# ── Service URLs (set in .env to enable real integrations) ────────────────────
_BLOCKCHAIN_URL: Optional[str]    = os.getenv("BLOCKCHAIN_API_URL",    "").rstrip("/")
_ML_URL: Optional[str]            = os.getenv("ML_API_URL",            "").rstrip("/")
_CYBERSECURITY_URL: Optional[str] = os.getenv("CYBERSECURITY_API_URL", "").rstrip("/")


def _is_testing() -> bool:
    return "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ


def _call_blockchain(path: str, timeout: float = 5.0) -> Optional[dict]:
    """
    Call the Blockchain Analytics service (port 8000).
    Returns the JSON response dict, or None on any error (caller falls back to mock).
    """
    if _is_testing() or not _BLOCKCHAIN_URL:
        return None
    try:
        resp = httpx.get(f"{_BLOCKCHAIN_URL}{path}", timeout=httpx.Timeout(timeout, connect=2.0))
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.warning("[Tools] Blockchain API call failed (%s): %s", path, exc)
        return None


def _call_ml(payload: dict, timeout: float = 5.0) -> Optional[dict]:
    """
    Call the ML Risk Scoring service (port 8002) POST /risk-score.
    Returns the JSON response dict, or None on any error (caller falls back to mock).
    """
    if _is_testing() or not _ML_URL:
        return None
    try:
        resp = httpx.post(f"{_ML_URL}/risk-score", json=payload, timeout=httpx.Timeout(timeout, connect=2.0))
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.warning("[Tools] ML API call failed: %s", exc)
        return None


def _call_cybersecurity(method: str, path: str,
                        payload: Optional[dict] = None,
                        timeout: float = 5.0) -> Optional[dict]:
    """
    Call the Cybersecurity service (port 8003).
    method: 'GET' or 'POST'. Returns JSON or None.
    """
    if _is_testing() or not _CYBERSECURITY_URL:
        return None
    try:
        url = f"{_CYBERSECURITY_URL}{path}"
        timeout_cfg = httpx.Timeout(timeout, connect=2.0)
        if method == "POST":
            resp = httpx.post(url, json=payload or {}, timeout=timeout_cfg)
        else:
            resp = httpx.get(url, timeout=timeout_cfg)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.warning("[Tools] Cybersecurity API call failed (%s): %s", path, exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 1. trace_wallet
# ─────────────────────────────────────────────────────────────────────────────
def trace_wallet(address: str) -> dict:
    """
    Calls the Blockchain Analytics module's GET /trace/{address} endpoint
    when BLOCKCHAIN_API_URL is configured. Falls back to deterministic mock.

    Returns
    -------
    {
        "graph_edges": [{"from", "to", "amount", "token", "timestamp", "tx_hash", "chain"}],
        "seed_address": str
    }
    """
    # ── Try real Blockchain Analytics service first ──────────────────────────
    real = _call_blockchain(f"/trace/{address}")
    if real is not None:
        logger.info("[Tools] trace_wallet: using REAL blockchain service for %s", address[:12])
        return {
            "graph_edges": real.get("graph_edges", []),
            "seed_address": real.get("seed_address", address),
        }

    # ── Deterministic mock fallback ──────────────────────────────────────────
    logger.debug("[Tools] trace_wallet: using MOCK for %s", address[:12])
    seed_short = address[-6:] if len(address) >= 6 else address
    neighbor_1 = f"TMOCK_{seed_short}_HOP1"
    neighbor_2 = f"TMOCK_{seed_short}_HOP2"
    exchange_deposit = f"TEXCHANGE_DEPOSIT_{seed_short}"

    return {
        "graph_edges": [
            {
                "from": address,     "to": neighbor_1,
                "amount": 1000.0,   "token": "USDT",
                "timestamp": "2024-10-15T08:23:11Z",
                "tx_hash": f"TXTX_A_{seed_short}", "chain": "tron",
            },
            {
                "from": neighbor_1,  "to": neighbor_2,
                "amount": 995.0,    "token": "USDT",
                "timestamp": "2024-10-15T09:01:44Z",
                "tx_hash": f"TXTX_B_{seed_short}", "chain": "tron",
            },
            {
                "from": neighbor_2,  "to": exchange_deposit,
                "amount": 990.0,    "token": "USDT",
                "timestamp": "2024-10-15T09:47:22Z",
                "tx_hash": f"TXTX_C_{seed_short}", "chain": "tron",
            },
        ],
        "seed_address": address,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. get_cluster
# ─────────────────────────────────────────────────────────────────────────────
def get_cluster(address: str) -> dict:
    """
    Calls the Blockchain Analytics module and returns the first cluster
    containing `address`. Falls back to deterministic mock.

    Returns
    -------
    {"cluster_id": str, "addresses": [str], "heuristic_evidence": [...]}
    """
    # ── Try real Blockchain Analytics service ─────────────────────────────────
    real = _call_blockchain(f"/trace/{address}")
    if real is not None:
        clusters = real.get("clusters", [])
        # Return the cluster that contains this address
        for c in clusters:
            if address in c.get("addresses", []):
                logger.info("[Tools] get_cluster: REAL result cluster_id=%s", c.get("cluster_id"))
                return {
                    "cluster_id":         c["cluster_id"],
                    "addresses":          c["addresses"],
                    "heuristic_evidence": c.get("heuristic_evidence", []),
                }
        # Address not in any cluster — return singleton
        if clusters:
            c = clusters[0]
            return {"cluster_id": c["cluster_id"], "addresses": c["addresses"],
                    "heuristic_evidence": c.get("heuristic_evidence", [])}

    # ── Deterministic mock fallback ───────────────────────────────────────────
    logger.debug("[Tools] get_cluster: using MOCK for %s", address[:12])
    seed_short = address[-6:] if len(address) >= 6 else address
    cluster_id = f"CLU_{seed_short.upper()}"
    addr_b = f"TMOCK_{seed_short}_COSP1"
    addr_c = f"TMOCK_{seed_short}_COSP2"

    return {
        "cluster_id": cluster_id,
        "addresses": [address, addr_b, addr_c],
        "heuristic_evidence": [
            {
                "addr_a": address, "addr_b": addr_b,
                "heuristic_name": "deposit_reuse",
                "evidence_tx": f"TXTX_EVIDENCE_{seed_short}_1",
            },
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. get_risk_score
# ─────────────────────────────────────────────────────────────────────────────
def get_risk_score(address_or_cluster_id: str) -> dict:
    """
    Calls the ML Risk Scoring service (port 8002) POST /risk-score.
    Falls back to a deterministic mock when ML_API_URL is not configured.

    The trace_wallet / get_cluster results are passed as blockchain_output
    so the ML model uses real graph features rather than defaults.

    Returns
    -------
    {
        "risk_score": float,   # 0.0 (clean) – 1.0 (high risk)
        "top_factors": [
            {"feature": str, "contribution": float, "plain_text": str}
        ],
        "confidence": str      # "high" | "medium" | "low"
    }
    """
    # ── Try real ML service first ──────────────────────────────────────────
    # Use a minimal feature payload — the caller (graph.py) can enrich this
    # by passing real blockchain_output if needed. For now we call with the
    # address only; the ML service defaults all missing features to 0.
    real = _call_ml({"address": address_or_cluster_id})
    if real is not None:
        logger.info("[Tools] get_risk_score: using REAL ML service for %s",
                    address_or_cluster_id[:16])
        # Normalise to the shape the graph.py nodes expect
        top_factors = [
            {
                "feature":      f.get("feature", ""),
                "contribution": f.get("contribution", 0.0),
                "plain_text":   f.get("plain_text", ""),
            }
            for f in real.get("top_factors", [])
        ]
        return {
            "risk_score":  float(real.get("risk_score", 0.5)),
            "top_factors": top_factors,
            "confidence":  real.get("confidence", "medium"),
        }

    # ── Deterministic mock fallback ────────────────────────────────────────
    logger.debug("[Tools] get_risk_score: using MOCK for %s", address_or_cluster_id[:16])
    is_cluster = address_or_cluster_id.startswith("CLU_")
    score = 0.87 if is_cluster else 0.72

    return {
        "risk_score": score,
        "top_factors": [
            {"feature": "rapid_fund_movement",      "contribution": 0.29,
             "plain_text": "Rapid fund movement (high velocity)"},
            {"feature": "has_deposit_reuse",        "contribution": 0.25,
             "plain_text": "Deposit address reuse pattern detected"},
            {"feature": "blacklist_reachable",      "contribution": 0.20,
             "plain_text": "Address reachable from a known blacklisted wallet"},
        ],
        "confidence": "high" if is_cluster else "medium",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. identify_exchange
# ─────────────────────────────────────────────────────────────────────────────
def identify_exchange(address: str) -> dict:
    """
    Calls the Blockchain Analytics module's attribution result.
    Falls back to deterministic mock.

    CONTRACT: If attributed=False, exchange_name and deposit_address MUST be None.

    Returns
    -------
    {"exchange_name": str|None, "deposit_address": str|None,
     "confidence": float, "attributed": bool}
    """
    # ── Try real Blockchain Analytics service ─────────────────────────────────
    real = _call_blockchain(f"/trace/{address}")
    if real is not None:
        attr = real.get("attribution", {})
        attributed = attr.get("attributed", False)
        logger.info(
            "[Tools] identify_exchange: REAL result attributed=%s exchange=%s",
            attributed, attr.get("exchange_name")
        )
        # Enforce contract: nulls when not attributed
        return {
            "exchange_name":   attr.get("exchange_name")   if attributed else None,
            "deposit_address": attr.get("deposit_address") if attributed else None,
            "confidence":      float(attr.get("confidence", 0.0)),
            "attributed":      attributed,
        }

    # ── Deterministic mock fallback ───────────────────────────────────────────
    logger.debug("[Tools] identify_exchange: using MOCK for %s", address[:12])
    last_char = address[-1] if address else "0"
    attributed = last_char.isdigit() and int(last_char) >= 5
    seed_short = address[-6:] if len(address) >= 6 else address

    if attributed:
        return {
            "exchange_name":   "MockEx India",
            "deposit_address": f"TEXCHANGE_DEPOSIT_{seed_short}",
            "confidence":      0.91,
            "attributed":      True,
        }
    # Enforce contract: nulls when not attributed — never guess.
    return {
        "exchange_name":   None,
        "deposit_address": None,
        "confidence":      0.42,
        "attributed":      False,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. check_blacklist
# ─────────────────────────────────────────────────────────────────────────────
def check_blacklist(address: str) -> dict:
    """
    MOCK – Blacklist / VASP watchlist lookup.

    Returns
    -------
    {
        "match": bool,
        "source_case": str | None   # CBI / ED case reference when matched
    }
    """
    # Mock: addresses containing "EXCHANGE_DEPOSIT" are blacklisted.
    matched = "EXCHANGE_DEPOSIT" in address or "BLACKLIST" in address.upper()

    return {
        "match": matched,
        "source_case": "CBI-2024-CRYPTO-0047" if matched else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. draft_legal_notice
# ─────────────────────────────────────────────────────────────────────────────
def draft_legal_notice(case_id: str, exchange: str, evidence_summary: str) -> dict:
    """
    MOCK / REAL (this repo) – Legal notice template engine.

    Fills a standard template using ONLY the arguments supplied.
    No facts are invented; `evidence_summary` must be built from prior
    tool outputs before calling this function.

    Returns
    -------
    {
        "draft_text": str,
        "watermark": "DRAFT - REQUIRES INVESTIGATOR REVIEW"
    }
    """
    draft_text = (
        f"NOTICE TO VIRTUAL ASSET SERVICE PROVIDER\n"
        f"{'=' * 60}\n"
        f"Case Reference : {case_id}\n"
        f"Date           : {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"Issued by      : WalletTrace Automated Analysis System\n\n"
        f"To              : Compliance Officer, {exchange}\n\n"
        f"Subject         : Request for User Account Information and\n"
        f"                  Transaction Records — Suspected Crypto Fraud\n\n"
        f"Pursuant to Section 66B of the Information Technology Act, 2000,\n"
        f"and the Prevention of Money Laundering Act, 2002, you are hereby\n"
        f"requested to provide account and KYC details for the wallet\n"
        f"address(es) identified in the attached evidence summary.\n\n"
        f"EVIDENCE SUMMARY\n"
        f"{'─' * 60}\n"
        f"{evidence_summary}\n"
        f"{'─' * 60}\n\n"
        f"This notice was system-generated.  All facts above are drawn\n"
        f"exclusively from the automated analysis session referenced above.\n"
        f"An authorised investigator MUST review and countersign before\n"
        f"submission to the exchange.\n\n"
        f"[SIGNATURE BLOCK — TO BE COMPLETED BY INVESTIGATOR]\n"
    )

    return {
        "draft_text": draft_text,
        "watermark": "DRAFT - REQUIRES INVESTIGATOR REVIEW",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. log_event
# ─────────────────────────────────────────────────────────────────────────────
def log_event(event_type: str, payload: dict) -> dict:
    """
    MOCK / REAL (this repo) – Append-only audit log.

    Returns
    -------
    {
        "entry_hash": str,   # SHA-256 of (event_type + payload + timestamp)
        "logged": bool
    }
    """
    ts = str(time.time_ns())
    raw = f"{event_type}{str(payload)}{ts}"
    entry_hash = hashlib.sha256(raw.encode()).hexdigest()

    # In a real implementation this would persist to a tamper-evident store.
    return {
        "entry_hash": entry_hash,
        "logged": True,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 8. verify_entry
# ─────────────────────────────────────────────────────────────────────────────
def verify_entry(entry_id: str) -> dict:
    """
    MOCK / REAL (this repo) – Verify integrity of a previously logged entry.

    Returns
    -------
    {
        "valid": bool,
        "chain_intact": bool
    }
    """
    # Mock: any non-empty entry_id is considered valid.
    valid = bool(entry_id and len(entry_id) > 0)
    return {
        "valid": valid,
        "chain_intact": valid,
    }
