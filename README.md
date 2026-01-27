# Executive Mind Matrix

AI-powered decision intelligence system with adversarial agent dialectics.

---

## 🚦 CURRENT SETUP STATUS

**Last Updated**: 2026-01-15 14:22

### ✅ Completed Steps
1. ✅ Environment file (.env) configured with all API keys and database IDs
2. ✅ Virtual environment created and dependencies installed
3. ✅ FastAPI application running successfully on http://0.0.0.0:8000
4. ✅ Health check passing - all systems operational
5. ✅ All 6 Notion databases connected to integration
   - ✅ DB_System_Inbox (ID: 2dcc88542aed80d0a1cee56edfbbe2ee)
   - ✅ DB_Executive_Intents (ID: 2dcc88542aed802880d9e98d8a7be73b)
   - ✅ DB_Action_Pipes (ID: 2dcc88542aed807abce7cdcf95bdae73)
   - ✅ DB_Agent_Registry (ID: 2dcc88542aed80f2acd3e5b1dd01dde7)
   - ✅ DB_Execution_Log (ID: 2dcc88542aed8018ad49daf21cd2044c)
   - ✅ DB_Training_Data (ID: 850be0fc91bf42878a38d8f6f81a55c3)
6. ✅ System health verified - all databases configured correctly
7. ✅ Poller running (2-minute cycle active)

### 🔄 NEXT: End-to-End Testing
**📍 YOU ARE HERE** → Ready to test the complete workflow

**When you have network access, do this**:

**Step 1: Create Test Intent in Notion**
1. Open your **System Inbox** database in Notion
2. Create a new entry:
   - **Title**: "Test Intent: Should I invest in index funds?"
   - **Status**: "Unprocessed" (or your equivalent)
   - **Description**: "I have $5k to invest. Should I go with VTI or individual stocks?"

**Step 2: Trigger the System**
```bash
# Option A: Wait 2 minutes for automatic polling
tail -f logs/app.log

# Option B: Trigger immediately
curl -X POST http://localhost:8000/trigger-poll
```

**Step 3: Verify the Flow**
- [ ] Intent picked up from System Inbox
- [ ] Status changed: "Unprocessed" → "Processing" → "Triaged_to_Intent"
- [ ] New entry created in **Executive Intents** database
- [ ] (Optional) Run dialectic analysis: `curl -X POST http://localhost:8000/dialectic/{INTENT_ID}`

**Step 4: After Testing**
- [ ] Review the AI-generated analysis in Executive Intents
- [ ] Test the training data logger by editing an AI suggestion
- [ ] (Optional) Deploy to Railway for 24/7 operation

### ⏭️ Future Steps
- [ ] Deploy to Railway (optional)
- [ ] Set up monitoring and alerts
- [ ] Configure production environment variables

---

## Features

### 1. **Async Notion Poller** (2-minute cycle)
- Monitors `DB_System_Inbox` for pending intents
- Non-blocking concurrent processing
- Automatic classification and routing

### 2. **Diff Logger** (Training Data Asset)
- Captures delta between AI suggestions and human edits
- Calculates acceptance rates for continuous learning
- Dual storage: Notion + JSON logs

### 3. **Adversarial Agent Router**
- **The Entrepreneur**: Growth-focused, revenue-oriented
- **The Quant**: Risk-adjusted, mathematical analysis
- **The Auditor**: Compliance, ethics, governance
- **Dialectic Flow**: Synthesizes competing perspectives

### 4. **FastAPI REST API**
- Health checks and metrics
- Manual triggers for testing
- Settlement logging endpoint

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Notion Poller │  │ Agent Router │  │ Diff Logger  │ │
│  │  (2 min loop) │  │  (Dialectic) │  │  (Training)  │ │
│  └───────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└──────────┼──────────────────┼──────────────────┼─────────┘
           │                  │                  │
           ▼                  ▼                  ▼
    ┌──────────────────────────────────────────────────┐
    │              Notion Databases                     │
    │  System Inbox │ Intents │ Actions │ Training     │
    └──────────────────────────────────────────────────┘
```

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Required variables:
- `NOTION_API_KEY`: Notion integration token
- `ANTHROPIC_API_KEY`: Claude API key
- Database IDs for all 6 Notion databases

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Or with uvicorn
uvicorn main:app --reload
```

### 3. Docker

```bash
# Build image
docker build -t executive-mind-matrix .

# Run container
docker run -p 8000:8000 --env-file .env executive-mind-matrix
```

### 4. Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set NOTION_API_KEY=secret_xxx
railway variables set ANTHROPIC_API_KEY=sk-ant-xxx
# ... (add all other variables)

# Deploy
railway up
```

Or use the Railway dashboard:
1. Connect your GitHub repo
2. Railway auto-detects `Dockerfile`
3. Add environment variables in dashboard
4. Deploy

## API Endpoints

### Health Check
```bash
GET /
GET /health
```

### Manual Triggers
```bash
# Trigger poll cycle
POST /trigger-poll

# Analyze specific intent
POST /analyze-intent/{intent_id}?agent=The%20Entrepreneur

# Run dialectic flow
POST /dialectic/{intent_id}
```

### Training Data
```bash
# Log settlement diff
POST /log-settlement
Body: {
  "intent_id": "xxx",
  "original_plan": {...},
  "final_plan": {...}
}

# Get agent metrics
GET /metrics/agent/{agent_name}
```

## Key Components

### NotionPoller (`app/notion_poller.py`)
- Async polling every 2 minutes
- Fetches intents with `Status == "Unprocessed"`
- Updates status: `Unprocessed` → `Processing` → `Triaged_to_Intent`
- Creates Executive Intents in Notion

### AgentRouter (`app/agent_router.py`)
- **Intent Classification**: Strategic vs Operational vs Reference
- **Single Agent Analysis**: Route to specific persona
- **Dialectic Flow**: Run Growth + Risk agents, synthesize output

### DiffLogger (`app/diff_logger.py`)
- Compare original AI plan vs final human-edited plan
- Calculate acceptance rate (alignment metric)
- Save to Notion `DB_Training_Data` + JSON log
- Query metrics for agent performance analysis

## Dialectic Flow Example

```python
# Input: "Should I invest $5k in VTI or Bitcoin?"

# Step 1: Growth Agent (Entrepreneur)
# → Recommends: 70% BTC, 30% alt-coins (high upside)

# Step 2: Risk Agent (Auditor)
# → Recommends: 100% VTI (governance, stability)

# Step 3: Synthesis
# → Balanced: 80% VTI, 20% BTC
# → Conflict: Growth wants risk, Auditor wants safety
# → Path: Index fund base + small crypto allocation
```

## Training Data Asset

Every time a user edits an AI-generated plan, the system captures:

```json
{
  "intent_id": "abc123",
  "original_plan": { "tasks": ["A", "B", "C"] },
  "final_plan": { "tasks": ["A", "B_modified", "D"] },
  "modifications": [
    "Modified task B",
    "Removed task C",
    "Added task D"
  ],
  "acceptance_rate": 0.67
}
```

This enables:
- Fine-tuning agent prompts
- A/B testing different personas
- Understanding user preferences over time

## Monitoring

```bash
# View logs
tail -f logs/app.log

# Check poller status
curl http://localhost:8000/health

# Get agent performance
curl http://localhost:8000/metrics/agent/The%20Entrepreneur
```

## Production Checklist

- [ ] Set `ENVIRONMENT=production` in Railway
- [ ] Configure `LOG_LEVEL=WARNING` for production
- [ ] Set up Railway metrics and alerts
- [ ] Add Sentry or error tracking
- [ ] Configure Notion database backups
- [ ] Set up monitoring for polling failures
- [ ] Implement rate limiting for API endpoints

## Model Configuration

**Current Model**: `claude-3-haiku-20240307`
- Fast and cost-effective for classification and analysis
- Works well for single-agent analysis
- Dialectic flow may have variable results with complex prompts

**To Upgrade** (requires API key with access):
- `claude-3-5-sonnet-20241022` - Better for complex reasoning and dialectic analysis
- Update `.env`: `ANTHROPIC_MODEL=claude-3-5-sonnet-20241022`

## Cost Estimates

**Anthropic API** (Haiku):
- ~10 intents/day × 2k tokens = ~$1-2/month

**Anthropic API** (Sonnet upgrade):
- ~10 intents/day × 4k tokens = ~$5-10/month

**Railway**:
- Starter plan: $5/month (512MB RAM, sufficient for this workload)

**Total**: ~$6-12/month (Haiku) or ~$15-20/month (Sonnet)

## License

MIT
