"""
train.py
─────────
One-shot training script for the WalletTrace ML risk-scoring model.

ML PRD Section 3.5:
  "Report standard metrics (precision, recall, F1, confusion matrix) on a
   held-out split of your labeled dataset. Document known limitations honestly."

Usage:
  cd ML
  python train.py

Output:
  ml/data/model.pkl   — trained XGBoost model (loaded by ml/model.py at startup)
  ml/data/model_card.md — auto-generated metrics report

Data source:
  ../blockchain/data/mock_transactions.json  (always available)
  Synthetic fraud/legitimate samples are generated programmatically so this
  script works out-of-the-box without any external dataset download.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from ml.features import FEATURE_NAMES, build_feature_vector
from ml.models import BlockchainFeatures, CybersecurityFlags

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "ml" / "data"
MODEL_PATH = OUTPUT_DIR / "model.pkl"
CARD_PATH  = OUTPUT_DIR / "model_card.md"


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic dataset generator
# Produces realistic fraud and legitimate feature vectors for training.
# ─────────────────────────────────────────────────────────────────────────────

def _make_fraud_sample(rng: np.random.Generator) -> tuple:
    bc = BlockchainFeatures(
        cluster_size       = int(rng.integers(3, 10)),
        hop_depth          = int(rng.integers(3, 6)),
        heuristic_types    = [
            ["deposit_address_reuse", "common_funding_source"],
            ["deposit_address_reuse", "repeated_interactions"],
            ["common_funding_source"],
            ["deposit_address_reuse"],
        ][int(rng.integers(0, 4))],
        fund_flow_velocity = float(rng.uniform(500, 5000)),
        in_degree          = int(rng.integers(1, 5)),
        out_degree         = int(rng.integers(3, 10)),
        tx_count           = int(rng.integers(5, 30)),
        total_inflow       = float(rng.uniform(50000, 500000)),
        total_outflow      = float(rng.uniform(45000, 490000)),
    )
    cy = CybersecurityFlags(
        mixer_flag               = bool(rng.random() > 0.4),
        peel_chain_flag          = bool(rng.random() > 0.3),
        rapid_hop_flag           = bool(rng.random() > 0.2),
        structuring_flag         = bool(rng.random() > 0.5),
        blacklist_proximity      = int(rng.integers(0, 3)),
        mixer_confidence         = float(rng.uniform(0.5, 1.0)),
        peel_chain_confidence    = float(rng.uniform(0.5, 1.0)),
    )
    return build_feature_vector(bc, cy), 1


def _make_legit_sample(rng: np.random.Generator) -> tuple:
    bc = BlockchainFeatures(
        cluster_size       = int(rng.integers(1, 3)),
        hop_depth          = int(rng.integers(0, 3)),
        heuristic_types    = [],
        fund_flow_velocity = float(rng.uniform(0, 200)),
        in_degree          = int(rng.integers(1, 8)),
        out_degree         = int(rng.integers(1, 8)),
        tx_count           = int(rng.integers(1, 15)),
        total_inflow       = float(rng.uniform(1000, 100000)),
        total_outflow      = float(rng.uniform(500, 95000)),
    )
    cy = CybersecurityFlags(
        mixer_flag               = False,
        peel_chain_flag          = bool(rng.random() > 0.85),
        rapid_hop_flag           = False,
        structuring_flag         = False,
        blacklist_proximity      = -1,
        mixer_confidence         = 0.0,
        peel_chain_confidence    = float(rng.uniform(0.0, 0.3)),
    )
    return build_feature_vector(bc, cy), 0


def generate_dataset(n_fraud: int = 150, n_legit: int = 150, seed: int = 42):
    rng = np.random.default_rng(seed)
    samples, labels = [], []
    for _ in range(n_fraud):
        vec, label = _make_fraud_sample(rng)
        samples.append(vec); labels.append(label)
    for _ in range(n_legit):
        vec, label = _make_legit_sample(rng)
        samples.append(vec); labels.append(label)
    X = np.array(samples)
    y = np.array(labels)
    return X, y


# ─────────────────────────────────────────────────────────────────────────────
# Training pipeline
# ─────────────────────────────────────────────────────────────────────────────

def train():
    logger.info("=== WalletTrace ML — Training Pipeline ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate dataset
    logger.info("Generating synthetic training dataset (fraud + legitimate samples)...")
    X, y = generate_dataset(n_fraud=150, n_legit=150, seed=42)
    logger.info("Dataset: %d samples | %d features | fraud=%d legit=%d",
                len(y), X.shape[1], y.sum(), (y == 0).sum())

    # 2. Train / test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info("Train=%d  Test=%d", len(y_train), len(y_test))

    # 3. Train XGBoost classifier
    logger.info("Training XGBoost classifier...")
    clf = XGBClassifier(
        n_estimators     = 200,
        max_depth        = 5,
        learning_rate    = 0.05,
        subsample        = 0.8,
        colsample_bytree = 0.8,
        use_label_encoder= False,
        eval_metric      = "logloss",
        random_state     = 42,
    )
    clf.fit(X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False)

    # 4. Evaluate
    y_pred  = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    acc     = accuracy_score(y_test, y_pred)
    auc     = roc_auc_score(y_test, y_proba)
    report  = classification_report(y_test, y_pred,
                                     target_names=["legitimate", "fraud"],
                                     output_dict=True)
    cm      = confusion_matrix(y_test, y_pred)

    logger.info("=== Evaluation Results ===")
    logger.info("Accuracy : %.4f", acc)
    logger.info("AUC-ROC  : %.4f", auc)
    logger.info("Precision: %.4f | Recall: %.4f | F1: %.4f",
                report["fraud"]["precision"],
                report["fraud"]["recall"],
                report["fraud"]["f1-score"])
    logger.info("Confusion Matrix:\n%s", cm)

    # 5. Save model
    joblib.dump(clf, MODEL_PATH)
    logger.info("Model saved to %s", MODEL_PATH)

    # 6. Write model card
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    card = f"""# WalletTrace ML Model Card
**Model version:** xgboost-v1
**Algorithm:** XGBoost (gradient-boosted trees)
**Last trained:** {now}

## Training Data
- 300 samples total (150 fraud + 150 legitimate)
- Synthetic dataset generated from realistic Tron/USDT-TRC20 behavioral patterns
- Fraud samples: high hop depth, multiple heuristics, mixer/peel-chain flags, blacklist proximity
- Legitimate samples: low hop depth, no cybersecurity flags, exchange-like patterns

## Evaluation Metrics (20% held-out test split — {len(y_test)} samples)
| Metric     | Value  |
|------------|--------|
| Accuracy   | {acc:.4f} |
| AUC-ROC    | {auc:.4f} |
| Precision (fraud) | {report["fraud"]["precision"]:.4f} |
| Recall (fraud)    | {report["fraud"]["recall"]:.4f}    |
| F1-Score (fraud)  | {report["fraud"]["f1-score"]:.4f}  |

## Confusion Matrix
```
              Predicted: Legit  Predicted: Fraud
Actual: Legit     {cm[0][0]:3d}              {cm[0][1]:3d}
Actual: Fraud     {cm[1][0]:3d}              {cm[1][1]:3d}
```

## Features ({len(FEATURE_NAMES)} total)
{chr(10).join(f"- `{f}`" for f in FEATURE_NAMES)}

## Top Feature Importances
{chr(10).join(f"- `{FEATURE_NAMES[i]}`: {clf.feature_importances_[i]:.4f}" for i in clf.feature_importances_.argsort()[::-1][:8])}

## Known Limitations
1. Trained on 300 synthetic samples — production would require federated learning with real labeled data from banks/exchanges.
2. No real NCRP Indian fraud-wallet labeled data was available.
3. Behavioral clustering is session-scoped (ephemeral).
4. Score is investigative intelligence only — NOT a legal determination.
5. Model does not do exchange attribution (Blockchain module's responsibility).

## How to Retrain
```bash
cd ML
python train.py
```
"""
    CARD_PATH.write_text(card, encoding="utf-8")
    logger.info("Model card written to %s", CARD_PATH)
    logger.info("=== Training complete ===")


if __name__ == "__main__":
    train()
