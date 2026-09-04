"""
ml/model.py
────────────
XGBoost Risk-Scoring Model — load, train interface, and inference.

ML PRD Section 3.2:
  "Start with an interpretable baseline: gradient-boosted trees (XGBoost/LightGBM)
   or logistic regression on the engineered features — trains fast, gives clean
   feature-importance output, and is far easier to defend under judge questioning
   than a deep net with no labeled-data justification."

At startup, the FastAPI app loads a pre-trained model.pkl produced by train.py.
If model.pkl does not exist, a fallback rule-based scorer is used so the service
starts cleanly even before training has been run.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from ml.config import settings
from ml.features import FEATURE_NAMES, build_feature_vector
from ml.models import BlockchainFeatures, CybersecurityFlags, RiskFactor
from ml.explainability import compute_top_factors

logger = logging.getLogger(__name__)

MODEL_VERSION = "xgboost-v1"


class RiskScoringModel:
    """
    Wraps an XGBoost classifier for risk score inference.

    Attributes
    ----------
    _clf         : loaded XGBoost classifier (or None if not available)
    _importances : feature importance array aligned with FEATURE_NAMES
    _is_trained  : True when a real model is loaded
    """

    def __init__(self):
        self._clf          = None
        self._importances: np.ndarray = np.ones(len(FEATURE_NAMES)) / len(FEATURE_NAMES)
        self._is_trained   = False
        self._load()

    def _load(self) -> None:
        """Attempt to load the pre-trained model from MODEL_PATH."""
        path = Path(settings.MODEL_PATH)
        if not path.exists():
            logger.warning(
                "[ML] model.pkl not found at %s — using rule-based fallback scorer. "
                "Run python train.py to train and save the model.",
                path,
            )
            return

        try:
            import joblib
            self._clf = joblib.load(path)
            # XGBoost stores feature importances as dict keyed by feature name or array
            if hasattr(self._clf, "feature_importances_"):
                self._importances = self._clf.feature_importances_
            self._is_trained = True
            logger.info("[ML] Loaded trained model from %s (version=%s)", path, MODEL_VERSION)
        except Exception as exc:
            logger.error("[ML] Failed to load model: %s — using fallback", exc)

    # ── Public interface ──────────────────────────────────────────────────────

    def predict(
        self,
        bc: BlockchainFeatures,
        cy: CybersecurityFlags,
    ) -> Tuple[float, list[RiskFactor], str]:
        """
        Compute risk score for an address given its feature inputs.

        Returns
        -------
        (risk_score, top_factors, confidence_label)
        """
        vec = build_feature_vector(bc, cy)

        if self._is_trained and self._clf is not None:
            risk_score = self._predict_xgb(vec)
        else:
            risk_score = self._fallback_score(vec)

        top_factors = compute_top_factors(vec, self._importances, top_n=5)
        confidence  = self._confidence_label(risk_score)

        return round(risk_score, 4), top_factors, confidence

    # ── Internal ──────────────────────────────────────────────────────────────

    def _predict_xgb(self, vec: np.ndarray) -> float:
        """XGBoost predict_proba for class=1 (fraud)."""
        X = vec.reshape(1, -1)
        proba = self._clf.predict_proba(X)[0][1]
        return float(proba)

    def _fallback_score(self, vec: np.ndarray) -> float:
        """
        Rule-based fallback used when model.pkl is absent.
        Weighted sum of the most discriminative features.
        This is explicitly deterministic and explainable — not a black box.
        """
        feat = dict(zip(FEATURE_NAMES, vec))

        score = 0.0
        # Blockchain signals
        score += min(feat["hop_depth"]         / 5.0, 1.0) * 0.20
        score += min(feat["cluster_size"]      / 5.0, 1.0) * 0.10
        score += min(feat["fund_flow_velocity"]/ 1000.0, 1.0) * 0.10
        score += feat["has_deposit_reuse"]               * 0.12
        score += feat["has_common_funding"]              * 0.08
        score += feat["has_repeated_interaction"]        * 0.06
        # Cybersecurity signals
        score += feat["mixer_flag"]            * 0.15
        score += feat["peel_chain_flag"]       * 0.10
        score += feat["rapid_hop_flag"]        * 0.05
        score += feat["blacklist_reachable"]   * 0.04

        # Override importances for fallback (uniform across features used)
        idx_map = {n: i for i, n in enumerate(FEATURE_NAMES)}
        imp = np.zeros(len(FEATURE_NAMES))
        for name, w in [
            ("hop_depth",0.20), ("cluster_size",0.10), ("fund_flow_velocity",0.10),
            ("has_deposit_reuse",0.12), ("has_common_funding",0.08),
            ("has_repeated_interaction",0.06), ("mixer_flag",0.15),
            ("peel_chain_flag",0.10), ("rapid_hop_flag",0.05), ("blacklist_reachable",0.04),
        ]:
            imp[idx_map[name]] = w
        self._importances = imp

        return float(min(score, 1.0))

    def _confidence_label(self, score: float) -> str:
        if score >= settings.HIGH_CONFIDENCE_THRESHOLD:
            return "high"
        if score >= settings.MEDIUM_CONFIDENCE_THRESHOLD:
            return "medium"
        return "low"

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    @property
    def feature_importances(self) -> np.ndarray:
        return self._importances


# ── Module-level singleton loaded once at startup ─────────────────────────────
_model: Optional[RiskScoringModel] = None


def get_model() -> RiskScoringModel:
    global _model
    if _model is None:
        _model = RiskScoringModel()
    return _model
