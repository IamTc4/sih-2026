# Workstream PRD — Cybersecurity Module
**Parent Project:** WalletTrace (SIH26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics)
**Owner:** Cybersecurity teammate
**Version:** v1.0 | **Status:** Draft

> This is one of five workstreams (Blockchain/ML, Agentic/LangGraph, Blockchain-chain, Software/Dashboard, Cybersecurity). This doc defines what the Cybersecurity owner builds independently, and exactly what they hand off to the other workstreams for integration. See Section 6 for interfaces.

---

## 1. Role of This Module in the Overall System

The rest of the team builds *tracing* (where did the money go) and *presentation* (dashboard, agent). This module is what makes the system **defensible, trustworthy, and legally usable** — the part that answers "how do we know this data wasn't tampered with, and why should this flagged address be trusted?" It has two halves:

1. **Threat-intelligence layer** — pattern/signature library that flags *why* an address or fund-flow looks like fraud (mixers, peel chains, known scam clusters), feeding confidence scores to the ML clustering model.
2. **Security & evidence-integrity layer** — secure handling of victim PII/case data, and the tamper-evident audit trail (Stage 4 in the master architecture) that hash-anchors every trace/action for prosecution.

---

## 2. Goals & Non-Goals

### Goals
- **G1:** Build a rules/pattern library that detects known obfuscation techniques (mixer usage, peel chains, rapid layering/hopping, structuring) from transaction graph data, and outputs a risk signal consumable by the ML model.
- **G2:** Maintain a curated list/signature set of known scam-cluster indicators (reused addresses from prior fraud cases, blacklisted addresses) to flag proximity matches.
- **G3:** Design and implement the tamper-evident evidence trail: every trace, cluster result, exchange-attribution, and agent-generated document gets hashed and logged immutably.
- **G4:** Define and enforce access-control and data-handling rules for victim/case PII (who can see raw complaint data vs. anonymized trace data).
- **G5:** Produce a short security review/threat model of the whole pipeline (attack surface: fake complaint injection, API abuse, agent prompt injection) that the team can present to judges.

### Non-Goals
- **NG1:** Not building the ML clustering model itself — you define the *features/signals* (e.g., "hop count > 5 in <1hr = high risk"), the AI/ML owner implements the model that consumes them.
- **NG2:** Not building the dashboard UI — you define what the evidence-trail API returns; Software Dev renders it.
- **NG3:** Not doing real-world exchange takedown/freezing — out of scope for the whole project (see master PRD NG2).
- **NG4:** Not building a production-grade blockchain (permissioned ledger or public-chain anchoring is enough — pick the simplest thing that's demoable and defensible under questioning).

---

## 3. Deliverables (What You Personally Build)

### 3.1 Fraud-Pattern / Threat-Signature Library
A rules engine (can start as a Python module, not ML) that takes a transaction graph/path as input and outputs flags + a risk contribution score. Signatures to include at minimum:
- **Mixer/tumbler usage** — funds passing through addresses with many-in/many-out fan patterns.
- **Peel chain detection** — a chain of transactions where a small amount is "peeled off" repeatedly while the bulk moves on (classic layering pattern).
- **Rapid hopping** — unusually fast multi-hop movement (time-window heuristic) suggesting evasion.
- **Known scam-cluster proximity** — address is within N hops of an address on your curated blacklist (seed this list from public scam-report datasets or prior case data).
- **Structuring** — multiple sub-threshold transactions that sum to a round/suspicious total.

Output format (per address/path): `{signature: str, confidence: float, evidence: [tx_hashes]}` — this is what you hand to the ML team as engineered features.

### 3.2 Evidence Trail / Hash-Anchoring Service
- Every significant pipeline event (wallet trace run, cluster result, exchange attribution, agent-generated legal notice) gets serialized, hashed (SHA-256), and appended to an immutable log.
- Simplest defensible build: a permissioned hash-chain (each entry stores hash of its content + hash of previous entry, like a lightweight blockchain) — you do **not** need a real distributed blockchain network for a 36-hour hackathon; a well-designed hash-chain with clear "this is how it'd anchor to a public chain in production" framing is enough and is what most SIH finalist teams actually ship.
- Expose a simple verification endpoint: given an entry, confirm its hash matches and the chain isn't broken.

### 3.3 PII / Data-Handling Policy + Enforcement
- Define what counts as sensitive (victim name/contact, raw complaint text) vs. safe-to-display (wallet addresses, trace graph, risk scores).
- Implement basic access control on the API (e.g., role: investigator vs. read-only viewer) and redaction rules for anything exported/logged.
- Document this as a short "data handling & security" one-pager — judges in this theme *will* ask about it.

### 3.4 Threat Model / Security Review of the Full Pipeline
- One-page threat model covering: fake/malicious complaint injection, API abuse/rate limiting, prompt injection against the LangGraph agent (e.g., a malicious wallet-linked note tricking the agent into fabricating a notice), and evidence-trail tampering attempts.
- For each: state the mitigation (even if just "documented as future work" for lower-priority ones).

---

## 4. Functional Requirements (This Module Only)

| ID | Requirement | Priority |
|---|---|---|
| SEC-FR1 | Module shall accept a transaction path/graph and return fraud-pattern flags with confidence scores. | Must |
| SEC-FR2 | Module shall maintain a queryable blacklist of known scam-linked addresses. | Must |
| SEC-FR3 | Module shall hash and append every trace/cluster/notice event to an immutable log. | Must |
| SEC-FR4 | Module shall expose a verify-integrity endpoint for any logged entry. | Should |
| SEC-FR5 | Module shall enforce role-based redaction of victim PII in API responses. | Should |
| SEC-FR6 | Module shall provide a documented threat model covering the end-to-end pipeline. | Should |

---

## 5. Tech Stack (Suggested)

| Layer | Tools |
|---|---|
| Pattern/rules engine | Python (pure logic + NetworkX for path analysis — no heavy ML needed here) |
| Hash-anchoring | Python `hashlib` (SHA-256) for the hash-chain; optionally anchor periodic checkpoints to a public testnet for the demo's "real blockchain" credibility |
| Access control | FastAPI dependency-based auth (simple JWT/role check is enough) |
| Blacklist storage | Simple DB (SQLite/Postgres) — table of flagged addresses + source/case reference |

---

## 6. Integration Interfaces (What You Hand Off)

| To | You Provide | Format |
|---|---|---|
| AI/ML owner | Fraud-signature flags + confidence per address/path | JSON: `{address, signatures: [...], risk_score}` |
| Agentic/LangGraph owner | Read-only "log this event" and "verify this entry" API calls the agent can invoke as tools | REST endpoints: `POST /log-event`, `GET /verify/{entry_id}` |
| Software Dev (dashboard) | Evidence-trail query endpoint for the UI's "evidence" panel | `GET /evidence-trail?case_id=` |
| Whole team | One-page security review + data-handling policy | Markdown/PDF, for the pitch deck's "trust & security" slide |

**Ask the other owners for their interface contracts too** (what a wallet-trace result object looks like, what a cluster object looks like) so you can log the *actual* shapes rather than guessing — that mismatch is the #1 place hackathon teams lose integration time on day 2.

---

## 7. Suggested Build Order (for a 36-hour-style timeline)

1. Blacklist + basic pattern flags (mixer/peel-chain detection on sample data) — get something flagging *something* early.
2. Hash-chain logging service with the verify endpoint.
3. Role-based redaction on a stub API.
4. Threat model write-up (can be done in parallel, doesn't block code).
5. Integration pass once ML/Agent/Dashboard owners have their stub interfaces ready.

---

*This is a workstream-level document, not the master submission PRD. Once all five workstreams have their own PRD, the next step is a combined architecture pass to lock down the shared data contracts (wallet object, cluster object, trace object) before build starts.*
