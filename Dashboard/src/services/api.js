// src/services/api.js
// CryptoSentinel — Unified API Service Layer (v2.0)

const AGENT_URL      = '/api/agent'
const BLOCKCHAIN_URL = '/api/blockchain'
const ML_URL         = '/api/ml'
const CYBER_URL      = '/api/cyber'

async function _fetch(url, opts = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 200)}`)
  }
  return res.json()
}

// ── Agent (Agentic AI, port 8001) ─────────────────────────────────────────────
export const agentQuery = (session_id, message) =>
  _fetch(`${AGENT_URL}/agent/query`, {
    method: 'POST',
    body: JSON.stringify({ session_id, message }),
  })

export const agentHealth = () => _fetch(`${AGENT_URL}/health`)

// ── Blockchain — Multi-Chain (port 8000) ──────────────────────────────────────
export const traceWallet = (address, max_hops = 4) =>
  _fetch(`${BLOCKCHAIN_URL}/trace`, {
    method: 'POST',
    body: JSON.stringify({ address, max_hops }),
  })

export const getCluster     = (address) => _fetch(`${BLOCKCHAIN_URL}/cluster/${address}`)
export const getAttribution = (address) => _fetch(`${BLOCKCHAIN_URL}/attribution/${address}`)
export const getGraph       = (address, max_hops = 3) => _fetch(`${BLOCKCHAIN_URL}/graph/${address}?max_hops=${max_hops}`)
export const getAddressDetails = (address) => _fetch(`${BLOCKCHAIN_URL}/address/${address}`)
export const blockchainHealth = () => _fetch(`${BLOCKCHAIN_URL}/health`)

// ── ML Risk Scoring (port 8002) ───────────────────────────────────────────────
export const getRiskScore = (address, blockchain_output = {}, cybersecurity_flags = {}) =>
  _fetch(`${ML_URL}/risk-score`, {
    method: 'POST',
    body: JSON.stringify({ address, blockchain_output, cybersecurity_flags }),
  })

export const getModelInfo = () => _fetch(`${ML_URL}/model-info`)
export const mlHealth     = () => _fetch(`${ML_URL}/health`)

// ── Cybersecurity v2 (port 8003) ──────────────────────────────────────────────

// Legacy
export const checkPatterns = (address, graph_edges = []) =>
  _fetch(`${CYBER_URL}/check-patterns`, {
    method: 'POST',
    body: JSON.stringify({ address, graph_edges }),
  })

export const checkBlacklist = (address) => _fetch(`${CYBER_URL}/blacklist/${address}`)

// Advanced Fraud Detection
export const analyzeFraudPatterns = (transactions, blacklist = []) =>
  _fetch(`${CYBER_URL}/fraud/analyze`, {
    method: 'POST',
    body: JSON.stringify({ transactions, blacklist }),
  })

// Threat Intel
export const screenAddresses = (addresses) =>
  _fetch(`${CYBER_URL}/threat-intel/screen`, {
    method: 'POST',
    body: JSON.stringify({ addresses }),
  })

// Evidence Trail
export const logEvent = (event_type, payload) =>
  _fetch(`${CYBER_URL}/log-event`, {
    method: 'POST',
    body: JSON.stringify({ event_type, payload }),
  })

export const verifyEntry    = (entry_id) => _fetch(`${CYBER_URL}/verify/${entry_id}`)
export const getAuditTrail  = (limit = 100, offset = 0) =>
  _fetch(`${CYBER_URL}/audit-trail?limit=${limit}&offset=${offset}`)
export const verifyFullChain = () => _fetch(`${CYBER_URL}/evidence/chain/verify`)
export const exportChain    = () =>
  _fetch(`${CYBER_URL}/evidence/export`, { method: 'POST' })

// RBAC
export const getRoles = () => _fetch(`${CYBER_URL}/policy/roles`)
export const checkAccess = (field_name, token) =>
  _fetch(`${CYBER_URL}/policy/check-access`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: JSON.stringify({ field_name }),
  })

// UPI Bridge
export const analyzeUPIComplaint = (complaint_text, amount_inr, fir_number, upi_ids) =>
  _fetch(`${CYBER_URL}/intake/upi-bridge`, {
    method: 'POST',
    body: JSON.stringify({ complaint_text, amount_inr, fir_number, upi_ids }),
  })

// ── NCRP & SAHYOG Gateway (Req 1.2) ──────────────────────────────
export const listNCRPTickets = () => _fetch(`${CYBER_URL}/intake/ncrp/tickets`)
export const getNCRPTicket = (id) => _fetch(`${CYBER_URL}/intake/ncrp/ticket/${id}`)
export const ingestNCRPComplaint = (payload) =>
  _fetch(`${CYBER_URL}/intake/ncrp/webhook`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
export const syncSahyog = (payload) =>
  _fetch(`${CYBER_URL}/intake/sahyog/sync`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })

// ── Cross-Chain Bridge Analytics (Req 2.6) ────────────────────────
export const getCrossChainBridges = () => _fetch(`${BLOCKCHAIN_URL}/cross-chain/bridges`)
export const correlateCrossChain = (source_address, source_chain = 'tron', target_chain = 'ethereum') =>
  _fetch(`${BLOCKCHAIN_URL}/cross-chain/correlate`, {
    method: 'POST',
    body: JSON.stringify({ source_address, source_chain, target_chain }),
  })
export const traceCrossChainWallet = (address) => _fetch(`${BLOCKCHAIN_URL}/cross-chain/trace/${address}`)

// ── Scalable Blockchain Indexer (Req 2.7) ─────────────────────────
export const getIndexingStats = () => _fetch(`${BLOCKCHAIN_URL}/indexing/stats`)

// ── LEA CCTNS & Gov SSO (Req 5.6) ─────────────────────────────────
export const exportCCTNSDiary = (payload) =>
  _fetch(`${CYBER_URL}/lea/cctns/export`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
export const authenticateGovSSO = (gov_email, badge_number) =>
  _fetch(`${CYBER_URL}/auth/gov-sso/authenticate`, {
    method: 'POST',
    body: JSON.stringify({ gov_email, badge_number }),
  })

export const cyberHealth = () => _fetch(`${CYBER_URL}/health`)

// ── Utility: detect chain from address ────────────────────────────────────────
export const detectChain = (address) => {
  if (!address) return { chain: 'unknown', color: '#6b7280', label: 'Unknown' }
  if (address.startsWith('T') && address.length === 34)
    return { chain: 'tron', color: '#EF4444', label: 'Tron TRC-20', token: 'USDT' }
  if (address.startsWith('0x') && address.length === 42)
    return { chain: 'ethereum', color: '#8B5CF6', label: 'Ethereum ERC-20', token: 'USDT' }
  if (address.startsWith('1') || address.startsWith('3') || address.startsWith('bc1'))
    return { chain: 'bitcoin', color: '#F59E0B', label: 'Bitcoin', token: 'BTC' }
  return { chain: 'unknown', color: '#6b7280', label: 'Unknown', token: '?' }
}
