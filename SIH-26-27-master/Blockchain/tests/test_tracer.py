"""
tests/test_tracer.py
─────────────────────
TEST (a): A synthetic 3-hop transaction chain traces correctly end-to-end.

Proves that:
  - BFS graph expansion records all edges for a 3-hop chain
  - trace_fund_flow() follows the majority path correctly
  - The terminal address is the correct 3rd hop, not an intermediate
  - All hop data (amount, tx_hash, token) is preserved correctly
"""
import pytest
from typing import List

from blockchain.graph import TronGraph
from blockchain.models import NormalizedTx
from blockchain.tracer import trace_fund_flow


# ── Synthetic 3-hop chain ─────────────────────────────────────────────────────
# Victim → MuleA → MuleB → Exchange Deposit
SEED  = "TvictimSeed000000000000000000001"
HOP1  = "TmuleAddress1000000000000000001"
HOP2  = "TmuleAddress2000000000000000002"
TERM  = "TexchangeDeposit00000000000003"

CHAIN_TXS: List[NormalizedTx] = [
    NormalizedTx(**{
        "from": SEED,  "to": HOP1,
        "amount": 1000.0, "token": "USDT",
        "timestamp": "2024-10-15T08:00:00Z",
        "tx_hash": "TX_HOP1", "chain": "tron",
    }),
    NormalizedTx(**{
        "from": HOP1,  "to": HOP2,
        "amount": 995.0, "token": "USDT",  # slightly less (fee deducted)
        "timestamp": "2024-10-15T08:30:00Z",
        "tx_hash": "TX_HOP2", "chain": "tron",
    }),
    NormalizedTx(**{
        "from": HOP2,  "to": TERM,
        "amount": 990.0, "token": "USDT",
        "timestamp": "2024-10-15T09:00:00Z",
        "tx_hash": "TX_HOP3", "chain": "tron",
    }),
    # Peeled small amount from HOP2 — should NOT be followed
    NormalizedTx(**{
        "from": HOP2,  "to": "TpeeledSmallChange0000000000004",
        "amount": 5.0, "token": "USDT",
        "timestamp": "2024-10-15T09:01:00Z",
        "tx_hash": "TX_PEEL", "chain": "tron",
    }),
]


def _stub_fetch(address: str) -> List[NormalizedTx]:
    """Return only transactions where this address is the sender."""
    return [tx for tx in CHAIN_TXS if tx.from_addr == address]


class TestThreeHopTrace:
    def setup_method(self):
        """Build graph once per test using the stub fetch function."""
        self.graph = TronGraph()
        self.graph.expand_bfs(SEED, fetch_fn=_stub_fetch, max_hops=6)

    def test_graph_has_all_chain_edges(self):
        """All 4 edges in the synthetic chain must be in the graph."""
        edges = self.graph.get_all_edges()
        tx_hashes = {e["tx_hash"] for e in edges}
        assert "TX_HOP1" in tx_hashes, "Missing HOP1 edge"
        assert "TX_HOP2" in tx_hashes, "Missing HOP2 edge"
        assert "TX_HOP3" in tx_hashes, "Missing HOP3 edge"
        assert "TX_PEEL" in tx_hashes, "Missing peel edge"

    def test_trace_reaches_terminal(self):
        """Majority-flow trace must end at TERM, not at HOP1 or HOP2."""
        result = trace_fund_flow(self.graph, SEED, max_hops=6)
        assert result.terminal == TERM, (
            f"Expected terminal {TERM}, got {result.terminal}"
        )

    def test_trace_depth_is_three(self):
        """The trace must traverse exactly 3 hops: SEED→HOP1→HOP2→TERM."""
        result = trace_fund_flow(self.graph, SEED, max_hops=6)
        assert len(result.hops) == 3, (
            f"Expected 3 hops, got {len(result.hops)}: {[h.address for h in result.hops]}"
        )

    def test_trace_hop_order(self):
        """Hops must be in the correct order: HOP1, HOP2, TERM."""
        result = trace_fund_flow(self.graph, SEED, max_hops=6)
        addresses = [h.address for h in result.hops]
        assert addresses == [HOP1, HOP2, TERM], (
            f"Hop order wrong: {addresses}"
        )

    def test_trace_preserves_amounts(self):
        """Each hop must carry the correct amount from the synthetic data."""
        result = trace_fund_flow(self.graph, SEED, max_hops=6)
        assert result.hops[0].amount == 1000.0
        assert result.hops[1].amount == 995.0
        assert result.hops[2].amount == 990.0

    def test_trace_does_not_follow_peel(self):
        """The small peeled amount (5 USDT) must NOT be the majority path at HOP2."""
        result = trace_fund_flow(self.graph, SEED, max_hops=6)
        terminal = result.terminal
        peel_addr = "TpeeledSmallChange0000000000004"
        assert terminal != peel_addr, (
            "Tracer incorrectly followed the peeled small amount instead of bulk flow"
        )

    def test_all_addresses_in_result(self):
        """result.all_addresses must include seed + all hop addresses."""
        result = trace_fund_flow(self.graph, SEED, max_hops=6)
        assert SEED in result.all_addresses
        assert HOP1 in result.all_addresses
        assert TERM in result.all_addresses

    def test_hop_depth_cap_respected(self):
        """With max_hops=1, tracer must stop after 1 hop."""
        result = trace_fund_flow(self.graph, SEED, max_hops=1)
        assert len(result.hops) <= 1, (
            f"Hop cap violated: got {len(result.hops)} hops with max_hops=1"
        )
