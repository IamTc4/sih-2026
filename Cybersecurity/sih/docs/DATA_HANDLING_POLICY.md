# Data Handling & Security Policy

**System:** Fraud Detection Pipeline — Evidence Trail & Threat Signature Library
**Version:** 1.0
**Date:** 2026-09-05
**Owner:** Security Engineering
**Classification:** PUBLIC (this document)

---

## 1. Purpose & Scope

This policy defines how data is classified, protected, accessed, and retained within the Fraud Detection Pipeline. It covers all components:
- Threat Signature Library (fraud detection)
- Evidence Trail Service (hash-chain logging)
- API Layer (trace, cluster, attribution endpoints)
- LangGraph Agent (legal notice generation)

**Applies to:** All personnel, contractors, and automated systems processing data in this pipeline.

---

## 2. Data Classification

| Level | Label | Examples | Access Roles | Encryption | Retention |
|-------|-------|----------|--------------|------------|-----------|
| **PUBLIC** | `public` | Wallet addresses, tx hashes, trace graphs, risk scores, fraud signatures, cluster IDs, evidence tx hashes | All (VIEWER+) | At-rest (AES-256) | 7 years |
| **INTERNAL** | `internal` | Cluster metadata, analysis notes, exchange attributions, investigation timestamps | ANALYST+ | At-rest (AES-256) | 7 years |
| **CONFIDENTIAL** | `confidential` | Victim name, email, phone, raw complaint text, complaint metadata (IP, UA) | INVESTIGATOR+ | At-rest + In-transit (TLS 1.3) + Field-level (AES-256-GCM) | 10 years |
| **RESTRICTED** | `restricted` | Legal notices, investigation details, takedown requests, agent prompts/outputs | INVESTIGATOR+ (ADMIN for mgmt) | At-rest + In-transit + Field-level + HSM-backed keys | 10 years + legal hold |

**Default:** Any unclassified field defaults to **INTERNAL**.

---

## 3. Role-Based Access Control (RBAC)

| Role | Description | PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED | Write Access |
|------|-------------|--------|----------|--------------|------------|--------------|
| **VIEWER** | Dashboard consumers, external auditors | ✅ Read | ❌ | ❌ | ❌ | ❌ |
| **ANALYST** | Fraud analysts, data scientists | ✅ R/W | ✅ Read | ❌ | ❌ | PUBLIC, INTERNAL |
| **INVESTIGATOR** | Law enforcement liaisons, case officers | ✅ R/W | ✅ R/W | ✅ Read | ✅ Read | All except RESTRICTED write |
| **ADMIN** | System administrators, security officers | ✅ R/W | ✅ R/W | ✅ R/W | ✅ R/W | All |
| **SYSTEM** | Service accounts, pipelines, agents | ✅ R/W | ✅ R/W | ✅ R/W | ✅ R/W | All |

**Enforcement:** Implemented at API layer via `RBACEnforcer` middleware. All responses filtered automatically.

---

## 4. PII Handling Requirements

### 4.1 Identified PII Categories
- **Direct Identifiers:** Full name, email, phone, government ID
- **Indirect Identifiers:** IP address, user agent, complaint free-text (may contain names/locations)
- **Legal Data:** Legal notice content, takedown requests, investigation findings

### 4.2 Controls
| Control | Implementation |
|---------|----------------|
| **Minimization** | Only collect PII required for investigation; complaint form validates required fields only |
| **Encryption** | Field-level encryption for CONFIDENTIAL/RESTRICTED using `cryptography.fernet` (AES-256-GCM) |
| **Key Management** | Keys stored in HashiCorp Vault (dev) / AWS KMS (prod); rotated quarterly |
| **Redaction** | Automatic redaction in API responses for unauthorized roles (`policy.redaction`) |
| **Anonymization** | Analytics exports use `Anonymizer` to replace addresses with `ADDR_XXXXXX` |
| **Audit Logging** | Every access to CONFIDENTIAL/RESTRICTED logged to Evidence Trail with user ID, timestamp, field |

### 4.3 Data Subject Rights
| Right | Process |
|-------|---------|
| **Access** | Investigators can request data export via admin API (logged) |
| **Rectification** | Victim contact info updatable via authenticated complaint amendment |
| **Erasure** | Not applicable during active investigation; post-closure, PII purged per retention schedule |
| **Portability** | JSON export of subject's data available on verified request |

---

## 5. Evidence Trail Integrity

| Property | Mechanism |
|----------|-----------|
| **Immutability** | Append-only SQLite/PostgreSQL; DB user lacks UPDATE/DELETE |
| **Tamper Evidence** | SHA-256 hash chain: `chain_hash = H(prev_hash \|\| content_hash)` |
| **Verification** | `GET /verify/{id}` and `GET /chain/verify` endpoints |
| **External Anchoring** | Periodic `chain_hash` committed to Ethereum mainnet (future) |
| **Backup** | Daily WORM export to S3 Object Lock (future) |

**Legal Admissibility:** Hash-chain design meets NIST SP 800-152 criteria for cryptographic logs.

---

## 6. Secure Development Practices

| Practice | Status |
|----------|--------|
| **Dependency Scanning** | `pip-audit` in CI; fail on HIGH/CRITICAL |
| **SAST** | `bandit` + `semgrep` in PR pipeline |
| **Secrets Management** | No secrets in code; `.env` gitignored; Vault/KMS in prod |
| **Input Validation** | Pydantic models on all API endpoints; strict schemas |
| **Output Encoding** | JSON responses; no HTML/template injection vectors |
| **Security Headers** | `CSP`, `HSTS`, `X-Frame-Options` via FastAPI middleware |
| **Penetration Testing** | Annual third-party; quarterly internal red-team |

---

## 7. Incident Response

| Phase | Action | Owner | SLA |
|-------|--------|-------|-----|
| **Detect** | SIEM alerts on: failed auth, chain verification failure, unusual access patterns | SOC | < 15 min |
| **Contain** | Revoke API keys; isolate affected DB; disable compromised service account | Security Eng | < 1 hour |
| **Investigate** | Query Evidence Trail for scope; verify chain integrity | Security Eng + Legal | < 4 hours |
| **Notify** | Data Protection Officer; affected data subjects (if PII exposed); regulators (GDPR/CCPA) | Legal | < 72 hours |
| **Recover** | Restore from WORM backup; rotate keys; re-anchor chain | DevOps | < 24 hours |
| **Post-Mortem** | Blameless retrospective; update threat model; implement fixes | All | < 2 weeks |

---

## 8. Compliance Mapping

| Regulation | Relevant Sections | Our Controls |
|------------|-------------------|--------------|
| **GDPR** | Art. 5 (minimization), Art. 25 (by design), Art. 32 (security), Art. 33-34 (breach) | Classification, RBAC, encryption, 72hr breach notify |
| **CCPA** | §1798.100 (access), §1798.105 (deletion), §1798.150 (security) | Subject rights API, retention schedule, encryption |
| **NIST 800-53** | AU-2, AU-3, AU-6, SC-8, SC-13, SI-7 | Audit logs, hash-chain, TLS, integrity verification |
| **ISO 27001** | A.8.2, A.9.2, A.12.4, A.18.1 | Classification, access control, logging, compliance |

---

## 9. Key Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| **Data Protection Officer** | dpo@company.com | Legal Counsel |
| **Security Engineering Lead** | sec-eng-lead@company.com | CISO |
| **Incident Commander** | incident@company.com | CTO |
| **Legal/Compliance** | legal@company.com | General Counsel |

---

## 10. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-05 | Security Engineering | Initial release |

---

**Approval:** This policy is approved by CISO and Legal Counsel. Changes require sign-off from both.

**Next Review:** 2027-03-05 (or upon material system change)