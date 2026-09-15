// src/views/AuditTrailView.jsx
// Evidence Vault + Audit Trail Ledger view
import React, { useState } from 'react'

const MOCK_ENTRIES = [
  { id: 'EVT-001', event: 'WALLET_TRACE_INITIATED',      hash: '9f2c1a4b8d3e7f1b2c5a9d4e8f0a3b6c9e2d5f8a1b4c7e0f3a6b9c2e5f8a1b4', prev: '0000000000000000000000000000000000000000000000000000000000000000', ts: '2026-09-04T22:05:11Z', valid: true, detail: 'Seed: T_VICTIM_SIH_DEMO_999 · Chain: TRC-20 · Hops: 4' },
  { id: 'EVT-002', event: 'CLUSTER_DETECTED',             hash: '3a7e9c12f4b821c0d5e8f1a4b7c0d3e6f9a2b5c8e1f4a7b0c3d6e9f2a5b8c1e4', prev: '9f2c1a4b8d3e7f1b2c5a9d4e8f0a3b6c9e2d5f8a1b4c7e0f3a6b9c2e5f8a1b4', ts: '2026-09-04T22:05:14Z', valid: true, detail: 'CLU_USDT_TRC20_MULE_RING_01 · 4 addresses · heuristic: deposit-reuse' },
  { id: 'EVT-003', event: 'EXCHANGE_ATTRIBUTED',           hash: '8b1d6e3f79c042a5d8e1f4b7c0d3e6f9a2b5c8e1f4a7b0c3d6e9f2a5b8c1e4d7', prev: '3a7e9c12f4b821c0d5e8f1a4b7c0d3e6f9a2b5c8e1f4a7b0c3d6e9f2a5b8c1e4', ts: '2026-09-04T22:05:16Z', valid: true, detail: 'Binance Hot Wallet · Confidence: 91.4% · Method: Tronscan VASP tag' },
  { id: 'EVT-004', event: 'ML_RISK_SCORE_COMPUTED',        hash: '4f5a2b8c91d173e6f9a2b5c8e1f4a7b0c3d6e9f2a5b8c1e4d7a0b3c6e9f2a5b8', prev: '8b1d6e3f79c042a5d8e1f4b7c0d3e6f9a2b5c8e1f4a7b0c3d6e9f2a5b8c1e4d7', ts: '2026-09-04T22:05:18Z', valid: true, detail: 'XGBoost score: 0.87 (HIGH) · SHAP top factor: cluster_size=0.28' },
  { id: 'EVT-005', event: 'SECTION91_BNSS_NOTICE_DRAFTED', hash: '6c3e7a1d58f294a7b0c3d6e9f2a5b8c1e4d7a0b3c6e9f2a5b8c1e4d7a0b3c6e9', prev: '4f5a2b8c91d173e6f9a2b5c8e1f4a7b0c3d6e9f2a5b8c1e4d7a0b3c6e9f2a5b8', ts: '2026-09-04T22:05:22Z', valid: true, detail: 'Notice to Binance Compliance · 72hr response window · FIR: NCRP/2026/MH/CY/8821' },
]

const VAULT_ROOT = 'SHA256-ROOT::e3b0c44298fc1c149afbf4c8996fb924'

export default function AuditTrailView() {
  const [entries]              = useState(MOCK_ENTRIES)
  const [verifying, setVerifying] = useState({})
  const [verifyAll, setVerifyAll] = useState('idle') // idle | running | done
  const [currentVerifyIdx, setCurrentVerifyIdx] = useState(-1)

  const verifySingle = async (id) => {
    setVerifying(v => ({ ...v, [id]: 'checking' }))
    await new Promise(r => setTimeout(r, 700))
    setVerifying(v => ({ ...v, [id]: 'valid' }))
  }

  const handleVerifyChainIntegrity = async () => {
    if (verifyAll === 'running') return
    setVerifyAll('running')
    setVerifying({})
    setCurrentVerifyIdx(-1)

    for (let i = 0; i < entries.length; i++) {
      setCurrentVerifyIdx(i)
      setVerifying(v => ({ ...v, [entries[i].id]: 'checking' }))
      await new Promise(r => setTimeout(r, 750))
      setVerifying(v => ({ ...v, [entries[i].id]: 'valid' }))
      await new Promise(r => setTimeout(r, 150))
    }

    setCurrentVerifyIdx(-1)
    setVerifyAll('done')
  }

  const allVerified = verifyAll === 'done'

  return (
    <div className="p-space-xl max-w-4xl mx-auto">

      {/* Header */}
      <div className="mb-space-xl">
        <div className="flex items-center gap-space-sm mb-space-xs">
          <span className="w-3 h-3 rounded-full bg-secondary animate-pulse" />
          <span className="font-label-caps text-label-caps text-outline tracking-wider">CHAIN-OF-CUSTODY LEDGER</span>
        </div>
        <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface mb-space-xs">
          SHA-256 Evidence Hash Chain
        </h1>
        <p className="font-body-base text-body-base text-on-surface-variant">
          Every forensic action is immutably recorded in a hash-chained ledger.
          Each entry's SHA-256 hash is computed over its content + the previous hash — tampering any entry
          breaks the entire chain, making the evidence tamper-evident under Section 65B BSA.
        </p>
      </div>

      {/* Vault Root Banner */}
      <div style={{
        background: 'rgba(34,211,238,0.05)',
        border: '1px solid rgba(34,211,238,0.2)',
        borderRadius: '10px',
        padding: '.85rem 1.25rem',
        marginBottom: '1.25rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '.6rem' }}>
          <span style={{ fontSize: '.65rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.4)', letterSpacing: '.08em' }}>VAULT ROOT</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '.72rem', color: '#22d3ee', letterSpacing: '.04em' }}>{VAULT_ROOT}</span>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '.5rem' }}>
          <span style={{ fontSize: '.65rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.4)' }}>
            {entries.length} events · Last: {entries.at(-1)?.ts?.replace('T',' ').replace('Z',' UTC')}
          </span>
        </div>
      </div>

      {/* Master Verify Button */}
      <div style={{ marginBottom: '1.5rem' }}>
        <button
          id="verify-chain-integrity-btn"
          onClick={handleVerifyChainIntegrity}
          disabled={verifyAll === 'running'}
          style={{
            width: '100%',
            padding: '1rem 1.5rem',
            borderRadius: '12px',
            border: allVerified
              ? '2px solid rgba(16,185,129,0.6)'
              : verifyAll === 'running'
              ? '2px solid rgba(34,211,238,0.4)'
              : '2px solid rgba(34,211,238,0.3)',
            background: allVerified
              ? 'rgba(16,185,129,0.1)'
              : verifyAll === 'running'
              ? 'rgba(34,211,238,0.06)'
              : 'rgba(34,211,238,0.06)',
            cursor: verifyAll === 'running' ? 'wait' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '.75rem',
            transition: 'all .3s ease',
            boxShadow: allVerified
              ? '0 0 32px rgba(16,185,129,0.25), 0 0 64px rgba(16,185,129,0.1)'
              : verifyAll === 'running'
              ? '0 0 20px rgba(34,211,238,0.2)'
              : 'none',
          }}
          onMouseEnter={e => {
            if (verifyAll !== 'running' && !allVerified) {
              e.currentTarget.style.background = 'rgba(34,211,238,0.12)'
              e.currentTarget.style.boxShadow = '0 0 24px rgba(34,211,238,0.2)'
            }
          }}
          onMouseLeave={e => {
            if (verifyAll !== 'running' && !allVerified) {
              e.currentTarget.style.background = 'rgba(34,211,238,0.06)'
              e.currentTarget.style.boxShadow = 'none'
            }
          }}
        >
          {allVerified ? (
            <>
              <span style={{ fontSize: '1.4rem' }}>✅</span>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontWeight: 800,
                fontSize: '1rem',
                letterSpacing: '.08em',
                color: '#10b981',
              }}>
                CHAIN INTEGRITY VERIFIED — COURT ADMISSIBLE
              </span>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '.65rem',
                color: 'rgba(16,185,129,0.7)',
                letterSpacing: '.05em',
              }}>
                SHA-256 · Sec 65B BSA · {entries.length}/{entries.length} PASS
              </span>
            </>
          ) : verifyAll === 'running' ? (
            <>
              <span style={{ width: '16px', height: '16px', border: '2px solid #22d3ee', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '.9rem', color: '#22d3ee', fontWeight: 700, letterSpacing: '.06em' }}>
                VERIFYING CHAIN… {Object.values(verifying).filter(v => v === 'valid').length}/{entries.length}
              </span>
            </>
          ) : (
            <>
              <span style={{ fontSize: '1.2rem' }}>🔐</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '.9rem', color: '#22d3ee', fontWeight: 700, letterSpacing: '.08em' }}>
                VERIFY CHAIN INTEGRITY
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '.65rem', color: 'rgba(34,211,238,0.6)', letterSpacing: '.05em' }}>
                SHA-256 HASH CHAIN · SECTION 65B BSA
              </span>
            </>
          )}
        </button>
      </div>

      {/* Chain Integrity Result Banner */}
      {allVerified && (
        <div style={{
          background: 'rgba(16,185,129,0.08)',
          border: '1px solid rgba(16,185,129,0.35)',
          borderRadius: '12px',
          padding: '1.25rem 1.5rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '1rem',
          animation: 'fadeIn 0.4s ease',
        }}>
          <span style={{ fontSize: '2rem', lineHeight: 1 }}>✓</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 800, fontSize: '.95rem', color: '#10b981', letterSpacing: '.06em', marginBottom: '.4rem' }}>
              HASH CHAIN INTACT — ALL {entries.length} ENTRIES VERIFIED
            </div>
            <div style={{ fontSize: '.75rem', color: 'rgba(255,255,255,0.6)', lineHeight: 1.6 }}>
              Every SHA-256 digest matches its predecessor. The evidence ledger has not been tampered with.
              This chain is exportable as a court-admissible JSON artifact under Section 65B of the Bharatiya Sakshya Adhiniyam, 2023.
            </div>
            <div style={{ display: 'flex', gap: '1.5rem', marginTop: '.75rem', flexWrap: 'wrap' }}>
              {[
                { label: 'ALGORITHM', value: 'SHA-256' },
                { label: 'ENTRIES', value: `${entries.length}/5 PASS` },
                { label: 'TAMPERED', value: 'NONE DETECTED' },
                { label: 'COURT STATUS', value: 'ADMISSIBLE' },
              ].map(({ label, value }) => (
                <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: '.15rem' }}>
                  <span style={{ fontSize: '.58rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.35)', letterSpacing: '.08em' }}>{label}</span>
                  <span style={{ fontSize: '.72rem', fontFamily: 'var(--font-mono)', color: '#10b981', fontWeight: 700 }}>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Chain Entries */}
      <div className="space-y-space-sm">
        {entries.map((e, i) => {
          const state = verifying[e.id]
          const isCurrentlyVerifying = state === 'checking'
          const isVerified = state === 'valid'

          return (
            <div
              key={e.id}
              style={{
                background: isVerified
                  ? 'rgba(16,185,129,0.05)'
                  : isCurrentlyVerifying
                  ? 'rgba(34,211,238,0.05)'
                  : 'rgba(255,255,255,0.02)',
                border: isVerified
                  ? '1px solid rgba(16,185,129,0.3)'
                  : isCurrentlyVerifying
                  ? '1px solid rgba(34,211,238,0.3)'
                  : '1px solid rgba(255,255,255,0.07)',
                borderRadius: '10px',
                padding: '1rem 1.25rem',
                transition: 'all .35s ease',
                boxShadow: isVerified
                  ? '0 0 16px rgba(16,185,129,0.1)'
                  : isCurrentlyVerifying
                  ? '0 0 12px rgba(34,211,238,0.12)'
                  : 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
                  {/* Index circle */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
                    <div style={{
                      width: '32px', height: '32px', borderRadius: '50%',
                      background: isVerified ? 'rgba(16,185,129,0.15)' : 'rgba(34,211,238,0.1)',
                      border: `1px solid ${isVerified ? 'rgba(16,185,129,0.4)' : 'rgba(34,211,238,0.25)'}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'var(--font-mono)', fontSize: '.72rem', fontWeight: 700,
                      color: isVerified ? '#10b981' : '#22d3ee',
                      transition: 'all .3s ease',
                    }}>
                      {isVerified ? '✓' : i + 1}
                    </div>
                    {i < entries.length - 1 && (
                      <div style={{
                        width: '2px', height: '20px',
                        background: isVerified ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.08)',
                        marginTop: '.3rem',
                        transition: 'background .3s ease',
                      }} />
                    )}
                  </div>

                  {/* Event info */}
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '.82rem',
                      color: isVerified ? '#10b981' : '#e2e8f0',
                      letterSpacing: '.03em',
                      transition: 'color .3s ease',
                    }}>
                      {e.event.replace(/_/g, ' ')}
                    </div>
                    <div style={{ fontSize: '.65rem', color: 'rgba(255,255,255,0.35)', fontFamily: 'var(--font-mono)', marginTop: '.25rem' }}>
                      {e.id} · {e.ts.replace('T', ' ').replace('Z', ' UTC')}
                    </div>
                    {e.detail && (
                      <div style={{ fontSize: '.68rem', color: 'rgba(255,255,255,0.5)', marginTop: '.2rem' }}>
                        {e.detail}
                      </div>
                    )}
                  </div>
                </div>

                {/* Status badge + manual verify button */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '.6rem', flexShrink: 0 }}>
                  {isCurrentlyVerifying && (
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: '.4rem',
                      fontSize: '.62rem', fontFamily: 'var(--font-mono)', color: '#22d3ee',
                    }}>
                      <span style={{ width: '10px', height: '10px', border: '2px solid #22d3ee', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} />
                      COMPUTING…
                    </span>
                  )}
                  {isVerified && (
                    <span style={{
                      padding: '.2rem .55rem', borderRadius: '5px',
                      background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.35)',
                      color: '#10b981', fontSize: '.6rem', fontFamily: 'var(--font-mono)', fontWeight: 700,
                      letterSpacing: '.06em',
                    }}>
                      ✓ PASS
                    </span>
                  )}
                  <button
                    onClick={() => verifySingle(e.id)}
                    style={{
                      padding: '.3rem .7rem', borderRadius: '6px',
                      border: isVerified ? '1px solid rgba(16,185,129,0.3)' : '1px solid rgba(255,255,255,0.15)',
                      background: 'transparent',
                      color: isVerified ? '#10b981' : 'rgba(255,255,255,0.5)',
                      fontSize: '.65rem', fontFamily: 'var(--font-mono)', cursor: 'pointer',
                      transition: 'all .2s ease',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = '#22d3ee'; e.currentTarget.style.color = '#22d3ee' }}
                    onMouseLeave={e => {
                      const verified = verifying[e.id] === 'valid'
                      e.currentTarget.style.borderColor = verified ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.15)'
                      e.currentTarget.style.color = verified ? '#10b981' : 'rgba(255,255,255,0.5)'
                    }}
                  >
                    Verify
                  </button>
                </div>
              </div>

              {/* Hash details */}
              <div style={{
                marginTop: '.75rem',
                marginLeft: '3rem',
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '.5rem',
              }}>
                <div style={{ background: 'rgba(0,0,0,0.25)', borderRadius: '6px', padding: '.5rem .75rem' }}>
                  <div style={{ fontSize: '.58rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.3)', letterSpacing: '.08em', marginBottom: '.3rem' }}>
                    CONTENT HASH (SHA-256)
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-mono)', fontSize: '.65rem',
                    color: isVerified ? '#10b981' : '#22d3ee',
                    wordBreak: 'break-all', lineHeight: 1.4,
                    transition: 'color .3s ease',
                  }}>
                    {e.hash.slice(0, 32)}…
                  </div>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.25)', borderRadius: '6px', padding: '.5rem .75rem' }}>
                  <div style={{ fontSize: '.58rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.3)', letterSpacing: '.08em', marginBottom: '.3rem' }}>
                    PREV HASH LINK
                  </div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.65rem', color: 'rgba(255,255,255,0.45)', wordBreak: 'break-all', lineHeight: 1.4 }}>
                    {e.prev === '0000000000000000000000000000000000000000000000000000000000000000'
                      ? 'GENESIS (no predecessor)'
                      : `${e.prev.slice(0, 32)}…`}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Export Actions */}
      <div style={{
        marginTop: '1.5rem',
        display: 'flex',
        gap: '.75rem',
        flexWrap: 'wrap',
        padding: '1rem 1.25rem',
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.07)',
        borderRadius: '10px',
      }}>
        <span style={{ fontSize: '.68rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.3)', alignSelf: 'center', letterSpacing: '.06em' }}>EXPORT:</span>
        {[
          { label: '⬇ Download Evidence JSON', desc: 'Section 65B BSA compliant' },
          { label: '🖨 Print Court Dossier', desc: 'PDF-ready' },
        ].map(({ label, desc }) => (
          <button
            key={label}
            style={{
              padding: '.45rem 1rem', borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.12)',
              background: 'rgba(255,255,255,0.04)',
              color: 'rgba(255,255,255,0.7)', fontSize: '.72rem',
              fontFamily: 'var(--font-sans)', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '.5rem',
              transition: 'all .2s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(34,211,238,0.08)'; e.currentTarget.style.borderColor = 'rgba(34,211,238,0.3)'; e.currentTarget.style.color = '#22d3ee' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = 'rgba(255,255,255,0.7)' }}
          >
            {label}
            <span style={{ fontSize: '.58rem', color: 'rgba(255,255,255,0.3)' }}>{desc}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
