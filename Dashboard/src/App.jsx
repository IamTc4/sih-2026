// src/App.jsx — CryptoSentinel Command Center Root
import React, { useState } from 'react'
import Header           from './components/Header'
import Sidebar          from './components/Sidebar'
import LoginModal       from './components/LoginModal'
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

const VIEW_LABELS = {
  'investigation':  'Wallet Investigation',
  'multichain':     'Multi-Chain Inspector',
  'batch':          'Fraud Ring Analysis',
  'evidence-intake':'Evidence Intake (NCRP & OCR)',
  'active-cases':   'Active Cases Registry',
  'upi-bridge':     'UPI → Crypto Bridge',
  'threat-map':     'Live Threat Intel Feed',
  'legal-notice':   'Section 91 BNSS Legal Notice',
  'bank-gateway':   'Exchange Gateway',
  'audit-trail':    'Evidence Chain (Hash-Verified)',
  'model-info':     'ML Model Transparency Card',
}

export default function App() {
  const [view, setView]           = useState('investigation')
  const [selectedWallet, setSelectedWallet] = useState(null)
  const [showLogin, setShowLogin] = useState(false)
  const [user, setUser]           = useState(null)

  const handleLaunchInvestigation = (wallet) => {
    setSelectedWallet(wallet)
    setView('investigation')
  }

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const renderView = () => {
    switch (view) {
      case 'investigation':
        return <InvestigationView initialWallet={selectedWallet} userRole={user?.role} />
      case 'multichain':
        return <MultiChainView />
      case 'batch':
        return <BatchInvestigationView />
      case 'evidence-intake':
        return <div className="cs-view"><EvidenceIntakeView onLaunchInvestigation={handleLaunchInvestigation} /></div>
      case 'active-cases':
        return <div className="cs-view"><ActiveCasesView onSelectCase={handleLaunchInvestigation} /></div>
      case 'upi-bridge':
        return <div className="cs-view"><UPIBridgeView /></div>
      case 'threat-map':
        return <ThreatMapView />
      case 'legal-notice':
        return <div className="cs-view"><LegalNoticeView initialWallet={selectedWallet || 'T_VICTIM_SIH_DEMO_999'} /></div>
      case 'bank-gateway':
        return <div className="cs-view" style={{ padding: '1.5rem' }}><BankGatewayView /></div>
      case 'audit-trail':
        return <div className="cs-view"><AuditTrailView /></div>
      case 'model-info':
        return <div className="cs-view"><ModelInfoView /></div>
      default:
        return <InvestigationView />
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', background: 'var(--bg-void)', color: 'var(--text-primary)', fontFamily: 'var(--font-sans)' }}>
      <Header
        activeView={view}
        userRole={user?.role}
        onOpenLogin={() => setShowLogin(true)}
      />
      <Sidebar active={view} onNav={setView} />

      {/* Main content */}
      <div style={{ marginLeft: 'var(--sidebar-w)', paddingTop: 'var(--header-h)', height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Breadcrumb */}
        <div style={{
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '.5rem',
          padding: '.4rem 1.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          background: 'rgba(6,12,20,.9)',
          fontFamily: 'var(--font-mono)',
          fontSize: '.68rem',
          color: 'var(--text-muted)',
          backdropFilter: 'blur(8px)',
        }}>
          <span style={{ color: 'var(--text-muted)' }}>CRYPTOSENTINEL</span>
          <span style={{ opacity: .4 }}>›</span>
          <span style={{ color: 'var(--cyan-400)', fontWeight: '600', letterSpacing: '.05em' }}>
            {VIEW_LABELS[view]?.toUpperCase()}
          </span>
          {user && (
            <>
              <span style={{ marginLeft: 'auto' }} />
              <span className="cs-tag cs-tag-cyan" style={{ marginLeft: 'auto' }}>
                🔐 {user.label} · {user.clearance}
              </span>
            </>
          )}
        </div>

        {/* View */}
        <div style={{ flex: 1, overflow: 'hidden auto' }}>
          {renderView()}
        </div>
      </div>

      {/* Login Modal */}
      {showLogin && (
        <LoginModal
          onLogin={handleLogin}
          onClose={() => setShowLogin(false)}
        />
      )}
    </div>
  )
}
