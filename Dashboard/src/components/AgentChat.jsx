// src/components/AgentChat.jsx
// Agent chat panel — connects to Agentic AI POST /agent/query
import React, { useState, useRef, useEffect } from 'react'
import { agentQuery } from '../services/api'

const WELCOME = {
  role: 'agent',
  text: 'WalletTrace AI ready. Trace a wallet to begin, or ask me anything about the current investigation.',
  citations: [],
}

const SUGGESTIONS = [
  'Summarise the forensic findings for this wallet',
  'What exchange received the funds?',
  'Draft a legal notice for the investigating officer',
  'Explain the highest-risk cluster',
]

export default function AgentChat({ sessionId, traceResult, riskResult }) {
  const [messages, setMessages] = useState([WELCOME])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [draft, setDraft]       = useState(null)
  const bottomRef               = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const msg = text || input.trim()
    if (!msg || loading) return
    setInput('')
    setMessages(m => [...m, { role: 'user', text: msg }])
    setLoading(true)

    try {
      const res = await agentQuery(sessionId, msg)
      setMessages(m => [...m, {
        role: 'agent',
        text: res.response_text,
        citations: res.citations ?? [],
        draft: res.draft_document,
      }])
      if (res.draft_document) setDraft(res.draft_document)
    } catch (e) {
      setMessages(m => [...m, {
        role: 'agent',
        text: `⚠ Agent unreachable (${e.message}). Ensure the Agentic AI service is running on port 8001.`,
        citations: [],
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Title bar */}
      <div className="flex items-center justify-between px-space-base py-space-xs border-b border-border-subtle bg-surface-container-low flex-shrink-0">
        <div className="flex items-center gap-space-xs">
          <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
          <span className="font-label-caps text-label-caps text-on-surface-variant tracking-wider">WALLETRACE AGENT</span>
          {loading && <span className="font-code-sm text-code-sm text-primary animate-pulse">thinking…</span>}
        </div>
        <div className="flex gap-space-xs">
          {SUGGESTIONS.slice(0, 2).map(s => (
            <button key={s} onClick={() => send(s)} disabled={loading} className="font-code-sm text-code-sm text-outline border border-border-subtle px-space-xs py-space-2xs rounded hover:text-on-surface hover:border-primary transition-colors truncate max-w-[180px]">
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-space-base py-space-sm flex flex-col gap-space-sm min-h-0">
        {messages.map((m, i) => (
          <div key={i} className={`flex flex-col gap-space-2xs max-w-[85%] ${m.role === 'user' ? 'self-end items-end' : 'self-start items-start'}`}>
            <div className={`px-space-sm py-space-xs rounded-xl font-body-sm text-body-sm leading-relaxed ${
              m.role === 'user'
                ? 'bg-gradient-to-br from-primary to-secondary text-surface'
                : 'bg-surface-container border border-border-subtle text-on-surface'
            }`}>
              {m.text}
            </div>
            {m.citations?.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {m.citations.map((c, j) => (
                  <span key={j} className="font-code-sm text-code-sm bg-surface-container-high border border-border-subtle text-outline px-space-xs py-space-2xs rounded">
                    [{c.tool}] {c.summary?.slice(0, 40)}…
                  </span>
                ))}
              </div>
            )}
            {m.draft && (
              <button onClick={() => setDraft(m.draft)} className="font-code-sm text-code-sm text-secondary border border-secondary/30 bg-status-success-bg px-space-xs py-space-2xs rounded hover:bg-secondary/20 transition-colors">
                📄 View Draft Legal Notice
              </button>
            )}
          </div>
        ))}
        {loading && (
          <div className="self-start flex gap-1 px-space-sm py-space-xs bg-surface-container border border-border-subtle rounded-xl">
            {[0,1,2].map(i => (
              <span key={i} className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: `${i*0.15}s` }} />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-space-sm px-space-base py-space-sm border-t border-border-subtle flex-shrink-0 bg-surface-container-low/50">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about the investigation…"
          className="flex-1 bg-surface-container border border-border-subtle rounded-lg px-space-sm py-space-xs font-body-sm text-body-sm text-on-surface placeholder:text-on-surface-variant/50 outline-none focus:border-primary transition-colors"
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || loading}
          className="px-space-base py-space-xs bg-primary text-on-primary font-body-medium text-body-medium font-bold rounded-lg disabled:opacity-40 hover:brightness-110 transition-all active:scale-95"
        >
          Send
        </button>
      </div>

      {/* Draft modal */}
      {draft && (
        <div className="fixed inset-0 z-50 bg-surface-lowest/80 backdrop-blur-sm flex items-center justify-center p-space-base" onClick={() => setDraft(null)}>
          <div className="bg-surface-container-low border border-border-strong rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-space-xl py-space-md border-b border-border-subtle">
              <span className="font-title-sm text-title-sm font-bold text-on-surface">Draft Legal Notice</span>
              <span className="font-label-caps text-label-caps text-status-warning bg-status-warning-bg border border-status-warning/30 px-space-xs py-space-2xs rounded">DRAFT — NOT SIGNED</span>
            </div>
            <div className="flex-1 overflow-y-auto p-space-xl">
              <pre className="font-code-sm text-code-sm text-on-surface-variant whitespace-pre-wrap leading-relaxed bg-surface-container p-space-base rounded-lg border border-border-subtle">{draft}</pre>
            </div>
            <div className="flex justify-end gap-space-sm px-space-xl py-space-md border-t border-border-subtle">
              <button onClick={() => { navigator.clipboard?.writeText(draft) }} className="px-space-base py-space-sm border border-border-subtle text-on-surface-variant rounded-lg font-body-medium text-body-medium hover:bg-surface-container transition-colors">Copy</button>
              <button onClick={() => setDraft(null)} className="px-space-base py-space-sm bg-surface-container-high text-on-surface rounded-lg font-body-medium text-body-medium hover:bg-surface-container-highest transition-colors">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
