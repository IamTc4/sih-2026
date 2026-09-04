// src/views/ActiveCasesView.jsx
// Case Management View (PRD FR9: assign, track, review, and close cyber complaints)
import React, { useState } from 'react'

const MOCK_CASES = [
  {
    id: 'CASE-2024-001',
    ncrp_ack: 'NCRP-2024-MH-89210',
    victim: 'Rajesh Kumar Sharma',
    amount: '45,000 USDT',
    suspect_wallet: 'T_VICTIM_SIH_DEMO_999',
    exchange: 'Binance',
    risk: 0.88,
    status: 'NOTICE_DRAFTED',
    io: 'Insp. Vikram Rathore',
    date: '2026-09-04',
  },
  {
    id: 'CASE-2024-002',
    ncrp_ack: 'NCRP-2024-DL-11029',
    victim: 'Priya Sundaram',
    amount: '12,500 USDT',
    suspect_wallet: 'T_LAZARUS_MIXER_01',
    exchange: 'Huobi',
    risk: 0.96,
    status: 'FUNDS_FROZEN',
    io: 'Sub-Insp. Neha Verma',
    date: '2026-09-03',
  },
  {
    id: 'CASE-2024-003',
    ncrp_ack: 'NCRP-2024-KA-44182',
    victim: 'Anand K. Hegde',
    amount: '8,200 USDT',
    suspect_wallet: 'TMOCK_CDEF15_HOP1',
    exchange: 'OKX',
    risk: 0.74,
    status: 'UNDER_TRACING',
    io: 'Insp. Vikram Rathore',
    date: '2026-09-02',
  },
  {
    id: 'CASE-2024-004',
    ncrp_ack: 'NCRP-2024-GJ-90231',
    victim: 'Kavita Patel',
    amount: '60,000 USDT',
    suspect_wallet: 'T_RANSOMWARE_AFFILIATE_99',
    exchange: 'CoinSwitch',
    risk: 0.92,
    status: 'MANUAL_REVIEW',
    io: 'ACP S. K. Joshi',
    date: '2026-09-01',
  }
]

export default function ActiveCasesView({ onSelectCase }) {
  const [cases, setCases] = useState(MOCK_CASES)
  const [filter, setFilter] = useState('ALL')

  const filtered = filter === 'ALL' ? cases : cases.filter(c => c.status === filter)

  return (
    <div className="p-space-base max-w-6xl mx-auto flex flex-col gap-space-base">
      <div className="flex items-center justify-between border-b border-border-subtle pb-space-xs">
        <div>
          <h2 className="font-headline-md text-headline-md font-bold text-on-surface flex items-center gap-2">
            <span>📁</span> Active Cyber Crime Cases (NCRP Registry)
          </h2>
          <p className="font-body-base text-on-surface-variant text-sm mt-1">
            Real-time tracking of crypto fraud complaints, assigned investigating officers (IOs), and multi-hop trace status.
          </p>
        </div>
        <div className="flex gap-2">
          {['ALL', 'UNDER_TRACING', 'NOTICE_DRAFTED', 'FUNDS_FROZEN'].map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`text-xs px-3 py-1.5 rounded font-bold transition-colors ${
                filter === s
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-surface-container-low border border-border-subtle rounded-lg overflow-hidden">
        <table className="w-full text-left text-xs text-on-surface">
          <thead className="bg-surface-container border-b border-border-subtle text-outline font-label-caps uppercase tracking-wider">
            <tr>
              <th className="p-3">Case ID</th>
              <th className="p-3">Victim & Fraud Type</th>
              <th className="p-3">Suspect Wallet</th>
              <th className="p-3">Loss (USDT)</th>
              <th className="p-3">Terminal Exchange</th>
              <th className="p-3">Risk</th>
              <th className="p-3">Status</th>
              <th className="p-3">IO Assigned</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {filtered.map(c => (
              <tr key={c.id} className="hover:bg-surface-container transition-colors">
                <td className="p-3 font-mono font-bold text-primary">{c.id}</td>
                <td className="p-3">
                  <div className="font-bold text-on-surface">{c.victim}</div>
                  <div className="text-outline text-[10px]">{c.ncrp_ack}</div>
                </td>
                <td className="p-3 font-mono text-[11px] text-secondary">{c.suspect_wallet}</td>
                <td className="p-3 font-bold">{c.amount}</td>
                <td className="p-3 font-bold text-on-surface">{c.exchange}</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded font-bold ${c.risk > 0.85 ? 'bg-error/20 text-error' : 'bg-warning/20 text-warning'}`}>
                    {(c.risk * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface font-bold text-[10px]">
                    {c.status}
                  </span>
                </td>
                <td className="p-3 text-on-surface-variant">{c.io}</td>
                <td className="p-3 text-right">
                  <button
                    onClick={() => onSelectCase && onSelectCase(c.suspect_wallet)}
                    className="bg-primary hover:bg-primary-hover text-on-primary font-bold px-3 py-1 rounded text-xs transition-colors"
                  >
                    Investigate
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
