"""
ml/features.py
───────────────
Feature engineering pipeline for the WalletTrace ML Risk Scoring model.

Takes:
  - BlockchainFeatures (from POST /trace response)
  - CybersecurityFlags (from POST /check-patterns response, or defaults)

Produces:
  - A fixed-length numpy feature vector (FEATURE_NAMES order)
  - Used by both train.py (training) and model.py (inference)

IMPORTANT: FEATURE_NAMES is the canonical feature order.
The trained model.pkl MUST match this order exactly.
Do NOT reorder without retraining.
"""
from __future__ import annotations

import math
from typing import List

import numpy as np

from ml.models import BlockchainFeatures, CybersecurityFlags

# ── Canonical feature column order (must match training) ──────────────────────
FEATURE_NAMES: List[str] = [
    # Blockchain-derived
    "cluster_size",
    "hop_depth",
    "fund_flow_velocity",
    "in_degree",
    "out_degree",
    "tx_count",
    "total_inflow",
    "total_outflow",
    "inout_ratio",              # out / (in + 1e-9)
    "heuristic_count",          # number of distinct heuristics that fired
    "has_deposit_reuse",        # 1 if deposit_address_reuse heuristic fired
    "has_common_funding",       # 1 if common_funding_source heuristic fired
    "has_repeated_interaction", # 1 if repeated_interactions heuristic fired
    # Cybersecurity-derived
    "mixer_flag",
    "peel_chain_flag",
    "rapid_hop_flag",
    "structuring_flag",
    "blacklist_reachable",      # 1 if blacklist_proximity >= 0
    "blacklist_proximity_inv",  # 1 / (proximity + 1); 0 if not found
    "mixer_confidence",
    "peel_chain_confidence",
    # Derived composite
    "combined_cyber_score",     # average of non-zero cyber confidences
    "velocity_x_hop",           # fund_flow_velocity * hop_depth (interaction term)
    "cluster_x_hop",            # cluster_size * hop_depth
]


def build_feature_vector(
    bc: BlockchainFeatures,
    cy: CybersecurityFlags,
) -> np.ndarray:
    """
    Constructs the feature vector from Blockchain + Cybersecurity inputs.
    Returns a 1-D numpy array of shape (len(FEATURE_NAMES),).
    """
    heuristic_count    = len(bc.heuristic_types)
    has_deposit_reuse  = int("deposit_address_reuse"  in bc.heuristic_types)
    has_common_funding = int("common_funding_source"   in bc.heuristic_types)
    has_repeated       = int("repeated_interactions"   in bc.heuristic_types)

    inout_ratio = bc.total_outflow / (bc.total_inflow + 1e-9)

    blacklist_reachable   = int(cy.blacklist_proximity >= 0)
    blacklist_prox_inv    = (1.0 / (cy.blacklist_proximity + 1)) if cy.blacklist_proximity >= 0 else 0.0

    # Combined cyber score: mean of non-zero flag confidences
    cyber_signals = [
        cy.mixer_confidence     if cy.mixer_flag        else 0.0,
        cy.peel_chain_confidence if cy.peel_chain_flag  else 0.0,
        0.8                     if cy.rapid_hop_flag    else 0.0,
        0.7                     if cy.structuring_flag  else 0.0,
        blacklist_prox_inv,
    ]
    combined_cyber = float(np.mean(cyber_signals))

    velocity_x_hop = bc.fund_flow_velocity * bc.hop_depth
    cluster_x_hop  = bc.cluster_size        * bc.hop_depth

    vec = [
        bc.cluster_size,
        bc.hop_depth,
        bc.fund_flow_velocity,
        bc.in_degree,
        bc.out_degree,
        bc.tx_count,
        bc.total_inflow,
        bc.total_outflow,
        inout_ratio,
        heuristic_count,
        has_deposit_reuse,
        has_common_funding,
        has_repeated,
        int(cy.mixer_flag),
        int(cy.peel_chain_flag),
        int(cy.rapid_hop_flag),
        int(cy.structuring_flag),
        blacklist_reachable,
        blacklist_prox_inv,
        cy.mixer_confidence,
        cy.peel_chain_confidence,
        combined_cyber,
        velocity_x_hop,
        cluster_x_hop,
    ]

    assert len(vec) == len(FEATURE_NAMES), (
        f"Feature count mismatch: {len(vec)} vs {len(FEATURE_NAMES)}"
    )
    return np.array(vec, dtype=float)
