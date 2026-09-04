# Workstream PRD — Agentic AI (LangChain / LangGraph) Module
**Parent Project:** WalletTrace (SIH26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics)
**Owner:** AI Agent / Automation teammate
**Version:** v1.0 | **Status:** Draft

> One of five workstreams. This is the module that turns "a pipeline of separate tools" into "one investigator-facing system." It doesn't do tracing, clustering, scoring, or logging itself — it **orchestrates** the other four workstreams' functions as tools, and gives the investigator a single natural-language interface over all of it. This is your strongest differentiator vs. other teams' static dashboards — treat it as the centerpiece of the pitch, not a bolt-on chatbot.

---

## 1. Role of This Module in the Overall System

Every other workstream produces a capability (trace a wallet, cluster addresses, score risk, log evidence). Without this module, the investigator has to manually click through five different outputs and mentally connect them. With it, the investigator asks one question — "trace this wallet and tell me where the money ended up, and if it's confirmed, draft the notice to the exchange" — and the agent plans the multi-step tool sequence, executes it, and returns a grounded, cited answer.

**Why LangGraph specifically (not just LangChain):** this workflow isn't a single prompt-response — it's a multi-step, stateful, sometimes-branching process (trace → check confidence → maybe re-trace deeper → cluster → attribute → conditionally draft notice → log). LangGraph's explicit state-machine/graph model is built for exactly this: durable multi-step agent workflows with conditional branches, not a single linear chain. That's the honest technical justification for the tool choice, and worth stating plainly if judges ask "why not just a simple LLM call."

---

## 2. Goals & Non-Goals

### Goals
- **G1:** Build a LangGraph-orchestrated agent that exposes the other workstreams' functions as callable tools.
- **G2:** Support natural-language investigator queries ("trace wallet X," "who else is linked to this cluster," "draft the notice for this case") resolved through correct tool sequencing.
- **G3:** Ground every agent response strictly in tool outputs — no answer should state a fact (an exchange name, a confidence score, a linked address) that didn't come from a tool call. This is non-negotiable for a law-enforcement-facing tool.
- **G4:** Auto-draft a legal request/notice document (freeze request / KYC-disclosure request format) to the identified exchange, using case facts pulled from tool outputs — always presented as a draft for human review, never auto-sent.
- **G5:** Log every agent action (tool calls + final answers) via the Cybersecurity module's evidence-trail API, so the agent's own reasoning trail is itself auditable.
- **G6:** Defend against prompt injection — since wallet-linked notes/labels could theoretically contain adversarial text designed to manipulate the agent's output.

### Non-Goals
- **NG1:** Not implementing the tracing, clustering, risk-scoring, or hash-anchoring logic itself — those are tool calls into the Blockchain, AI/ML, and Cybersecurity modules.
- **NG2:** Not auto-sending any generated document to a real exchange or freezing any account — draft-and-human-review only (mirrors master PRD NG2/NG3).
- **NG3:** Not building a general-purpose chatbot — the agent's scope is strictly the investigation workflow; refuse/deflect off-topic queries.
- **NG4:** Not fine-tuning a custom LLM — use an existing hosted LLM via API with tool-calling support; your novelty is orchestration and grounding, not model training.

---

## 3. Deliverables (What You Personally Build)

### 3.1 Tool Definitions (Wrapping Other Workstreams' APIs)
Each tool is a thin, well-typed wrapper around another team's endpoint — you don't reimplement their logic, you just expose it correctly to the agent:

| Tool | Wraps | Returns |
|---|---|---|
| `trace_wallet(address)` | Blockchain module's `GET /trace/{address}` | graph + trace path |
| `get_cluster(address)` | Blockchain module's cluster output | cluster_id, addresses, heuristic evidence |
| `get_risk_score(address_or_path)` | AI/ML module's risk-scoring endpoint (once available) | risk score + contributing signals |
| `identify_exchange(address)` | Blockchain module's attribution output | exchange name, deposit address, confidence |
| `check_blacklist(address)` | Cybersecurity module's blacklist query | match / no match + source case |
| `draft_legal_notice(case_id, exchange, evidence_summary)` | Your own LLM prompt, grounded in prior tool outputs | draft notice text |
| `log_event(event_type, payload)` | Cybersecurity module's `POST /log-event` | confirmation + entry hash |
| `verify_entry(entry_id)` | Cybersecurity module's `GET /verify/{entry_id}` | integrity confirmation |

### 3.2 LangGraph State Machine
- Design the graph nodes: `Intake → Trace → Cluster → RiskScore → Attribute → (branch: confidence high enough?) → DraftNotice → Log → Respond`.
- Conditional edges: e.g., if attribution confidence is low, route to a "recommend manual review" terminal node instead of drafting a notice.
- Persist state per case/session so an investigator can ask follow-up questions without re-running the whole pipeline (LangGraph's state persistence is the right fit here — this is the concrete reason to use it over a plain LangChain chain).

### 3.3 Grounding & Citation Layer
- Every claim in a final agent response must be traceable to a specific tool call's output. Implement this as: agent responses include inline references to which tool result supports each stated fact (e.g., "Exchange X [from identify_exchange, confidence 87%]").
- Reject/flag any generation step where the model would need to state a fact not present in tool outputs.

### 3.4 Legal-Notice Drafting
- Template-guided LLM generation: structure (case reference, wallet(s) involved, traced evidence summary, requested action) is fixed; the LLM fills in case-specific narrative from tool outputs.
- Explicitly watermark/label output as "DRAFT — REQUIRES INVESTIGATOR REVIEW."

### 3.5 Prompt-Injection Defense
- Treat any text pulled from on-chain data or address labels as untrusted content, not instructions — never let content retrieved via tools be interpreted as new instructions to the agent.
- Basic input sanitization + a system-prompt boundary that explicitly tells the model to ignore instructions embedded in tool-returned data.
- Document this as part of the team's security review (feeds into Cybersecurity's threat model doc).

---

## 4. Functional Requirements (This Module Only)

| ID | Requirement | Priority |
|---|---|---|
| AG-FR1 | Agent shall resolve natural-language investigator queries into a correct sequence of tool calls. | Must |
| AG-FR2 | Agent shall ground every factual claim in its response to a specific tool output. | Must |
| AG-FR3 | Agent shall draft a legal notice document when attribution confidence exceeds a defined threshold, otherwise recommend manual review. | Must |
| AG-FR4 | Agent shall log every tool call and final response via the evidence-trail API. | Should |
| AG-FR5 | Agent shall resist prompt injection from untrusted tool-returned content. | Should |
| AG-FR6 | Agent shall maintain conversational state per case for follow-up queries without full re-execution. | Should |
| AG-FR7 | Agent shall refuse queries outside the investigation-workflow scope. | Could |

---

## 5. Tech Stack

| Layer | Tools |
|---|---|
| Orchestration | LangGraph (state machine / multi-step agent), LangChain (tool-calling utilities, prompt templates) |
| LLM | Any hosted model with reliable tool-calling (Claude, GPT, or Gemini via API — pick based on team's API budget/access) |
| Tool wrappers | Python, calling the other workstreams' FastAPI endpoints |
| State persistence | LangGraph's built-in checkpointing (in-memory or lightweight DB for the hackathon) |
| Frontend hook-in | Expose a single `/agent/query` endpoint for the Dashboard team's chat UI to call |

---

## 6. Integration Interfaces

| To/From | Interface |
|---|---|
| Blockchain module | Consumes `GET /trace/{address}`, cluster/attribution outputs — **confirm exact JSON field names with them before building tool wrappers** |
| AI/ML module | Consumes risk-scoring endpoint (build this tool wrapper once their API contract is defined — coordinate early since it's downstream of their work) |
| Cybersecurity module | Consumes `POST /log-event`, `GET /verify/{entry_id}`, blacklist-check endpoint |
| Dashboard/Software Dev | Provides single `POST /agent/query {session_id, message}` → returns `{response_text, citations, draft_document?}` for their chat UI to render |

**This module is the last one to fully build** since it depends on every other team's API — but you can and should build the LangGraph skeleton and mock tool responses immediately so you're not blocked, then swap in real endpoints as teammates finish theirs.

---

## 7. Demo Script (Your Segment)

1. Investigator types: "Trace this wallet and tell me where the money ended up."
2. Agent visibly calls `trace_wallet` → `get_cluster` → `identify_exchange` (tool-call trace shown in UI for transparency/wow-factor).
3. Agent responds: "Funds traced through 4 hops, clustered with 2 other addresses via deposit-reuse pattern, terminated at Exchange X (87% confidence)." — each clause cited to its tool source.
4. Investigator asks: "Draft the notice for this case."
5. Agent calls `draft_legal_notice`, returns a labeled draft document.
6. Agent logs the full session via `log_event`; investigator can click "verify" to show the entry's integrity check live.

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Blocked waiting on other teams' APIs | Build against mocked tool responses first; swap real endpoints in once available |
| LLM hallucinates a fact not in tool output | Strict grounding/citation enforcement (Section 3.3); consider a post-generation check that flags ungrounded claims |
| Prompt injection via on-chain data (e.g., a malicious memo field) | Treat all tool-returned content as data, not instructions (Section 3.5) |
| Live demo LLM latency/API flakiness | Have a recorded fallback of a full successful agent session |
| Judges think it's "just a chatbot wrapper" | Be ready to explain the state-machine/branching logic and grounding enforcement — that's the actual engineering, not the LLM call itself |

---

## 9. Open Items Before Build Starts

- Confirm LLM provider and API budget with the team.
- Get draft API contracts (even mocked) from Blockchain and Cybersecurity teammates ASAP so tool wrappers can be scaffolded in parallel.
- Decide the confidence threshold for auto-offering a draft notice vs. recommending manual review (Section 3.4/AG-FR3) — this is a product decision, not just engineering, so agree it with the whole team.
- Confirm exact legal-notice template/format with whoever has domain input (Cybersecurity teammate's fraud-typology knowledge is useful here).

---

*Workstream-level document. This depends on the Blockchain and Cybersecurity workstream PRDs already delivered, and will need the AI/ML risk-scoring contract once that PRD is ready.*
