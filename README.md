# CryptoSentinel — AI-Powered Crypto Crime Investigation Platform

> **SIH-2026 Problem Statement 26183** | Ministry of Home Affairs · I4C · MHA  
> International Hackathon Edition — v2.0

---

## 🎯 What Problem Do We Solve?

**India's #1 cybercrime vector**: UPI fraud → Crypto conversion → Cross-border laundering.
- ₹11,300+ crore lost to cyber fraud in 2023 (MHA I4C data)
- Average USDT-Tron transaction: 4.2 seconds. Police response: 48 hours.
- **No existing Indian LEA tool** can trace cross-chain crypto flows in real time.

**CryptoSentinel closes this gap** by giving investigators a single command center to:
1. Trace USDT flows across Tron TRC-20 **and** Ethereum ERC-20
2. Detect fraud patterns with graph-based AI (5 detectors, 20+ patterns)
3. Map UPI complaints directly to crypto investigation leads
4. Generate court-admissible tamper-evident evidence chains
5. Screen wallets against live OFAC sanctions + CryptoScamDB

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│          CryptoSentinel Command Center (React Dashboard)        │
│  Investigation · Multi-Chain · Fraud Ring · UPI Bridge          │
│  Threat Intel Feed · Evidence Chain · RBAC Login               │
└──────────┬─────────────┬──────────────┬──────────────┬──────────┘
           │             │              │              │
     :8000/blockchain  :8001/agent  :8002/ml      :8003/cyber
           │             │              │              │
  ┌────────┴──┐  ┌───────┴──┐  ┌───────┴──┐  ┌───────┴──────────┐
  │ Multi-Chain│  │LangGraph │  │Ensemble  │  │ Threat Intel     │
  │ Forensics  │  │Agentic AI│  │ML Engine │  │ Evidence Trail   │
  │            │  │ 10 tools │  │  + GCN   │  │ RBAC · UPI Bridge│
  │  Tron TRC20│  │  + RAG   │  │          │  │ Fraud Detector   │
  │  ETH ERC20 │  │          │  │          │  │ OFAC · ScamDB    │
  └────────────┘  └──────────┘  └──────────┘  └──────────────────┘
```

---

## 🔥 What Makes This International-Hackathon Level

### 1. Real Multi-Chain Blockchain Forensics
- **Tron TRC-20** (primary India fraud corridor) + **Ethereum ERC-20** in one unified trace
- Live Tronscan + Etherscan dynamic tag lookup (real-time entity attribution)
- 6-step pipeline: Ingest → Graph → Cluster → Trace → Attribute → Report

### 2. Advanced Graph-Based Fraud Detection (5 Patterns)
| Pattern | What It Detects | Confidence |
|---------|----------------|------------|
| MixerTumbler | Fan-in/fan-out address laundering | 0.85+ |
| PeelChain | Progressive fund stripping hops | 0.80+ |
| RapidHopping | Sub-5-minute multi-wallet transfers | 0.90+ |
| Structuring | Below-threshold split transactions | 0.75+ |
| ScamClusterProximity | Known-bad address adjacency | 0.95 |

### 3. Live Threat Intelligence (3 Feeds)
- **OFAC SDN List** — US Treasury sanctions (auto-refreshed every 60min)
- **CryptoScamDB** — Community-reported scam addresses
- **Internal I4C Watchlist** — MHA-specific Indian LEA intelligence

### 4. UPI → Crypto Bridge (India-Unique)
Maps raw FIR/NCRP complaint text to:
- Extracted UPI IDs, phone numbers, crypto addresses
- Identified P2P corridor (Binance P2P, WazirX, CoinDCX, Mudrex)
- Auto-generated Section 91 BNSS / PMLA / IT Act legal notice templates

### 5. Court-Ready Evidence Chain
- SQLite hash chain with SHA-256 verification
- Full chain integrity audit in one API call
- JSON export for court submission
- Tamper detection: any modification breaks the chain

### 6. RBAC Policy Engine (5 Roles)
- Viewer / Analyst / Investigator / Admin / System
- 4 data classification levels (Public → Secret)
- PII redaction enforced at the API layer

### 7. LangGraph Agentic AI (10 Tools)
- trace_wallet, batch_trace_wallets, detect_address_chain
- screen_against_sanctions, analyze_upi_complaint
- get_risk_score, check_blacklist, draft_legal_notice
- log_event, get_case_summary
- Real HTTP calls to all backend services — not mocked

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) TronGrid API key, Etherscan API key

### Run All Services

```bash
# Terminal 1 — Blockchain
cd blockchain && pip install -r requirements.txt
python main.py

# Terminal 2 — Cybersecurity
cd Cybersecurity && pip install -r requirements.txt
python main.py

# Terminal 3 — ML
cd ML && pip install -r requirements.txt
python ml/main.py

# Terminal 4 — Agentic AI
cd Agentic_Ai && pip install -r requirements.txt
python walletrace/main.py

# Terminal 5 — Dashboard
cd Dashboard && npm install
npm run dev
```

### Service URLs
| Service | URL | Docs |
|---------|-----|------|
| Blockchain | http://localhost:8000 | /docs |
| Agentic AI | http://localhost:8001 | /docs |
| ML Engine  | http://localhost:8002 | /docs |
| Cybersecurity | http://localhost:8003 | /docs |
| Dashboard  | http://localhost:5173 | — |

---

## 🧪 Tests

```bash
# Cybersecurity (7 tests)
cd Cybersecurity && python -m pytest tests/ -q

# Blockchain (7 tests)
cd blockchain && python -m pytest tests/ -q

# ML (5 tests)
cd ML && python -m pytest tests/ -q

# Agentic AI (6 tests)
cd Agentic_Ai && python -m pytest tests/ -q

# All at once
python -m pytest Cybersecurity/tests/ blockchain/tests/ ML/tests/ Agentic_Ai/tests/ -q
```

---

## 📁 Project Structure

```
sih2026/
├── blockchain/            # Multi-chain forensics (Tron + ETH)
│   ├── ingestion/         # TronClient, EthereumClient, ClientFactory
│   ├── graph/             # NetworkX transaction graph
│   ├── clustering/        # Explainable address clustering
│   ├── tracing/           # Multi-hop peel-chain tracer
│   ├── attribution/       # Exchange matcher (live Tronscan + Etherscan)
│   └── api/               # FastAPI routes (port 8000)
│
├── Cybersecurity/         # Threat intelligence & evidence
│   ├── fraud_detector/    # 5 graph-based fraud patterns
│   ├── evidence_trail/    # SQLite hash-chain evidence vault
│   ├── policy/            # RBAC (5 roles, 4 classifications)
│   ├── threat_intel/      # Live OFAC + CryptoScamDB feeds
│   ├── intake/            # UPI → Crypto bridge
│   ├── rules/             # Legacy rules engine
│   ├── audit/             # Legacy SHA-256 ledger
│   └── api/               # FastAPI routes (port 8003)
│
├── ML/                    # ML risk scoring
│   └── ml/                # Ensemble model + feature engineering
│
├── Agentic_Ai/            # LangGraph investigation agent
│   └── walletrace/
│       ├── graph.py        # State machine
│       ├── tools/          # 10 tool wrappers (real + mock)
│       └── main.py         # FastAPI streaming (port 8001)
│
└── Dashboard/             # React Command Center UI
    └── src/
        ├── views/          # 11 views including 4 new
        ├── components/     # Header, Sidebar, LoginModal
        └── services/       # Unified API service layer
```

---

## 🏆 Key Differentiators vs Other SIH Projects

| Feature | Typical SIH Project | CryptoSentinel |
|---------|---------------------|----------------|
| Chains supported | 1 (Tron) | 2 (Tron + ETH) |
| Fraud patterns | Basic keyword rules | 5 graph-based detectors |
| Threat intel | Static blacklist | 3 live refreshing feeds |
| Evidence | Simple logs | SHA-256 tamper-evident chain |
| Auth | None | RBAC 5 roles + JWT |
| UPI integration | None | Full NLP intake + legal notices |
| Dashboard | Basic | Dark SOC Command Center |
| AI Agent | Mocked tools | 10 real HTTP tool calls |

---

## 👥 Team SIH-26183

Built for **Smart India Hackathon 2026** — Ministry of Home Affairs Problem 26183.  
"AI-Enabled Platform for Tracing and Seizing Virtual Digital Assets Used in Cyber Crimes"

---

*CryptoSentinel is a research and law enforcement tool. All data analysis is for authorized investigative purposes only.*
