"""
walletrace/config.py
────────────────────
Centralised configuration.  All tunable constants live here so teammates
only need to change one file when adjusting thresholds or model choices.
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# ── Attribution confidence gate ────────────────────────────────────────────
# If identify_exchange() returns confidence >= CONFIDENCE_THRESHOLD the graph
# routes to DraftNotice; otherwise it routes to RecommendManualReview.
# Teammates: adjust this single constant after your joint calibration session.
CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))

# ── LLM provider / model ───────────────────────────────────────────────────
GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# ── Security ───────────────────────────────────────────────────────────────
# Phrases that, if found verbatim in any tool output, trigger sanitisation
# before the text reaches the LLM context.  Extend this list defensively.
INJECTION_PATTERNS: List[str] = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard previous",
    "forget previous instructions",
    "new instructions:",
    "system prompt:",
    "you are now",
    "act as",
    "pretend you are",
    "override your",
]
