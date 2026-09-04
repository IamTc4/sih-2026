// src/components/GraphView.jsx
// Cytoscape.js transaction graph — nodes = wallets, edges = USDT transfers
import React, { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import fcose from 'cytoscape-fcose'

cytoscape.use(fcose)

const NODE_COLOR = {
  seed:     '#8ed5ff',   // victim
  terminal: '#ff938c',   // exchange / terminal
  cluster:  '#fbbf24',   // clustered mule
  default:  '#4edea3',   // intermediate
}

function buildElements(traceResult) {
  if (!traceResult) return []
  const els = []
  const nodes = traceResult.graph?.nodes ?? []
  const edges = traceResult.graph?.edges ?? []
  const clusterMembers = new Set(
    (traceResult.clusters ?? []).flatMap(c => c.addresses)
  )

  nodes.forEach(n => {
    let color = NODE_COLOR.default
    if (n.is_seed) color = NODE_COLOR.seed
    else if (n.is_terminal) color = NODE_COLOR.terminal
    else if (clusterMembers.has(n.id)) color = NODE_COLOR.cluster

    els.push({
      data: {
        id: n.id,
        label: n.label ?? n.id.slice(0, 12) + '…',
        color,
        size: n.is_seed ? 40 : n.is_terminal ? 32 : 22,
        is_seed: n.is_seed,
        is_terminal: n.is_terminal,
      }
    })
  })

  edges.forEach((e, i) => {
    els.push({
      data: {
        id: `e${i}`,
        source: e.source,
        target: e.target,
        label: `${e.amount?.toLocaleString('en-IN', { maximumFractionDigits: 0 })} USDT`,
        width: Math.max(1, Math.min(8, Math.log10(e.amount + 1) * 2)),
      }
    })
  })

  return els
}

export default function GraphView({ traceResult, loading, loadSteps, loadStep, onDemo }) {
  const containerRef = useRef(null)
  const cyRef        = useRef(null)

  useEffect(() => {
    if (!containerRef.current) return
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: [],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(color)',
            'label': 'data(label)',
            'width': 'data(size)',
            'height': 'data(size)',
            'font-size': '9px',
            'color': '#d4e4fa',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'text-outline-color': '#051424',
            'text-outline-width': 2,
            'border-width': 2,
            'border-color': 'rgba(255,255,255,0.15)',
          }
        },
        {
          selector: 'node[?is_seed]',
          style: {
            'border-color': '#8ed5ff',
            'border-width': 3,
            'box-shadow': '0 0 12px #8ed5ff',
          }
        },
        {
          selector: 'node[?is_terminal]',
          style: {
            'border-color': '#ff938c',
            'border-width': 3,
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(width)',
            'line-color': 'rgba(142, 213, 255, 0.35)',
            'target-arrow-color': 'rgba(142, 213, 255, 0.6)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '8px',
            'color': '#87929a',
            'text-outline-color': '#051424',
            'text-outline-width': 2,
          }
        },
        {
          selector: ':selected',
          style: { 'border-color': '#38bdf8', 'border-width': 3 }
        }
      ],
      layout: { name: 'fcose', animate: true, animationDuration: 600 },
      userZoomingEnabled: true,
      userPanningEnabled: true,
      minZoom: 0.3,
      maxZoom: 3,
    })
    return () => cyRef.current?.destroy()
  }, [])

  useEffect(() => {
    if (!cyRef.current || !traceResult) return
    cyRef.current.elements().remove()
    cyRef.current.add(buildElements(traceResult))
    cyRef.current.layout({ name: 'fcose', animate: true, animationDuration: 600 }).run()
    cyRef.current.fit(undefined, 40)
  }, [traceResult])

  const fitGraph = () => cyRef.current?.fit(undefined, 40)
  const zoomIn   = () => cyRef.current?.zoom({ level: cyRef.current.zoom() * 1.3, renderedPosition: { x: 200, y: 200 } })
  const zoomOut  = () => cyRef.current?.zoom({ level: cyRef.current.zoom() * 0.75, renderedPosition: { x: 200, y: 200 } })

  return (
    <div className="flex-1 relative bg-surface-dim" style={{ minHeight: 0 }}>
      {/* Empty state */}
      {!traceResult && !loading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-space-md text-on-surface-variant z-10">
          <div className="text-5xl opacity-20">⬡</div>
          <div className="text-center">
            <p className="font-body-medium text-body-medium mb-space-sm">Enter a wallet address above to begin forensic tracing</p>
            <p className="font-code-sm text-code-sm text-outline mb-space-base">Try the demo dataset:</p>
            <button onClick={onDemo} className="font-code-sm text-code-sm text-primary bg-surface-container-low border border-outline/50 px-space-base py-space-xs rounded-lg hover:border-primary transition-colors">
              T_VICTIM_SIH_DEMO_999
            </button>
          </div>
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 z-20 bg-surface-dim/80 backdrop-blur-sm flex flex-col items-center justify-center gap-space-base">
          <div className="w-8 h-8 border-2 border-surface-container-high border-t-primary rounded-full animate-spin" />
          <div className="flex flex-col gap-space-xs">
            {loadSteps.map((s, i) => (
              <div key={i} className={`flex items-center gap-space-xs font-code-sm text-code-sm transition-colors ${i < loadStep ? 'text-secondary' : i === loadStep ? 'text-primary' : 'text-outline/50'}`}>
                <span className="w-4 text-center">{i < loadStep ? '✓' : i === loadStep ? '▸' : '○'}</span>
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cytoscape container */}
      <div ref={containerRef} className="absolute inset-0" />

      {/* Controls */}
      <div className="absolute top-3 right-3 flex flex-col gap-1 z-10">
        {[['＋', zoomIn], ['－', zoomOut], ['⊡', fitGraph]].map(([lbl, fn]) => (
          <button key={lbl} onClick={fn} className="w-8 h-8 bg-surface-container border border-border-subtle text-on-surface-variant rounded-lg flex items-center justify-center hover:bg-surface-container-high hover:text-on-surface transition-colors text-sm font-bold">
            {lbl}
          </button>
        ))}
      </div>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex gap-2 flex-wrap z-10">
        {[
          ['Victim/Seed', NODE_COLOR.seed],
          ['Terminal/Exchange', NODE_COLOR.terminal],
          ['Mule Cluster', NODE_COLOR.cluster],
          ['Intermediate', NODE_COLOR.default],
        ].map(([lbl, col]) => (
          <div key={lbl} className="flex items-center gap-1 bg-surface-container/80 border border-border-subtle px-2 py-0.5 rounded-full text-on-surface-variant font-code-sm text-code-sm">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: col }} />
            {lbl}
          </div>
        ))}
      </div>

      {/* Summary strip */}
      {traceResult && (
        <div className="absolute top-3 left-3 flex gap-2 flex-wrap z-10">
          {[
            [`${traceResult.graph?.total_nodes ?? 0} nodes`, 'text-primary'],
            [`${traceResult.graph?.total_edges ?? 0} edges`, 'text-secondary'],
            [`${traceResult.clusters?.length ?? 0} clusters`, 'text-status-warning'],
            [`${traceResult.all_paths?.length ?? 0} paths`, 'text-tertiary'],
          ].map(([lbl, cls]) => (
            <span key={lbl} className={`bg-surface-container/90 border border-border-subtle px-2 py-0.5 rounded font-code-sm text-code-sm ${cls}`}>{lbl}</span>
          ))}
        </div>
      )}
    </div>
  )
}
