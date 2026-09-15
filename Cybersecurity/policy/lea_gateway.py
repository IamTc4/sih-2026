"""
Cybersecurity/policy/lea_gateway.py
───────────────────────────────────
Official Law Enforcement Agency (LEA) System Integration Gateway (SIH26183 Requirement 5.6).

Implements deep integration with Indian Police Digital Infrastructure:
1. CCTNS (Crime and Criminal Tracking Network & Systems): Form II / Case Diary export in official XML & JSON.
2. ICJS (Inter-operable Criminal Justice System): Tamper-evident digital evidence packet for courts.
3. National Gov SSO (Parichay / MeriPehchan): Police intranet OAuth2/OIDC authentication simulator.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import hashlib
import uuid
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

# ── CCTNS Form-II Case Diary Models ───────────────────────────────────────────
class CCTNSCaseDiaryExportRequest(BaseModel):
    fir_number: str = Field(..., description="CCTNS FIR Number, e.g. FIR-0142/2026/CYBER")
    police_station: str = Field("Cyber Crime Police Station, Central Crime Branch", description="Police Station Name")
    district: str = Field("Mumbai Cyber", description="Police District")
    state: str = Field("Maharashtra", description="State")
    investigating_officer: str = Field("Insp. R. K. Sharma", description="Name of IO")
    officer_belt_no: str = Field("CC-8821", description="Police ID / Belt Number")
    sections_of_law: List[str] = Field(
        default=["Section 66D IT Act 2008", "Section 318(4) BNS 2023", "Section 91 BNSS 2023"],
        description="Statutory sections"
    )
    suspect_wallets: List[str] = Field(default_factory=list)
    suspect_upi_vpas: List[str] = Field(default_factory=list)
    terminal_vasp: Optional[str] = "Binance P2P / WazirX"
    seizure_amount_inr: float = 250000.0
    forensic_findings: str

class CCTNSExportResponse(BaseModel):
    cctns_dispatch_id: str
    export_format: str
    xml_payload: str
    json_payload: Dict[str, Any]
    icjs_sha256_seal: str
    timestamp: str


# ── Police Intranet SSO Authentication Models ─────────────────────────────────
class GovSSORequest(BaseModel):
    gov_email: str = Field(..., description="Officer Gov Email (@gov.in / @nic.in / @pol.gov.in)")
    badge_number: str = Field(..., description="Police ID / Service Number")
    sso_provider: str = Field("Parichay / MeriPehchan (National Gov SSO)", description="SSO Provider")
    auth_token: Optional[str] = None

class GovSSOResponse(BaseModel):
    authenticated: bool
    officer_name: str
    designation: str
    department: str
    jurisdiction: str
    security_clearance: str
    bearer_token: str
    sso_session_id: str
    expires_in_seconds: int


class LEAGateway:
    """
    Law Enforcement Systems Integration Gateway providing CCTNS, ICJS, and Gov SSO interfaces.
    """

    def __init__(self):
        logger.info("LEAGateway active. CCTNS XML & ICJS Evidence Engine initialized.")

    def export_cctns_diary(self, req: CCTNSCaseDiaryExportRequest) -> CCTNSExportResponse:
        """
        Generates official CCTNS Case Diary Part-II (Technical Evidence Report)
        in standardized XML and JSON schema.
        """
        dispatch_id = f"CCTNS-MH-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        iso_now = datetime.now(timezone.utc).isoformat()

        # Build Standardized XML Document according to NCRB CCTNS Data Exchange Standards
        root = ET.Element("CCTNS_CaseDiary_Part_II", attrib={"xmlns": "http://ncrb.gov.in/cctns/v2.1", "version": "2.1"})
        
        meta = ET.SubElement(root, "Metadata")
        ET.SubElement(meta, "DispatchID").text = dispatch_id
        ET.SubElement(meta, "Timestamp").text = iso_now
        ET.SubElement(meta, "State").text = req.state
        ET.SubElement(meta, "District").text = req.district
        ET.SubElement(meta, "PoliceStation").text = req.police_station
        ET.SubElement(meta, "FIRNumber").text = req.fir_number

        officer = ET.SubElement(root, "InvestigatingOfficer")
        ET.SubElement(officer, "Name").text = req.investigating_officer
        ET.SubElement(officer, "BeltNo").text = req.officer_belt_no

        laws = ET.SubElement(root, "StatutorySections")
        for s in req.sections_of_law:
            ET.SubElement(laws, "Section").text = s

        evidence = ET.SubElement(root, "DigitalEvidenceSeizure")
        wallets = ET.SubElement(evidence, "SuspectCryptocurrencyWallets")
        for w in req.suspect_wallets:
            ET.SubElement(wallets, "WalletAddress").text = w

        vpas = ET.SubElement(evidence, "SuspectUPIVPAs")
        for v in req.suspect_upi_vpas:
            ET.SubElement(vpas, "VPA").text = v

        ET.SubElement(evidence, "TerminalVASP").text = req.terminal_vasp or "UNATTRIBUTED"
        ET.SubElement(evidence, "SeizureAmountINR").text = str(req.seizure_amount_inr)
        ET.SubElement(evidence, "ForensicFindingsSummary").text = req.forensic_findings

        xml_string = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

        # Cryptographic ICJS Tamper Seal
        seal_hash = hashlib.sha256(xml_string.encode("utf-8")).hexdigest()

        json_data = {
            "dispatch_id": dispatch_id,
            "fir_number": req.fir_number,
            "police_station": req.police_station,
            "investigating_officer": f"{req.investigating_officer} ({req.officer_belt_no})",
            "statutory_sections": req.sections_of_law,
            "suspect_wallets": req.suspect_wallets,
            "suspect_upi_vpas": req.suspect_upi_vpas,
            "terminal_vasp": req.terminal_vasp,
            "seizure_amount_inr": req.seizure_amount_inr,
            "forensic_summary": req.forensic_findings,
            "icjs_tamper_seal": seal_hash,
            "status": "APPROVED_FOR_COURT_FILING"
        }

        return CCTNSExportResponse(
            cctns_dispatch_id=dispatch_id,
            export_format="CCTNS_XML_V2.1_AND_JSON",
            xml_payload=xml_string,
            json_payload=json_data,
            icjs_sha256_seal=seal_hash,
            timestamp=iso_now
        )

    def authenticate_gov_sso(self, req: GovSSORequest) -> GovSSOResponse:
        """
        Authenticates an officer via National Gov SSO (Parichay / MeriPehchan / NIC).
        """
        email = req.gov_email.strip().lower()
        badge = req.badge_number.strip().upper()
        
        # Determine designation from email/badge
        is_sp = "sp" in email or "ips" in email
        designation = "Superintendent of Police (IPS)" if is_sp else "Inspector of Police / Cyber Forensics Investigator"
        clearance = "TOP_SECRET_PII_FULL" if is_sp else "SECRET_INVESTIGATOR_READ_WRITE"
        role = "admin" if is_sp else "investigator"

        session_id = f"PARICHAY-SSO-{uuid.uuid4().hex[:10].upper()}"
        bearer_token = f"{role}:{badge}"

        return GovSSOResponse(
            authenticated=True,
            officer_name="Officer " + badge,
            designation=designation,
            department="Cyber Crime Police Station / MHA I4C Task Force",
            jurisdiction="All-India Cyber Fraud Jurisdiction (MHA Authorized)",
            security_clearance=clearance,
            bearer_token=bearer_token,
            sso_session_id=session_id,
            expires_in_seconds=28800  # 8 hours
        )


# Global singleton
_lea_gateway_instance: Optional[LEAGateway] = None

def get_lea_gateway() -> LEAGateway:
    global _lea_gateway_instance
    if _lea_gateway_instance is None:
        _lea_gateway_instance = LEAGateway()
    return _lea_gateway_instance
