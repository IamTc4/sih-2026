// src/views/MultiChainView.jsx — Multi-Chain Wallet Inspector
import React, { useState } from 'react'
import { traceWallet, getRiskScore, screenAddresses, detectChain, getAttribution } from '../services/api'

const DEMO_WALLETS = [
  { addr: 'T_VICTIM_SIH_DEMO_999', label: 'Tron Demo (Victim)', chain: 'tron' },
  { addr: '0x_VICTIM_SIH_DEMO_999', label: 'Ethereum Demo (Victim)', chain: 'ethereum' },
  { addr: 'TXkrKLFaLKPNzp3sPV4i7HGFt9M1kxB2q', label: 'Known Fraud (Tron)', chain: 'tron' },
]

export default function MultiChainView() {
  const [address, setAddress] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const chainInfo = address ? detectChain(address) : null

  const investigate = async (addr) => {
    const a = addr || address
    if (!a.trim()) return
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const [trace, risk, sanctions, attribution] = await Promise.allSettled([
        traceWallet(a.trim(), 4),
        getRiskScore(a.trim()),
        screenAddresses([a.trim()]),
        getAttribution(a.trim()),
      ])

      setResults({
        address: a.trim(),
        chain: detectChain(a.trim()),
        trace:       trace.status === 'fulfilled'       ? trace.value       : null,
        risk:        risk.status === 'fulfilled'        ? risk.value        : null,
        sanctions:   sanctions.status === 'fulfilled'   ? sanctions.value   : null,
        attribution: attribution.status === 'fulfilled' ? attribution.value : null,
        traceError: trace.reason?.message,
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const riskColor = (score) => {
    if (!score && score !== 0) return 'var(--text-muted)'
    if (score >= 0.7) return 'var(--red-400)'
    if (score >= 0.4) return 'var(--amber-400)'
    return 'var(--emerald-400)'
  }

  const riskLabel = (score) => {
    if (!score && score !== 0) return 'N/A'
    if (score >= 0.7) return 'HIGH RISK'
    if (score >= 0.4) return 'MEDIUM'
    return 'LOW RISK'
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="cs-section-title">⛓️ Multi-Chain Wallet Inspector</div>
      <p className="text-sm text-secondary mb-4">
        Automatically detects Tron TRC-20 or Ethereum ERC-20. Paste any wallet address.
      </p>

      {/* Input */}
      <div className="cs-card mb-4">
        <div className="flex gap-3 mb-3">
          <div style={{ flex: 1 }}>
            <label className="cs-label">Wallet Address (Tron T... or Ethereum 0x...)</label>
            <input
              className="cs-input"
              placeholder="T... or 0x..."
              value={address}
              onChange={e => setAddress(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && investigate()}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              className="cs-btn cs-btn-primary cs-btn-lg"
              onClick={() => investigate()}
              disabled={loading || !address.trim()}
            >
              {loading ? <span className="cs-spinner" /> : '🔍'} Investigate
            </button>
          </div>
        </div>

        {/* Chain badge */}
        {chainInfo && address && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem' }}>
            <span className={`chain-pill ${chainInfo.chain}`}>
              ● {chainInfo.label}
            </span>
            <span className="text-xs text-muted">{chainInfo.token}</span>
            {chainInfo.chain !== 'unknown' && (
              <span className="text-xs text-muted">Auto-detected from address prefix</span>
            )}
          </div>
        )}

        {/* Demo wallets */}
        <div className="cs-divider-label">Quick Load Demo Wallets</div>
        <div style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap' }}>
          {DEMO_WALLETS.map(w => (
            <button
              key={w.addr}
              className="cs-btn cs-btn-ghost cs-btn-sm"
              onClick={() => { setAddress(w.addr); investigate(w.addr) }}
            >
              <span className={`chain-pill ${w.chain}`} style={{ marginRight: '.3rem' }}>●</span>
              {w.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="cs-alert cs-alert-critical mb-3">
          <span>⚠️</span> {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <>
          {/* Stats row */}
          <div className="grid-4 mb-4">
            <div className="cs-stat">
              <div className="cs-stat-label">Risk Score</div>
              <div className="cs-stat-value" style={{ color: riskColor(results.risk?.risk_score), fontSize: '1.8rem' }}>
                {results.risk?.risk_score != null ? (results.risk.risk_score * 100).toFixed(0) : '—'}
              </div>
              <div className="cs-stat-delta" style={{ color: riskColor(results.risk?.risk_score) }}>
                {riskLabel(results.risk?.risk_score)}
              </div>
            </div>

            <div className="cs-stat">
              <div className="cs-stat-label">Chain</div>
              <div style={{ marginTop: '.5rem' }}>
                <span className={`chain-pill ${results.chain.chain}`} style={{ fontSize: '.8rem', padding: '.3rem .7rem' }}>
                  {results.chain.label}
                </span>
              </div>
              <div className="cs-stat-delta">{results.chain.token}</div>
            </div>

            <div className="cs-stat">
              <div className="cs-stat-label">Attribution</div>
              <div className="cs-stat-value" style={{ fontSize: '1rem', marginTop: '.4rem', color: results.attribution?.status === 'KNOWN' ? 'var(--cyan-400)' : 'var(--text-muted)' }}>
                {results.attribution?.exchange_name || 'UNATTRIBUTED'}
              </div>
              <div className="cs-stat-delta">
                {results.attribution?.confidence != null ? `${(results.attribution.confidence * 100).toFixed(0)}% confidence` : '—'}
              </div>
            </div>

            <div className="cs-stat">
              <div className="cs-stat-label">Sanctions</div>
              {results.sanctions?.results?.[0]?.hit ? (
                <>
                  <div className="cs-stat-value red" style={{ fontSize: '1rem', marginTop: '.4rem' }}>⚠️ HIT</div>
                  <div className="cs-stat-delta text-red">{results.sanctions.results[0].source}</div>
                </>
              ) : (
                <>
                  <div className="cs-stat-value green" style={{ fontSize: '1rem', marginTop: '.4rem' }}>✓ CLEAN</div>
                  <div className="cs-stat-delta">No sanctions hit</div>
                </>
              )}
            </div>
          </div>

          {/* Trace details */}
          {results.trace && (
            <div className="cs-card mb-4">
              <div className="cs-card-header">
                <div className="cs-card-title">🗺️ Fund Trace</div>
                <span className="cs-tag cs-tag-cyan">{results.trace.total_transactions_ingested || 0} TXs</span>
              </div>

              <div className="grid-2 gap-4">
                <div>
                  <div className="cs-label mb-1">Trace Summary</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.75rem', lineHeight: 1.7 }}>
                    <div>Nodes: <span className="text-cyan">{results.trace.graph?.total_nodes || 0}</span></div>
                    <div>Edges: <span className="text-cyan">{results.trace.graph?.total_edges || 0}</span></div>
                    <div>Clusters: <span className="text-cyan">{results.trace.clusters?.length || 0}</span></div>
                    <div>Paths: <span className="text-cyan">{results.trace.all_paths?.length || 0}</span></div>
                  </div>
                </div>

                <div>
                  <div className="cs-label mb-1">Attribution</div>
                  {results.trace.attribution?.status === 'KNOWN' ? (
                    <div>
                      <div className="text-cyan fw-600" style={{ fontSize: '.9rem' }}>
                        {results.trace.attribution.exchange_name}
                      </div>
                      <div className="text-xs text-secondary mt-1">{results.trace.attribution.recommendation}</div>
                    </div>
                  ) : (
                    <div className="text-secondary text-sm">
                      No exchange match — manual OSINT recommended
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Risk explanation */}
          {results.risk?.top_features && (
            <div className="cs-card">
              <div className="cs-card-header">
                <div className="cs-card-title">🧠 Risk Factors</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '.6rem' }}>
                {results.risk.top_features.slice(0, 5).map((f, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '.75rem' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.72rem', color: 'var(--text-secondary)', width: '160px', flexShrink: 0 }}>
                      {f.feature}
                    </div>
                    <div className="cs-progress" style={{ flex: 1 }}>
                      <div
                        className={`cs-progress-bar ${f.contribution > 0.15 ? 'red' : f.contribution > 0.08 ? '' : 'green'}`}
                        style={{ width: `${Math.min(100, Math.abs(f.contribution) * 400)}%` }}
                      />
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '.7rem', color: 'var(--text-muted)', width: '50px', textAlign: 'right' }}>
                      {(f.contribution * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
