"""
Core Evidence Trail Service with Hash-Chaining
"""

import hashlib
import json
import sqlite3
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional
from pathlib import Path


@dataclass
class LogEntry:
    """A single entry in the hash-chain log."""
    entry_id: int
    timestamp: str
    event_type: str
    payload: dict[str, Any]
    content_hash: str
    previous_hash: str
    chain_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: tuple) -> "LogEntry":
        return cls(
            entry_id=row[0],
            timestamp=row[1],
            event_type=row[2],
            payload=json.loads(row[3]),
            content_hash=row[4],
            previous_hash=row[5],
            chain_hash=row[6]
        )


class EvidenceTrailService:
    """
    Hash-chain based tamper-evident log service.
    Each entry contains: content hash + previous entry's hash.
    """

    def __init__(self, db_path: str = "evidence_trail.db"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with hash-chain table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_log (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    chain_hash TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type ON evidence_log(event_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON evidence_log(timestamp)
            """)
            conn.commit()

    def _compute_content_hash(self, event_type: str, payload: dict[str, Any]) -> str:
        """Compute SHA-256 hash of event content."""
        content = json.dumps({"event_type": event_type, "payload": payload}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _compute_chain_hash(self, content_hash: str, previous_hash: str) -> str:
        """Compute chain hash linking this entry to previous."""
        combined = f"{previous_hash}{content_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _get_latest_hash(self) -> str:
        """Get the chain_hash of the most recent entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT chain_hash FROM evidence_log ORDER BY entry_id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return row[0] if row else "0" * 64  # Genesis hash

    def log_event(self, event_type: str, payload: dict[str, Any]) -> LogEntry:
        """
        Serialize an event, hash it, append to immutable log.

        Args:
            event_type: Type of event (e.g., "wallet_trace", "cluster_result")
            payload: Event data to log

        Returns:
            LogEntry with all hash-chain fields populated
        """
        with self._lock:
            timestamp = datetime.utcnow().isoformat() + "Z"
            content_hash = self._compute_content_hash(event_type, payload)
            previous_hash = self._get_latest_hash()
            chain_hash = self._compute_chain_hash(content_hash, previous_hash)

            entry = LogEntry(
                entry_id=0,  # Will be set by DB
                timestamp=timestamp,
                event_type=event_type,
                payload=payload,
                content_hash=content_hash,
                previous_hash=previous_hash,
                chain_hash=chain_hash
            )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """INSERT INTO evidence_log
                       (timestamp, event_type, payload, content_hash, previous_hash, chain_hash)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (entry.timestamp, entry.event_type, json.dumps(entry.payload),
                     entry.content_hash, entry.previous_hash, entry.chain_hash)
                )
                entry.entry_id = cursor.lastrowid
                conn.commit()

            return entry

    def verify_entry(self, entry_id: int) -> dict[str, Any]:
        """
        Verify a single entry's hash integrity.

        Returns:
            Dict with verification results
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM evidence_log WHERE entry_id = ?", (entry_id,)
            )
            row = cursor.fetchone()

        if not row:
            return {
                "valid": False,
                "entry_id": entry_id,
                "error": "Entry not found"
            }

        entry = LogEntry.from_row(row)

        # Recompute content hash
        expected_content_hash = self._compute_content_hash(entry.event_type, entry.payload)
        content_valid = entry.content_hash == expected_content_hash

        # Verify chain linkage
        previous_entry = self.get_entry(entry_id - 1) if entry_id > 1 else None
        expected_previous_hash = previous_entry.chain_hash if previous_entry else "0" * 64
        chain_valid = entry.previous_hash == expected_previous_hash

        # Recompute chain hash
        expected_chain_hash = self._compute_chain_hash(entry.content_hash, entry.previous_hash)
        chain_hash_valid = entry.chain_hash == expected_chain_hash

        return {
            "valid": content_valid and chain_valid and chain_hash_valid,
            "entry_id": entry_id,
            "content_hash_valid": content_valid,
            "chain_link_valid": chain_valid,
            "chain_hash_valid": chain_hash_valid,
            "entry": entry.to_dict()
        }

    def verify_chain(self, start_id: int = 1, end_id: Optional[int] = None) -> dict[str, Any]:
        """
        Verify the entire hash-chain from start_id to end_id (or latest).

        Returns:
            Dict with chain verification results
        """
        with sqlite3.connect(self.db_path) as conn:
            if end_id is None:
                cursor = conn.execute(
                    "SELECT * FROM evidence_log WHERE entry_id >= ? ORDER BY entry_id",
                    (start_id,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM evidence_log WHERE entry_id BETWEEN ? AND ? ORDER BY entry_id",
                    (start_id, end_id)
                )
            rows = cursor.fetchall()

        if not rows:
            return {"valid": True, "entries_checked": 0, "errors": []}

        errors = []
        previous_chain_hash = "0" * 64

        for row in rows:
            entry = LogEntry.from_row(row)

            # Verify content hash
            expected_content = self._compute_content_hash(entry.event_type, entry.payload)
            if entry.content_hash != expected_content:
                errors.append(f"Entry {entry.entry_id}: content hash mismatch")

            # Verify chain link
            if entry.previous_hash != previous_chain_hash:
                errors.append(f"Entry {entry.entry_id}: broken chain link")

            # Verify chain hash
            expected_chain = self._compute_chain_hash(entry.content_hash, entry.previous_hash)
            if entry.chain_hash != expected_chain:
                errors.append(f"Entry {entry.entry_id}: chain hash mismatch")

            previous_chain_hash = entry.chain_hash

        return {
            "valid": len(errors) == 0,
            "entries_checked": len(rows),
            "errors": errors,
            "final_chain_hash": previous_chain_hash
        }

    def get_entry(self, entry_id: int) -> Optional[LogEntry]:
        """Retrieve a single log entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM evidence_log WHERE entry_id = ?", (entry_id,)
            )
            row = cursor.fetchone()
        return LogEntry.from_row(row) if row else None

    def get_entries(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[LogEntry]:
        """Retrieve log entries with optional filtering."""
        with sqlite3.connect(self.db_path) as conn:
            if event_type:
                cursor = conn.execute(
                    "SELECT * FROM evidence_log WHERE event_type = ? ORDER BY entry_id DESC LIMIT ? OFFSET ?",
                    (event_type, limit, offset)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM evidence_log ORDER BY entry_id DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            rows = cursor.fetchall()

        return [LogEntry.from_row(row) for row in rows]

    def get_latest_entry(self) -> Optional[LogEntry]:
        """Get the most recent log entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM evidence_log ORDER BY entry_id DESC LIMIT 1"
            )
            row = cursor.fetchone()
        return LogEntry.from_row(row) if row else None

    def export_chain(self, filepath: str):
        """Export the entire chain for external verification/anchoring."""
        entries = self.get_entries(limit=1000000)
        data = {
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "total_entries": len(entries),
            "chain": [e.to_dict() for e in entries]
        }
        Path(filepath).write_text(json.dumps(data, indent=2))

    def anchor_to_public_chain(self, entry_id: int, tx_hash: str, block_number: int) -> bool:
        """
        Record an anchor to a public blockchain (e.g., Ethereum).
        This is a placeholder for production integration.
        """
        # In production, this would verify the anchor on-chain
        # For now, we log it as a special event
        anchor_payload = {
            "anchored_entry_id": entry_id,
            "public_chain_tx_hash": tx_hash,
            "public_chain_block": block_number,
            "anchor_type": "ethereum"
        }
        self.log_event("public_chain_anchor", anchor_payload)
        return True