// src/components/LoginModal.jsx — RBAC Role Selector for Demo
import React, { useState } from 'react'

const ROLES = [
  {
    id: 'investigator',
    label: 'Lead Investigator',
    icon: '🕵️',
    clearance: 'TOP SECRET',
    desc: 'Full access: victim PII, legal notices, evidence trail. Can initiate freeze requests.',
    token: 'investigator:inv_officer_001',
    color: 'var(--red-400)',
  },
  {
    id: 'analyst',
    label: 'Crypto Analyst',
    icon: '📊',
    clearance: 'CONFIDENTIAL',
    desc: 'Read public + internal data. Write analysis notes. Cannot access victim PII.',
    token: 'analyst:analyst_001',
    color: 'var(--amber-400)',
  },
  {
    id: 'viewer',
    label: 'Reviewing Officer',
    icon: '👁️',
    clearance: 'PUBLIC',
    desc: 'Read-only access to public data: graphs, risk scores, attribution. No PII.',
    token: 'viewer:viewer_001',
    color: 'var(--emerald-400)',
  },
  {
    id: 'admin',
    label: 'System Administrator',
    icon: '⚙️',
    clearance: 'ADMIN',
    desc: 'Full system access + user management. Evidence chain administration.',
    token: 'admin:admin_001',
    color: 'var(--purple-400)',
  },
]

export default function LoginModal({ onLogin, onClose }) {
  const [selected, setSelected] = useState(null)

  const handleLogin = () => {
    if (!selected) return
    const role = ROLES.find(r => r.id === selected)
    onLogin({ role: role.id, label: role.label, token: role.token, clearance: role.clearance })
    onClose()
  }

  return (
    <div className="cs-modal-backdrop" onClick={onClose}>
      <div className="cs-modal" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div className="cs-modal-title">🔐 CryptoSentinel Access Control</div>
          <div className="cs-modal-subtitle">
            Select your role to enable role-based data access (RBAC).
            Each role has different clearance levels per MHA I4C security policy.
          </div>
        </div>

        {/* Roles */}
        {ROLES.map(role => (
          <div
            key={role.id}
            className={`cs-role-card ${selected === role.id ? 'selected' : ''}`}
            onClick={() => setSelected(role.id)}
          >
            <div className="cs-role-icon" style={{ background: `${role.color}18`, borderColor: `${role.color}30` }}>
              {role.icon}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginBottom: '.2rem' }}>
                <span className="fw-600 text-sm">{role.label}</span>
                <span className="cs-tag" style={{
                  background: `${role.color}18`,
                  color: role.color,
                  border: `1px solid ${role.color}30`,
                }}>{role.clearance}</span>
              </div>
              <div className="text-xs text-muted">{role.desc}</div>
            </div>
            {selected === role.id && (
              <span style={{ color: 'var(--cyan-400)', fontSize: '1.1rem' }}>✓</span>
            )}
          </div>
        ))}

        <div className="cs-divider" />

        {/* Actions */}
        <div style={{ display: 'flex', gap: '.75rem', justifyContent: 'flex-end' }}>
          <button className="cs-btn cs-btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="cs-btn cs-btn-primary"
            onClick={handleLogin}
            disabled={!selected}
          >
            Authenticate as {selected ? ROLES.find(r => r.id === selected)?.label : '...'}
          </button>
        </div>

        <div className="text-xs text-muted" style={{ marginTop: '.75rem', textAlign: 'center' }}>
          Demo mode: all roles bypass real JWT validation · Data redaction is enforced by the Cybersecurity API
        </div>
      </div>
    </div>
  )
}
