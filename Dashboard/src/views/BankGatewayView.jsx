// src/views/BankGatewayView.jsx
// Simulated Bank Gateway — demonstrates how WalletTrace intercepts a fraud transaction
// Design sourced from the reference HTML provided by the user
import React, { useState, useEffect, useRef } from 'react'

const TOTAL_SECS = 8 * 60 + 42
const CIRC = 2 * Math.PI * 42

export default function BankGatewayView() {
  const [secs, setSecs]               = useState(TOTAL_SECS)
  const [showModal, setModal]         = useState(false)
  const [syncPercent, setSyncPercent] = useState(0)
  const intervalRef                   = useRef(null)

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setSecs(s => (s <= 0 ? 0 : s - 1))
    }, 1000)
    return () => clearInterval(intervalRef.current)
  }, [])

  // Sync count-up animation on load (0 to 100% over 800ms)
  useEffect(() => {
    let startTimestamp = null
    const duration = 800
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setSyncPercent(Math.round(eased * 100))
      if (progress < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [])

  const mm = String(Math.floor(secs / 60)).padStart(2, '0')
  const ss = String(secs % 60).padStart(2, '0')
  const progress = secs / TOTAL_SECS
  const dashOffset = CIRC * (1 - progress)

  const isReverted = secs <= 0
  const isUrgent   = secs <= 60 && !isReverted
  const timerRingColor = isReverted ? '#10b981' : isUrgent ? '#ea580c' : '#93000a'

  return (
    <div className="w-full bg-consumer-surface rounded-xl shadow-xl overflow-hidden text-consumer-text-primary">

      {/* Sandbox interlock bar */}
      <div className="bg-surface-elevated text-on-surface px-space-base py-space-xs flex flex-wrap items-center justify-between gap-space-sm font-code-sm text-code-sm">
        <div className="flex items-center gap-space-sm">
          <span className="inline-flex items-center px-space-xs py-space-2xs rounded bg-status-warning-bg text-status-warning font-label-caps text-label-caps">
            SANDBOX INTERLOCK ACTIVE
          </span>
          <span className="text-on-surface-variant">TARGET SYSTEM: CBS-CORE-AXIS-FED-SIMULATOR v4.19</span>
        </div>
        <div className="flex items-center gap-space-md text-primary">
          <span className="flex items-center gap-space-xs">
            <span className="w-2 h-2 rounded-full bg-secondary animate-ping" />
            REAL-TIME HOOK: NCRP-GATEWAY #1930
          </span>
          <span className="text-on-surface-variant font-label-caps text-label-caps tracking-wider">RESPONSE LATENCY: 2.1s</span>
        </div>
      </div>

      {/* Consumer bank header */}
      <header className="bg-consumer-surface px-space-xl py-space-md shadow-sm flex flex-wrap items-center justify-between gap-space-base">
        <div className="flex items-center gap-space-md">
          <div className="w-10 h-10 rounded-lg bg-surface-base flex items-center justify-center shadow-sm">
            <span className="text-primary text-xl">🏦</span>
          </div>
          <div>
            <div className="flex items-center gap-space-xs">
              <span className="font-headline-md text-headline-md font-bold tracking-tight text-consumer-text-primary">APEX COMMERCIAL BANK</span>
              <span className="px-space-xs py-space-2xs rounded bg-surface-container-high text-primary font-label-caps text-label-caps">INSTITUTIONAL</span>
            </div>
            <p className="font-body-sm text-body-sm text-consumer-text-secondary">Official Retail &amp; Corporate Internet Banking Platform • RBI Regulated</p>
          </div>
        </div>
        <div className="flex items-center gap-space-lg">
          <div className="hidden sm:flex items-center gap-space-xs px-space-sm py-space-xs bg-status-success-bg text-on-secondary-container rounded-full font-code-sm text-code-sm">
            <span className="text-sm">🔒</span>
            <span className="font-medium">256-Bit TLS Extended Validation</span>
          </div>
          <div className="flex items-center gap-space-sm bg-consumer-bg py-space-xs px-space-sm rounded-lg">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-surface font-bold">AP</div>
            <div className="text-left">
              <div className="font-body-medium text-body-medium font-semibold text-consumer-text-primary leading-tight">Aarav Patel</div>
              <div className="font-code-sm text-code-sm text-consumer-text-secondary">A/C **4821 • Premier Wealth</div>
            </div>
          </div>
        </div>
      </header>

      {/* Intercept ribbon with slide-down animation */}
      <div className={`px-space-xl py-space-md flex items-start sm:items-center justify-between gap-space-base shadow-inner animate-slide-down transition-colors duration-500 ${
        isReverted
          ? 'bg-status-success-bg text-secondary border-b border-secondary/30'
          : 'bg-error-container text-on-error-container'
      }`}>
        <div className="flex items-start sm:items-center gap-space-md">
          <div className="w-10 h-10 rounded-full bg-on-error-container/20 flex items-center justify-center shrink-0 text-xl">
            {isReverted ? '✅' : '⚖️'}
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-space-xs">
              <span className="font-title-sm text-title-sm font-bold tracking-tight">
                {isReverted
                  ? 'TRANSACTION RESOLVED — REGULATORY HOLD EXPIRED & FUNDS RESTORED'
                  : 'TRANSACTION SUSPENDED — SUSPECTED FRAUD RING INTERCEPT'}
              </span>
              <span className={`px-space-xs py-space-2xs rounded font-label-caps text-label-caps uppercase ${
                isReverted
                  ? 'bg-secondary text-surface'
                  : 'bg-on-error-container text-error-container'
              }`}>
                {isReverted ? 'Sec. 91 Auto-Reversion' : 'NCRP Section 91 Trigger'}
              </span>
            </div>
            <p className="font-body-sm text-body-sm opacity-90 mt-space-2xs">
              {isReverted
                ? 'Statutory escrow timer concluded. Funds of ₹12,18,450.00 have been safely returned to your primary account without deduction.'
                : 'National Cybercrime Reporting Portal (MHA-I4C) flag detected on outbound destination settlement route. Escrow safety protocols engaged.'}
            </p>
          </div>
        </div>
        <div className="hidden lg:flex flex-col text-right shrink-0">
          <span className="font-label-caps text-label-caps uppercase tracking-wider opacity-80">Telemetry Feed</span>
          <span className="font-code-base text-code-base font-bold">
            {isReverted ? 'HOLD-AUTO-RESOLVED' : 'I4C-INTERLOCK-LIVE'}
          </span>
        </div>
      </div>

      {/* Main grid */}
      <div className="p-space-xl grid grid-cols-1 xl:grid-cols-12 gap-space-xl bg-consumer-bg">

        {/* Left 8 cols */}
        <div className="xl:col-span-8 flex flex-col gap-space-lg">

          {/* Countdown card */}
          <div className="bg-consumer-surface rounded-xl p-space-xl shadow-sm flex flex-col md:flex-row items-center justify-between gap-space-lg relative overflow-hidden">
            <div className={`absolute -right-12 -top-12 w-48 h-48 rounded-full pointer-events-none transition-colors duration-500 ${
              isReverted ? 'bg-status-success-bg/40' : 'bg-status-danger-bg'
            }`} />
            <div className="flex items-center gap-space-lg z-10">
              {/* SVG countdown ring with color shift */}
              <div className="relative w-24 h-24 shrink-0 flex items-center justify-center">
                <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="#E2E8F0" strokeWidth="8" />
                  <circle
                    cx="50" cy="50" r="42" fill="none"
                    stroke={timerRingColor} strokeWidth="8"
                    strokeDasharray={`${CIRC.toFixed(2)}`}
                    strokeDashoffset={dashOffset.toFixed(2)}
                    strokeLinecap="round"
                    style={{ transition: 'stroke-dashoffset 1s linear, stroke 0.5s ease' }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className={`font-display-lg text-headline-lg font-bold tracking-tight transition-colors duration-300 ${
                    isReverted ? 'text-secondary' : isUrgent ? 'text-status-warning' : 'text-consumer-text-primary'
                  }`}>{mm}:{ss}</span>
                  <span className="font-label-caps text-label-caps text-consumer-text-secondary">
                    {isReverted ? 'RESTORED' : 'REMAINING'}
                  </span>
                </div>
              </div>
              <div className="space-y-space-xs">
                <div className={`inline-flex items-center gap-space-xs px-space-xs py-space-2xs rounded font-label-caps text-label-caps uppercase transition-colors ${
                  isReverted
                    ? 'bg-status-success-bg text-secondary'
                    : 'bg-status-danger-bg text-error-container'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${isReverted ? 'bg-secondary' : 'bg-error-container animate-pulse'}`} />
                  {isReverted ? 'Escrow Window Resolved' : 'Temporary Regulatory Hold in Effect'}
                </div>
                <h2 className="font-headline-md text-headline-md font-bold text-consumer-text-primary tracking-tight">
                  {isReverted ? 'Funds Restored to Account **4821' : 'Auto-Reversion Escrow Window'}
                </h2>
                <p className="font-body-base text-body-base text-consumer-text-secondary max-w-lg">
                  {isReverted
                    ? 'The 8-minute regulatory clearance interval completed. The outbound transfer was safely reversed into your checking account.'
                    : 'If unverified within the remaining timeframe, funds will be automatically recalled and restored to account **4821 without penalty.'}
                </p>
              </div>
            </div>
            <div className="flex md:flex-col items-end justify-center shrink-0 z-10 text-right">
              <span className="font-label-caps text-label-caps text-consumer-text-secondary uppercase">Hold Reference ID</span>
              <span className="font-code-base text-code-base font-bold text-consumer-text-primary">TXN-HOLD-9812-NCRP</span>
              <span className={`font-body-sm text-body-sm font-semibold mt-space-2xs flex items-center gap-1 ${
                isReverted ? 'text-secondary' : 'text-status-warning'
              }`}>
                <span className="inline-block animate-lock-shake">🔒</span>
                <span>{isReverted ? 'Escrow State: RESTORED' : 'Escrow State: LOCKED'}</span>
              </span>
            </div>
          </div>

          {/* Transaction dossier */}
          <div className="bg-consumer-surface rounded-xl p-space-xl shadow-sm">
            <div className="flex items-center justify-between mb-space-base pb-space-sm">
              <div className="flex items-center gap-space-xs">
                <span className="text-consumer-text-secondary text-lg">🧾</span>
                <h3 className="font-title-sm text-title-sm font-bold text-consumer-text-primary">Outbound Transaction Specification</h3>
              </div>
              <span className="font-code-sm text-code-sm text-consumer-text-secondary">26 Oct 2026, 14:01:22 IST</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-space-base mb-space-lg">
              <div className="p-space-base rounded-lg bg-consumer-bg">
                <span className="font-label-caps text-label-caps text-consumer-text-secondary uppercase block mb-space-2xs">Held Amount</span>
                <div className="flex items-baseline gap-space-xs">
                  <span className="font-display-lg text-display-lg font-bold text-consumer-text-primary">₹12,18,450.00</span>
                  <span className="font-code-sm text-code-sm text-consumer-text-secondary">(~14,500 USDT eq.)</span>
                </div>
                <span className="font-body-sm text-body-sm text-consumer-text-secondary mt-space-xs block">IMPS/RTGS Rapid Crypto Liquidity Channel</span>
              </div>
              <div className="p-space-base rounded-lg bg-consumer-bg">
                <span className="font-label-caps text-label-caps text-consumer-text-secondary uppercase block mb-space-2xs">Designated Settlement Counterparty</span>
                <div className="font-title-sm text-title-sm font-semibold text-consumer-text-primary">Crypto Gateway Settlement</div>
                <div className="font-body-sm text-body-sm text-consumer-text-secondary mt-space-2xs">TRC-20 Liquidity Pool Deposit Bridge</div>
                <div className="mt-space-xs flex items-center gap-space-xs">
                  <span className="font-code-sm text-code-sm font-semibold text-consumer-text-primary bg-consumer-surface px-space-xs py-space-2xs rounded">MEMO / DEST: TX9p...wK3L</span>
                  <span className="text-error-container text-lg" title="Flagged Address">⚠️</span>
                </div>
              </div>
            </div>

            {/* I4C notice */}
            <div className="bg-status-danger-bg p-space-base rounded-lg mb-space-lg">
              <div className="flex items-start gap-space-sm">
                <span className="text-error-container text-2xl shrink-0 mt-space-2xs">🛡️</span>
                <div className="space-y-space-2xs">
                  <span className="font-label-caps text-label-caps font-bold text-error-container uppercase tracking-wider">
                    MHA Cyber Crime Coordination Centre (I4C) Notice
                  </span>
                  <p className="font-body-base text-body-base text-consumer-text-primary leading-relaxed">
                    An automated fraud intercept was requested via the <strong>Ministry of Home Affairs Cyber Crime Coordination Centre (I4C)</strong>. The destination settlement wallet <code className="font-code-sm text-code-sm font-bold">TX9p8k...wK3L</code> has been positively identified as an unverified mule/peel node directly linked to active NCRP extortion complaint <strong className="text-error-container">#1930-DL-88219</strong>.
                  </p>
                  <p className="font-body-sm text-body-sm text-consumer-text-secondary italic">
                    Funds are secured in statutory banking escrow under Section 91 CrPC compliance to prevent irreversible cross-border conversion.
                  </p>
                </div>
              </div>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-space-md pt-space-xs">
              <button
                onClick={() => setModal(true)}
                className="flex-1 bg-error-container hover:opacity-90 active:scale-[0.99] text-on-error px-space-lg py-space-base rounded-lg font-title-sm text-title-sm font-bold flex items-center justify-center gap-space-sm shadow-md transition-all"
              >
                <span>🚫</span>
                <span>I Did Not Authorize This • Cancel &amp; Secure Account</span>
              </button>
              <button
                onClick={() => alert('Notice: Proceeding requires formal Video KYC identification and biometric submission under Section 91 statutory clearance.')}
                className="bg-surface-raised hover:bg-surface-elevated text-on-surface px-space-base py-space-base rounded-lg font-body-medium text-body-medium font-semibold flex items-center justify-center gap-space-xs transition-colors"
              >
                <span>✅</span>
                <span>Confirm Legitimate P2P Transfer (Requires Video KYC)</span>
              </button>
            </div>

            {/* Helpline */}
            <div className="mt-space-lg pt-space-md flex flex-wrap items-center justify-between gap-space-sm font-body-sm text-body-sm text-consumer-text-secondary">
              <div className="flex items-center gap-space-xs">
                <span>📞</span>
                <span>Immediate Helpline:</span>
                <a href="tel:1930" className="font-title-sm text-title-sm font-bold text-consumer-text-primary hover:underline">National Cyber Helpline: 1930</a>
                <span>(Toll-Free, 24x7)</span>
              </div>
              <div className="flex items-center gap-space-xs">
                <span>🎧</span>
                <span>Apex Fraud Desk: 1800-419-5959</span>
              </div>
            </div>
          </div>

          {/* Forensic route geometry */}
          <div className="bg-consumer-surface rounded-xl p-space-lg shadow-sm">
            <div className="flex items-center justify-between mb-space-md">
              <div>
                <span className="font-label-caps text-label-caps text-consumer-text-secondary uppercase">Forensic Route Geometry</span>
                <h4 className="font-title-sm text-title-sm font-bold text-consumer-text-primary">Detected Transaction Flow &amp; Choke Point</h4>
              </div>
              <span className="px-space-xs py-space-2xs rounded bg-status-danger-bg text-error-container font-code-sm text-code-sm font-bold">High Risk Velocity</span>
            </div>

            <div className="bg-consumer-bg p-space-base rounded-lg flex flex-col md:flex-row items-center justify-between gap-space-md">
              {/* Node 1 */}
              <div className="flex flex-col items-center text-center w-full md:w-1/4">
                <div className="w-12 h-12 rounded-full bg-secondary-container text-consumer-surface flex items-center justify-center text-2xl mb-space-2xs shadow-sm">💼</div>
                <span className="font-body-medium text-body-medium font-semibold text-consumer-text-primary">Account **4821</span>
                <span className="font-code-sm text-code-sm text-consumer-text-secondary">Source Retail A/C</span>
                <span className="text-secondary-container font-label-caps text-label-caps mt-space-2xs">Funds Held Safe</span>
              </div>
              {/* Arrow */}
              <div className="flex md:flex-col items-center justify-center text-error-container">
                <span className="text-2xl font-bold">→</span>
                <span className="font-code-sm text-code-sm font-bold">₹12.18L</span>
              </div>
              {/* Node 2 — intercept */}
              <div className="flex flex-col items-center text-center w-full md:w-1/4 p-space-sm bg-status-danger-bg rounded-lg">
                <div className="w-12 h-12 rounded-full bg-error-container text-on-error flex items-center justify-center text-2xl mb-space-2xs shadow-sm">⚖️</div>
                <span className="font-body-medium text-body-medium font-bold text-error-container">ESCROW CHOKEPOINT</span>
                <span className="font-code-sm text-code-sm text-consumer-text-secondary">Bank &amp; NCRP Filter</span>
                <span className="px-space-xs py-space-2xs rounded bg-error-container text-on-error font-label-caps text-label-caps mt-space-2xs">Active Intercept</span>
              </div>
              {/* Arrow — blocked */}
              <div className="flex md:flex-col items-center justify-center text-consumer-text-secondary opacity-60">
                <span className="text-2xl">→</span>
                <span className="font-label-caps text-label-caps">BLOCKED</span>
              </div>
              {/* Node 3 */}
              <div className="flex flex-col items-center text-center w-full md:w-1/4 opacity-75">
                <div className="w-12 h-12 rounded-full bg-surface-base text-error flex items-center justify-center text-2xl mb-space-2xs">💱</div>
                <span className="font-body-medium text-body-medium font-semibold text-consumer-text-primary">Mule Peel Cluster</span>
                <span className="font-code-sm text-code-sm text-consumer-text-secondary">TRC20: TX9p...wK3L</span>
                <span className="text-error-container font-label-caps text-label-caps mt-space-2xs">Blacklisted Entity</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right 4 cols */}
        <div className="xl:col-span-4 flex flex-col gap-space-lg">

          {/* WalletTrace Interlock card */}
          <div className="bg-surface-base text-on-surface rounded-xl p-space-lg shadow-md flex flex-col justify-between relative overflow-hidden">
            <div className="flex items-center justify-between pb-space-sm mb-space-sm">
              <div className="flex items-center gap-space-xs">
                <span className="w-2.5 h-2.5 rounded-full bg-primary animate-ping" />
                <span className="font-title-sm text-title-sm font-bold tracking-tight text-primary">WalletTrace ™ Interlock</span>
              </div>
              <span className="px-space-xs py-space-2xs rounded bg-surface-container-high text-secondary font-label-caps text-label-caps tabular-nums">
                SYNC: {syncPercent}%
              </span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mb-space-base">
              Cryptographic handshake active between Bank Core Banking Switch and Central Law Enforcement Case Management System.
            </p>
            <div className="space-y-space-sm font-code-sm text-code-sm">
              {[
                ['Associated Case ID:', '#NCRP-2026-9812'],
                ['Investigating Unit:', 'MHA I4C Cyber Cell Zone 4'],
                ['Forensic Hash:', '0x7c9b2...8f31'],
                ['Lead Officer:', 'Insp. R. Sharma (Badge #1930)'],
                ['Interlock Directive:', 'Sec. 91 Statutory Freeze'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between p-space-xs bg-surface-container-low rounded">
                  <span className="text-on-surface-variant">{k}</span>
                  <span className={`font-bold truncate max-w-[140px] ${k === 'Interlock Directive:' ? 'text-error' : k === 'Forensic Hash:' ? 'text-primary' : 'text-on-surface'}`}>{v}</span>
                </div>
              ))}
            </div>
            <div className="mt-space-lg p-space-sm bg-surface-container-highest rounded-lg flex items-center gap-space-sm">
              <span className="text-secondary text-2xl">✓</span>
              <div className="text-left">
                <div className="font-label-caps text-label-caps text-secondary uppercase font-bold">Evidentiary Chain Maintained</div>
                <div className="font-code-sm text-code-sm text-on-surface-variant">Audit Trail Stored in SEC-Vault #882</div>
              </div>
            </div>
          </div>

          {/* Officer advisory note — live incoming dispatch slide-in */}
          <div
            className="bg-consumer-surface rounded-xl p-space-lg shadow-sm animate-slide-in-right"
            style={{ animationDelay: '300ms' }}
          >
            <div className="flex items-center gap-space-sm mb-space-sm">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-surface font-bold">RS</div>
              <div>
                <h4 className="font-title-sm text-title-sm font-bold text-consumer-text-primary flex items-center gap-2">
                  <span>Officer Advisory Note</span>
                  <span className="px-1.5 py-0.5 rounded bg-status-danger-bg text-error-container font-label-caps text-[9px] uppercase tracking-wider">LIVE DISPATCH</span>
                </h4>
                <p className="font-body-sm text-body-sm text-consumer-text-secondary">Direct Dispatch • Cyber Cell New Delhi</p>
              </div>
            </div>
            <blockquote className="bg-consumer-bg p-space-sm rounded-lg font-body-base text-body-base text-consumer-text-primary italic mb-space-base">
              "Consumer alert: This transfer matches known Telegram task/investment fraud syndicates channeling fiat through crypto P2P aggregators. If you were coached via phone to approve this, DO NOT proceed."
            </blockquote>
            <div className="space-y-space-xs">
              {[
                'Your account credentials have NOT been compromised',
                'No fees or penalties apply to this regulatory escrow',
                'Instant FIR acknowledgement will be dispatched via SMS',
              ].map(t => (
                <div key={t} className="flex items-center gap-space-xs text-consumer-text-secondary font-body-sm text-body-sm">
                  <span className="text-status-warning">✓</span>
                  <span>{t}</span>
                </div>
              ))}
            </div>
          </div>

          {/* FAQ drawer */}
          <div className="bg-consumer-surface rounded-xl p-space-lg shadow-sm">
            <h4 className="font-title-sm text-title-sm font-bold text-consumer-text-primary mb-space-sm">Consumer Protection FAQs</h4>
            <div className="space-y-space-xs font-body-sm text-body-sm">
              {[
                ['Why was my money stopped?', 'WalletTrace detected an active blacklisted crypto-mule cluster associated with nationwide fraud complaints. Under Section 91, financial institutions must prevent fund dissipation.'],
                ['When will I get my money back?', 'If you click \'Cancel & Secure Account\' or allow the timer to expire, funds will revert immediately into your primary checking account.'],
                ['What if this is a genuine transaction?', 'You may request verification by submitting mandatory Video KYC and counterparty identity declaration, subject to Cyber Cell NOC.'],
              ].map(([q, a]) => (
                <details key={q} className="group p-space-xs bg-consumer-bg rounded cursor-pointer">
                  <summary className="font-semibold text-consumer-text-primary flex justify-between items-center list-none">
                    <span>{q}</span>
                    <span className="group-open:rotate-180 transition-transform">▾</span>
                  </summary>
                  <p className="text-consumer-text-secondary mt-space-2xs pt-space-2xs">{a}</p>
                </details>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Success modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-surface-container-lowest/80 backdrop-blur-sm flex items-center justify-center p-space-base">
          <div className="bg-consumer-surface rounded-xl max-w-lg w-full p-space-xl shadow-2xl text-consumer-text-primary relative animate-in">
            <div className="w-16 h-16 rounded-full bg-status-success-bg mx-auto flex items-center justify-center mb-space-base text-4xl">🛡️</div>
            <h3 className="font-headline-md text-headline-md font-bold text-center mb-space-xs">Transfer Canceled &amp; Funds Protected</h3>
            <p className="font-body-base text-body-base text-consumer-text-secondary text-center mb-space-lg">
              The transaction of <strong className="text-consumer-text-primary">₹12,18,450.00</strong> has been successfully revoked. The amount is fully credited back to account <strong>**4821</strong>.
            </p>
            <div className="bg-consumer-bg p-space-base rounded-lg mb-space-lg font-code-sm text-code-sm space-y-space-2xs">
              {[
                ['Incident Reference:', 'INC-REVOKE-88192-DELHI'],
                ['Status:', 'SECURED & RECORDED'],
                ['SMS Receipt Dispatched:', '+91 98*** **410'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between">
                  <span className="text-consumer-text-secondary">{k}</span>
                  <span className={`font-bold ${k === 'Status:' ? 'text-secondary-container' : ''}`}>{v}</span>
                </div>
              ))}
            </div>
            <button
              onClick={() => setModal(false)}
              className="w-full bg-surface-base hover:bg-surface-elevated text-on-surface py-space-base rounded-lg font-title-sm text-title-sm font-semibold transition-colors"
            >
              Return to Account Overview
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
