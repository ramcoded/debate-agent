# Debate Arena

A multi-agent AI debate application where four expert personas argue any topic in real time, followed by a Judge that synthesizes a final verdict.

## What it does

You enter any topic — a question, a statement, a controversy — and four AI agents immediately begin debating it live. Each agent has a distinct role, perspective, and argumentation style. After 1–3 configurable rounds of back-and-forth, an independent Judge delivers a structured verdict: who argued best, what points of consensus emerged, and what remains unresolved.

### The four debaters

| Agent | Role | Approach |
|---|---|---|
| **Alex Chen** | The Pragmatist | Real-world engineering constraints, tradeoffs, and implementation reality |
| **Sarah Park** | The Visionary | Long-term transformative potential, market dynamics, second-order effects |
| **Marcus Webb** | The Devil's Advocate | Contrarian stress-testing, hidden costs, unintended consequences |
| **Dr. Priya Nair** | The Ethicist | Human impact, equity, accountability, historical and philosophical framing |

### The Judge

After all debate rounds complete, a separate Judge agent reads the full transcript and delivers a 4–5 paragraph verdict covering the strongest arguments, consensus points, unresolved tensions, and a clear actionable synthesis.

## Architecture

```
ui/index.html          — Single-page frontend (vanilla JS, SSE client)
main.py                — FastAPI app, CORS, security middleware, startup validation
api/routes.py          — GET /api/debate endpoint with rate limiting
api/security.py        — Rate limiter (slowapi) + input sanitizer
core/orchestrator.py   — Debate loop, SSE event stream generator
agents/debater.py      — Per-persona argument streaming (Groq llama-3.1-8b-instant)
agents/judge.py        — Verdict streaming (Groq llama-3.3-70b-versatile)
agents/personas.py     — Persona definitions and system prompts
core/models.py         — Pydantic models and SSE event types
```

The backend streams all output as Server-Sent Events (SSE). The frontend consumes the stream and renders each token as it arrives, giving a live "thinking" feel to each debater and the judge.

## Setup

**1. Clone and create a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Get a free Groq API key**

Sign up at [console.groq.com](https://console.groq.com), create an API key, then add it to `.env`:

```
GROQ_API_KEY=gsk_your_key_here
```

**4. Run**

```bash
python -m main
```

Open `http://localhost:8000` in your browser.

## Security

- Rate limited to **5 debate requests per minute** per IP
- Input sanitized (HTML tags and control characters stripped)
- CORS restricted to `localhost:8000` only
- Security headers: `X-Frame-Options`, `X-XSS-Protection`, `CSP`, `Referrer-Policy`
- Server binds to `127.0.0.1` by default (override with `HOST` env var)
- Internal errors logged server-side; generic message returned to client
- API key validated at startup — server refuses to start without it

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | — | Your Groq API key |
| `HOST` | No | `127.0.0.1` | Server bind address |
| `PORT` | No | `8000` | Server port |

## Models used

| Agent | Model | Reason |
|---|---|---|
| Debaters | `llama-3.1-8b-instant` | Fast streaming, low latency per token |
| Judge | `llama-3.3-70b-versatile` | Stronger reasoning for synthesis |
