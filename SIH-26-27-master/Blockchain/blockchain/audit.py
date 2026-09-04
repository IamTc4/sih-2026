"""
blockchain/audit.py
────────────────────
Audit log stub — will be wired to the Agentic AI's log_event endpoint.

SCOPE NOTE: The real tamper-evident audit log is owned by the Agentic AI
module (walletrace/tools/mocks.py::log_event). This stub accepts the same
call signature so this module's code compiles and runs without the Agentic
AI service being up. Wire AGENTIC_AI_URL in .env to activate real logging.
"""
from __future__ import annotations

import hashlib
import logging
import os
import time

logger = logging.getLogger(__name__)
AGENTIC_AI_URL = os.getenv("AGENTIC_AI_URL", "")


def log_event(event_type: str, payload: dict) -> dict:
    """
    Stub: log an audit event.

    If AGENTIC_AI_URL is configured, forwards to the Agentic AI log endpoint.
    Otherwise, computes a local SHA-256 entry hash and logs to Python logger.

    Returns {"entry_hash": str, "logged": bool} — same shape as the real tool.
    """
    raw = f"{event_type}{str(payload)}{time.time_ns()}"
    entry_hash = hashlib.sha256(raw.encode()).hexdigest()

    if AGENTIC_AI_URL:
        try:
            import httpx
            httpx.post(
                f"{AGENTIC_AI_URL}/internal/log",
                json={"event_type": event_type, "payload": payload},
                timeout=3.0,
            )
        except Exception as exc:
            logger.warning("[Audit] Could not reach Agentic AI log endpoint: %s", exc)

    logger.info("[Audit] %s | hash=%s | payload=%s", event_type, entry_hash[:16], payload)
    return {"entry_hash": entry_hash, "logged": True}
