"""
ml/behavioral.py
─────────────────
Behavioral Clustering Layer — ML PRD Section 3.3

"Compute address embeddings from behavioral features (timing patterns,
 amount distributions, hop velocity) — a lightweight approach
 (feature vector + cosine similarity) is enough."

IMPORTANT: This is LOWER CONFIDENCE than deterministic clustering.
The UI and Agent MUST clearly label this as a behavioral similarity signal,
NEVER as a definitive cluster membership claim.

This module compares a query address's feature vector against a small
in-memory reference set built from the current session's traced addresses.
In a production system, this reference set would be a persistent embedding store.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from ml.features import FEATURE_NAMES
from ml.models import BehavioralSimilarity, BlockchainFeatures, CybersecurityFlags
from ml.features import build_feature_vector
from ml.config import settings


class BehavioralClusterer:
    """
    Lightweight cosine-similarity behavioral clusterer.

    Usage:
        clusterer = BehavioralClusterer()
        clusterer.register("addr_A", bc_features_A, cy_flags_A)
        clusterer.register("addr_B", bc_features_B, cy_flags_B)
        result = clusterer.find_similar("addr_X", bc_features_X, cy_flags_X)
    """

    def __init__(self, threshold: float | None = None):
        self.threshold = threshold or settings.BEHAVIORAL_SIMILARITY_THRESHOLD
        # address -> normalised feature vector
        self._registry: Dict[str, np.ndarray] = {}

    def register(
        self,
        address: str,
        bc: BlockchainFeatures,
        cy: CybersecurityFlags,
    ) -> None:
        """Add an address's feature vector to the reference registry."""
        vec = build_feature_vector(bc, cy)
        self._registry[address] = self._normalise(vec)

    def find_similar(
        self,
        address: str,
        bc: BlockchainFeatures,
        cy: CybersecurityFlags,
    ) -> Optional[BehavioralSimilarity]:
        """
        Find addresses in the registry with cosine similarity >= threshold.
        Returns None if the registry is empty or no matches above threshold.
        """
        if not self._registry:
            return None

        query_vec = self._normalise(build_feature_vector(bc, cy))
        matches: List[Tuple[str, float]] = []

        for addr, ref_vec in self._registry.items():
            if addr == address:
                continue
            sim = float(np.dot(query_vec, ref_vec))  # cosine (both normalised)
            if sim >= self.threshold:
                matches.append((addr, sim))

        if not matches:
            return None

        matches.sort(key=lambda x: x[1], reverse=True)
        best_score = matches[0][1]
        similar_addrs = [m[0] for m in matches]

        return BehavioralSimilarity(
            similar_addresses=similar_addrs,
            similarity_score=round(best_score, 4),
            method="cosine",
        )

    @staticmethod
    def _normalise(vec: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-9)


# Module-level singleton (reused per request; state is ephemeral per process restart)
_clusterer = BehavioralClusterer()


def get_clusterer() -> BehavioralClusterer:
    return _clusterer
