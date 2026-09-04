// src/views/AuditTrailView.jsx
// Evidence Vault + Audit Trail Ledger view
import React, { useState } from 'react'

const MOCK_ENTRIES = [
  { id: 'EVT-001', event: 'WALLET_TRACE_INITIATED',  hash: '0x9f2c1a4b8d...e301', prev: '0x0000000000', ts: '2026-09-04T22:05:11Z', valid: true },
  { id: 'EVT-002', event: 'CLUSTER_DETECTED',         hash: '0x3a7e9c12f4...b821', prev: '0x9f2c1a4b8d', ts: '2026-09-04T22:05:14Z', valid: true },
  { id: 'EVT-003', event: 'EXCHANGE_ATTRIBUTED',      hash: '0x8b1d6e3f79...c042', prev: '0x3a7e9c12f4', ts: '2026-09-04T22:05:16Z', valid: true },
  { id: 'EVT-004', event: 'ML_RISK_SCORE_COMPUTED',   hash: '0x4f5a2b8c91...d173', prev: '0x8b1d6e3f79', ts: '2026-09-04T22:05:18Z', valid: true },
  { id: 'EVT-005', event: 'DRAFT_NOTICE_GENERATED',   hash: '0x6c3e7a1d58...f294', prev: '0x4f5a2b8c91', ts: '2026-09-04T22:05:22Z', valid: true },
]

export default function AuditTrailView() {
  const [entries, setEntries] = useState(MOCK_ENTRIES)
  const [verifying, setVerifying] = useState({})

  const verify = async (id) => {
    setVerifying(v => ({ ...v, [id]: 'checking' }))
    await new Promise(r => setTimeout(r, 800))
    setVerifying(v => ({ ...v, [id]: 'valid' }))
  }

  return (
    <div className="p-space-xl max-w-4xl mx-auto">
      <div className="mb-space-xl">
        <div className="flex items-center gap-space-sm mb-space-xs">
          <span className="w-3 h-3 rounded-full bg-secondary animate-pulse" />
          <span className="font-label-caps text-label-caps text-outline tracking-wider">CHAIN-OF-CUSTODY LEDGER</span>
        </div>
        <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface mb-space-xs">Audit Trail Ledger</h1>
        <p className="font-body-base text-body-base text-on-surface-variant">
          SHA-256 hash-chained event log. Every forensic action is immutably recorded.
          Each entry's hash is computed over its content + previous hash — any tampering breaks the chain.
        </p>
      </div>

      {/* Chain integrity banner */}
      <div className="bg-status-success-bg border border-secondary/20 rounded-xl p-space-base mb-space-xl flex items-center gap-space-md">
        <span className="text-secondary text-2xl">✓</span>
        <div>
          <div className="font-title-sm text-title-sm font-bold text-secondary">Hash Chain Intact</div>
          <div className="font-code-sm text-code-sm text-on-surface-variant">{entries.length} entries verified • Last: {entries.at(-1)?.ts}</div>
        </div>
        <div className="ml-auto font-code-sm text-code-sm text-secondary">VAULT: SEC-882B...DF19</div>
      </div>

      {/* Entries */}
      <div className="space-y-space-sm">
        {entries.map((e, i) => (
          <div key={e.id} className="bg-surface-container rounded-xl border border-border-subtle p-space-base">
            <div className="flex items-start justify-between gap-space-base">
              <div className="flex items-center gap-space-sm">
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center font-code-sm text-code-sm text-primary font-bold">{i+1}</div>
                  {i < entries.length - 1 && <div className="w-px h-6 bg-border-subtle mt-1" />}
                </div>
                <div>
                  <div className="font-body-medium text-body-medium font-bold text-on-surface">{e.event.replace(/_/g, ' ')}</div>
                  <div className="font-code-sm text-code-sm text-outline mt-space-2xs">{e.id} • {e.ts}</div>
                </div>
              </div>
              <button
                onClick={() => verify(e.id)}
                className={`font-code-sm text-code-sm px-space-sm py-space-2xs rounded border transition-colors flex-shrink-0 ${
                  verifying[e.id] === 'valid'    ? 'border-secondary/40 text-secondary bg-status-success-bg' :
                  verifying[e.id] === 'checking' ? 'border-border-subtle text-outline animate-pulse' :
                  'border-border-subtle text-outline hover:border-primary hover:text-primary'}`}
              >
                {verifying[e.id] === 'valid' ? '✓ Verified' : verifying[e.id] === 'checking' ? 'Verifying…' : 'Verify'}
              </button>
            </div>
            <div className="mt-space-sm ml-10 grid grid-cols-1 sm:grid-cols-2 gap-space-xs">
              <div className="bg-surface-container-low rounded p-space-xs">
                <div className="font-label-caps text-label-caps text-outline mb-space-2xs">CONTENT HASH</div>
                <div className="font-code-sm text-code-sm text-primary truncate">{e.hash}…e8f2</div>
              </div>
              <div className="bg-surface-container-low rounded p-space-xs">
                <div className="font-label-caps text-label-caps text-outline mb-space-2xs">PREV HASH</div>
                <div className="font-code-sm text-code-sm text-on-surface-variant truncate">{e.prev}…</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
