import sqlite3
import json
from datetime import datetime

DB_PATH = "cases.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            addresses TEXT,
            exchange TEXT,
            filed_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_case(case_id: str, addresses: list[str], exchange: str | None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO cases VALUES (?, ?, ?, ?)",
        (case_id, json.dumps(addresses), exchange, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def find_overlaps(addresses: list[str], exclude_case_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT case_id, addresses, exchange, filed_date FROM cases").fetchall()
    conn.close()

    current_set = set(addresses)
    matches = []
    for case_id, addr_json, exchange, filed_date in rows:
        if case_id == exclude_case_id:
            continue
        stored_set = set(json.loads(addr_json))
        overlap = current_set & stored_set
        if overlap:
            matches.append({
                "case_id": case_id,
                "overlap_addresses": list(overlap),
                "exchange": exchange,
                "filed_date": filed_date
            })
    return matches