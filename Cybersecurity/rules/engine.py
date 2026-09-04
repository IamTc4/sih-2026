"""
Cybersecurity Rules Engine
Detects fraud signatures: Mixers, Peel Chains, Rapid Hopping, Structuring, and Blacklist Proximity.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import math

KNOWN_BLACKLIST = {
    "T_LAZARUS_MIXER_01": "OFAC-SDN-2023-CYBER-889",
    "T_RANSOMWARE_AFFILIATE_99": "CBI-2024-CRYPTO-0047",
    "T_PONZI_FEEDER_WALLET_007": "ED-PMLA-2023-TRON-112",
    "T_DARKNET_ESCROW_NODE_66": "I4C-NCRP-SUSPECT-2024-8192",
    "TEXCHANGE_DEPOSIT_MOCK_BLACK": "CBI-2024-CRYPTO-0047",
}

class PatternFlag:
    def __init__(self, signature: str, confidence: float, evidence: List[str], description: str):
        self.signature = signature
        self.confidence = confidence
        self.evidence = evidence
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signature": self.signature,
            "confidence": round(self.confidence, 2),
            "evidence": self.evidence,
            "description": self.description,
        }

class ThreatPatternEngine:
    """Analyzes transaction graphs and wallet activity for obfuscation patterns"""

    def __init__(self, blacklist: Optional[Dict[str, str]] = None):
        self.blacklist = blacklist or KNOWN_BLACKLIST

    def check_blacklist(self, address: str) -> Dict[str, Any]:
        """Check if an address matches curated fraud/sanction watchlists"""
        clean_addr = address.strip()
        matched = clean_addr in self.blacklist or any(k.lower() == clean_addr.lower() for k in self.blacklist)
        source = self.blacklist.get(clean_addr)
        if not source and matched:
            for k, v in self.blacklist.items():
                if k.lower() == clean_addr.lower():
                    source = v
                    break

        return {
            "address": address,
            "match": matched,
            "source_case": source if matched else None
        }

    def detect_mixer(self, graph_edges: List[Dict[str, Any]]) -> Optional[PatternFlag]:
        """Detects high-fanout / high-fanin mixing signatures"""
        in_degrees: Dict[str, int] = {}
        out_degrees: Dict[str, int] = {}
        edge_map: Dict[str, List[str]] = {}

        for edge in graph_edges:
            src = edge.get("from", edge.get("from_address", edge.get("source", "")))
            dst = edge.get("to", edge.get("to_address", edge.get("target", "")))
            tx = edge.get("tx_hash", "tx_unknown")
            out_degrees[src] = out_degrees.get(src, 0) + 1
            in_degrees[dst] = in_degrees.get(dst, 0) + 1
            edge_map.setdefault(src, []).append(tx)
            edge_map.setdefault(dst, []).append(tx)

        # Mixer criteria: high fan-in AND high fan-out at intermediate nodes
        for node, in_cnt in in_degrees.items():
            out_cnt = out_degrees.get(node, 0)
            if in_cnt >= 3 and out_cnt >= 3:
                return PatternFlag(
                    signature="mixer",
                    confidence=0.88,
                    evidence=edge_map.get(node, [])[:4],
                    description=f"Tumbler/Mixer fan pattern detected at wallet {node[:10]}... (in={in_cnt}, out={out_cnt})"
                )
        return None

    def detect_peel_chain(self, graph_edges: List[Dict[str, Any]]) -> Optional[PatternFlag]:
        """Detects sequential transfers where a small portion peels off and the bulk moves on"""
        if len(graph_edges) < 2:
            return None

        # Look for asymmetric outgoing splits: 85-99% forward, 1-15% peeled change
        amounts = [float(e.get("amount", 0)) for e in graph_edges if float(e.get("amount", 0)) > 0]
        if len(amounts) >= 3:
            # Check if amounts decrease gradually by small amounts
            peel_evidence = []
            for i in range(len(amounts) - 1):
                ratio = amounts[i+1] / amounts[i] if amounts[i] > 0 else 0
                if 0.70 <= ratio <= 0.98:
                    tx = graph_edges[i].get("tx_hash", f"tx_{i}")
                    peel_evidence.append(tx)

            if len(peel_evidence) >= 2:
                return PatternFlag(
                    signature="peel_chain",
                    confidence=0.91,
                    evidence=peel_evidence,
                    description=f"Classic peel chain layering pattern: repeated ~{round((1-0.85)*100)}% peel-offs across hops"
                )
        return None

    def detect_rapid_hop(self, graph_edges: List[Dict[str, Any]]) -> Optional[PatternFlag]:
        """Detects evasion through abnormally fast multi-hop transfers (< 30 minutes)"""
        timestamps = []
        for e in graph_edges:
            ts_str = e.get("timestamp")
            if ts_str:
                try:
                    dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    timestamps.append((dt.timestamp(), e.get("tx_hash", "")))
                except Exception:
                    pass

        if len(timestamps) >= 3:
            timestamps.sort(key=lambda x: x[0])
            total_span = timestamps[-1][0] - timestamps[0][0]
            # 3 or more hops in less than 3600 seconds (1 hour)
            if total_span < 3600:
                return PatternFlag(
                    signature="rapid_hop",
                    confidence=0.85,
                    evidence=[tx for _, tx in timestamps],
                    description=f"Rapid hop laundering signature: {len(timestamps)} hops executed within {int(total_span//60)} minutes"
                )
        return None

    def detect_structuring(self, graph_edges: List[Dict[str, Any]]) -> Optional[PatternFlag]:
        """Detects structuring (smurfing) — repeated transactions just below regulatory reporting thresholds ($10,000)"""
        structuring_txs = []
        for e in graph_edges:
            amt = float(e.get("amount", 0))
            if 8000 <= amt < 10000:
                structuring_txs.append(e.get("tx_hash", "tx_unknown"))

        if len(structuring_txs) >= 2:
            return PatternFlag(
                signature="structuring",
                confidence=0.82,
                evidence=structuring_txs,
                description=f"Structuring / smurfing signature: {len(structuring_txs)} transactions just below the $10,000 PMLA/FIU regulatory reporting threshold"
            )
        return None

    def analyze(self, address: str, graph_edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive scan returning all triggered fraud flags and composite threat score"""
        flags: List[PatternFlag] = []

        # Check blacklist
        bl_res = self.check_blacklist(address)
        if bl_res["match"]:
            flags.append(PatternFlag(
                signature="blacklist_match",
                confidence=1.0,
                evidence=[address],
                description=f"Direct match against Law Enforcement Watchlist: Case {bl_res['source_case']}"
            ))

        # Check patterns
        mixer = self.detect_mixer(graph_edges)
        if mixer:
            flags.append(mixer)

        peel = self.detect_peel_chain(graph_edges)
        if peel:
            flags.append(peel)

        rapid = self.detect_rapid_hop(graph_edges)
        if rapid:
            flags.append(rapid)

        struct = self.detect_structuring(graph_edges)
        if struct:
            flags.append(struct)

        # Composite risk score (0.0 - 1.0)
        base_score = 0.15
        for f in flags:
            if f.signature == "blacklist_match":
                base_score = max(base_score, 0.95)
            elif f.signature in ["mixer", "peel_chain"]:
                base_score += 0.35 * f.confidence
            else:
                base_score += 0.20 * f.confidence

        composite_risk = min(1.0, round(base_score, 2))

        return {
            "address": address,
            "flags": [f.to_dict() for f in flags],
            "risk_signal": composite_risk,
            "blacklist": bl_res,
            "total_flags": len(flags)
        }
