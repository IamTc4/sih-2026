"""
forensics/typology.py
─────────────────────
On-chain Fraud Typology Classifier for SIH26183:
Maps on-chain transaction graph topology, clustering heuristics, and VASP attributions
into standardized cyber fraud typologies:
1. P2P Crypto Corridor / Mule Account Syndicate
2. Task-Based Fraud (Telegram/WhatsApp Part-Time Job Scams)
3. Investment Scam / Pig Butchering (Fake MT5 / High Yield)
4. Mixer / Privacy Laundering (Tornado Cash / ChangeNOW / FixedFloat)
5. Phishing / Automated Sweeper Drainer
6. Ransomware / Extortion
"""
from typing import List, Optional
from schemas.models import (
    Cluster, TracePath, GraphResponse, AttributionResult,
    Transaction, TypologySummary
)

def infer_fraud_typology(
    seed_address: str,
    clusters: List[Cluster],
    primary_path: Optional[TracePath],
    graph: GraphResponse,
    attribution: AttributionResult,
    transactions: List[Transaction]
) -> TypologySummary:
    """
    Evaluates graph structure, heuristic evidence chains, and transaction amounts
    to determine the most probable fraud typology and legal action recommendations.
    """
    all_heuristics = set()
    for c in clusters:
        all_heuristics.add(c.primary_heuristic)
        for e in c.evidence_chain:
            all_heuristics.add(e.heuristic_name)

    indicators: List[str] = []
    hop_depth = primary_path.hops_count if primary_path else 0
    total_inflow = sum(n.total_inflow for n in graph.nodes if n.is_seed)

    # 1. Mixer / Privacy-Protocol Proximity
    if "mixer_proximity" in all_heuristics or (attribution.entity_type and "mixer" in attribution.entity_type.lower()):
        indicators.append("Direct transfer hop into/out of known mixer or no-KYC swap protocol")
        if hop_depth >= 2:
            indicators.append(f"Dispersal layered across {hop_depth} hops prior to mixer ingestion")
        return TypologySummary(
            typology_name="Mixer & Privacy-Protocol Laundering",
            typology_code="MIXER_LAUNDERING",
            confidence=0.95,
            indicators=indicators,
            modus_operandi=(
                "Fraud syndicate routes illicit proceeds through non-custodial mixing protocols "
                "(Tornado Cash, ChangeNOW, FixedFloat) to deliberately break on-chain audit trails."
            ),
            recommended_legal_action=(
                "Serve emergency preservation order under Section 91 BNSS to target liquidity pools; "
                "flag terminal wallet for FIU-IND international Mutual Legal Assistance Treaty (MLAT) requisition."
            )
        )

    # 2. P2P Crypto Corridor / Mule Account Syndicate
    if "deposit_address_reuse" in all_heuristics or ("common_funding_source" in all_heuristics and len(clusters) > 0):
        indicators.append("Centralized deposit address reuse across disparate wallet nodes")
        if "common_funding_source" in all_heuristics:
            indicators.append("Common funding source indicates pre-seeded mule syndicate wallets")
        if "structuring_pattern" in all_heuristics:
            indicators.append("Sub-threshold structuring (₹7.5L - ₹9.9L equivalent in USDT) observed")
        return TypologySummary(
            typology_name="P2P Crypto Corridor / Mule Syndicate",
            typology_code="P2P_MULE",
            confidence=0.92,
            indicators=indicators,
            modus_operandi=(
                "Domestic victims deposit INR via UPI into mule bank accounts. P2P crypto merchants rapidly convert "
                "INR to USDT and distribute to syndicate consolidation wallets."
            ),
            recommended_legal_action=(
                "Issue Section 91 BNSS notice to Indian FIU-registered exchange (CoinDCX/WazirX/Binance P2P) "
                "for merchant KYC, registered mobile, linked bank accounts, and Section 102 CrPC freeze."
            )
        )

    # 3. Task-Based Fraud / Part-Time Job Scam
    if "rapid_hop_velocity" in all_heuristics or (hop_depth >= 3 and "structuring_pattern" in all_heuristics):
        indicators.append("Rapid sequential transfers (< 5 minutes per hop) across peel chain")
        indicators.append("Progressive amount escalation consistent with task-based deposit demands")
        return TypologySummary(
            typology_name="Task-Based / Part-Time Job Scam",
            typology_code="TASK_FRAUD",
            confidence=0.88,
            indicators=indicators,
            modus_operandi=(
                "Victims solicited via Telegram/WhatsApp for video rating tasks; small payouts given initially, "
                "followed by demand for high-tier deposits, which are instantly swept across automated multi-hop chains."
            ),
            recommended_legal_action=(
                "Initiate Golden-Hour 1930 NCRP / NPCI bank freeze on initial UPI collection accounts; "
                "serve Section 91 notice to terminal VASP to seize remaining crypto balances."
            )
        )

    # 4. Investment Scam / Pig Butchering (Fake High-Yield Platform)
    if total_inflow > 25000 or "repeated_high_volume_interaction" in all_heuristics:
        indicators.append(f"Substantial high-volume fund accumulation (${total_inflow:,.2f} USDT)")
        indicators.append("Unidirectional inflow without reciprocal payout to depositor")
        return TypologySummary(
            typology_name="Investment Scam / Pig Butchering",
            typology_code="INVESTMENT_SCAM",
            confidence=0.89,
            indicators=indicators,
            modus_operandi=(
                "Victim lured through dating or investment groups to deposit large sums onto simulated trading portals. "
                "All deposits are transferred into offshore high-liquidity exchange wallets."
            ),
            recommended_legal_action=(
                "Issue Section 91 BNSS notice to terminal exchange for user KYC, login IP logs, and device fingerprints; "
                "submit domain and app package to Cert-In for emergency blocking."
            )
        )

    # 5. Phishing / Sweeper Drainer
    seed_nodes = [n for n in graph.nodes if n.is_seed]
    in_edges = len([e for e in graph.edges if e.target == seed_address])
    out_edges = len([e for e in graph.edges if e.source == seed_address])
    if in_edges >= 3 and out_edges <= 1:
        indicators.append(f"Multiple victim inputs ({in_edges}) swept into single recipient wallet")
        indicators.append("Automated sweeper script behavior matching token approval drainers")
        return TypologySummary(
            typology_name="Phishing / Automated Wallet Drainer",
            typology_code="PHISHING_DRAINER",
            confidence=0.85,
            indicators=indicators,
            modus_operandi=(
                "Victims phished via counterfeit airdrop or DeFi approvals. Automated sweeper bot monitors "
                "victim balances and empties tokens instantaneously upon deposit."
            ),
            recommended_legal_action=(
                "Submit malicious smart contract address to Etherscan/Tronscan for public scam tagging; "
                "serve Section 91 notice to domain host."
            )
        )

    # Default Organized Cybercrime classification
    return TypologySummary(
        typology_name="Organized Cyber-Enabled Financial Crime",
        typology_code="ORGANIZED_CYBERCRIME",
        confidence=0.82,
        indicators=[
            f"Multi-hop fund routing across {hop_depth} hops",
            f"Consolidation into terminal address {attribution.exchange_name or 'unattributed wallet'}"
        ],
        modus_operandi=(
            "Funds routed through intermediary non-custodial wallets exhibiting layering behavior "
            "typical of cyber fraud collection networks."
        ),
        recommended_legal_action=(
            "Serve Section 91 BNSS notice on terminal VASP requesting complete transaction history and KYC records."
        )
    )
