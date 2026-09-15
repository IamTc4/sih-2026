// src/components/DemoCaseCard.jsx
// Three dramatic pre-canned demo case picker cards
import React from 'react'

const CASES = [
  {
    id: 'A',
    wallet: 'T_VICTIM_SIH_DEMO_999',
    type: 'Romance Scam',
    amount: '₹1.2L',
    hops: 3,
    risk: 'CRITICAL',
    riskColor: 'text-error border-error/30 bg-status-danger-bg',
    lineColor: 'from-error/30 to-transparent',
    tagColor: 'text-error',
    desc: 'Victim sent USDT to a "girlfriend" on Instagram. Funds vanished in 3 hops.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    id: 'B',
    wallet: 'T_VICTIM_SIH_DEMO_TRADING',
    type: 'Fake Trading App',
    amount: '₹77L',
    hops: 4,
    risk: 'HIGH',
    riskColor: 'text-error border-error/20 bg-status-danger-bg/60',
    lineColor: 'from-status-warning/30 to-transparent',
    tagColor: 'text-status-warning',
    desc: '₹77L laundered through dual-layer mixing before hitting exchange deposit.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="currentColor" strokeWidth="1.5">
        <path d="M3 3v18h18" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M7 16l4-4 4 4 4-8" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    id: 'C',
    wallet: 'T_VICTIM_SIH_DEMO_OTP',
    type: 'OTP Fraud',
    amount: '₹8,500',
    hops: 3,
    risk: 'MEDIUM',
    riskColor: 'text-status-warning border-status-warning/30 bg-status-warning-bg',
    lineColor: 'from-secondary/20 to-transparent',
    tagColor: 'text-secondary',
    desc: 'Classic 2-mule chain from OTP phishing. Exchange identified, KYC required.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="w-7 h-7" stroke="currentColor" strokeWidth="1.5">
        <rect x="5" y="2" width="14" height="20" rx="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 18h.01" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M9 8h6M9 12h4" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
]

export default function DemoCaseCard({ onLaunch }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 px-6">
      {/* Title */}
      <div className="text-center">
        <div className="text-4xl opacity-10 mb-3 font-headline-lg">⬡</div>
        <p className="font-headline-md text-headline-md text-on-surface font-bold mb-1">Select a Case to Investigate</p>
        <p className="font-code-sm text-code-sm text-outline/70">Live demo — pick a scenario or enter your own wallet address above</p>
      </div>

      {/* Case cards */}
      <div className="flex gap-4 w-full max-w-3xl">
        {CASES.map(c => (
          <button
            key={c.id}
            id={`demo-case-${c.id.toLowerCase()}`}
            onClick={() => onLaunch(c.wallet)}
            className="card-lift flex-1 flex flex-col text-left bg-surface-container border border-border-subtle rounded-xl p-4 cursor-pointer hover:border-primary/50 transition-all group"
          >
            {/* Top row */}
            <div className="flex items-start justify-between mb-3">
              <div className={`p-2 rounded-lg bg-surface-container-high ${c.tagColor} group-hover:scale-110 transition-transform`}>
                {c.icon}
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className="font-label-caps text-label-caps text-outline/60">CASE {c.id}</span>
                <span className={`font-label-caps text-label-caps px-2 py-0.5 rounded border ${c.riskColor}`}>
                  {c.risk}
                </span>
              </div>
            </div>

            {/* Type + desc */}
            <div className="font-title-sm text-title-sm text-on-surface font-bold mb-1 group-hover:text-primary transition-colors">
              {c.type}
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant/70 leading-relaxed mb-3 flex-1">
              {c.desc}
            </p>

            {/* Stats row */}
            <div className="flex items-center gap-3 mb-3">
              <div className="flex items-center gap-1">
                <span className="font-code-sm text-code-sm text-outline/60">AMT</span>
                <span className="font-code-sm text-code-sm text-primary font-bold">{c.amount}</span>
              </div>
              <div className="w-px h-3 bg-border-subtle" />
              <div className="flex items-center gap-1">
                <span className="font-code-sm text-code-sm text-outline/60">HOPS</span>
                <span className="font-code-sm text-code-sm text-primary font-bold">{c.hops}</span>
              </div>
            </div>

            {/* Wallet address chip */}
            <div className="bg-surface-container-high px-2 py-1.5 rounded-lg border border-border-subtle/50">
              <div className="font-code-sm text-code-sm text-outline/60 text-[10px] mb-0.5">WALLET</div>
              <div className="font-code-sm text-code-sm text-on-surface-variant truncate text-[11px]">{c.wallet}</div>
            </div>

            {/* Launch button */}
            <div className="mt-3 flex items-center justify-center gap-2 bg-primary/10 border border-primary/20 rounded-lg py-2 group-hover:bg-primary/20 transition-colors">
              <span className="font-code-sm text-code-sm text-primary font-bold">Launch Investigation</span>
              <span className="text-primary text-sm group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
