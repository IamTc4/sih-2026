"""
Evidence Trail / Hash-Anchoring Service
Tamper-evident logging with hash-chain integrity verification.
"""

from .service import EvidenceTrailService, LogEntry
from .api import create_app

__all__ = ["EvidenceTrailService", "LogEntry", "create_app"]