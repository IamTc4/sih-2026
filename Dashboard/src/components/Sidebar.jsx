// src/components/Sidebar.jsx
import React from 'react'

const NAV = [
  { id: 'investigation',  label: 'Investigation View',       group: 'TACTICAL OPERATIONS' },
  { id: 'active-cases',   label: 'Active Cases',             group: 'TACTICAL OPERATIONS', badge: '14' },
  { id: 'forensic-graph', label: 'Forensic Graph',           group: 'TACTICAL OPERATIONS' },
  { id: 'exchange-intel', label: 'Exchange Intelligence',    group: 'TACTICAL OPERATIONS' },
  { id: 'evidence-vault', label: 'Evidence Vault',           group: 'TACTICAL OPERATIONS' },
  { id: 'bank-gateway',   label: 'Simulated Bank Gateway',   group: 'SIMULATION & SANDBOX' },
  { id: 'audit-trail',    label: 'Audit Trail Ledger',       group: 'SIMULATION & SANDBOX' },
  { id: 'model-info',     label: 'ML Model Card',            group: 'SIMULATION & SANDBOX' },
]

export default function Sidebar({ active, onNav }) {
  const groups = [...new Set(NAV.map(n => n.group))]
  return (
    <aside className="fixed left-0 top-20 bottom-0 w-sidebar-compact bg-surface-container-low z-40 flex flex-col justify-between py-space-md overflow-y-auto">
      <div className="flex flex-col gap-space-base">
        {groups.map(grp => (
          <div key={grp} className="px-space-base">
            <span className="font-label-caps text-label-caps text-outline tracking-wider block mb-space-xs">{grp}</span>
            <nav className="flex flex-col gap-space-2xs">
              {NAV.filter(n => n.group === grp).map(n => (
                <button
                  key={n.id}
                  onClick={() => onNav(n.id)}
                  className={`flex items-center justify-between px-space-sm py-space-sm transition-colors font-body-medium text-body-medium rounded w-full text-left ${
                    active === n.id
                      ? 'bg-primary-container text-on-primary-container font-bold'
                      : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
                  }`}
                >
                  <span>{n.label}</span>
                  {n.badge && (
                    <span className="font-code-sm text-code-sm px-space-xs py-space-2xs bg-surface-container-highest text-primary font-bold rounded">
                      {n.badge}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>
        ))}
      </div>

      {/* Station integrity */}
      <div className="mx-space-sm px-space-base py-space-sm bg-surface-container-lowest rounded mt-space-base">
        <div className="font-label-caps text-label-caps text-on-surface-variant">STATION INTEGRITY</div>
        <div className="font-code-sm text-code-sm text-secondary font-bold">CHAIN-OF-CUSTODY VERIFIED</div>
        <div className="font-code-sm text-code-sm text-outline mt-space-2xs">KEY ID: 0x882B...DF19</div>
      </div>
    </aside>
  )
}
