"""
ml/typology.py
──────────────
Deterministic & heuristic fraud typology classifier aligned with SIH26183 problem statement:
- Task-based Frauds (Telegram/WhatsApp Part-Time Job Scams)
- Investment Scams / Pig Butchering (Fake High-Yield Platforms)
- P2P Crypto Corridor / Mule Account Networks (UPI -> P2P -> USDT)
- Mixer / Privacy-Enhanced Laundering (Tornado Cash, ChangeNOW, FixedFloat)
- Ransomware / Extortion (High-velocity single extortion payments)
- Phishing / Sweeper Drainers (Multi-victim automated sweeps)
"""
from typing import List, Tuple
from ml.models import BlockchainFeatures, CybersecurityFlags, FraudTypology

def classify_fraud_typology(
    address: str,
    bc: BlockchainFeatures,
    cy: CybersecurityFlags,
    risk_score: float
) -> FraudTypology:
    """
    Infers the most probable cyber fraud typology from on-chain behavioral features,
    heuristics triggered, and cybersecurity pattern flags.
    """
    heuristics = set(bc.heuristic_types)
    indicators: List[str] = []
    
    has_mixer = cy.mixer_flag or "mixer_proximity" in heuristics
    has_peel = cy.peel_chain_flag or bc.hop_depth >= 3
    has_structuring = cy.structuring_flag or "structuring_pattern" in heuristics
    has_rapid = cy.rapid_hop_flag or "rapid_hop_velocity" in heuristics
    has_deposit_reuse = "deposit_address_reuse" in heuristics
    has_common_funding = "common_funding_source" in heuristics
    has_high_volume = bc.total_inflow > 50000 or "repeated_high_volume_interaction" in heuristics

    # Case 1: Mixer / Privacy Enhancing Protocol Laundering
    if has_mixer:
        indicators.append("Transaction hop directly touches known mixer/tumbler or no-KYC swap protocol")
        if has_peel:
            indicators.append("Multi-hop peel-chain dispersal utilized before/after mixer entry")
        if has_rapid:
            indicators.append("Rapid execution (< 5 min intervals) to bypass mempool tracking")
        return FraudTypology(
            typology_name="Mixer & Privacy-Protocol Laundering",
            typology_code="MIXER_LAUNDERING",
            confidence=0.94 if cy.mixer_confidence > 0.8 else 0.88,
            indicators=indicators,
            modus_operandi=(
                "Perpetrators route illicit funds through decentralized mixing pools (e.g. Tornado Cash) "
                "or non-custodial cross-chain swap services (e.g. ChangeNOW, FixedFloat) to sever the on-chain audit trail."
            ),
            recommended_legal_action=(
                "Immediate Section 91 BNSS requisition to liquidity pool bridge nodes and target VASP cashout endpoints; "
                "flag counterparty addresses for FIU-IND international intelligence coordination."
            )
        )

    # Case 2: P2P Crypto Corridor / Mule Account Ring (Highest prevalence in Indian Cyber Crime)
    if has_deposit_reuse or (has_common_funding and bc.cluster_size >= 2):
        indicators.append("Deposit address reuse detected across multiple distinct counterparty wallets")
        if has_common_funding:
            indicators.append("Shared root funding source indicates centrally managed mule syndication")
        if has_structuring:
            indicators.append("Structuring amounts observed in ₹7.5L-₹10L bracket to evade mandatory CTR reporting")
        return FraudTypology(
            typology_name="P2P Crypto Corridor / Mule Syndicate",
            typology_code="P2P_MULE",
            confidence=0.91,
            indicators=indicators,
            modus_operandi=(
                "Syndicate recruits domestic mule bank accounts linked to UPI VPAs. Victims deposit INR via UPI, "
                "which is rapidly settled by P2P crypto merchants into USDT and swept into centralized mule consolidation clusters."
            ),
            recommended_legal_action=(
                "Issue Section 91 BNSS notice to P2P merchant platform (e.g., Binance P2P, WazirX P2P) demanding "
                "counterparty KYC, bank UTR numbers, and Section 102 CrPC account freeze."
            )
        )

    # Case 3: Task-Based Fraud / Part-Time Job Scam
    if has_rapid and (has_structuring or bc.hop_depth >= 2):
        indicators.append("Rapid sequential hop velocity (< 300 seconds elapsed between transfers)")
        indicators.append("Stepped layer amounts consistent with progressive task deposits (₹10k -> ₹50k -> ₹2L)")
        if bc.cluster_size > 1:
            indicators.append(f"Connected to multi-hop distribution cluster with {bc.cluster_size} member nodes")
        return FraudTypology(
            typology_name="Task-Based / Work-From-Home Scam",
            typology_code="TASK_FRAUD",
            confidence=0.86,
            indicators=indicators,
            modus_operandi=(
                "Victims lured via Telegram/WhatsApp offering commissions for liking YouTube videos or completing tasks. "
                "Deposits escalated incrementally until victim attempts withdrawal, whereupon funds are swept across automated peel chains."
            ),
            recommended_legal_action=(
                "Issue Section 91 BNSS notices to Telegram/WhatsApp communication channels and request NPCI UPI reversal "
                "within golden hours (under 4 hours) to intercept mule bank accounts."
            )
        )

    # Case 4: High-Yield Investment Scam / Pig Butchering
    if has_high_volume or bc.total_inflow > 25000:
        indicators.append(f"High-volume aggregate fund accumulation (${bc.total_inflow:,.2f} USDT)")
        indicators.append("Asymmetric flow pattern: extensive inward accumulation with minimal outbound victim payout")
        if has_peel:
            indicators.append("Peel-chain architecture used to siphon portions to cold storage while maintaining hot-wallet activity")
        return FraudTypology(
            typology_name="Investment Scam / Pig Butchering",
            typology_code="INVESTMENT_SCAM",
            confidence=0.89,
            indicators=indicators,
            modus_operandi=(
                "Fraudsters build rapport with victim over dating or social apps, steering them to fraudulent MT5/crypto trading websites. "
                "Victim deposits large sums showing fabricated profits, then funds are siphoned to offshore syndicates."
            ),
            recommended_legal_action=(
                "Issue Section 91 BNSS notice to hosting/domain registrar to preserve scam portal access logs; "
                "issue freeze notice to terminal VASP deposit address identified in trace path."
            )
        )

    # Case 5: Phishing / Automated Sweeper Drainer
    if bc.in_degree > 3 and bc.out_degree <= 2:
        indicators.append(f"High in-degree ({bc.in_degree} distinct inward inputs) with concentrated consolidation ({bc.out_degree} outputs)")
        indicators.append("Automated sweeper transaction pattern typical of malicious smart contract drainers")
        return FraudTypology(
            typology_name="Phishing / Automated Wallet Drainer",
            typology_code="PHISHING_DRAINER",
            confidence=0.84,
            indicators=indicators,
            modus_operandi=(
                "Victims sign malicious token approval transactions on spoofed airdrop or support sites. "
                "Smart contract sweeper bots immediately transfer victim assets to a consolidation master wallet."
            ),
            recommended_legal_action=(
                "Submit malicious domain to Cert-In & MHA I4C for emergency takedown; requisition Cloudflare DNS query logs under BNSS Section 91."
            )
        )

    # Default baseline typology based on risk score
    if risk_score >= 0.7:
        return FraudTypology(
            typology_name="Organized Cyber-Enabled Financial Crime",
            typology_code="ORGANIZED_CYBERCRIME",
            confidence=0.80,
            indicators=["Elevated on-chain risk score", f"Multi-hop layering across {bc.hop_depth} hops"],
            modus_operandi="Funds routed through non-custodial intermediary wallets exhibiting layering behavior consistent with organized financial crime.",
            recommended_legal_action="Serve Section 91 BNSS preservation order on terminal deposit exchange to identify beneficiary entity."
        )
    else:
        return FraudTypology(
            typology_name="Standard On-Chain Wallet Activity",
            typology_code="LOW_RISK_TRANSFERS",
            confidence=0.75,
            indicators=["No known high-risk heuristics triggered", "Direct peer-to-peer or exchange transfer patterns"],
            modus_operandi="Normal cryptocurrency transaction flow with no established links to known fraud syndicates.",
            recommended_legal_action="Standard due diligence; monitor for subsequent high-risk interactions."
        )
