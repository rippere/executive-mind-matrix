# Executive Mind Matrix

AI-powered decision intelligence system with adversarial agent dialectics.

---

## 🚦 CURRENT SETUP STATUS

**Last Updated**: 2026-02-17

### ✅ Completed Steps
1. ✅ Environment file (.env) configured with all API keys and database IDs
2. ✅ Virtual environment created and dependencies installed
3. ✅ **Deployed to Railway** — live at `https://web-production-3d888.up.railway.app`
4. ✅ Health check passing — all systems operational
5. ✅ All 10 Notion databases connected and verified
   - ✅ DB_System_Inbox
   - ✅ DB_Executive_Intents
   - ✅ DB_Action_Pipes
   - ✅ DB_Agent_Registry
   - ✅ DB_Execution_Log
   - ✅ DB_Training_Data
   - ✅ DB_Tasks
   - ✅ DB_Projects
   - ✅ DB_Areas
   - ✅ DB_Nodes
6. ✅ Poller running (2-minute cycle, picks up items with no status set)
7. ✅ All three triage routes operational:
   - ✅ Strategic → Executive Intents (with agent analysis)
   - ✅ Operational → Tasks (with inbox writeback)
   - ✅ Reference → Knowledge Nodes (with inbox writeback)
8. ✅ System Inbox writeback working — `Triage_Destination`, `Routed_to_Intent`, `Routed_to_Task`, `Routed_to_Node` all populated after processing

### 📍 Current State: Production Live

The system is fully deployed and operational. To trigger a manual poll:
```bash
curl -X POST https://web-production-3d888.up.railway.app/trigger-poll
```

To check system health:
```bash
curl https://web-production-3d888.up.railway.app/health
```

### ⏭️ Next Steps
- [ ] Upgrade Anthropic model from `claude-3-haiku` to Claude Sonnet for better analysis quality
- [ ] Deploy `main_enhanced.py` (Sentry, Prometheus metrics, security middleware)
- [ ] Set up Prometheus + Grafana monitoring
- [ ] Collect training data settlements for fine-tuning pipeline
- [ ] Configure production environment variables

---

## Phase 1 Features

### 1. **Async Notion Poller** (2-minute cycle)
- Monitors `DB_System_Inbox` for pending intents
- **Three-way classification and routing**:
  - **Strategic** → Creates Executive Intents
  - **Operational** → Creates Tasks in DB_Tasks
  - **Reference** → Creates Knowledge Nodes in DB_Nodes
- Non-blocking concurrent processing
- Status tracking: Unprocessed → Processing → Triaged_to_Intent/Task/Node

### 2. **Operational Task Creation**
- Automatically creates actionable tasks from operational intents
- Rich context with callouts and formatting
- Bidirectional linking to source System Inbox entry
- Audit logging to Execution Log
- Auto-marked as auto-generated for tracking

### 3. **Knowledge Node Creation**
- AI-powered concept extraction from reference content
- Automatic node creation/finding in DB_Nodes
- Auto-tagging with semantic categories
- Bidirectional linking with System Inbox
- Audit logging to Execution Log

### 4. **Diff Logger** (Training Data Asset)
- Captures delta between AI suggestions and human edits
- Calculates acceptance rates for continuous learning
- Dual storage: Notion + JSON logs

### 5. **Property Validation Logging**
- Logs all property additions to `logs/property_changes.jsonl`
- Structured JSONL format with ISO timestamps
- Prevents redundant property creation
- Enables schema governance analysis

### 6. **Adversarial Agent Router**
- **The Entrepreneur**: Growth-focused, revenue-oriented
- **The Quant**: Risk-adjusted, mathematical analysis
- **The Auditor**: Compliance, ethics, governance
- **Dialectic Flow**: Synthesizes competing perspectives

### 7. **FastAPI REST API**
- Health checks and system status
- Manual triggers for testing and override
- Settlement logging endpoint
- Agent performance metrics

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     FastAPI Application (2min cycle)               │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Notion Poller    │  │Agent Router  │  │DiffLogger/Validation │ │
│  │(2 min poll)      │  │ (Dialectic)  │  │(Training/Audit)      │ │
│  └────────┬─────────┘  └──────┬───────┘  └──────────┬───────────┘ │
└───────────┼────────────────────┼──────────────────────┼─────────────┘
            │                    │                      │
     ┌──────┴───────────┐        │            ┌─────────┴──────┐
     │                  │        │            │                │
     ▼                  ▼        │            ▼                ▼
┌─────────────┐  ┌────────────┐ │     ┌──────────────┐  ┌──────────┐
│ClassifyIntent   │Route Task  │ │     │Task Creation │  │Property  │
│(Strategic)  │  │(Operational)     │  │Creation      │  │Logging   │
│(Operational)│  │(Reference) │ │     │              │  │          │
│(Reference)  │  │            │ │     │              │  │          │
└──┬────┬─────┘  └┬───────┬───┘ │     └──────────────┘  └──────────┘
   │    │        │       │      │
   ▼    ▼        ▼       ▼      ▼
┌────────────────────────────────────────────────────────────┐
│              Notion Databases (7+ connected)               │
│ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐        │
│ │ System  │ │Executive │ │  Tasks  │ │  Nodes   │        │
│ │ Inbox   │ │Intents   │ │         │ │(Knowledge)        │
│ └─────────┘ └──────────┘ └─────────┘ └──────────┘        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│ │Action    │ │Training  │ │Execution │                   │
│ │Pipes     │ │Data      │ │Log       │                   │
│ └──────────┘ └──────────┘ └──────────┘                   │
└────────────────────────────────────────────────────────────┘
```

**Phase 1 Data Flow:**
```
System Inbox Entry (Unprocessed)
    ↓
    Classify Intent (Strategic/Operational/Reference)
    ├─ STRATEGIC → Executive Intents + Agent Router
    ├─ OPERATIONAL → DB_Tasks + Rich Context + Audit Log
    └─ REFERENCE → DB_Nodes + Concepts + Categories + Audit Log
    ↓
Update Status (Triaged_to_Intent/Task/Node)
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
- **Polling Service** (lines 1-61): Async 2-minute polling loop with retry logic
- **Intent Fetching** (lines 62-85): Queries System Inbox for unprocessed items
- **Intent Processing** (lines 87-249): Routes based on classification
  - **Strategic Route** (lines 109-120): Uses workflow integration
  - **Operational Route** (lines 121-173): Creates DB_Tasks with context
  - **Reference Route** (lines 175-240): Creates DB_Nodes with concepts
- **Audit Methods**:
  - `_add_operational_task_context()`: Rich formatting for tasks
  - `_log_task_creation()`: Execution Log for task creation
  - `_log_knowledge_node_creation()`: Execution Log for node creation

### AgentRouter (`app/agent_router.py`)
- **Intent Classification**: Strategic vs Operational vs Reference
- **Single Agent Analysis**: Route to specific persona
- **Dialectic Flow**: Run Growth + Risk agents, synthesize output
- **Personas**:
  - The Entrepreneur: Growth, revenue, scalability
  - The Quant: Risk-adjusted returns, math analysis
  - The Auditor: Governance, ethics, compliance

### DiffLogger (`app/diff_logger.py`)
- Compare original AI plan vs final human-edited plan
- Calculate acceptance rate (alignment metric)
- Save to Notion `DB_Training_Data` + JSON log
- Query metrics for agent performance analysis

### PropertyValidator (`app/property_validator.py`)
- **Pre-flight Checks** (lines 20-85): Validates before property creation
- **Redundancy Detection**:
  - Exact name matching
  - Fuzzy name matching
  - Semantic overlap detection
- **Audit Logging** (lines 149-186): JSONL format with ISO timestamps
  - Log file: `logs/property_changes.jsonl`
  - Non-blocking (doesn't fail property creation)

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

**Phase 1 Deployment:**
- [x] Operational Task Creation - Implemented
- [x] Knowledge Node Creation - Implemented
- [x] Property Validation Logging - Implemented
- [x] Audit trail for all operations
- [ ] End-to-end testing (all three routes)
- [ ] Deploy to Railway for 24/7 operation
- [ ] Monitor execution and property logs

**Production Operations:**
- [ ] Set `ENVIRONMENT=production` in Railway
- [ ] Configure `LOG_LEVEL=WARNING` for production
- [ ] Set up Railway metrics and alerts
- [ ] Add Sentry or error tracking
- [ ] Configure Notion database backups
- [ ] Set up monitoring for polling failures
- [ ] Implement rate limiting for API endpoints
- [ ] Monitor logs/property_changes.jsonl for schema evolution
- [ ] Review Execution Log regularly for audit trail

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
