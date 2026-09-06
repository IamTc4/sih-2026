// src/views/ThreatMapView.jsx — Live Threat Intelligence Feed
import React, { useState, useEffect, useRef } from 'react'
import { cyberHealth, screenAddresses } from '../services/api'

// Simulated live threat events (in production, this would be a WebSocket)
const THREAT_PATTERNS = [
  { icon: '🌀', type: 'MIXER', label: 'Mixer/Tumbler Detected', color: 'var(--red-400)', severity: 'HIGH' },
  { icon: '🔗', type: 'PEEL',  label: 'Peel Chain (7 hops)',   color: 'var(--amber-400)', severity: 'MEDIUM' },
  { icon: '⚡', type: 'HOP',   label: 'Rapid Hopping (<5min)', color: 'var(--red-400)', severity: 'HIGH' },
  { icon: '📊', type: 'STRUCT',label: 'Structuring Pattern',   color: 'var(--amber-400)', severity: 'MEDIUM' },
  { icon: '🔴', type: 'OFAC',  label: 'OFAC Sanctions Hit',    color: 'var(--red-400)', severity: 'CRITICAL' },
  { icon: '🕸️', type: 'RING',  label: 'Fraud Ring Identified',  color: 'var(--purple-400)', severity: 'HIGH' },
]

const EXCHANGES = ['Binance', 'OKX', 'Bybit', 'KuCoin', 'HTX', 'Gate.io', 'MEXC']
const CHAINS    = ['Tron TRC-20', 'Ethereum ERC-20']

function randomAddr() {
  const isEth = Math.random() > 0.6
  return isEth
    ? '0x' + [...Array(40)].map(() => Math.floor(Math.random() * 16).toString(16)).join('')
    : 'T' + [...Array(33)].map(() => 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz0123456789'[Math.floor(Math.random() * 58)]).join('')
}

let _feedId = 1

export default function ThreatMapView() {
  const [feed, setFeed]       = useState([])
  const [stats, setStats]     = useState({ total: 0, critical: 0, ofac: 0, rings: 0 })
  const [paused, setPaused]   = useState(false)
  const [screenAddr, setScreenAddr] = useState('')
  const [screenResult, setScreenResult] = useState(null)
  const [screening, setScreening] = useState(false)
  const feedRef = useRef(null)

  // Simulate live threat events
  useEffect(() => {
    if (paused) return
    const addEvent = () => {
      const pattern  = THREAT_PATTERNS[Math.floor(Math.random() * THREAT_PATTERNS.length)]
      const exchange = EXCHANGES[Math.floor(Math.random() * EXCHANGES.length)]
      const chain    = CHAINS[Math.floor(Math.random() * CHAINS.length)]
      const addr     = randomAddr()
      const event = {
        id: _feedId++,
        timestamp: new Date().toISOString(),
        ...pattern,
        address: addr,
        exchange,
        chain,
        amount: (Math.random() * 50000 + 1000).toFixed(2),
      }
      setFeed(prev => [event, ...prev].slice(0, 100))
      setStats(prev => ({
        total: prev.total + 1,
        critical: prev.critical + (pattern.severity === 'CRITICAL' ? 1 : 0),
        ofac:  prev.ofac  + (pattern.type === 'OFAC' ? 1 : 0),
        rings: prev.rings + (pattern.type === 'RING' ? 1 : 0),
      }))
    }
    // Initial burst
    for (let i = 0; i < 8; i++) setTimeout(addEvent, i * 200)
    const interval = setInterval(addEvent, 2500)
    return () => clearInterval(interval)
  }, [paused])

  // Auto-scroll feed
  useEffect(() => {
    if (feedRef.current && !paused) {
      feedRef.current.scrollTop = 0
    }
  }, [feed.length])

  const doScreen = async () => {
    if (!screenAddr.trim()) return
    setScreening(true)
    try {
      const r = await screenAddresses([screenAddr.trim()])
      setScreenResult(r.results?.[0] || null)
    } catch (e) {
      setScreenResult({ error: e.message })
    } finally {
      setScreening(false)
    }
  }

  return (
    <div className="p-6" style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: '1.5rem', height: 'calc(100vh - 100px)' }}>
      {/* Left — Feed */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflow: 'hidden' }}>
        <div className="cs-section-title">🛡️ Live Threat Intelligence Feed</div>

        {/* Stats */}
        <div className="grid-4" style={{ flexShrink: 0 }}>
          {[
            { label: 'Total Events', val: stats.total, color: 'cyan' },
            { label: 'Critical Alerts', val: stats.critical, color: 'red' },
            { label: 'OFAC Hits', val: stats.ofac, color: 'red' },
            { label: 'Fraud Rings', val: stats.rings, color: 'purple' },
          ].map(s => (
            <div key={s.label} className="cs-stat">
              <div className="cs-stat-label">{s.label}</div>
              <div className={`cs-stat-value ${s.color}`}>{s.val}</div>
            </div>
          ))}
        </div>

        {/* Controls */}
        <div style={{ display: 'flex', gap: '.75rem', alignItems: 'center', flexShrink: 0 }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.7rem', color: 'var(--text-muted)' }}>
            {paused ? '⏸ PAUSED' : '● LIVE FEED'}
          </div>
          <div className="status-dot" style={{ background: paused ? 'var(--amber-400)' : 'var(--emerald-400)', boxShadow: `0 0 8px ${paused ? 'var(--amber-400)' : 'var(--emerald-400)'}`, animation: paused ? 'none' : 'pulse 1.5s infinite' }} />
          <button className="cs-btn cs-btn-ghost cs-btn-sm" onClick={() => setPaused(p => !p)}>
            {paused ? '▶ Resume' : '⏸ Pause'}
          </button>
        </div>

        {/* Feed list */}
        <div ref={feedRef} className="cs-card" style={{ flex: 1, overflow: 'hidden auto', padding: '1rem' }}>
          {feed.length === 0 ? (
            <div className="flex-center" style={{ height: '100%', color: 'var(--text-muted)', fontSize: '.82rem' }}>
              Initializing threat feed...
            </div>
          ) : feed.map(ev => (
            <div key={ev.id} className="cs-feed-item" style={{ animationDelay: '0ms' }}>
              <div className="cs-feed-icon" style={{ background: `${ev.color}18` }}>
                {ev.icon}
              </div>
              <div className="cs-feed-content">
                <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', flexWrap: 'wrap' }}>
                  <span className={`cs-tag ${ev.severity === 'CRITICAL' ? 'cs-tag-red' : ev.severity === 'HIGH' ? 'cs-tag-amber' : 'cs-tag-cyan'}`}>
                    {ev.severity}
                  </span>
                  <span className="cs-feed-title">{ev.label}</span>
                </div>
                <div className="cs-feed-meta" style={{ marginTop: '.3rem' }}>
                  <span className="text-cyan">{ev.address.slice(0, 12)}...{ev.address.slice(-6)}</span>
                  {' · '}<span>{ev.chain}</span>
                  {' · '}<span style={{ color: 'var(--amber-400)' }}>${Number(ev.amount).toLocaleString()} USDT</span>
                  {' → '}<span style={{ color: 'var(--cyan-400)' }}>{ev.exchange}</span>
                </div>
                <div className="cs-feed-meta">{new Date(ev.timestamp).toLocaleTimeString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right — Sanctions screener + source legend */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Manual Sanctions Screen */}
        <div className="cs-card">
          <div className="cs-card-title mb-3">🔎 Sanctions Screener</div>
          <label className="cs-label">Wallet Address</label>
          <input
            className="cs-input mb-2"
            placeholder="T... or 0x..."
            value={screenAddr}
            onChange={e => setScreenAddr(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && doScreen()}
          />
          <button className="cs-btn cs-btn-primary w-full" onClick={doScreen} disabled={screening || !screenAddr.trim()}>
            {screening ? <><span className="cs-spinner" /> Screening...</> : '🔍 Screen Now'}
          </button>

          {screenResult && (
            <div className={`cs-alert mt-3 ${screenResult.error ? 'cs-alert-critical' : screenResult.hit ? 'cs-alert-critical' : 'cs-alert-success'}`}>
              {screenResult.error ? (
                <span>⚠️ {screenResult.error}</span>
              ) : screenResult.hit ? (
                <div>
                  <div className="fw-600">⚠️ SANCTIONS HIT</div>
                  <div className="text-xs mt-1">Source: {screenResult.source}</div>
                  <div className="text-xs">Category: {screenResult.category}</div>
                  <div className="text-xs mt-1">{screenResult.description}</div>
                </div>
              ) : (
                <div>
                  <div className="fw-600">✓ CLEAN</div>
                  <div className="text-xs mt-1">{screenResult.description}</div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Feed Sources */}
        <div className="cs-card" style={{ flex: 1 }}>
          <div className="cs-card-title mb-3">📡 Intel Sources</div>
          {[
            { src: 'OFAC SDN List',         status: 'LIVE', color: 'cs-tag-green', desc: 'US Treasury sanctions — crypto addresses' },
            { src: 'CryptoScamDB',           status: 'LIVE', color: 'cs-tag-green', desc: 'Community-reported scam addresses' },
            { src: 'I4C Internal Watchlist', status: 'LIVE', color: 'cs-tag-cyan',  desc: 'MHA I4C India-specific watchlist' },
            { src: 'ED India Seizures',      status: 'LIVE', color: 'cs-tag-cyan',  desc: 'Enforcement Directorate PMLA seizures' },
            { src: 'CBI Crypto Cell',        status: 'LIVE', color: 'cs-tag-cyan',  desc: 'CBI FIR-linked crypto addresses' },
            { src: 'Elliptic Dataset',        status: 'STATIC', color: 'cs-tag-purple', desc: 'Academic labeled fraud dataset' },
          ].map(s => (
            <div key={s.src} style={{ padding: '.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '.2rem' }}>
                <span className="fw-600 text-sm">{s.src}</span>
                <span className={`cs-tag ${s.color}`}>{s.status}</span>
              </div>
              <div className="text-xs text-muted">{s.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
