"""
blockchain/tracer.py
─────────────────────
Multi-hop fund-flow tracer with peel-chain awareness.

Starting from a seed address, this module follows the MAJORITY (bulk) fund
flow forward hop-by-hop, distinguishing:
  - Majority path: the single outgoing edge that carries >= MAJORITY_FLOW_THRESHOLD
    of total outflow from a node. This is the real money trail.
  - Peeled amounts: smaller outgoing edges to other addresses — change outputs,
    fee payments, diversion to secondary wallets (peel-chain pattern).

The tracer produces an ordered hop list: seed → hop1 → hop2 → ... → terminal.
The terminal address is the final destination (exchange deposit, cold wallet,
or unknown). This terminal address is what the attribution layer checks.

Configurable MAX_HOP_DEPTH caps traversal for demo speed. In production,
investigators would typically trace 10-15+ hops.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Set

from blockchain.config import MAX_HOP_DEPTH, MAJORITY_FLOW_THRESHOLD
from blockchain.graph import TronGraph
from blockchain.models import NormalizedTx

logger = logging.getLogger(__name__)


class HopResult:
    """One step in the traced fund-flow path."""
    __slots__ = ("address", "hop_index", "amount", "token", "tx_hash",
                 "is_majority_flow", "timestamp")

    def __init__(
        self,
        address: str,
        hop_index: int,
        amount: float,
        token: str,
        tx_hash: str,
        is_majority_flow: bool,
        timestamp: str,
    ) -> None:
        self.address         = address
        self.hop_index       = hop_index
        self.amount          = amount
        self.token           = token
        self.tx_hash         = tx_hash
        self.is_majority_flow = is_majority_flow
        self.timestamp       = timestamp

    def to_dict(self) -> dict:
        return {
            "address":          self.address,
            "hop_index":        self.hop_index,
            "amount":           self.amount,
            "token":            self.token,
            "tx_hash":          self.tx_hash,
            "is_majority_flow": self.is_majority_flow,
            "timestamp":        self.timestamp,
        }


class FundFlowTrace:
    """Result of a multi-hop trace."""

    def __init__(self, seed: str, hops: List[HopResult]) -> None:
        self.seed     = seed
        self.hops     = hops
        self.terminal = hops[-1].address if hops else seed

    @property
    def all_addresses(self) -> List[str]:
        return [self.seed] + [h.address for h in self.hops]

    def to_dict(self) -> dict:
        return {
            "seed":     self.seed,
            "terminal": self.terminal,
            "hops":     [h.to_dict() for h in self.hops],
            "depth":    len(self.hops),
        }


# ─────────────────────────────────────────────────────────────────────────────
def trace_fund_flow(
    graph: TronGraph,
    seed_address: str,
    max_hops: int = MAX_HOP_DEPTH,
) -> FundFlowTrace:
    """
    Follow the majority fund flow from `seed_address` forward through the graph.

    Algorithm:
      At each address, call graph.get_majority_out_edge() to find the outgoing
      edge that carries >= MAJORITY_FLOW_THRESHOLD of total outflow.
      If found, move forward to that edge's destination. Otherwise, stop
      (we have reached a terminal: exchange deposit, cold wallet, or dead end).

    Cycle protection: if we revisit an address, stop to avoid infinite loops.

    Returns
    -------
    FundFlowTrace
        Ordered list of HopResult objects. The last hop's address is the
        terminal address for the attribution layer.
    """
    hops: List[HopResult] = []
    visited: Set[str]     = {seed_address}
    current               = seed_address

    logger.info("[Tracer] Starting fund-flow trace from %s (max_hops=%d)", seed_address, max_hops)

    for hop_idx in range(max_hops):
        majority_edge = graph.get_majority_out_edge(current)

        if majority_edge is None:
            logger.info(
                "[Tracer] Terminal at hop %d: %s (no majority out-edge)", hop_idx, current
            )
            break

        _, next_addr, edge_data = majority_edge

        if next_addr in visited:
            logger.info(
                "[Tracer] Cycle detected at hop %d: %s → %s (already visited)",
                hop_idx, current, next_addr,
            )
            break

        amount   = edge_data.get("amount", 0.0)
        token    = edge_data.get("token", "TRX")
        tx_hash  = edge_data.get("tx_hash", "")
        ts       = edge_data.get("timestamp", "")

        hop = HopResult(
            address=next_addr,
            hop_index=hop_idx + 1,
            amount=amount,
            token=token,
            tx_hash=tx_hash,
            is_majority_flow=True,
            timestamp=ts,
        )
        hops.append(hop)
        visited.add(next_addr)
        current = next_addr

        logger.info(
            "[Tracer] Hop %d: %s → %s | %.4f %s | tx=%s",
            hop_idx + 1, _short(current), _short(next_addr), amount, token, tx_hash[:12],
        )

    result = FundFlowTrace(seed=seed_address, hops=hops)
    logger.info(
        "[Tracer] Trace complete: %d hops, terminal=%s",
        len(hops), result.terminal,
    )
    return result


def _short(addr: str, n: int = 8) -> str:
    """Short display form of an address for logging."""
    return addr[:n] + "…" if len(addr) > n else addr
