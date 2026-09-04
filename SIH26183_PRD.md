# Product Requirements Document (PRD)

**Project Codename:** WalletTrace (placeholder — rename before submission)
**SIH 2026 — Problem Statement SIH26183**
**Title:** Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics
**Ministry:** Ministry of Home Affairs (MHA)
**Theme:** Blockchain & Cybersecurity | **Category:** Software
**Version:** v1.0 | **Status:** Draft — for team & mentor review

> ⚠️ Verify exact wording, background, dataset links, and evaluation criteria on sih.gov.in before final submission.

---

## 1. Executive Summary

When a victim reports a crypto-fraud complaint (via NCRP/1930), investigators today get a single wallet address and little else. Tracing where those funds went — which exchange they were cashed out at, which other wallets are linked to the same fraud ring — is manual, slow, and requires deep on-chain forensics expertise most cybercrime cells don't have in-house.

**WalletTrace** is an AI-augmented blockchain analytics platform that:

1. Ingests victim-reported suspect wallet addresses from complaint intake.
2. Automatically traces on-chain fund flows (multi-hop) across wallets and clusters addresses likely controlled by the same actor, using graph algorithms + ML.
3. Identifies the **exchange(s)** the funds were ultimately deposited to (the actionable choke point — exchanges are KYC-regulated entities that can freeze funds/reveal identity).
4. Uses an **LLM agent (LangChain/LangGraph)** to auto-draft the legal request package (freeze request / information request) to the identified exchange, and to answer investigator questions in natural language over the traced graph ("who else received funds from this wallet?").
5. Anchors every trace and generated document to a tamper-evident hash log for evidentiary integrity.
6. Ships an optional IoT/mobile capture module for field units to submit wallet evidence (screenshots, QR codes) directly into the pipeline.

This turns a manual, expert-dependent forensics task into a same-day, explainable, investigator-facing workflow — while giving your team a legitimate reason to showcase **agentic AI (LangChain/LangGraph), ML clustering, blockchain analytics, and cybersecurity** together, even though the PS is filed under "Software."

---

## 2. Problem Statement (Official, as indexed)

Development of a system for **real-time identification of fraud-linked cryptocurrency exchanges from victim-reported suspect wallet addresses through automated blockchain analytics.**

**Core pain points:**
- Investigators receive a wallet address with no tooling to trace it beyond public block explorers (manual, slow, no case linkage).
- No automated way to cluster wallets belonging to the same fraud ring (mixers, hop-chains, peel chains).
- No fast, standardized way to identify *which exchange* received the funds — the only point where legal action (freeze/KYC disclosure) is actually possible.
- No investigator-friendly interface — current tools (Chainalysis, TRM Labs) are expensive, foreign, and not built for NCRP-scale Indian case intake.

---

## 3. Goals & Non-Goals

### Goals
- **G1:** Given a suspect wallet address, trace multi-hop fund flow and output the exchange(s) funds terminated at, with confidence scores.
- **G2:** Cluster wallets likely controlled by the same entity (co-spend heuristics, timing, behavioral patterns) using ML/graph models.
- **G3:** Provide a conversational agent (LangGraph) that lets an investigator query the trace in plain language and auto-generates a draft legal request to the exchange.
- **G4:** Maintain a tamper-evident, hash-anchored log of every trace/action for court admissibility.
- **G5:** Provide a real-time investigator dashboard visualizing the fund-flow graph.

### Non-Goals (explicit, for defensibility)
- **NG1:** No live integration with real exchange KYC databases — simulated/synthetic exchange address-attribution dataset for demo.
- **NG2:** No automated fund freezing — system generates intelligence + draft legal requests only; human-in-the-loop.
- **NG3:** Not building a new blockchain indexer from scratch — use existing public chain data (via APIs) and open on-chain heuristics; team's novelty is the clustering + agentic layer, not raw indexing.
- **NG4:** Not attempting cross-chain bridge tracing in the MVP (stretch goal only) — start with a single chain (e.g., Ethereum or a stablecoin/USDT-on-Tron corridor, which is the dominant real-world fraud rail in India).

---

## 4. Why This Lets You Use Your Full Team Skillset

| Skill | Where it fits |
|---|---|
| **Agentic AI / LangChain / LangGraph** | Investigator-facing conversational agent that orchestrates: wallet lookup → graph query → exchange identification → draft legal notice generation. This is the centerpiece differentiator vs. static dashboards. |
| **ML model + training** | Wallet clustering model (co-spend/heuristic + embedding-based similarity) and an anomaly/risk-scoring model for "likelihood this address is exchange-controlled." |
| **Blockchain** | Core domain — on-chain data ingestion, address clustering, hash-anchoring of evidence trail. |
| **Cybersecurity** | Threat-actor pattern library (mixer detection, peel-chain detection, known scam-cluster signatures), secure handling of victim/complaint PII. |
| **IoT (optional/stretch)** | Field-evidence capture app/device for cyber cells to submit wallet screenshots/QR at point of complaint intake, feeding OCR → pipeline. Keep this as a bonus module, not core path — don't let it dilute the core PS. |

---

## 5. System Architecture

```
┌─────────────────────┐   ┌───────────────────────────┐   ┌──────────────────────┐
│ Stage 1: Intake &    │   │ Stage 2: Blockchain Graph  │   │ Stage 3: Agentic      │
│ Wallet Ingestion     │──▶│ Analytics Engine (ML)      │──▶│ Investigation Layer   │
│ (complaint + wallet) │   │                            │   │ (LangGraph agent)     │
└─────────────────────┘   └───────────────────────────┘   └──────────────────────┘
        │                          │                                │
        ▼                          ▼                                ▼
  OCR/manual entry,          On-chain data fetch,             Natural-language Q&A,
  case metadata,             multi-hop trace,                 auto-draft legal notice,
  wallet validation          co-spend clustering,              exchange identification
                              exchange-tag matching             summary
                                     │
                                     ▼
                       ┌───────────────────────────┐
                       │ Stage 4: Evidence Trail    │
                       │ (hash-anchored audit log)  │
                       └───────────────────────────┘
                                     │
                                     ▼
                       ┌───────────────────────────┐
                       │ Stage 5: Investigator      │
                       │ Dashboard (Web)            │
                       │ Graph viz, case mgmt,      │
                       │ agent chat panel           │
                       └───────────────────────────┘
```

### 5.1 Stage 1 — Intake & Wallet Ingestion
- Manual/CSV entry of victim-reported wallet address + case metadata (replicates NCRP complaint fields).
- Address validation (chain detection: BTC/ETH/TRC-20 etc.), sanity checks.
- Optional: image/QR upload with OCR extraction for field-submitted evidence.

### 5.2 Stage 2 — Blockchain Graph Analytics Engine (core ML/blockchain work)
- Pull on-chain transaction data via public APIs (Etherscan/Blockchair/Tronscan-equivalent, or a public dataset for demo reliability).
- Build a transaction graph: nodes = addresses, edges = transfers (amount, timestamp).
- **Multi-hop tracing:** follow funds through peel chains / hops up to N degrees.
- **Clustering model:** co-spend heuristic (common-input-ownership) + ML similarity model (behavioral features: transaction timing, amount patterns, gas/fee patterns) to group addresses likely controlled by one actor.
- **Exchange attribution:** match terminal addresses against a labeled address dataset (known exchange hot/deposit wallets — public labeled datasets exist, e.g. from block explorers' tagged addresses) → output "funds terminated at Exchange X, deposit address Y, confidence Z%."
- Risk/anomaly scoring per address (mixer usage, rapid hopping, known scam-cluster proximity).

### 5.3 Stage 3 — Agentic Investigation Layer (LangChain/LangGraph — your differentiator)
- LangGraph-orchestrated agent with tools:
  - `trace_wallet(address)` → calls Stage 2 engine
  - `get_cluster(address)` → returns linked addresses
  - `identify_exchange(address)` → returns exchange + confidence
  - `draft_legal_notice(case_id, exchange)` → LLM-generated draft request letter (freeze/KYC-disclosure format) using case facts, ready for investigator review/edit — **never auto-sent**
- Investigator chat interface: "Trace this wallet and tell me where the money ended up," "Show me all wallets linked to this scam cluster," "Draft the notice to the exchange."
- Explainability: every agent answer cites the underlying trace/cluster data it used.

### 5.4 Stage 4 — Evidence Trail (Blockchain/Cybersecurity team)
- Every trace, cluster result, and generated document is hashed and appended to an immutable/tamper-evident log (permissioned ledger or hash-anchoring), giving chain-of-custody for prosecution — mirrors your DevCrypt approach from the other PRD.

### 5.5 Stage 5 — Investigator Dashboard (Web)
- Interactive fund-flow graph visualization (nodes/edges, zoom into clusters).
- Case management: open/assign/close cases.
- Embedded agent chat panel (Stage 3).
- Exchange-identification summary card with confidence + evidence links.

---

## 6. Platform Decision

**Web dashboard + backend + agent service. No standalone mobile app for MVP** (same reasoning as before: judges see a projected web demo; API layer designed to be mobile-ready but not built out). IoT capture module, if included, is a thin evidence-submission client feeding the same backend API — keep it minimal.

---

## 7. Team & Workstream Mapping

| Team | Ownership | Key Deliverables |
|---|---|---|
| AI/ML | Clustering model, exchange-attribution matching, risk scoring | Trained model, evaluation metrics |
| Agentic/LangChain-LangGraph dev | Stage 3 agent, tool orchestration, notice-drafting prompts | Working agent with tool-calling, chat UI backend |
| Blockchain | On-chain data ingestion, graph construction, hash-anchoring evidence trail | Data pipeline, evidence trail service |
| Cybersecurity | Threat-pattern library (mixers/peel chains), PII handling, security review of pipeline | Domain rules feeding clustering features, security audit doc |
| Software Dev | Dashboard (frontend + backend API), case management | Web app |
| IoT (optional) | Field evidence capture client (mobile/web + OCR) | Capture app feeding Stage 1 |

---

## 8. Data Strategy (Address Proactively)

- Real exchange KYC data is not available — use **public labeled-address datasets** (many block explorers and open-source projects publish tagged exchange deposit addresses) for exchange attribution in the demo.
- Use **real public blockchain data** (mainnet, via public APIs) for the transaction graph — this is genuinely real data, a strong differentiator vs. teams using fully synthetic chains.
- Synthetic **victim complaint metadata** calibrated to plausible NCRP-style fields (since real complaint data won't be available).
- Document all data sources and labeling methodology transparently — judges will ask.

---

## 9. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR1 | System shall accept a victim-reported wallet address and validate/detect chain type. | Must |
| FR2 | System shall trace multi-hop fund flow from the input address. | Must |
| FR3 | System shall cluster addresses likely controlled by the same actor with a confidence score. | Must |
| FR4 | System shall identify terminal exchange(s) receiving traced funds, with confidence and evidence. | Must |
| FR5 | System shall provide a conversational agent (LangGraph) for natural-language investigation queries. | Must |
| FR6 | Agent shall generate a draft legal notice to the identified exchange (human review required before use). | Should |
| FR7 | System shall log every trace/cluster/notice action to a tamper-evident audit trail. | Should |
| FR8 | Dashboard shall visualize the fund-flow graph interactively. | Must |
| FR9 | Dashboard shall support case management (assign, track, close). | Should |
| FR10 | System shall expose a documented API for the ingestion/trace/agent functions. | Could |

---

## 10. Tech Stack (Proposed)

| Layer | Tools |
|---|---|
| On-chain data | Public chain APIs (Etherscan/Blockchair/Tron equivalents), public labeled-address datasets |
| Graph/ML | Python, NetworkX / PyTorch Geometric, scikit-learn for clustering + risk scoring |
| Agentic layer | LangChain, LangGraph, an LLM (Claude/Gemini/OpenAI via API) with tool-calling |
| Backend API | FastAPI / Node.js |
| Frontend | React/Next.js, graph visualization (e.g., Cytoscape.js / D3), chat UI |
| Evidence trail | Hash-anchoring service, permissioned ledger or public-chain anchoring |
| IoT (optional) | Lightweight mobile/web capture client + OCR (e.g., Tesseract) |

---

## 11. Live Demo Script

1. Investigator pastes a suspect wallet address into the dashboard.
2. System traces multi-hop flow live — graph animates as hops resolve.
3. Cluster of related addresses highlights; risk score displayed.
4. System flags: "Funds terminated at Exchange X, deposit address Y — 87% confidence."
5. Investigator opens agent chat: "Draft a freeze request to Exchange X for this case." Agent generates draft notice citing the trace evidence.
6. Evidence panel shows the hash-anchored log entry for the full trace + generated document.

**One-line pitch:** "We don't just show a wallet address — we trace where the money actually went, tell you which exchange to contact, and draft the legal request for you, with every step evidentially anchored."

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Exchange-attribution dataset incomplete/inaccurate | Use multiple public tagging sources; clearly caveat confidence scores; document methodology |
| Multi-hop tracing across many hops is compute-heavy for a live demo | Cap hop depth for live demo; precompute/cache a few strong demo wallets as fallback |
| Agent hallucinates trace details in notice drafts | Ground every agent output strictly in tool-returned data (RAG-style grounding); show citations in UI |
| Judges see IoT/mobile as scope creep on a "software" PS | Keep IoT module clearly labeled as optional/bonus, not core to FR1–FR9 |
| Live demo failure | Recorded fallback video; rehearse |

---

## 13. Open Items Before Submission

- Confirm exact official PS wording/dataset links on sih.gov.in.
- Decide primary chain for MVP (recommend a stablecoin corridor most relevant to Indian crypto fraud, e.g. USDT-TRC20, plus ETH as secondary).
- Confirm which public labeled-address dataset to use for exchange attribution.
- Confirm LLM provider/API budget for the agentic layer.
- Assign internal milestones once team availability is confirmed.

---

*Prepared for internal team/mentor review — not an official SIH submission document.*
