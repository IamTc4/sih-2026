"""
walletrace/api.py
─────────────────
FastAPI application exposing the WalletTrace agent.

Single endpoint:
  POST /agent/query
  Body:  {"session_id": str, "message": str}
  Response: {"response_text": str, "citations": [...], "draft_document": str | null}

Session persistence:
  LangGraph's MemorySaver (configured in graph.py) stores graph state keyed
  by session_id.  Send the same session_id in follow-up requests to continue
  an investigation without re-running the full pipeline.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from walletrace.graph import GRAPH

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="WalletTrace – Agentic Orchestration API",
    description=(
        "SIH26183: Real-time identification of fraud-linked cryptocurrency exchanges "
        "from victim-reported wallet addresses, for Indian law enforcement. "
        "This API is the orchestration layer only. "
        "Blockchain tracing, clustering, and risk scoring are separate modules."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────
class QueryRequest(BaseModel):
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier. Reuse the same ID for follow-up questions.",
    )
    message: str = Field(
        ...,
        description="Investigator message — typically a wallet address or follow-up query.",
        min_length=1,
        max_length=2000,
    )


class CitationEntry(BaseModel):
    tool: str
    summary: str


class QueryResponse(BaseModel):
    session_id: str
    response_text: str
    citations: list[CitationEntry]
    draft_document: str | None = Field(
        None,
        description=(
            "Draft legal notice text. Always null unless attribution confidence "
            "meets the threshold AND the notice has been system-generated. "
            "Requires investigator review before submission."
        ),
    )
    related_cases: list[dict] = []

# ── Endpoint ──────────────────────────────────────────────────────────────────
@app.post("/agent/query", response_model=QueryResponse)
async def agent_query(request: QueryRequest) -> QueryResponse:
    """
    Run the WalletTrace investigation pipeline for the given wallet address
    or follow-up question.

    If `session_id` matches a previous session, the graph resumes from the
    last checkpoint and can answer follow-up questions without re-tracing.
    """
    logger.info("POST /agent/query session=%s msg_len=%d", request.session_id, len(request.message))

    initial_state: dict[str, Any] = {
        "session_id": request.session_id,
        "original_message": request.message,
        "tool_evidence": {},
    }

    config = {"configurable": {"thread_id": request.session_id}}

    try:
        final_state = await GRAPH.ainvoke(initial_state, config=config)
    except Exception as exc:
        logger.exception("Graph execution failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Agent execution error: {exc}")

    # Extract draft document if available
    draft_document: str | None = None
    draft_result = final_state.get("draft_result")
    if draft_result and isinstance(draft_result, dict):
        draft_text = draft_result.get("draft_text", "")
        watermark = draft_result.get("watermark", "DRAFT - REQUIRES INVESTIGATOR REVIEW")
        draft_document = f"[{watermark}]\n\n{draft_text}"

    citations = [
        CitationEntry(tool=c["tool"], summary=c["summary"])
        for c in final_state.get("citations", [])
    ]

    return QueryResponse(
        session_id=request.session_id,
        response_text=final_state.get("response_text", ""),
        citations=citations,
        draft_document=draft_document,
        related_cases=final_state.get("related_cases", [])
    )


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "walletrace-agent"}


# ── Entry point for `python -m walletrace.api` ────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("walletrace.api:app", host="0.0.0.0", port=8000, reload=True)
