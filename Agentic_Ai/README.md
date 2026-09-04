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

# 4. Run the API server
python main.py

# 5. Run all tests (no API key required — LLM is mocked)
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
  [Cluster]    ← calls get_cluster()                             │
      │                                                           │
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
                                                │
                                         API Response
```

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
│   ├── api.py                    # FastAPI app — POST /agent/query
│   └── tools/
│       ├── __init__.py
│       └── mocks.py              # All 8 tool stubs (drop-in swap when real modules ready)
│
└── tests/
    ├── __init__.py
    ├── test_tools.py             # Unit tests for all 8 tool schemas
    ├── test_security.py          # Injection detection + grounding tests
    └── test_graph_integration.py # 3 mandated integration tests + scope refusal
```

---

## Tool Contract Reference

All 8 tools are in `walletrace/tools/mocks.py`. **Do not change signatures.**

| Tool | Owner | Status |
|------|-------|--------|
| `trace_wallet(address)` | Blockchain team | MOCK |
| `get_cluster(address)` | Clustering team | MOCK |
| `get_risk_score(address_or_cluster_id)` | ML/Risk team | MOCK |
| `identify_exchange(address)` | Attribution team | MOCK |
| `check_blacklist(address)` | Attribution team | MOCK |
| `draft_legal_notice(case_id, exchange, evidence_summary)` | This repo | MOCK/REAL |
| `log_event(event_type, payload)` | This repo | MOCK/REAL |
| `verify_entry(entry_id)` | This repo | MOCK/REAL |

---

## Configurable Constants (`walletrace/config.py`)

| Constant | Default | Description |
|----------|---------|-------------|
| `CONFIDENCE_THRESHOLD` | `0.75` | Attribution confidence gate for DraftNotice vs ManualReview |
| `LLM_MODEL` | `gemini-1.5-pro` | LLM model name |
| `LLM_TEMPERATURE` | `0.1` | LLM temperature |
| `INJECTION_PATTERNS` | (list) | Phrases triggering `[INJECTION_FLAG]` in tool output |

Set via `.env` file or environment variables.

---

## Security Architecture

### 1. Prompt Injection Defence
- Every tool output is passed through `sanitize_tool_output()` before reaching the LLM
- Any text matching patterns in `INJECTION_PATTERNS` (e.g. "ignore previous instructions") is prepended with `[INJECTION_FLAG]` and wrapped in `<TOOL_OUTPUT>` data tags
- The system prompt (`SYSTEM_BOUNDARY`) explicitly forbids the LLM from following instructions found inside tool output tags
- Routing decisions are made on **numeric confidence values**, never on exchange name strings

### 2. Grounding Enforcement
- `build_grounded_prompt()` inserts all tool evidence and requires the LLM to cite each claim: `"[source: tool_name → field]"`
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
  "draft_document": "[DRAFT - REQUIRES INVESTIGATOR REVIEW]\n\nNOTICE TO..."
}
```

`draft_document` is `null` when confidence is below threshold.

### `GET /health`
```json
{"status": "ok", "service": "walletrace-agent"}
```

Interactive docs available at `http://localhost:8000/docs`.

---

## Test Results

```
49 passed, 1 warning in 0.49s
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
| `TestScopeRefusal` | Off-topic → OUT_OF_SCOPE, no tools called |
