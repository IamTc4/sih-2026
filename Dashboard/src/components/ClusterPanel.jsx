// src/components/ClusterPanel.jsx
import React, { useState } from 'react'

export default function ClusterPanel({ traceResult, loading }) {
  const clusters = traceResult?.clusters ?? []
  const [expanded, setExpanded] = useState(null)

  return (
    <div className="p-space-base flex-shrink-0">
      <div className="font-label-caps text-label-caps text-outline tracking-wider mb-space-sm flex items-center gap-space-xs">
        <span className="w-2 h-2 rounded-full bg-status-warning" />
        ADDRESS CLUSTERS
      </div>

      {!clusters.length && !loading && (
        <p className="font-code-sm text-code-sm text-on-surface-variant">No clusters found yet.</p>
      )}

      {loading && !clusters.length && (
        <div className="animate-pulse space-y-2">
          {[1,2].map(i => <div key={i} className="h-12 bg-surface-container-high rounded" />)}
        </div>
      )}

      <div className="space-y-space-xs">
        {clusters.map((c, i) => (
          <div key={c.cluster_id} className="bg-surface-container rounded-lg border border-border-subtle overflow-hidden">
            <button
              className="w-full flex items-center justify-between p-space-sm text-left hover:bg-surface-container-high transition-colors"
              onClick={() => setExpanded(expanded === i ? null : i)}
            >
              <div className="flex items-center gap-space-xs">
                <span className="font-code-base text-code-base text-primary font-bold">{c.cluster_id}</span>
                <span className="font-body-sm text-body-sm text-on-surface-variant">{c.addresses.length} addresses</span>
              </div>
              <div className="flex items-center gap-space-xs">
                <span className="font-code-sm text-code-sm text-status-warning px-space-xs py-space-2xs bg-status-warning-bg rounded">
                  {c.primary_heuristic?.replace(/_/g, ' ')}
                </span>
                <span className="text-on-surface-variant">{expanded === i ? '▴' : '▾'}</span>
              </div>
            </button>

            {expanded === i && (
              <div className="px-space-sm pb-space-sm space-y-space-2xs">
                {c.addresses.map(addr => (
                  <div key={addr} className="flex items-center gap-space-xs bg-surface-container-low px-space-xs py-space-2xs rounded font-code-sm text-code-sm text-on-surface">
                    <span className="w-1.5 h-1.5 rounded-full bg-status-warning flex-shrink-0" />
                    <span className="truncate">{addr}</span>
                  </div>
                ))}
                {c.evidence_chain?.slice(0, 2).map((ev, j) => (
                  <div key={j} className="text-outline font-code-sm text-code-sm p-space-xs bg-surface-container-high rounded">
                    <div className="text-secondary font-bold">{ev.heuristic_name?.replace(/_/g, ' ')}</div>
                    <div className="mt-space-2xs">{ev.explanation}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
