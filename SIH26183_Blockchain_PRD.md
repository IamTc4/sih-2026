# Workstream PRD — Blockchain Module
**Parent Project:** WalletTrace (SIH26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics)
**Owner:** Blockchain teammate
**Version:** v1.0 | **Status:** Draft

> One of five workstreams. This owns the **on-chain data + graph + clustering + attribution** core — the actual heart of the PS. Cybersecurity owns the evidence/hash-trail and threat-pattern *risk scoring* (separate doc); AI/ML owns fuzzy/behavioral ML on top of what this module produces; you own the deterministic on-chain forensics layer.

---

## 1. Why This Module Is the Real Differentiator (Research Findings)

Most SIH teams tackling a "blockchain analytics" PS will build a shallow demo: paste an address, call one block-explorer API, show a graph. That's not defensible under judge questioning and isn't how real blockchain forensics works. Research into how actual investigators/forensic platforms (Chainalysis, TRM Labs, open-source GraphSense/BlockSci) operate points to a specific, well-established methodology you can credibly replicate:

- **Address clustering isn't guesswork — it has named heuristics.** On UTXO chains (Bitcoin-style), the **common-input-ownership heuristic** is the industry-standard technique: if multiple addresses are used as inputs to the same transaction, they're almost certainly controlled by one entity, since spending requires all their private keys. This single heuristic routinely collapses what looks like 50 separate actors into 5–8 real clusters.
- **Account-based chains (Ethereum, and Tron — which is what most Indian USDT fraud actually runs on) need different heuristics**: deposit-address reuse, nonce/gas-payment pattern analysis, and contract-interaction timing, rather than the common-input heuristic.
- **Clustering and attribution are two separate, sequential steps.** Clustering groups addresses that behave as one entity; attribution is the separate step of labeling a cluster as "this is a known exchange" using off-chain tagged-address data. Keep these as two distinct modules in your pipeline — it makes your architecture look rigorous, not hand-wavy, when judges ask "how does clustering actually work?"
- **Open-source prior art exists and is citable**: GraphSense (address clustering + entity resolution + transaction graph analysis) and BlockSci (large-scale chain analysis, custom heuristics) are real open-source platforms — referencing them ("we follow the same clustering methodology as GraphSense") gives you instant credibility instead of looking like you invented forensics from scratch.
- **USDT-TRC20 (Tron) is the dominant real-world rail for Indian crypto fraud**, not Bitcoin — pick this as your primary chain for the demo dataset; it's more realistic and more relevant to an MHA problem statement than a generic BTC/ETH toy example.
- **Cross-chain tracing (bridges) is the current frontier** and explicitly hard even for state-of-the-art systems — good to mention as a stretch goal / "future work," not something to promise as a working MVP feature.

**Your unique angle:** most competing teams will present clustering as a black box. You differentiate by making the **heuristic pipeline explainable and chain-aware** — i.e., the system states *which* heuristic fired for each clustering decision ("addresses X and Y merged: common-input-ownership, tx 0xabc..."), which directly serves FR4 in the master PRD (explainability) and is something judges can verify live.

---

## 2. Goals & Non-Goals

### Goals
- **G1:** Ingest real on-chain transaction data for a given victim-reported wallet address (primary chain: Tron/USDT-TRC20; secondary: Ethereum).
- **G2:** Build a transaction graph (nodes = addresses, edges = transfers w/ amount, timestamp, tx hash).
- **G3:** Implement deterministic address-clustering heuristics (common-input-ownership for UTXO-style flows if BTC included; deposit-reuse + behavioral heuristics for Tron/Ethereum) — each clustering decision must record *which heuristic* fired and on which transaction, for explainability.
- **G4:** Implement multi-hop fund-flow tracing (peel-chain aware) up to a configurable hop depth.
- **G5:** Implement exchange attribution — match terminal cluster addresses against a labeled address dataset and output the exchange name + deposit address + confidence.
- **G6:** Expose all of the above as a clean internal API/data contract for the AI/ML, Cybersecurity, Agent, and Dashboard teams to consume.

### Non-Goals
- **NG1:** Not building the risk-scoring/fraud-pattern ML model (that's AI/ML's + Cybersecurity's job — you supply the raw graph/cluster data they score).
- **NG2:** Not building the hash-anchored evidence trail (Cybersecurity owns Stage 4 — you just call their logging endpoint after each trace).
- **NG3:** Not attempting full cross-chain bridge tracing in the MVP — flag it explicitly as future work when asked.
- **NG4:** Not building a full custom blockchain indexer — use existing public APIs/open datasets; your novelty is the heuristic + attribution pipeline on top, not raw indexing infrastructure.

---

## 3. Deliverables (What You Personally Build)

### 3.1 On-Chain Data Ingestion
- Pull transaction history for an input address via public chain APIs (Tronscan API for Tron/USDT-TRC20 as primary; Etherscan-equivalent for Ethereum as secondary).
- Normalize into a common schema regardless of chain: `{tx_hash, from, to, amount, token, timestamp, chain}`.

### 3.2 Transaction Graph Construction
- Build a directed graph (NetworkX or similar) from normalized transactions.
- Support incremental expansion (BFS-style hop-by-hop traversal from the seed address) rather than pulling the whole chain — keeps it demo-fast.

### 3.3 Clustering Engine (the credibility centerpiece)
- Implement heuristics appropriate to each supported chain (see Section 1 research).
- Each merge decision is logged with: `{addr_a, addr_b, heuristic_name, evidence_tx}` — this record is what feeds explainability in the dashboard and what Cybersecurity hashes into the evidence trail.
- Output: cluster objects — sets of addresses with a cluster ID and the heuristic evidence chain that formed them.

### 3.4 Multi-Hop Fund-Flow Tracer
- Given a seed address, traverse outward following largest/most-relevant fund flows (peel-chain aware: distinguish "bulk of funds moving forward" from "small peeled-off change").
- Configurable max hop depth (cap for live-demo performance; document that production would go deeper).

### 3.5 Exchange Attribution
- Maintain/import a labeled-address dataset (publicly available tagged exchange deposit addresses — document your source clearly, this is a judge-question magnet).
- Match terminal cluster addresses against this dataset; output `{exchange_name, deposit_address, confidence}`.
- Where no match is found, clearly state "unattributed — recommend manual investigation" rather than forcing a guess (honesty here builds more trust with judges than overclaiming, same lesson as the master PRD's Stage 5 framing).

---

## 4. Functional Requirements (This Module Only)

| ID | Requirement | Priority |
|---|---|---|
| BC-FR1 | Module shall ingest on-chain transaction data for a given seed address on the primary chain. | Must |
| BC-FR2 | Module shall construct a transaction graph incrementally via hop-by-hop traversal. | Must |
| BC-FR3 | Module shall cluster addresses using chain-appropriate deterministic heuristics, logging the heuristic + evidence per merge. | Must |
| BC-FR4 | Module shall trace multi-hop fund flow distinguishing bulk-forward movement from peeled change. | Must |
| BC-FR5 | Module shall attribute terminal clusters to known exchanges with a confidence score, or explicitly report "unattributed." | Must |
| BC-FR6 | Module shall expose all outputs (graph, clusters, trace paths, attribution) via a documented internal API. | Must |
| BC-FR7 | Module shall support a second chain (Ethereum) as a stretch goal to demonstrate generality. | Could |

---

## 5. Tech Stack

| Layer | Tools |
|---|---|
| Chain data source | Tronscan API (primary — USDT-TRC20), Etherscan API (secondary/stretch) |
| Graph | Python + NetworkX |
| Clustering heuristics | Custom Python rules engine (reference GraphSense's public methodology as prior art) |
| Labeled-address data | Public tagged-address datasets (block-explorer-published exchange tags) — document exact source(s) used |
| API layer | FastAPI (internal service, consumed by other workstreams) |

---

## 6. Integration Interfaces (What You Hand Off)

| To | You Provide | Format |
|---|---|---|
| AI/ML owner | Raw graph + cluster objects + heuristic metadata, for them to layer behavioral/ML risk scoring on top | JSON: `{clusters: [{cluster_id, addresses, heuristic_evidence}], graph_edges: [...]}` |
| Cybersecurity owner | Every trace/cluster/attribution event, for hashing into the evidence trail | Call their `POST /log-event` with your event payload |
| Agentic/LangGraph owner | Callable functions: `trace_wallet(address)`, `get_cluster(address)`, `identify_exchange(address)` | Function/API contract the agent's tools wrap |
| Dashboard owner | Graph + cluster + attribution data for visualization | `GET /trace/{address}` returning full result object |

**Coordinate early** with AI/ML and Cybersecurity on the exact JSON field names for cluster/trace objects — this is the #1 place hackathon teams lose integration time on day 2 (same warning as the Cybersecurity doc).

---

## 7. Demo Script (Your Segment)

1. Seed wallet address entered.
2. Live: graph expands hop by hop as data is pulled.
3. Clustering fires visibly — UI (built by Dashboard team, fed by you) highlights "these 3 addresses merged: common deposit-reuse pattern, evidence tx [hash]."
4. Trace continues to terminal address.
5. Attribution result: "Exchange X, deposit address Y, 87% confidence" — or honest "unattributed, flagged for manual review."

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Public API rate limits during live demo | Pre-cache a few known-good demo wallets; have a rehearsed fallback |
| Labeled exchange-address dataset is incomplete | Use multiple public sources; be upfront about confidence being probabilistic, not certain |
| Judges ask "why not just use Chainalysis/TRM?" | Answer prepared: those are expensive, proprietary, foreign platforms not built for NCRP-scale Indian intake — your system is open, explainable, and India-specific |
| Tron API differs enough from Ethereum to slow stretch goal | Treat Ethereum support as explicitly optional; don't let it block the primary Tron path |

---

## 9. Open Items Before Build Starts

- Confirm final labeled-address dataset source(s) for exchange attribution.
- Confirm hop-depth cap for live demo performance.
- Sync field-name contracts with AI/ML, Cybersecurity, and Dashboard owners (see Section 6).
- Decide whether Ethereum stretch goal is worth the time given team size/timeline.

---

*Workstream-level document. Combine with the AI/ML, Agentic, Cybersecurity, and Dashboard PRDs before finalizing the master architecture.*
