"""
tests/test_clustering.py
─────────────────────────
TEST (b): Two addresses that both deposit into the same third address within a
time window are correctly merged into one cluster with the deposit_reuse
heuristic logged.

Also tests:
  - The heuristic_name in evidence is exactly "deposit_reuse"
  - The evidence_tx is a real tx_hash from the data
  - Addresses with no shared collector are NOT merged (no false positives)
  - The UTXO common-input-ownership heuristic returns empty list for Tron data
"""
import pytest
from typing import List

from blockchain.graph import TronGraph
from blockchain.models import NormalizedTx
from blockchain.clustering import (
    apply_deposit_reuse_heuristic,
    apply_common_input_ownership_heuristic,
    build_clusters,
)


# ── Synthetic clustering scenario ─────────────────────────────────────────────
# Three victim-facing mule wallets all forward funds to the same collector.
# MULE_A and MULE_B deposit to COLLECTOR within 60 seconds → should merge.
# MULE_C deposits to a DIFFERENT collector → should NOT merge with A/B.

COLLECTOR   = "TcollectorFraudWallet0000000001"
OTHER_COLL  = "TotherCollector00000000000002"
MULE_A      = "TmuleA00000000000000000000001"
MULE_B      = "TmuleB00000000000000000000002"
MULE_C      = "TmuleC00000000000000000000003"  # deposits to a DIFFERENT collector

BASE_TS = 1696348800  # epoch for 2023-10-03T12:00:00Z

CLUSTER_TXS: List[NormalizedTx] = [
    # MULE_A → COLLECTOR at T+0
    NormalizedTx(**{
        "from": MULE_A, "to": COLLECTOR,
        "amount": 500.0, "token": "USDT",
        "timestamp": "2023-10-03T12:00:00Z",
        "tx_hash": "TX_MULE_A_TO_COLL", "chain": "tron",
    }),
    # MULE_B → COLLECTOR at T+30s (within 1-hour window)
    NormalizedTx(**{
        "from": MULE_B, "to": COLLECTOR,
        "amount": 480.0, "token": "USDT",
        "timestamp": "2023-10-03T12:00:30Z",
        "tx_hash": "TX_MULE_B_TO_COLL", "chain": "tron",
    }),
    # MULE_C → DIFFERENT collector (should NOT merge with A or B)
    NormalizedTx(**{
        "from": MULE_C, "to": OTHER_COLL,
        "amount": 300.0, "token": "USDT",
        "timestamp": "2023-10-03T12:00:45Z",
        "tx_hash": "TX_MULE_C_TO_OTHER", "chain": "tron",
    }),
]


def _stub_fetch(address: str) -> List[NormalizedTx]:
    return [tx for tx in CLUSTER_TXS if tx.from_addr == address]


class TestDepositReuseHeuristic:
    def setup_method(self):
        self.graph = TronGraph()
        self.graph.expand_bfs(MULE_A, fetch_fn=_stub_fetch, max_hops=2)
        # Also expand from MULE_B and MULE_C so all nodes are in graph
        self.graph.expand_bfs(MULE_B, fetch_fn=_stub_fetch, max_hops=2)
        self.graph.expand_bfs(MULE_C, fetch_fn=_stub_fetch, max_hops=2)

    def test_deposit_reuse_detects_merge(self):
        """MULE_A and MULE_B must be detected as co-owned via deposit_reuse."""
        evidence = apply_deposit_reuse_heuristic(
            self.graph, CLUSTER_TXS, time_window_sec=3600
        )
        pairs = {(ev.addr_a, ev.addr_b) for ev in evidence}
        # Either (A,B) or (B,A) must appear
        found = (MULE_A, MULE_B) in pairs or (MULE_B, MULE_A) in pairs
        assert found, (
            f"Expected MULE_A↔MULE_B merge not found in evidence pairs: {pairs}"
        )

    def test_heuristic_name_is_deposit_reuse(self):
        """Every evidence entry must have heuristic_name='deposit_reuse'."""
        evidence = apply_deposit_reuse_heuristic(
            self.graph, CLUSTER_TXS, time_window_sec=3600
        )
        for ev in evidence:
            assert ev.heuristic_name == "deposit_reuse", (
                f"heuristic_name must be 'deposit_reuse', got '{ev.heuristic_name}'"
            )

    def test_evidence_tx_is_real_hash(self):
        """evidence_tx must match one of the real tx_hashes in the dataset."""
        evidence = apply_deposit_reuse_heuristic(
            self.graph, CLUSTER_TXS, time_window_sec=3600
        )
        real_hashes = {tx.tx_hash for tx in CLUSTER_TXS}
        for ev in evidence:
            assert ev.evidence_tx in real_hashes, (
                f"evidence_tx '{ev.evidence_tx}' is not a real tx_hash"
            )

    def test_mule_c_not_merged_with_a_or_b(self):
        """MULE_C goes to a different collector — must NOT be merged with A or B."""
        evidence = apply_deposit_reuse_heuristic(
            self.graph, CLUSTER_TXS, time_window_sec=3600
        )
        for ev in evidence:
            pair = {ev.addr_a, ev.addr_b}
            assert MULE_C not in pair or (MULE_A not in pair and MULE_B not in pair), (
                f"MULE_C incorrectly merged with MULE_A or MULE_B: {ev}"
            )

    def test_time_window_exclusion(self):
        """With a tiny 1-second window, even the 30-second gap should NOT merge."""
        evidence = apply_deposit_reuse_heuristic(
            self.graph, CLUSTER_TXS, time_window_sec=1
        )
        pairs = {(ev.addr_a, ev.addr_b) for ev in evidence}
        found = (MULE_A, MULE_B) in pairs or (MULE_B, MULE_A) in pairs
        assert not found, (
            "With 1-second window, 30-second gap should NOT trigger merge"
        )

    def test_build_clusters_merges_correctly(self):
        """Full build_clusters must produce a cluster containing both MULE_A and MULE_B."""
        clusters = build_clusters(self.graph, CLUSTER_TXS, time_window_sec=3600)
        merged_cluster = None
        for c in clusters:
            if MULE_A in c.addresses and MULE_B in c.addresses:
                merged_cluster = c
                break
        assert merged_cluster is not None, (
            "No cluster contains both MULE_A and MULE_B"
        )
        # Evidence must be attached to the cluster
        assert len(merged_cluster.heuristic_evidence) > 0, (
            "Merged cluster must have heuristic_evidence attached"
        )


class TestCommonInputOwnership:
    def test_returns_empty_for_tron_data(self):
        """
        Common-input-ownership heuristic must return empty list for Tron data
        because Tron is account-model (no UTXO multi-input transactions).
        """
        evidence = apply_common_input_ownership_heuristic(CLUSTER_TXS)
        assert evidence == [], (
            "common_input_ownership must return [] for Tron account-model data. "
            f"Got: {evidence}"
        )
