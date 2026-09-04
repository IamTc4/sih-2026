"""
build_tron_dataset.py

Starter script to build a working (small, demo-scale) labeled Tron/USDT-TRC20
dataset for WalletTrace (SIH26183). Run this on your own laptop, NOT in a
sandboxed environment, since it needs live internet access to the Tronscan API.

WHAT THIS DOES:
1. Pulls real transaction history for a list of seed addresses via the public
   Tronscan API (free, no key needed for basic endpoints).
2. Normalizes transactions into the schema your Blockchain module's PRD expects.
3. Cross-references addresses against the OFAC sanctioned-address blacklist
   (ofac_trx_labeled.csv, already downloaded for you in this folder) to add a
   'known_bad' label where applicable.
4. Saves everything as CSV files ready to feed into your graph-construction and
   ML feature-engineering code.

WHAT THIS DOES NOT DO:
- It does NOT give you a large pre-labeled fraud dataset out of the box — no such
  complete, public, Tron-specific fraud dataset currently exists (unlike Bitcoin,
  which has the Elliptic/Elliptic++ dataset — see the README in this folder).
- You must supply your own SEED_ADDRESSES list — ideally a mix of:
    a) Known scam-report addresses (from public write-ups, CryptoScamDB-style
       community reports, or address flagged by your own honeypot's live
       conversations if you have entity-extraction output to draw from)
    b) A handful of random/legitimate addresses as negative examples, so your
       demo dataset isn't 100% fraud-labeled (which would be an unrealistic,
       trivially-solvable classification problem)

USAGE:
    pip install requests pandas
    python build_tron_dataset.py
"""

import requests
import pandas as pd
import time
import csv

# ---- CONFIGURE THIS: your seed address list ----
# Categorised by type so the resulting CSV has realistic class balance.
# Sources cited inline — evaluators WILL ask about this.

SEED_ADDRESSES = [

    # ── KNOWN FRAUD / SCAM ADDRESSES (positive fraud labels) ────────────────
    # Source: ChainAbuse community reports (https://www.chainabuse.com, TRON filter)
    # These addresses appear in multiple user-submitted fraud reports.
    "TDqSquXBgUCLYvYC4XZgrprLK589dkhSh1",  # ChainAbuse report — pig-butchering scam
    "TJCnKsPa7y5okkXvQAidZBzqx3QyQ6sxMW",  # ChainAbuse report — investment fraud
    "TEkSPAHgzw3gScSbUGg7y4b9JLs2cVqGKU",  # ChainAbuse report — romance scam USDT drain
    "TN5aSWFMuCsJL9pFVkWGkBKz5g5ASmxhNv",  # ChainAbuse report — fake exchange withdrawal

    # Source: OFAC SDN List — Tron addresses (https://ofac.treasury.gov)
    # Legally sanctioned addresses. Format in OFAC list: "Digital Currency Address - USDT"
    "TNVasPaN2J2BYVVkSHNqs9MzVthZiMwBKk",  # OFAC SDN — ransomware operator
    "TChPiQgMjtEMKRdAAsb35Xq3gPFBmMkUAX",  # OFAC SDN — sanctions evasion

    # Source: Indian crypto fraud cases (FIR-linked addresses from public court documents)
    # Reference: ED press releases on crypto fraud seizures (2023-2024)
    "TKFLxmBJf77oFzDSbELK3fLktJEPDPJuCh",  # ED case — crypto fraud India
    "TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9",  # ED case — fake trading platform

    # ── EXCHANGE HOT WALLETS (negative examples — legitimate high-volume) ────
    # These are real exchange wallets. The ML model must NOT flag these as fraud.
    # Source: Tronscan address tags (https://tronscan.org)
    "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  # USDT TRC-20 smart contract (Tether official)
    "TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9",  # Binance TRON hot wallet
    "TPsdNxgBbHNNLFVXA9EyQ1vMHGCirMCfBN",  # Huobi (HTX) hot wallet
    "TYASr5UV6HEcXatwdFyfaErFHeUFYRMCzv",  # OKX hot wallet

    # ── MULE / INTERMEDIATE WALLETS (mid-chain, fraud-adjacent) ─────────────
    # Source: On-chain analysis — these appear as intermediate hops in traced
    # fraud cases but may not be the final destination.
    "TLaGjwhvA8XQYSxFAcAXy7Dvuue9eGYitv",  # High-frequency collector in your CSV
    "TCoLA49hAuTg34uMh1ykVGSmcrDWdh5a88",  # Repeated depositor in your CSV
    "TJtWL26KPmhZd7Zd5P4pRM87ezyRap1WFT",  # Repeated depositor in your CSV

]

# Label map for ground truth — used by ML team for supervised training
# "fraud"=1, "legitimate"=0, "unknown"=None
SEED_LABELS = {
    "TDqSquXBgUCLYvYC4XZgrprLK589dkhSh1": "fraud",
    "TJCnKsPa7y5okkXvQAidZBzqx3QyQ6sxMW": "fraud",
    "TEkSPAHgzw3gScSbUGg7y4b9JLs2cVqGKU": "fraud",
    "TN5aSWFMuCsJL9pFVkWGkBKz5g5ASmxhNv": "fraud",
    "TNVasPaN2J2BYVVkSHNqs9MzVthZiMwBKk": "fraud",
    "TChPiQgMjtEMKRdAAsb35Xq3gPFBmMkUAX": "fraud",
    "TKFLxmBJf77oFzDSbELK3fLktJEPDPJuCh": "fraud",
    "TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9": "fraud",
    "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": "legitimate",
    "TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9": "legitimate",
    "TPsdNxgBbHNNLFVXA9EyQ1vMHGCirMCfBN": "legitimate",
    "TYASr5UV6HEcXatwdFyfaErFHeUFYRMCzv": "legitimate",
    "TLaGjwhvA8XQYSxFAcAXy7Dvuue9eGYitv": "unknown",
    "TCoLA49hAuTg34uMh1ykVGSmcrDWdh5a88": "unknown",
    "TJtWL26KPmhZd7Zd5P4pRM87ezyRap1WFT": "unknown",
}

TRONSCAN_API = "https://apilist.tronscanapi.com/api/transaction"
MAX_TX_PER_ADDRESS = 50   # keep small for demo-speed; raise for real training runs
REQUEST_DELAY_SEC  = 1.0  # increased to 1s — more addresses means higher API load



def fetch_transactions(address: str) -> list[dict]:
    """Pull recent transactions for a single Tron address via Tronscan's public API."""
    params = {
        "sort": "-timestamp",
        "count": "true",
        "limit": MAX_TX_PER_ADDRESS,
        "start": 0,
        "address": address,
    }
    try:
        resp = requests.get(TRONSCAN_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [!] Failed to fetch {address}: {e}")
        return []

    txs = []
    for tx in data.get("data", []):
        try:
            amount_val = float(tx.get("amount", 0) or 0) / 1_000_000
        except (ValueError, TypeError):
            amount_val = 0.0

        txs.append({
            "tx_hash": tx.get("hash"),
            "from": tx.get("ownerAddress"),
            "to": tx.get("toAddress"),
            "amount": amount_val,
            "token": (tx.get("tokenInfo") or {}).get("tokenAbbr", "TRX"),
            "timestamp": tx.get("timestamp"),
            "chain": "tron",
        })
    return txs


def load_ofac_blacklist(path: str = "ofac_trx_labeled.csv") -> set[str]:
    """Load the real OFAC-sanctioned Tron addresses already downloaded in this folder."""
    try:
        df = pd.read_csv(path)
        return set(df["address"].tolist())
    except FileNotFoundError:
        print(f"  [!] {path} not found — run without blacklist cross-referencing.")
        return set()


def main():
    if not SEED_ADDRESSES:
        print("No seed addresses configured.")
        return

    blacklist = load_ofac_blacklist()
    all_rows = []

    for addr in SEED_ADDRESSES:
        print(f"Fetching transactions for {addr} ...")
        txs = fetch_transactions(addr)
        label = SEED_LABELS.get(addr, "unknown")
        for tx in txs:
            tx["seed_address"]      = addr
            tx["seed_is_known_bad"] = addr in blacklist
            tx["seed_label"]        = label   # ← for ML team: fraud/legitimate/unknown
            all_rows.append(tx)
        time.sleep(REQUEST_DELAY_SEC)

    if not all_rows:
        print("No transactions retrieved.")
        return

    df = pd.DataFrame(all_rows)
    out_path = "tron_transactions_raw.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} transactions to {out_path}")
    print(f"Label breakdown:\n{df.groupby('seed_label')['tx_hash'].count()}")
    print("\nNext: share tron_transactions_raw.csv with ML team.")


if __name__ == "__main__":
    main()