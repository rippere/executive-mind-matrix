# Executive Mind Matrix

A decision intelligence platform that runs adversarial AI agent dialectics so strategic decisions get pressure-tested before they're made.

Instead of asking one AI for an answer, Executive Mind Matrix routes every intent through three competing agent personas with distinct cognitive profiles. They debate. Their outputs are synthesized into a risk-adjusted recommendation with explicit tradeoffs.

Built on top of Notion as the operational interface, with a FastAPI backend deployed on Railway.

---

## How It Works

```
Notion Inbox → Smart Router → Adversarial Dialectic → Synthesized Output → Notion
```

1. Drop an intent into the Notion System Inbox (a decision, a strategy question, an opportunity)
2. The Smart Router classifies it as **Strategic**, **Operational**, or **Reference**
3. Strategic intents trigger the adversarial dialectic — three agents analyze and debate in parallel
4. A synthesis layer combines their outputs into a structured recommendation with risk flags
5. The result writes back to Notion with scenario options and confidence levels

## The Three Agents

| Persona | Cognitive Profile | Focus |
|---|---|---|
| **Entrepreneur** | Growth-maximizing | Revenue potential, scalability, speed to market, moats |
| **Quant** | Probabilistic | Expected value, downside protection, Sharpe equivalent, Kelly sizing |
| **Auditor** | Risk/ethics | Mission alignment, legal exposure, long-term reputation, governance |

Each agent produces 3 scenario options with explicit reasoning. The synthesis layer identifies consensus, surfaces disagreements, and flags dominated strategies.

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (async, Python 3.11) |
| AI | Claude Sonnet / Haiku via Anthropic API |
| Database / Interface | Notion (10 connected databases) |
| Workers | Async background poller (2-minute cycle) |
| Auth / Security | Rate limiting, CORS, input sanitization |
| Infra | Docker · Railway (production) |
| Observability | Loguru structured logging · Sentry (WIP) |

## Quickstart

**Prerequisites:** Python 3.11+, a [Notion integration](https://www.notion.so/my-integrations), an [Anthropic API key](https://console.anthropic.com).

```bash
git clone https://github.com/rippere/executive-mind-matrix
cd executive-mind-matrix

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in: ANTHROPIC_API_KEY, NOTION_API_KEY, database IDs

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or with Docker:

```bash
docker build -t emm . && docker run -p 8000:8000 --env-file .env emm
```

Trigger a manual poll:
```bash
curl -X POST http://localhost:8000/trigger-poll
```

Health check:
```bash
curl http://localhost:8000/health
```

## Notion Database Schema

The system connects to 10 Notion databases:

- `DB_System_Inbox` — inbound intents, the entry point
- `DB_Executive_Intents` — routed strategic items with dialectic outputs
- `DB_Action_Pipes` — operational tasks
- `DB_Agent_Registry` — agent persona configuration
- `DB_Execution_Log` — full audit trail of every agent run
- `DB_Training_Data` — user feedback on AI recommendations for fine-tuning
- `DB_Tasks`, `DB_Projects`, `DB_Areas`, `DB_Nodes` — knowledge management layer

## Real-World Use

I built this to run decision-making for the [Triangle Fraternity WSU chapter](https://en.wikipedia.org/wiki/Triangle_Fraternity) — a 60+ member organization I founded. Strategic planning, recruitment triage, and operational decisions route through this system before executive board discussion.

## Roadmap

- [ ] Upgrade to Claude Sonnet for primary analysis (currently Haiku)
- [ ] Prometheus + Grafana observability
- [ ] Training data settlement pipeline for fine-tuning
- [ ] Slack / Telegram notification layer
