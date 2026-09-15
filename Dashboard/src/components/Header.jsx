// src/components/Header.jsx
// Live clock, animated block counter, scrolling status ticker
import React, { useState, useEffect } from 'react'

const TICKER_ITEMS = [
  '⬡ TRON MAINNET RPC LIVE',
  '⬡ SHA-256 HASH CHAIN ACTIVE',
  '⬡ SIH26183 — WALLETTRACE v1.0',
  '⬡ ML MODEL v2.4.1 LOADED',
  '⬡ FIU-IND VASP WATCHLIST SYNCED',
  '⬡ LANGGRAPH AGENT ONLINE',
  '⬡ EVIDENCE CHAIN INTEGRITY VERIFIED',
  '⬡ MHA I4C NATIONAL FORENSICS PORTAL',
]

export default function Header({ activeView }) {
  const [time, setTime]         = useState(new Date())
  const [blockH, setBlockH]     = useState(67_841_353)
  const [isTicking, setIsTicking] = useState(false)

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    const b = setInterval(() => {
      setIsTicking(true)
      setBlockH(h => h + Math.floor(Math.random() * 3) + 1)
      setTimeout(() => setIsTicking(false), 150)
    }, 3800)
    return () => clearInterval(b)
  }, [])

  const ticker = [...TICKER_ITEMS, ...TICKER_ITEMS].join('    ')

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest/95 backdrop-blur-md border-b border-border-subtle">

      {/* ── Scrolling ticker bar ── */}
      <div className="h-5 bg-[#020a14] overflow-hidden flex items-center border-b border-border-subtle/40">
        <div className="flex-shrink-0 px-3 bg-primary text-on-primary font-label-caps text-label-caps font-bold tracking-widest text-[9px] h-full flex items-center gap-1.5 mr-3 z-10">
          <span className="w-1.5 h-1.5 rounded-full bg-on-primary animate-subtle-pulse" />
          LIVE
        </div>
        <div className="overflow-hidden flex-1">
          <div className="animate-ticker whitespace-nowrap font-label-caps text-label-caps text-on-surface-variant/60 tracking-widest text-[9px]">
            {ticker}
          </div>
        </div>
        {/* Block counter with 150ms count-up transition */}
        <div className="flex-shrink-0 px-3 font-code-sm text-code-sm text-secondary/80 border-l border-border-subtle/40 h-full flex items-center gap-1">
          <span className="text-outline/60">BLK</span>
          <span className={`chain-live text-secondary tabular-nums transition-transform duration-150 inline-block ${isTicking ? 'animate-number-tick text-primary' : ''}`}>
            {blockH.toLocaleString('en-IN')}
          </span>
        </div>
      </div>

      {/* ── Main header bar ── */}
      <div className="h-[52px] px-4 flex items-center justify-between">
        {/* Logo + title */}
        <div className="flex items-center gap-3">
          {/* Logo mark */}
          <div className="relative w-9 h-9 flex-shrink-0">
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary via-secondary to-primary opacity-25 animate-pulse" />
            <div className="relative w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-surface font-bold text-sm font-headline-md" style={{ fontSize: '1.05rem' }}>
              ⬡
            </div>
          </div>

          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-headline-md text-headline-md font-bold tracking-tight text-on-surface leading-none">
                Crypto<span className="text-primary">Sentinel</span>
              </span>
              <span className="font-code-sm text-code-sm text-primary/70 font-bold hidden md:block">// CYBER-COMMAND</span>
            </div>
            <span className="font-label-caps text-label-caps text-on-surface-variant/60 tracking-wider leading-none mt-0.5">
              MHA I4C · NATIONAL CRYPTO FORENSICS PORTAL · SIH26183
            </span>
          </div>

          {/* Badges */}
          <div className="ml-3 hidden lg:flex items-center gap-2">
            <span className="px-2 py-0.5 bg-status-danger-bg text-error font-label-caps text-label-caps rounded border border-error/20 animate-pulse">
              RESTRICTED — LE ONLY
            </span>
            <span className="px-2 py-0.5 bg-status-warning-bg text-status-warning font-label-caps text-label-caps rounded border border-status-warning/20">
              CRITICAL: 14 ACTIVE
            </span>
          </div>
        </div>

        {/* Right side — clock + user */}
        <div className="flex items-center gap-4">
          {/* Live clock */}
          <div className="hidden sm:flex flex-col items-end">
            <div className="font-code-base text-code-base text-primary tabular-nums chain-live leading-none">
              {time.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
            </div>
            <div className="font-label-caps text-label-caps text-outline/70 tracking-wider leading-none mt-0.5">
              {time.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()} IST
            </div>
          </div>

          {/* Divider */}
          <div className="w-px h-8 bg-border-subtle" />

          {/* Officer */}
          <div className="text-right hidden sm:block">
            <div className="font-body-medium text-body-medium text-on-surface leading-none">Insp. R. Sharma</div>
            <div className="font-code-sm text-code-sm text-on-surface-variant/70 leading-none mt-0.5">Cyber Cell Zone 4 • NCRP #1930</div>
          </div>
          <div className="relative w-8 h-8 flex-shrink-0">
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-secondary to-primary opacity-30 animate-pulse" />
            <div className="relative w-8 h-8 rounded-full bg-gradient-to-br from-secondary to-primary flex items-center justify-center text-surface font-bold text-xs">
              RS
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
