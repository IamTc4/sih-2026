# WalletTrace ML Model Card
**Model version:** xgboost-v1
**Algorithm:** XGBoost (gradient-boosted trees)
**Last trained:** 2026-09-04

## Training Data
- 300 samples total (150 fraud + 150 legitimate)
- Synthetic dataset generated from realistic Tron/USDT-TRC20 behavioral patterns
- Fraud samples: high hop depth, multiple heuristics, mixer/peel-chain flags, blacklist proximity
- Legitimate samples: low hop depth, no cybersecurity flags, exchange-like patterns

## Evaluation Metrics (20% held-out test split — 60 samples)
| Metric     | Value  |
|------------|--------|
| Accuracy   | 1.0000 |
| AUC-ROC    | 1.0000 |
| Precision (fraud) | 1.0000 |
| Recall (fraud)    | 1.0000    |
| F1-Score (fraud)  | 1.0000  |

## Confusion Matrix
```
              Predicted: Legit  Predicted: Fraud
Actual: Legit      30                0
Actual: Fraud       0               30
```

## Features (24 total)
- `cluster_size`
- `hop_depth`
- `fund_flow_velocity`
- `in_degree`
- `out_degree`
- `tx_count`
- `total_inflow`
- `total_outflow`
- `inout_ratio`
- `heuristic_count`
- `has_deposit_reuse`
- `has_common_funding`
- `has_repeated_interaction`
- `mixer_flag`
- `peel_chain_flag`
- `rapid_hop_flag`
- `structuring_flag`
- `blacklist_reachable`
- `blacklist_proximity_inv`
- `mixer_confidence`
- `peel_chain_confidence`
- `combined_cyber_score`
- `velocity_x_hop`
- `cluster_x_hop`

## Top Feature Importances
- `cluster_size`: 0.4851
- `hop_depth`: 0.4112
- `fund_flow_velocity`: 0.0515
- `blacklist_reachable`: 0.0194
- `mixer_confidence`: 0.0167
- `peel_chain_confidence`: 0.0161
- `combined_cyber_score`: 0.0000
- `cluster_x_hop`: 0.0000

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
