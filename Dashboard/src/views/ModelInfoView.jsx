// src/views/ModelInfoView.jsx
// ML Model Card view — fetches from GET /api/ml/model-info
import React, { useState, useEffect } from 'react'
import { getModelInfo, mlHealth } from '../services/api'

export default function ModelInfoView() {
  const [info, setInfo]     = useState(null)
  const [health, setHealth] = useState(null)
  const [error, setError]   = useState('')

  useEffect(() => {
    Promise.all([getModelInfo(), mlHealth()])
      .then(([i, h]) => { setInfo(i); setHealth(h) })
      .catch(e => setError(e.message))
  }, [])

  return (
    <div className="p-space-xl max-w-4xl mx-auto">
      <div className="mb-space-xl">
        <div className="flex items-center gap-space-sm mb-space-xs">
          <span className="w-3 h-3 rounded-full bg-primary" />
          <span className="font-label-caps text-label-caps text-outline tracking-wider">ML MODULE</span>
        </div>
        <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface mb-space-xs">ML Risk Model Card</h1>
        <p className="font-body-base text-body-base text-on-surface-variant">
          Transparency report for the XGBoost risk-scoring model. Required for judicial/courtroom defensibility.
        </p>
      </div>

      {error && (
        <div className="bg-status-danger-bg border border-error/20 rounded-xl p-space-base mb-space-xl text-error font-code-sm text-code-sm">
          {error} — Make sure the ML service is running on port 8002.
        </div>
      )}

      {!info && !error && (
        <div className="animate-pulse space-y-4">
          {[1,2,3,4].map(i => <div key={i} className="h-24 bg-surface-container rounded-xl" />)}
        </div>
      )}

      {info && (
        <div className="space-y-space-lg">
          {/* Health */}
          {health && (
            <div className={`rounded-xl p-space-base border flex items-center gap-space-md ${health.model_trained ? 'bg-status-success-bg border-secondary/20' : 'bg-status-warning-bg border-status-warning/20'}`}>
              <span className="text-2xl">{health.model_trained ? '✅' : '⚠️'}</span>
              <div>
                <div className={`font-title-sm text-title-sm font-bold ${health.model_trained ? 'text-secondary' : 'text-status-warning'}`}>
                  {health.model_trained ? 'Trained Model Loaded' : 'Using Rule-Based Fallback'}
                </div>
                <div className="font-code-sm text-code-sm text-on-surface-variant">
                  {health.model_trained ? `${info.model_version} • ${health.features} features` : 'Run python train.py in the ML/ directory to train'}
                </div>
              </div>
            </div>
          )}

          {/* Algorithm */}
          <div className="bg-surface-container rounded-xl p-space-lg border border-border-subtle">
            <div className="font-label-caps text-label-caps text-outline tracking-wider mb-space-sm">ALGORITHM</div>
            <div className="font-title-sm text-title-sm font-bold text-primary mb-space-xs">{info.algorithm}</div>
            <div className="font-body-sm text-body-sm text-on-surface-variant">{info.training_data}</div>
          </div>

          {/* Metrics */}
          <div className="bg-surface-container rounded-xl p-space-lg border border-border-subtle">
            <div className="font-label-caps text-label-caps text-outline tracking-wider mb-space-sm">EVALUATION METRICS</div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-sm">
              {Object.entries(info.evaluation_metrics).filter(([k]) => k !== 'note').map(([k, v]) => (
                <div key={k} className="bg-surface-container-high rounded-lg p-space-sm text-center">
                  <div className="font-display-lg text-headline-lg font-bold text-primary">{(v * 100).toFixed(0)}%</div>
                  <div className="font-label-caps text-label-caps text-outline mt-space-2xs">{k.replace(/_/g, ' ').toUpperCase()}</div>
                </div>
              ))}
            </div>
            <p className="font-code-sm text-code-sm text-outline mt-space-sm italic">{info.evaluation_metrics.note}</p>
          </div>

          {/* Features */}
          <div className="bg-surface-container rounded-xl p-space-lg border border-border-subtle">
            <div className="font-label-caps text-label-caps text-outline tracking-wider mb-space-sm">FEATURES ({info.features?.length})</div>
            <div className="flex flex-wrap gap-space-xs">
              {info.features?.map(f => (
                <span key={f} className="font-code-sm text-code-sm bg-surface-container-high border border-border-subtle text-on-surface-variant px-space-xs py-space-2xs rounded">
                  {f}
                </span>
              ))}
            </div>
          </div>

          {/* Limitations */}
          <div className="bg-status-warning-bg border border-status-warning/20 rounded-xl p-space-lg">
            <div className="font-label-caps text-label-caps text-status-warning tracking-wider mb-space-sm">⚠ KNOWN LIMITATIONS</div>
            <ul className="space-y-space-xs">
              {info.known_limitations?.map((l, i) => (
                <li key={i} className="flex items-start gap-space-xs font-body-sm text-body-sm text-on-surface-variant">
                  <span className="text-status-warning mt-0.5 flex-shrink-0">•</span>
                  <span>{l}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
