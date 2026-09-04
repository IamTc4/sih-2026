"""
walletrace/graph.py
────────────────────
LangGraph state-machine definition for the WalletTrace orchestration pipeline.

Pipeline shape:
  Intake → Trace → Cluster → RiskScore → Attribute
    → [conditional]
        ≥ CONFIDENCE_THRESHOLD → DraftNotice → Log → Respond
        < CONFIDENCE_THRESHOLD → RecommendManualReview → Log → Respond

State persistence:
  Uses LangGraph's MemorySaver (in-memory) so follow-up questions in the same
  session_id resume from the last checkpoint without re-running the full graph.
  To switch to a persistent DB, replace MemorySaver with SqliteSaver or
  PostgresSaver — only the saver import line changes.
"""

from __future__ import annotations

import re
import os
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from walletrace.config import CONFIDENCE_THRESHOLD, GOOGLE_API_KEY, OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from walletrace.state import WalletTraceState
from walletrace.security import SYSTEM_BOUNDARY, sanitize_tool_output, build_grounded_prompt
from walletrace.tools.mocks import (
    trace_wallet,
    get_cluster,
    get_risk_score,
    identify_exchange,
    check_blacklist,
    draft_legal_notice,
    log_event,
)

logger = logging.getLogger(__name__)

# ── LLM initialisation ───────────────────────────────────────────────────────
def _build_llm():
    """Return a LangChain chat model based on available API keys."""
    if GOOGLE_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            google_api_key=GOOGLE_API_KEY,
        )
    elif OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            openai_api_key=OPENAI_API_KEY,
        )
    else:
        raise EnvironmentError(
            "No LLM API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY in .env"
        )


# ── Scope-guard: detect off-topic questions ──────────────────────────────────
_SCOPE_KEYWORDS = [
    "wallet", "address", "crypto", "bitcoin", "ethereum", "transaction",
    "trace", "fraud", "exchange", "investigate", "cluster", "risk",
    "blacklist", "notice", "case", "report", "0x", "btc", "eth", "usdt",
    "blockchain", "token", "chain", "defi", "scam", "phishing", "ponzi",
]

def _is_in_scope(message: str) -> bool:
    lower = message.lower()
    return any(kw in lower for kw in _SCOPE_KEYWORDS)


# ── Helper: extract wallet address from message ───────────────────────────────
def _extract_address(message: str) -> str | None:
    """
    Try to extract a wallet address from the investigator's message.
    Supports Ethereum (0x…) and a generic 25-62 char alphanumeric fallback.
    """
    eth_pattern = r"\b0x[0-9a-fA-F]{40}\b"
    match = re.search(eth_pattern, message)
    if match:
        return match.group(0)

    # Generic fallback: long alphanumeric tokens that look like crypto addresses
    generic_pattern = r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"  # Bitcoin-ish
    match = re.search(generic_pattern, message)
    if match:
        return match.group(0)

    # If message itself looks like a raw address (no spaces, right length)
    stripped = message.strip()
    if re.match(r"^[0-9a-fA-Z_x]{25,130}$", stripped):
        return stripped

    return None


# ─────────────────────────────────────────────────────────────────────────────
# NODE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

def node_intake(state: WalletTraceState) -> WalletTraceState:
    """
    Intake node.
    Validates the incoming message, checks scope, and extracts the seed address.
    """
    message = state.get("original_message", "")

    if not _is_in_scope(message):
        return {
            **state,
            "error": "OUT_OF_SCOPE",
            "response_text": (
                "I'm WalletTrace, specialised for cryptocurrency fraud investigation "
                "for Indian law enforcement. I can help you trace wallet addresses, "
                "assess risk, identify exchanges, and draft investigation notices.\n\n"
                "Please provide a cryptocurrency wallet address or describe your "
                "investigation query."
            ),
            "citations": [],
        }

    address = _extract_address(message)
    if not address:
        return {
            **state,
            "error": "NO_ADDRESS",
            "response_text": (
                "No wallet address detected in your message. "
                "Please provide the victim-reported wallet address to begin tracing. "
                "Example: 0x1234...abcd or a Bitcoin address starting with 1 or 3."
            ),
            "citations": [],
        }

    logger.info("[Intake] Session=%s Address=%s", state.get("session_id"), address)
    return {
        **state,
        "wallet_address": address,
        "tool_evidence": {},
        "error": None,
    }


def node_trace(state: WalletTraceState) -> WalletTraceState:
    """Trace node — calls trace_wallet() on the seed address."""
    address = state["wallet_address"]
    result = trace_wallet(address)
    sanitised = sanitize_tool_output("trace_wallet", result)
    logger.info("[Trace] %d edges found", len(result.get("graph_edges", [])))
    return {
        **state,
        "trace_result": result,
        "tool_evidence": {**state.get("tool_evidence", {}), "trace_wallet": sanitised},
    }


def node_cluster(state: WalletTraceState) -> WalletTraceState:
    """Cluster node — calls get_cluster() on the seed address."""
    address = state["wallet_address"]
    result = get_cluster(address)
    sanitised = sanitize_tool_output("get_cluster", result)
    logger.info("[Cluster] cluster_id=%s", result.get("cluster_id"))
    return {
        **state,
        "cluster_result": result,
        "tool_evidence": {**state.get("tool_evidence", {}), "get_cluster": sanitised},
    }


def node_risk_score(state: WalletTraceState) -> WalletTraceState:
    """RiskScore node — scores the cluster (preferred) or seed address."""
    cluster_id = state.get("cluster_result", {}).get("cluster_id")
    target = cluster_id if cluster_id else state["wallet_address"]
    result = get_risk_score(target)
    sanitised = sanitize_tool_output("get_risk_score", result)
    logger.info("[RiskScore] score=%.2f confidence=%s", result["risk_score"], result["confidence"])
    return {
        **state,
        "risk_result": result,
        "tool_evidence": {**state.get("tool_evidence", {}), "get_risk_score": sanitised},
    }


def node_attribute(state: WalletTraceState) -> WalletTraceState:
    """
    Attribute node — identifies exchange and checks blacklist for all
    addresses in the cluster (or seed if no cluster).
    """
    addresses = state.get("cluster_result", {}).get("addresses", [state["wallet_address"]])

    # Check exchange attribution for each address; take highest-confidence hit
    best_attribution = {"attributed": False, "confidence": 0.0, "exchange_name": None, "deposit_address": None}
    blacklist_hit = {"match": False, "source_case": None}
    all_sanitised = []

    for addr in addresses:
        attr = identify_exchange(addr)
        bl = check_blacklist(addr)

        all_sanitised.append(sanitize_tool_output(f"identify_exchange({addr[:12]}…)", attr))
        all_sanitised.append(sanitize_tool_output(f"check_blacklist({addr[:12]}…)", bl))

        if attr["confidence"] > best_attribution["confidence"]:
            best_attribution = attr
        if bl["match"]:
            blacklist_hit = bl

    combined_exchange_output = "\n".join(all_sanitised)
    evidence = state.get("tool_evidence", {})
    evidence["identify_exchange"] = combined_exchange_output
    evidence["check_blacklist"] = combined_exchange_output  # already included above

    logger.info(
        "[Attribute] attributed=%s confidence=%.2f blacklist_match=%s",
        best_attribution["attributed"],
        best_attribution["confidence"],
        blacklist_hit["match"],
    )

    return {
        **state,
        "attribution_result": best_attribution,
        "blacklist_result": blacklist_hit,
        "tool_evidence": evidence,
    }


def node_draft_notice(state: WalletTraceState) -> WalletTraceState:
    """
    DraftNotice node — compiles evidence and calls draft_legal_notice().
    Only reached when attribution confidence >= CONFIDENCE_THRESHOLD.

    IMPORTANT: This node only DRAFTS — it never claims to send or execute.
    """
    session_id = state.get("session_id", "UNKNOWN")
    attribution = state["attribution_result"]
    risk = state["risk_result"]
    blacklist = state["blacklist_result"]
    cluster = state.get("cluster_result", {})
    trace = state.get("trace_result", {})

    exchange_name = attribution.get("exchange_name", "Unknown Exchange")
    deposit_address = attribution.get("deposit_address", "N/A")

    evidence_summary = (
        f"Seed address  : {state['wallet_address']}\n"
        f"Cluster ID    : {cluster.get('cluster_id', 'N/A')}\n"
        f"Cluster size  : {len(cluster.get('addresses', []))} addresses\n"
        f"Tx edges traced: {len(trace.get('graph_edges', []))}\n"
        f"Risk score    : {risk['risk_score']:.2f} (confidence: {risk['confidence']})\n"
        f"Exchange      : {exchange_name} [identified via identify_exchange, confidence {attribution['confidence']*100:.0f}%]\n"
        f"Deposit addr  : {deposit_address}\n"
        f"Blacklist hit : {blacklist['match']} "
        f"(case: {blacklist.get('source_case', 'N/A')})\n"
        f"Top risk factors: "
        + ", ".join(f["feature"] for f in risk.get("top_factors", []))
    )

    result = draft_legal_notice(
        case_id=f"WT-{session_id[:8].upper()}",
        exchange=exchange_name,
        evidence_summary=evidence_summary,
    )
    sanitised = sanitize_tool_output("draft_legal_notice", result)
    evidence = {**state.get("tool_evidence", {}), "draft_legal_notice": sanitised}

    logger.info("[DraftNotice] Draft generated for exchange=%s", exchange_name)

    return {
        **state,
        "draft_result": result,
        "routing_decision": "draft_notice",
        "tool_evidence": evidence,
    }


def node_recommend_manual_review(state: WalletTraceState) -> WalletTraceState:
    """
    RecommendManualReview node — reached when attribution confidence is
    below CONFIDENCE_THRESHOLD.  Sets routing_decision but does NOT draft
    any notice.
    """
    attribution = state.get("attribution_result", {})
    logger.info(
        "[ManualReview] confidence=%.2f below threshold=%.2f",
        attribution.get("confidence", 0.0),
        CONFIDENCE_THRESHOLD,
    )
    return {
        **state,
        "draft_result": None,
        "routing_decision": "manual_review",
    }


def node_log(state: WalletTraceState) -> WalletTraceState:
    """Log node — creates an immutable audit log entry for this pipeline run."""
    payload = {
        "session_id": state.get("session_id"),
        "wallet_address": state.get("wallet_address"),
        "routing_decision": state.get("routing_decision"),
        "risk_score": state.get("risk_result", {}).get("risk_score"),
        "attributed": state.get("attribution_result", {}).get("attributed"),
        "blacklist_match": state.get("blacklist_result", {}).get("match"),
    }
    result = log_event("pipeline_complete", payload)
    logger.info("[Log] entry_hash=%s", result["entry_hash"])
    return {
        **state,
        "log_result": result,
    }


def node_respond(state: WalletTraceState) -> WalletTraceState:
    """
    Respond node — calls the LLM to generate a grounded natural-language
    response.  Uses build_grounded_prompt() to enforce citation of every fact.
    Enforces the system-prompt data/instruction boundary via SYSTEM_BOUNDARY.
    """
    llm = _build_llm()

    grounded_prompt = build_grounded_prompt(
        question=state.get("original_message", ""),
        tool_evidence=state.get("tool_evidence", {}),
        routing_decision=state.get("routing_decision", "manual_review"),
    )

    messages = [
        SystemMessage(content=SYSTEM_BOUNDARY),
        HumanMessage(content=grounded_prompt),
    ]

    response = llm.invoke(messages)
    response_text = response.content

    # Build structured citations from tool_evidence keys
    citations = [
        {"tool": tool_name, "summary": output[:200] + "…" if len(output) > 200 else output}
        for tool_name, output in state.get("tool_evidence", {}).items()
    ]

    logger.info("[Respond] response_length=%d", len(response_text))

    return {
        **state,
        "response_text": response_text,
        "citations": citations,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CONDITIONAL ROUTING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def route_after_attribute(state: WalletTraceState) -> Literal["DraftNotice", "RecommendManualReview"]:
    """
    Branch point after the Attribute node.
    Routes to DraftNotice if attribution confidence >= CONFIDENCE_THRESHOLD,
    otherwise routes to RecommendManualReview.

    The CONFIDENCE_THRESHOLD constant is defined in walletrace/config.py
    and is NOT hardcoded here.
    """
    attribution = state.get("attribution_result", {})
    confidence = attribution.get("confidence", 0.0)
    attributed = attribution.get("attributed", False)

    if attributed and confidence >= CONFIDENCE_THRESHOLD:
        logger.info(
            "[Router] confidence=%.2f >= threshold=%.2f → DraftNotice",
            confidence, CONFIDENCE_THRESHOLD,
        )
        return "DraftNotice"
    else:
        logger.info(
            "[Router] confidence=%.2f < threshold=%.2f → RecommendManualReview",
            confidence, CONFIDENCE_THRESHOLD,
        )
        return "RecommendManualReview"


def route_after_intake(state: WalletTraceState) -> Literal["Trace", "Respond"]:
    """Short-circuit to Respond immediately if Intake found an error."""
    if state.get("error"):
        return "Respond"
    return "Trace"


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Assembles and compiles the WalletTrace LangGraph state machine.

    Returns a compiled graph with MemorySaver checkpointing so that
    sessions can resume with follow-up questions without re-running
    the full pipeline.
    """
    builder = StateGraph(WalletTraceState)

    # ── Register nodes ───────────────────────────────────────────────────────
    builder.add_node("Intake", node_intake)
    builder.add_node("Trace", node_trace)
    builder.add_node("Cluster", node_cluster)
    builder.add_node("RiskScore", node_risk_score)
    builder.add_node("Attribute", node_attribute)
    builder.add_node("DraftNotice", node_draft_notice)
    builder.add_node("RecommendManualReview", node_recommend_manual_review)
    builder.add_node("Log", node_log)
    builder.add_node("Respond", node_respond)

    # ── Define edges ─────────────────────────────────────────────────────────
    builder.add_edge(START, "Intake")

    # After Intake: short-circuit to Respond on error, else continue
    builder.add_conditional_edges(
        "Intake",
        route_after_intake,
        {"Trace": "Trace", "Respond": "Respond"},
    )

    # Linear pipeline: Trace → Cluster → RiskScore → Attribute
    builder.add_edge("Trace", "Cluster")
    builder.add_edge("Cluster", "RiskScore")
    builder.add_edge("RiskScore", "Attribute")

    # Conditional branch after Attribute
    builder.add_conditional_edges(
        "Attribute",
        route_after_attribute,
        {
            "DraftNotice": "DraftNotice",
            "RecommendManualReview": "RecommendManualReview",
        },
    )

    # Both branches converge at Log → Respond → END
    builder.add_edge("DraftNotice", "Log")
    builder.add_edge("RecommendManualReview", "Log")
    builder.add_edge("Log", "Respond")
    builder.add_edge("Respond", END)

    # ── Compile with in-memory persistence ───────────────────────────────────
    # MemorySaver keeps checkpoints in RAM keyed by (thread_id = session_id).
    # Follow-up questions in the same session resume from the last saved state.
    # To switch to SQLite: from langgraph.checkpoint.sqlite import SqliteSaver
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# Module-level singleton (imported by api.py and tests)
GRAPH = build_graph()
