// src/views/LegalNoticeView.jsx
// Standardized Section 91 & Section 102 CrPC Statutory Notice Generator (PRD G5 & Section 3.4)
import React, { useState } from 'react'

export default function LegalNoticeView({ initialCaseId = 'CASE-2024-001', initialExchange = 'Binance', initialWallet = 'T_VICTIM_SIH_DEMO_999' }) {
  const [caseId, setCaseId] = useState(initialCaseId)
  const [exchange, setExchange] = useState(initialExchange)
  const [wallet, setWallet] = useState(initialWallet)
  const [copied, setCopied] = useState(false)

  const noticeDate = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })

  const noticeText = `═══════════════════════════════════════════════════════════════════════════════
   OFFICE OF THE SUPERINTENDENT OF POLICE / CYBER CRIME INVESTIGATION CELL
        CENTRAL NATIONAL CYBERCRIME REPORTING PORTAL (NCRP) / MHA I4C
═══════════════════════════════════════════════════════════════════════════════

NOTICE UNDER SECTION 91 READ WITH SECTION 102 OF THE CODE OF CRIMINAL PROCEDURE, 1973
(CORRESPONDING TO SECTION 94 & 107 OF BHARATIYA NAGARIK SURAKSHA SANHITA, 2023)
& SECTION 66B / 66C / 66D OF THE INFORMATION TECHNOLOGY (AMENDMENT) ACT, 2008

Notice Reference No. : NCRP/CRPC-91/${caseId}
Issue Date & Time    : ${noticeDate} (Issued under urgent evidentiary powers)
Investigating Unit   : Cyber Crime Police Station (Financial Crimes & Crypto Forensics Cell)

TO:
The Nodal / Designated Compliance Officer,
${exchange} (Virtual Digital Asset Service Provider / FIU-IND Reporting Entity)

SUBJECT: URGENT STATUTORY REQUISITION FOR SUBSCRIBER KYC, TRANSACTION AUDIT TRAILS,
         IP LOGS, AND IMMEDIATE FREEZING OF SUSPECT WALLET/ACCOUNTS

Sir / Madam,

WHEREAS, an investigation has been initiated into an alleged cyber fraud / financial syndicate under Case/FIR Ref: ${caseId}, involving wrongful diversion and laundering of cryptocurrency (USDT-TRC20 on Tron network).

AND WHEREAS, through automated multi-hop blockchain forensic tracing and heuristic clustering, the stolen funds originating from victim seed address [${wallet}] have been traced through a multi-hop peel chain and conclusively identified as having terminated into deposit infrastructure owned and/or operated by your platform (${exchange}).

EVIDENCE OF ON-CHAIN FUND FLOW & ATTRIBUTION:
───────────────────────────────────────────────────────────────────────────────
Seed Suspect Address : ${wallet}
Cluster Identification: CLU_USDT_TRC20_MULE_RING_01 (4 addresses merged via deposit-reuse)
Hop Depth Traversed  : 3 Hops along primary peel-chain fund flow
Terminal Deposit Addr: TBinanceUSDTDeposit666666666666
Attribution Evidence : Matched against FIU-IND / Tronscan VASP Deposit Hot-Wallet Directory
Confidence Score     : 91.4% (Conclusive Exchange Terminal Attribution)
───────────────────────────────────────────────────────────────────────────────

YOU ARE HEREBY DIRECTED PURSUANT TO SECTION 91 & SECTION 102 CrPC / BNSS TO FURNISH THE FOLLOWING RECORDS WITHIN TWENTY-FOUR (24) HOURS OF RECEIPT OF THIS NOTICE:

1. Complete KYC Dossier: Full Legal Name, Date of Birth, Permanent Address, Certified Identity Proof (PAN / Aadhaar / Passport), Registered Mobile Number, and Email ID.
2. Fiat Banking Links: Bank Account Numbers, Account Holder Name, IFSC Code, and associated UPI VPA IDs linked to this account.
3. Detailed Transaction History: Full ledger of all crypto-to-crypto and crypto-to-INR/fiat conversions, P2P trade counterparty records, and off-chain transfer logs.
4. Access Logs & Device Telemetry: Complete IP address login history with port numbers, MAC addresses, IMEI/Device Fingerprints, and timestamped session records.
5. IMMEDIATE FREEZING ORDER: In exercise of powers under Section 102 CrPC, you are directed to immediately FREEZE all current balances (crypto and fiat) associated with the identified user account(s) and prevent any outward remittance.

TAKE NOTICE that intentional omission, non-compliance, or destruction of requested electronic evidence shall attract penal prosecution under Sections 175, 176, and 201 of the Indian Penal Code, 1860 / Bharatiya Nyaya Sanhita, 2023, and provisions of PMLA 2002.

───────────────────────────────────────────────────────────────────────────────
LEGAL STATUS: [ DRAFT - REQUIRES INVESTIGATOR REVIEW & DIGITAL SIGNATURE ]
Generated via WalletTrace Automated Forensics Engine (SIH26183 Compliance)

INVESTIGATING OFFICER (IO):
Name / Badge No.    : __________________________________________
Designation / Rank  : Inspector of Police / Cyber Forensics Investigator
Police Station      : Cyber Crime Police Station, Central Crime Branch
Official Seal       : [AFFIX POLICE SEAL HERE]`

  const handleCopy = () => {
    navigator.clipboard.writeText(noticeText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="p-space-base max-w-5xl mx-auto flex flex-col gap-space-base">
      <div className="flex items-center justify-between border-b border-border-subtle pb-space-xs">
        <div>
          <h2 className="font-headline-md text-headline-md font-bold text-on-surface flex items-center gap-2">
            <span>📜</span> Section 91 & 102 CrPC Statutory Requisition Generator
          </h2>
          <p className="font-body-base text-on-surface-variant text-sm mt-1">
            Automated legal requisition package demanding KYC disclosure and account freezing for identified exchanges.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="bg-surface-container-high hover:bg-surface-container-highest text-on-surface text-xs font-bold px-3 py-2 rounded flex items-center gap-1 border border-border-subtle"
          >
            {copied ? '✓ Copied!' : '📋 Copy Text'}
          </button>
          <button
            onClick={handlePrint}
            className="bg-primary hover:bg-primary-hover text-on-primary text-xs font-bold px-4 py-2 rounded flex items-center gap-1 shadow"
          >
            🖨 Print / Export PDF
          </button>
        </div>
      </div>

      {/* Configuration Controls */}
      <div className="grid grid-cols-3 gap-space-sm bg-surface-container-low border border-border-subtle rounded-lg p-3">
        <div>
          <label className="text-[10px] uppercase font-bold text-outline block mb-1">Case ID Reference</label>
          <input
            type="text"
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
            className="w-full bg-surface-container-lowest border border-border-subtle rounded px-2 py-1 text-xs text-on-surface"
          />
        </div>
        <div>
          <label className="text-[10px] uppercase font-bold text-outline block mb-1">Target VDA Exchange</label>
          <input
            type="text"
            value={exchange}
            onChange={(e) => setExchange(e.target.value)}
            className="w-full bg-surface-container-lowest border border-border-subtle rounded px-2 py-1 text-xs text-on-surface"
          />
        </div>
        <div>
          <label className="text-[10px] uppercase font-bold text-outline block mb-1">Traced Suspect Wallet</label>
          <input
            type="text"
            value={wallet}
            onChange={(e) => setWallet(e.target.value)}
            className="w-full bg-surface-container-lowest border border-border-subtle rounded px-2 py-1 text-xs text-on-surface font-mono"
          />
        </div>
      </div>

      {/* Legal Document Display */}
      <div className="relative bg-surface-container-lowest border-2 border-border-subtle rounded-lg p-6 shadow-2xl font-mono text-xs leading-relaxed text-on-surface overflow-x-auto whitespace-pre">
        {/* Watermark Banner */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rotate-[-25deg] pointer-events-none opacity-10 text-3xl font-extrabold text-error border-4 border-error px-8 py-4 uppercase select-none">
          DRAFT - REQUIRES INVESTIGATOR REVIEW
        </div>
        {noticeText}
      </div>
    </div>
  )
}
