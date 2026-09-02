# HANDOFF — Sentinel Agent (Fencio Internship Assessment)

> Read me first when starting a new session in this project. This file is kept
> up to date with the current state and the ONLY remaining tasks.

## Goal
Fencio internship assessment: onboard an AI agent to Fencio's red-teaming
platform **Shark** (shark.fencio.dev), run a scan, and email the vulnerability
report to krishnaa@fencio.dev.

## Project facts
- **Agent:** Sentinel Agent — FastAPI backend + HTML/JS frontend on port 8000.
- **Stack:** Python/FastAPI, local AI engine (`AI_PROVIDER=local`), 5 tools
  (calculator, weather, time, create_ticket, knowledge_lookup).
- **Repo:** private `github.com/Mithil0605/sentinel-agent` (pushed, clean —
  no `.env`/secrets/identity; `.env` is gitignored).
- **Verification (all done & green):**
  - Bandit (SAST): 0 findings
  - DAST/VAPT probe (`security/dast_probe.py`): 0 FAIL / 0 WARN
  - AI red-team (`security/ai_audit.py`): 0 FAIL
  - Functional tests: `pytest tests/` = 9 passed
  - Docker build + run: verified working

## Current live deployment (TEMPORARY)
- Public URL: **https://d611c13c1647c5.lhr.life** (open to anyone)
- Ephemeral; dies if the machine reboots or the tunnel process stops.
- Restart with `./scripts/tunnel.sh`, then re-read `/tmp/tunnel.log` for the
  new `*.lhr.life` URL.

## Scripts
- `./scripts/start.sh` — start backend on 127.0.0.1:8000 (log: logs/sentinel.log)
- `./scripts/tunnel.sh` — open temporary public URL
- `./scripts/stop.sh` — stop backend

---

## ONLY REMAINING TASKS

### 1) Permanent deployment (needs user action — I have no Render token)
- User: sign into **dashboard.render.com** (free, connect GitHub).
- New → **Blueprint** → connect repo `Mithil0605/sentinel-agent`.
- The pushed **`render.yaml`** auto-deploys a permanent URL
  (~ `https://sentinel-agent.onrender.com`).
- Free tier cold-starts after ~15 min idle; first request wakes it (30–60s).
- Give this permanent URL to Fencio and point Shark at it.

### 2) Shark assessment (REQUIRES USER LOGIN — not automatable)
- Log into **shark.fencio.dev** with Google.
- Register the agent, pointed at a live URL.
- Run the red-team scan.
- Export the vulnerability report.
- Email it to **krishnaa@fencio.dev**.

## Nice-to-haves (offered, not done)
- Draft the email to Fencio.
- Set up the permanent Render/Fly deployment (once user provides account/token).
