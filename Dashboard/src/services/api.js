// src/services/api.js
// Centralised API calls for all backend services

const AGENT_URL      = '/api/agent'   // → :8001
const BLOCKCHAIN_URL = '/api/blockchain' // → :8000
const ML_URL         = '/api/ml'        // → :8002
const CYBER_URL      = '/api/cyber'     // → :8003

async function _fetch(url, opts = {}) {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

// ── Agent (Agentic AI, port 8001) ────────────────────────────────────────────
export const agentQuery = (session_id, message) =>
  _fetch(`${AGENT_URL}/agent/query`, {
    method: 'POST',
    body: JSON.stringify({ session_id, message }),
  })

export const agentHealth = () => _fetch(`${AGENT_URL}/health`)

// ── Blockchain (port 8000) ────────────────────────────────────────────────────
export const traceWallet = (address, max_hops) =>
  _fetch(`${BLOCKCHAIN_URL}/trace`, {
    method: 'POST',
    body: JSON.stringify({ address, max_hops }),
  })

export const getCluster = (address) =>
  _fetch(`${BLOCKCHAIN_URL}/cluster/${address}`)

export const getAttribution = (address) =>
  _fetch(`${BLOCKCHAIN_URL}/attribution/${address}`)

export const blockchainHealth = () => _fetch(`${BLOCKCHAIN_URL}/health`)

// ── ML Risk Scoring (port 8002) ───────────────────────────────────────────────
export const getRiskScore = (address, blockchain_output = {}, cybersecurity_flags = {}) =>
  _fetch(`${ML_URL}/risk-score`, {
    method: 'POST',
    body: JSON.stringify({ address, blockchain_output, cybersecurity_flags }),
  })

export const getModelInfo = () => _fetch(`${ML_URL}/model-info`)
export const mlHealth     = () => _fetch(`${ML_URL}/health`)

// ── Cybersecurity (port 8003) ─────────────────────────────────────────────────
export const checkPatterns = (address, graph_edges) =>
  _fetch(`${CYBER_URL}/check-patterns`, {
    method: 'POST',
    body: JSON.stringify({ address, graph_edges }),
  })

export const checkBlacklist  = (address) => _fetch(`${CYBER_URL}/blacklist/${address}`)
export const logEvent        = (event_type, payload) =>
  _fetch(`${CYBER_URL}/log-event`, { method: 'POST', body: JSON.stringify({ event_type, payload }) })
export const verifyEntry     = (entry_id) => _fetch(`${CYBER_URL}/verify/${entry_id}`)
export const getEvidenceTrail = (session_id) => _fetch(`${CYBER_URL}/evidence-trail?session_id=${session_id}`)
export const cyberHealth     = () => _fetch(`${CYBER_URL}/health`)
