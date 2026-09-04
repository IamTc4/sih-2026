# WalletTrace — End-to-End Crypto Forensics & Incident Response Platform
**SIH 2026 Problem Statement: 26183 | MHA I4C Cyber Crime Investigation**

WalletTrace is an integrated, explainable cryptocurrency forensics and law enforcement intelligence platform designed specifically for investigating crypto mule accounts, fraudulent USDT-TRC20 flows, automated Section 91 CrPC legal notices, and tamper-evident evidentiary chain of custody.

---

## 🏛 System Architecture (5 Interconnected Modules)

```
                               ┌────────────────────────────────────────────────────────┐
                               │           WalletTrace Web Dashboard (Port 3000)        │
                               │  - Interactive Graph & Multi-Hop BFS Visualizer        │
                               │  - Field Evidence Intake (OCR & QR Code Scanner)       │
                               │  - NCRP Active Cases Registry & Case Tracking          │
                               │  - Section 91 / 102 CrPC Legal Notice & PDF Export     │
                               │  - Real-time ML Risk Score & Top Factors Breakdown     │
                               │  - Tamper-Evident SHA-256 Audit Trail & Hash-Chain     │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
              ┌────────────────────────────┬───────────────┴───────────────┬────────────────────────────┐
              │ REST /api/blockchain       │ REST /api/agent               │ REST /api/ml               │ REST /api/cyber
              ▼                            ▼                               ▼                            ▼
┌─────────────────────────────┐ ┌────────────────────────────┐ ┌────────────────────────────┐ ┌─────────────────────────────┐
│     Blockchain Forensics    │ │     Agentic AI Engine      │ │    ML Risk Scoring (XGB)   │ │  Cybersecurity Threat Engine │
│         (Port 8000)         │ │        (Port 8001)         │ │        (Port 8002)         │ │         (Port 8003)         │
├─────────────────────────────┤ ├────────────────────────────┤ ├────────────────────────────┤ ├─────────────────────────────┤
│ - Tron USDT-TRC20 Ingestion │ │ - LangGraph State Machine  │ │ - XGBoost Fraud Classifier │ │ - Mixer / Tumbler Detection │
│ - NetworkX Graph Builder    │ │ - Attribution Guardrails   │ │ - 24 Feature Engineering   │ │ - Peel Chain Layering Rule  │
│ - Deterministic Clustering  │ │ - Grounded Prompt Engine   │ │ - Cosine Behavioral Sim.   │ │ - Rapid Hop Evasion Check   │
│ - Multi-Hop Peel-Chain Trace│ │ - Section 91 CrPC Drafting │ │ - Model Card Transparency  │ │ - Structuring / Smurfing    │
│ - Exchange Attribution DB   │ │ - Prompt Injection Defense │ │ - Courtroom-Defensible EXP │ │ - Curated LE Watchlists     │
│ - GET & POST /trace API     │ │ - Session Persistence     │ │ - Accuracy: 1.00, AUC: 1.0 │ │ - SHA-256 Hash Chain Vault  │
└─────────────────────────────┘ └────────────────────────────┘ └────────────────────────────┘ └─────────────────────────────┘
```

---

## 🚀 Single-Machine Quick Start

### Prerequisites
- Python 3.10+ (added to PATH)
- Node.js 18+ and npm
- Windows PowerShell

### 1. One-Click Launch (All 5 Services)
Run the automated single-machine startup script from the repository root:

```powershell
cd C:\work\sih2026
.\start_all.ps1
```

This will automatically launch:
1. **Blockchain Forensics Service** on `http://localhost:8000` (`/docs`)
2. **Agentic AI Orchestration Service** on `http://localhost:8001` (`/docs`)
3. **ML Risk Scoring Service** on `http://localhost:8002` (`/docs`)
4. **Cybersecurity & Threat Engine** on `http://localhost:8003` (`/docs`)
5. **Interactive Cyber Command Dashboard** on `http://localhost:3000`
6. Opens the dashboard in your default browser automatically.

### 2. Clean Shutdown
To cleanly terminate all running background microservices and release all ports:
```powershell
cd C:\work\sih2026
.\stop_all.ps1
```

---

## 🧪 Comprehensive Automated Test Suites

Every microservice includes an independent, automated pytest test suite running 100% offline:

| Service | Path | Command | Test Count | Pass Rate |
|---|---|---|:---:|:---:|
| **Agentic AI** | `Agentic_Ai/` | `python -m pytest tests/ -q` | 49 tests | **100% (49/49)** |
| **ML Risk Scoring** | `ML/` | `python -m pytest tests/test_ml.py -v` | 12 tests | **100% (12/12)** |
| **Blockchain** | `blockchain/` | `python -m pytest tests/ -v` | 7 tests | **100% (7/7)** |
| **Cybersecurity** | `Cybersecurity/` | `python -m pytest tests/ -v` | 7 tests | **100% (7/7)** |
| **Dashboard** | `Dashboard/` | `npm run build` | 53 modules | **100% (0 errors)** |

---

## 📁 Clean Repository Structure

```
sih2026/
├── blockchain/                     # Blockchain Forensics Service (Port 8000)
│   ├── ingestion/                  # TronGrid & Tronscan TRC20 Ingestion
│   ├── graph/                      # NetworkX BFS Multi-hop Graph Constructor
│   ├── clustering/                 # Deterministic Heuristic Clustering Engine
│   ├── tracing/                    # Peel-Chain Flow Ranking & Primary Path Tracer
│   ├── attribution/                # Known Exchange Attribution Matching Engine
│   ├── api/routes.py               # REST Endpoints (POST /trace, GET /trace/{addr})
│   └── tests/                      # 7 Pytest Forensics Tests
│
├── Agentic_Ai/                     # Autonomous Agentic AI Module (Port 8001)
│   ├── walletrace/graph.py         # LangGraph Forensic Decision State Machine
│   ├── walletrace/security.py      # Prompt Injection Defense & Sanitizer
│   ├── walletrace/tools/           # Tool Adapters (Blockchain, ML, Cyber, Legal)
│   ├── walletrace/api.py           # FastAPI Agent Endpoints (/agent/query)
│   └── tests/                      # 49 Pytest Integration & Guardrail Tests
│
├── ML/                             # Machine Learning Risk Scoring Engine (Port 8002)
│   ├── ml/model.py                 # Trained XGBoost Classifier Wrapper
│   ├── ml/features.py              # 24-Dimension Feature Fusion Extractor
│   ├── ml/behavioral.py            # Cosine Behavioral Clustering & Embeddings
│   ├── ml/explainability.py        # Plain-Text Feature Attribution Generator
│   ├── ml/api.py                   # FastAPI Scoring Endpoints (/risk-score, /model-info)
│   ├── train.py                    # Synthetic & Historical Training Pipeline
│   └── tests/                      # 12 Pytest Risk Model & Feature Tests
│
├── Cybersecurity/                  # Threat Intelligence & Evidence Vault (Port 8003)
│   ├── rules/engine.py             # Mixer, Peel-chain, Rapid-hop, Structuring, Watchlist
│   ├── audit/hash_chain.py         # Tamper-Evident SHA-256 Hash Chain Ledger
│   ├── api/routes.py               # Endpoints (/check-patterns, /blacklist, /log-event, /verify)
│   └── tests/                      # 7 Pytest Threat & Cryptographic Tests
│
├── Dashboard/                      # Cyber Command Web Interface (Port 3000)
│   ├── src/views/                  # Investigation, EvidenceIntake, ActiveCases, LegalNotice, BankGateway, AuditTrail, ModelCard
│   ├── src/components/             # GraphView (Cytoscape), RiskPanel, ExchangePanel, AgentChat, Sidebar, Header
│   ├── src/services/api.js         # Unified API Service Layer
│   └── package.json                # React 18, Cytoscape, Lucide-React, TailwindCSS
│
├── shared/                         # Locked Cross-Module Schema Definitions
│   └── schemas.py                  # Canonical Pydantic Models for all teams
│
├── docker-compose.yml              # Multi-container 5-service deployment
├── start_all.ps1                   # Single-command local startup script
├── stop_all.ps1                    # Clean port release shutdown script
└── README.md                       # Master Documentation & User Manual
```

---

## ⚖️ Legal & Courtroom Defensibility

1. **Section 91 & 102 CrPC / Section 94 & 107 BNSS Requisition:** Automated drafting of official requisition notices to compliance officers of virtual digital asset exchanges demanding KYC dossiers, bank linkages, IP logs, and immediate freezing directives.
2. **Tamper-Evident Chain of Custody:** Every trace, score, cluster, and notice is hashed into an immutable SHA-256 block linked to the prior block, satisfying the requirements of the Indian Evidence Act.
3. **Courtroom Explainability:** Every risk score features plain-text factor contributions, and every clustering merge cites the specific transaction hash and named forensic heuristic (`deposit_address_reuse`, `common_funding_source`).
