"""
blockchain/graph.py
────────────────────
NetworkX directed graph construction with incremental BFS traversal.

Design principles:
  - Nodes  = Tron wallet addresses (strings)
  - Edges  = Transactions (directed: sender → receiver)
  - Edge attributes carry the full NormalizedTx fields for downstream analysis
  - BFS expansion is capped at MAX_HOP_DEPTH hops for demo speed
  - Majority-flow vs peel-chain distinction is computed per node

Majority-flow logic (peel-chain awareness):
  From any node, the outgoing edge that carries >= MAJORITY_FLOW_THRESHOLD of
  the total outflow is tagged as the "majority" (bulk) path. All other outgoing
  edges from the same node are "peeled" (minor) amounts — a peel-chain pattern.
  This distinction is passed to the tracer and clustering layers.
"""
from __future__ import annotations

import logging
from collections import deque
from typing import Callable, Dict, List, Optional, Set, Tuple

import networkx as nx

from blockchain.config import MAX_HOP_DEPTH, MAJORITY_FLOW_THRESHOLD
from blockchain.models import NormalizedTx

logger = logging.getLogger(__name__)


class TronGraph:
    """
    Directed transaction graph for a single investigation session.
    Uses MultiDiGraph to allow parallel edges (same pair, different tx_hash).
    """

    def __init__(self) -> None:
        self.G: nx.MultiDiGraph = nx.MultiDiGraph()
        self._visited: Set[str] = set()

    # ── Core BFS expansion ────────────────────────────────────────────────────
    def expand_bfs(
        self,
        seed_address: str,
        fetch_fn: Callable[[str], List[NormalizedTx]],
        max_hops: int = MAX_HOP_DEPTH,
    ) -> None:
        """
        BFS-style incremental graph expansion from `seed_address`.

        For each address in the frontier (up to max_hops levels):
          1. Fetch its transactions via `fetch_fn`.
          2. Add every tx as a directed edge with full metadata.
          3. Enqueue newly discovered addresses (not yet visited) for
             the next hop.

        This deliberately avoids pulling the entire chain history — only
        addresses reachable from the seed within `max_hops` are fetched.
        Production investigations may increase max_hops to 10-15.

        Parameters
        ----------
        seed_address : str
            Starting wallet address (victim-reported).
        fetch_fn : Callable
            Function signature: (address: str) -> List[NormalizedTx]
            Injected so tests can pass a stub without live API calls.
        max_hops : int
            BFS depth cap. Default from config.
        """
        # Queue: (address, current_hop_depth)
        queue: deque[Tuple[str, int]] = deque([(seed_address, 0)])
        self._visited.add(seed_address)

        logger.info("[Graph] BFS start: seed=%s max_hops=%d", seed_address, max_hops)

        while queue:
            address, hop = queue.popleft()

            if hop >= max_hops:
                logger.debug("[Graph] Hop cap reached at %s (hop %d)", address, hop)
                continue

            txs = fetch_fn(address)
            logger.info(
                "[Graph] Hop %d | %s | %d txs fetched", hop, address, len(txs)
            )

            for tx in txs:
                self._add_transaction(tx)

                # Enqueue newly seen addresses for the next hop
                for neighbour in (tx.from_addr, tx.to_addr):
                    if neighbour and neighbour not in self._visited:
                        self._visited.add(neighbour)
                        queue.append((neighbour, hop + 1))

        logger.info(
            "[Graph] BFS complete: %d nodes, %d edges",
            self.G.number_of_nodes(),
            self.G.number_of_edges(),
        )

    # ── Internal edge builder ─────────────────────────────────────────────────
    def _add_transaction(self, tx: NormalizedTx) -> None:
        """
        Add a single NormalizedTx as a directed edge to the MultiDiGraph.
        MultiDiGraph allows parallel edges; each tx_hash is a unique edge.
        """
        if not tx.from_addr or not tx.to_addr:
            return

        # Check if this exact tx_hash already exists as an edge key
        existing_keys = self.G.get_edge_data(tx.from_addr, tx.to_addr)
        if existing_keys:
            for key, data in existing_keys.items():
                if data.get("tx_hash") == tx.tx_hash:
                    return  # already present

        self.G.add_edge(
            tx.from_addr,
            tx.to_addr,
            tx_hash=tx.tx_hash,
            amount=tx.amount,
            token=tx.token,
            timestamp=tx.timestamp,
            chain=tx.chain,
        )

    # ── Majority-flow / peel-chain analysis ───────────────────────────────────
    def get_majority_out_edge(
        self, address: str
    ) -> Optional[Tuple[str, str, dict]]:
        """
        From `address`, find the outgoing edge carrying the majority of funds.
        Works with MultiDiGraph: aggregates across all parallel edges.
        """
        if address not in self.G:
            return None

        # MultiDiGraph: G.out_edges(u, data=True) yields (u, v, data)
        out_edges = list(self.G.out_edges(address, data=True))
        if not out_edges:
            return None

        # Aggregate by destination
        flow_by_dest: Dict[str, float] = {}
        best_edge_by_dest: Dict[str, dict] = {}
        for (_, to_addr, data) in out_edges:
            flow_by_dest[to_addr] = flow_by_dest.get(to_addr, 0.0) + data.get("amount", 0.0)
            if to_addr not in best_edge_by_dest or data.get("amount", 0) > best_edge_by_dest[to_addr].get("amount", 0):
                best_edge_by_dest[to_addr] = data

        total_out = sum(flow_by_dest.values())
        if total_out <= 0:
            if out_edges:
                (_, to_addr, data) = max(out_edges, key=lambda e: e[2].get("timestamp", ""))
                return (address, to_addr, data)
            return None

        best_dest  = max(flow_by_dest, key=lambda d: flow_by_dest[d])
        best_share = flow_by_dest[best_dest] / total_out

        if best_share >= MAJORITY_FLOW_THRESHOLD:
            return (address, best_dest, best_edge_by_dest[best_dest])
        return None

    # ── Accessors ─────────────────────────────────────────────────────────────
    def get_all_edges(self) -> List[dict]:
        """Return all edges as a list of dicts matching the API contract."""
        result = []
        for (u, v, data) in self.G.edges(data=True):
            result.append({
                "from":      u,
                "to":        v,
                "amount":    data.get("amount", 0.0),
                "token":     data.get("token", "TRX"),
                "timestamp": data.get("timestamp", ""),
                "tx_hash":   data.get("tx_hash", ""),
                "chain":     data.get("chain", "tron"),
            })
        return result

    def get_out_neighbours(self, address: str) -> List[str]:
        if address not in self.G:
            return []
        return list(self.G.successors(address))

    def get_in_neighbours(self, address: str) -> List[str]:
        if address not in self.G:
            return []
        return list(self.G.predecessors(address))

    def nodes(self) -> List[str]:
        return list(self.G.nodes())

    def get_edges_between(self, addr_a: str, addr_b: str) -> List[dict]:
        """Return all edges from addr_a to addr_b (MultiDiGraph may have many)."""
        edge_data = self.G.get_edge_data(addr_a, addr_b) or {}
        return [data for data in edge_data.values()]
