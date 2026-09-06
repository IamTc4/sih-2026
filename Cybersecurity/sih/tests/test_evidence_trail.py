"""
Tests for Evidence Trail Service
"""

import pytest
import json
import time
from evidence_trail import EvidenceTrailService, LogEntry


class TestEvidenceTrailService:
    """Test the hash-chain evidence trail service."""

    def setup_method(self):
        """Create a fresh service for each test."""
        self.service = EvidenceTrailService("test_evidence.db")

    def test_log_event_creates_entry(self):
        entry = self.service.log_event("wallet_trace", {"address": "0x123", "hops": 5})

        assert entry.entry_id == 1
        assert entry.event_type == "wallet_trace"
        assert entry.payload == {"address": "0x123", "hops": 5}
        assert len(entry.content_hash) == 64  # SHA-256 hex
        assert len(entry.previous_hash) == 64
        assert len(entry.chain_hash) == 64
        assert entry.previous_hash == "0" * 64  # Genesis

    def test_chain_links_correctly(self):
        e1 = self.service.log_event("event1", {"data": "first"})
        e2 = self.service.log_event("event2", {"data": "second"})
        e3 = self.service.log_event("event3", {"data": "third"})

        # Each entry's previous_hash should match prior entry's chain_hash
        assert e2.previous_hash == e1.chain_hash
        assert e3.previous_hash == e2.chain_hash

        # Chain hashes should be correctly computed
        import hashlib
        expected_chain_2 = hashlib.sha256((e1.chain_hash + e2.content_hash).encode()).hexdigest()
        assert e2.chain_hash == expected_chain_2

    def test_verify_valid_entry(self):
        entry = self.service.log_event("test_event", {"key": "value"})
        result = self.service.verify_entry(entry.entry_id)

        assert result["valid"] is True
        assert result["content_hash_valid"] is True
        assert result["chain_link_valid"] is True
        assert result["chain_hash_valid"] is True
        assert result["entry_id"] == entry.entry_id

    def test_verify_nonexistent_entry(self):
        result = self.service.verify_entry(999)
        assert result["valid"] is False
        assert "not found" in result["error"].lower()

    def test_verify_chain_integrity(self):
        for i in range(5):
            self.service.log_event(f"event_{i}", {"seq": i})

        result = self.service.verify_chain()
        assert result["valid"] is True
        assert result["entries_checked"] == 5
        assert len(result["errors"]) == 0

    def test_verify_chain_detects_tampering(self):
        # Add entries
        e1 = self.service.log_event("event1", {"data": "original"})

        # Manually corrupt the database
        import sqlite3
        with sqlite3.connect("test_evidence.db") as conn:
            conn.execute(
                "UPDATE evidence_log SET payload = ? WHERE entry_id = ?",
                (json.dumps({"data": "TAMPERED"}), 1)
            )
            conn.commit()

        # Verification should catch it
        result = self.service.verify_entry(1)
        assert result["valid"] is False
        assert result["content_hash_valid"] is False

        chain_result = self.service.verify_chain()
        assert chain_result["valid"] is False
        assert any("content hash mismatch" in e for e in chain_result["errors"])

    def test_get_entries_with_filtering(self):
        self.service.log_event("wallet_trace", {"addr": "0x1"})
        self.service.log_event("cluster_result", {"cluster": 5})
        self.service.log_event("wallet_trace", {"addr": "0x2"})

        all_entries = self.service.get_entries(limit=10)
        assert len(all_entries) == 3

        trace_entries = self.service.get_entries(event_type="wallet_trace", limit=10)
        assert len(trace_entries) == 2
        assert all(e.event_type == "wallet_trace" for e in trace_entries)

    def test_export_chain(self):
        self.service.log_event("event1", {"data": "1"})
        self.service.log_event("event2", {"data": "2"})

        self.service.export_chain("test_export.json")

        import os
        assert os.path.exists("test_export.json")

        with open("test_export.json") as f:
            data = json.load(f)

        assert data["total_entries"] == 2
        assert len(data["chain"]) == 2
        assert data["chain"][0]["event_type"] == "event1"

    def test_anchor_to_public_chain(self):
        entry = self.service.log_event("original", {"data": "test"})

        # Anchor should create a new log entry
        result = self.service.anchor_to_public_chain(entry.entry_id, "0xabc...", 12345)
        assert result is True

        # Check anchor entry exists
        entries = self.service.get_entries(event_type="public_chain_anchor")
        assert len(entries) == 1
        assert entries[0].payload["anchored_entry_id"] == entry.entry_id
        assert entries[0].payload["public_chain_tx_hash"] == "0xabc..."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])