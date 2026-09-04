// src/App.jsx — WalletTrace Dashboard root
import React, { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import InvestigationView from './views/InvestigationView'
import BankGatewayView   from './views/BankGatewayView'
import AuditTrailView    from './views/AuditTrailView'
import ModelInfoView     from './views/ModelInfoView'
import EvidenceIntakeView from './views/EvidenceIntakeView'
import ActiveCasesView    from './views/ActiveCasesView'
import LegalNoticeView    from './views/LegalNoticeView'

const VIEW_LABELS = {
  'investigation':    'Investigation View',
  'evidence-intake':  'Evidence Intake (NCRP & OCR)',
  'active-cases':     'Active Cases Registry',
  'legal-notice':     'Section 91 CrPC Notice',
  'bank-gateway':     'Simulated Bank Gateway',
  'audit-trail':      'Audit Trail Ledger',
  'model-info':       'ML Model Transparency Card',
}

export default function App() {
  const [view, setView] = useState('investigation')
  const [selectedWallet, setSelectedWallet] = useState(null)

  const handleLaunchInvestigation = (wallet) => {
    setSelectedWallet(wallet)
    setView('investigation')
  }

  const renderView = () => {
    switch (view) {
      case 'investigation':    return <InvestigationView initialWallet={selectedWallet} />
      case 'evidence-intake':  return <div className="overflow-y-auto h-full"><EvidenceIntakeView onLaunchInvestigation={handleLaunchInvestigation} /></div>
      case 'active-cases':     return <div className="overflow-y-auto h-full"><ActiveCasesView onSelectCase={handleLaunchInvestigation} /></div>
      case 'legal-notice':     return <div className="overflow-y-auto h-full"><LegalNoticeView initialWallet={selectedWallet || 'T_VICTIM_SIH_DEMO_999'} /></div>
      case 'bank-gateway':     return <div className="overflow-y-auto h-full"><div className="p-space-base"><BankGatewayView /></div></div>
      case 'audit-trail':      return <div className="overflow-y-auto h-full"><AuditTrailView /></div>
      case 'model-info':       return <div className="overflow-y-auto h-full"><ModelInfoView /></div>
      default:                 return <InvestigationView />
    }
  }

  return (
    <div className="dark min-h-screen bg-bg-app font-body-base text-body-base text-on-surface antialiased">
      <Header activeView={view} />
      <Sidebar active={view} onNav={setView} />

      {/* Content offset for fixed header + sidebar */}
      <div className="pl-sidebar-compact pt-20 h-screen flex flex-col overflow-hidden">
        {/* Breadcrumb bar */}
        <div className="flex-shrink-0 flex items-center gap-space-xs px-space-base py-space-xs bg-surface-container-low/50 border-b border-border-subtle">
          <span className="font-label-caps text-label-caps text-outline tracking-wider">WALLETTRACE</span>
          <span className="text-outline">›</span>
          <span className="font-label-caps text-label-caps text-primary tracking-wider">{VIEW_LABELS[view]?.toUpperCase()}</span>
        </div>

        {/* Main view area */}
        <div className="flex-1 min-h-0 overflow-hidden">
          {renderView()}
        </div>
      </div>
    </div>
  )
}
