# Workstream PRD — AI/ML Module
**Parent Project:** WalletTrace (SIH26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics)
**Owner:** AI/ML teammate
**Version:** v1.0 | **Status:** Draft

> Last of the five workstreams to spec, but not last in importance — this is the "trainable model" that gives you a genuine ML story (not just rules), and it's the one piece judges will most directly ask "how did you train this / what's your accuracy?" about. It sits **downstream of Blockchain's raw graph/clusters** and **Cybersecurity's fraud-pattern signals**, and feeds **the Agent's `get_risk_score` tool** and the Dashboard's risk display.

---

## 1. Role of This Module in the Overall System

Blockchain gives you *deterministic* clustering (heuristics: common-input-ownership, deposit-reuse). Cybersecurity gives you *rule-based* fraud-pattern flags (mixer usage, peel chains, blacklist proximity). Neither of those is a trained model — they're forensics logic and threat rules. **This module is where actual machine learning happens**: taking the combined signal from those two and producing a calibrated, learned risk score, plus a *behavioral* clustering layer that catches relationships the deterministic heuristics miss (e.g., addresses that don't share inputs or deposit patterns but behave suspiciously alike in timing/amount).

Being explicit about this separation matters for your pitch: you're not claiming "AI did the forensics" (which is false and judges will probe it) — you're claiming "AI learns from real forensic signal + labeled fraud data to prioritize and generalize beyond hand-written rules," which is both true and a stronger, more defensible claim.

---

## 2. Goals & Non-Goals

### Goals
- **G1:** Build a **risk-scoring model** that takes Blockchain's cluster/trace output + Cybersecurity's fraud-pattern flags as input features and outputs a calibrated 0–1 risk score with a breakdown of contributing factors (explainability, not a black box).
- **G2:** Build a **behavioral clustering layer** (embedding-based similarity on transaction timing, amount patterns, hop velocity) as a complement to Blockchain's deterministic heuristics — flag "these addresses aren't provably the same entity, but behave suspiciously alike" as a lower-confidence, separate signal.
- **G3:** Train/validate on a labeled dataset (see Section 5 — Data Strategy) so you can report real evaluation metrics (precision/recall, not just a demo that "looks right").
- **G4:** Expose the model via a documented API consumed by the Agent's `get_risk_score` tool and the Dashboard.
- **G5:** Ensure every score is explainable — output the top contributing features per prediction, not just a number.

### Non-Goals
- **NG1:** Not building the deterministic clustering/tracing (Blockchain module owns that — you consume its output as a feature).
- **NG2:** Not building the rule-based fraud-pattern signatures (Cybersecurity module owns that — you consume its flags as a feature).
- **NG3:** Not doing exchange attribution (Blockchain module's job — you're scoring risk, not identifying destinations).
- **NG4:** Not deploying a deep/black-box model with no explainability layer — for a law-enforcement-facing tool, an interpretable model (or a black-box model + a SHAP-style explanation layer) is a requirement, not a nice-to-have.

---

## 3. Deliverables (What You Personally Build)

### 3.1 Feature Engineering (from upstream modules)
Combine into a single feature vector per address/cluster:
- From Blockchain: cluster size, hop depth to seed, heuristic types that fired, fund-flow velocity (amount/time).
- From Cybersecurity: mixer-flag boolean/confidence, peel-chain-flag, blacklist-proximity distance, structuring-flag.
- Derived by you: transaction timing entropy, amount-pattern similarity to known fraud clusters, address-age, in/out-degree ratio.

### 3.2 Risk-Scoring Model
- Start with an interpretable baseline: gradient-boosted trees (XGBoost/LightGBM) or logistic regression on the engineered features — trains fast, gives clean feature-importance output, and is far easier to defend under judge questioning than a deep net with no labeled-data justification.
- Output: `{risk_score: 0–1, top_factors: [{feature, contribution}], confidence: str}`.
- Stretch goal only (if time permits): a GNN (graph neural network) operating directly on Blockchain's transaction graph for a more sophisticated behavioral signal — mention as future work if not shipped, don't over-promise it for the live demo.

### 3.3 Behavioral Clustering Layer
- Compute address embeddings from behavioral features (timing patterns, amount distributions, hop velocity) — a lightweight approach (e.g., feature vector + cosine similarity or a simple autoencoder) is enough; this doesn't need to be exotic.
- Flag high-similarity pairs *not* already merged by Blockchain's deterministic heuristics as a separate, clearly-labeled "behavioral similarity" signal (lower confidence than deterministic clustering — never conflate the two in the UI).

### 3.4 Explainability Layer
- For every risk score, surface the top 3–5 contributing features in plain language (e.g., "high risk mainly due to: rapid multi-hop movement, proximity to blacklisted cluster").
- This is what both the Dashboard's explainability panel and the Agent's grounded responses will cite — treat it as a first-class output, not an afterthought.

### 3.5 Model Evaluation
- Report standard metrics (precision, recall, F1, confusion matrix) on a held-out split of your labeled dataset.
- Document known limitations honestly (e.g., "trained on synthetic + public fraud-report data, real Indian NCRP data unavailable") — judges respond far better to honest limitations than to inflated accuracy claims.

---

## 4. Functional Requirements (This Module Only)

| ID | Requirement | Priority |
|---|---|---|
| ML-FR1 | Module shall combine Blockchain and Cybersecurity outputs into a feature vector per address/cluster. | Must |
| ML-FR2 | Module shall output a calibrated risk score (0–1) with top contributing factors. | Must |
| ML-FR3 | Module shall provide a behavioral-similarity signal distinct from deterministic clustering. | Should |
| ML-FR4 | Module shall report evaluation metrics on a held-out labeled dataset. | Must |
| ML-FR5 | Module shall expose scoring via a documented API for the Agent and Dashboard. | Must |
| ML-FR6 | Module shall (stretch) support a GNN-based scoring variant operating on the raw transaction graph. | Could |

---

## 5. Data Strategy (Judges Will Ask — Have This Ready)

- **No real NCRP/labeled Indian fraud-wallet dataset will be available.** Use:
  - Public labeled fraud-address datasets (e.g., academic datasets of scam/phishing/ransomware addresses, Elliptic-style labeled transaction datasets referenced in blockchain-forensics research) for real positive labels.
  - Synthetic negative examples (legitimate-looking transaction patterns) generated to balance the dataset.
- Document exact sources and labeling methodology in your model card — this transparency is what separates a credible ML claim from a black-box demo.
- Be upfront in the pitch that production deployment would need a data-sharing/federated-learning arrangement with banks/exchanges (this is already flagged as a talking point in the master architecture) — you don't need to build this, just show you've thought about it.

---

## 6. Tech Stack

| Layer | Tools |
|---|---|
| Feature engineering | Python, pandas |
| Risk model | XGBoost / LightGBM (baseline), scikit-learn for evaluation; PyTorch Geometric only if GNN stretch goal is attempted |
| Explainability | Native feature-importance (tree models) or SHAP if time permits |
| Behavioral clustering | scikit-learn (cosine similarity / simple embeddings) |
| API | FastAPI, consumed by Agent + Dashboard |

---

## 7. Integration Interfaces

| From/To | Interface |
|---|---|
| Blockchain module | Consumes cluster/trace/heuristic-evidence output as input features — **confirm exact JSON field names with them** |
| Cybersecurity module | Consumes fraud-pattern flags (mixer/peel-chain/blacklist/structuring) as input features |
| Agentic AI module | Provides `get_risk_score(address_or_cluster)` → `{risk_score, top_factors, confidence}` for their tool wrapper |
| Dashboard | Provides risk score + explanation for the UI's risk display / explainability panel |

You are the **third dependency in the chain** (after Blockchain and Cybersecurity) — you can't fully train/score until their output schemas are locked, so build against mocked feature vectors first and get their real schemas as early as possible.

---

## 8. Demo Script (Your Segment)

1. Once Blockchain traces + clusters and Cybersecurity flags patterns, this module's score appears on the dashboard: "Risk: 0.87 — high, primarily due to rapid multi-hop movement and blacklist proximity."
2. If asked "how was this trained," show the evaluation metrics slide (precision/recall on held-out data) and the labeled-data sources.
3. If a behavioral-similarity flag fires on addresses the deterministic clustering didn't merge, highlight it as a distinct, lower-confidence signal — a good "look how nuanced our system is" moment if judges probe.

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| No real labeled fraud data | Use public labeled datasets + synthetic negatives; document methodology transparently (Section 5) |
| Model looks like a black box under questioning | Lead with an interpretable baseline (tree model) + explicit feature-importance output; keep GNN as unshipped stretch goal only |
| Blocked waiting on Blockchain/Cybersecurity schemas | Build and train against a mocked feature vector first; retrain once real schemas land |
| Overclaiming accuracy | Report honest metrics on a small held-out set rather than an inflated headline number |

---

## 10. Open Items Before Build Starts

- Confirm exact feature schema from Blockchain and Cybersecurity modules (their evidence/flag field names).
- Identify and download the specific public labeled fraud-address dataset(s) to use.
- Decide whether the GNN stretch goal is realistic given team time — default assumption: no, ship the tree-model baseline solidly instead.
- Agree on the risk-score threshold the Agent uses to decide "draft notice" vs. "recommend manual review" (this was flagged as an open item in the Agentic AI PRD too — needs a joint decision).

---

*Workstream-level document. Depends on Blockchain and Cybersecurity PRDs (already delivered); feeds the Agentic AI PRD's `get_risk_score` tool. This completes all five workstream PRDs — next step is the shared data-contract pass to lock field names before build starts.*
