// src/views/InvestigationView.jsx
// Main forensic investigation panel — wallet input → full pipeline results
import React, { useState, useRef, useCallback } from 'react'
import GraphView from '../components/GraphView'
import AgentChat from '../components/AgentChat'
import RiskPanel from '../components/RiskPanel'
import ClusterPanel from '../components/ClusterPanel'
import ExchangePanel from '../components/ExchangePanel'
import { traceWallet, getRiskScore } from '../services/api'

const DEMO_ADDRESS = 'T_VICTIM_SIH_DEMO_999'

export default function InvestigationView() {
  const [address, setAddress]       = useState('')
  const [maxHops, setMaxHops]       = useState(4)
  const [loading, setLoading]       = useState(false)
  const [loadStep, setLoadStep]     = useState(0)
  const [traceResult, setTrace]     = useState(null)
  const [riskResult, setRisk]       = useState(null)
  const [error, setError]           = useState('')
  const sessionId = useRef(`sess_${Date.now()}`)

  const STEPS = [
    'Ingesting blockchain transactions…',
    'Building transaction graph…',
    'Running clustering engine…',
    'Tracing fund paths…',
    'Attributing exchanges…',
    'Computing ML risk score…',
  ]

  const run = useCallback(async (addr) => {
    const seed = (addr || address).trim()
    if (!seed) return
    setError(''); setLoading(true); setTrace(null); setRisk(null); setLoadStep(0)

    try {
      // Step through the pipeline with visual feedback
      for (let i = 0; i < STEPS.length - 1; i++) {
        setLoadStep(i)
        await new Promise(r => setTimeout(r, 400))
      }
      // Real blockchain trace
      const trace = await traceWallet(seed, maxHops)
      setTrace(trace)
      setLoadStep(5)

      // ML risk score using blockchain output
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
      const risk = await getRiskScore(seed, bcFeatures, {})
      setRisk(risk)
    } catch (e) {
      setError(`Error: ${e.message}. Make sure the Blockchain (port 8000) and ML (port 8002) services are running.`)
    } finally {
      setLoading(false)
    }
  }, [address, maxHops])

  return (
    <div className="flex flex-col h-full">
      {/* Wallet input bar */}
      <div className="px-space-base py-space-md border-b border-border-subtle flex-shrink-0 bg-surface-container-low/50">
        <div className="flex gap-space-sm items-center">
          <div className="flex-1 relative">
            <input
              value={address}
              onChange={e => setAddress(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && run()}
              placeholder="Enter victim or suspicious wallet address (TRC20)…"
              className="w-full bg-surface-container border border-border-subtle rounded-lg px-space-base py-space-sm font-code-base text-code-base text-on-surface placeholder:text-on-surface-variant/50 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
            />
          </div>
          <select
            value={maxHops}
            onChange={e => setMaxHops(+e.target.value)}
            className="bg-surface-container border border-border-subtle rounded-lg px-space-sm py-space-sm font-code-sm text-code-sm text-on-surface-variant outline-none cursor-pointer"
          >
            {[2,3,4,5].map(h => <option key={h} value={h}>{h} hops</option>)}
          </select>
          <button
            onClick={() => run()}
            disabled={loading || !address.trim()}
            className="px-space-lg py-space-sm bg-primary text-on-primary font-body-medium text-body-medium font-bold rounded-lg disabled:opacity-40 hover:brightness-110 transition-all active:scale-95"
          >
            {loading ? 'Tracing…' : 'Trace Wallet'}
          </button>
          <button
            onClick={() => { setAddress(DEMO_ADDRESS); run(DEMO_ADDRESS) }}
            disabled={loading}
            className="px-space-base py-space-sm border border-outline text-on-surface-variant font-code-sm text-code-sm rounded-lg hover:bg-surface-container hover:text-on-surface transition-colors disabled:opacity-40"
          >
            Demo
          </button>
        </div>
        {error && (
          <div className="mt-space-sm px-space-sm py-space-xs bg-status-danger-bg text-error font-code-sm text-code-sm rounded-lg border border-error/20">
            {error}
          </div>
        )}
      </div>

      {/* Main content area */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Graph panel */}
        <div className="flex-1 relative border-r border-border-subtle flex flex-col">
          <GraphView traceResult={traceResult} loading={loading} loadSteps={STEPS} loadStep={loadStep} onDemo={() => { setAddress(DEMO_ADDRESS); run(DEMO_ADDRESS) }} />
        </div>

        {/* Right sidebar — risk + cluster + exchange */}
        <div className="w-96 flex flex-col overflow-y-auto bg-surface-container-low/30">
          <RiskPanel riskResult={riskResult} loading={loading} />
          <ExchangePanel traceResult={traceResult} loading={loading} />
          <ClusterPanel traceResult={traceResult} loading={loading} />
        </div>
      </div>

      {/* Bottom agent chat */}
      <div className="flex-shrink-0 border-t border-border-subtle" style={{ height: '200px' }}>
        <AgentChat sessionId={sessionId.current} traceResult={traceResult} riskResult={riskResult} />
      </div>
    </div>
  )
}
