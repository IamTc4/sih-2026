// src/components/Sidebar.jsx — CryptoSentinel Command Center
// Glowing active item, grouped nav, rotating integrity hash
import React, { useState, useEffect } from 'react'

const NAV = [
  // ── Stage 1: Case Intake & Corridor ──────────────────────────
  { id: 'upi-bridge',      label: '1. UPI → Crypto Bridge', icon: '💳', group: 'STAGE 1: INTAKE', badge: 'START' },
  { id: 'evidence-intake', label: 'Evidence OCR & Ingestion', icon: '📄', group: 'STAGE 1: INTAKE' },
  { id: 'active-cases',    label: 'Active Cases Registry',   icon: '📁', group: 'STAGE 1: INTAKE', badge: '4' },

  // ── Stage 2: Blockchain Forensics ────────────────────────────
  { id: 'investigation',   label: '2. Graph & AI Trace',     icon: '⬡', group: 'STAGE 2: FORENSICS' },
  { id: 'multichain',      label: 'Multi-Chain Inspector',   icon: '⛓', group: 'STAGE 2: FORENSICS' },
  { id: 'batch',           label: 'Mule Ring Clustering',    icon: '◈', group: 'STAGE 2: FORENSICS', badge: 'NEW' },

  // ── Stage 3: Live Threat & Prevention ────────────────────────
  { id: 'threat-map',      label: '3. Threat Intel Feed',    icon: '🛰', group: 'STAGE 3: PREVENTION' },
  { id: 'bank-gateway',    label: 'Bank Gateway (1930 Hold)',icon: '🏦', group: 'STAGE 3: PREVENTION' },

  // ── Stage 4: Legal Freeze & Court Dossier ────────────────────
  { id: 'legal-notice',    label: '4. Section 91 BNSS Freeze',icon: '⚖', group: 'STAGE 4: ENFORCEMENT' },
  { id: 'audit-trail',     label: '5. Hash Evidence Chain',  icon: '🔐', group: 'STAGE 4: ENFORCEMENT' },
  { id: 'model-info',      label: 'ML Model Transparency',   icon: '🧠', group: 'STAGE 4: ENFORCEMENT' },

  // ── System Intelligence ───────────────────────────────────────
  { id: 'system-intel',    label: 'System Intelligence',     icon: '⚙', group: 'SYSTEM INTELLIGENCE', badge: 'INFO' },
]

const HASHES = [
  '0x882B…DF19', '0xA3C1…E702', '0x5F8D…9B44',
  '0x1E4A…C835', '0xD7B2…4F61', '0xC990…A17E',
]

export default function Sidebar({ active, onNav, open = true }) {
  const groups = [...new Set(NAV.map(n => n.group))]
  const [hashIdx, setHashIdx] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setHashIdx(i => (i + 1) % HASHES.length), 8000)
    return () => clearInterval(t)
  }, [])

  if (!open) return null

  return (
    <aside style={{
      position: 'fixed',
      left: 0,
      top: 'var(--header-h, 60px)',
      bottom: 0,
      width: 'var(--sidebar-w, 220px)',
      background: '#000000',
      zIndex: 40,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      padding: '1rem 0',
      overflowY: 'auto',
      borderRight: '1px solid rgba(34,211,238,0.08)',
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {groups.map(grp => (
          <div key={grp} style={{ padding: '0 .75rem' }}>
            <span style={{
              display: 'block',
              fontSize: '.6rem',
              fontFamily: 'var(--font-mono)',
              letterSpacing: '.12em',
              color: 'rgba(255,255,255,0.28)',
              marginBottom: '.5rem',
              paddingLeft: '.5rem',
            }}>
              {grp}
            </span>
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              {NAV.filter(n => n.group === grp).map(n => {
                const isActive = active === n.id
                return (
                  <button
                    key={n.id}
                    id={`nav-${n.id}`}
                    onClick={() => onNav(n.id)}
                    style={{
                      position: 'relative',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '.55rem .75rem',
                      borderRadius: '8px',
                      border: 'none',
                      cursor: 'pointer',
                      textAlign: 'left',
                      width: '100%',
                      transition: 'all .18s ease',
                      background: isActive
                        ? 'rgba(34,211,238,0.10)'
                        : 'transparent',
                      color: isActive
                        ? 'var(--cyan-400, #22d3ee)'
                        : 'rgba(255,255,255,0.55)',
                      fontWeight: isActive ? 600 : 400,
                      fontSize: '.78rem',
                      fontFamily: 'var(--font-sans)',
                      boxShadow: isActive
                        ? 'inset 0 0 12px rgba(34,211,238,0.06)'
                        : 'none',
                    }}
                    onMouseEnter={e => {
                      if (!isActive) {
                        e.currentTarget.style.background = 'rgba(255,255,255,0.05)'
                        e.currentTarget.style.color = 'rgba(255,255,255,0.85)'
                      }
                    }}
                    onMouseLeave={e => {
                      if (!isActive) {
                        e.currentTarget.style.background = 'transparent'
                        e.currentTarget.style.color = 'rgba(255,255,255,0.55)'
                      }
                    }}
                  >
                    {/* Active indicator bar */}
                    {isActive && (
                      <div style={{
                        position: 'absolute',
                        left: 0,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        width: '3px',
                        height: '60%',
                        background: 'var(--cyan-400, #22d3ee)',
                        borderRadius: '0 2px 2px 0',
                        boxShadow: '0 0 8px rgba(34,211,238,0.6)',
                      }} />
                    )}

                    <div style={{ display: 'flex', alignItems: 'center', gap: '.6rem' }}>
                      <span style={{ fontSize: '.85rem', opacity: isActive ? 1 : 0.6, flexShrink: 0 }}>
                        {n.icon}
                      </span>
                      <span style={{ lineHeight: 1.2 }}>{n.label}</span>
                    </div>

                    {n.badge && (
                      <span style={{
                        fontSize: '.58rem',
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 700,
                        padding: '.15rem .4rem',
                        borderRadius: '4px',
                        flexShrink: 0,
                        background: n.badge === 'NEW'
                          ? 'rgba(167,139,250,0.18)'
                          : 'rgba(34,211,238,0.12)',
                        color: n.badge === 'NEW'
                          ? 'var(--purple-400, #a78bfa)'
                          : 'var(--cyan-400, #22d3ee)',
                        border: `1px solid ${n.badge === 'NEW' ? 'rgba(167,139,250,0.3)' : 'rgba(34,211,238,0.2)'}`,
                      }}>
                        {n.badge}
                      </span>
                    )}
                  </button>
                )
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Station integrity footer */}
      <div style={{
        margin: '0 .75rem',
        padding: '.75rem',
        background: 'rgba(0,0,0,0.3)',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.06)',
        marginTop: '1rem',
      }}>
        <div style={{
          fontSize: '.58rem',
          fontFamily: 'var(--font-mono)',
          letterSpacing: '.1em',
          color: 'rgba(255,255,255,0.25)',
          marginBottom: '.4rem',
        }}>STATION INTEGRITY</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginBottom: '.35rem' }}>
          <span style={{
            width: '6px', height: '6px', borderRadius: '50%',
            background: '#10b981', flexShrink: 0,
            boxShadow: '0 0 6px #10b981',
            animation: 'pulse 2s infinite',
          }} />
          <span style={{
            fontSize: '.62rem',
            fontFamily: 'var(--font-mono)',
            color: '#10b981',
            fontWeight: 700,
          }}>CHAIN-OF-CUSTODY VERIFIED</span>
        </div>
        <div style={{
          fontSize: '.58rem',
          fontFamily: 'var(--font-mono)',
          color: 'rgba(255,255,255,0.2)',
          transition: 'all .5s ease',
        }}>
          KEY: {HASHES[hashIdx]}
        </div>
      </div>
    </aside>
  )
}
