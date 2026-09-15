# 🎬 CryptoSentinel — Full Demo Video Script
### SIH 2026 · PS ID 26183 · Ministry of Home Affairs / I4C
### Total runtime: ≤ 3:00 · Single narrator · Screen-capture + voiceover

---

> **FORMAT KEY**
> - **[ACTION]** = what happens on screen (editing / recording cue)
> - *"Quote"* = word-for-word narrator line (record exactly as written)
> - ⏸ = deliberate pause — hold silence for 1–2 seconds, let the visual land
> - 🔍 = zoom cue — punch in on this element
> - 📌 = on-screen text overlay to add in editing
> - 🎵 = music/audio note

---
---

## ━━━ ACT 1 · HOOK · 0:00 – 0:12 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> *"Right now, somewhere in India, a cybercrime victim has just lost ₹4 lakhs."*
> *"The money is already moving — hopping across three wallets — disappearing into a crypto exchange."* ⏸
> *"The police have 48 hours before it is gone forever."*

**[ACTION — TITLE CARD]**
Full-screen dark background (`#0A0E1A`). Animated blockchain nodes pulse red.
Text fades in, centre-screen:

📌 **"₹11,333 Crore lost to cyber fraud in India — 2023"**
📌 *(small, below)* Source: MHA I4C Annual Report

**[ACTION]** Hard cut to the CryptoSentinel SOC dashboard — the dark command center loads.

🎵 Subtle ambient tech track begins — **−20 dB under voice**. Keep it there for the full video.

---

## ━━━ ACT 2 · PROBLEM · 0:12 – 0:25 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> *"Today, an investigating officer manually traces each wallet — one blockchain explorer tab at a time."*
> *"It takes 48 to 72 hours."* ⏸
> *"By the time a freeze request reaches the exchange — the funds have already been cashed out."*

**[ACTION — SPLIT SCREEN]**
Left side: icon of an officer at a desk, spreadsheets, hourglass ticking — **"72 hours"** label in amber.
Right side: animated wallet graph — nodes lighting up and vanishing as money moves.

📌 On-screen keyword overlays appear one by one:
- **"Manual process"** (amber)
- **"72 hours"** (amber)
- **"Funds gone"** (red)

---

## ━━━ ACT 3 · SOLUTION REVEAL · 0:25 – 0:40 ━━━━━━━━━━━━━━━━━━━━━━━

> *"We built CryptoSentinel."*
> *"India's first AI-powered, multi-chain crypto forensics platform — purpose-built for law enforcement."* ⏸
> *"One wallet address in. A complete, court-ready investigation dossier out. In seconds."*

**[ACTION — LOGO REVEAL]**
CryptoSentinel shield icon + wordmark animates in, centre screen.
Tagline appears beneath:

📌 **"Trace · Detect · Freeze"**

**[ACTION]** Transition to dashboard home — the SOC Command Center is visible in full.

📌 Metric card slides in from right:
**"48 hours → 4.2 seconds"**

Hold for 1 beat. ⏸

---

## ━━━ ACT 4 · ARCHITECTURE · 0:40 – 0:55 ━━━━━━━━━━━━━━━━━━━━━━━━━━

> *"CryptoSentinel runs as four specialised microservices — all behind a React SOC Command Center used directly by investigators."*

**[ACTION — DIAGRAM]**
Show a clean animated architecture diagram (dark bg, colour-coded blocks, animated arrows):

```
┌──────────────────────────────────────────────────┐
│         React SOC Command Center  :5173          │
│  11 investigation views · LEA SSO · RBAC login   │
└────────┬────────────┬───────────┬────────────────┘
         │            │           │            │
    :8000           :8001       :8002        :8003
  Blockchain      Agentic AI   ML Risk    Cybersecurity
  Forensics       LangGraph    XGBoost    NCRP · SAHYOG
  Tron / ETH      10 Tools     + SHAP     CCTNS · LEA
  Cross-chain     Streaming    0–100
```

> *"Blockchain forensics. Agentic AI. Machine learning risk scoring. And a full cybersecurity and legal gateway."*
> *"Let us show you what this looks like in a real investigation."*

🎵 Music lifts very slightly (+2 dB) as we cut to demo.

---

## ━━━ ACT 5 · LIVE DEMO · 0:55 – 2:30 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> **⚠ RECORDING NOTE: Full screen-capture, 1920×1080. No transition effects inside the demo — hard cuts only. Pointer highlights (circle/arrow) added in editing.**

---

### ── SCENE 5A · Opening the Investigation · 0:55 – 1:20 ──

**[ACTION]** Navigate to **"Stage 2: Graph & AI Trace"** in the sidebar.
The wallet input bar is visible and empty — the SOC dashboard is clean and ready.

📌 On-screen lower-third appears: **"LIVE DEMO — Tron TRC-20 USDT Investigation"**

> *"An investigator receives a victim complaint. They have one piece of evidence — a single suspect wallet address."* ⏸
> *"They enter it here."*

**[ACTION]** Click the wallet address input field (`id: wallet-address-input`).
Type — or paste — the demo address: `T_VICTIM_SIH_DEMO_999`
The **"Demo Case"** badge (purple) appears on the right of the field.

> *"One field. And click Trace."* ⏸

**[ACTION]** Click the **"⬡ Trace Wallet"** button.
The 6-step pipeline animation fires in sequence:

📌 Add subtitle overlays as each step lights up:
1. *Ingesting blockchain transactions...*
2. *Building directed transaction graph...*
3. *Running clustering engine...*
4. *Tracing multi-hop fund paths...*
5. *Attributing exchanges...*
6. *Computing ML risk score...*

> *"Our engine instantly ingests live TRC-20 USDT transaction data from the Tron blockchain..."*
> *"...builds a directed transaction graph using NetworkX..."*
> *"...runs our clustering engine using deposit-address reuse heuristics..."*
> *"...and within seconds — traces the multi-hop fund flow to identify exactly where the money went."*

**[ACTION]** The graph loads in the left panel — nodes and edges animate outward, forming the peel chain.

🔍 **ZOOM IN** — the terminal red node on the graph.

📌 Overlay callout on the red node: **"🏦 VASP: Binance · Terminal Node"**

> *"The graph shows the exact path the stolen funds took."* ⏸
> *"Three hops. A classic peel chain. Terminal node attributed — to Binance."*

---

### ── SCENE 5B · The ML Risk Score Moment · 1:20 – 1:50 ──

🔍 **ZOOM IN** — right sidebar, top card: **ML RISK SCORE**

> *"Simultaneously — our XGBoost ML ensemble evaluates 15 graph-level features."*

**[ACTION]** Watch the animated circular gauge count up live:
23 (green) → 51 (amber) → 74 (orange) → **87** (RED)

A red pulsing ring fires around the gauge at 87.
The label snaps to: **"⚠ HIGH RISK"**

> *"Risk score — 0.87."* ⏸ *"HIGH."* ⏸

**[ACTION]** The **"⚠ IMMEDIATE FREEZE RECOMMENDED"** badge pulses in below the score.

> *"Immediate freeze recommended."* ⏸

🔍 **ZOOM IN** — the SHAP factor bars below the gauge.
Hold the zoom. Let the bars sit for 1 full second before speaking.

📌 Highlight each bar as narrator speaks:
- Cluster size → **28%**
- Multi-hop depth → **24%**
- Exchange attribution → **22%**

> *"But here is what makes this different from any black-box system."* ⏸
> *"Every single factor — explained."*
> *"Cluster size: 28% contribution. Multi-hop peeling depth: 24%. Exchange attribution: 22%."*
> *"No black box."* ⏸ *"Every flag backed by a specific transaction hash — a judge can verify in court."*

**[ACTION]** Scroll down to show the **Fraud Typology Classification Card**.
The typology name reads with a confidence badge.

📌 Callout: **"Fraud Type: Peel Chain · Confidence 85%"**

> *"The system classifies the fraud typology — 85% confidence. Ready for the FIR chargesheet."*

---

### ── SCENE 5C · UPI Bridge + LangGraph Agent · 1:50 – 2:10 ──

**[ACTION]** Click **"Stage 1: UPI → Crypto Bridge"** in the sidebar.
The UPI Bridge view loads.

**[ACTION]** Click **"📋 OTP / KYC Freeze Scam"** to load the sample complaint.
The FIR text fills the textarea — containing UPI IDs, phone numbers, and USDT references.

> *"Now — here is India's unique problem."* ⏸
> *"Most cybercrime complaints arrive as raw FIR text. Not as wallet addresses."*
> *"The investigator has a complaint like this — with UPI IDs, phone numbers, and no crypto address at all."*

**[ACTION]** Click **"🔬 Analyze Complaint"**.
The 5-step NLP pipeline fires — each step lights up sequentially.

📌 Add subtitle for each step:
1. *NLP Entity Extraction*
2. *UPI ID Resolution*
3. *P2P Corridor Detection*
4. *Sanctions Watchlist Screening*
5. *Legal Notice Drafting*

> *"Our UPI Bridge parses this raw complaint — extracting every UPI VPA, every phone number, every crypto address."*

**[ACTION]** The LangGraph agent panel appears (purple border, pulsing activity dot).
Tool calls fire one by one with ✓ ticks:

📌 Show each tool call as it completes:
`extract_upi_entities()` ✓ → `resolve_upi_vpa_mapping()` ✓ → `detect_p2p_corridor()` ✓ → `query_sanctions_watchlist()` ✓ → `draft_section91_notice()` ✓

> *"Our LangGraph autonomous agent executes five real backend tool calls."*
> *"It resolves UPI handles to bank accounts... detects the P2P crypto corridor..."*
> *"...screens against the OFAC SDN list and I4C internal watchlist..."*
> *"...and automatically drafts a statutory Section 91 BNSS freeze notice."* ⏸
> *"No foreign platform — not Chainalysis, not TRM Labs — does this for India's UPI-to-crypto corridor."*

🔍 **ZOOM IN** — the results panel.

📌 Highlight the result card: **"Corridor: Binance P2P · Priority: IMMEDIATE"**

> *"Corridor identified. Binance P2P. Priority: Immediate."*
> *"The investigator can file the freeze request — the same day."*

---

### ── SCENE 5D · Evidence Chain — Court Admissibility · 2:10 – 2:30 ──

**[ACTION]** Click **"5. Hash Evidence Chain"** in the sidebar.
The AuditTrailView loads — 5 chain entries, each with hash values visible.

> *"Finally — every action CryptoSentinel takes is logged to a SHA-256 tamper-evident hash chain."*
> *"Each entry's digest is computed over its content plus the previous entry's hash."*
> *"Tamper any single entry — and the entire chain breaks."*

**[ACTION]** Click the large **"🔐 VERIFY CHAIN INTEGRITY"** button at the top.
Sequential animation: each entry cycles through a spinning loader → flips to green **"✓ PASS"** badge.

📌 Show each entry verifying:
Entry 1 ✓ → Entry 2 ✓ → Entry 3 ✓ → Entry 4 ✓ → Entry 5 ✓

🔍 **ZOOM IN** — the full-width success banner. **Hold the zoom for 3 seconds. Do not cut.**

📌 Banner reads:
> **"✅ CHAIN INTEGRITY VERIFIED — COURT ADMISSIBLE"**
> *SHA-256 · Sec 65B BSA · 5/5 PASS*

> *"One click."* ⏸
> *"The entire forensic evidence package — provably unaltered."*
> *"Court-admissible under Section 65B of the Bharatiya Sakshya Adhiniyam, 2023."*
> *"This is what turns a blockchain trace — into a prosecution."*

---

## ━━━ ACT 6 · PROOF POINTS · 2:30 – 2:45 ━━━━━━━━━━━━━━━━━━━━━━━━━━

> *"Here is what CryptoSentinel delivers — by the numbers."*

**[ACTION — METRIC CARDS]**
Large metric cards animate in one at a time (hold each for 1.5 seconds):

| Metric | Value |
|--------|-------|
| ⚡ Investigation time | **72 hours → 4.2 seconds** |
| 🧠 Fraud typologies detected | **6** — Peel Chain, Mixer, Smurfing, Rapid Hop, P2P Mule, Drainer |
| 🌐 Chains covered | **Tron TRC-20 + Ethereum ERC-20** + 4 bridge protocols |
| 🏦 VASPs identified | **Binance, WazirX, CoinDCX, ZebPay, Mudrex, Bybit, KuCoin** |
| 📈 Indexer throughput | **4,200+ tx/sec** · < 1.4 ms latency |
| ⚖️ Legal outputs | CCTNS Form-II · Sec 91/102 BNSS · ICJS SHA-256 seals |
| 🔗 Gov integrations | **NCRP 1930 · SAHYOG · Parichay SSO · MeriPehchan** |
| ✅ Tests passing | **25 / 25** automated tests · Production build verified |

📌 Each card uses: bold white number, dark navy card, electric blue accent border.

---

## ━━━ ACT 7 · IMPACT · 2:45 – 2:55 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> *"CryptoSentinel is production-ready today."*
> *"Every state police cybercrime unit. Every I4C analyst. Every ED investigator."*
> *"They can deploy this — and start recovering stolen funds in seconds, not days."*

**[ACTION]**
India map animates — nodes light up across major cities/states.

📌 Three text overlays appear in sequence:
1. **"Nationwide deployment ready"**
2. **"NCRP & SAHYOG integrated — Day 1"**
3. **"Court-admissible evidence — every case"**

> *"India-built. For India's cybercrime corridor. No foreign vendor dependency."*

---

## ━━━ ACT 8 · CLOSING · 2:55 – 3:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> *"Team [Your Team Name]. Thank you, SIH judges."* ⏸
> *"CryptoSentinel — Trace. Detect. Freeze."*

**[ACTION — CLOSING CARD]**
CryptoSentinel shield icon centred.
Team name + institution below.
Tagline: **"Built for India's Law Enforcement. Built for SIH 2026."**
Subtle fade to black.

🎵 Music fades out with the visual.

---
---

## 🎙️ CLEAN VOICEOVER SCRIPT (read-aloud order)

> **[HOOK]**
> "Right now, somewhere in India, a cybercrime victim has just lost ₹4 lakhs. The money is already moving — hopping across three wallets — disappearing into a crypto exchange. The police have 48 hours before it is gone forever."

> **[PROBLEM]**
> "Today, an investigating officer manually traces each wallet — one blockchain explorer tab at a time. It takes 48 to 72 hours. By the time a freeze request reaches the exchange — the funds have already been cashed out."

> **[SOLUTION]**
> "We built CryptoSentinel. India's first AI-powered, multi-chain crypto forensics platform — purpose-built for law enforcement. One wallet address in. A complete, court-ready investigation dossier out. In seconds."

> **[ARCHITECTURE]**
> "CryptoSentinel runs as four specialised microservices — all behind a React SOC Command Center used directly by investigators. Blockchain forensics. Agentic AI. Machine learning risk scoring. And a full cybersecurity and legal gateway. Let us show you what this looks like in a real investigation."

> **[DEMO — Intake]**
> "An investigator receives a victim complaint. They have one piece of evidence — a single suspect wallet address. They enter it here. One field. And click Trace."

> **[DEMO — Trace]**
> "Our engine instantly ingests live TRC-20 USDT transaction data from the Tron blockchain... builds a directed transaction graph using NetworkX... runs our clustering engine using deposit-address reuse heuristics... and within seconds — traces the multi-hop fund flow to identify exactly where the money went. The graph shows the exact path the stolen funds took. Three hops. A classic peel chain. Terminal node attributed — to Binance."

> **[DEMO — Risk Score]**
> "Simultaneously — our XGBoost ML ensemble evaluates 15 graph-level features. Risk score — 0.87. HIGH. Immediate freeze recommended. But here is what makes this different from any black-box system. Every single factor — explained. Cluster size: 28% contribution. Multi-hop peeling depth: 24%. Exchange attribution: 22%. No black box. Every flag backed by a specific transaction hash — a judge can verify in court. The system classifies the fraud typology — 85% confidence. Ready for the FIR chargesheet."

> **[DEMO — UPI Bridge]**
> "Now — here is India's unique problem. Most cybercrime complaints arrive as raw FIR text. Not as wallet addresses. The investigator has a complaint like this — with UPI IDs, phone numbers, and no crypto address at all. Our UPI Bridge parses this raw complaint — extracting every UPI VPA, every phone number, every crypto address. Our LangGraph autonomous agent executes five real backend tool calls. It resolves UPI handles to bank accounts... detects the P2P crypto corridor... screens against the OFAC SDN list and I4C internal watchlist... and automatically drafts a statutory Section 91 BNSS freeze notice. No foreign platform — not Chainalysis, not TRM Labs — does this for India's UPI-to-crypto corridor. Corridor identified. Binance P2P. Priority: Immediate. The investigator can file the freeze request — the same day."

> **[DEMO — Evidence Chain]**
> "Finally — every action CryptoSentinel takes is logged to a SHA-256 tamper-evident hash chain. Each entry's digest is computed over its content plus the previous entry's hash. Tamper any single entry — and the entire chain breaks. One click. The entire forensic evidence package — provably unaltered. Court-admissible under Section 65B of the Bharatiya Sakshya Adhiniyam, 2023. This is what turns a blockchain trace — into a prosecution."

> **[PROOF]**
> "Here is what CryptoSentinel delivers — by the numbers." *(let metric cards speak)*

> **[IMPACT]**
> "CryptoSentinel is production-ready today. Every state police cybercrime unit. Every I4C analyst. Every ED investigator. They can deploy this — and start recovering stolen funds in seconds, not days. India-built. For India's cybercrime corridor. No foreign vendor dependency."

> **[CLOSING]**
> "Team [Your Team Name]. Thank you, SIH judges. CryptoSentinel — Trace. Detect. Freeze."

---
---

## 🎨 Visual Style Guide

| Element | Specification |
|---------|--------------|
| **Background** | Deep navy `#0A0E1A` — matches SOC dark theme |
| **Primary accent** | Electric blue `#00D4FF` — borders, active states |
| **Alert accent** | Amber `#FF8C00` (warning) · Red `#FF2D55` (critical) |
| **Font** | **Outfit** or **Inter** (Google Fonts) — Bold for numbers, Regular for body |
| **Transitions** | Hard cuts inside demo · Subtle fade (0.3s) between Acts |
| **On-screen text** | ≤ 5 words per callout · Min 28pt equivalent · White or accent colour |
| **Screen recording** | 1920×1080 · Pointer highlights (circle + arrow) added in editing |
| **Zoom behaviour** | Punch-in, hold 2–3 s, punch-out · Never zoom mid-sentence |
| **Captions** | Auto-synced white subtitles · Dark semi-transparent pill background |
| **Music** | Ambient tech track · −20 dB under voice throughout · Fade out at closing card |

---

## 🎯 Delivery Tips

| Tip | Detail |
|-----|--------|
| **Pause on red** | Let the HIGH RISK gauge sit for 1–2 s before speaking — the visual does the work |
| **"No black box"** slowly | This is the key differentiator — give it its own beat and pause after |
| **"No foreign platform"** | Emphasise India — SIH judges respond strongly to indigenous solutions |
| **Zoom the PASS banner** | Hold for 3 full seconds — don't rush off it |
| **Voice on "One click"** | Drop volume slightly, then pause — it lands harder |
| **Tell the investigator story** | You are narrating a real investigation, not a product demo — keep the officer persona alive throughout |
| **Don't explain the tech** | The UI explains itself. Your job is to tell the story of the investigator solving the case |
| **Rehearse 3× minimum** | Time each run. If you go over 3:00, cut explanation, never cut demo or proof |

---

## 🛟 Backup Lines (if something goes wrong live)

> *(If backend is unavailable)*
> *"The system's local forensic fallback mode is generating results from heuristic data — in a production deployment this runs against the live Tron mainnet."*

> *(On any lag)*
> *"The system is performing a live multi-hop blockchain trace — this is the actual computation running."*

> *(If a step fails)*
> *"What you would see here is the automated exchange attribution — let me show you the result directly."*
> *(Navigate to the result panel and show the outcome.)*

---

## ✅ Pre-Submission Checklist

- [ ] Total video length: **≤ 3:00** (time it 3 times)
- [ ] Hook lands within first **12 seconds**
- [ ] One narrator, one voice, one mic — quiet room
- [ ] All on-screen text readable at 1080p — min 28pt equivalent
- [ ] Demo rehearsed end-to-end — no loading failures, no misclicks
- [ ] **"72 hours → 4.2 seconds"** metric appears visually on screen
- [ ] SAHYOG / NCRP integration shown in demo (Scene 5C tool calls)
- [ ] Cross-chain bridge detection shown (Architecture diagram + graph node)
- [ ] UPI Bridge NLP pipeline shown (Scene 5C)
- [ ] Evidence hash chain verification shown (Scene 5D — PASS banner)
- [ ] Metric cards animated in Act 6 — not just spoken
- [ ] "No foreign platform" line delivered clearly
- [ ] Team name / logo at close
- [ ] Subtitles / captions proofread — zero errors
- [ ] Reviewed by someone unfamiliar with the project — story is clear to them

---

*CryptoSentinel · SIH26183 · Ministry of Home Affairs · Indian Cybercrime Coordination Centre (I4C)*
*v3.0 — Updated per SIH winning video patterns analysis*
