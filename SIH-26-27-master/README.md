# WalletTrace — SIH26183

> **Real-time identification of fraud-linked cryptocurrency exchanges from victim-reported wallet addresses, for Indian law enforcement.**

Smart India Hackathon 2026–27 | Problem Statement SIH26183

---

## Project Structure

```
SIH-26-27/
├── Agentic_Ai/          # LangGraph orchestration + FastAPI agent (port 8000)
│   ├── walletrace/
│   │   ├── graph.py     # LangGraph state machine
│   │   ├── security.py  # Prompt injection defence + grounding
│   │   ├── api.py       # POST /agent/query
│   │   └── tools/
│   │       └── mocks.py # Tool stubs → connects to Blockchain module
│   └── tests/           # 49 tests (all passing)
│
├── Blockchain/          # On-chain analytics module (port 8001)
│   ├── blockchain/
│   │   ├── ingestion.py # Tronscan API (TRX + TRC-20)
│   │   ├── graph.py     # NetworkX BFS graph construction
│   │   ├── clustering.py# Deposit-reuse heuristic
│   │   ├── tracer.py    # Multi-hop fund-flow tracer
│   │   ├── attribution.py# Exchange attribution
│   │   └── api.py       # GET /trace/{address}
│   └── tests/           # 24 tests (all passing)
│
├── dataset.py           # Tronscan data collection script
└── tron_transactions_raw.csv  # 350 labeled Tron transactions (demo dataset)
```

---

## Quick Start

### Blockchain Analytics Module (port 8001)
```bash
cd Blockchain
pip install -r requirements.txt
copy .env.example .env
python main.py              # live Tronscan API
python main.py --csv        # offline CSV mode
```

### Agentic AI Module (port 8000)
```bash
cd Agentic_Ai
pip install -r requirements.txt
copy .env.example .env      # add GOOGLE_API_KEY + BLOCKCHAIN_API_URL=http://localhost:8001
python main.py
```

### Run All Tests
```bash
cd Blockchain  && python -m pytest -v   # 24 passed
cd Agentic_Ai  && python -m pytest -v   # 49 passed
```

---

## Architecture

```
Investigator submits wallet address
        ↓  POST /agent/query  (Agentic AI :8000)
  LangGraph pipeline:
    Intake → Trace → Cluster → RiskScore → Attribute
      → [confidence ≥ 0.75] → DraftNotice → Log → Respond
      → [confidence < 0.75] → ManualReview → Log → Respond
        ↓  GET /trace/{address}  (Blockchain :8001)
  Tronscan API → NetworkX graph → Deposit-reuse clustering
  → Multi-hop tracer → Exchange attribution
        ↓
  Response: exchange name, confidence, draft legal notice
```

---

## Module Ownership

| Module | Owner | Status |
|--------|-------|--------|
| Agentic AI orchestration | Atharva | ✅ Complete |
| Blockchain analytics / tracing | Atharva | ✅ Complete |
| ML risk scoring | Teammate | 🔄 Stub in `mocks.py` |
| Cybersecurity / blacklist | Teammate | 🔄 Stub in `mocks.py` |

---

## Dataset

`tron_transactions_raw.csv` — 350 real Tron/USDT-TRC20 transactions.

| Label | Count | Source |
|-------|-------|--------|
| `fraud` | 100 | ChainAbuse reports + OFAC SDN list + ED India cases |
| `legitimate` | 100 | Binance, Huobi, OKX hot wallets (Tronscan tags) |
| `unknown` | 150 | Intermediate mule wallets from on-chain tracing |

Primary chain: **Tron / USDT-TRC20** (dominant rail for Indian crypto fraud).
Data source: [Tronscan public API](https://apilist.tronscanapi.com).
