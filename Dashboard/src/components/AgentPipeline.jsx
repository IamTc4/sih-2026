// src/components/AgentPipeline.jsx
// Live agent reasoning trace panel — lights up each LangGraph stage as it executes
import React, { useState, useEffect } from 'react'

const PIPELINE_STAGES = [
  { stage: 'Intake',                label: 'Intake & Validation',    icon: '⬡', color: 'text-primary' },
  { stage: 'Trace',                 label: 'Blockchain Trace',       icon: '⬢', color: 'text-primary' },
  { stage: 'Cluster',               label: 'Address Clustering',     icon: '◈', color: 'text-status-warning' },
  { stage: 'RiskScore',             label: 'ML Risk Scoring',        icon: '◉', color: 'text-error' },
  { stage: 'Attribute',             label: 'Exchange Attribution',   icon: '⊞', color: 'text-primary' },
  { stage: 'DraftNotice',           label: 'Draft Legal Notice',     icon: '⚖', color: 'text-secondary' },
  { stage: 'RecommendManualReview', label: 'Manual Review Flag',     icon: '⊘', color: 'text-status-warning' },
  { stage: 'Log',                   label: 'Tamper-Proof Log',       icon: '⛓', color: 'text-outline' },
  { stage: 'Respond',               label: 'LLM Response',           icon: '◎', color: 'text-secondary' },
]

function StatusIcon({ status }) {
  if (status === 'complete') return <span className="text-secondary animate-stage-in">✓</span>
  if (status === 'skipped')  return <span className="text-outline/60 animate-stage-in">⊘</span>
  if (status === 'error')    return <span className="text-error animate-stage-in">✕</span>
  if (status === 'active')   return (
    <span className="inline-flex gap-0.5">
      {[0,1,2].map(i => (
        <span key={i} className="w-1 h-1 rounded-full bg-primary animate-bounce"
          style={{ animationDelay: `${i * 0.12}s` }} />
      ))}
    </span>
  )
  return <span className="w-2 h-2 rounded-full border border-outline/30 inline-block" />
}

export default function AgentPipeline({ toolCalls = [], isRunning = false, collapsed: initCollapsed = false }) {
  const [collapsed, setCollapsed] = useState(initCollapsed)
  const [liveStep, setLiveStep]   = useState(-1)

  // Stagger in-flight execution indicator (450ms per stage)
  useEffect(() => {
    if (!isRunning) {
      setLiveStep(-1)
      return
    }
    setLiveStep(0)
    const interval = setInterval(() => {
      setLiveStep(s => (s < PIPELINE_STAGES.length - 2 ? s + 1 : s))
    }, 480)
    return () => clearInterval(interval)
  }, [isRunning])

  // Build a lookup by stage name
  const traceMap = {}
  toolCalls.forEach(tc => { traceMap[tc.stage] = tc })

  // Determine stage state
  const completedCount = toolCalls.length
  const finalDecision = traceMap['Log']
    ? (traceMap['DraftNotice'] ? 'NOTICE DRAFTED' : 'MANUAL REVIEW')
    : null

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="w-full flex items-center justify-between px-3 py-2 bg-surface-container-low border-b border-border-subtle hover:bg-surface-container transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          <span className="font-label-caps text-label-caps text-on-surface-variant tracking-wider">AGENT PIPELINE</span>
          {finalDecision && (
            <span className={`font-code-sm text-code-sm px-1.5 py-0.5 rounded text-[10px] border ${
              finalDecision === 'NOTICE DRAFTED'
                ? 'bg-status-success-bg text-secondary border-secondary/30'
                : 'bg-status-warning-bg text-status-warning border-status-warning/30'
            }`}>{finalDecision}</span>
          )}
        </div>
        <span className="text-outline/60 text-xs">▾ expand</span>
      </button>
    )
  }

  return (
    <div className="border-b border-border-subtle flex-shrink-0 bg-surface-container-lowest/40">
      {/* Header */}
      <button
        onClick={() => setCollapsed(true)}
        className="w-full flex items-center justify-between px-3 py-2 border-b border-border-subtle/50 hover:bg-surface-container/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className={`w-1.5 h-1.5 rounded-full ${isRunning ? 'bg-primary animate-pulse' : completedCount > 0 ? 'bg-secondary' : 'bg-outline/40'}`} />
          <span className="font-label-caps text-label-caps text-on-surface-variant tracking-wider">AGENT REASONING TRACE</span>
          {isRunning && (
            <span className="font-code-sm text-code-sm text-primary animate-pulse">orchestrating…</span>
          )}
          {finalDecision && !isRunning && (
            <span className={`font-code-sm text-code-sm px-1.5 py-0.5 rounded text-[10px] border ${
              finalDecision === 'NOTICE DRAFTED'
                ? 'bg-status-success-bg text-secondary border-secondary/30'
                : 'bg-status-warning-bg text-status-warning border-status-warning/30'
            }`}>{finalDecision}</span>
          )}
        </div>
        <span className="text-outline/60 text-xs">▴ collapse</span>
      </button>

      {/* Pipeline stages */}
      <div className="px-3 py-2 space-y-0.5">
        {PIPELINE_STAGES.map((ps, i) => {
          const trace = traceMap[ps.stage]
          const isDone   = !!trace || (isRunning && i < liveStep)
          const isActive = isRunning && i === liveStep
          const isPending = !isDone && !isActive

          // Skip stages that weren't hit AND we have completed results (e.g. DraftNotice vs ManualReview)
          const shouldDim = completedCount > 0 && isPending &&
            (ps.stage === 'DraftNotice' || ps.stage === 'RecommendManualReview') &&
            !trace

          return (
            <div
              key={ps.stage}
              className={`flex items-center gap-2 px-2 py-1.5 rounded transition-all duration-300 ${
                isActive ? 'bg-primary/15 border border-primary/40 animate-stage-in shadow-sm shadow-primary/20' :
                isDone   ? 'opacity-95' : shouldDim ? 'opacity-25' : 'opacity-35'
              }`}
              style={{ animationDelay: `${i * 40}ms` }}
            >
              {/* Status icon */}
              <div className="w-5 flex items-center justify-center flex-shrink-0">
                <StatusIcon status={
                  isActive ? 'active' :
                  trace?.status === 'skipped' ? 'skipped' :
                  trace?.status === 'error' ? 'error' :
                  isDone ? 'complete' : 'idle'
                } />
              </div>

              {/* Stage label */}
              <div className="flex-1 min-w-0">
                <div className={`font-code-sm text-code-sm font-bold ${
                  isActive ? 'text-primary' :
                  isDone ? (trace.status === 'skipped' ? 'text-outline/60' : ps.color) :
                  'text-outline/40'
                }`}>
                  {ps.icon} {ps.label}
                </div>
                {isDone && trace.summary && (
                  <div className="font-code-sm text-code-sm text-outline/60 truncate text-[10px] mt-0.5 animate-stage-in">
                    {trace.summary}
                  </div>
                )}
              </div>

              {/* Elapsed time */}
              {isDone && trace.elapsed_ms > 0 && (
                <div className="font-code-sm text-code-sm text-outline/50 flex-shrink-0 tabular-nums text-[10px]">
                  {trace.elapsed_ms < 1000 ? `${trace.elapsed_ms}ms` : `${(trace.elapsed_ms / 1000).toFixed(1)}s`}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
