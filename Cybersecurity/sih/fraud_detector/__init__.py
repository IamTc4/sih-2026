"""
Fraud Pattern / Threat Signature Library
Rules-based detector for known fraud techniques in transaction graphs.
"""

from .detector import FraudDetector, DetectorConfig, DetectionResult
from .patterns import (
    TransactionGraph,
    MixerTumblerPattern,
    PeelChainPattern,
    RapidHoppingPattern,
    ScamClusterProximityPattern,
    StructuringPattern,
)

__all__ = [
    "FraudDetector",
    "DetectorConfig",
    "DetectionResult",
    "TransactionGraph",
    "MixerTumblerPattern",
    "PeelChainPattern",
    "RapidHoppingPattern",
    "ScamClusterProximityPattern",
    "StructuringPattern",
]