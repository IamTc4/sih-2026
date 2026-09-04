"""
blockchain/ingestion.py
────────────────────────
Data ingestion layer: Tronscan API calls + normalization to NormalizedTx.

Data source: Tronscan Public API
  - Transaction list: GET /api/transaction?address=<addr>&limit=<n>&sort=-timestamp
  - TRC-20 transfers: GET /api/token_trc20/transfers?relatedAddress=<addr>&limit=<n>
  - API docs: https://docs.tronscan.org/

No API key is required for basic endpoints at moderate call rates.
For production, set TRONSCAN_API_KEY in .env for higher rate limits.

SCOPE NOTE: This module fetches and normalises data only.
  Graph construction → blockchain/graph.py
  Clustering         → blockchain/clustering.py
  Attribution        → blockchain/attribution.py
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List

import httpx

from blockchain.config import (
    TRONSCAN_API_BASE,
    TRONSCAN_API_KEY,
    MAX_TX_PER_ADDRESS,
)
from blockchain.models import NormalizedTx

logger = logging.getLogger(__name__)

# ── HTTP client (shared, with timeout) ───────────────────────────────────────
_HEADERS = {"TRON-PRO-API-KEY": TRONSCAN_API_KEY} if TRONSCAN_API_KEY else {}
_CLIENT  = httpx.Client(headers=_HEADERS, timeout=15.0)


def _ms_to_iso(ts_ms: int | str) -> str:
    """
    Convert a Unix millisecond timestamp (as returned by Tronscan) to ISO-8601.
    Example: 1788444867000 -> "2026-09-02T15:14:27Z"
    """
    try:
        ts_sec = int(ts_ms) / 1000
        return datetime.fromtimestamp(ts_sec, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    except (TypeError, ValueError, OSError):
        return str(ts_ms)


def _safe_amount(raw) -> float:
    """Parse an amount field; Tronscan returns amounts in SUN (1 TRX = 1e6 SUN)."""
    try:
        return float(raw or 0) / 1_000_000
    except (TypeError, ValueError):
        return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Primary fetch: native TRX transactions
# ─────────────────────────────────────────────────────────────────────────────
def fetch_trx_transactions(address: str) -> List[NormalizedTx]:
    """
    Pull native TRX transactions for `address` from the Tronscan /api/transaction
    endpoint.

    Tronscan API reference:
      GET https://apilist.tronscanapi.com/api/transaction
      Params: address, limit, sort, start

    Returns a list of NormalizedTx objects sorted by timestamp descending.
    Returns empty list on network error (caller logs and continues BFS).
    """
    url = f"{TRONSCAN_API_BASE}/transaction"
    params = {
        "address": address,
        "limit":   MAX_TX_PER_ADDRESS,
        "sort":    "-timestamp",
        "start":   0,
        "count":   "true",
    }
    try:
        resp = _CLIENT.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        logger.warning("[Ingestion] TRX fetch failed for %s: %s", address, exc)
        return []

    txs: List[NormalizedTx] = []
    for tx in data.get("data", []):
        from_addr = tx.get("ownerAddress") or tx.get("contractData", {}).get("owner_address", "")
        to_addr   = tx.get("toAddress")   or tx.get("contractData", {}).get("to_address", "")
        if not from_addr or not to_addr:
            continue
        txs.append(NormalizedTx(**{
            "from":      from_addr,
            "to":        to_addr,
            "amount":    _safe_amount(tx.get("amount", 0)),
            "token":     "TRX",
            "timestamp": _ms_to_iso(tx.get("timestamp", 0)),
            "tx_hash":   tx.get("hash", ""),
            "chain":     "tron",
        }))

    logger.info("[Ingestion] TRX: %d txs for %s", len(txs), address)
    return txs


# ─────────────────────────────────────────────────────────────────────────────
# TRC-20 token transfers (USDT, USDC, etc.) — PRIMARY fraud rail on Tron
# ─────────────────────────────────────────────────────────────────────────────
def fetch_trc20_transfers(address: str) -> List[NormalizedTx]:
    """
    Pull TRC-20 token transfers (USDT-TRC20 is the dominant Indian fraud rail).

    Tronscan API reference:
      GET https://apilist.tronscanapi.com/api/token_trc20/transfers
      Params: relatedAddress, limit, start, direction (0=out,1=in,2=both)

    The `amount` field in TRC-20 transfers is in token base units;
    for USDT (6 decimals) divide by 1e6.
    """
    url = f"{TRONSCAN_API_BASE}/token_trc20/transfers"
    params = {
        "relatedAddress": address,
        "limit":          MAX_TX_PER_ADDRESS,
        "start":          0,
        "direction":      2,   # 2 = both incoming and outgoing
        "db_version":     1,
    }
    try:
        resp = _CLIENT.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        logger.warning("[Ingestion] TRC-20 fetch failed for %s: %s", address, exc)
        return []

    txs: List[NormalizedTx] = []
    for tx in data.get("token_transfers", []):
        from_addr = tx.get("from_address", "")
        to_addr   = tx.get("to_address",   "")
        if not from_addr or not to_addr:
            continue

        token_info = tx.get("tokenInfo", {}) or {}
        symbol     = token_info.get("tokenAbbr") or tx.get("tokenName") or "TRC20"
        decimals   = int(token_info.get("tokenDecimal") or 6)

        try:
            raw_amt = float(tx.get("quant") or tx.get("amount") or 0)
            amount  = raw_amt / (10 ** decimals)
        except (TypeError, ValueError):
            amount = 0.0

        txs.append(NormalizedTx(**{
            "from":      from_addr,
            "to":        to_addr,
            "amount":    amount,
            "token":     symbol,
            "timestamp": _ms_to_iso(tx.get("block_ts") or tx.get("timestamp") or 0),
            "tx_hash":   tx.get("transaction_id") or tx.get("hash") or "",
            "chain":     "tron",
        }))

    logger.info("[Ingestion] TRC-20: %d txs for %s", len(txs), address)
    return txs


# ─────────────────────────────────────────────────────────────────────────────
# Combined fetch (both TRX + TRC-20)
# ─────────────────────────────────────────────────────────────────────────────
def fetch_all_transactions(address: str) -> List[NormalizedTx]:
    """
    Fetch and combine TRX + TRC-20 transfers for an address.
    Deduplicates by tx_hash. TRC-20/USDT is prioritised (fraud-relevant).
    """
    trx  = fetch_trx_transactions(address)
    trc20 = fetch_trc20_transfers(address)

    seen: set[str] = set()
    merged: List[NormalizedTx] = []
    for tx in trc20 + trx:  # TRC-20 first (more fraud-relevant)
        key = tx.tx_hash or f"{tx.from_addr}:{tx.to_addr}:{tx.timestamp}"
        if key not in seen:
            seen.add(key)
            merged.append(tx)

    return merged


# ─────────────────────────────────────────────────────────────────────────────
# CSV fallback loader (for offline demo / testing against the provided CSV)
# ─────────────────────────────────────────────────────────────────────────────
def load_transactions_from_csv(csv_path: str) -> List[NormalizedTx]:
    """
    Load transactions from the pre-downloaded tron_transactions_raw.csv.
    Use this for offline demo or testing without live Tronscan access.

    CSV schema (matches dataset.py output):
      tx_hash, from, to, amount, token, timestamp, chain, seed_address, seed_is_known_bad
    """
    import csv

    txs: List[NormalizedTx] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # timestamp in CSV is Unix ms — normalise to ISO
                ts_raw = row.get("timestamp", "0")
                ts_iso = _ms_to_iso(ts_raw) if str(ts_raw).isdigit() else str(ts_raw)
                txs.append(NormalizedTx(**{
                    "from":      row["from"],
                    "to":        row["to"],
                    "amount":    float(row.get("amount") or 0),
                    "token":     row.get("token", "TRX"),
                    "timestamp": ts_iso,
                    "tx_hash":   row["tx_hash"],
                    "chain":     row.get("chain", "tron"),
                }))
            except (KeyError, ValueError) as exc:
                logger.warning("[CSV] Skipping malformed row: %s — %s", row, exc)

    logger.info("[CSV] Loaded %d transactions from %s", len(txs), csv_path)
    return txs
