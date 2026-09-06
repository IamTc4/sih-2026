// src/views/BatchInvestigationView.jsx — Fraud Ring Multi-Wallet Analysis
import React, { useState } from 'react'
import { traceWallet, getRiskScore, detectChain } from '../services/api'

const DEMO_RING = [
  'T_VICTIM_SIH_DEMO_999',
  'TXkrKLFaLKPNzp3sPV4i7HGFt9M1kxB2q',
  'TLgz3sPKFk8C4UxvTbHJQYpRWNJ7iMFd3',
]

export default function BatchInvestigationView() {
  const [input, setInput]     = useState('')
  const [addresses, setAddresses] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)

  const parseAddresses = (text) => {
    return text.split(/[\n,;]+/).map(a => a.trim()).filter(a => a.length > 10)
  }

  const loadDemo = () => {
    setInput(DEMO_RING.join('\n'))
    setAddresses(DEMO_RING)
  }

  const runBatch = async () => {
    const addrs = parseAddresses(input)
    if (addrs.length === 0) return
    setAddresses(addrs)
    setLoading(true)
    setResults(null)
    setProgress(0)

    const perWallet = []
    for (let i = 0; i < addrs.length; i++) {
      const addr = addrs[i]
      try {
        const [trace, risk] = await Promise.allSettled([
          traceWallet(addr, 3),
          getRiskScore(addr),
        ])
        perWallet.push({
          address: addr,
          chain: detectChain(addr),
          trace:  trace.status === 'fulfilled'  ? trace.value  : null,
          risk:   risk.status  === 'fulfilled'  ? risk.value   : null,
        })
      } catch {
        perWallet.push({ address: addr, chain: detectChain(addr), trace: null, risk: null })
      }
      setProgress(Math.round(((i + 1) / addrs.length) * 100))
    }

    // Cross-wallet analysis
    const exchangeCounts = {}
    let highRisk = 0
    for (const r of perWallet) {
      const ex = r.trace?.attribution?.exchange_name
      if (ex) exchangeCounts[ex] = (exchangeCounts[ex] || 0) + 1
      if ((r.risk?.risk_score || 0) >= 0.7) highRisk++
    }
    const commonEx = Object.entries(exchangeCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, count]) => ({ name, count }))

    const ringConf = Math.min(0.98,
      (highRisk / addrs.length) * 0.5 + (commonEx[0]?.count > 1 ? 0.35 : 0) + (addrs.length > 2 ? 0.15 : 0)
    )

    setResults({ perWallet, commonEx, highRisk, ringConfidence: ringConf, total: addrs.length })
    setLoading(false)
  }

  const riskColor = s => s >= 0.7 ? 'var(--red-400)' : s >= 0.4 ? 'var(--amber-400)' : 'var(--emerald-400)'

  return (
    <div className="p-6" style={{ maxWidth: '1100px' }}>
      <div className="cs-section-title">🕸️ Fraud Ring Analysis (Batch Investigation)</div>
      <p className="text-sm text-secondary mb-4">
        Investigate multiple wallets simultaneously to detect fraud rings, shared exchange destinations, and coordinated mule activity.
      </p>

      {/* Input */}
      <div className="cs-card mb-4">
        <label className="cs-label">Wallet Addresses (one per line, or comma-separated)</label>
        <textarea
          className="cs-input mb-3"
          style={{ minHeight: '100px', resize: 'vertical', fontFamily: 'var(--font-mono)' }}
          placeholder={'T_VICTIM_SIH_DEMO_999\nTXkrKLFaLKPNzp3sPV...\n0x_VICTIM_SIH_DEMO_999'}
          value={input}
          onChange={e => setInput(e.target.value)}
        />
        <div style={{ display: 'flex', gap: '.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <button className="cs-btn cs-btn-primary cs-btn-lg" onClick={runBatch} disabled={loading || !input.trim()}>
            {loading ? <><span className="cs-spinner" /> Investigating... {progress}%</> : '🕸️ Analyze Fraud Ring'}
          </button>
          <button className="cs-btn cs-btn-ghost" onClick={loadDemo}>📋 Load Demo Ring</button>
          <button className="cs-btn cs-btn-ghost" onClick={() => { setInput(''); setResults(null) }}>🗑️ Clear</button>
          {input && (
            <span className="text-xs text-muted">
              {parseAddresses(input).length} address{parseAddresses(input).length !== 1 ? 'es' : ''} detected
            </span>
          )}
        </div>
        {loading && (
          <div className="mt-3">
            <div className="cs-progress">
              <div className="cs-progress-bar" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {results && (
        <>
          {/* Ring assessment */}
          <div className={`threat-indicator ${results.ringConfidence > 0.7 ? 'critical' : results.ringConfidence > 0.4 ? 'high' : 'medium'} mb-4`}
            style={{ padding: '1.25rem' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '.5rem' }}>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: '700',
                  color: results.ringConfidence > 0.7 ? 'var(--red-400)' : results.ringConfidence > 0.4 ? 'var(--amber-400)' : 'var(--emerald-400)',
                  lineHeight: 1 }}>
                  {(results.ringConfidence * 100).toFixed(0)}%
                </div>
                <div>
                  <div className="fw-600" style={{ fontSize: '1rem' }}>Fraud Ring Confidence</div>
                  <div className="text-sm text-secondary mt-1">
                    {results.ringConfidence > 0.7 ? '⚠️ CONFIRMED FRAUD RING — coordinated multi-wallet scheme detected' :
                     results.ringConfidence > 0.4 ? '⚡ LIKELY CONNECTED — shared activity patterns observed' :
                     '🔍 INSUFFICIENT EVIDENCE — wallets may be unrelated'}
                  </div>
                </div>
              </div>
              {results.commonEx[0] && (
                <div className="cs-alert cs-alert-critical mt-3" style={{ padding: '.6rem .85rem' }}>
                  <span>🎯</span>
                  <span><strong>All funds converging on {results.commonEx[0].name}</strong> ({results.commonEx[0].count}/{results.total} wallets) —
                    Issue consolidated Section 91 BNSS notice immediately.</span>
                </div>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="grid-4 mb-4">
            <div className="cs-stat">
              <div className="cs-stat-label">Wallets Investigated</div>
              <div className="cs-stat-value cyan">{results.total}</div>
            </div>
            <div className="cs-stat">
              <div className="cs-stat-label">High Risk</div>
              <div className="cs-stat-value red">{results.highRisk}</div>
            </div>
            <div className="cs-stat">
              <div className="cs-stat-label">Common Exchange</div>
              <div style={{ fontFamily: 'var(--font-sans)', fontWeight: '600', fontSize: '.9rem', color: 'var(--cyan-400)', marginTop: '.4rem' }}>
                {results.commonEx[0]?.name || 'None'}
              </div>
            </div>
            <div className="cs-stat">
              <div className="cs-stat-label">Ring Confidence</div>
              <div className={`cs-stat-value ${results.ringConfidence > 0.7 ? 'red' : results.ringConfidence > 0.4 ? 'amber' : 'green'}`}>
                {(results.ringConfidence * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          {/* Per-wallet table */}
          <div className="cs-card">
            <div className="cs-card-title mb-3">📊 Per-Wallet Results</div>
            <div style={{ overflowX: 'auto' }}>
              <table className="cs-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Address</th>
                    <th>Chain</th>
                    <th>Risk Score</th>
                    <th>Attribution</th>
                    <th>Tx Count</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.perWallet.map((r, i) => {
                    const riskScore = r.risk?.risk_score
                    const ex = r.trace?.attribution?.exchange_name
                    return (
                      <tr key={i}>
                        <td className="mono" style={{ opacity: .6 }}>{i + 1}</td>
                        <td>
                          <span className="mono truncate" style={{ maxWidth: '180px', display: 'block' }}>
                            {r.address.slice(0, 12)}...{r.address.slice(-6)}
                          </span>
                        </td>
                        <td><span className={`chain-pill ${r.chain.chain}`}>●&nbsp;{r.chain.chain}</span></td>
                        <td>
                          {riskScore != null ? (
                            <span className="mono fw-600" style={{ color: riskColor(riskScore) }}>
                              {(riskScore * 100).toFixed(0)}%
                            </span>
                          ) : <span className="text-muted">—</span>}
                        </td>
                        <td>{ex ? <span className="text-cyan fw-600">{ex}</span> : <span className="text-muted">Unattributed</span>}</td>
                        <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                          {r.trace?.total_transactions_ingested || '—'}
                        </td>
                        <td>
                          {riskScore >= 0.7
                            ? <span className="cs-tag cs-tag-red">HIGH RISK</span>
                            : riskScore >= 0.4
                            ? <span className="cs-tag cs-tag-amber">MEDIUM</span>
                            : <span className="cs-tag cs-tag-green">LOW</span>
                          }
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
