// src/components/ExchangePanel.jsx
// Causally linked to GraphView terminal node arrival with scale-in & highlight flash
import React, { useState, useEffect } from 'react'

export default function ExchangePanel({ traceResult, loading, terminalReached = true }) {
  const attr = traceResult?.attribution
  const isRevealed = attr && terminalReached

  return (
    <div className="border-b border-border-subtle p-space-base flex-shrink-0 transition-all duration-300">
      <div className="font-label-caps text-label-caps text-outline tracking-wider mb-space-sm flex items-center gap-space-xs">
        <span className={`w-2 h-2 rounded-full transition-colors ${isRevealed ? 'bg-primary animate-pulse' : 'bg-outline/50'}`} />
        EXCHANGE ATTRIBUTION
      </div>

      {!attr && !loading && (
        <p className="font-code-sm text-code-sm text-on-surface-variant">Run a trace to see attribution.</p>
      )}

      {(loading || (attr && !terminalReached)) && (
        <div className="animate-pulse space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-ping" />
            <span className="font-code-sm text-xs text-primary">Tracing hops to identify terminal exchange…</span>
          </div>
          <div className="h-5 bg-surface-container-high rounded w-2/3" />
          <div className="h-3 bg-surface-container rounded w-1/2" />
          <div className="h-2 bg-surface-container rounded w-full" />
        </div>
      )}

      {isRevealed && (
        <div className="space-y-space-sm animate-in">
          <div className="flex items-center justify-between">
            <div>
              {attr.status === 'KNOWN' ? (
                <div className="font-headline-md text-headline-md font-bold text-primary animate-in">
                  {attr.exchange_name}
                </div>
              ) : (
                <div className="font-title-sm text-title-sm font-semibold text-on-surface-variant">UNATTRIBUTED</div>
              )}
              {attr.entity_type && (
                <div className="font-code-sm text-code-sm text-outline">{attr.entity_type}</div>
              )}
            </div>
            <span className={`font-label-caps text-label-caps px-space-xs py-space-2xs rounded border animate-badge-flash ${
              attr.status === 'KNOWN'
                ? 'bg-status-trace-bg text-primary border-primary/30'
                : 'bg-surface-container text-outline border-border-subtle'}`}>
              {attr.status}
            </span>
          </div>

          {attr.deposit_address && (
            <div className="bg-surface-container-low p-space-xs rounded-lg">
              <div className="font-label-caps text-label-caps text-outline mb-space-2xs">DEPOSIT ADDRESS</div>
              <div className="font-code-sm text-code-sm text-on-surface break-all">{attr.deposit_address}</div>
            </div>
          )}

          {/* Confidence bar */}
          <div>
            <div className="flex justify-between font-code-sm text-code-sm text-on-surface-variant mb-space-2xs">
              <span>Attribution Confidence</span>
              <span className="text-primary font-bold">{(attr.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="h-1.5 bg-surface-container-high rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary to-secondary"
                style={{ width: `${attr.confidence * 100}%`, transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)' }}
              />
            </div>
          </div>

          {attr.recommendation && (
            <div className="bg-surface-container-low p-space-xs rounded-lg">
              <div className="font-label-caps text-label-caps text-secondary mb-space-2xs">RECOMMENDATION</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant">{attr.recommendation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
