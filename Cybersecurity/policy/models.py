"""
Data classification and user role definitions.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any


class DataClassification(str, Enum):
    """Classification levels for data sensitivity."""
    PUBLIC = "public"           # Safe for anyone: wallet addresses, trace graphs, risk scores
    INTERNAL = "internal"       # Internal use only: cluster metadata, analysis results
    CONFIDENTIAL = "confidential"  # Restricted: victim names, contact info, raw complaints
    RESTRICTED = "restricted"   # Highly restricted: PII, legal notices, investigation details


class UserRole(str, Enum):
    """User roles for RBAC."""
    VIEWER = "viewer"           # Read-only access to PUBLIC data
    ANALYST = "analyst"         # Read PUBLIC + INTERNAL, write analysis results
    INVESTIGATOR = "investigator"  # Full access including CONFIDENTIAL/RESTRICTED
    ADMIN = "admin"             # Full access + user management
    SYSTEM = "system"           # Service-to-service, full access


# Role hierarchy (higher roles inherit lower role permissions)
ROLE_HIERARCHY = {
    UserRole.VIEWER: 1,
    UserRole.ANALYST: 2,
    UserRole.INVESTIGATOR: 3,
    UserRole.ADMIN: 4,
    UserRole.SYSTEM: 5,
}


@dataclass
class DataPolicy:
    """Policy defining data classification and handling rules."""
    field_name: str
    classification: DataClassification
    description: str
    pii_category: str | None = None  # e.g., "name", "email", "phone", "address"
    retention_days: int | None = None
    encryption_required: bool = False
    audit_access: bool = True


# Default data policy mapping for the fraud detection system
DEFAULT_DATA_POLICIES: dict[str, DataPolicy] = {
    # PUBLIC - Safe for all roles
    "wallet_address": DataPolicy(
        field_name="wallet_address",
        classification=DataClassification.PUBLIC,
        description="Blockchain wallet address (public identifier)",
        pii_category=None
    ),
    "tx_hash": DataPolicy(
        field_name="tx_hash",
        classification=DataClassification.PUBLIC,
        description="Transaction hash (public on-chain)",
        pii_category=None
    ),
    "trace_graph": DataPolicy(
        field_name="trace_graph",
        classification=DataClassification.PUBLIC,
        description="Transaction trace graph (derived from public data)",
        pii_category=None
    ),
    "risk_score": DataPolicy(
        field_name="risk_score",
        classification=DataClassification.PUBLIC,
        description="Calculated risk score (0-100)",
        pii_category=None
    ),
    "cluster_id": DataPolicy(
        field_name="cluster_id",
        classification=DataClassification.PUBLIC,
        description="Cluster identifier from ML grouping",
        pii_category=None
    ),
    "fraud_signature": DataPolicy(
        field_name="fraud_signature",
        classification=DataClassification.PUBLIC,
        description="Detected fraud pattern signature",
        pii_category=None
    ),
    "confidence": DataPolicy(
        field_name="confidence",
        classification=DataClassification.PUBLIC,
        description="Detection confidence score",
        pii_category=None
    ),
    "evidence_tx_hashes": DataPolicy(
        field_name="evidence_tx_hashes",
        classification=DataClassification.PUBLIC,
        description="Transaction hashes used as evidence",
        pii_category=None
    ),

    # INTERNAL - Analyst and above
    "cluster_metadata": DataPolicy(
        field_name="cluster_metadata",
        classification=DataClassification.INTERNAL,
        description="ML cluster metadata and statistics",
        pii_category=None
    ),
    "analysis_notes": DataPolicy(
        field_name="analysis_notes",
        classification=DataClassification.INTERNAL,
        description="Analyst notes and annotations",
        pii_category=None
    ),
    "attribution_data": DataPolicy(
        field_name="attribution_data",
        classification=DataClassification.INTERNAL,
        description="Exchange/service attribution results",
        pii_category=None
    ),

    # CONFIDENTIAL - Investigator and above
    "victim_name": DataPolicy(
        field_name="victim_name",
        classification=DataClassification.CONFIDENTIAL,
        description="Victim full name",
        pii_category="name",
        encryption_required=True,
        audit_access=True
    ),
    "victim_email": DataPolicy(
        field_name="victim_email",
        classification=DataClassification.CONFIDENTIAL,
        description="Victim email address",
        pii_category="email",
        encryption_required=True,
        audit_access=True
    ),
    "victim_phone": DataPolicy(
        field_name="victim_phone",
        classification=DataClassification.CONFIDENTIAL,
        description="Victim phone number",
        pii_category="phone",
        encryption_required=True,
        audit_access=True
    ),
    "complaint_text": DataPolicy(
        field_name="complaint_text",
        classification=DataClassification.CONFIDENTIAL,
        description="Raw complaint submission text",
        pii_category="free_text",
        encryption_required=True,
        audit_access=True
    ),
    "complaint_metadata": DataPolicy(
        field_name="complaint_metadata",
        classification=DataClassification.CONFIDENTIAL,
        description="Complaint submission metadata (IP, timestamp, user agent)",
        pii_category="metadata",
        encryption_required=True,
        audit_access=True
    ),

    # RESTRICTED - Investigator/Admin only
    "legal_notice": DataPolicy(
        field_name="legal_notice",
        classification=DataClassification.RESTRICTED,
        description="Generated legal notice content",
        pii_category="legal",
        encryption_required=True,
        audit_access=True
    ),
    "investigation_details": DataPolicy(
        field_name="investigation_details",
        classification=DataClassification.RESTRICTED,
        description="Detailed investigation findings",
        pii_category="investigation",
        encryption_required=True,
        audit_access=True
    ),
    "takedown_request": DataPolicy(
        field_name="takedown_request",
        classification=DataClassification.RESTRICTED,
        description="Exchange takedown/freeze request details",
        pii_category="legal",
        encryption_required=True,
        audit_access=True
    ),
}


# Role-based field access matrix
ROLE_FIELD_ACCESS: dict[UserRole, set[DataClassification]] = {
    UserRole.VIEWER: {DataClassification.PUBLIC},
    UserRole.ANALYST: {DataClassification.PUBLIC, DataClassification.INTERNAL},
    UserRole.INVESTIGATOR: {
        DataClassification.PUBLIC,
        DataClassification.INTERNAL,
        DataClassification.CONFIDENTIAL,
        DataClassification.RESTRICTED
    },
    UserRole.ADMIN: {
        DataClassification.PUBLIC,
        DataClassification.INTERNAL,
        DataClassification.CONFIDENTIAL,
        DataClassification.RESTRICTED
    },
    UserRole.SYSTEM: {
        DataClassification.PUBLIC,
        DataClassification.INTERNAL,
        DataClassification.CONFIDENTIAL,
        DataClassification.RESTRICTED
    },
}