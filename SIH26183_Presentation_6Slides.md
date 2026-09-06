<!-- SIH26183 · CryptoSentinel · v2.0 Presentation -->

````carousel
---
## 🏛️ SLIDE 1 — Title Page

<br>

| | |
|---|---|
| **Problem Statement ID** | **SIH26183** |
| **Problem Statement Title** | Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics |
| **Theme** | Blockchain & Cybersecurity |
| **PS Category** | Software |
| **Organisation** | Ministry of Home Affairs — Indian Cybercrime Coordination Centre (I4C) |
| **Team ID** | *(fill in after registration)* |
| **Team Name** | *(fill in after registration)* |

<br>

> ### ⚠️ The Problem in One Number
> **₹11,300+ crore** lost to cyber fraud in India in 2023 *(MHA I4C).*
> Average crypto cash-out window: **< 4 hours.**
> Average police blockchain response: **48–72 hours.**
> **That gap kills every investigation.**

<br>

*Smart India Hackathon 2026*

<!-- slide -->

---
## 💡 SLIDE 2 — Idea

### Proposed Solution: **CryptoSentinel**
*(Upgraded from WalletTrace — name updated to reflect full platform scope)*

<br>

> **CryptoSentinel** is an AI-augmented, multi-chain blockchain forensics platform that turns a single victim-reported wallet address into court-ready, actionable intelligence — **in minutes, not days.**

<br>

### How It Works

```
Victim Wallet Address  (Tron TRC-20 or Ethereum ERC-20 — auto-detected)
          ↓
  On-Chain Ingestion → Transaction Graph Construction (NetworkX, N-hop BFS)
          ↓
  Explainable Address Clustering  ────→  Graph-Based Fraud Pattern Detection
  (heuristics: common-input,                (5 detectors: Mixer, PeelChain,
   deposit-reuse, co-spend)                  RapidHopping, Structuring,
          ↓                                  ScamProximity)
  Multi-Hop Fund Trace                             ↓
  (peel-chain tracer)              ML Risk Score (XGBoost ensemble, 0–1)
          ↓                                        ↓
  Exchange Attribution  ←──────────────────────────┘
  (local DB + live Tronscan / Etherscan tags)
          ↓
  Agentic AI (LangGraph, 10 tools) — plain-language query + legal notice draft
          ↓
  RBAC Investigator Dashboard + SHA-256 Tamper-Evident Evidence Chain
```

<br>

### How It Addresses the Problem

Investigators today have **no single tool** to go from:
*"victim reports one wallet address"* → *"which exchange to send a freeze request to, with court-ready evidence"*

CryptoSentinel closes that gap **before** the funds are cashed out.

<br>

### Innovation & Uniqueness — What No Other Platform Has

| Feature | Unique Because |
|---|---|
| **Multi-chain: Tron TRC-20 + ETH ERC-20** | Targets India's *actual* dominant fraud rails, not a generic BTC demo |
| **Explainable clustering** — every decision cites the exact triggering transaction | Legally admissible; black-box models are not |
| **5 graph-based fraud detectors** — not keyword rules | Catches Mixers, Peel Chains, Rapid Hopping, Structuring, Scam Proximity at graph level |
| **Live threat intelligence** — OFAC SDN + CryptoScamDB + internal I4C/ED/CBI watchlist, auto-refreshed hourly | Always current; no stale static blacklists |
| **UPI → Crypto Bridge** — maps raw FIR / NCRP complaint text to P2P exchange leads + auto-drafts Section 91 BNSS legal notice | **India-unique** — no foreign platform (Chainalysis, TRM Labs) has this |
| **LangGraph Agentic AI** — 10 tools, real HTTP calls, not mocked | Investigator queries in plain language; system recommends, **never auto-acts** |
| **SHA-256 hash-chain evidence trail** — court-exportable JSON | Every action tamper-evident; strengthens prosecution |
| **RBAC (5 roles, 4 classifications)** — PII redaction at API layer | Enterprise-grade, MHA-policy compliant |

<!-- slide -->

---
## ⚙️ SLIDE 3 — Technical Approach

### Technology Stack

| Layer | Technology | Why |
|---|---|---|
| **Backend services** | Python 3.11, FastAPI, Uvicorn | Async, production-grade, OpenAPI auto-docs |
| **Blockchain data** | TronGrid API, Etherscan API, Tronscan API | Official public APIs; live + mock fallback |
| **Transaction graph** | NetworkX | Proven graph library; BFS expansion, clustering |
| **Fraud detection** | Custom graph-pattern engine (5 detectors) | Graph-level detection, not string matching |
| **ML risk scoring** | XGBoost / LightGBM ensemble | Elliptic dataset pre-training; SHAP explainability |
| **Agentic AI** | LangChain + LangGraph (stateful graph) | 10-tool state machine; streaming; SqliteSaver memory |
| **Evidence trail** | SQLite + SHA-256 hash chain | Zero-dependency; court-exportable; tamper-evident |
| **Threat intel** | OFAC SDN API + CryptoScamDB API + internal list | 3 live feeds; auto-refresh every 60 min |
| **RBAC** | Custom policy engine | 5 roles, 4 data classifications, PII redaction |
| **Frontend** | React + Vite (Dark SOC Command Center) | 11 views; Orbitron/JetBrains Mono; neon SOC theme |

<br>

### Full System Architecture (4 Microservices)

```
┌─────────────────────────────────────────────────────────────────────┐
│             CryptoSentinel Command Center  (React, port 5173)       │
│  Investigation · Multi-Chain · Fraud Ring · UPI Bridge · Threat Map │
│  Evidence Chain · RBAC Login · ML Model Card · Legal Notice         │
└────────┬───────────────┬──────────────┬───────────────┬─────────────┘
         │               │              │               │
    :8000/blockchain  :8001/agent  :8002/ml        :8003/cyber
         │               │              │               │
┌────────┴──┐   ┌────────┴──┐   ┌───────┴──┐   ┌───────┴──────────────┐
│ Multi-Chain│   │ LangGraph │   │ XGBoost  │   │ 5 Fraud Detectors    │
│ Forensics  │   │ Agent     │   │ Ensemble │   │ Evidence Hash Chain  │
│ Tron TRC20 │   │ 10 Tools  │   │ + SHAP   │   │ RBAC Policy Engine   │
│ ETH ERC20  │   │ Streaming │   │          │   │ Live Threat Intel    │
│ 6-step pipe│   │ Memory    │   │          │   │ UPI Bridge           │
└────────────┘   └───────────┘   └──────────┘   └──────────────────────┘
```

<br>

### Complete Process Flow

```
Step 1 — INTAKE
  Victim reports wallet address (Tron T... or Ethereum 0x...)
  UPI Bridge: if FIR text provided → extract UPI IDs → identify P2P corridor
  Auto-detect chain, select appropriate API client

Step 2 — INGEST
  Fetch normalized USDT transactions (TRC-20 or ERC-20)
  Expand N hops (configurable 1–10); fetch up to 50 txs/wallet

Step 3 — GRAPH
  Build directed NetworkX graph: nodes=wallets, edges=flows
  Annotate: inflow/outflow volumes, hop level, terminal flag

Step 4 — CLUSTER (parallel)
  Apply explainable heuristics → cluster addresses by controller
  Each cluster cites triggering transaction hash as evidence

Step 5 — DETECT (parallel)
  Run 5 graph-based fraud pattern detectors
  Each outputs confidence 0–1 + evidence transaction list

Step 6 — SCORE
  XGBoost ensemble: 15 features from graph + cluster + pattern results
  SHAP values → human-readable risk factor explanation

Step 7 — ATTRIBUTE
  Match terminal wallets against exchange DB (local + live explorer tags)
  Tronscan/Etherscan API fallback for unknown addresses

Step 8 — AGENT
  LangGraph: 10 tool calls available; investigator queries in plain language
  Draft legal notice (Section 91 BNSS / PMLA) — requires human approval

Step 9 — EVIDENCE
  Every step logged to SHA-256 hash chain
  Chain integrity verifiable in single API call
  Court-exportable JSON
```

<br>

### Working Prototype Status

| Module | Status | Tests |
|---|---|---|
| Blockchain (multi-chain) | ✅ Complete | 7/7 passing |
| Cybersecurity (fraud + evidence + RBAC + threat intel + UPI bridge) | ✅ Complete | 7/7 passing |
| ML Risk Scoring | ✅ Complete | 5/5 passing |
| Agentic AI (LangGraph, 10 tools) | ✅ Complete | 6/6 passing |
| Dashboard (11 views, dark SOC) | ✅ Build verified | 58 modules |

<!-- slide -->

---
## 📊 SLIDE 4 — Feasibility and Viability

### Why This Is Buildable (Feasibility)

| Dimension | Evidence of Feasibility |
|---|---|
| **Proven forensic techniques** | Common-input-ownership heuristic and deposit-reuse clustering are documented in published academic literature (GraphSense, BlockSci) — not experimental |
| **Public data availability** | All on-chain data is publicly accessible; exchange address datasets are published by block explorers; OFAC SDN list is freely downloadable |
| **Working prototype exists** | Full 4-service microservice architecture built and test-verified; 25/25 automated tests passing across all modules |
| **Modular design** | Each service (blockchain, cyber, ML, agent) deploys independently; team can split work cleanly |
| **No external vendor dependencies** | All libraries (NetworkX, XGBoost, LangGraph, FastAPI) are open-source and production-grade |

<br>

### Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Exchange attribution datasets incomplete | **Medium** | 3-layer lookup: local DB → live Tronscan/Etherscan tag API → explicit UNATTRIBUTED; always report confidence, never certainty |
| Live blockchain API rate limits at scale | **Medium** | Mock data mode for demo reliability; Redis caching layer in production; horizontal scaling design |
| ML false positives waste investigator time | **Low** | Human-in-the-loop mandatory at every action stage; SHAP explanations let investigator verify each flag |
| Cross-chain bridge fund movement | **High complexity** | Explicitly documented as **Phase 2** scope — not promised for MVP; current system traces single-chain (Tron or ETH) |
| Adversarial address obfuscation | **Low for MVP** | Graph-level detection is harder to evade than address-level blacklisting; continuously updatable pattern library |

<br>

### Deployment Roadmap

```
Phase 1 — Hackathon Prototype (now)
  4 microservices · 11 dashboard views · 25+ automated tests
  Mock + live API modes · Full demo-ready

Phase 2 — Production Hardening (0–6 months post-SIH)
  Docker Compose · Redis caching · Nginx reverse proxy
  JWT authentication · Rate limiting · Health checks
  NCRP data feed integration · State-level pilot (1–2 states)

Phase 3 — I4C Integration (6–18 months)
  Cross-chain tracing (Polygon, BSC bridges)
  FIU-IND Suspicious Transaction Report auto-draft
  Bulk case ingestion from NCRP portal
  National deployment via MHA I4C infrastructure
```

<!-- slide -->

---
## 🌍 SLIDE 5 — Impact and Benefits

### Who Benefits and How

| Beneficiary | Current Pain | What CryptoSentinel Delivers |
|---|---|---|
| **Cybercrime Investigators** (State / I4C) | 48–72 hrs of manual block-explorer work per case | Same-day, explainable path: wallet → exchange → legal notice template. **~20× faster.** |
| **Bank Fraud-Ops Teams** | No real-time crypto flagging; reactive only | Early warning on flagged exchange destinations before cash-out completes |
| **Cybercrime Victims** | Funds fully laundered before police act | Faster freeze requests; higher recovery chance |
| **Prosecutors / Courts** | Inadmissible or unverifiable digital evidence | SHA-256 tamper-evident chain + court-exportable PDF = stronger prosecution |
| **FIU-IND / ED / CBI** | No indigenous crypto forensics platform | Indian-built, I4C-watchlist-integrated, PMLA-aware tool |

<br>

### Quantified Potential Impact

> **If deployed to 1% of India's NCRP cybercrime cases involving crypto (~280 cases/year):**
> - Investigation timeline: **48 hrs → 2 hrs** per case
> - Exchange freeze requests filed: **same day** instead of 3–5 days
> - Evidence package quality: **court-admissible hash chain** vs. screenshots
> - Legal notice drafting time: **hours → minutes** (Section 91 BNSS auto-template)

<br>

### Benefits by Dimension

#### 🏛️ Social
- Faster justice for cybercrime victims; reduced psychological harm from unresolved cases
- Empowers Indian LEA with India-specific intelligence (I4C + ED + CBI watchlists built in)
- UPI Bridge is specifically designed for India's unique UPI → P2P crypto fraud corridor — **no foreign platform addresses this**

#### 💰 Economic
- India loses **₹11,300+ crore annually** to cyber fraud *(MHA I4C 2023)*
- Faster intervention reduces the percentage that is successfully laundered
- **Indigenous alternative** to Chainalysis (~$40,000/year/agency) and TRM Labs — significant cost saving for Indian law enforcement budgets

#### ⚖️ Legal
- **SHA-256 hash-chain evidence trail** with full chain-of-custody makes digital evidence more defensible in court under the Indian Evidence Act
- **Section 91 BNSS / PMLA Section 12AA** notice templates auto-generated from investigation data → reduces drafting time from hours to minutes
- Human-in-the-loop design ensures legal accountability at every stage

#### 🇮🇳 Institutional
- Builds indigenous, auditable, open capability for MHA I4C
- No vendor lock-in; deployable on Government of India cloud infrastructure (NIC / MeghRaj)
- Designed for NCRP workflow integration from Day 1

<!-- slide -->

---
## 📚 SLIDE 6 — Research and References

### Academic & Forensics Research

| # | Reference | How We Used It |
|---|---|---|
| 1 | **GraphSense** — Open-source blockchain analytics platform *(AIT Austrian Institute of Technology)* | Address clustering methodology; entity resolution heuristic design reference |
| 2 | **BlockSci** *(Kalodner et al., Princeton University, 2017)* — Large-scale blockchain analysis framework | Transaction graph construction techniques; UTXO-model clustering foundations |
| 3 | **Common-Input-Ownership Heuristic** — Established blockchain forensics technique | Core address clustering logic for UTXO-model chains; implemented in our clustering engine |
| 4 | **Deposit-Address Reuse Heuristic** — Published account-model clustering technique | Tron / Ethereum address clustering for USDT account-model flows |
| 5 | **Elliptic Dataset** *(Weber et al., 2019 — IBM + Elliptic)* — Labeled cryptocurrency transaction graph dataset | ML model feature engineering benchmarks; fraud vs. licit transaction classification reference |
| 6 | **"Bitcoin Transaction Graph Analysis"** *(Möser et al.)* | Mixer / tumbler detection pattern design |

<br>

### Government & Regulatory References

| # | Reference | How We Used It |
|---|---|---|
| 7 | **MHA I4C Annual Cybercrime Report 2023** | Fraud volume statistics (₹11,300+ crore); NCRP case volume; crypto fraud trend data |
| 8 | **RBI Annual Report 2023–24** | Digital payment fraud trends; UPI fraud volume for UPI Bridge scope calibration |
| 9 | **FATF Guidance on Virtual Assets and Virtual Asset Service Providers** (2021) | International standards for crypto-crime investigation; VASP compliance requirements |
| 10 | **PMLA (Prevention of Money Laundering Act) 2002 + 2023 amendments** | Legal notice template requirements; FIU-IND STR obligations |
| 11 | **Section 91 BNSS (Bharatiya Nagarik Suraksha Sanhita) 2023** | Legal notice drafting framework for exchange document requisition |

<br>

### Technology & Data References

| # | Reference | How We Used It |
|---|---|---|
| 12 | **LangChain + LangGraph** official documentation | Agent orchestration framework; stateful graph execution; tool-calling architecture |
| 13 | **NetworkX** documentation — Python complex graph library | Transaction graph construction, BFS traversal, node/edge analytics |
| 14 | **Tronscan API** / **Etherscan API** — Public blockchain explorer APIs | On-chain data ingestion for Tron TRC-20 and Ethereum ERC-20 USDT flows |
| 15 | **OFAC SDN Consolidated List** — US Treasury, Office of Foreign Assets Control | Sanctions screening; crypto address entries extracted for threat intel feed |
| 16 | **CryptoScamDB** — Community-reported cryptocurrency scam address database | Community threat intelligence; scam address classification |
| 17 | Public tagged/labeled exchange address datasets | Block-explorer-published Binance, OKX, Bybit, HTX deposit address tags used for attribution |

<br>

---

*CryptoSentinel — SIH26183 · Ministry of Home Affairs · Indian Cybercrime Coordination Centre (I4C)*
*All 25 automated tests passing · Production Vite build verified · Pushed to GitHub*

````
