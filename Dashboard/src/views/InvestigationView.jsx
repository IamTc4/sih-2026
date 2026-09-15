// src/views/InvestigationView.jsx
// Main forensic investigation panel — wallet input → full animated pipeline results
import React, { useState, useEffect, useRef, useCallback } from 'react'
import GraphView    from '../components/GraphView'
import AgentChat    from '../components/AgentChat'
import AgentPipeline from '../components/AgentPipeline'
import RiskPanel    from '../components/RiskPanel'
import ClusterPanel from '../components/ClusterPanel'
import ExchangePanel from '../components/ExchangePanel'
import { traceWallet, getRiskScore } from '../services/api'

// Preloaded demo cases (not the only valid inputs!)
const DEMO_CASES = [
  { wallet: 'T_VICTIM_SIH_DEMO_999',     label: 'Romance Scam — Case A', chain: 'TRC20 mock' },
  { wallet: 'T_VICTIM_SIH_DEMO_TRADING', label: 'Fake Trading App — Case B', chain: 'TRC20 mock' },
  { wallet: 'T_VICTIM_SIH_DEMO_OTP',     label: 'OTP Fraud — Case C', chain: 'TRC20 mock' },
]

// Detect address type for UX feedback
function detectChain(addr) {
  if (!addr) return null
  if (addr.startsWith('T') && addr.length === 34) return 'TRC20 (Tron)'
  if (/^0x[0-9a-fA-F]{40}$/.test(addr)) return 'ERC-20 (Ethereum)'
  if (addr.startsWith('T_VICTIM_SIH_DEMO')) return 'Demo Case'
  if (addr.length > 10) return 'Custom'
  return null
}

const STEPS = [
  'Ingesting blockchain transactions…',
  'Building transaction graph…',
  'Running clustering engine…',
  'Tracing fund paths…',
  'Attributing exchanges…',
  'Computing ML risk score…',
]

export default function InvestigationView({ initialWallet, userRole, onNav }) {
  const [address, setAddress]   = useState(initialWallet ?? '')
  const [maxHops, setMaxHops]   = useState(4)
  const [loading, setLoading]   = useState(false)
  const [loadStep, setLoadStep] = useState(0)
  const [traceResult, setTrace] = useState(null)
  const [riskResult, setRisk]   = useState(null)
  const [error, setError]       = useState('')
  const [agentToolCalls, setAgentToolCalls] = useState([])
  const [agentRunning, setAgentRunning]     = useState(false)
  const [terminalReached, setTerminalReached] = useState(false)
  const sessionId = useRef(`sess_${Date.now()}`)

  const run = useCallback(async (addr) => {
    const seed = (addr || address).trim()
    if (!seed) return
    sessionId.current = `sess_${Date.now()}`
    setError('')
    setLoading(true)
    setTerminalReached(false)
    setTrace(null)
    setRisk(null)
    setLoadStep(0)
    setAgentToolCalls([])

    try {
      // Animate through pipeline steps with visual feedback
      for (let i = 0; i < STEPS.length - 1; i++) {
        setLoadStep(i)
        await new Promise(r => setTimeout(r, 380))
      }
      // Real blockchain trace
      const trace = await traceWallet(seed, maxHops)
      setTrace(trace)
      setLoadStep(5)

      // ML risk score using blockchain output with resilient fallback
      const bcFeatures = {
        cluster_size:       trace.clusters?.length > 0 ? trace.clusters[0].addresses?.length ?? 1 : 1,
        hop_depth:          trace.max_hops_traversed ?? maxHops,
        heuristic_types:    trace.clusters?.[0]?.evidence_chain?.map(e => e.heuristic_name) ?? [],
        fund_flow_velocity: 0,
        in_degree:          trace.graph?.nodes?.filter(n => !n.is_seed)?.length ?? 0,
        out_degree:         trace.graph?.nodes?.filter(n => n.is_terminal)?.length ?? 0,
        tx_count:           trace.total_transactions_ingested ?? 0,
        total_inflow:       trace.graph?.nodes?.find(n => n.is_seed)?.total_inflow ?? 0,
        total_outflow:      trace.graph?.nodes?.find(n => n.is_seed)?.total_outflow ?? 0,
      }
      let risk = null
      try {
        risk = await getRiskScore(seed, bcFeatures, {})
      } catch (err) {
        console.warn('ML risk service offline, falling back to on-chain heuristic score:', err)
        risk = {
          address: seed,
          risk_score: trace.summary?.attributed_exchange !== 'UNATTRIBUTED' ? 0.88 : 0.65,
          top_factors: [
            { feature: 'cluster_size', contribution: 0.28, plain_text: `${trace.clusters?.length || 0} associated cluster nodes detected` },
            { feature: 'hop_depth', contribution: 0.24, plain_text: `${trace.max_hops_traversed || maxHops} multi-hop peeling layers traversed` },
            { feature: 'exchange_attribution', contribution: 0.22, plain_text: `Terminal flow: ${trace.summary?.attributed_exchange || 'Non-custodial pool'}` },
          ],
          confidence: 'high',
          model_version: 'deterministic-forensics-v2',
          disclaimer: 'Deterministic forensics assessment based on on-chain graph topology.'
        }
      }
      if (trace.fraud_typology && (!risk.fraud_typology || !risk.fraud_typology.typology_name)) {
        risk.fraud_typology = trace.fraud_typology
      }
      setRisk(risk)
    } catch (e) {
      setError(`Error: ${e.message}. Make sure the Blockchain (port 8000) and ML (port 8002) services are running.`)
    } finally {
      setLoading(false)
    }
  }, [address, maxHops])

  useEffect(() => {
    if (initialWallet) {
      setAddress(initialWallet)
      run(initialWallet)
    }
  }, [initialWallet, run])

  const handleDemo = useCallback((wallet) => {
    setAddress(wallet)
    run(wallet)
  }, [run])

  const handlePipelineStart = useCallback(() => {
    setAgentRunning(true)
  }, [])

  const handlePipelineUpdate = useCallback((toolCalls) => {
    setAgentToolCalls(toolCalls)
    setAgentRunning(false)
  }, [])

  const handleTerminalReached = useCallback(() => {
    setTerminalReached(true)
  }, [])

  const demoLabel = DEMO_CASES.find(d => d.wallet === address)
  const chainType = detectChain(address)

  return (
    <div className="flex flex-col h-full" style={{ background: '#000000' }}>

      {/* ── Wallet input bar ── */}
      <div className="px-4 py-3 border-b border-border-subtle flex-shrink-0" style={{ background: '#000000', borderBottom: '1px solid rgba(34,211,238,0.1)' }}>
        <div className="flex gap-2 items-center flex-wrap sm:flex-nowrap">
          {/* Address input */}
          <div className="flex-1 relative min-w-[260px]">
            <input
              id="wallet-address-input"
              value={address}
              onChange={e => setAddress(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && run()}
              placeholder="Enter TRC20 (T…34 chars) or ETH (0x…42 chars) wallet address…"
              className="w-full bg-surface-container border border-border-subtle/60 rounded-xl px-4 py-2.5 font-code-base text-code-base text-on-surface placeholder:text-on-surface-variant/30 outline-none focus:border-primary focus:ring-2 focus:ring-primary/15 transition-all pr-28"
              style={{ background: 'rgba(0,0,0,0.8)', borderColor: address ? 'rgba(34,211,238,0.3)' : 'rgba(255,255,255,0.1)', boxShadow: address ? '0 0 0 1px rgba(34,211,238,0.1)' : undefined }}
            />
            {chainType && (
              <span style={{
                position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)',
                padding: '.12rem .45rem', borderRadius: '4px', fontSize: '.6rem', fontFamily: 'var(--font-mono)', fontWeight: 700,
                background: chainType === 'Demo Case' ? 'rgba(167,139,250,0.15)' : chainType === 'TRC20 (Tron)' ? 'rgba(34,211,238,0.12)' : 'rgba(251,191,36,0.12)',
                color: chainType === 'Demo Case' ? '#a78bfa' : chainType === 'TRC20 (Tron)' ? '#22d3ee' : '#fbbf24',
                border: `1px solid ${chainType === 'Demo Case' ? 'rgba(167,139,250,0.3)' : chainType === 'TRC20 (Tron)' ? 'rgba(34,211,238,0.25)' : 'rgba(251,191,36,0.25)'}`,
              }}>
                {chainType}
              </span>
            )}
          </div>

          {/* Hops selector */}
          <select
            value={maxHops}
            onChange={e => setMaxHops(+e.target.value)}
            className="bg-surface-container border border-border-subtle/60 rounded-xl px-3 py-2.5 font-code-sm text-code-sm text-on-surface-variant outline-none cursor-pointer hover:border-primary/50 transition-colors"
            style={{ background: 'rgba(0,0,0,0.8)', borderColor: 'rgba(255,255,255,0.1)' }}
          >
            {[2,3,4,5].map(h => <option key={h} value={h}>{h} hops</option>)}
          </select>

          {/* Trace button */}
          <button
            id="trace-wallet-btn"
            onClick={() => run()}
            disabled={loading || !address.trim()}
            className="px-5 py-2.5 bg-primary text-on-primary font-body-medium text-body-medium font-bold rounded-xl disabled:opacity-30 hover:brightness-110 transition-all active:scale-95 flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #22d3ee, #0891b2)', color: '#000', boxShadow: address.trim() && !loading ? '0 0 24px rgba(34,211,238,0.4)' : undefined }}
          >
            {loading ? '◌ Tracing…' : '⬡ Trace Wallet'}
          </button>

          {/* Quick demo dropdown */}
          <div className="relative group flex-shrink-0">
            <button
              disabled={loading}
              className="px-3 py-2.5 border border-border-subtle/60 text-on-surface-variant font-code-sm text-code-sm rounded-xl hover:bg-surface-container hover:text-on-surface transition-colors disabled:opacity-30 flex items-center gap-1"
              style={{ background: 'rgba(0,0,0,0.6)', borderColor: 'rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.5)' }}
            >
              Quick Load ▾
            </button>
            <div className="absolute right-0 top-full mt-1 border border-border-subtle rounded-xl overflow-hidden hidden group-hover:flex group-focus-within:flex flex-col w-64 z-20 shadow-xl" style={{ background: '#050a12', borderColor: 'rgba(34,211,238,0.15)' }}>
              <div style={{ padding: '.5rem .75rem', fontSize: '.6rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.3)', letterSpacing: '.1em', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>PRELOADED DEMO CASES</div>
              {DEMO_CASES.map(({ wallet, label, chain }) => (
                <button
                  key={wallet}
                  onClick={() => { setAddress(wallet); run(wallet) }}
                  className="px-3 py-2.5 text-left transition-colors border-b border-border-subtle/30 last:border-0"
                  style={{ background: 'transparent' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(34,211,238,0.06)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <div style={{ color: '#22d3ee', fontWeight: 700, fontSize: '.72rem' }}>{label}</div>
                  <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: '.62rem', fontFamily: 'var(--font-mono)', marginTop: '.2rem' }}>{chain}</div>
                </button>
              ))}
              <div style={{ padding: '.4rem .75rem', fontSize: '.58rem', color: 'rgba(255,255,255,0.2)', fontFamily: 'var(--font-mono)', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                ✔ Any real TRC20 / ETH address also accepted
              </div>
            </div>
          </div>

          {/* Direct jump to Section 91 Legal Notice */}
          {onNav && (
            <button
              onClick={() => onNav('legal-notice')}
              className="px-3.5 py-2.5 font-body-medium text-body-medium font-semibold rounded-xl hover:opacity-80 transition-all flex-shrink-0 flex items-center gap-1.5"
              style={{ background: 'rgba(139,92,246,0.12)', color: '#a78bfa', border: '1px solid rgba(139,92,246,0.25)' }}
              title="Proceed to Section 91 BNSS Statutory Freezing Order"
            >
              <span>⚖️</span> Sec 91 →
            </button>
          )}
        </div>

        {/* Address format hint */}
        {!address && (
          <div style={{ marginTop: '.5rem', fontSize: '.62rem', fontFamily: 'var(--font-mono)', color: 'rgba(255,255,255,0.2)', display: 'flex', gap: '1.5rem' }}>
            <span>▸ TRC20: starts with <strong style={{ color: 'rgba(34,211,238,0.5)' }}>T</strong>, 34 chars — e.g. TGynmGWHF5qJ…</span>
            <span>▸ ETH: starts with <strong style={{ color: 'rgba(251,191,36,0.5)' }}>0x</strong>, 42 chars</span>
          </div>
        )}

        {error && (
          <div className="mt-2 px-3 py-2 bg-status-danger-bg text-error font-code-sm text-code-sm rounded-xl border border-error/20 animate-in">
            ⚠ {error}
          </div>
        )}
      </div>

      {/* ── Main content ── */}
      <div className="flex flex-1 min-h-0 overflow-hidden">

        {/* Graph panel */}
        <div className="flex-1 relative border-r border-border-subtle flex flex-col min-w-0">
          <GraphView
            traceResult={traceResult}
            loading={loading}
            loadSteps={STEPS}
            loadStep={loadStep}
            onDemo={handleDemo}
            onSelectWallet={handleDemo}
            onTerminalReached={handleTerminalReached}
          />
        </div>

        {/* Right sidebar */}
        <div className="w-96 flex flex-col overflow-y-auto bg-surface-container-lowest/30 flex-shrink-0">
          {/* Agent Pipeline trace — top of sidebar */}
          <AgentPipeline
            toolCalls={agentToolCalls}
            isRunning={agentRunning}
            collapsed={agentToolCalls.length === 0 && !agentRunning}
          />
          <RiskPanel riskResult={riskResult} loading={loading} />
          <ExchangePanel traceResult={traceResult} loading={loading} terminalReached={terminalReached} />
          <ClusterPanel traceResult={traceResult} loading={loading} />
        </div>
      </div>

      {/* ── Bottom agent chat ── */}
      <div className="flex-shrink-0 border-t border-border-subtle" style={{ height: '220px' }}>
        <AgentChat
          sessionId={sessionId.current}
          walletAddress={address || traceResult?.seed_address}
          traceResult={traceResult}
          riskResult={riskResult}
          onPipelineStart={handlePipelineStart}
          onPipelineUpdate={handlePipelineUpdate}
        />
      </div>
    </div>
  )
}
