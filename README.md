PLACEHOLDER_MARKER_FOR_FULL_REPLACE
# DELVE — Deep Evidence & Log Verification Engine

An AI-powered incident investigation platform. Give it a plain-English incident description; it dispatches specialized AI agents to pull real evidence from logs, metrics, deployments, and historical incidents in parallel, then synthesizes an evidence-grounded root cause hypothesis — never presenting a guess as a confirmed fact.

> Built as a hands-on production-engineering learning project: multi-agent orchestration, RAG, guardrails, evaluations, and CI/CD, using a free-tier LLM stack end to end.

---

## Why This Exists

Investigating a production incident today means manually correlating logs, metrics, deployment history, and past postmortems across separate tools — slow, and easy to get wrong under pressure. DELVE automates the *investigation*, not the fix: it proposes a hypothesis and next steps, and requires a human to approve anything before it's considered actionable.

**Core design principle:** DELVE must never present a guess as a fact. Every architectural decision below traces back to this.

---

## Architecture

```
Streamlit Dashboard → FastAPI → Triage Agent → Investigation Team
                                                       │
                                    ┌──────────────────┼──────────────────┐
                                    ▼                  ▼                  ▼
                            Parallel Agents:    Root Cause Agent    Evidence Store
                         Log / Metrics /        (synthesis, runs    (Postgres, FK
                     Deployment / Historical    AFTER parallel)     to incident)
                            (RAG via Chroma)           │
                                                        ▼
                                          Guardrails → Actions (risk-classified)
                                                        │
                                                        ▼
                                          Human Approval Gate (nothing auto-executes)
```

Full architectural writeup, line-by-line code walkthrough, and every real bug hit along the way: see [`DELVE_Complete_Guide.md`](./DELVE_Complete_Guide.md).

---

## Tech Stack

| Layer | Choice | Cost |
|---|---|---|
| API | FastAPI | Free |
| Database | PostgreSQL (Docker) | Free |
| Agent framework | Google ADK | Free (open source) |
| LLM inference | Groq (`gpt-oss-120b` / `gpt-oss-20b` via LiteLLM) | Free tier |
| Embeddings | `sentence-transformers` (local) | Free, no API calls |
| Vector store | ChromaDB (embedded) | Free |
| Dashboard | Streamlit | Free |
| CI/CD | GitHub Actions | Free (public repo) |

**Zero paid infrastructure required to run this project.**

---

## Features

- **Automated triage** on incident creation — instant, hypothesis-framed initial assessment
- **Multi-agent parallel investigation** — log, metrics, deployment, and historical-precedent agents run concurrently
- **RAG over historical incidents** — semantic search (not keyword match) correctly distinguishes a true pattern match from a same-service-different-cause incident
- **Evidence-grounded root cause synthesis** — every claim traces to a real observed fact; confidence is explicitly `low`/`medium`/`high`, never asserted as certain
- **Guardrails** — input injection scanning, tool-level service allowlisting, evidence-grounding verification, action risk classification
- **Human approval gate** — every recommended action requires explicit approval; nothing auto-executes
- **Full observability** — per-step execution timing and success/failure logged to Postgres
- **CI pipeline** — lint + import-sanity check on every push via GitHub Actions

---

## Observed Performance (real numbers from development testing)

Measured on Groq's **free tier** (`gpt-oss-120b` for reasoning/tool-calling steps, `gpt-oss-20b` for formatting steps), running locally against Postgres in Docker. These are real, observed dev-environment numbers — not a formal benchmark suite, and free-tier latency/throughput will differ from a paid tier.

| Step | Observed Latency | Notes |
|---|---|---|
| Triage (`POST /incidents`) | **~2–4 seconds** | Single LLM call, structured output, no tool calls |
| Full investigation (`POST /incidents/{id}/investigate`) | **~25–45 seconds** (clean run) | 4 parallel investigator+formatter pairs (8 LLM calls) + 1 root-cause synthesis call = 9 LLM calls total per investigation |
| Full investigation, with 1 rate-limit retry | **~90–120 seconds** | Retry logic waits 70s before re-attempting after a 429 |
| RAG retrieval (`search_historical_incidents`) | **< 100ms** | Local embedding model + local ChromaDB, no network call |
| Health check (`GET /health`) | **< 10ms** | No DB/LLM dependency |

**Rate-limit ceiling (Groq free tier, observed):**
- `gpt-oss-120b`: **8,000 tokens/minute** per organization
- A single full investigation run uses roughly **6,000–8,000 tokens** across all 9 LLM calls combined — i.e., very close to the free-tier ceiling in one burst
- **Mitigation implemented:** investigator/synthesis calls run on `gpt-oss-120b`; formatter calls (the simpler reformat-to-JSON steps) run on `gpt-oss-20b` — splitting load across two independent rate-limit pools measurably reduced 429s during testing

**Retrieval accuracy (RAG, qualitative, n=4 test documents):**
- Given a payment-service DB-pool-exhaustion incident, the retrieval correctly ranked the semantically matching historical postmortem (`INC-0042`, same failure pattern) **first**, and correctly ranked a same-service-but-different-root-cause postmortem (`INC-0063`, null-pointer crash) **below** it — confirming genuine semantic discrimination rather than keyword or service-name matching.

**Evaluation harness:** `src/delve/evals/run_eval.py` scores the pipeline against known-answer test cases (keyword grounding in the root cause hypothesis, correct historical match, minimum confidence threshold). Current dataset: 1 case (`CASE_001`) — intentionally small; built to be extended.

---

## Project Structure

```
delve/
├── .github/workflows/ci.yml      # Lint + import check on every push
├── src/delve/
│   ├── main.py, config.py, db.py # App entrypoint, settings, DB setup
│   ├── models/                   # SQLAlchemy tables (Incident, Evidence, Action, ExecutionLog)
│   ├── schemas/                  # Pydantic API request/response shapes
│   ├── routers/incidents.py      # All API endpoints
│   ├── tools/                    # Functions agents call (search_logs, get_metrics, ...)
│   ├── data/                     # Simulated logs/metrics/deployments + postmortem docs
│   ├── rag/                      # Embedding + vector search (ChromaDB)
│   ├── agents/                   # Triage, investigation, root-cause, orchestration
│   ├── guardrails/                # Input, tool, evidence, and action safety checks
│   ├── evals/                    # Automated evaluation dataset + scorer
│   └── dashboard/app.py          # Streamlit UI
├── docker-compose.yml            # Postgres + Redis
└── pyproject.toml / uv.lock      # Dependencies (uv-managed)
```

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone https://github.com/jayant132/Delve-Deep-Evidence-Log-Verification-Engine-.git
cd Delve-Deep-Evidence-Log-Verification-Engine-

# 2. Install dependencies (uv)
uv python pin 3.11
uv sync

# 3. Configure environment
cp .env.example .env
# edit .env: add your free Groq API key from console.groq.com/keys

# 4. Start Postgres + Redis
docker compose up -d

# 5. Create database tables
uv run python -c "
from delve.db import Base, engine
from delve.models.incident import Incident
from delve.models.evidence import Evidence
from delve.models.action import Action
from delve.models.execution_log import ExecutionLog
Base.metadata.create_all(engine)
"

# 6. Ingest RAG postmortem data
uv run python -m delve.rag.run_ingest

# 7. Run the API
uv run uvicorn delve.main:app --port 8000

# 8. (separate terminal) Run the dashboard
uv run streamlit run src/delve/dashboard/app.py
```

Open `http://localhost:8501` for the dashboard, or `http://localhost:8000/docs` for the raw API.

---

## Example Usage

```bash
curl -X POST http://localhost:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{"title": "Payment failures spiking", "description": "5xx error rate on payment service jumped from 0.2% to 18% about 10 minutes after latest deployment"}'

curl -X POST http://localhost:8000/incidents/{id}/investigate
curl http://localhost:8000/incidents/{id}/evidence
curl http://localhost:8000/incidents/{id}/actions
```

---

## Known Limitations (honest, not swept under the rug)

- **Free-tier rate limits are real** — heavy back-to-back testing will hit Groq's 8,000 TPM ceiling; retry logic handles transient spikes, not sustained overload
- **Simulated data only** — logs/metrics/deployments are hand-authored fixtures, not real infrastructure integrations (by design for this phase; tool interfaces are built to be swappable)
- **Eval dataset is small** (1 case) — proves the harness works, not statistically significant coverage
- **No containerized deployment of the app itself** — attempted (see guide), shelved due to local disk constraints from the `torch`/CUDA dependency chain; Postgres/Redis run containerized, the app runs natively
- **Guardrails are detection-first, not hard-blocking** for input injection — a deliberate tradeoff to avoid false-positive blocking of legitimate incident text; documented in the guide

---

## Full Documentation

See [`DELVE_Complete_Guide.md`](./DELVE_Complete_Guide.md) for the complete business case, architecture rationale, line-by-line code walkthrough, every real bug encountered during development and why, and a step-by-step guide to rebuilding this project from scratch.

## License

MIT (or your preferred license)
