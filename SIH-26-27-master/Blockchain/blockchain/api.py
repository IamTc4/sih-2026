"""
blockchain/api.py
──────────────────
FastAPI application for the WalletTrace Blockchain Analytics Module.

Endpoint:
  GET /trace/{address}
  Returns the full trace, cluster, and attribution result for a Tron address.

Integration with Agentic AI:
  The Agentic AI module's trace_wallet() stub calls this endpoint.
  See walletrace/tools/mocks.py in the Agentic_Ai folder — replace the mock
  body with: return httpx.get("http://localhost:8001/trace/{address}").json()

Service port: 8001 (Agentic AI runs on 8000)
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from blockchain.attribution import attribute_trace
from blockchain.audit import log_event
from blockchain.clustering import build_clusters
from blockchain.graph import TronGraph
from blockchain.ingestion import fetch_all_transactions, load_transactions_from_csv
from blockchain.models import TraceResponse
from blockchain.tracer import trace_fund_flow

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="WalletTrace — Blockchain Analytics API",
    description=(
        "SIH26183 | Tron/USDT-TRC20 on-chain tracing, clustering, and "
        "exchange attribution for Indian law enforcement. "
        "Primary chain: Tron. Data source: Tronscan public API."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Optional CSV mode (for offline demo) ─────────────────────────────────────
# Set env var CSV_MODE=1 and CSV_PATH=path/to/tron_transactions_raw.csv
# to run fully offline against the provided CSV instead of live Tronscan API.
_CSV_MODE: bool = os.getenv("CSV_MODE", "0") == "1"
_CSV_PATH: str  = os.getenv("CSV_PATH", "../tron_transactions_raw.csv")


def _get_fetch_fn(address: str):
    """Return the appropriate fetch function based on mode (live vs CSV)."""
    if _CSV_MODE:
        # Load from CSV; filter to only transactions involving this address
        all_csv_txs = load_transactions_from_csv(_CSV_PATH)
        relevant = [
            tx for tx in all_csv_txs
            if tx.from_addr == address or tx.to_addr == address
        ]
        # Return a function that returns the pre-loaded list
        return lambda addr: [tx for tx in all_csv_txs if tx.from_addr == addr or tx.to_addr == addr]
    return fetch_all_transactions


# ─────────────────────────────────────────────────────────────────────────────
# GET /trace/{address}  — Main endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/trace/{address}", response_model=TraceResponse)
async def trace_address(
    address: str,
    max_hops: Optional[int] = Query(None, description="Override MAX_HOP_DEPTH for this request"),
    csv_mode: Optional[bool] = Query(None, description="Force CSV offline mode for this request"),
) -> TraceResponse:
    """
    Full end-to-end blockchain analysis for a Tron wallet address.

    Steps performed:
      1. BFS graph expansion from `address` (Tronscan API or CSV)
      2. Deposit-reuse clustering
      3. Multi-hop majority-flow tracing
      4. Exchange attribution against labeled dataset

    Returns the exact schema required by the Agentic AI orchestration module.
    """
    logger.info("GET /trace/%s", address)

    if not address or len(address) < 10:
        raise HTTPException(status_code=422, detail="Invalid Tron address format.")

    # ── Step 1: Graph construction via BFS ────────────────────────────────────
    graph = TronGraph()

    force_csv = csv_mode if csv_mode is not None else _CSV_MODE
    if force_csv:
        all_txs = load_transactions_from_csv(_CSV_PATH)
        def csv_fetch(addr: str):
            return [tx for tx in all_txs if tx.from_addr == addr or tx.to_addr == addr]
        fetch_fn = csv_fetch
    else:
        fetch_fn = fetch_all_transactions

    from blockchain.config import MAX_HOP_DEPTH
    hops = max_hops if max_hops is not None else MAX_HOP_DEPTH

    try:
        graph.expand_bfs(address, fetch_fn=fetch_fn, max_hops=hops)
    except Exception as exc:
        logger.exception("BFS expansion failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Graph construction failed: {exc}")

    # Collect all transactions that were added to the graph
    all_edges = graph.get_all_edges()

    # Reconstruct NormalizedTx list from edge dicts (for clustering)
    from blockchain.models import NormalizedTx
    all_txs_for_clustering = [
        NormalizedTx(**{
            "from":      e["from"],
            "to":        e["to"],
            "amount":    e["amount"],
            "token":     e["token"],
            "timestamp": e["timestamp"],
            "tx_hash":   e["tx_hash"],
            "chain":     e["chain"],
        })
        for e in all_edges
    ]

    # ── Step 2: Clustering ─────────────────────────────────────────────────────
    clusters = build_clusters(graph, all_txs_for_clustering)

    # ── Step 3: Fund-flow tracing ─────────────────────────────────────────────
    flow_trace = trace_fund_flow(graph, address, max_hops=hops)

    # Collect all addresses in the terminal's cluster for attribution
    terminal_cluster_addrs: list[str] = []
    for cluster in clusters:
        if flow_trace.terminal in cluster.addresses:
            terminal_cluster_addrs = cluster.addresses
            break

    # ── Step 4: Attribution ────────────────────────────────────────────────────
    attribution = attribute_trace(
        trace_addresses=flow_trace.all_addresses,
        cluster_addresses=terminal_cluster_addrs,
    )

    # ── Audit log ──────────────────────────────────────────────────────────────
    log_event("trace_complete", {
        "seed":        address,
        "hops":        len(flow_trace.hops),
        "terminal":    flow_trace.terminal,
        "clusters":    len(clusters),
        "attributed":  attribution.attributed,
        "exchange":    attribution.exchange_name,
    })

    return TraceResponse(
        seed_address=address,
        graph_edges=all_edges,
        clusters=clusters,
        attribution=attribution,
    )


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health() -> dict:
    return {
        "status":    "ok",
        "service":   "walletrace-blockchain",
        "chain":     "tron",
        "csv_mode":  _CSV_MODE,
    }


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("blockchain.api:app", host="0.0.0.0", port=8001, reload=True)
