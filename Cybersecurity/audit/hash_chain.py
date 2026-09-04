"""
Cybersecurity Audit Trail — Tamper-Evident Hash Chain
Anchors every trace, cluster result, risk score, and legal notice into an immutable SHA-256 chain of custody.
"""
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class HashChainBlock:
    def __init__(self, entry_id: str, event_type: str, payload: Dict[str, Any], prev_hash: str, timestamp: Optional[str] = None):
        self.entry_id = entry_id
        self.event_type = event_type
        self.payload = payload
        self.prev_hash = prev_hash
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.content_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        # Canonical JSON representation for deterministic hashing
        serialized_payload = json.dumps(self.payload, sort_keys=True)
        raw = f"{self.entry_id}|{self.event_type}|{serialized_payload}|{self.prev_hash}|{self.timestamp}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "content_hash": self.content_hash,
            "logged": True
        }

class AuditLedger:
    """In-memory append-only tamper-evident hash-chain ledger"""

    def __init__(self):
        self.chain: List[HashChainBlock] = []
        self._seed_genesis()

    def _seed_genesis(self):
        genesis = HashChainBlock(
            entry_id="EVT-GENESIS-000",
            event_type="GENESIS_BLOCK",
            payload={"system": "WalletTrace", "version": "1.0.0", "mha_compliance": "SIH26183"},
            prev_hash="0000000000000000000000000000000000000000000000000000000000000000",
            timestamp="2026-09-04T00:00:00Z"
        )
        self.chain.append(genesis)

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Appends a new event to the hash chain and returns proof"""
        prev_hash = self.chain[-1].content_hash
        entry_id = f"EVT-{len(self.chain):04d}"

        block = HashChainBlock(
            entry_id=entry_id,
            event_type=event_type,
            payload=payload,
            prev_hash=prev_hash
        )
        self.chain.append(block)

        return {
            "entry_id": block.entry_id,
            "entry_hash": block.content_hash,
            "content_hash": block.content_hash,
            "prev_hash": block.prev_hash,
            "timestamp": block.timestamp,
            "logged": True
        }

    def verify_entry(self, entry_id: str) -> Dict[str, Any]:
        """Verifies individual entry hash and chain of custody integrity"""
        for i, block in enumerate(self.chain):
            if block.entry_id == entry_id:
                # 1. Verify content hash
                recomputed = block._calculate_hash()
                hash_valid = (recomputed == block.content_hash)

                # 2. Verify link to previous block
                link_valid = True
                if i > 0:
                    link_valid = (block.prev_hash == self.chain[i-1].content_hash)

                return {
                    "entry_id": entry_id,
                    "valid": hash_valid and link_valid,
                    "chain_intact": link_valid,
                    "content_hash": block.content_hash,
                    "recomputed_hash": recomputed,
                    "timestamp": block.timestamp
                }

        return {
            "entry_id": entry_id,
            "valid": False,
            "chain_intact": False,
            "error": "Entry ID not found in ledger"
        }

    def get_all_entries(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.chain]
