"""
Main fraud detector orchestrating all patterns.
"""

from dataclasses import dataclass, field
from typing import Any
from .patterns import (
    FraudPattern,
    TransactionGraph,
    DetectionResult,
    MixerTumblerPattern,
    PeelChainPattern,
    RapidHoppingPattern,
    ScamClusterProximityPattern,
    StructuringPattern,
)


@dataclass
class DetectorConfig:
    """Configuration for fraud detector."""
    enable_mixer_tumbler: bool = True
    enable_peel_chain: bool = True
    enable_rapid_hopping: bool = True
    enable_scam_proximity: bool = True
    enable_structuring: bool = True

    mixer_min_degree: int = 10
    mixer_amount_similarity: float = 0.8

    peel_min_chain_length: int = 3
    peel_ratio_threshold: float = 0.1

    rapid_time_window_seconds: int = 300
    rapid_min_hops: int = 4

    scam_max_hops: int = 3
    scam_blacklist: set[str] = field(default_factory=set)

    structuring_threshold: float = 10000.0
    structuring_time_window_hours: int = 24
    structuring_min_transactions: int = 3


class FraudDetector:
    """
    Main fraud detection engine.
    Takes transaction graph data and runs all enabled patterns.
    """

    def __init__(self, config: DetectorConfig | None = None):
        self.config = config or DetectorConfig()
        self.patterns: list[FraudPattern] = []
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize all detection patterns based on config."""
        if self.config.enable_mixer_tumbler:
            self.patterns.append(MixerTumblerPattern(
                min_degree=self.config.mixer_min_degree,
                amount_similarity_threshold=self.config.mixer_amount_similarity
            ))

        if self.config.enable_peel_chain:
            self.patterns.append(PeelChainPattern(
                min_chain_length=self.config.peel_min_chain_length,
                peel_ratio_threshold=self.config.peel_ratio_threshold
            ))

        if self.config.enable_rapid_hopping:
            self.patterns.append(RapidHoppingPattern(
                time_window_seconds=self.config.rapid_time_window_seconds,
                min_hops=self.config.rapid_min_hops
            ))

        if self.config.enable_scam_proximity:
            pattern = ScamClusterProximityPattern(
                max_hops=self.config.scam_max_hops,
                blacklist=self.config.scam_blacklist.copy()
            )
            self.patterns.append(pattern)

        if self.config.enable_structuring:
            self.patterns.append(StructuringPattern(
                threshold_amount=self.config.structuring_threshold,
                time_window_hours=self.config.structuring_time_window_hours,
                min_transactions=self.config.structuring_min_transactions
            ))

    def update_scam_blacklist(self, addresses: set[str]):
        """Update scam blacklist for proximity detection."""
        for pattern in self.patterns:
            if isinstance(pattern, ScamClusterProximityPattern):
                pattern.update_blacklist(addresses)

    def detect(self, graph: TransactionGraph) -> list[DetectionResult]:
        """
        Run all enabled patterns on the transaction graph.

        Args:
            graph: TransactionGraph with transactions loaded

        Returns:
            List of DetectionResult objects, one per detected pattern instance
        """
        all_results = []
        for pattern in self.patterns:
            try:
                results = pattern.detect(graph)
                all_results.extend(results)
            except Exception as e:
                all_results.append(DetectionResult(
                    signature=f"{pattern.name}_error",
                    confidence=0.0,
                    evidence=[],
                    metadata={"error": str(e), "pattern": pattern.name}
                ))
        return all_results

    def detect_address(self, graph: TransactionGraph, address: str) -> list[DetectionResult]:
        """Run detection focused on a specific address."""
        all_results = self.detect(graph)
        return [r for r in all_results if r.metadata.get("address") == address]

    def get_pattern_names(self) -> list[str]:
        """Get names of all enabled patterns."""
        return [p.name for p in self.patterns]