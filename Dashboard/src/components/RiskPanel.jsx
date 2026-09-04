// src/components/RiskPanel.jsx
// ML Risk Score card for the right sidebar
import React from 'react'

function RiskGauge({ score }) {
  const r   = 30
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - score)
  const color = score >= 0.75 ? '#ffb4ab' : score >= 0.45 ? '#fbbf24' : '#4edea3'
  return (
    <svg width="80" height="80" viewBox="0 0 80 80">
      <circle cx="40" cy="40" r={r} fill="none" stroke="#1c2b3c" strokeWidth="8" />
      <circle
        cx="40" cy="40" r={r} fill="none"
        stroke={color} strokeWidth="8"
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 40 40)"
        style={{ transition: 'stroke-dashoffset 0.8s ease' }}
      />
      <text x="40" y="45" textAnchor="middle" fill={color} fontSize="14" fontWeight="700" fontFamily="JetBrains Mono">
        {Math.round(score * 100)}
      </text>
    </svg>
  )
}

export default function RiskPanel({ riskResult, loading }) {
  const skeleton = loading && !riskResult

  return (
    <div className="border-b border-border-subtle p-space-base flex-shrink-0">
      <div className="font-label-caps text-label-caps text-outline tracking-wider mb-space-sm flex items-center gap-space-xs">
        <span className="w-2 h-2 rounded-full bg-error animate-pulse" />
        ML RISK SCORE
      </div>

      {!riskResult && !loading && (
        <p className="font-code-sm text-code-sm text-on-surface-variant">Run a trace to see the ML risk score.</p>
      )}

      {skeleton && (
        <div className="flex items-center gap-space-base animate-pulse">
          <div className="w-20 h-20 rounded-full bg-surface-container-high" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-surface-container-high rounded w-3/4" />
            <div className="h-3 bg-surface-container rounded w-1/2" />
          </div>
        </div>
      )}

      {riskResult && (
        <>
          <div className="flex items-center gap-space-base mb-space-sm">
            <RiskGauge score={riskResult.risk_score} />
            <div className="flex-1">
              <div className={`font-title-sm text-title-sm font-bold mb-space-2xs ${
                riskResult.confidence === 'high' ? 'text-error' :
                riskResult.confidence === 'medium' ? 'text-status-warning' : 'text-secondary'}`}>
                {riskResult.confidence?.toUpperCase()} RISK
              </div>
              <div className={`font-code-sm text-code-sm px-space-xs py-space-2xs rounded inline-block border ${
                riskResult.confidence === 'high'   ? 'bg-status-danger-bg text-error border-error/30' :
                riskResult.confidence === 'medium' ? 'bg-status-warning-bg text-status-warning border-status-warning/30' :
                'bg-status-success-bg text-secondary border-secondary/30'}`}>
                {riskResult.confidence} confidence
              </div>
              <div className="font-code-sm text-code-sm text-outline mt-space-2xs">{riskResult.model_version}</div>
            </div>
          </div>

          {/* Top factors */}
          <div className="space-y-space-xs">
            {(riskResult.top_factors ?? []).map((f, i) => (
              <div key={i} className="flex flex-col gap-space-2xs">
                <div className="flex justify-between items-center">
                  <span className="font-body-sm text-body-sm text-on-surface-variant truncate flex-1 pr-2">{f.plain_text}</span>
                  <span className="font-code-sm text-code-sm text-primary flex-shrink-0">{(f.contribution * 100).toFixed(1)}%</span>
                </div>
                <div className="h-1 bg-surface-container-high rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-primary to-error"
                    style={{ width: `${Math.min(100, f.contribution * 400)}%`, transition: 'width 0.8s ease' }}
                  />
                </div>
              </div>
            ))}
          </div>

          {riskResult.behavioral_similarity && (
            <div className="mt-space-sm p-space-xs bg-status-warning-bg border border-status-warning/20 rounded-lg">
              <span className="font-label-caps text-label-caps text-status-warning">BEHAVIORAL SIMILARITY (LOW CONFIDENCE)</span>
              <p className="font-code-sm text-code-sm text-on-surface-variant mt-space-2xs">
                {riskResult.behavioral_similarity.similar_addresses.length} similar addresses detected (score: {(riskResult.behavioral_similarity.similarity_score * 100).toFixed(0)}%)
              </p>
            </div>
          )}

          <p className="font-body-sm text-body-sm text-outline mt-space-sm italic">{riskResult.disclaimer}</p>
        </>
      )}
    </div>
  )
}
