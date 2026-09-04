"""
ml/explainability.py
─────────────────────
Human-readable explanation layer for ML risk scores.

Per ML PRD Section 3.4:
  "For every risk score, surface the top 3-5 contributing features in
   plain language. This is what both the Dashboard's explainability panel
   and the Agent's grounded responses will cite — treat it as a first-class
   output, not an afterthought."

Uses the XGBoost model's native feature_importances_ (gain-based) combined
with the per-sample feature vector values to produce directional contributions.
This is a lightweight alternative to full SHAP that runs fast at inference time.
"""
from __future__ import annotations

from typing import List

import numpy as np

from ml.features import FEATURE_NAMES
from ml.models import RiskFactor

# ── Plain-text templates for each feature ─────────────────────────────────────
_PLAIN_TEXT: dict = {
    "cluster_size":            "Large cluster of co-controlled wallets detected",
    "hop_depth":               "Deep multi-hop fund movement (layering)",
    "fund_flow_velocity":      "Rapid fund movement (high velocity)",
    "in_degree":               "Many incoming wallet connections",
    "out_degree":              "Many outgoing wallet connections (fan-out pattern)",
    "tx_count":                "High transaction count",
    "total_inflow":            "Large total incoming volume",
    "total_outflow":           "Large total outgoing volume",
    "inout_ratio":             "High outflow-to-inflow ratio (funds being moved out quickly)",
    "heuristic_count":         "Multiple forensic heuristics triggered",
    "has_deposit_reuse":       "Deposit address reuse pattern detected (common fraud signature)",
    "has_common_funding":      "Common funding source with other mule wallets",
    "has_repeated_interaction":"Repeated high-volume interactions between wallet pair",
    "mixer_flag":              "Mixer/tumbler usage detected (obfuscation attempt)",
    "peel_chain_flag":         "Peel-chain layering pattern (classic structuring)",
    "rapid_hop_flag":          "Unusually rapid hop movement within short timeframe",
    "structuring_flag":        "Structuring detected (sub-threshold transaction splitting)",
    "blacklist_reachable":     "Address is reachable from a known blacklisted wallet",
    "blacklist_proximity_inv": "Close proximity to blacklisted address",
    "mixer_confidence":        "High confidence mixer/tumbler signature",
    "peel_chain_confidence":   "High confidence peel-chain pattern",
    "combined_cyber_score":    "Multiple cybersecurity threat signatures triggered",
    "velocity_x_hop":          "High velocity combined with deep hop depth (rapid layering)",
    "cluster_x_hop":           "Large co-controlled cluster with deep fund movement",
}


def compute_top_factors(
    feature_vector: np.ndarray,
    feature_importances: np.ndarray,
    top_n: int = 5,
) -> List[RiskFactor]:
    """
    Computes top contributing risk factors.

    Combines model's global feature importance (gain) with the magnitude
    of the per-sample feature value to produce a directional contribution.

    Parameters
    ----------
    feature_vector      : 1-D array of feature values for this sample
    feature_importances : 1-D array of model's gain-based importances
    top_n               : number of top factors to return

    Returns
    -------
    List[RiskFactor] sorted descending by contribution, length <= top_n.
    Only returns factors with positive contribution (features that increased risk).
    """
    # Normalise importances to [0, 1]
    total_imp = feature_importances.sum()
    if total_imp == 0:
        normalised_imp = feature_importances
    else:
        normalised_imp = feature_importances / total_imp

    # Per-sample contribution = importance × |feature_value| (scaled to 0-1 range)
    # Simple but fast — avoids full SHAP tree explainer which requires full dataset
    max_val = np.abs(feature_vector).max()
    scaled_values = np.abs(feature_vector) / (max_val + 1e-9)
    contributions = normalised_imp * scaled_values

    # Sort descending
    sorted_indices = np.argsort(contributions)[::-1]
    top_indices = sorted_indices[:top_n]

    factors: List[RiskFactor] = []
    for idx in top_indices:
        contrib = float(contributions[idx])
        if contrib < 1e-6:
            continue
        name = FEATURE_NAMES[idx]
        factors.append(RiskFactor(
            feature=name,
            contribution=round(contrib, 4),
            plain_text=_PLAIN_TEXT.get(name, name.replace("_", " ").title()),
        ))

    return factors
