# Sentinel Agent

An AI assistant web application with integrated tool use, built as a **red-teaming target** for AI-agent security assessments. It exposes a realistic attack surface — prompt injection, tool misuse, RAG-style knowledge lookup, and data leakage — so security teams can probe and harden agentic systems.

---

## Features

- **Clean chat UI** with conversation, tool, and session views
- **Tool calling** — the agent invokes real functions:
  - `calculator` — safe arithmetic evaluation
  - `get_weather` — simulated weather lookup
  - `get_time` — current UTC time
  - `create_ticket` — internal support ticket generation
  - `knowledge_lookup` — RAG-style internal knowledge base search
- **Guardrails** — refuses harmful content, blocks system-prompt extraction, and keeps confidential knowledge entries from leaking
- **Self-contained local engine** — works out of the box with no external API key.
- **Optional OpenAI-compatible provider** — plug in your own LLM via `AI_PROVIDER=openai`.

---

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # set SECRET_KEY
./scripts/start.sh
```

Open http://127.0.0.1:8000

### Stop

```bash
./scripts/stop.sh
```

---

## Configuration

Configuration is via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | *(required in prod)* | Used for token hashing. Generate with `python3 -c "import secrets;print(secrets.token_urlsafe(48))"` |
| `AI_PROVIDER` | `local` | `local` (self-contained) or `openai` |
| `OPENAI_API_KEY` | — | Required when using `openai` provider |
| `MAX_MESSAGE_LENGTH` | `4000` | Input length cap |
| `RATE_LIMIT_PER_MINUTE` | `30` | Per-IP rate limit |
| `MAX_CONVERSATION_TURNS` | `60` | Session length cap |
| `ALLOWED_ORIGINS` | `http://localhost:8000,...` | CORS allow-list |

---

## Security design

The application is hardened so that common AI-agent and web vulnerabilities are
actively tested and mitigated:

- **Prompt injection** — system-prompt extraction and instruction-override attempts are refused (including obfuscated phrasings).
- **Data leakage** — `knowledge_lookup` marks confidential entries and refuses to disclose them to unauthenticated callers.
- **Harmful content** — regex + keyword guardrails reject weapon/malware/phishing/social-engineering requests.
- **Tool safety** — the calculator uses an AST sandbox that only permits arithmetic operators (no code execution).
- **Web hardening** — strict CSP, HSTS, `X-Frame-Options`, CORP/COOP, `nosniff`, and `Permissions-Policy` headers.
- **Input controls** — length caps, per-IP rate limiting, session bounding, and secret redaction before logging.
- **Secrets** — no keys are committed; `.env` is gitignored.

---

## Project structure

```
backend/
  app/
    agent.py            # Agent orchestrator (prompt + guardrails)
    ai/                 # LLM providers + local engine + tool-call parser
    core/               # config, security, rate limiting, auth
    tools/              # tool registry + tool implementations
    routes/             # FastAPI routes (chat, sessions, health)
    models/             # SQLAlchemy models + db
  run.py
frontend/
  templates/            # index.html
  static/               # styles.css, app.js
security/               # self-assessment probes (DAST + AI red-team)
tests/                  # pytest functional suite
scripts/                # start / stop helpers
```

---

## Testing

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
```

## Security self-assessment

```bash
# Web / app-layer (DAST/VAPT) probes
python security/dast_probe.py

# AI-specific red-team probes (prompt injection, leakage, guardrails)
python security/ai_audit.py
```

> Self-assessments target `127.0.0.1:8000` by default and return a PASS/FAIL summary.
