"""
Data redaction utilities for PII protection.
"""

import re
from dataclasses import dataclass, field
from typing import Any
from .models import DataClassification, DEFAULT_DATA_POLICIES


@dataclass
class RedactionRules:
    """Configurable redaction rules for different PII categories."""
    patterns: dict[str, list[tuple[re.Pattern, str]]] = field(default_factory=dict)

    def __post_init__(self):
        self._init_default_patterns()

    def _init_default_patterns(self):
        """Initialize default regex patterns for common PII."""
        self.patterns = {
            "email": [
                (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), "[EMAIL]")
            ],
            "phone": [
                (re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'), "[PHONE]"),
                (re.compile(r'\b\d{10,}\b'), "[PHONE]")
            ],
            "name": [
                # This is heuristic - real implementation would use NER
                (re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'), "[NAME]")
            ],
            "ssn": [
                (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), "[SSN]")
            ],
            "credit_card": [
                (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), "[CARD]")
            ],
            "ip_address": [
                (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), "[IP]")
            ],
            "eth_address": [
                (re.compile(r'\b0x[a-fA-F0-9]{40}\b'), "[WALLET]")
            ],
            "tx_hash": [
                (re.compile(r'\b0x[a-fA-F0-9]{64}\b'), "[TX_HASH]")
            ],
        }

    def add_pattern(self, category: str, pattern: re.Pattern, replacement: str):
        """Add a custom redaction pattern."""
        if category not in self.patterns:
            self.patterns[category] = []
        self.patterns[category].append((pattern, replacement))

    def redact_text(self, text: str, categories: list[str] | None = None) -> str:
        """Redact PII from free text."""
        if not isinstance(text, str):
            return text

        categories = categories or list(self.patterns.keys())
        result = text

        for category in categories:
            if category in self.patterns:
                for pattern, replacement in self.patterns[category]:
                    result = pattern.sub(replacement, result)

        return result

    def redact_dict(self, data: dict[str, Any], user_role: str | None = None) -> dict[str, Any]:
        """Redact PII fields in a dictionary based on classification."""
        result = {}

        for key, value in data.items():
            policy = DEFAULT_DATA_POLICIES.get(key)

            if policy is None:
                # Unknown field - conservative: redact if looks like PII
                if isinstance(value, str) and self._looks_like_pii(value):
                    result[key] = "[REDACTED]"
                else:
                    result[key] = value
                continue

            # Check if user role can access this classification
            if user_role and self._role_can_access(user_role, policy.classification):
                result[key] = value
            elif policy.classification in {DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED}:
                # Redact based on PII category
                if isinstance(value, str) and policy.pii_category:
                    result[key] = self._redact_by_category(value, policy.pii_category)
                else:
                    result[key] = f"[REDACTED: {policy.classification.value}]"
            else:
                result[key] = value

        return result

    def _role_can_access(self, role: str, classification: DataClassification) -> bool:
        """Check if role can access classification level."""
        from .models import UserRole, ROLE_FIELD_ACCESS
        try:
            user_role = UserRole(role)
            return classification in ROLE_FIELD_ACCESS.get(user_role, set())
        except ValueError:
            return False

    def _looks_like_pii(self, text: str) -> bool:
        """Heuristic check if text might contain PII."""
        for category, patterns in self.patterns.items():
            for pattern, _ in patterns:
                if pattern.search(text):
                    return True
        return False

    def _redact_by_category(self, text: str, category: str) -> str:
        """Redact text using patterns for a specific PII category."""
        if category not in self.patterns:
            return "[REDACTED]"

        result = text
        for pattern, replacement in self.patterns[category]:
            result = pattern.sub(replacement, result)
        return result


# Global redaction rules instance
_redaction_rules: RedactionRules | None = None


def get_redaction_rules() -> RedactionRules:
    global _redaction_rules
    if _redaction_rules is None:
        _redaction_rules = RedactionRules()
    return _redaction_rules


def redact_payload(
    payload: dict[str, Any],
    user_role: str | None = None,
    rules: RedactionRules | None = None
) -> dict[str, Any]:
    """
    Redact PII from a payload based on user role and data classification.

    Args:
        payload: Data payload to redact
        user_role: Role of the requesting user (VIEWER, ANALYST, INVESTIGATOR, ADMIN)
        rules: Optional custom redaction rules

    Returns:
        Redacted payload safe for the user's role
    """
    rules = rules or get_redaction_rules()
    return rules.redact_dict(payload, user_role)


def redact_text(text: str, categories: list[str] | None = None) -> str:
    """Redact PII from free text."""
    return get_redaction_rules().redact_text(text, categories)


class Anonymizer:
    """Anonymize data for analytics while preserving structure."""

    def __init__(self):
        self._address_map: dict[str, str] = {}
        self._counter = 0

    def anonymize_address(self, address: str) -> str:
        """Replace wallet address with consistent anonymized identifier."""
        if address not in self._address_map:
            self._counter += 1
            self._address_map[address] = f"ADDR_{self._counter:06d}"
        return self._address_map[address]

    def anonymize_tx_hash(self, tx_hash: str) -> str:
        """Replace tx hash with consistent anonymized identifier."""
        if tx_hash not in self._address_map:
            self._counter += 1
            self._address_map[tx_hash] = f"TX_{self._counter:06d}"
        return self._address_map[tx_hash]

    def anonymize_graph(self, graph: dict[str, Any]) -> dict[str, Any]:
        """Anonymize a transaction graph."""
        # This is a simplified version - real implementation would traverse the graph
        result = {}
        for key, value in graph.items():
            if key in ("nodes", "addresses") and isinstance(value, list):
                result[key] = [self.anonymize_address(v) if isinstance(v, str) else v for v in value]
            elif key in ("edges", "transactions") and isinstance(value, list):
                result[key] = [
                    {**e, "from": self.anonymize_address(e.get("from", "")),
                     "to": self.anonymize_address(e.get("to", ""))}
                    if isinstance(e, dict) else e
                    for e in value
                ]
            else:
                result[key] = value
        return result