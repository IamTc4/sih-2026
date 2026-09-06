// src/components/Sidebar.jsx — CryptoSentinel Dark SOC Sidebar
import React from 'react'

const NAV = [
  // ── Tactical Operations
  { id: 'investigation',   label: 'Investigation',          icon: '🔍', group: 'TACTICAL OPS' },
  { id: 'multichain',      label: 'Multi-Chain Inspector',  icon: '⛓️', group: 'TACTICAL OPS', badge: 'NEW' },
  { id: 'batch',           label: 'Fraud Ring Analysis',    icon: '🕸️', group: 'TACTICAL OPS', badge: 'NEW' },
  { id: 'evidence-intake', label: 'Evidence Intake (NCRP)', icon: '📷', group: 'TACTICAL OPS' },
  { id: 'upi-bridge',      label: 'UPI → Crypto Bridge',   icon: '🏦', group: 'TACTICAL OPS', badge: 'NEW' },
  { id: 'active-cases',    label: 'Active Cases',           icon: '📂', group: 'TACTICAL OPS', badge: '4' },
  // ── Intelligence
  { id: 'threat-map',      label: 'Threat Intel Feed',      icon: '🛡️', group: 'INTELLIGENCE', badge: 'LIVE' },
  // ── Legal
  { id: 'legal-notice',    label: 'Legal Notice (§91 BNSS)',icon: '⚖️', group: 'LEGAL' },
  { id: 'bank-gateway',    label: 'Exchange Gateway',       icon: '🏛️', group: 'LEGAL' },
  // ── Compliance
  { id: 'audit-trail',     label: 'Evidence Chain',         icon: '🔗', group: 'COMPLIANCE' },
  { id: 'model-info',      label: 'ML Model Card',          icon: '🧠', group: 'COMPLIANCE' },
]

export default function Sidebar({ active, onNav }) {
  const groups = [...new Set(NAV.map(n => n.group))]

  return (
    <aside className="cs-sidebar">
      <div>
        {groups.map(grp => (
          <div key={grp} className="cs-nav-group">
            <div className="cs-nav-group-label">{grp}</div>
            {NAV.filter(n => n.group === grp).map(n => (
              <button
                key={n.id}
                onClick={() => onNav(n.id)}
                className={`cs-nav-item ${active === n.id ? 'active' : ''}`}
              >
                <span style={{ fontSize: '.9rem' }}>{n.icon}</span>
                <span style={{ flex: 1, textAlign: 'left' }}>{n.label}</span>
                {n.badge && (
                  <span className={`cs-nav-badge ${n.badge === 'LIVE' ? 'alert' : ''}`}>
                    {n.badge}
                  </span>
                )}
              </button>
            ))}
          </div>
        ))}
      </div>

      {/* Station integrity */}
      <div style={{ margin: '0 .75rem', padding: '.75rem', background: 'var(--bg-input)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.6rem', color: 'var(--text-muted)', letterSpacing: '.1em', marginBottom: '.3rem' }}>
          STATION INTEGRITY
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.7rem', color: 'var(--emerald-400)', fontWeight: '600' }}>
          ✓ CHAIN VERIFIED
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.65rem', color: 'var(--text-muted)', marginTop: '.2rem' }}>
          SIH-26183 · v2.0
        </div>
      </div>
    </aside>
  )
}
