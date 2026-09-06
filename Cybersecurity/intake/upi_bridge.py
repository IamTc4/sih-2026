"""
CryptoSentinel UPI → Crypto Investigation Bridge
Maps Indian banking fraud complaints to cryptocurrency investigation leads.

Indian fraud corridor: Victim → UPI → P2P exchange (Binance P2P / WazirX / CoinDCX) → USDT → Tron/ETH → Scammer
"""
import re
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# ── Known P2P Crypto Corridors (India) ───────────────────────────────────────
P2P_EXCHANGE_PATTERNS = {
    "binance_p2p": {
        "name": "Binance P2P",
        "legal_entity": "Binance Holdings Ltd",
        "compliance_email": "compliance@binance.com",
        "legal_notice_authority": "Section 91 BNSS / PMLA Section 12AA",
        "kyc_data_available": True,
        "upi_linked": True,
        "known_upi_prefixes": ["BINANCEPAY", "BNB"],
        "kyc_demand_template": "BINANCE_COMPLIANCE_91BNSS",
    },
    "wazirx": {
        "name": "WazirX",
        "legal_entity": "Zanmai Labs Pvt Ltd",
        "compliance_email": "compliance@wazirx.com",
        "legal_notice_authority": "Section 91 BNSS / IT Act Section 69",
        "kyc_data_available": True,
        "upi_linked": True,
        "known_upi_prefixes": ["WAZIRX", "WRX"],
        "kyc_demand_template": "WAZIRX_COMPLIANCE_91BNSS",
    },
    "coindcx": {
        "name": "CoinDCX",
        "legal_entity": "Neblio Technologies Pvt Ltd",
        "compliance_email": "compliance@coindcx.com",
        "legal_notice_authority": "Section 91 BNSS / PMLA",
        "kyc_data_available": True,
        "upi_linked": True,
        "known_upi_prefixes": ["COINDCX", "DCX"],
        "kyc_demand_template": "COINDCX_COMPLIANCE_91BNSS",
    },
    "mudrex": {
        "name": "Mudrex",
        "legal_entity": "Mudrex Inc.",
        "compliance_email": "compliance@mudrex.com",
        "legal_notice_authority": "Section 91 BNSS",
        "kyc_data_available": True,
        "upi_linked": True,
        "known_upi_prefixes": ["MUDREX"],
        "kyc_demand_template": "MUDREX_COMPLIANCE_91BNSS",
    },
}

# ── UPI extraction patterns ───────────────────────────────────────────────────
UPI_REGEX = re.compile(
    r'\b([a-zA-Z0-9.\-_]{2,256}@(?:oksbi|okaxis|okhdfcbank|okicici|ybl|ibl|axl|upi|'
    r'paytm|freecharge|apl|rbl|indus|barodampay|boi|hsbc|juspay|'
    r'kotak|pingpay|pnb|sbi|ubi|utbi|waaxis|woksbi|wpay|nsdl|yespay|'
    r'waave|tijori|dbs|dlb|fbl|fino|hdfcbank|icici|idbi|idfc|idfcbank|'
    r'ikwik|indusind|jkb|kvb|lvb|mahb|oksbi|rblbank|sib|syndicate|tjsb|'
    r'uco|vijb|viom|yesg|yesbank|upi))\b',
    re.IGNORECASE
)

PHONE_REGEX = re.compile(r'\b(?:\+91[\s\-]?)?[6-9]\d{9}\b')
AMOUNT_REGEX = re.compile(r'(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d{1,2})?)', re.IGNORECASE)
CRYPTO_ADDR_REGEX = re.compile(r'\b(T[A-Za-z0-9]{33}|0x[a-fA-F0-9]{40})\b')


@dataclass
class CryptoLead:
    lead_type: str
    exchange: str
    confidence: float
    evidence_basis: str
    legal_action: str
    compliance_contact: str
    priority: str  # IMMEDIATE / HIGH / MEDIUM / LOW


@dataclass
class UPIBridgeReport:
    fir_number: Optional[str]
    amount_inr: Optional[float]
    extracted_upi_ids: List[str]
    extracted_phones: List[str]
    extracted_crypto_addresses: List[str]
    p2p_corridor: Optional[str]
    corridor_confidence: float
    crypto_leads: List[CryptoLead]
    recommended_next_steps: List[str]
    legal_notices_suggested: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class UPIBridge:
    """
    Bridges Indian banking fraud (UPI) to crypto investigation.
    
    Workflow:
    1. Extract UPI IDs, phone numbers, amounts from complaint text
    2. Identify likely P2P crypto exchange corridor
    3. Generate actionable crypto investigation leads
    4. Suggest specific legal notices under Indian law
    """

    def analyze(
        self,
        complaint_text: str,
        upi_ids: Optional[List[str]] = None,
        phone: Optional[str] = None,
        amount_inr: Optional[float] = None,
        fir_number: Optional[str] = None,
    ) -> dict:
        """
        Analyze a fraud complaint and generate crypto investigation leads.
        """
        # Extract entities from complaint text
        extracted_upi = list(set(UPI_REGEX.findall(complaint_text)))
        extracted_upi += [u for u in (upi_ids or []) if u not in extracted_upi]

        extracted_phones = list(set(PHONE_REGEX.findall(complaint_text)))
        if phone and phone not in extracted_phones:
            extracted_phones.append(phone)

        extracted_crypto = list(set(CRYPTO_ADDR_REGEX.findall(complaint_text)))

        extracted_amounts = AMOUNT_REGEX.findall(complaint_text)
        if not amount_inr and extracted_amounts:
            try:
                amount_inr = float(extracted_amounts[0].replace(",", ""))
            except ValueError:
                pass

        # Identify P2P corridor
        corridor, corridor_conf = self._identify_corridor(extracted_upi, complaint_text)

        # Generate leads
        leads = self._generate_leads(
            corridor=corridor,
            upi_ids=extracted_upi,
            phones=extracted_phones,
            crypto_addrs=extracted_crypto,
            amount_inr=amount_inr,
            complaint_text=complaint_text,
        )

        # Legal notices
        notices = self._suggest_legal_notices(corridor, amount_inr)

        # Next steps
        next_steps = self._next_steps(corridor, extracted_upi, extracted_crypto, amount_inr)

        report = UPIBridgeReport(
            fir_number=fir_number,
            amount_inr=amount_inr,
            extracted_upi_ids=extracted_upi,
            extracted_phones=extracted_phones,
            extracted_crypto_addresses=extracted_crypto,
            p2p_corridor=corridor,
            corridor_confidence=corridor_conf,
            crypto_leads=leads,
            recommended_next_steps=next_steps,
            legal_notices_suggested=notices,
            metadata={
                "text_length": len(complaint_text),
                "entities_found": {
                    "upi_ids": len(extracted_upi),
                    "phones": len(extracted_phones),
                    "crypto_addresses": len(extracted_crypto),
                },
                "analysis_version": "2.0",
            }
        )
        return self._serialize(report)

    def _identify_corridor(self, upi_ids: List[str], complaint_text: str) -> tuple:
        """Identify the most likely P2P crypto exchange corridor."""
        scores: Dict[str, float] = {k: 0.0 for k in P2P_EXCHANGE_PATTERNS}

        text_lower = complaint_text.lower()

        for key, meta in P2P_EXCHANGE_PATTERNS.items():
            # Check UPI prefix match
            for upi in upi_ids:
                for prefix in meta["known_upi_prefixes"]:
                    if prefix.lower() in upi.lower():
                        scores[key] += 0.6

            # Check complaint text for exchange mentions
            if meta["name"].lower() in text_lower:
                scores[key] += 0.4
            if key.replace("_", " ") in text_lower or key.replace("_p2p", "").replace("_", "") in text_lower:
                scores[key] += 0.3

        # Generic P2P indicators (no specific exchange identified)
        generic_keywords = ["p2p", "usdt", "crypto", "bitcoin", "tether", "exchange", "wallet", "transfer"]
        generic_hits = sum(1 for kw in generic_keywords if kw in text_lower)

        best = max(scores, key=scores.get)
        best_score = scores[best]

        if best_score > 0.3:
            return best, min(0.9, best_score)
        elif generic_hits >= 2:
            return "binance_p2p", 0.45  # default most common corridor
        else:
            return None, 0.2

    def _generate_leads(self, corridor, upi_ids, phones, crypto_addrs, amount_inr, complaint_text) -> List[CryptoLead]:
        leads = []

        if corridor and corridor in P2P_EXCHANGE_PATTERNS:
            meta = P2P_EXCHANGE_PATTERNS[corridor]
            priority = "IMMEDIATE" if (amount_inr or 0) > 100000 else "HIGH"
            leads.append(CryptoLead(
                lead_type="p2p_exchange_kyc_demand",
                exchange=meta["name"],
                confidence=0.78,
                evidence_basis=f"UPI IDs {upi_ids[:2]} match {meta['name']} P2P corridor pattern",
                legal_action=f"Issue {meta['legal_notice_authority']} notice to {meta['name']} compliance requesting: KYC dossier, bank linkage, IP logs, transaction history, wallet addresses",
                compliance_contact=meta["compliance_email"],
                priority=priority,
            ))

        # Direct crypto address leads
        for addr in crypto_addrs:
            chain = "Tron (USDT-TRC20)" if addr.startswith("T") else "Ethereum (USDT-ERC20)"
            leads.append(CryptoLead(
                lead_type="direct_wallet_trace",
                exchange=f"Chain: {chain}",
                confidence=0.95,
                evidence_basis=f"Crypto address {addr} extracted directly from complaint text",
                legal_action=f"Immediate blockchain trace on {addr} via CryptoSentinel — identify exchange and issue freeze notice",
                compliance_contact="N/A — run blockchain trace first",
                priority="IMMEDIATE",
            ))

        return leads

    def _suggest_legal_notices(self, corridor, amount_inr) -> List[str]:
        notices = [
            "Section 91 BNSS: Requisition for documents from payment service provider",
            "Section 91 BNSS: Requisition for KYC records from identified crypto exchange",
        ]
        if amount_inr and amount_inr >= 100000:
            notices.append("PMLA Section 12AA: Suspicious Transaction Report mandate to FIU-IND")
            notices.append("IT Act Section 69: Direction to CERT-In for network forensics assistance")
        if corridor:
            meta = P2P_EXCHANGE_PATTERNS.get(corridor, {})
            if meta:
                notices.append(
                    f"Section 91 BNSS to {meta['legal_entity']}: Demand UPI-linked KYC, "
                    f"wallet IDs, IP logs, and account freeze for addresses identified in trace"
                )
        return notices

    def _next_steps(self, corridor, upi_ids, crypto_addrs, amount_inr) -> List[str]:
        steps = []
        if crypto_addrs:
            steps.append(f"🔍 Immediately trace {len(crypto_addrs)} crypto address(es) in CryptoSentinel blockchain module")
        if corridor:
            meta = P2P_EXCHANGE_PATTERNS.get(corridor, {})
            if meta:
                steps.append(f"📧 Send Section 91 BNSS notice to {meta['name']} at {meta['compliance_email']}")
        if upi_ids:
            steps.append(f"🏦 Request UPI transaction logs from NPCI/PSP for {len(upi_ids)} UPI ID(s) identified")
        if amount_inr and amount_inr >= 100000:
            steps.append(f"📊 File STR with FIU-IND (amount ₹{amount_inr:,.0f} exceeds ₹1L threshold)")
        steps.append("📝 Log all findings to CryptoSentinel evidence trail for court-admissible record")
        steps.append("🔗 Cross-reference extracted addresses with OFAC sanctions database")
        return steps

    def _serialize(self, report: UPIBridgeReport) -> dict:
        return {
            "fir_number": report.fir_number,
            "amount_inr": report.amount_inr,
            "extracted_upi_ids": report.extracted_upi_ids,
            "extracted_phones": report.extracted_phones,
            "extracted_crypto_addresses": report.extracted_crypto_addresses,
            "p2p_corridor_analysis": {
                "likely_corridor": P2P_EXCHANGE_PATTERNS.get(report.p2p_corridor, {}).get("name", "Unknown") if report.p2p_corridor else "Not identified",
                "corridor_key": report.p2p_corridor,
                "confidence": report.corridor_confidence,
            },
            "crypto_leads": [
                {
                    "lead_type": l.lead_type,
                    "exchange": l.exchange,
                    "confidence": l.confidence,
                    "evidence_basis": l.evidence_basis,
                    "legal_action": l.legal_action,
                    "compliance_contact": l.compliance_contact,
                    "priority": l.priority,
                }
                for l in report.crypto_leads
            ],
            "legal_notices_suggested": report.legal_notices_suggested,
            "recommended_next_steps": report.recommended_next_steps,
            "metadata": report.metadata,
        }
