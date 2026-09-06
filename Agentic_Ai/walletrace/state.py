"""
walletrace/state.py
───────────────────
Typed state schema for the WalletTrace LangGraph state machine.

Every node reads from and writes to this TypedDict.
LangGraph uses it for both in-memory checkpointing and future DB persistence.

NOTE: All type annotations use typing.Optional / typing.Dict / typing.List
(not X | Y syntax) for Python 3.9 compatibility. LangGraph calls
get_type_hints() at runtime which does not respect __future__ annotations.
"""

from typing import Dict, List, Optional, TypedDict


class WalletTraceState(TypedDict, total=False):
    # ── Input ────────────────────────────────────────────────────────────────
    session_id: str          # Unique session identifier (from API caller)
    wallet_address: str      # Seed address submitted by the investigator
    original_message: str    # Raw investigator message (may include context)

    # ── Node outputs (populated as the graph progresses) ─────────────────────
    trace_result: dict       # Output of trace_wallet()
    cluster_result: dict     # Output of get_cluster()
    risk_result: dict        # Output of get_risk_score()
    attribution_result: dict # Output of identify_exchange()
    blacklist_result: dict   # Output of check_blacklist()
    draft_result: Optional[dict]     # Output of draft_legal_notice(), or None
    log_result: dict         # Output of log_event()

    # ── Routing ──────────────────────────────────────────────────────────────
    routing_decision: str    # "draft_notice" | "manual_review"

    # ── Grounding / citations ────────────────────────────────────────────────
    # Dict mapping tool_name -> sanitised tool output string.
    # Populated incrementally as each node runs.
    tool_evidence: Dict[str, str]

    # ── Final response ────────────────────────────────────────────────────────
    response_text: str            # LLM-generated, grounded natural-language response
    citations: List[dict]         # Structured citation objects for the API response
    error: Optional[str]          # Set by any node that encounters a fatal error
    
    related_cases: list[dict]  # populated by node_correlate
