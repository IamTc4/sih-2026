// src/components/GraphView.jsx
// Live animated heist-movie chase visualization with live telemetry ticker & target lock-on
import React, { useEffect, useRef, useState, useCallback } from 'react'
import cytoscape from 'cytoscape'
import fcose from 'cytoscape-fcose'
import DemoCaseCard from './DemoCaseCard'

cytoscape.use(fcose)

const NODE_COLOR = {
  seed:     '#8ed5ff',   // victim / seed entry
  terminal: '#ff6b6b',   // exchange / target acquired
  cluster:  '#fbbf24',   // clustered mule
  default:  '#4edea3',   // intermediate hop
}

function buildNodeMap(traceResult) {
  if (!traceResult) return { nodes: [], edges: [], orderedHops: [] }

  let rawNodes = traceResult.graph?.nodes ?? []
  let rawEdges = traceResult.graph?.edges ?? traceResult.graph_edges ?? []
  const clusterMembers = new Set(
    (traceResult.clusters ?? []).flatMap(c => c.addresses || [])
  )

  // Normalize edges — handle backend fields: source/target OR from/to OR from_address/to_address
  // Backend GraphEdge has tx_hashes (list) not tx_hash — pick first element as representative
  const normalizedEdges = rawEdges
    .map((e, i) => {
      const rawSource = e.source ?? e.from ?? e.from_address
      const rawTarget = e.target ?? e.to ?? e.to_address
      // Filter out edges with missing endpoints BEFORE stringifying (String(undefined) = "undefined")
      if (rawSource == null || rawTarget == null) return null
      const source = String(rawSource).trim()
      const target = String(rawTarget).trim()
      if (!source || !target || source === 'undefined' || target === 'undefined') return null
      const amount = Number(e.amount ?? e.value ?? 0)
      // Backend returns tx_hashes (array) — use first element; fall back to tx_hash or synthetic id
      const txHash = (Array.isArray(e.tx_hashes) && e.tx_hashes.length > 0)
        ? e.tx_hashes[0]
        : (e.tx_hash ?? `tx_${i}`)
      const shortHash = String(txHash).slice(-6) || String(i)
      return {
        id: `e_${i}_${shortHash}`,
        source,
        target,
        amount,
        token: e.token || 'USDT',
        tx_hash: txHash,
        tx_count: e.tx_count ?? 1,
        timestamp: e.timestamp,
        hop_number: e.hop_number ?? (i + 1),
      }
    })
    .filter(Boolean)   // remove nulls from skipped edges

  // Determine seed address
  const seedAddress = traceResult.seed_address || (normalizedEdges[0]?.source) || ''

  // Determine terminal exchange address
  const terminalAddress = traceResult.attribution?.deposit_address ||
                          traceResult.attribution?.address ||
                          (normalizedEdges.length ? normalizedEdges[normalizedEdges.length - 1].target : '')

  // Build / synthesize node map if not provided or only seed
  let nodeMap = new Map()
  rawNodes.forEach(n => {
    nodeMap.set(String(n.id), {
      id: String(n.id),
      label: n.label ?? (n.id.length > 14 ? n.id.slice(0, 8) + '…' + n.id.slice(-4) : n.id),
      is_seed: Boolean(n.is_seed || n.id === seedAddress),
      is_terminal: Boolean(n.is_terminal || n.id === terminalAddress),
      inflow: n.total_inflow ?? 0,
      outflow: n.total_outflow ?? 0,
    })
  })

  // Ensure all edge endpoints exist in nodeMap
  normalizedEdges.forEach((e, idx) => {
    if (!nodeMap.has(e.source)) {
      nodeMap.set(e.source, {
        id: e.source,
        label: e.source.length > 14 ? e.source.slice(0, 8) + '…' + e.source.slice(-4) : e.source,
        is_seed: e.source === seedAddress,
        is_terminal: false,
        inflow: 0,
        outflow: e.amount,
      })
    }
    if (!nodeMap.has(e.target)) {
      const isTerminal = (idx === normalizedEdges.length - 1) || (e.target === terminalAddress)
      nodeMap.set(e.target, {
        id: e.target,
        label: e.target.length > 14 ? e.target.slice(0, 8) + '…' + e.target.slice(-4) : e.target,
        is_seed: false,
        is_terminal: isTerminal,
        inflow: e.amount,
        outflow: 0,
      })
    }
  })

  // Assemble Cytoscape elements
  const nodes = Array.from(nodeMap.values()).map(n => {
    let color = NODE_COLOR.default
    let role = 'Intermediate Hop'
    if (n.is_seed) {
      color = NODE_COLOR.seed
      role = 'Victim Entry (Seed)'
    } else if (n.is_terminal) {
      color = NODE_COLOR.terminal
      role = `Exchange Receptacle (${traceResult.attribution?.exchange_name || 'VASP'})`
    } else if (clusterMembers.has(n.id)) {
      color = NODE_COLOR.cluster
      role = 'Mule Co-Spend Cluster'
    }

    return {
      data: {
        id: n.id,
        label: n.label,
        rawAddress: n.id,
        color,
        role,
        size: n.is_seed ? 44 : n.is_terminal ? 42 : clusterMembers.has(n.id) ? 32 : 26,
        is_seed: n.is_seed,
        is_terminal: n.is_terminal,
        is_cluster: clusterMembers.has(n.id),
      }
    }
  })

  const edges = normalizedEdges.map((e) => ({
    data: {
      id: e.id,
      source: e.source,
      target: e.target,
      label: `${e.amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })} ${e.token}`,
      amount: e.amount,
      token: e.token,
      tx_hash: e.tx_hash,
      width: Math.max(2, Math.min(8, Math.log10(e.amount + 1) * 2.2)),
    }
  }))

  return { nodes, edges, orderedHops: normalizedEdges }
}

export default function GraphView({
  traceResult,
  loading,
  loadSteps = [],
  loadStep = 0,
  onDemo,
  onSelectWallet,
  onTerminalReached,
}) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const chaseTimerRef = useRef([])

  // Chase visualization telemetry state
  const [targetAcquired, setTargetAcquired] = useState(false)
  const [activeTarget, setActiveTarget] = useState(null)
  const [chaseActive, setChaseActive] = useState(false)
  const [chaseHopIndex, setChaseHopIndex] = useState(0)
  const [totalHops, setTotalHops] = useState(0)
  const [chaseVolume, setChaseVolume] = useState(0)
  const [chaseSpeed, setChaseSpeed] = useState('1x') // '1x', '2x', 'fast'
  const [chaseStatus, setChaseStatus] = useState('System Standby')
  const [selectedNode, setSelectedNode] = useState(null)
  const [builtNodes, setBuiltNodes] = useState(0)
  const [clusterTooltip, setClusterTooltip] = useState(null)

  // Clear running timers
  const clearChaseTimers = () => {
    chaseTimerRef.current.forEach(id => clearTimeout(id))
    chaseTimerRef.current = []
  }

  // Smooth volume count-up
  const animateVolumeTo = useCallback((targetVal) => {
    let startTimestamp = null
    const duration = 350
    let startVal = 0
    setChaseVolume(prev => { startVal = prev; return prev })

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / duration, 1)
      const current = Math.round(startVal + (targetVal - startVal) * progress)
      setChaseVolume(current)
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }
    requestAnimationFrame(step)
  }, [])

  // ── Initialize Cytoscape instance ──────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return

    const cy = cytoscape({
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
            'font-size': '10px',
            'font-family': 'monospace',
            'color': '#d4e4fa',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'text-outline-color': '#030b14',
            'text-outline-width': 2.5,
            'border-width': 2,
            'border-color': 'rgba(255,255,255,0.18)',
            'opacity': 0,
            'transition-property': 'opacity, width, height, border-width, border-color',
            'transition-duration': '0.2s',
          }
        },
        {
          selector: 'node.visible',
          style: { 'opacity': 1 }
        },
        {
          selector: 'node[?is_seed]',
          style: {
            'border-color': '#8ed5ff',
            'border-width': 3,
            'shadow-blur': 22,
            'shadow-color': '#8ed5ff',
            'shadow-opacity': 0.6,
          }
        },
        {
          selector: 'node[?is_terminal]',
          style: {
            'border-color': '#ff6b6b',
            'border-width': 4,
            'shadow-blur': 28,
            'shadow-color': '#ff6b6b',
            'shadow-opacity': 0.8,
          }
        },
        {
          selector: 'node[?is_cluster]',
          style: {
            'border-color': '#fbbf24',
            'border-width': 2.5,
            'shadow-blur': 14,
            'shadow-color': '#fbbf24',
            'shadow-opacity': 0.5,
          }
        },
        {
          selector: 'node.chase-focus',
          style: {
            'border-color': '#00f0ff',
            'border-width': 5,
            'width': 'data(size) * 1.3',
            'height': 'data(size) * 1.3',
            'shadow-blur': 35,
            'shadow-color': '#00f0ff',
            'shadow-opacity': 0.9,
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(width)',
            'line-color': 'rgba(142,213,255,0.22)',
            'target-arrow-color': 'rgba(142,213,255,0.45)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '8.5px',
            'font-family': 'monospace',
            'color': '#87929a',
            'text-outline-color': '#030b14',
            'text-outline-width': 2,
            'opacity': 0,
            'transition-property': 'opacity, line-color, target-arrow-color, width',
            'transition-duration': '0.2s',
          }
        },
        {
          selector: 'edge.visible',
          style: {
            'opacity': 1,
            'line-color': 'rgba(142,213,255,0.38)',
            'target-arrow-color': 'rgba(142,213,255,0.75)',
          }
        },
        {
          selector: 'edge.chase-pulse',
          style: {
            'opacity': 1,
            'line-color': '#00f0ff',
            'target-arrow-color': '#00f0ff',
            'width': 'data(width) * 1.6',
            'shadow-blur': 16,
            'shadow-color': '#00f0ff',
            'shadow-opacity': 0.9,
          }
        },
        {
          selector: ':selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4,
            'shadow-blur': 25,
            'shadow-color': '#38bdf8',
          }
        }
      ],
      layout: { name: 'preset' },
      userZoomingEnabled: true,
      userPanningEnabled: true,
      minZoom: 0.15,
      maxZoom: 4.5,
    })

    // Node click handler
    cy.on('tap', 'node', (evt) => {
      const node = evt.target
      setSelectedNode({
        id: node.data('rawAddress') || node.id(),
        label: node.data('label'),
        role: node.data('role'),
        color: node.data('color'),
        isSeed: node.data('is_seed'),
        isTerminal: node.data('is_terminal'),
        isCluster: node.data('is_cluster'),
      })
    })

    // Background click dismisses inspector
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null)
      }
    })

    // Node hover highlights direct edges & dims unrelated elements to 0.25 (200ms transition)
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target
      const connectedEdges = node.connectedEdges()
      const connectedNodes = connectedEdges.connectedNodes()
      cy.elements().difference(connectedEdges.union(connectedNodes).union(node)).style({ opacity: 0.25 })
      connectedEdges.style({ opacity: 1, 'line-color': '#00f0ff' })
    })

    cy.on('mouseout', 'node', () => {
      cy.elements().style({ opacity: 1, 'line-color': 'rgba(142,213,255,0.38)' })
    })

    cyRef.current = cy
    return () => {
      clearChaseTimers()
      cy.destroy()
    }
  }, [])

  // ── Cinematic Heist "Chase" Animation with incremental assembly ─────────────
  const playChase = useCallback(async (res, speedMultiplier = 1) => {
    const cy = cyRef.current
    if (!cy || !res) return

    clearChaseTimers()
    setTargetAcquired(false)
    setSelectedNode(null)
    setChaseActive(true)
    setClusterTooltip(null)

    const { nodes, edges, orderedHops } = buildNodeMap(res)
    if (!nodes.length) {
      setChaseActive(false)
      return
    }

    const totalHopCount = orderedHops.length || 1
    setTotalHops(totalHopCount)
    setChaseHopIndex(0)
    setChaseVolume(0)
    setChaseStatus('⚡ INITIALIZING HIGH-VELOCITY TRACE CHASE…')

    // Reset graph layout & visibility
    cy.elements().remove()
    cy.add([...nodes, ...edges])

    const layout = cy.layout({
      name: 'fcose',
      animate: false,
      randomize: true,
      quality: 'proof',
      nodeDimensionsIncludeLabels: true,
      spacingFactor: 1.35,
    })
    layout.run()

    cy.elements().removeClass('visible chase-pulse chase-focus')

    // Stagger duration: 1x = 400ms, 2x = 200ms, Turbo = 90ms (perceptibly sequential)
    const stepInterval = speedMultiplier >= 4 ? 90 : speedMultiplier >= 2 ? 200 : 400

    // Step 1: Seed node fades/scales in first (300ms ease-out)
    const seedNodeId = nodes.find(n => n.data.is_seed)?.data.id || nodes[0].data.id
    const seedEle = cy.getElementById(seedNodeId)
    if (seedEle) {
      seedEle.addClass('visible chase-focus')
      setBuiltNodes(1)
      setChaseStatus(`[PHASE 1] VICTIM ENTRY LOCKED: ${seedNodeId.slice(0, 10)}…`)
      cy.animate({
        center: { eles: seedEle },
        zoom: 1.5,
        duration: 300,
        easing: 'ease-out',
      })
    }

    await new Promise(r => setTimeout(r, stepInterval))

    // Step 2: Step through each subsequent hop in sequence
    let currentVolume = 0

    for (let h = 0; h < orderedHops.length; h++) {
      const hop = orderedHops[h]
      const sourceEle = cy.getElementById(hop.source)
      const targetEle = cy.getElementById(hop.target)
      const edgeEle = cy.getElementById(hop.id)

      setChaseHopIndex(h + 1)
      currentVolume += hop.amount
      animateVolumeTo(currentVolume)

      const isLastHop = h === orderedHops.length - 1
      const isTerminal = targetEle.data('is_terminal') || isLastHop

      // Status message per hop
      if (h === 0) {
        setChaseStatus(`[HOP 1/${totalHopCount}] MULE ACQUISITION: Transfer of ${hop.amount.toLocaleString()} ${hop.token}`)
      } else if (!isTerminal) {
        setChaseStatus(`[HOP ${h + 1}/${totalHopCount}] PEEL/FORWARD: Routing through ${targetEle.data('role') || 'intermediary'}`)
      } else {
        setChaseStatus(`[FINAL HOP] VASP INFILTRATION: Approaching Exchange Hot Wallet…`)
      }

      // Animated drawing line from previous node to target node
      if (edgeEle) {
        edgeEle.addClass('visible chase-pulse')
        cy.elements().removeClass('chase-focus')
        if (sourceEle) sourceEle.addClass('visible')
        if (targetEle) {
          targetEle.addClass('visible chase-focus')
          setBuiltNodes(prev => Math.max(prev, h + 2))
        }

        // Camera smoothly glides along with the chase
        cy.animate({
          center: { eles: targetEle },
          duration: Math.min(300, stepInterval),
          easing: 'ease-out',
        })
      }

      // Step 2c: When a cluster forms (Mule Cluster node), animate underlying addresses merging into cluster node
      if (targetEle.data('is_cluster')) {
        const heuristicName = res.clusters?.[0]?.evidence_chain?.[0]?.heuristic_name || 'deposit-reuse'
        setClusterTooltip({
          show: true,
          heuristic: heuristicName,
        })
        setTimeout(() => setClusterTooltip(null), 2400)

        // Spawn 2 temporary sub-nodes snapping into cluster position
        const cPos = targetEle.position()
        const sub1 = cy.add({
          group: 'nodes',
          data: { id: `_csub1_${h}`, label: 'addr_a', color: '#fbbf24', size: 12 },
          position: { x: cPos.x + 30, y: cPos.y - 25 }
        })
        const sub2 = cy.add({
          group: 'nodes',
          data: { id: `_csub2_${h}`, label: 'addr_b', color: '#fbbf24', size: 12 },
          position: { x: cPos.x - 30, y: cPos.y + 25 }
        })
        sub1.addClass('visible')
        sub2.addClass('visible')

        // 400ms snap/merge animation
        sub1.animate({ position: { x: cPos.x, y: cPos.y }, style: { opacity: 0 } }, { duration: 400 })
        sub2.animate({ position: { x: cPos.x, y: cPos.y }, style: { opacity: 0 } }, {
          duration: 400,
          complete: () => {
            cy.remove(sub1)
            cy.remove(sub2)
          }
        })
      }

      await new Promise(r => setTimeout(r, stepInterval))

      // Keep edge visible but remove laser pulse
      if (edgeEle) {
        edgeEle.removeClass('chase-pulse')
      }

      // Step 2d: Terminal Node "TARGET ACQUIRED" radial pulse (2 pulses, 600ms each) + red border
      if (isTerminal) {
        const attribution = res.attribution || {}
        const exchangeName = attribution.exchange_name || 'OKX Hot Wallet'
        const confidence = attribution.confidence ? Math.round(attribution.confidence * 100) : 98

        setActiveTarget({
          exchangeName,
          confidence,
          address: hop.target,
          amount: currentVolume,
        })
        setTargetAcquired(true)
        setChaseStatus(`⊕ TARGET ACQUIRED: ${exchangeName.toUpperCase()} (${confidence}% CONFIDENCE)`)

        // 2 radial pulses (600ms each) + border transitions to red
        targetEle.animate({ style: { 'border-width': 12, 'border-color': '#ef4444' } }, { duration: 300 })
        targetEle.animate({ style: { 'border-width': 4, 'border-color': '#ef4444' } }, { duration: 300, queue: true })
        targetEle.animate({ style: { 'border-width': 10, 'border-color': '#ef4444' } }, { duration: 300, queue: true })
        targetEle.animate({ style: { 'border-width': 4, 'border-color': '#ef4444' } }, { duration: 300, queue: true })

        // Dramatic camera zoom directly into target node
        cy.animate({
          zoom: 2.6,
          center: { eles: targetEle },
          duration: 750,
          easing: 'ease-in-out',
        })

        // Notify parent that terminal node is reached so ExchangePanel can reveal causally!
        if (onTerminalReached) {
          onTerminalReached(attribution)
        }

        // After 3.2s, fit view to show full crime trail
        const zoomOutTimer = setTimeout(() => {
          cy.animate({
            fit: { eles: cy.elements(), padding: 45 },
            duration: 800,
            easing: 'ease-in-out',
          })
          setChaseActive(false)
        }, 3200)

        // Dismiss the target banner after 4.5s
        const bannerTimer = setTimeout(() => {
          setTargetAcquired(false)
        }, 4500)

        chaseTimerRef.current.push(zoomOutTimer, bannerTimer)
        return
      }
    }

    // Final overview fit
    setTimeout(() => {
      cy.elements().removeClass('chase-focus')
      cy.animate({ fit: { eles: cy.elements(), padding: 45 }, duration: 600 })
      setChaseActive(false)
      setChaseStatus('Trace traversal complete — evidence preserved')
    }, 400)
  }, [animateVolumeTo, onTerminalReached])

  // ── Trigger chase on new traceResult or speed change ───────────────────────
  useEffect(() => {
    if (!traceResult) return
    const mult = chaseSpeed === '2x' ? 2 : chaseSpeed === 'fast' ? 4 : 1
    playChase(traceResult, mult)
  }, [traceResult, chaseSpeed, playChase])

  const replayChase = () => {
    if (!traceResult) return
    const mult = chaseSpeed === '2x' ? 2 : chaseSpeed === 'fast' ? 4 : 1
    playChase(traceResult, mult)
  }

  // Zoom controls (+ / - / fit-to-screen) centering on container midpoint
  const fitGraph = () => {
    if (!cyRef.current) return
    cyRef.current.animate({ fit: { eles: cyRef.current.elements(), padding: 45 }, duration: 400 })
  }
  const zoomIn = () => {
    if (!cyRef.current) return
    const w = cyRef.current.width()
    const h = cyRef.current.height()
    cyRef.current.zoom({ level: cyRef.current.zoom() * 1.3, renderedPosition: { x: w / 2, y: h / 2 } })
  }
  const zoomOut = () => {
    if (!cyRef.current) return
    const w = cyRef.current.width()
    const h = cyRef.current.height()
    cyRef.current.zoom({ level: cyRef.current.zoom() * 0.75, renderedPosition: { x: w / 2, y: h / 2 } })
  }

  const { nodes: allNodes } = traceResult ? buildNodeMap(traceResult) : { nodes: [] }
  const totalNodesCount = allNodes.length

  return (
    <div className="flex-1 relative hex-grid overflow-hidden flex flex-col" style={{ minHeight: 0, background: '#000000' }}>

      {/* ── Empty state — Case Selector Cards ── */}
      {!traceResult && !loading && (
        <div className="absolute inset-0 z-10 backdrop-blur-sm flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.9)' }}>
          <DemoCaseCard onLaunch={onDemo} />
        </div>
      )}

      {/* ── Single-node result — real address with no indexed hops ── */}
      {traceResult && !loading && totalNodesCount <= 1 && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center" style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(4px)' }}>
          <div style={{
            padding: '2.5rem 3rem',
            borderRadius: '16px',
            border: '1px solid rgba(34,211,238,0.2)',
            background: 'rgba(0,0,0,0.95)',
            maxWidth: '520px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⬡</div>
            <div style={{ color: '#22d3ee', fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '.85rem', letterSpacing: '.12em', marginBottom: '.75rem' }}>
              SEED NODE INDEXED
            </div>
            <div style={{ color: '#8ed5ff', fontFamily: 'var(--font-mono)', fontSize: '.75rem', marginBottom: '.5rem', wordBreak: 'break-all', opacity: .8 }}>
              {traceResult?.seed_address}
            </div>
            <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: '.72rem', fontFamily: 'var(--font-sans)', lineHeight: 1.6, marginTop: '1rem' }}>
              No outbound USDT-TRC20 transactions found within {traceResult?.max_hops_traversed ?? '?'} hops.<br />
              This is normal for real addresses not yet involved in observed fraud flows.<br />
              <span style={{ color: 'rgba(34,211,238,0.5)', marginTop: '.5rem', display: 'block' }}>Try the preloaded demo cases to see a full multi-hop fraud graph.</span>
            </div>
          </div>
        </div>
      )}

      {/* ── Node & Edge stats banner ── */}
      {traceResult && !loading && totalNodesCount > 1 && (
        <div style={{
          position: 'absolute', top: '8px', left: '50%', transform: 'translateX(-50%)',
          zIndex: 20, display: 'flex', gap: '1rem',
          background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)',
          padding: '.35rem 1rem', borderRadius: '20px',
          border: '1px solid rgba(34,211,238,0.15)',
          fontFamily: 'var(--font-mono)', fontSize: '.62rem',
        }}>
          <span style={{ color: '#8ed5ff' }}>⬡ {totalNodesCount} Nodes</span>
          <span style={{ color: 'rgba(255,255,255,0.2)' }}>|</span>
          <span style={{ color: '#fbbf24' }}>➡ {traceResult?.graph?.edges?.length ?? 0} Edges</span>
          <span style={{ color: 'rgba(255,255,255,0.2)' }}>|</span>
          <span style={{ color: '#34d399' }}>{traceResult?.max_hops_traversed ?? '?'} Hops</span>
        </div>
      )}

      {/* ── Loading Overlay with Animated Step Pipeline ── */}
      {loading && (
        <div className="absolute inset-0 z-30 bg-[#030b14]/95 backdrop-blur-md flex flex-col items-center justify-center gap-5">
          <div className="relative">
            <div className="w-20 h-20 rounded-full border-2 border-primary/20 border-t-primary animate-spin" />
            <div className="absolute inset-2 w-16 h-16 rounded-full border-2 border-secondary/20 border-b-secondary animate-spin-slow" />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-primary font-bold text-xl tracking-wider animate-pulse">WT</span>
            </div>
          </div>

          <div className="text-center">
            <div className="font-headline-sm text-headline-sm text-on-surface font-bold tracking-wide">
              DISPATCHING BLOCKCHAIN FORENSIC AGENT
            </div>
            <div className="font-code-sm text-code-sm text-outline/70 mt-1">
              Ingesting TRC20 ledger data & constructing deterministic transaction graph
            </div>
          </div>

          {/* Stepper */}
          <div className="flex flex-col gap-2 min-w-[300px] bg-surface-container/60 border border-border-subtle/50 p-4 rounded-xl">
            {loadSteps.map((s, i) => (
              <div
                key={i}
                className={`flex items-center gap-3 font-code-sm text-code-sm transition-all duration-300 ${
                  i < loadStep ? 'text-secondary' :
                  i === loadStep ? 'text-primary font-bold' : 'text-outline/30'
                }`}
              >
                <span className="w-5 flex-shrink-0 text-center font-mono">
                  {i < loadStep ? '✓' : i === loadStep ? '▶' : '○'}
                </span>
                <span className={i === loadStep ? 'animate-pulse' : ''}>{s}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── TARGET ACQUIRED Tactical Climax Banner ── */}
      {targetAcquired && activeTarget && (
        <div className="absolute inset-0 z-40 pointer-events-none flex items-center justify-center animate-in">
          <div className="relative flex flex-col items-center">
            {/* Outer radar ping rings */}
            <div className="absolute w-72 h-72 rounded-full border border-error/50 target-ring-pulse -top-20" />
            <div className="absolute w-44 h-44 rounded-full border-2 border-error/70 target-ring-pulse -top-6" />

            {/* Tactical HUD card */}
            <div
              className="hud-panel rounded-2xl px-8 py-6 text-center shadow-2xl relative"
              style={{
                boxShadow: '0 0 60px rgba(255, 107, 107, 0.45)',
                border: '1px solid rgba(255, 107, 107, 0.7)',
              }}
            >
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-error animate-ping" />
                <span className="font-code-sm text-code-sm text-error font-mono tracking-widest uppercase">
                  VASP ATTRIBUTION LOCKED
                </span>
              </div>

              <div className="font-headline-lg text-headline-lg font-black text-error tracking-tight flex items-center justify-center gap-2">
                <span>⊕ TARGET ACQUIRED:</span>
                <span className="text-white drop-shadow-[0_0_15px_rgba(255,107,107,0.8)]">
                  {activeTarget.exchangeName}
                </span>
              </div>

              <div className="flex items-center justify-center gap-4 mt-3 pt-3 border-t border-error/30 font-code-sm text-code-sm">
                <div>
                  <span className="text-outline/60 text-[11px] block">CONFIDENCE</span>
                  <span className="text-secondary font-bold text-sm">{activeTarget.confidence}% MATCH</span>
                </div>
                <div className="w-px h-6 bg-error/30" />
                <div>
                  <span className="text-outline/60 text-[11px] block">FUNDS TRACED</span>
                  <span className="text-primary font-bold text-sm">
                    {activeTarget.amount.toLocaleString()} USDT
                  </span>
                </div>
                <div className="w-px h-6 bg-error/30" />
                <div>
                  <span className="text-outline/60 text-[11px] block">LEGAL PROTOCOL</span>
                  <span className="text-error font-bold text-sm">SEC 91 CrPC READY</span>
                </div>
              </div>

              <div className="mt-2 text-[10px] font-code-sm text-outline/50 truncate max-w-sm">
                Target Receptacle: {activeTarget.address}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Cluster Merge Heuristic Tooltip ── */}
      {clusterTooltip && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-35 animate-in pointer-events-none">
          <div className="bg-status-warning-bg border border-status-warning/40 text-status-warning px-4 py-2 rounded-xl flex items-center gap-2.5 shadow-xl backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-status-warning animate-ping" />
            <div className="font-code-sm text-xs">
              <span className="font-bold uppercase tracking-wider text-[10px] block opacity-80">Mule Cluster Formation</span>
              <span>Heuristic: <strong>{clusterTooltip.heuristic}</strong> (Co-spend merge)</span>
            </div>
          </div>
        </div>
      )}

      {/* ── Cytoscape Graph Canvas ── */}
      <div ref={containerRef} className="flex-1 w-full h-full" />

      {/* ── Top Left Forensic Metrics Strip ── */}
      {traceResult && (
        <div className="absolute top-3 left-3 flex gap-2 flex-wrap z-20 pointer-events-auto">
          <div className="hud-panel px-3 py-1.5 rounded-lg flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="font-code-sm text-code-sm text-primary font-bold">
                {totalNodesCount} Nodes
              </span>
            </div>
            <div className="w-px h-3 bg-border-subtle" />
            <div className="font-code-sm text-code-sm text-secondary font-bold">
              {traceResult.graph?.total_edges ?? traceResult.graph_edges?.length ?? 0} Edges
            </div>
            <div className="w-px h-3 bg-border-subtle" />
            <div className="font-code-sm text-code-sm text-status-warning font-bold">
              {traceResult.clusters?.length ?? 0} Cluster(s)
            </div>
            {builtNodes > 0 && (
              <>
                <div className="w-px h-3 bg-border-subtle" />
                <span className="font-code-sm text-code-sm text-outline/60 text-[11px]">
                  Mapped: {builtNodes}/{totalNodesCount}
                </span>
              </>
            )}
          </div>
        </div>
      )}

      {/* ── Top Right Controls Toolbar ── */}
      <div className="absolute top-3 right-3 flex items-center gap-2 z-20">
        {/* Replay Chase Button */}
        {traceResult && (
          <button
            id="replay-chase-btn"
            onClick={replayChase}
            className="hud-panel px-3 py-1.5 rounded-lg flex items-center gap-2 text-on-surface hover:text-primary hover:border-primary/50 transition-all font-code-sm text-code-sm cursor-pointer"
            title="Replay forensic hop-by-hop money chase"
          >
            <span className={chaseActive ? 'animate-spin' : ''}>↺</span>
            <span className="font-bold">Replay Chase</span>
          </button>
        )}

        {/* Speed Toggle */}
        {traceResult && (
          <div className="hud-panel p-1 rounded-lg flex items-center gap-1 text-[11px] font-code-sm">
            {['1x', '2x', 'fast'].map(spd => (
              <button
                key={spd}
                onClick={() => setChaseSpeed(spd)}
                className={`px-2 py-0.5 rounded cursor-pointer transition-all ${
                  chaseSpeed === spd
                    ? 'bg-primary text-surface font-bold shadow-sm'
                    : 'text-outline/70 hover:text-on-surface'
                }`}
              >
                {spd === 'fast' ? '⚡ Turbo' : spd}
              </button>
            ))}
          </div>
        )}

        {/* Camera Zoom / Fit Controls */}
        <div className="hud-panel p-1 rounded-lg flex items-center gap-1">
          {[
            ['＋', zoomIn, 'zoom-in', 'Zoom In'],
            ['－', zoomOut, 'zoom-out', 'Zoom Out'],
            ['⊡', fitGraph, 'fit', 'Fit Graph to Screen'],
          ].map(([lbl, fn, id, tip]) => (
            <button
              key={id}
              id={`graph-ctrl-${id}`}
              onClick={fn}
              title={tip}
              className="w-7 h-7 flex items-center justify-center text-on-surface hover:text-primary hover:bg-surface-container-high rounded transition-all font-bold text-xs cursor-pointer"
            >
              {lbl}
            </button>
          ))}
        </div>
      </div>

      {/* ── Node Inspector Floating Drawer ── */}
      {selectedNode && (
        <div className="absolute top-16 right-3 w-80 hud-panel rounded-xl p-4 z-25 animate-in shadow-2xl border border-primary/40">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: selectedNode.color, boxShadow: `0 0 8px ${selectedNode.color}` }}
              />
              <span className="font-headline-sm text-sm text-on-surface font-bold">Node Inspector</span>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-outline/50 hover:text-on-surface font-bold text-xs p-1"
            >
              ✕
            </button>
          </div>

          <div className="space-y-2.5 text-xs font-code-sm">
            <div>
              <span className="text-outline/60 text-[10px] block mb-0.5">CLASSIFICATION</span>
              <span
                className="inline-block px-2 py-0.5 rounded font-bold border"
                style={{
                  color: selectedNode.color,
                  borderColor: `${selectedNode.color}40`,
                  backgroundColor: `${selectedNode.color}15`,
                }}
              >
                {selectedNode.role}
              </span>
            </div>

            <div>
              <span className="text-outline/60 text-[10px] block mb-0.5">WALLET ADDRESS</span>
              <div className="bg-surface-container-high px-2 py-1 rounded font-mono text-[11px] text-on-surface-variant break-all select-all border border-border-subtle/50">
                {selectedNode.id}
              </div>
            </div>

            <div className="flex gap-2 pt-2 border-t border-border-subtle/50">
              <button
                onClick={() => navigator.clipboard?.writeText(selectedNode.id)}
                className="flex-1 py-1 px-2 rounded bg-surface-container border border-border-subtle hover:border-primary/40 text-on-surface-variant hover:text-primary transition-all text-center cursor-pointer text-[11px]"
              >
                Copy Address
              </button>
              <a
                href={`https://tronscan.org/#/address/${selectedNode.id}`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 py-1 px-2 rounded bg-surface-container border border-border-subtle hover:border-secondary/40 text-on-surface-variant hover:text-secondary transition-all text-center cursor-pointer text-[11px]"
              >
                Tronscan ↗
              </a>
            </div>

            {onSelectWallet && (
              <button
                onClick={() => {
                  onSelectWallet(selectedNode.id)
                  setSelectedNode(null)
                }}
                className="w-full py-1.5 px-3 rounded bg-primary/20 hover:bg-primary/30 border border-primary/40 text-primary font-bold text-center transition-all cursor-pointer text-[11px]"
              >
                Investigate this Wallet ➔
              </button>
            )}
          </div>
        </div>
      )}

      {/* ── Bottom Left Legend ── */}
      <div className="absolute bottom-16 left-3 flex gap-2 flex-wrap z-20 pointer-events-none">
        {[
          ['Victim Entry', NODE_COLOR.seed],
          ['VASP Receptacle', NODE_COLOR.terminal],
          ['Mule Cluster', NODE_COLOR.cluster],
          ['Intermediate Hop', NODE_COLOR.default],
        ].map(([lbl, col]) => (
          <div
            key={lbl}
            className="flex items-center gap-1.5 bg-surface-container/90 border border-border-subtle/60 px-2.5 py-1 rounded-full text-on-surface-variant font-code-sm text-[10px] backdrop-blur-sm shadow-sm"
          >
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ background: col, boxShadow: `0 0 6px ${col}` }}
            />
            {lbl}
          </div>
        ))}
      </div>

      {/* ── Bottom Live "Chase" Ticker HUD Bar ── */}
      <div className="w-full bg-[#040e1b]/95 border-t border-border-subtle/80 px-4 py-2 flex items-center justify-between z-20 backdrop-blur-md flex-shrink-0">
        <div className="flex items-center gap-4">
          {/* Live Chase Indicator */}
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${chaseActive ? 'bg-error animate-ping' : 'bg-secondary'}`} />
            <span className="font-label-caps text-label-caps text-on-surface tracking-wider font-bold">
              {chaseActive ? 'FORENSIC CHASE ACTIVE' : 'TELEMETRY HUD'}
            </span>
          </div>

          <div className="w-px h-4 bg-border-subtle" />

          {/* Current Hop Indicator */}
          <div className="flex items-center gap-1.5 font-code-sm text-code-sm">
            <span className="text-outline/60 text-[11px]">HOP TRAVERSED:</span>
            <span className="text-primary font-bold">
              {chaseHopIndex}/{totalHops || traceResult?.max_hops_traversed || 4}
            </span>
          </div>

          <div className="w-px h-4 bg-border-subtle" />

          {/* Volume Counter */}
          <div className="flex items-center gap-1.5 font-code-sm text-code-sm">
            <span className="text-outline/60 text-[11px]">FUNDS IN FLIGHT:</span>
            <span className="text-secondary font-bold">
              ${chaseVolume.toLocaleString()} USDT
            </span>
            <span className="text-outline/50 text-[10px]">
              (~₹{(chaseVolume * 83.5).toLocaleString('en-IN', { maximumFractionDigits: 0 })})
            </span>
          </div>

          <div className="w-px h-4 bg-border-subtle hidden md:block" />

          {/* Velocity */}
          <div className="items-center gap-1.5 font-code-sm text-code-sm hidden md:flex">
            <span className="text-outline/60 text-[11px]">VELOCITY:</span>
            <span className="text-status-warning font-bold">
              {chaseHopIndex > 2 ? '4.8 hops/hr (HIGH)' : '1.2 hops/hr (NORMAL)'}
            </span>
          </div>
        </div>

        {/* Live Status String */}
        <div className="flex items-center gap-2 font-code-sm text-code-sm max-w-[420px] truncate">
          <span className="text-primary animate-pulse">▶</span>
          <span className="text-on-surface-variant font-mono text-xs truncate">
            {chaseStatus}
          </span>
        </div>
      </div>

    </div>
  )
}
