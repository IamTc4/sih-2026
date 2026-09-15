// src/components/RiskPanel.jsx
// ML Risk Score card — animated gauge with live count-up & color transitions, staggered factor bars
import React, { useState, useEffect, useCallback } from 'react'

function RiskGauge({ score, onFinish, onScoreUpdate }) {
  const [currentVal, setCurrentVal] = useState(0)
  const targetPercent = Math.round((score ?? 0) * 100)

  useEffect(() => {
    setCurrentVal(0)
    let startTimestamp = null
    const duration = 900 // 900ms ease-out
    let animId = null

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / duration, 1)
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const val = Math.round(eased * targetPercent)
      setCurrentVal(val)
      if (onScoreUpdate) onScoreUpdate(val)

      if (progress < 1) {
        animId = requestAnimationFrame(step)
      } else {
        if (onFinish) onFinish()
      }
    }

    animId = requestAnimationFrame(step)
    return () => cancelAnimationFrame(animId)
  }, [targetPercent, onFinish, onScoreUpdate])

  const r = 38
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - currentVal / 100)

  // Transition color dynamically as number crosses thresholds (<40 green, 40-70 amber, 70+ red)
  const color = currentVal >= 70 ? '#ff6b6b' : currentVal >= 40 ? '#fbbf24' : '#4edea3'
  const glow = currentVal >= 70
    ? '0 0 28px rgba(255,107,107,0.7), 0 0 56px rgba(255,107,107,0.3)'
    : currentVal >= 40
    ? '0 0 20px rgba(251,191,36,0.5)'
    : '0 0 20px rgba(78,222,163,0.4)'

  return (
    <div className="relative">
      <svg width="100" height="100" viewBox="0 0 100 100" style={{ filter: `drop-shadow(${glow})` }}>
        {/* Outer decorative ring */}
        <circle cx="50" cy="50" r={r + 8} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
        {/* Track */}
        <circle cx="50" cy="50" r={r} fill="none" stroke="#1c2b3c" strokeWidth="9" />
        {/* Fill */}
        <circle
          cx="50" cy="50" r={r} fill="none"
          stroke={color} strokeWidth="9"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: 'stroke 0.2s ease, filter 0.2s ease' }}
        />
        {/* Outer ring pulse for high risk once count reaches high */}
        {currentVal >= 70 && (
          <circle cx="50" cy="50" r={r + 8} fill="none" stroke="rgba(255,107,107,0.25)"
            strokeWidth="2" className="animate-ping" style={{ animationDuration: '1.8s' }} />
        )}
        {/* Score text */}
        <text x="50" y="55" textAnchor="middle" fill={color} fontSize="20" fontWeight="800"
          fontFamily="JetBrains Mono" className="tabular-nums transition-colors duration-150">{currentVal}</text>
        <text x="50" y="66" textAnchor="middle" fill="rgba(135,146,154,0.7)" fontSize="8"
          fontFamily="JetBrains Mono" letterSpacing="2">RISK</text>
      </svg>
    </div>
  )
}

export default function RiskPanel({ riskResult, loading }) {
  const [displayedScore, setDisplayedScore] = useState(0)
  const [gaugeComplete, setGaugeComplete]   = useState(false)
  const [showBehavioral, setShowBehavioral] = useState(false)

  useEffect(() => {
    setDisplayedScore(0)
    setGaugeComplete(false)
    setShowBehavioral(false)
  }, [riskResult])

  const handleGaugeFinish = useCallback(() => {
    setGaugeComplete(true)
    setTimeout(() => {
      setShowBehavioral(true)
    }, 300)
  }, [])

  const skeleton  = loading && !riskResult
  const currentRiskIsHigh = displayedScore >= 70
  const currentRiskIsMed  = displayedScore >= 40 && displayedScore < 70
  const currentRiskIsLow  = displayedScore < 40

  return (
    <div
      className={`border-b border-border-subtle p-4 flex-shrink-0 transition-all`}
      style={{
        background: currentRiskIsHigh && gaugeComplete
          ? 'rgba(255,50,50,0.04)'
          : 'transparent',
        border: currentRiskIsHigh && gaugeComplete
          ? '1px solid rgba(255,107,107,0.25)'
          : undefined,
        boxShadow: currentRiskIsHigh && gaugeComplete
          ? 'inset 0 0 40px rgba(255,50,50,0.06), 0 0 0 1px rgba(255,107,107,0.15)'
          : undefined,
        transition: 'all 0.5s ease',
        borderBottom: '1px solid rgba(255,255,255,0.07)',
      }}
    >
      {/* Header row */}
      <div className="font-label-caps text-label-caps text-outline/80 tracking-widest mb-3 flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full transition-colors duration-200 ${
          currentRiskIsHigh ? 'bg-error animate-pulse' : currentRiskIsMed ? 'bg-status-warning' : 'bg-secondary'
        }`} />
        ML RISK SCORE
        <span style={{
          marginLeft: 'auto',
          fontSize: '.58rem',
          fontFamily: 'var(--font-mono)',
          color: 'rgba(255,255,255,0.25)',
          letterSpacing: '.06em',
        }}>
          XGBoost · SHAP
        </span>
        {riskResult && (
          <span className={`font-code-sm text-code-sm px-1.5 py-0.5 rounded border transition-colors duration-200 ${
            currentRiskIsHigh ? 'bg-status-danger-bg text-error border-error/30' :
            currentRiskIsMed  ? 'bg-status-warning-bg text-status-warning border-status-warning/30' :
                                'bg-status-success-bg text-secondary border-secondary/30'
          }`}>
            {currentRiskIsHigh ? 'HIGH' : currentRiskIsMed ? 'MEDIUM' : 'LOW'}
          </span>
        )}
      </div>

      {!riskResult && !loading && (
        <p className="font-code-sm text-code-sm text-on-surface-variant/50">Run a trace to see the ML risk score.</p>
      )}

      {skeleton && (
        <div className="flex items-center gap-4 animate-pulse">
          <div className="w-[100px] h-[100px] rounded-full bg-surface-container-high" />
          <div className="flex-1 space-y-2">
            <div className="h-5 bg-surface-container-high rounded w-3/4" />
            <div className="h-3 bg-surface-container rounded w-1/2" />
            <div className="h-3 bg-surface-container rounded w-1/3" />
          </div>
        </div>
      )}

      {riskResult && (
        <>
          {/* Gauge + label row */}
          <div className="flex items-center gap-4 mb-3">
            <RiskGauge
              score={riskResult.risk_score}
              onFinish={handleGaugeFinish}
              onScoreUpdate={setDisplayedScore}
            />
            <div className="flex-1">
              <div className={`font-headline-md text-headline-md font-bold mb-1 transition-colors duration-200 ${
                currentRiskIsHigh ? 'text-error' : currentRiskIsMed ? 'text-status-warning' : 'text-secondary'
              }`}>
                {currentRiskIsHigh ? '⚠ HIGH RISK' : currentRiskIsMed ? '⚡ MEDIUM RISK' : '✓ LOW RISK'}
              </div>
              <div className="font-code-sm text-code-sm text-outline/70">{riskResult.model_version}</div>

              {/* IMMEDIATE FREEZE badge — fires after gauge complete */}
              {currentRiskIsHigh && gaugeComplete && (
                <div style={{
                  marginTop: '.6rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '.45rem',
                  padding: '.35rem .75rem',
                  borderRadius: '6px',
                  background: 'rgba(239,68,68,0.12)',
                  border: '1px solid rgba(239,68,68,0.4)',
                  boxShadow: '0 0 16px rgba(239,68,68,0.2)',
                  animation: 'pulse 1.8s infinite',
                }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#ef4444', animation: 'pulse 1s infinite', display: 'inline-block' }} />
                  <span style={{
                    fontSize: '.65rem', fontFamily: 'var(--font-mono)',
                    color: '#f87171', fontWeight: 800, letterSpacing: '.07em',
                  }}>
                    IMMEDIATE FREEZE RECOMMENDED
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* SHAP Explainability label */}
          {riskResult.top_factors?.length > 0 && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '.5rem',
              marginBottom: '.65rem',
            }}>
              <span style={{
                fontSize: '.58rem', fontFamily: 'var(--font-mono)', letterSpacing: '.1em',
                color: 'rgba(255,255,255,0.3)', fontWeight: 700,
              }}>
                SHAP EXPLAINABILITY FACTORS
              </span>
              <span style={{
                fontSize: '.58rem', padding: '.1rem .4rem', borderRadius: '3px',
                background: 'rgba(167,139,250,0.12)', border: '1px solid rgba(167,139,250,0.25)',
                color: '#a78bfa', fontFamily: 'var(--font-mono)', fontWeight: 700,
              }}>NO BLACK BOX</span>
            </div>
          )}

          {/* Factor bars — staggered */}
          <div className="space-y-2">
            {(riskResult.top_factors ?? []).map((f, i) => (
              <div key={i} className="flex flex-col gap-1" style={{ animationDelay: `${i * 120}ms` }}>
                <div className="flex justify-between items-center">
                  <span className="font-body-sm text-body-sm text-on-surface-variant/80 truncate flex-1 pr-2">
                    {f.plain_text}
                  </span>
                  <span className="font-code-sm text-code-sm text-primary flex-shrink-0 tabular-nums">
                    {(f.contribution * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-1.5 bg-surface-container-high rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full animate-bar-grow"
                    style={{
                      width: `${Math.min(100, f.contribution * 400)}%`,
                      background: `linear-gradient(90deg, #8ed5ff, ${currentRiskIsHigh ? '#ff6b6b' : currentRiskIsMed ? '#fbbf24' : '#4edea3'})`,
                      transition: 'width 1s cubic-bezier(0.34,1.56,0.64,1)',
                      animationDelay: `${i * 120}ms`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Fraud Typology Classification Card */}
          {riskResult.fraud_typology && (
            <div className="mt-3 p-2.5 rounded-lg border border-primary/30 bg-primary/5 transition-all">
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className="font-label-caps text-[10px] uppercase tracking-wider text-primary font-bold flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                  CLASSIFIED FRAUD TYPOLOGY
                </span>
                <span className="font-code-sm text-[10px] px-1.5 py-0.5 rounded bg-primary/15 text-primary border border-primary/20 font-bold">
                  {Math.round((riskResult.fraud_typology.confidence ?? 0.85) * 100)}% CONF
                </span>
              </div>

              <div className="font-body-md text-sm font-semibold text-on-surface text-cyan-300">
                {riskResult.fraud_typology.typology_name}
              </div>

              {riskResult.fraud_typology.modus_operandi && (
                <p className="font-body-sm text-[11px] text-on-surface-variant/80 mt-1 line-clamp-2">
                  {riskResult.fraud_typology.modus_operandi}
                </p>
              )}

              {riskResult.fraud_typology.indicators?.length > 0 && (
                <div className="mt-2 pt-2 border-t border-white/5 space-y-1">
                  {riskResult.fraud_typology.indicators.slice(0, 2).map((ind, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-[10px] text-outline">
                      <span className="text-amber-400">⚡</span>
                      <span className="flex-1 truncate">{ind}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Behavioral match — fades and slides in 300ms AFTER gauge finishes */}
          {riskResult.behavioral_similarity && showBehavioral && (
            <div className="mt-3 p-2 bg-status-warning-bg border border-status-warning/20 rounded-lg animate-in">
              <span className="font-label-caps text-label-caps text-status-warning">BEHAVIORAL MATCH</span>
              <p className="font-code-sm text-code-sm text-on-surface-variant mt-1">
                {riskResult.behavioral_similarity.similar_addresses.length} similar addresses (score: {(riskResult.behavioral_similarity.similarity_score * 100).toFixed(0)}%)
              </p>
            </div>
          )}

          <p className="font-body-sm text-body-sm text-outline/50 mt-2 italic text-[11px]">{riskResult.disclaimer}</p>
        </>
      )}
    </div>
  )
}
