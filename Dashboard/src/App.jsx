// src/App.jsx — WalletTrace Dashboard root
import React, { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import InvestigationView from './views/InvestigationView'
import BankGatewayView   from './views/BankGatewayView'
import AuditTrailView    from './views/AuditTrailView'
import ModelInfoView     from './views/ModelInfoView'

const VIEW_LABELS = {
  'investigation':  'Investigation View',
  'active-cases':   'Active Cases',
  'forensic-graph': 'Forensic Graph',
  'exchange-intel': 'Exchange Intelligence',
  'evidence-vault': 'Evidence Vault',
  'bank-gateway':   'Simulated Bank Gateway',
  'audit-trail':    'Audit Trail Ledger',
  'model-info':     'ML Model Card',
}

function PlaceholderView({ id }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-space-md text-on-surface-variant">
      <div className="text-5xl opacity-20">🔒</div>
      <h2 className="font-headline-md text-headline-md font-bold text-on-surface">{VIEW_LABELS[id]}</h2>
      <p className="font-body-base text-body-base text-center max-w-sm">
        This view is part of the full integration build.
        Go to <strong className="text-primary">Investigation View</strong> or <strong className="text-primary">Simulated Bank Gateway</strong> for live demos.
      </p>
    </div>
  )
}

export default function App() {
  const [view, setView] = useState('investigation')

  const renderView = () => {
    switch (view) {
      case 'investigation':  return <InvestigationView />
      case 'bank-gateway':   return <div className="overflow-y-auto h-full"><div className="p-space-base"><BankGatewayView /></div></div>
      case 'audit-trail':    return <div className="overflow-y-auto h-full"><AuditTrailView /></div>
      case 'model-info':     return <div className="overflow-y-auto h-full"><ModelInfoView /></div>
      default:               return <PlaceholderView id={view} />
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
