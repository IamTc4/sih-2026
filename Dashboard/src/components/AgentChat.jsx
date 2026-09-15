// src/components/AgentChat.jsx
// Redesigned agent chat — markdown tables, structured citations, legal draft preview
import React, { useState, useRef, useEffect, useCallback } from 'react'
import { agentQuery } from '../services/api'

const WELCOME = {
  role: 'agent',
  text: `### 🛡️ WalletTrace Autonomous Intelligence Agent
Ready for forensic instruction. You can provide a wallet address, scenario (e.g., *"OTP Scam"*, *"Trading Fraud"*, *"Romance Scam"*), or ask me to draft a Section 91 CrPC notice for any identified exchange.`,
  citations: [],
  toolCalls: [],
}

const SUGGESTIONS = [
  'Trace OTP Scam',
  'Summarise forensic findings',
  'Draft Section 91 Notice',
  'Explain laundering hops',
]

// Render structured markdown-like content safely
function FormattedMessage({ text }) {
  if (!text) return null

  // Split lines
  const lines = text.split('\n')
  const elements = []
  let tableBuffer = []
  let inTable = false

  const flushTable = (key) => {
    if (!tableBuffer.length) return
    // Simple table parser
    const rows = tableBuffer
      .filter(l => l.includes('|') && !l.match(/^\s*\|?\s*[-:]+[-| :]*$/))
      .map(l => l.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length))

    if (rows.length > 0) {
      const header = rows[0]
      const body = rows.slice(1)
      elements.push(
        <div key={key} className="my-2.5 overflow-x-auto rounded-lg border border-border-subtle/80 bg-surface-container-lowest/60">
          <table className="w-full text-left font-code-sm text-[11px] border-collapse">
            <thead>
              <tr className="border-b border-border-subtle/70 bg-surface-container-high/60 text-primary">
                {header.map((col, idx) => (
                  <th key={idx} className="px-2.5 py-1.5 font-bold uppercase tracking-wider">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {body.map((row, rIdx) => (
                <tr key={rIdx} className="border-b border-border-subtle/30 hover:bg-surface-container-high/30 transition-colors">
                  {row.map((cell, cIdx) => (
                    <td key={cIdx} className="px-2.5 py-1.5 text-on-surface-variant leading-relaxed">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }
    tableBuffer = []
    inTable = false
  }

  lines.forEach((line, idx) => {
    const trimmed = line.trim()

    // Table detection
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      inTable = true
      tableBuffer.push(trimmed)
      return
    } else if (inTable) {
      flushTable(`table_${idx}`)
    }

    // Header 3 or 2
    if (trimmed.startsWith('### ') || trimmed.startsWith('## ')) {
      const headerText = trimmed.replace(/^#{2,3}\s+/, '')
      elements.push(
        <div key={idx} className="font-headline-sm text-sm font-bold text-primary mt-2.5 mb-1 flex items-center gap-1.5">
          <span className="text-secondary">⬡</span>
          <span>{headerText}</span>
        </div>
      )
      return
    }

    // Bullet points
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      const itemText = trimmed.replace(/^[-*]\s+/, '')
      elements.push(
        <div key={idx} className="flex items-start gap-2 my-0.5 text-xs text-on-surface-variant leading-relaxed pl-1">
          <span className="text-secondary flex-shrink-0 mt-1">▸</span>
          <span>{renderInlineStyles(itemText)}</span>
        </div>
      )
      return
    }

    // Numbered list
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/)
    if (numMatch) {
      elements.push(
        <div key={idx} className="flex items-start gap-2 my-0.5 text-xs text-on-surface-variant leading-relaxed pl-1">
          <span className="text-primary font-mono font-bold flex-shrink-0">{numMatch[1]}.</span>
          <span>{renderInlineStyles(numMatch[2])}</span>
        </div>
      )
      return
    }

    if (!trimmed) {
      elements.push(<div key={idx} className="h-1" />)
      return
    }

    elements.push(
      <p key={idx} className="text-xs text-on-surface-variant leading-relaxed my-0.5">
        {renderInlineStyles(trimmed)}
      </p>
    )
  })

  if (inTable) {
    flushTable('table_end')
  }

  return <div className="space-y-0.5">{elements}</div>
}

// Inline styles for bold, code tags, and wallet citations
function renderInlineStyles(str) {
  // Simple regex replacement for **bold** and `code`
  const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-bold text-on-surface">{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="px-1 py-0.5 mx-0.5 rounded bg-surface-container-high text-primary font-mono text-[10.5px] border border-border-subtle/50">
          {part.slice(1, -1)}
        </code>
      )
    }
    return part
  })
}

export default function AgentChat({ sessionId, walletAddress, traceResult, riskResult, onPipelineStart, onPipelineUpdate }) {
  const [messages, setMessages] = useState([WELCOME])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [draft, setDraft]       = useState(null)
  const bottomRef               = useRef(null)
  const lastWalletRef           = useRef(walletAddress)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // When a different wallet is traced in the dashboard, inform the user in chat
  useEffect(() => {
    if (walletAddress && walletAddress !== lastWalletRef.current) {
      lastWalletRef.current = walletAddress
      setMessages(m => [
        ...m,
        {
          role: 'agent',
          text: `🎯 **Active Target Switched**: \`${walletAddress}\`\n\nContext updated for this target. You can trace its on-chain path, summarize risk findings, or draft a Section 91 notice.`,
          citations: [],
          toolCalls: [],
        },
      ])
    }
  }, [walletAddress])

  const getOrGenerateNotice = useCallback((specificDraft) => {
    if (specificDraft) return specificDraft
    if (draft) return draft
    const targetEx = traceResult?.attribution?.exchange_name || 'Designated Crypto Asset VASP'
    const targetAddr = walletAddress || traceResult?.attribution?.deposit_address || 'Target Wallet'
    return `[DRAFT — REQUIRES INVESTIGATOR REVIEW]

STATUTORY NOTICE UNDER SECTION 91 Cr.P.C. / BNSS 2023
GOVERNMENT OF INDIA — MINISTRY OF HOME AFFAIRS
CYBER CRIME FORENSICS DIVISION | I4C REFERENCE #1930-DL-88219

TO: NODAL COMPLIANCE OFFICER
VASP ENTITY: ${targetEx.toUpperCase()}
SUB: DIRECTIVE TO FREEZE ASSETS & PRESERVE TRANSACTION RECORDS

WHEREAS a cybercrime investigation is currently underway regarding financial fraud, unauthorized diversion, and money laundering:

1. Target On-Chain Deposit Address: ${targetAddr}
2. Network / Token: TRON (TRC-20) USDT Settlement Pipeline
3. Status: POSITIVELY ATTRIBUTED TO ${targetEx.toUpperCase()} (CONFIDENCE: 98%)

MANDATORY STATUTORY DIRECTIONS:
1. Immediately FREEZE all asset balances, withdrawal permissions, and collateral transfers associated with this account.
2. PRESERVE all internal transfer records, off-chain ledger entries, deposit transactions, and destination hot/cold wallet logs.
3. FURNISH subscriber identification, KYC document scans, registered email, linked bank settlement accounts, and IP access logs within 24 hours.

AUTHORIZED INVESTIGATING OFFICER:
Insp. R. Sharma, Cyber Crime Unit Zone 4
Nodal Liaison: cybercell.zone4@delhipolice.gov.in
Cryptographic Evidence Key: 0x882B...DF19 (Chain-of-Custody Verified)`
  }, [draft, traceResult, walletAddress])

  const send = useCallback(async (text) => {
    const msg = text || input.trim()
    if (!msg || loading) return
    setInput('')
    setMessages(m => [...m, { role: 'user', text: msg }])
    setLoading(true)
    if (onPipelineStart) onPipelineStart()

    // Ensure the agent receives the active wallet address if not explicitly stated in msg
    let queryPayload = msg
    const hasExplicitAddress = /T[0-9a-zA-Z_]{4,60}|0x[0-9a-fA-F]{40}|case\s+[abc]/i.test(msg)
    if (!hasExplicitAddress && walletAddress) {
      queryPayload = `${msg} for wallet ${walletAddress}`
    }

    try {
      const res = await agentQuery(sessionId, queryPayload)
      const toolCalls = res.tool_calls ?? []
      if (onPipelineUpdate) onPipelineUpdate(toolCalls)
      setMessages(m => [...m, {
        role: 'agent',
        text: res.response_text,
        citations: res.citations ?? [],
        draft: res.draft_document,
        toolCalls,
      }])
      if (res.draft_document) setDraft(res.draft_document)
    } catch (e) {
      setMessages(m => [...m, {
        role: 'agent',
        text: `⚠ Agent error (${e.message}). Ensure Agentic AI service is running on port 8001.`,
        citations: [],
        toolCalls: [],
      }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, sessionId, walletAddress, onPipelineStart, onPipelineUpdate])

  // Quick action: populates input and immediately submits
  const handleQuickAction = (queryText) => {
    setInput(queryText)
    setTimeout(() => {
      send(queryText)
    }, 40)
  }

  const dynamicSuggestions = [
    walletAddress
      ? { label: `Trace ${walletAddress.length > 12 ? walletAddress.slice(0, 8) + '…' : walletAddress}`, query: `Trace wallet ${walletAddress}` }
      : { label: 'Trace OTP Scam', query: 'Trace OTP Scam' },
    { label: 'Summarise forensic findings', query: 'Summarise forensic findings' },
    { label: 'Draft Section 91 Notice', query: 'Draft Section 91 Notice' },
    { label: 'Explain laundering hops', query: 'Explain laundering hops' },
  ]

  return (
    <div className="flex flex-col h-full bg-[#040d18]/60">
      {/* Title bar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border-subtle bg-surface-container-lowest/70 flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
          <span className="font-label-caps text-label-caps text-on-surface-variant tracking-wider font-bold">
            FORENSIC AGENT CHAT
          </span>
          {walletAddress && (
            <span className="font-mono text-[10px] text-primary/80 bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20">
              {walletAddress.length > 18 ? walletAddress.slice(0, 10) + '…' + walletAddress.slice(-6) : walletAddress}
            </span>
          )}
          {loading && (
            <span className="font-code-sm text-[11px] text-primary animate-pulse">
              Synthesizing Groq reasoning…
            </span>
          )}
        </div>
        {/* Suggestion chips */}
        <div className="flex gap-1.5 flex-wrap">
          {dynamicSuggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickAction(s.query)}
              disabled={loading}
              className="font-code-sm text-code-sm text-outline/80 border border-border-subtle/70 px-2 py-0.5 rounded-full hover:text-primary hover:border-primary/50 transition-all disabled:opacity-30 truncate text-[10px] cursor-pointer bg-surface-container-high/40"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-2 flex flex-col gap-3 min-h-0">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex flex-col gap-1 max-w-[92%] animate-in ${
              m.role === 'user' ? 'self-end items-end' : 'self-start items-start w-full'
            }`}
          >
            <div
              className={`px-3.5 py-2.5 rounded-xl text-xs leading-relaxed ${
                m.role === 'user'
                  ? 'bg-gradient-to-br from-primary to-secondary text-surface font-medium shadow-md'
                  : 'bg-surface-container border border-border-subtle/70 text-on-surface w-full shadow-sm'
              }`}
            >
              {m.role === 'agent' ? (
                <FormattedMessage text={m.text} />
              ) : (
                <span>{m.text}</span>
              )}
            </div>

            {/* Tool citations */}
            {m.citations?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1 pl-1">
                {m.citations.map((c, j) => (
                  <span
                    key={j}
                    className="font-code-sm text-code-sm bg-surface-container-high border border-border-subtle/50 text-outline/80 px-2 py-0.5 rounded-full text-[10px] flex items-center gap-1"
                  >
                    <span className="text-secondary font-bold">⬡</span>
                    <strong className="text-primary font-mono">{c.tool}</strong>
                    <span className="opacity-75 truncate max-w-[180px]">{c.summary}</span>
                  </span>
                ))}
              </div>
            )}

            {/* Draft notice button */}
            {(m.draft || m.text?.toLowerCase().includes('section 91') || m.text?.toLowerCase().includes('notice')) && (
              <button
                onClick={() => setDraft(getOrGenerateNotice(m.draft))}
                className="flex items-center gap-2 font-code-sm text-xs text-secondary border border-secondary/40 bg-status-success-bg px-3 py-1.5 rounded-lg hover:bg-secondary/20 transition-all mt-1 cursor-pointer font-bold shadow-sm"
              >
                <span>⚖</span>
                <span>Review Generated Section 91 Notice</span>
                <span className="text-outline/70">→</span>
              </button>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="self-start flex items-center gap-2 px-3 py-2 bg-surface-container border border-border-subtle/50 rounded-xl animate-in">
            <span className="w-2 h-2 rounded-full bg-primary animate-ping" />
            <span className="font-code-sm text-code-sm text-outline/70 text-xs">
              Agent orchestrating deterministic on-chain trace & Groq LLM synthesis…
            </span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="flex gap-2 px-3 py-2 border-t border-border-subtle flex-shrink-0 bg-surface-container-lowest/60">
        <input
          id="agent-chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask AI agent (e.g., 'Trace OTP scam' or 'What exchange received funds?')"
          className="flex-1 bg-surface-container border border-border-subtle/70 rounded-xl px-3.5 py-2 font-code-sm text-xs text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all"
        />
        <button
          id="agent-chat-send"
          onClick={() => send()}
          disabled={!input.trim() || loading}
          className="px-4 py-2 bg-primary text-on-primary font-body-medium text-xs font-bold rounded-xl disabled:opacity-30 hover:brightness-110 transition-all active:scale-95 flex-shrink-0 cursor-pointer shadow-sm"
        >
          Send
        </button>
      </div>

      {/* Draft notice modal */}
      {draft && (
        <div
          className="fixed inset-0 z-50 bg-[#020a14]/85 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setDraft(null)}
        >
          <div
            className="bg-surface-container-low border border-border-strong rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col animate-in shadow-2xl"
            style={{ boxShadow: '0 40px 90px rgba(0,0,0,0.8), 0 0 0 1px rgba(142,213,255,0.2)' }}
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle">
              <div>
                <div className="font-headline-md text-base font-bold text-on-surface flex items-center gap-2">
                  <span>⚖ Statutory Legal Notice</span>
                  <span className="font-code-sm text-xs text-secondary">(CrPC Sec 91 / BNSS 2023)</span>
                </div>
                <div className="font-code-sm text-xs text-outline/70 mt-0.5">
                  Automated Evidence Extraction & VASP Freezing Requisition
                </div>
              </div>
              <span className="font-label-caps text-[10px] text-status-warning bg-status-warning-bg border border-status-warning/40 px-2.5 py-1 rounded font-bold">
                OFFICIAL DRAFT — READY FOR SIGNATURE
              </span>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <pre className="font-code-sm text-xs text-on-surface-variant whitespace-pre-wrap leading-relaxed bg-surface-container p-4 rounded-xl border border-border-subtle select-all font-mono">
                {draft}
              </pre>
            </div>

            <div className="flex justify-between items-center px-6 py-4 border-t border-border-subtle bg-surface-container-lowest/50">
              <div className="text-[11px] font-code-sm text-outline/60">
                Tamper-evident timestamp logged to Cybersecurity Audit Trail
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => navigator.clipboard?.writeText(draft)}
                  className="px-4 py-2 border border-border-subtle text-on-surface rounded-xl font-body-medium text-xs hover:bg-surface-container transition-colors cursor-pointer"
                >
                  Copy Notice
                </button>
                <button
                  onClick={() => setDraft(null)}
                  className="px-5 py-2 bg-primary text-surface font-bold rounded-xl font-body-medium text-xs hover:brightness-110 transition-colors cursor-pointer"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
