// src/components/Header.jsx
import React from 'react'

export default function Header({ activeView }) {
  const now = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest/95 backdrop-blur-md">
      {/* Top status bar */}
      <div className="h-6 px-space-base bg-surface-dim flex items-center justify-between font-label-caps text-label-caps tracking-widest text-on-surface-variant">
        <div className="flex items-center gap-space-md">
          <span className="flex items-center gap-space-xs text-secondary">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" />
            RPC LIVE: TRON-MAINNET
          </span>
          <span className="text-outline">|</span>
          <span>SHA-256 HASH CHAIN: ACTIVE</span>
          <span className="text-outline">|</span>
          <span className="text-primary">SIH26183 — WALLETTRACE v1.0</span>
        </div>
        <div className="flex items-center gap-space-md font-code-sm text-code-sm">
          <span className="text-on-surface-variant">MHA I4C CYBER CELL</span>
          <span className="px-space-xs bg-error-container text-on-error-container font-label-caps text-label-caps rounded">
            SECURE CONSOLE
          </span>
        </div>
      </div>

      {/* Main header */}
      <div className="h-14 px-space-base flex items-center justify-between">
        <div className="flex items-center gap-space-md">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-surface font-bold text-sm">W</div>
          <div className="flex flex-col">
            <div className="flex items-center gap-space-sm">
              <span className="font-headline-md text-headline-md font-bold tracking-tight text-on-surface">WALLETTRACE</span>
              <span className="font-code-base text-code-base text-primary font-bold">// CYBER-COMMAND</span>
            </div>
            <span className="font-label-caps text-label-caps text-on-surface-variant tracking-wider">
              MHA CYBER FORENSICS • NATIONAL INTELLIGENCE PORTAL
            </span>
          </div>
          <div className="ml-space-md hidden lg:flex items-center gap-space-sm">
            <span className="px-space-xs py-space-2xs bg-status-danger-bg text-error font-label-caps text-label-caps rounded">
              RESTRICTED — LAW ENFORCEMENT ONLY
            </span>
            <span className="px-space-xs py-space-2xs bg-status-warning-bg text-status-warning font-label-caps text-label-caps rounded">
              ACTIVE INCIDENTS: 14 CRITICAL
            </span>
          </div>
        </div>
        <div className="flex items-center gap-space-md">
          <div className="text-right hidden sm:block">
            <div className="font-title-sm text-title-sm text-on-surface">Insp. R. Sharma</div>
            <div className="font-code-sm text-code-sm text-on-surface-variant">Cyber Cell Zone 4 • NCRP #1930</div>
          </div>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-secondary to-primary flex items-center justify-center text-surface font-bold text-sm">RS</div>
        </div>
      </div>
    </header>
  )
}
