// src/components/Header.jsx — CryptoSentinel Command Center Header
import React, { useState, useEffect } from 'react'
import { blockchainHealth, mlHealth, cyberHealth, agentHealth } from '../services/api'

const SERVICES = [
  { key: 'blockchain', label: 'BLOCKCHAIN', fn: blockchainHealth },
  { key: 'ml',         label: 'ML ENGINE',  fn: mlHealth         },
  { key: 'cyber',      label: 'CYBER INTEL',fn: cyberHealth      },
  { key: 'agent',      label: 'AGENT',      fn: agentHealth      },
]

export default function Header({ activeView, userRole, onOpenLogin }) {
  const [statuses, setStatuses] = useState({})
  const [time, setTime]         = useState(new Date())

  useEffect(() => {
    const fetchStatus = async () => {
      const results = {}
      await Promise.all(SERVICES.map(async s => {
        try { await s.fn(); results[s.key] = 'ok' }
        catch { results[s.key] = 'err' }
      }))
      setStatuses(results)
    }
    fetchStatus()
    const si = setInterval(fetchStatus, 30000)
    const ti = setInterval(() => setTime(new Date()), 1000)
    return () => { clearInterval(si); clearInterval(ti) }
  }, [])

  return (
    <header className="cs-header">
      {/* Logo */}
      <div className="cs-logo">
        CRYPTO<span>SENTINEL</span>
      </div>

      {/* Subtitle */}
      <div style={{ fontSize: '.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', letterSpacing: '.08em', marginLeft: '.5rem' }}>
        MHA I4C · SIH-26183
      </div>

      {/* Service health pills */}
      <div className="cs-header-status" style={{ gap: '.5rem' }}>
        {SERVICES.map(s => (
          <div key={s.key} className="cs-header-pill">
            <span className={`status-dot ${statuses[s.key] === 'ok' ? 'green' : statuses[s.key] === 'err' ? 'red' : 'amber'}`} />
            {s.label}
          </div>
        ))}
      </div>

      {/* Clock */}
      <div style={{ marginLeft: 'auto', fontFamily: 'var(--font-mono)', fontSize: '.72rem', color: 'var(--text-secondary)' }}>
        {time.toISOString().replace('T', ' ').substring(0, 19)} UTC
      </div>

      {/* Role badge */}
      <button
        onClick={onOpenLogin}
        style={{
          marginLeft: '.75rem',
          padding: '.3rem .8rem',
          borderRadius: '20px',
          border: '1px solid rgba(34,211,238,.3)',
          background: 'rgba(34,211,238,.08)',
          color: 'var(--cyan-400)',
          fontFamily: 'var(--font-mono)',
          fontSize: '.68rem',
          fontWeight: '600',
          cursor: 'pointer',
          letterSpacing: '.05em',
          display: 'flex',
          alignItems: 'center',
          gap: '.4rem',
        }}
      >
        <span>🔐</span>
        {userRole ? userRole.toUpperCase() : 'SIGN IN'}
      </button>
    </header>
  )
}
