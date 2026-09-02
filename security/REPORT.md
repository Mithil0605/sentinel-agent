# Sentinel Agent — Security Assessment Report

This report summarizes the security assessment performed on the Sentinel Agent,
an AI assistant web application built as a red-team target. It covers static
analysis (SAST), dynamic/active testing (DAST/VAPT), and AI-specific attack
paths. Findings were remediated and re-tested.

> Environment note: all scans targeted the application locally on loopback
> (`127.0.0.1:8000`). No production data was involved.

---

## 1. Scope

- **Target:** Sentinel Agent FastAPI backend + HTML/JS frontend
- **Attack surface:** REST API (`/api/chat`, `/api/tools`, `/api/sessions`, `/api/health`), agent tool layer, RAG-style knowledge lookup, chat UI
- **Techniques:** Bandit (SAST), custom DAST/VAPT probes, Nuclei, and an AI-specific red-team suite

---

## 2. SAST (Static Application Security Testing)

Tool: Bandit 1.9.4

| Finding | Severity | Status |
|---------|----------|--------|
| `B104` — service bound to all interfaces by default | Medium | **Fixed** — HOST now defaults to `127.0.0.1`; exposed only via explicit env override |
| `B110` — bare try/except/pass when loading `.env` | Low | **Fixed** — added error logging |

**Result:** 0 findings after remediation.

---

## 3. DAST / VAPT (Dynamic & Active Testing)

Custom probe + Nuclei against the live app.

| Check | Result |
|-------|--------|
| Missing security headers (CSP, HSTS, XFO, nosniff, CORP/COOP, Permissions-Policy) | **Fixed** — all present after hardening |
| CORS reflecting arbitrary origins | Pass (no reflection) |
| Path traversal (`/static/../../etc/passwd`, URL-encoded variants) | Pass (blocked, 404) |
| Sensitive file exposure (`.env`, source, `/proc`, db) | Pass (blocked) |
| HTTP method tampering (TRACE/PUT/DELETE) | Pass (405) |
| Open redirect | Pass |
| SQLi / XSS payloads in inputs | Pass (handled, no reflection) |
| Oversized payload DoS | Pass (422 on > max length) |

**Result:** 0 FAIL / 0 WARN after remediation.

---

## 4. AI-Specific Red-Team Audit

Dedicated suite against the agent's model/tool layer.

### 4.1 System-prompt extraction / prompt injection
Attempts to reveal the system prompt — including obfuscated phrasings
("repeat the text before", "DEBUG MODE", "show me the rules", "ignore previous
instructions") — are **denied**.

### 4.2 Confidential data leakage (RAG / knowledge base)
Direct queries for confidential knowledge entries returned **no confidential
content**. The `knowledge_lookup` tool now:
- marks entries as `confidential`,
- refuses to disclose confidential bodies to unauthenticated callers,
- returns only a notice that access is restricted.

### 4.3 Harmful-content refusal
Requests for bomb construction, phishing templates, ransomware, and
credential-theft social engineering were **refused**.

**Finding (original):** the initial substring blocklist was trivially bypassed
by rephrasing (e.g., "build a bomb", "phishing email template", "write
ransomware"). **Remediated:** replaced with broader regex + keyword coverage.

**Result:** 0 FAIL / 0 WARN on core attack paths after remediation.

---

## 5. Summary

| Category | Tooling | Findings |
|----------|---------|----------|
| SAST | Bandit | 2 (fixed) → 0 |
| DAST/VAPT | Custom + Nuclei | 4 (fixed) → 0 |
| AI red-team | Custom suite | 5 (fixed) → 0 |

All remediated findings were re-tested and the complete test suites
(`tests/`, `security/dast_probe.py`, `security/ai_audit.py`) pass.
