# WalletTrace — Agentic AI Orchestration Module
**SIH26183 | Real-time Identification of Fraud-Linked Cryptocurrency Exchanges**

---

## Quick Start

```bash
# 1. Clone / navigate to this folder
cd c:\SIH_26-27\Agentic_Ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env and set GOOGLE_API_KEY or OPENAI_API_KEY
# (a real key is required for now — mock-LLM mode is not yet implemented)

# 4. Seed demo case data (optional, enables cross-case correlation demo)
python seed_demo.py

# 5. Run the API server
python main.py

# 6. Run all tests (no API key required — LLM is mocked)
python -m pytest -v
```

---

## Architecture

```
POST /agent/query
      │
      ▼
  [Intake] ──── (out-of-scope or no address) ────────────────────┐
      │                                                           │
      ▼                                                           │
  [Trace]      ← calls trace_wallet()                            │
      │                                                           │
      ▼                                                           │
  [Cluster]    ← calls get_cluster()                              │
      │                                                           │
      ▼                                                           │
  [Correlate]  ← checks cluster addresses against case_store.py  │
      │           for overlap with prior, unrelated cases         │
      ▼                                                           │
  [RiskScore]  ← calls get_risk_score(cluster_id)                │
      │                                                           │
      ▼                                                           │
  [Attribute]  ← calls identify_exchange() + check_blacklist()   │
      │                                                           │
      ├── confidence ≥ CONFIDENCE_THRESHOLD ──► [DraftNotice]    │
      │                                              │            │
      └── confidence <  CONFIDENCE_THRESHOLD ──► [ManualReview]  │
                                                     │            │
                                              [Log] ◄────────────┘
                                                │
                                           [Respond] ← LLM call with grounded prompt
                                                │  (cites related_cases same as any
                                                │   other tool evidence)
                                         API Response
```

### Cross-Case Correlation
Real fraud rings hit multiple victims who each file separate, disconnected
complaints. The `[Correlate]` node checks every new trace's cluster
addresses against previously logged cases (`case_store.py`, SQLite-backed)
and surfaces any overlap as `related_cases` — e.g. "this wallet's cluster
shares 2 addresses with Case #4521, filed 6 days ago." This turns
single-wallet tracing into organized-ring detection across otherwise
unconnected NCRP complaints, and is grounded/cited exactly like any other
tool output (`[source: case_correlation]`).

Run `seed_demo.py` before a live demo to pre-populate a prior case
that deliberately overlaps with the wallet you plan to trace on stage.

### Session Persistence
LangGraph's `MemorySaver` stores checkpoints keyed by `session_id` (thread_id).  
Send the **same `session_id`** in follow-up requests to continue an investigation  
without re-running the full pipeline.  
To switch to SQLite: replace `MemorySaver` with `SqliteSaver` in `graph.py` (one line change).

---

## File Structure

```
Agentic_Ai/
├── main.py                       # CLI entry point
├── seed_demo.py                  # Pre-populates case_store.py for demo correlation
├── requirements.txt
├── pytest.ini
├── .env.example                  # Copy to .env
│
├── walletrace/
│   ├── __init__.py
│   ├── config.py                 # All tunable constants (CONFIDENCE_THRESHOLD etc.)
│   ├── state.py                  # LangGraph TypedDict state schema
│   ├── graph.py                  # Graph definition: nodes, edges, routing
│   ├── security.py               # Injection sanitizer + grounding prompt builder
│   ├── case_store.py             # SQLite store + overlap lookup for cross-case correlation
│   ├── api.py                    # FastAPI app — POST /agent/query
│   └── tools/
│       ├── __init__.py
│       └── mocks.py              # All 8 tool stubs (drop-in swap when real modules ready)
│
└── tests/
    ├── __init__.py
    ├── test_tools.py             # Unit tests for all 8 tool schemas
    ├── test_security.py          # Injection detection + grounding tests
    └── test_graph_integration.py # Integration tests: pipeline, scope refusal, correlation
```

---

## Tool Contract Reference

All 8 tools are in `walletrace/tools/mocks.py`. **Do not change signatures.**

| Tool | Owner | Status |
|------|-------|--------|
| `trace_wallet(address)` | Blockchain team | MOCK (real endpoint via `BLOCKCHAIN_API_URL`) |
| `get_cluster(address)` | Clustering team | MOCK (real endpoint via `BLOCKCHAIN_API_URL`) |
| `get_risk_score(address_or_cluster_id)` | ML/Risk team | MOCK ✅ (real endpoint via `ML_API_URL`) |
| `identify_exchange(address)` | Attribution team | MOCK (real endpoint via `BLOCKCHAIN_API_URL`) |
| `check_blacklist(address)` | Attribution team | MOCK (real endpoint via `CYBERSECURITY_API_URL`) |
| `draft_legal_notice(case_id, exchange, evidence_summary)` | This repo | MOCK/REAL |
| `log_event(event_type, payload)` | This repo | MOCK/REAL |
| `verify_entry(entry_id)` | This repo | MOCK/REAL |

`case_store.py`'s correlation lookup is **not** an external tool call — it's an
in-process node (`[Correlate]`) that queries a local SQLite store, so it has
no upstream-team dependency and works fully offline/mocked.

---

## Configurable Constants (`walletrace/config.py`)

| Constant | Default | Description |
|----------|---------|-------------|
| `CONFIDENCE_THRESHOLD` | `0.75` | Attribution confidence gate for DraftNotice vs ManualReview |
| `LLM_MODEL` | `gemini-1.5-pro` | LLM model name |
| `LLM_TEMPERATURE` | `0.1` | LLM temperature |
| `INJECTION_PATTERNS` | (list) | Phrases triggering `[INJECTION_FLAG]` in tool output |

Set via `.env` file or environment variables.

> **Note:** A mock-LLM mode (to run/demo without a real API key) is not yet
> implemented — currently a valid `GOOGLE_API_KEY` (or `OPENAI_API_KEY`) is
> required for the `[Respond]` node to complete. This is a good next addition
> if demoing offline is a priority.

---

## Security Architecture

### 1. Prompt Injection Defence
- Every tool output is passed through `sanitize_tool_output()` before reaching the LLM
- Any text matching patterns in `INJECTION_PATTERNS` (e.g. "ignore previous instructions") is prepended with `[INJECTION_FLAG]` and wrapped in `<TOOL_OUTPUT>` data tags
- The system prompt (`SYSTEM_BOUNDARY`) explicitly forbids the LLM from following instructions found inside tool output tags
- Routing decisions are made on **numeric confidence values**, never on exchange name strings

### 2. Grounding Enforcement
- `build_grounded_prompt()` inserts all tool evidence (including `related_cases`, when present) and requires the LLM to cite each claim: `"[source: tool_name → field]"`
- If a fact can't be grounded, the LLM must say "unable to confirm"
- Citations are returned as structured objects in the API response

### 3. No Auto-Execution
- `node_draft_notice` only calls `draft_legal_notice()` — it does not send, submit, or freeze anything
- All draft output is watermarked: `DRAFT - REQUIRES INVESTIGATOR REVIEW`
- The system prompt forbids claiming any irreversible action was taken

---

## API Reference

### `POST /agent/query`

**Request:**
```json
{
  "session_id": "inv-session-abc123",
  "message": "Please trace wallet 0xABCDEF1234567890ABCDEF1234567890ABCDEF15"
}
```

**Response:**
```json
{
  "session_id": "inv-session-abc123",
  "response_text": "Risk score: 0.87 [source: get_risk_score → risk_score]...",
  "citations": [
    {"tool": "trace_wallet", "summary": "..."},
    {"tool": "get_risk_score", "summary": "..."}
  ],
  "draft_document": "[DRAFT - REQUIRES INVESTIGATOR REVIEW]\n\nNOTICE TO...",
  "related_cases": [
    {
      "case_id": "CASE-2026-04521",
      "overlap_addresses": ["TMOCK_9F2E1D_COSP1", "TMOCK_9F2E1D_COSP2"],
      "exchange": "MockEx India",
      "filed_date": "2026-09-06T15:26:16.853687"
    }
  ]
}
```

`draft_document` is `null` when confidence is below threshold.
`related_cases` is `[]` when no prior case shares any address with the current cluster.

### `GET /health`
```json
{"status": "ok", "service": "walletrace-agent"}
```

Interactive docs available at `http://localhost:8000/docs`.

---

## Demo Data

See `seed_demo.py` for a ready-to-run script that seeds a prior case
sharing a cluster suffix with a wallet you can trace live. Sample requests
covering each pipeline branch (high confidence, low confidence, correlation,
blacklist match, session resume, scope refusal, injection attempt) are
documented alongside it for quick manual testing via `/docs`.

---

## Test Results

```
50 passed, 1 warning in 0.5x s
```

| Test class | Coverage |
|------------|----------|
| `TestTraceWallet` | Schema, edges, seed echo |
| `TestGetCluster` | Schema, seed membership, heuristics |
| `TestGetRiskScore` | Range, factors, cluster vs address score |
| `TestIdentifyExchange` | Attributed/unattributed, null contract |
| `TestCheckBlacklist` | Match/no-match |
| `TestDraftLegalNotice` | Watermark, case ID, exchange, evidence |
| `TestLogEvent` | Hash format, logged=True |
| `TestVerifyEntry` | Valid/invalid entries |
| `TestSanitizeToolOutput` | Injection detection, all patterns, case-insensitive |
| `TestBuildGroundedPrompt` | Evidence inclusion, citation instruction, routing |
| `TestEndToEndHighConfidence` | **(a)** Full pipeline → DraftNotice, log, citations |
| `TestEndToEndLowConfidence` | **(b)** Low confidence → ManualReview, no draft |
| `TestPromptInjectionDefence` | **(c)** Injection text → flagged, routing unchanged |
| `TestScopeRefusal` | Off-topic → OUT_OF_SCOPE, no tools called; also covers **(d)** cross-case correlation integration (`node_correlate` populates `related_cases` when a traced wallet's cluster overlaps a pre-seeded case) |

> **Note:** An autouse `isolated_case_db` fixture in `test_graph_integration.py`
> redirects `case_store.DB_PATH` to a temporary file for every test in that
> module. This keeps test runs from writing into the real `cases.db` used by
> the live server, so repeated test runs never pollute `seed_demo.py`'s
> pre-seeded demo data.