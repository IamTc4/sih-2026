"""
blockchain/config.py
─────────────────────
All tunable constants for the Blockchain Analytics module.
Change values here or via environment variables / .env file.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

# ── Tronscan API ──────────────────────────────────────────────────────────────
TRONSCAN_API_BASE: str = os.getenv(
    "TRONSCAN_API_BASE", "https://apilist.tronscanapi.com/api"
)
TRONSCAN_API_KEY: str = os.getenv("TRONSCAN_API_KEY", "")  # empty = unauthenticated

# ── Traversal limits ──────────────────────────────────────────────────────────
# NOTE: Production investigations should increase MAX_HOP_DEPTH to 10-15;
# 6 is chosen for live-demo speed (sub-second for most wallets at 50 tx/hop).
MAX_HOP_DEPTH: int = int(os.getenv("MAX_HOP_DEPTH", "6"))
MAX_TX_PER_ADDRESS: int = int(os.getenv("MAX_TX_PER_ADDRESS", "50"))

# ── Clustering parameters ────────────────────────────────────────────────────
# Deposit-reuse heuristic: two addresses that both forward to the same
# collector within this time window (seconds) are merged into one cluster.
CLUSTER_TIME_WINDOW_SEC: int = int(os.getenv("CLUSTER_TIME_WINDOW_SEC", "3600"))

# ── Peel-chain / majority-flow ────────────────────────────────────────────────
# An outgoing edge is considered the "bulk/majority" flow if it carries at
# least this fraction of the total outflow from a node.
MAJORITY_FLOW_THRESHOLD: float = float(os.getenv("MAJORITY_FLOW_THRESHOLD", "0.5"))

# ── Service port ─────────────────────────────────────────────────────────────
SERVICE_PORT: int = int(os.getenv("BLOCKCHAIN_PORT", "8001"))
