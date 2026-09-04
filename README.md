# WalletTrace — End-to-End Crypto Forensics & Incident Response Platform
**SIH 2026 Problem Statement: 26183 | MHA I4C Cyber Crime Investigation**

WalletTrace is an integrated, explainable cryptocurrency forensics and law enforcement intelligence platform designed specifically for investigating crypto mule accounts, fraudulent USDT-TRC20 flows, and automated legal notice generation.

---

## 🏛 System Architecture

The system operates across 4 core microservices orchestrated on a single machine or multi-container environment:

```
                               ┌──────────────────────────────────────────────┐
                               │       WalletTrace Web Dashboard (3000)       │
                               │  - Interactive Graph & Peel-Chain Explorer   │
                               │  - Real-time Risk Score & Factors Panel      │
                               │  - Agentic Legal Notice & Bank Freeze UI     │
                               │  - SHA-256 Audit Trail & Evidence Vault      │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       │ (REST /api/agent)            │ (REST /api/blockchain)       │ (REST /api/ml)
                       ▼                              ▼                              ▼
        ┌────────────────────────────┐ ┌─────────────────────────────┐ ┌────────────────────────────┐
        │     Agentic AI Engine      │ │     Blockchain Forensics    │ │    ML Risk Scoring (XGB)   │
        │        (Port 8001)         │ │         (Port 8000)         │ │        (Port 8002)         │
        ├────────────────────────────┤ ├─────────────────────────────┤ ├────────────────────────────┤
        │ - LangGraph State Machine  │ │ - Tron USDT-TRC20 Ingestion │ │ - XGBoost Fraud Classifier │
        │ - Attribution Guardrails   │ │ - NetworkX Graph Builder    │ │ - Feature Engineering (24)│
        │ - Grounded Prompt Engine   │ │ - Deterministic Clustering  │ │ - Cosine Behavioral Sim.   │
        │ - Sec. 91 CrPC Auto-Draft  │ │ - Multi-Hop Peel-Chain Trace│ │ - Model Card Transparency  │
        │ - Prompt Injection Defense │ │ - Exchange Attribution DB   │ │ - Courtroom-Defensible EXP │
        └──────────────┬─────────────┘ └─────────────────────────────┘ └────────────────────────────┘
                       │
                       ▼ (Audit Log Chain)
        ┌────────────────────────────┐
        │  Cybersecurity & Logging   │
        │        (Port 8003)         │
        └────────────────────────────┘
```

---

## 🚀 Quick Start — Run on a Single Machine

### Prerequisites
- Python 3.10+ (installed and added to PATH)
- Node.js 18+ and npm
- Windows PowerShell

### 1. One-Click Launch
Run the automated single-machine startup script from the project root:

```powershell
cd C:\work\sih2026
.\start_all.ps1
```

This will automatically:
1. Verify ML model weights (`ML/ml/data/model.pkl`), training the model on first launch if needed.
2. Launch the **Blockchain Forensics Service** on `http://localhost:8000`.
3. Launch the **Agentic AI Orchestrator** on `http://localhost:8001`.
4. Launch the **ML Risk Scoring Service** on `http://localhost:8002`.
5. Launch the **React/Vite Dashboard** on `http://localhost:3000`.
6. Open your default web browser to the dashboard automatically.

### 2. Stop All Services
To cleanly terminate all running microservices and release all ports:
```powershell
cd C:\work\sih2026
.\stop_all.ps1
```

---

## 🧪 Verification & Test Suites

Every module includes an automated pytest test suite that runs offline without external API dependencies:

### 1. ML Risk Scoring Tests (12/12 passing)
```bash
cd C:\work\sih2026\ML
python -m pytest tests/test_ml.py -v
```

### 2. Blockchain Forensics Tests (7/7 passing)
```bash
cd C:\work\sih2026\blockchain
python -m pytest tests/ -v
```

### 3. Agentic AI & Guardrail Tests (49/49 passing)
```bash
cd C:\work\sih2026\SIH-26-27-master\Agentic_Ai
python -m pytest tests/ -v
```

### 4. Dashboard Production Build
```bash
cd C:\work\sih2026\Dashboard
npm run build
```

---

## 📁 Repository Structure

```
sih2026/
├── blockchain/                     # Blockchain Forensics Service (Port 8000)
│   ├── ingestion/                  # TronGrid & Tronscan TRC20 Ingestion
│   ├── graph/                      # NetworkX BFS Multi-hop Graph Constructor
│   ├── clustering/                 # Deterministic Heuristic Clustering Engine
│   ├── tracing/                    # Peel-Chain Flow Ranking & Primary Path Tracer
│   ├── attribution/                # Known Exchange Attribution Matching Engine
│   ├── api/routes.py               # FastAPI Forensics Endpoints (/trace, /cluster, etc.)
│   └── tests/                      # Pytest Forensics Test Suite
│
├── ML/                             # Machine Learning Risk Scoring Engine (Port 8002)
│   ├── ml/model.py                 # Trained XGBoost Classifier Wrapper
│   ├── ml/features.py              # 24-Dimension Feature Extractor
│   ├── ml/behavioral.py            # Cosine Behavioral Clustering & Embeddings
│   ├── ml/explainability.py        # Plain-Text Feature Attribution Generator
│   ├── ml/api.py                   # FastAPI Scoring Endpoints (/risk-score, /model-info)
│   ├── train.py                    # Synthetic & Historical Training Pipeline
│   └── tests/                      # 12 Pytest Risk Model & Feature Tests
│
├── SIH-26-27-master/
│   └── Agentic_Ai/                 # Autonomous Agentic AI Module (Port 8001)
│       ├── walletrace/graph.py     # LangGraph Forensic Decision Graph
│       ├── walletrace/security.py  # Prompt Injection & Output Sanitizer
│       ├── walletrace/state.py     # Pydantic State Definition
│       ├── walletrace/tools/       # Tool Adapters (Blockchain, ML, Cyber)
│       ├── walletrace/api.py       # FastAPI Agent Endpoints (/agent/query, /health)
│       └── tests/                  # 49 Pytest Integration & Guardrail Tests
│
├── Dashboard/                      # Investigation Web Interface (Port 3000)
│   ├── src/views/                  # Main Views: Investigation, BankGateway, Audit, ModelCard
│   ├── src/components/             # GraphView, RiskPanel, ExchangePanel, AgentChat, etc.
│   ├── src/services/api.js         # Unified API Service Layer
│   ├── vite.config.js              # Vite Dev Proxy to 8000, 8001, 8002
│   └── package.json                # React 18, Cytoscape, Lucide-React, TailwindCSS
│
├── shared/                         # Locked Schema Definitions
│   └── schemas.py                  # Canonical Pydantic Models for all teams
│
├── docker-compose.yml              # Multi-container deployment specification
├── start_all.ps1                   # Single-command local startup script
├── stop_all.ps1                    # Clean shutdown script
└── README.md                       # Documentation & User Manual
```

---

## ⚖️ Legal & Courtroom Defensibility

1. **Section 91 CrPC Compliance:** Legal notice generator embeds verified transaction hashes, exchange entity identifiers, node clustering evidence, and an indelible watermark.
2. **Immutable Audit Trail:** Every investigative query and automated action generates a SHA-256 hash linked to the prior block, ensuring chain-of-custody compliance under the Indian Evidence Act.
3. **Model Transparency:** Complete model card available via `GET /model-info` detailing training parameters, feature importance, known limitations, and evaluation metrics (AUC-ROC: 1.00 on synthetic validation).
