// src/views/UPIBridgeView.jsx — UPI → Crypto Investigation Bridge
import React, { useState } from 'react'
import { analyzeUPIComplaint } from '../services/api'

const SAMPLE_COMPLAINT = `Complaint: I received a call from someone claiming to be from "TechCrypto Investments" on WhatsApp. They asked me to invest in USDT cryptocurrency for guaranteed 3x returns. I transferred ₹2,50,000 via UPI to suresh.kumar9871@ybl on 15/03/2024. After transfer they stopped responding. My UPI ref no is UPI/24315/1234567890. The person's WhatsApp number was 9876543210.`

export default function UPIBridgeView() {
  const [complaint, setComplaint]   = useState('')
  const [amount, setAmount]         = useState('')
  const [fir, setFir]               = useState('')
  const [result, setResult]         = useState(null)
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)

  const analyze = async () => {
    if (!complaint.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const r = await analyzeUPIComplaint(
        complaint,
        amount ? parseFloat(amount) : null,
        fir || null,
        null,
      )
      setResult(r)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const priorityColor = (p) => {
    if (p === 'IMMEDIATE') return 'cs-tag-red'
    if (p === 'HIGH')      return 'cs-tag-amber'
    return 'cs-tag-cyan'
  }

  return (
    <div className="p-6" style={{ maxWidth: '1100px' }}>
      <div className="cs-section-title">🏦 UPI → Crypto Investigation Bridge</div>
      <p className="text-sm text-secondary mb-4">
        Paste a raw FIR/NCRP complaint. The system extracts UPI IDs, identifies the P2P crypto corridor,
        and generates Section 91 BNSS legal notice recommendations.
      </p>

      {/* Input form */}
      <div className="cs-card mb-4">
        <div className="grid-2 gap-3 mb-3">
          <div>
            <label className="cs-label">FIR / NCRP Complaint Number (optional)</label>
            <input className="cs-input" placeholder="e.g. NCRP/2024/MH/CY/8821" value={fir} onChange={e => setFir(e.target.value)} />
          </div>
          <div>
            <label className="cs-label">Fraud Amount (INR)</label>
            <input className="cs-input" type="number" placeholder="e.g. 250000" value={amount} onChange={e => setAmount(e.target.value)} />
          </div>
        </div>

        <label className="cs-label">Complaint Text (FIR / NCRP / Victim Statement)</label>
        <textarea
          className="cs-input"
          style={{ minHeight: '120px', resize: 'vertical', fontFamily: 'var(--font-sans)' }}
          placeholder="Paste the raw complaint text here..."
          value={complaint}
          onChange={e => setComplaint(e.target.value)}
        />
        <div style={{ display: 'flex', gap: '.75rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          <button className="cs-btn cs-btn-primary cs-btn-lg" onClick={analyze} disabled={loading || !complaint.trim()}>
            {loading ? <><span className="cs-spinner" /> Analyzing...</> : '🔬 Analyze Complaint'}
          </button>
          <button
            className="cs-btn cs-btn-ghost"
            onClick={() => { setComplaint(SAMPLE_COMPLAINT); setAmount('250000'); setFir('NCRP/2024/MH/CY/8821') }}
          >
            📋 Load Sample Complaint
          </button>
          <button className="cs-btn cs-btn-ghost" onClick={() => { setComplaint(''); setResult(null); setFir(''); setAmount('') }}>
            🗑️ Clear
          </button>
        </div>
      </div>

      {error && <div className="cs-alert cs-alert-critical mb-3"><span>⚠️</span> {error}</div>}

      {/* Results */}
      {result && (
        <>
          {/* Summary row */}
          <div className="grid-4 mb-4">
            <div className="cs-stat">
              <div className="cs-stat-label">UPI IDs Found</div>
              <div className="cs-stat-value cyan">{result.extracted_upi_ids?.length || 0}</div>
            </div>
            <div className="cs-stat">
              <div className="cs-stat-label">Crypto Addresses</div>
              <div className="cs-stat-value cyan">{result.extracted_crypto_addresses?.length || 0}</div>
            </div>
            <div className="cs-stat">
              <div className="cs-stat-label">P2P Corridor</div>
              <div style={{ fontFamily: 'var(--font-sans)', fontWeight: '600', fontSize: '.9rem', color: 'var(--cyan-400)', marginTop: '.4rem' }}>
                {result.p2p_corridor_analysis?.likely_corridor || 'Unknown'}
              </div>
              <div className="cs-stat-delta">{result.p2p_corridor_analysis?.confidence != null ? `${(result.p2p_corridor_analysis.confidence * 100).toFixed(0)}% confidence` : ''}</div>
            </div>
            <div className="cs-stat">
              <div className="cs-stat-label">Investigation Leads</div>
              <div className="cs-stat-value green">{result.crypto_leads?.length || 0}</div>
            </div>
          </div>

          {/* Extracted entities */}
          {(result.extracted_upi_ids?.length > 0 || result.extracted_crypto_addresses?.length > 0) && (
            <div className="cs-card mb-4">
              <div className="cs-card-title mb-3">🔍 Extracted Entities</div>
              <div className="grid-2 gap-4">
                <div>
                  <div className="cs-label mb-2">UPI IDs</div>
                  {result.extracted_upi_ids?.length > 0 ? result.extracted_upi_ids.map((id, i) => (
                    <div key={i} className="cs-hash-block mb-1">
                      <span className="mono" style={{ fontSize: '.78rem', color: 'var(--amber-400)' }}>{id}</span>
                    </div>
                  )) : <div className="text-muted text-sm">None extracted</div>}
                </div>
                <div>
                  <div className="cs-label mb-2">Crypto Addresses</div>
                  {result.extracted_crypto_addresses?.length > 0 ? result.extracted_crypto_addresses.map((addr, i) => (
                    <div key={i} className="cs-hash-block mb-1">
                      <span className="mono" style={{ fontSize: '.73rem', color: 'var(--cyan-400)' }}>{addr}</span>
                    </div>
                  )) : <div className="text-muted text-sm">None extracted — investigators should trace UPI endpoint</div>}
                </div>
              </div>
            </div>
          )}

          {/* Investigation leads */}
          {result.crypto_leads?.length > 0 && (
            <div className="cs-card mb-4">
              <div className="cs-card-title mb-3">🎯 Investigation Leads</div>
              {result.crypto_leads.map((lead, i) => (
                <div key={i} className="threat-indicator medium mb-3">
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginBottom: '.4rem' }}>
                      <span className={`cs-tag ${priorityColor(lead.priority)}`}>{lead.priority}</span>
                      <span className="fw-600 text-sm">{lead.exchange}</span>
                    </div>
                    <div className="text-sm" style={{ marginBottom: '.3rem' }}>{lead.legal_action}</div>
                    <div className="text-xs text-muted">Evidence basis: {lead.evidence_basis}</div>
                    {lead.compliance_contact && lead.compliance_contact !== 'N/A — run blockchain trace first' && (
                      <div className="text-xs" style={{ marginTop: '.3rem', color: 'var(--cyan-400)' }}>
                        📧 {lead.compliance_contact}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Legal notices */}
          <div className="cs-card mb-4">
            <div className="cs-card-title mb-3">⚖️ Suggested Legal Notices</div>
            {result.legal_notices_suggested?.map((notice, i) => (
              <div key={i} className="cs-hash-block mb-2" style={{ borderLeftColor: 'var(--purple-500)' }}>
                <div className="text-sm">{notice}</div>
              </div>
            ))}
          </div>

          {/* Next steps */}
          <div className="cs-card">
            <div className="cs-card-title mb-3">📋 Recommended Next Steps</div>
            {result.recommended_next_steps?.map((step, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '.75rem', padding: '.5rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '.9rem' }}>{step.slice(0, 2)}</span>
                <span className="text-sm">{step.slice(2)}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
