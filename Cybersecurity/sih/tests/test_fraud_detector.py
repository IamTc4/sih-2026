"""
Tests for Fraud Pattern Detection Library
"""

import pytest
import time
from fraud_detector import (
    FraudDetector,
    DetectorConfig,
    TransactionGraph,
    DetectionResult,
    MixerTumblerPattern,
    PeelChainPattern,
    RapidHoppingPattern,
    ScamClusterProximityPattern,
    StructuringPattern,
)


class TestTransactionGraph:
    """Test the transaction graph data structure."""

    def test_add_transaction(self):
        graph = TransactionGraph()
        graph.add_transaction(
            tx_hash="0x123",
            from_addr="0xaaa",
            to_addr="0xbbb",
            amount=1.5,
            timestamp=time.time()
        )
        assert "0xaaa" in graph.nodes
        assert "0xbbb" in graph.nodes
        assert graph.nodes["0xaaa"]["out_degree"] == 1
        assert graph.nodes["0xbbb"]["in_degree"] == 1

    def test_get_neighbors(self):
        graph = TransactionGraph()
        now = time.time()
        graph.add_transaction("0x1", "0xaaa", "0xbbb", 1.0, now)
        graph.add_transaction("0x2", "0xbbb", "0xccc", 2.0, now + 1)

        out_edges = graph.get_neighbors("0xaaa", "out")
        assert len(out_edges) == 1
        assert out_edges[0]["tx_hash"] == "0x1"

        in_edges = graph.get_neighbors("0xbbb", "in")
        assert len(in_edges) == 1
        assert in_edges[0]["tx_hash"] == "0x1"


class TestMixerTumblerPattern:
    """Test mixer/tumbler detection."""

    def test_detects_high_fan_address(self):
        pattern = MixerTumblerPattern(min_degree=3, min_unique_counterparties=2)
        graph = TransactionGraph()
        now = time.time()

        # Create address with many in/out from different counterparties
        for i in range(5):
            graph.add_transaction(f"0x_in_{i}", f"0xsrc{i}", "0xmixer", 1.0, now + i)
        for i in range(5):
            graph.add_transaction(f"0x_out_{i}", "0xmixer", f"0xdst{i}", 1.0, now + 10 + i)

        results = pattern.detect(graph)
        assert len(results) == 1
        assert results[0].signature == "mixer_tumbler"
        assert results[0].confidence > 0.5
        assert results[0].metadata["address"] == "0xmixer"

    def test_ignores_low_degree(self):
        pattern = MixerTumblerPattern(min_degree=10)
        graph = TransactionGraph()
        now = time.time()

        graph.add_transaction("0x1", "0xaaa", "0xbbb", 1.0, now)
        graph.add_transaction("0x2", "0xbbb", "0xccc", 1.0, now + 1)

        results = pattern.detect(graph)
        assert len(results) == 0


class TestPeelChainPattern:
    """Test peel chain detection."""

    def test_detects_peel_chain(self):
        pattern = PeelChainPattern(min_chain_length=3, peel_ratio_threshold=0.15)
        graph = TransactionGraph()
        now = time.time()

        # Create peel chain: A -> (peel 0.1) + (bulk 9.9) -> (peel 0.1) + (bulk 9.8) ...
        current = "0xstart"
        bulk = 10.0
        for i in range(4):
            peel_tx = f"0xpeel_{i}"
            bulk_tx = f"0xbulk_{i}"
            peel_amt = 0.1
            bulk_amt = bulk - peel_amt
            next_addr = f"0xbulk_{i}"

            graph.add_transaction(peel_tx, current, f"0xpeel_dst_{i}", peel_amt, now + i * 2)
            graph.add_transaction(bulk_tx, current, next_addr, bulk_amt, now + i * 2 + 1)

            current = next_addr
            bulk = bulk_amt

        results = pattern.detect(graph)
        assert len(results) >= 1
        assert results[0].signature == "peel_chain"
        assert results[0].metadata["chain_length"] >= 3


class TestRapidHoppingPattern:
    """Test rapid hopping detection."""

    def test_detects_rapid_hops(self):
        pattern = RapidHoppingPattern(time_window_seconds=60, min_hops=3)
        graph = TransactionGraph()
        now = time.time()

        # Create rapid chain within 60 seconds
        addrs = ["0xa", "0xb", "0xc", "0xd", "0xe"]
        for i in range(len(addrs) - 1):
            graph.add_transaction(
                f"0xhop_{i}",
                addrs[i],
                addrs[i + 1],
                1.0,
                now + i * 10  # 10 seconds apart
            )

        results = pattern.detect(graph)
        assert len(results) >= 1
        assert results[0].signature == "rapid_hopping"
        assert results[0].metadata["path_length"] >= 3

    def test_ignores_slow_hops(self):
        pattern = RapidHoppingPattern(time_window_seconds=60, min_hops=3)
        graph = TransactionGraph()
        now = time.time()

        # Same chain but over hours
        addrs = ["0xa", "0xb", "0xc", "0xd"]
        for i in range(len(addrs) - 1):
            graph.add_transaction(
                f"0xhop_{i}",
                addrs[i],
                addrs[i + 1],
                1.0,
                now + i * 3600  # 1 hour apart
            )

        results = pattern.detect(graph)
        assert len(results) == 0


class TestScamClusterProximityPattern:
    """Test scam cluster proximity detection."""

    def test_detects_proximity(self):
        blacklist = {"0xscam1", "0xscam2"}
        pattern = ScamClusterProximityPattern(max_hops=2, blacklist=blacklist)
        graph = TransactionGraph()
        now = time.time()

        # Normal user -> 0xintermediary -> 0xscam1 (2 hops)
        graph.add_transaction("0x1", "0xuser", "0xintermediary", 1.0, now)
        graph.add_transaction("0x2", "0xintermediary", "0xscam1", 1.0, now + 1)

        results = pattern.detect(graph)
        assert len(results) >= 1
        # Check user is flagged
        user_results = [r for r in results if r.metadata.get("address") == "0xuser"]
        assert len(user_results) == 1
        assert user_results[0].metadata["distance_to_blacklist"] == 2

    def test_no_false_positive_beyond_max_hops(self):
        blacklist = {"0xscam1"}
        pattern = ScamClusterProximityPattern(max_hops=2, blacklist=blacklist)
        graph = TransactionGraph()
        now = time.time()

        # 3 hops away - should not trigger
        graph.add_transaction("0x1", "0xuser", "0xa", 1.0, now)
        graph.add_transaction("0x2", "0xa", "0xb", 1.0, now + 1)
        graph.add_transaction("0x3", "0xb", "0xscam1", 1.0, now + 2)

        results = pattern.detect(graph)
        user_results = [r for r in results if r.metadata.get("address") == "0xuser"]
        assert len(user_results) == 0


class TestStructuringPattern:
    """Test structuring detection."""

    def test_detects_structuring(self):
        pattern = StructuringPattern(
            threshold_amount=100.0,
            time_window_hours=1,
            min_transactions=3
        )
        graph = TransactionGraph()
        now = time.time()

        # Multiple small transactions summing over threshold
        for i in range(5):
            graph.add_transaction(
                f"0xstruct_{i}",
                "0xsource",
                "0xtarget",
                25.0,  # 5 * 25 = 125 > 100
                now + i * 600  # 10 min apart
            )

        results = pattern.detect(graph)
        assert len(results) >= 1
        assert results[0].signature == "structuring"
        assert results[0].metadata["total_amount"] >= 100.0
        assert results[0].metadata["transaction_count"] >= 3

    def test_ignores_below_threshold(self):
        pattern = StructuringPattern(threshold_amount=100.0, min_transactions=3)
        graph = TransactionGraph()
        now = time.time()

        for i in range(3):
            graph.add_transaction(f"0x_{i}", "0xsrc", "0xdst", 20.0, now + i * 600)  # Total = 60

        results = pattern.detect(graph)
        assert len(results) == 0


class TestFraudDetector:
    """Test the main fraud detector orchestration."""

    def test_detector_runs_all_patterns(self):
        config = DetectorConfig(
            enable_mixer_tumbler=True,
            enable_peel_chain=True,
            enable_rapid_hopping=True,
            enable_scam_proximity=True,
            enable_structuring=True,
            scam_blacklist={"0xbad"}
        )
        detector = FraudDetector(config)
        graph = TransactionGraph()
        now = time.time()

        # Add some transactions for each pattern type
        # Mixer
        for i in range(12):
            graph.add_transaction(f"0xm_in_{i}", f"0xs{i}", "0xmixer", 1.0, now + i)
        for i in range(12):
            graph.add_transaction(f"0xm_out_{i}", "0xmixer", f"0xd{i}", 1.0, now + 20 + i)

        # Scam proximity
        graph.add_transaction("0xp1", "0xuser", "0xmid", 1.0, now)
        graph.add_transaction("0xp2", "0xmid", "0xbad", 1.0, now + 1)

        results = detector.detect(graph)
        signatures = {r.signature for r in results}

        assert "mixer_tumbler" in signatures
        assert "scam_cluster_proximity" in signatures

    def test_detector_config_enables_disables_patterns(self):
        config = DetectorConfig(
            enable_mixer_tumbler=False,
            enable_peel_chain=True
        )
        detector = FraudDetector(config)
        names = detector.get_pattern_names()

        assert "mixer_tumbler" not in names
        assert "peel_chain" in names

    def test_update_scam_blacklist(self):
        config = DetectorConfig(scam_blacklist={"0xold"})
        detector = FraudDetector(config)

        detector.update_scam_blacklist({"0xnew1", "0xnew2"})

        for pattern in detector.patterns:
            if isinstance(pattern, ScamClusterProximityPattern):
                assert "0xnew1" in pattern.blacklist
                assert "0xnew2" in pattern.blacklist
                assert "0xold" in pattern.blacklist


if __name__ == "__main__":
    pytest.main([__file__, "-v"])