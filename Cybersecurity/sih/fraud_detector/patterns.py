"""
Fraud detection patterns for transaction graph analysis.
Each pattern implements a specific fraud technique detection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict
import time


@dataclass
class DetectionResult:
    """Result of a fraud pattern detection."""
    signature: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class FraudPattern(ABC):
    """Base class for fraud detection patterns."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this pattern."""
        pass

    @abstractmethod
    def detect(self, graph: "TransactionGraph", **kwargs) -> list[DetectionResult]:
        """Detect pattern in transaction graph."""
        pass


class TransactionGraph:
    """Represents a transaction graph for analysis."""

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self.adjacency: dict[str, list[dict]] = defaultdict(list)
        self.reverse_adjacency: dict[str, list[dict]] = defaultdict(list)

    def add_transaction(
        self,
        tx_hash: str,
        from_addr: str,
        to_addr: str,
        amount: float,
        timestamp: float,
        token: str = "ETH"
    ):
        """Add a transaction to the graph."""
        for addr in (from_addr, to_addr):
            if addr not in self.nodes:
                self.nodes[addr] = {
                    "address": addr,
                    "in_degree": 0,
                    "out_degree": 0,
                    "total_in": 0.0,
                    "total_out": 0.0,
                    "tx_hashes": [],
                    "timestamps": []
                }

        edge = {
            "tx_hash": tx_hash,
            "from": from_addr,
            "to": to_addr,
            "amount": amount,
            "timestamp": timestamp,
            "token": token
        }
        self.edges.append(edge)
        self.adjacency[from_addr].append(edge)
        self.reverse_adjacency[to_addr].append(edge)

        self.nodes[from_addr]["out_degree"] += 1
        self.nodes[from_addr]["total_out"] += amount
        self.nodes[from_addr]["tx_hashes"].append(tx_hash)
        self.nodes[from_addr]["timestamps"].append(timestamp)

        self.nodes[to_addr]["in_degree"] += 1
        self.nodes[to_addr]["total_in"] += amount
        self.nodes[to_addr]["tx_hashes"].append(tx_hash)
        self.nodes[to_addr]["timestamps"].append(timestamp)

    def get_neighbors(self, address: str, direction: str = "out") -> list[dict]:
        """Get neighboring transactions."""
        if direction == "out":
            return self.adjacency.get(address, [])
        return self.reverse_adjacency.get(address, [])

    def get_address_info(self, address: str) -> dict | None:
        """Get info for an address."""
        return self.nodes.get(address)


class MixerTumblerPattern(FraudPattern):
    """
    Detect mixer/tumbler usage: addresses with many-in/many-out fan patterns.
    Mixers typically have high in-degree and out-degree with similar amounts.
    """

    def __init__(
        self,
        min_degree: int = 10,
        amount_similarity_threshold: float = 0.8,
        min_unique_counterparties: int = 5
    ):
        self.min_degree = min_degree
        self.amount_similarity_threshold = amount_similarity_threshold
        self.min_unique_counterparties = min_unique_counterparties

    @property
    def name(self) -> str:
        return "mixer_tumbler"

    def detect(self, graph: TransactionGraph, **kwargs) -> list[DetectionResult]:
        results = []

        for address, info in graph.nodes.items():
            in_degree = info["in_degree"]
            out_degree = info["out_degree"]

            if in_degree < self.min_degree or out_degree < self.min_degree:
                continue

            in_edges = graph.get_neighbors(address, "in")
            out_edges = graph.get_neighbors(address, "out")

            unique_in = len(set(e["from"] for e in in_edges))
            unique_out = len(set(e["to"] for e in out_edges))

            if unique_in < self.min_unique_counterparties or unique_out < self.min_unique_counterparties:
                continue

            in_amounts = [e["amount"] for e in in_edges]
            out_amounts = [e["amount"] for e in out_edges]

            in_similarity = self._calculate_amount_similarity(in_amounts)
            out_similarity = self._calculate_amount_similarity(out_amounts)

            if in_similarity >= self.amount_similarity_threshold and out_similarity >= self.amount_similarity_threshold:
                confidence = min(0.95, (in_similarity + out_similarity) / 2 * 0.9)
                evidence = [e["tx_hash"] for e in in_edges + out_edges]

                results.append(DetectionResult(
                    signature=self.name,
                    confidence=confidence,
                    evidence=evidence,
                    metadata={
                        "address": address,
                        "in_degree": in_degree,
                        "out_degree": out_degree,
                        "unique_in": unique_in,
                        "unique_out": unique_out,
                        "in_amount_similarity": in_similarity,
                        "out_amount_similarity": out_similarity
                    }
                ))

        return results

    def _calculate_amount_similarity(self, amounts: list[float]) -> float:
        """Calculate how similar amounts are (coefficient of variation inverse)."""
        if len(amounts) < 2:
            return 0.0
        mean = sum(amounts) / len(amounts)
        if mean == 0:
            return 0.0
        variance = sum((a - mean) ** 2 for a in amounts) / len(amounts)
        cv = (variance ** 0.5) / mean
        return max(0.0, 1.0 - cv)


class PeelChainPattern(FraudPattern):
    """
    Detect peel chains: small amounts peeled off repeatedly while bulk moves on.
    Pattern: A -> (small peel) + (large remainder) -> (small peel) + (large remainder) ...
    """

    def __init__(
        self,
        peel_ratio_threshold: float = 0.1,
        min_chain_length: int = 3,
        max_peel_amount_ratio: float = 0.05
    ):
        self.peel_ratio_threshold = peel_ratio_threshold
        self.min_chain_length = min_chain_length
        self.max_peel_amount_ratio = max_peel_amount_ratio

    @property
    def name(self) -> str:
        return "peel_chain"

    def detect(self, graph: TransactionGraph, **kwargs) -> list[DetectionResult]:
        results = []
        visited_chains = set()

        for address in graph.nodes:
            chain = self._trace_peel_chain(graph, address)
            if len(chain) >= self.min_chain_length:
                chain_key = tuple(sorted(c["address"] for c in chain))
                if chain_key not in visited_chains:
                    visited_chains.add(chain_key)
                    evidence = []
                    for step in chain:
                        evidence.extend(step["tx_hashes"])
                    results.append(DetectionResult(
                        signature=self.name,
                        confidence=0.85,
                        evidence=evidence,
                        metadata={
                            "chain_length": len(chain),
                            "chain": chain,
                            "total_peeled": sum(s["peel_amount"] for s in chain)
                        }
                    ))

        return results

    def _trace_peel_chain(self, graph: TransactionGraph, start_address: str) -> list[dict]:
        """Trace a potential peel chain starting from an address."""
        chain = []
        current = start_address

        while True:
            out_edges = graph.get_neighbors(current, "out")
            if len(out_edges) != 2:
                break

            amounts = [e["amount"] for e in out_edges]
            total = sum(amounts)
            if total == 0:
                break

            smaller = min(amounts)
            larger = max(amounts)
            peel_ratio = smaller / total

            if peel_ratio > self.peel_ratio_threshold or peel_ratio < 0.001:
                break

            if smaller / larger > self.max_peel_amount_ratio:
                break

            peel_edge = next(e for e in out_edges if e["amount"] == smaller)
            bulk_edge = next(e for e in out_edges if e["amount"] == larger)

            chain.append({
                "address": current,
                "peel_amount": smaller,
                "bulk_amount": larger,
                "peel_ratio": peel_ratio,
                "peel_tx": peel_edge["tx_hash"],
                "bulk_tx": bulk_edge["tx_hash"],
                "tx_hashes": [peel_edge["tx_hash"], bulk_edge["tx_hash"]]
            })

            current = bulk_edge["to"]
            if current in [c["address"] for c in chain]:
                break

        return chain


class RapidHoppingPattern(FraudPattern):
    """
    Detect rapid hopping: unusually fast multi-hop movement within a time window.
    """

    def __init__(
        self,
        time_window_seconds: int = 300,
        min_hops: int = 4,
        max_hops: int = 20
    ):
        self.time_window_seconds = time_window_seconds
        self.min_hops = min_hops
        self.max_hops = max_hops

    @property
    def name(self) -> str:
        return "rapid_hopping"

    def detect(self, graph: TransactionGraph, **kwargs) -> list[DetectionResult]:
        results = []

        for address in graph.nodes:
            paths = self._find_rapid_paths(graph, address)
            for path in paths:
                if len(path) >= self.min_hops:
                    tx_hashes = [step["tx_hash"] for step in path]
                    time_span = path[-1]["timestamp"] - path[0]["timestamp"]
                    confidence = min(0.9, len(path) / self.max_hops * (1 - time_span / self.time_window_seconds))

                    results.append(DetectionResult(
                        signature=self.name,
                        confidence=max(0.5, confidence),
                        evidence=tx_hashes,
                        metadata={
                            "path_length": len(path),
                            "time_span_seconds": time_span,
                            "path": path
                        }
                    ))

        return results

    def _find_rapid_paths(self, graph: TransactionGraph, start: str) -> list[list[dict]]:
        """Find paths with rapid successive transactions."""
        paths = []

        def dfs(current: str, path: list[dict], start_time: float, visited: set):
            if len(path) >= self.max_hops:
                return

            out_edges = graph.get_neighbors(current, "out")
            for edge in out_edges:
                if edge["tx_hash"] in visited:
                    continue

                if edge["timestamp"] - start_time > self.time_window_seconds:
                    continue

                new_path = path + [{
                    "from": current,
                    "to": edge["to"],
                    "tx_hash": edge["tx_hash"],
                    "amount": edge["amount"],
                    "timestamp": edge["timestamp"]
                }]

                if len(new_path) >= self.min_hops:
                    paths.append(new_path)

                visited.add(edge["tx_hash"])
                dfs(edge["to"], new_path, start_time, visited)
                visited.remove(edge["tx_hash"])

        start_info = graph.get_address_info(start)
        if start_info and start_info["timestamps"]:
            earliest = min(start_info["timestamps"])
            dfs(start, [], earliest, set())

        return paths


class ScamClusterProximityPattern(FraudPattern):
    """
    Detect proximity to known scam clusters: address within N hops of blacklisted address.
    """

    def __init__(
        self,
        max_hops: int = 3,
        blacklist: set[str] | None = None,
        blacklist_source: str = "internal"
    ):
        self.max_hops = max_hops
        self.blacklist = blacklist or set()
        self.blacklist_source = blacklist_source

    @property
    def name(self) -> str:
        return "scam_cluster_proximity"

    def update_blacklist(self, addresses: set[str]):
        """Update the blacklist with new addresses."""
        self.blacklist.update(addresses)

    def detect(self, graph: TransactionGraph, **kwargs) -> list[DetectionResult]:
        results = []

        if not self.blacklist:
            return results

        for address in graph.nodes:
            distance, path = self._find_shortest_path_to_blacklist(graph, address)
            if distance is not None and distance <= self.max_hops:
                tx_hashes = [step["tx_hash"] for step in path]
                confidence = max(0.6, 1.0 - (distance / (self.max_hops + 1)))

                results.append(DetectionResult(
                    signature=self.name,
                    confidence=confidence,
                    evidence=tx_hashes,
                    metadata={
                        "address": address,
                        "distance_to_blacklist": distance,
                        "blacklisted_address": path[-1]["to"] if path else None,
                        "path": path,
                        "blacklist_source": self.blacklist_source
                    }
                ))

        return results

    def _find_shortest_path_to_blacklist(
        self,
        graph: TransactionGraph,
        start: str
    ) -> tuple[int | None, list[dict]]:
        """BFS to find shortest path to any blacklisted address."""
        if start in self.blacklist:
            return 0, []

        from collections import deque
        queue = deque([(start, 0, [])])
        visited = {start}

        while queue:
            current, dist, path = queue.popleft()

            if dist >= self.max_hops:
                continue

            out_edges = graph.get_neighbors(current, "out")
            for edge in out_edges:
                next_addr = edge["to"]
                if next_addr in visited:
                    continue

                new_path = path + [{
                    "from": current,
                    "to": next_addr,
                    "tx_hash": edge["tx_hash"],
                    "amount": edge["amount"]
                }]

                if next_addr in self.blacklist:
                    return dist + 1, new_path

                visited.add(next_addr)
                queue.append((next_addr, dist + 1, new_path))

        return None, []


class StructuringPattern(FraudPattern):
    """
    Detect structuring: multiple sub-threshold transactions summing to suspicious total.
    Common threshold: $10,000 (USD) or equivalent.
    """

    def __init__(
        self,
        threshold_amount: float = 10000.0,
        time_window_hours: int = 24,
        min_transactions: int = 3,
        max_transactions: int = 50
    ):
        self.threshold_amount = threshold_amount
        self.time_window_seconds = time_window_hours * 3600
        self.min_transactions = min_transactions
        self.max_transactions = max_transactions

    @property
    def name(self) -> str:
        return "structuring"

    def detect(self, graph: TransactionGraph, **kwargs) -> list[DetectionResult]:
        results = []

        for address, info in graph.nodes.items():
            txs = self._get_recent_transactions(graph, address)
            if len(txs) < self.min_transactions:
                continue

            clusters = self._find_structuring_clusters(txs)
            for cluster in clusters:
                if len(cluster) >= self.min_transactions:
                    total = sum(t["amount"] for t in cluster)
                    if total >= self.threshold_amount:
                        tx_hashes = [t["tx_hash"] for t in cluster]
                        confidence = min(0.9, len(cluster) / self.max_transactions * (total / self.threshold_amount))

                        results.append(DetectionResult(
                            signature=self.name,
                            confidence=confidence,
                            evidence=tx_hashes,
                            metadata={
                                "address": address,
                                "transaction_count": len(cluster),
                                "total_amount": total,
                                "threshold": self.threshold_amount,
                                "time_span_hours": (cluster[-1]["timestamp"] - cluster[0]["timestamp"]) / 3600,
                                "transactions": cluster
                            }
                        ))

        return results

    def _get_recent_transactions(self, graph: TransactionGraph, address: str) -> list[dict]:
        """Get all transactions for an address sorted by time."""
        all_txs = []
        for edge in graph.get_neighbors(address, "in") + graph.get_neighbors(address, "out"):
            all_txs.append({
                "tx_hash": edge["tx_hash"],
                "amount": edge["amount"],
                "timestamp": edge["timestamp"],
                "direction": "in" if edge["to"] == address else "out",
                "counterparty": edge["from"] if edge["to"] == address else edge["to"]
            })
        return sorted(all_txs, key=lambda x: x["timestamp"])

    def _find_structuring_clusters(self, transactions: list[dict]) -> list[list[dict]]:
        """Find clusters of transactions within time window."""
        clusters = []
        n = len(transactions)

        for i in range(n):
            cluster = [transactions[i]]
            for j in range(i + 1, min(n, i + self.max_transactions)):
                if transactions[j]["timestamp"] - transactions[i]["timestamp"] <= self.time_window_seconds:
                    cluster.append(transactions[j])
                else:
                    break
            if len(cluster) >= self.min_transactions:
                clusters.append(cluster)

        return clusters