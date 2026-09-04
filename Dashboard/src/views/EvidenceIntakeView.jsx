// src/views/EvidenceIntakeView.jsx
// Stage 1: Field Evidence Intake & NCRP Complaint Ingestion (PRD Section 5.1)
import React, { useState } from 'react'

export default function EvidenceIntakeView({ onLaunchInvestigation }) {
  const [complaintNo, setComplaintNo] = useState('NCRP-2024-MH-89210')
  const [victimName, setVictimName] = useState('Rajesh Kumar Sharma')
  const [fraudType, setFraudType] = useState('Crypto Investment & Telegram Task Scam')
  const [stolenAmount, setStolenAmount] = useState('45,000 USDT (₹39,15,000)')
  const [suspectWallet, setSuspectWallet] = useState('T_VICTIM_SIH_DEMO_999')
  const [ocrStatus, setOcrStatus] = useState(null)
  const [previewImg, setPreviewImg] = useState(null)

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return

    setPreviewImg(URL.createObjectURL(file))
    setOcrStatus('Scanning image for crypto wallet addresses & QR codes...')

    setTimeout(() => {
      // Simulate client-side OCR extraction
      const detected = 'T_VICTIM_SIH_DEMO_999'
      setSuspectWallet(detected)
      setOcrStatus(`✓ OCR / QR Extraction Successful: Detected Tron TRC20 Wallet: ${detected}`)
    }, 1200)
  }

  const handleDispatch = () => {
    if (onLaunchInvestigation) {
      onLaunchInvestigation(suspectWallet)
    } else {
      alert(`Case ${complaintNo} queued! Switched suspect wallet to ${suspectWallet}`)
    }
  }

  return (
    <div className="p-space-base max-w-5xl mx-auto flex flex-col gap-space-base">
      <div className="border-b border-border-subtle pb-space-xs">
        <div className="flex items-center gap-space-xs">
          <span className="text-2xl">📸</span>
          <h2 className="font-headline-md text-headline-md font-bold text-on-surface">Field Evidence Intake & NCRP Case Ingestion</h2>
        </div>
        <p className="font-body-base text-on-surface-variant mt-1">
          Stage 1 Ingestion: Intake victim complaints from National Cybercrime Reporting Portal (1930 / NCRP) or upload field-captured wallet screenshots and QR codes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-space-base">
        {/* NCRP Complaint Form */}
        <div className="bg-surface-container-low border border-border-subtle rounded-lg p-space-base flex flex-col gap-space-sm">
          <div className="font-title-sm text-title-sm font-bold text-primary flex items-center gap-space-2xs">
            <span>📋</span> NCRP Case Metadata (Replicates 1930 Intake)
          </div>

          <div>
            <label className="font-label-caps text-label-caps text-outline block mb-1">NCRP Acknowledgment No.</label>
            <input
              type="text"
              value={complaintNo}
              onChange={(e) => setComplaintNo(e.target.value)}
              className="w-full bg-surface-container-lowest border border-border-subtle rounded px-3 py-2 text-sm text-on-surface"
            />
          </div>

          <div>
            <label className="font-label-caps text-label-caps text-outline block mb-1">Victim Full Name</label>
            <input
              type="text"
              value={victimName}
              onChange={(e) => setVictimName(e.target.value)}
              className="w-full bg-surface-container-lowest border border-border-subtle rounded px-3 py-2 text-sm text-on-surface"
            />
          </div>

          <div className="grid grid-cols-2 gap-space-sm">
            <div>
              <label className="font-label-caps text-label-caps text-outline block mb-1">Fraud Classification</label>
              <input
                type="text"
                value={fraudType}
                onChange={(e) => setFraudType(e.target.value)}
                className="w-full bg-surface-container-lowest border border-border-subtle rounded px-3 py-2 text-sm text-on-surface"
              />
            </div>
            <div>
              <label className="font-label-caps text-label-caps text-outline block mb-1">Stolen Amount</label>
              <input
                type="text"
                value={stolenAmount}
                onChange={(e) => setStolenAmount(e.target.value)}
                className="w-full bg-surface-container-lowest border border-border-subtle rounded px-3 py-2 text-sm text-on-surface"
              />
            </div>
          </div>

          <div>
            <label className="font-label-caps text-label-caps text-outline block mb-1">Primary Suspect Wallet Address (Ingested)</label>
            <input
              type="text"
              value={suspectWallet}
              onChange={(e) => setSuspectWallet(e.target.value)}
              className="w-full bg-surface-container-lowest border border-primary/50 text-primary font-mono text-sm rounded px-3 py-2"
            />
          </div>
        </div>

        {/* Field Evidence / OCR Upload */}
        <div className="bg-surface-container-low border border-border-subtle rounded-lg p-space-base flex flex-col gap-space-sm">
          <div className="font-title-sm text-title-sm font-bold text-secondary flex items-center gap-space-2xs">
            <span>📷</span> Field Evidence Capture (OCR / QR Scanner)
          </div>

          <p className="text-xs text-on-surface-variant">
            Upload WhatsApp chat screenshots, mobile wallet screens, or physical QR slips seized during field raids. The optical parser automatically extracts Tron TRC20 and EVM wallet hashes.
          </p>

          <div className="border-2 border-dashed border-border-subtle hover:border-primary/50 transition-colors rounded-lg p-6 flex flex-col items-center justify-center text-center cursor-pointer relative bg-surface-container-lowest">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
            {previewImg ? (
              <img src={previewImg} alt="Field Evidence" className="max-h-40 rounded object-contain mb-2" />
            ) : (
              <>
                <div className="text-3xl mb-2">📁</div>
                <div className="text-sm font-bold text-on-surface">Click or Drag & Drop evidence screenshot</div>
                <div className="text-xs text-outline mt-1">Supports PNG, JPG, WEBP, PDF slips</div>
              </>
            )}
          </div>

          {ocrStatus && (
            <div className={`text-xs p-2 rounded ${ocrStatus.includes('✓') ? 'bg-secondary/10 text-secondary border border-secondary/30' : 'bg-primary/10 text-primary animate-pulse'}`}>
              {ocrStatus}
            </div>
          )}

          <div className="flex items-center gap-2 mt-auto">
            <button
              onClick={() => {
                setSuspectWallet('T_VICTIM_SIH_DEMO_999')
                setOcrStatus('✓ Loaded SIH Demo TRC20 Mule Syndicate Address')
              }}
              className="text-xs text-outline hover:text-primary underline"
            >
              Load Demo Mule Address
            </button>
            <span className="text-outline text-xs">|</span>
            <button
              onClick={() => {
                setSuspectWallet('T_LAZARUS_MIXER_01')
                setOcrStatus('✓ Loaded High-Risk OFAC Blacklisted Mixer Address')
              }}
              className="text-xs text-outline hover:text-error underline"
            >
              Load Blacklisted Mixer Address
            </button>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="bg-surface-container-low border border-border-subtle rounded-lg p-space-base flex items-center justify-between">
        <div>
          <div className="text-sm font-bold text-on-surface">Ready for On-Chain Multi-Hop Analysis</div>
          <div className="text-xs text-on-surface-variant">
            Dispatches ingested case to Blockchain Graph Builder, ML Risk Engine, and Agentic Orchestrator.
          </div>
        </div>
        <button
          onClick={handleDispatch}
          className="bg-primary hover:bg-primary-hover text-on-primary font-bold px-6 py-2.5 rounded shadow-lg transition-all flex items-center gap-2"
        >
          <span>🚀 Launch Investigation</span>
        </button>
      </div>
    </div>
  )
}
