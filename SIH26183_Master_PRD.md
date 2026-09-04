# Product Requirements Document (PRD) — Master
**Project Codename:** WalletTrace (placeholder — rename before submission)
**SIH 2026 — Problem Statement SIH26183**
**Title:** Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics
**Ministry:** Ministry of Home Affairs (MHA) | **Theme:** Blockchain & Cybersecurity | **Category:** Software
**Version:** v2.0 (consolidated) | **Status:** Draft — for team & mentor review

> ⚠️ Verify exact wording, background, dataset links, and evaluation criteria on sih.gov.in before final submission.
> This document consolidates the four workstream PRDs already delivered (Blockchain, Cybersecurity, Agentic AI, ML). Each workstream retains its own detailed doc — this is the integration-level view: how the pieces fit, what each hands the next, and what still needs a joint decision.

---

## 1. Executive Summary

When a victim reports a crypto-fraud complaint, investigators today get a wallet address and have to manually trace it through public block explorers — slow, expert-dependent, and not standardized. **WalletTrace** turns this into a same-day, explainable, investigator-facing workflow:

1. **Blockchain module** ingests the reported wallet, builds a transaction graph, clusters addresses using named, explainable forensic heuristics (not a black box), and traces multi-hop fund flow to identify the terminal **exchange** funds landed at — the one actionable choke point where legal action is actually possible.
2. **ML module** layers a trained risk-scoring model and a behavioral-similarity signal on top of the Blockchain module's deterministic output and the Cybersecurity module's rule-based flags, giving a calibrated, explainable risk score per address/cluster.
3. **Cybersecurity module** supplies the fraud-pattern signature library (mixers, peel chains, blacklist proximity) that feeds both Blockchain's context and ML's features, and owns the tamper-evident, hash-anchored evidence trail that gives every trace/score/document legal weight.
4. **Agentic AI module** (LangGraph) orchestrates all three as tools behind a single natural-language investigator interface — "trace this wallet, tell me where the money ended up, and draft the notice to the exchange" — with every claim grounded in a specific tool output, never hallucinated.

The result is a full **trace → cluster → score → attribute → explain → act → prove** pipeline — materially more defensible than a single-team's static dashboard, because each layer is independently real (real on-chain data, named heuristics, trained model with reported metrics, tamper-evident logging) rather than one team's demo dressed up with AI branding.

---

## 2. Problem Statement (Official, as indexed)

Development of a system for **real-time identification of fraud-linked cryptocurrency exchanges from victim-reported suspect wallet addresses through automated blockchain analytics.**

**Core pain points:**
- Investigators receive a wallet address with no tooling beyond manual block-explorer lookups.
- No automated way to cluster wallets belonging to the same fraud ring.
- No fast way to identify which exchange received the funds — the only point where legal action (freeze/KYC disclosure) is possible.
- No investigator-friendly interface; existing tools (Chainalysis, TRM Labs) are expensive, foreign, and not built for India-scale complaint intake.

---

## 3. Goals & Non-Goals (System-Level)

### Goals
- **G1:** Given a victim-reported wallet address, trace multi-hop fund flow and identify the terminal exchange(s) with a confidence score.
- **G2:** Cluster wallets likely controlled by one actor using explainable, named heuristics (deterministic) plus a behavioral-similarity signal (ML) for what heuristics miss.
- **G3:** Produce a calibrated, explainable risk score per address/cluster, combining forensic and rule-based signal into a trained model.
- **G4:** Let an investigator interact with the whole pipeline conversationally via an agent that plans multi-step tool calls and grounds every answer in real tool output.
- **G5:** Auto-draft (never auto-send) legal request documents to identified exchanges, always requiring human review.
- **G6:** Maintain a tamper-evident, hash-anchored audit trail of every trace/score/document for court admissibility.
- **G7:** Present all of the above in a real-time investigator dashboard.

### Non-Goals (explicit, for defensibility)
- **NG1:** No live integration with real exchange KYC databases — public labeled-address datasets for demo attribution.
- **NG2:** No automated fund freezing or account action — intelligence + drafts only, human-in-the-loop always.
- **NG3:** No blockchain indexer built from scratch — use public chain APIs; novelty is in the heuristic/ML/agent layers on top.
- **NG4:** No full cross-chain bridge tracing in MVP — explicit future work.
- **NG5:** No citizen-facing mobile app — investigators/bank fraud-ops are the users; web is the deployment context.

---

## 4. System Architecture (Integration View)

```
 Victim wallet address
        │
        ▼
┌─────────────────────────┐
│  BLOCKCHAIN MODULE       │  Ingest on-chain data (Tron/USDT-TRC20 primary)
│  - graph construction    │  Cluster via named heuristics (common-input-
│  - clustering            │    ownership / deposit-reuse), each merge logs
│  - multi-hop tracing     │    the heuristic + evidence tx
│  - exchange attribution  │  Trace peel-chain-aware fund flow
└─────────────────────────┘  Attribute terminal cluster → exchange + confidence
        │  cluster/trace/attribution output
        ▼
┌─────────────────────────┐        ┌─────────────────────────┐
│  CYBERSECURITY MODULE    │◀──────▶│  ML MODULE               │
│  - fraud-pattern flags   │  flags │  - feature fusion         │
│    (mixer/peel/          │  ─────▶│    (Blockchain + Cyber)   │
│    blacklist/structuring)│        │  - risk-scoring model     │
│  - evidence-trail        │        │    (XGBoost baseline)     │
│    hash-anchoring        │        │  - behavioral clustering  │
│  - PII/access control    │        │    (catches what heuristics│
└─────────────────────────┘        │    miss)                  │
        │  log_event/verify         │  - explainability layer   │
        │                            └─────────────────────────┘
        │                                    │  risk_score + factors
        ▼                                    ▼
┌───────────────────────────────────────────────────────────┐
│              AGENTIC AI MODULE (LangGraph)                  │
│  Orchestrates all of the above as tools behind a single     │
│  natural-language investigator interface. Grounds every     │
│  claim in a tool output. Drafts legal notices (human-review │
│  required). Logs its own reasoning trail via Cybersecurity's │
│  evidence API.                                               │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  DASHBOARD (Web)         │  Graph visualization, case management,
│  - graph/cluster viz     │  embedded agent chat, explainability panels,
│  - agent chat panel      │  evidence-trail verification UI
│  - evidence panel        │
└─────────────────────────┘
```

---

## 5. Module Ownership Summary

| Module | Owner | Core Output | Detailed Doc |
|---|---|---|---|
| Blockchain | Blockchain teammate | Graph, deterministic clusters, trace paths, exchange attribution | `SIH26183_Blockchain_PRD.md` |
| Cybersecurity | Cybersecurity teammate | Fraud-pattern flags, hash-anchored evidence trail, access control, threat model | `SIH26183_Cybersecurity_PRD.md` |
| AI/ML | ML teammate | Trained risk-scoring model, behavioral-similarity signal, explainability | `SIH26183_MLmodel_PRD.md` |
| Agentic AI | Agent/automation teammate | LangGraph orchestration, natural-language interface, grounded answers, notice drafting | `SIH26183_AgenticAI_PRD.md` |
| Dashboard (Software Dev) | Whoever owns frontend | Web UI presenting all of the above | *(not yet written — say the word if you want this one too)* |

**Dependency order:** Blockchain and Cybersecurity are foundational (no upstream dependencies — start first). ML depends on both. Agentic AI depends on all three, plus Dashboard needs stable contracts from everyone. This means Blockchain + Cybersecurity should be first to lock their API schemas.

---

## 6. Cross-Cutting Requirements

| ID | Requirement | Priority |
|---|---|---|
| SYS-FR1 | End-to-end: wallet input → traced, clustered, scored, attributed result within demo-acceptable latency (<10s target for cached/demo data). | Must |
| SYS-FR2 | Every user-facing claim (exchange name, risk score, cluster membership) must be traceable to its originating module's evidence. | Must |
| SYS-FR3 | Every significant action (trace, cluster, score, notice draft) is hash-logged to the evidence trail. | Must |
| SYS-FR4 | System never auto-executes an irreversible action (freeze, send) — draft/recommend only. | Must |
| SYS-FR5 | Dashboard shows real-time updates as each module's stage completes. | Should |

---

## 7. Open Decisions Requiring Joint Sign-Off

These are flagged individually in the workstream docs — listing them together here so the team resolves them as a group before build, not separately per person:

1. **Shared JSON field names** for wallet/cluster/trace/risk-score objects — Blockchain, Cybersecurity, and ML all need to agree on one schema before any integration works. *(Recommend doing this as a 30-minute team sync before coding starts.)*
2. **Risk-score threshold** for the Agent to auto-offer a draft legal notice vs. recommend manual review — a product decision, not purely technical (flagged in both Agentic AI and ML docs).
3. **Labeled dataset sources** — Blockchain needs a labeled exchange-address dataset for attribution; ML needs a labeled fraud/legitimate dataset for training. Confirm both are documented consistently for the "how do you know this is real" judge question.
4. **Primary chain scope** — Tron/USDT-TRC20 as primary (Blockchain doc's recommendation, based on real Indian fraud-corridor relevance); Ethereum as optional stretch. Confirm the whole team is aligned so ML/Agent don't build chain-specific assumptions that break.
5. **Legal-notice template format** — needs domain input (Cybersecurity teammate's fraud-typology knowledge) before Agentic AI can finalize drafting prompts.

---

## 8. Live Demo Script (Full Pipeline)

1. Investigator enters a victim-reported wallet address.
2. **Blockchain**: graph expands live; clustering fires visibly with heuristic evidence shown ("merged: common deposit-reuse, tx 0xabc...").
3. **Cybersecurity + ML**: risk score appears with top contributing factors ("0.87 — rapid multi-hop movement, blacklist proximity").
4. **Blockchain**: terminal exchange identified with confidence, or honest "unattributed — manual review" if below threshold.
5. Investigator asks the **Agent** (chat panel): "Draft the notice for this case." Agent calls tools live, returns a grounded, cited answer and a labeled draft document.
6. **Cybersecurity**: evidence panel shows the hash-anchored log entry for the full session; investigator clicks "verify" to demonstrate integrity live.

**One-line pitch:** "We don't just flag a wallet — we trace where the money actually went using real forensic heuristics, score the risk with a trained model, let an investigator ask for it in plain language, and leave an unforgeable evidence trail for prosecution."

---

## 9. Risks & Mitigations (System-Level)

| Risk | Mitigation |
|---|---|
| Integration breaks due to schema mismatch across modules | Lock shared field names in a joint sync before build (Section 7, item 1) |
| Live demo fails on stage (API flakiness, LLM latency) | Recorded fallback video of a full successful run; rehearse live version multiple times |
| Judges probe "is this really ML or just rules?" | Be precise in the pitch: Blockchain/Cybersecurity are deterministic forensics + rules; ML is the trained, evaluated model layer on top — don't conflate them |
| Judges probe "is this really agentic or just a chatbot?" | Show the LangGraph state/branching logic and the grounding/citation enforcement, not just a chat window |
| Scope too ambitious for available time | Priority order if cutting scope: Blockchain core (Must) → Cybersecurity evidence trail (Must) → ML baseline risk model (Must) → Agent orchestration (Must, but can start with 2-3 tools not all 8) → behavioral clustering / GNN stretch / Ethereum stretch (cut first) |

---

## 10. Open Items Before Submission

- Confirm exact official PS wording/dataset links on sih.gov.in.
- Confirm final project name (replace "WalletTrace" placeholder).
- Resolve the five joint decisions in Section 7.
- Write the Dashboard/Software Dev workstream PRD (not yet done).
- Assign internal build milestones once schema sync is complete.

---

*Master integration document. Individual workstream PRDs remain the source of truth for each module's detailed scope — this document exists to keep the four (soon five) pieces honest about what they hand each other.*
