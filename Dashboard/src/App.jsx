// src/App.jsx — CryptoSentinel Command Center Root
import React, { useState } from 'react'
import Header               from './components/Header'
import Sidebar              from './components/Sidebar'
import LoginModal           from './components/LoginModal'
import InvestigationView    from './views/InvestigationView'
import BankGatewayView      from './views/BankGatewayView'
import AuditTrailView       from './views/AuditTrailView'
import ModelInfoView        from './views/ModelInfoView'
import EvidenceIntakeView   from './views/EvidenceIntakeView'
import ActiveCasesView      from './views/ActiveCasesView'
import LegalNoticeView      from './views/LegalNoticeView'
import MultiChainView       from './views/MultiChainView'
import ThreatMapView        from './views/ThreatMapView'
import UPIBridgeView        from './views/UPIBridgeView'
import BatchInvestigationView from './views/BatchInvestigationView'
import SystemIntelView      from './views/SystemIntelView'

const VIEW_LABELS = {
  'upi-bridge':     'Stage 1: UPI → Crypto Investigation Bridge',
  'evidence-intake':'Stage 1: Evidence Intake (FIR OCR & Logs)',
  'active-cases':   'Stage 1: Active Cases Registry',
  'investigation':  'Stage 2: On-Chain Graph & AI Trace',
  'multichain':     'Stage 2: Multi-Chain Inspector',
  'batch':          'Stage 2: Mule Ring Clustering',
  'threat-map':     'Stage 3: Live Threat Intelligence Feed',
  'bank-gateway':   'Stage 3: Bank Gateway (NCRP 1930 Hold Intercept)',
  'legal-notice':   'Stage 4: Section 91 BNSS Statutory Requisition',
  'audit-trail':    'Stage 4: Evidence Hash Chain (Sec 65B BSA)',
  'model-info':     'Stage 4: ML Model Transparency Card',
  'system-intel':   'System Intelligence — Cyber Standards · ML Model · AI Agent',
}

const PIPELINE_STEPS = [
  { id: 'intake',      label: '1. FIR / UPI Intake',       targetView: 'upi-bridge',   views: ['upi-bridge', 'evidence-intake', 'active-cases'] },
  { id: 'forensics',   label: '2. On-Chain Graph Trace',   targetView: 'investigation',views: ['investigation', 'multichain', 'batch'] },
  { id: 'prevention',  label: '3. Bank Intercept & Threat',targetView: 'bank-gateway', views: ['bank-gateway', 'threat-map'] },
  { id: 'enforcement', label: '4. Section 91 BNSS Freeze', targetView: 'legal-notice', views: ['legal-notice'] },
  { id: 'evidence',    label: '5. Court Hash Chain',       targetView: 'audit-trail',  views: ['audit-trail', 'model-info'] },
]

export default function App() {
  const [view, setView]           = useState('upi-bridge')
  const [selectedWallet, setSelectedWallet] = useState(null)
  const [showLogin, setShowLogin] = useState(false)
  const [user, setUser]           = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLaunchInvestigation = (wallet) => {
    setSelectedWallet(wallet)
    setView('investigation')
  }

  const handleLogin = (userData) => {
    setUser(userData)
    setShowLogin(false)
  }

  const renderView = () => {
    switch (view) {
      case 'investigation':
        return <InvestigationView initialWallet={selectedWallet} userRole={user?.role} onNav={setView} />
      case 'multichain':
        return <MultiChainView onNav={setView} />
      case 'batch':
        return <BatchInvestigationView onNav={setView} />
      case 'evidence-intake':
        return <EvidenceIntakeView onLaunchInvestigation={handleLaunchInvestigation} onNav={setView} />
      case 'active-cases':
        return <ActiveCasesView onSelectCase={handleLaunchInvestigation} onNav={setView} />
      case 'upi-bridge':
        return <UPIBridgeView onLaunchInvestigation={handleLaunchInvestigation} onNav={setView} />
      case 'threat-map':
        return <ThreatMapView onNav={setView} />
      case 'legal-notice':
        return <LegalNoticeView initialWallet={selectedWallet || 'T_VICTIM_SIH_DEMO_999'} onNav={setView} />
      case 'bank-gateway':
        return <BankGatewayView onNav={setView} />
      case 'audit-trail':
        return <AuditTrailView onNav={setView} />
      case 'model-info':
        return <ModelInfoView onNav={setView} />
      case 'system-intel':
        return <SystemIntelView onNav={setView} />
      default:
        return <UPIBridgeView onLaunchInvestigation={handleLaunchInvestigation} onNav={setView} />
    }
  }

  const SIDEBAR_W = sidebarOpen ? 260 : 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', background: 'var(--bg-void)', color: 'var(--text-primary)' }}>
      <Header
        activeView={view}
        userRole={user?.role}
        onOpenLogin={() => setShowLogin(true)}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(s => !s)}
      />

      <Sidebar active={view} onNav={(v) => { setView(v) }} open={sidebarOpen} />

      {/* Main content */}
      <div style={{
        marginLeft: sidebarOpen ? 'var(--sidebar-w)' : '0',
        paddingTop: 'var(--header-h)',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        transition: 'margin-left 0.3s ease',
      }}>
        {/* Breadcrumb & Quick Info */}
        <div style={{
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '.4rem 1.25rem',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          background: 'rgba(2,4,8,.95)',
          fontFamily: 'var(--font-mono)',
          fontSize: '.68rem',
          color: 'var(--text-muted)',
          backdropFilter: 'blur(8px)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '.4rem' }}>
            <span style={{ color: 'var(--text-muted)', letterSpacing: '.08em' }}>CRYPTOSENTINEL</span>
            <span style={{ opacity: .4, margin: '0 .2rem' }}>›</span>
            <span style={{ color: 'var(--cyan-400)', fontWeight: '600', letterSpacing: '.05em' }}>
              {VIEW_LABELS[view]?.toUpperCase()}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '.75rem' }}>
            {selectedWallet && (
              <span style={{
                padding: '.15rem .5rem',
                borderRadius: '4px',
                background: 'rgba(34,211,238,0.1)',
                border: '1px solid rgba(34,211,238,0.25)',
                color: '#22d3ee',
                fontSize: '.62rem',
              }}>
                Target: {selectedWallet.slice(0, 8)}…{selectedWallet.slice(-6)}
              </span>
            )}
            {user && (
              <span style={{
                padding: '.2rem .6rem',
                borderRadius: '20px',
                border: '1px solid rgba(34,211,238,.25)',
                background: 'rgba(34,211,238,.08)',
                color: 'var(--cyan-400)',
                fontSize: '.65rem',
              }}>
                🔐 {user.label} · {user.clearance}
              </span>
            )}
          </div>
        </div>

        {/* ── Investigation Lifecycle Stepper Bar ── */}
        <div style={{
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          padding: '.45rem 1.25rem',
          background: 'rgba(10,14,24,0.92)',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          gap: '.5rem',
          overflowX: 'auto',
        }}>
          <span style={{
            fontSize: '.62rem',
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            color: 'rgba(255,255,255,0.35)',
            letterSpacing: '.08em',
            marginRight: '.25rem',
            whiteSpace: 'nowrap',
          }}>
            CASE WORKFLOW:
          </span>
          {PIPELINE_STEPS.map((step, idx) => {
            const isCurrent = step.views.includes(view)
            return (
              <React.Fragment key={step.id}>
                <button
                  onClick={() => setView(step.targetView)}
                  title={`Navigate to ${step.label}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '.4rem',
                    padding: '.28rem .65rem',
                    borderRadius: '6px',
                    border: isCurrent ? '1px solid var(--cyan-400, #22d3ee)' : '1px solid rgba(255,255,255,0.08)',
                    background: isCurrent ? 'rgba(34,211,238,0.12)' : 'rgba(255,255,255,0.02)',
                    color: isCurrent ? '#22d3ee' : 'rgba(255,255,255,0.6)',
                    fontSize: '.72rem',
                    fontFamily: 'var(--font-sans)',
                    fontWeight: isCurrent ? 700 : 400,
                    cursor: 'pointer',
                    transition: 'all .15s ease',
                    whiteSpace: 'nowrap',
                    boxShadow: isCurrent ? '0 0 10px rgba(34,211,238,0.15)' : 'none',
                  }}
                  onMouseEnter={e => {
                    if (!isCurrent) {
                      e.currentTarget.style.background = 'rgba(255,255,255,0.06)'
                      e.currentTarget.style.color = '#fff'
                    }
                  }}
                  onMouseLeave={e => {
                    if (!isCurrent) {
                      e.currentTarget.style.background = 'rgba(255,255,255,0.02)'
                      e.currentTarget.style.color = 'rgba(255,255,255,0.6)'
                    }
                  }}
                >
                  <span style={{
                    width: '15px',
                    height: '15px',
                    borderRadius: '50%',
                    background: isCurrent ? '#22d3ee' : 'rgba(255,255,255,0.12)',
                    color: isCurrent ? '#000' : 'rgba(255,255,255,0.7)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '.58rem',
                    fontWeight: 800,
                  }}>
                    {idx + 1}
                  </span>
                  <span>{step.label}</span>
                </button>
                {idx < PIPELINE_STEPS.length - 1 && (
                  <span style={{ color: 'rgba(255,255,255,0.18)', fontSize: '.68rem', userSelect: 'none' }}>→</span>
                )}
              </React.Fragment>
            )
          })}
        </div>

        {/* View */}
        <div style={{ flex: 1, overflow: 'hidden auto' }}>
          {renderView()}
        </div>
      </div>

      {showLogin && (
        <LoginModal
          onLogin={handleLogin}
          onClose={() => setShowLogin(false)}
        />
      )}
    </div>
  )
}
