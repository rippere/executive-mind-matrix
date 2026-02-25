# Executive Mind Matrix - Command Reference

**Quick reference for all commands, endpoints, and operations**

Production URL: `https://web-production-3d888.up.railway.app`

---

## Table of Contents

1. [API Endpoints](#api-endpoints)
   - [Health & Status](#health--status)
   - [Workflow Operations](#workflow-operations)
   - [Analytics & Training Data](#analytics--training-data)
   - [Command Center](#command-center)
   - [Manual Triggers](#manual-triggers)
2. [Development Commands](#development-commands)
3. [Docker Commands](#docker-commands)
4. [Git & Deployment](#git--deployment)
5. [Notion Operations](#notion-operations)
6. [Monitoring & Observability](#monitoring--observability)
7. [Troubleshooting](#troubleshooting)

---

## API Endpoints

### Health & Status

#### Get Service Status
```bash
GET /
```

**What it does:** Returns basic service information and poller status

**Example:**
```bash
curl https://web-production-3d888.up.railway.app/
```

**Response:**
```json
{
  "status": "running",
  "service": "Executive Mind Matrix",
  "version": "1.0.0",
  "environment": "production",
  "poller_running": true
}
```

---

#### Get Detailed Health Check
```bash
GET /health
```

**What it does:** Returns detailed health status including database connections and poller state

**Example:**
```bash
curl https://web-production-3d888.up.railway.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "poller_active": true,
  "polling_interval": 120,
  "databases_configured": {
    "system_inbox": true,
    "executive_intents": true,
    "action_pipes": true,
    "agent_registry": true,
    "execution_log": true,
    "training_data": true,
    "tasks": true,
    "projects": true,
    "areas": true,
    "nodes": true
  }
}
```

**When to use:** Regular health checks, deployment verification, debugging connection issues

---

### Workflow Operations

#### Manually Trigger Poll Cycle
```bash
POST /trigger-poll
```

**What it does:** Forces an immediate poll of the System Inbox (useful for testing)

**Example:**
```bash
curl -X POST https://web-production-3d888.up.railway.app/trigger-poll
```

**Response:**
```json
{
  "status": "success",
  "message": "Poll cycle completed"
}
```

**When to use:** Testing triage logic, forcing immediate processing of new inbox items

---

#### Run Dialectic Analysis
```bash
POST /dialectic/{intent_id}
```

**What it does:** Runs adversarial dialectic analysis (Growth + Risk agents) on a strategic intent and creates an Action Pipe with recommendations

**Required Parameters:**
- `intent_id` (path): The Notion page ID of the Executive Intent

**Example:**
```bash
curl -X POST https://web-production-3d888.up.railway.app/dialectic/abc123-def456-ghi789
```

**Response:**
```json
{
  "status": "success",
  "intent_id": "abc123-def456-ghi789",
  "action_id": "xyz789-uvw456-rst123",
  "message": "Dialectic analysis complete and Action Pipe created",
  "synthesis": "Balanced approach combining growth with risk mitigation...",
  "recommended_path": "Proceed with phased rollout...",
  "conflict_points": ["Growth wants rapid expansion, Risk prefers validation"],
  "growth_recommendation": "Option 2",
  "risk_recommendation": "Option 1"
}
```

**When to use:** Get multi-perspective analysis on strategic decisions, generate Action Pipes with AI recommendations

---

#### Create Action from Intent
```bash
POST /intent/{intent_id}/create-action
```

**What it does:** Creates an Action Pipe linked to an Executive Intent

**Required Parameters:**
- `intent_id` (path): The Notion page ID of the Executive Intent

**Optional Query Parameters:**
- `action_title` (string): Title for the action (default: "Action from Intent")
- `action_description` (string): Description text

**Example:**
```bash
curl -X POST "https://web-production-3d888.up.railway.app/intent/abc123/create-action?action_title=Launch%20Campaign&action_description=Execute%20Q1%20marketing%20strategy"
```

**Response:**
```json
{
  "status": "success",
  "intent_id": "abc123-def456-ghi789",
  "action_id": "xyz789-uvw456-rst123",
  "message": "Action Pipe created and linked to Intent",
  "url": "https://notion.so/xyz789uvw456rst123"
}
```

**When to use:** Manually create actions without running full dialectic analysis

---

#### Approve Action
```bash
POST /action/{action_id}/approve
```

**What it does:** Approves an Action Pipe, sets approval timestamp, and logs training data diff

**Required Parameters:**
- `action_id` (path): The Notion page ID of the Action Pipe

**Example:**
```bash
curl -X POST https://web-production-3d888.up.railway.app/action/xyz789/approve
```

**Response:**
```json
{
  "status": "success",
  "action_id": "xyz789-uvw456-rst123",
  "message": "Action approved successfully"
}
```

**When to use:** Approve actions and automatically capture training data for fine-tuning

---

#### Spawn Tasks from Action
```bash
POST /action/{action_id}/spawn-tasks
```

**What it does:** Creates tasks and a project from an approved Action Pipe's task template

**Required Parameters:**
- `action_id` (path): The Notion page ID of the Action Pipe

**Example:**
```bash
curl -X POST https://web-production-3d888.up.railway.app/action/xyz789/spawn-tasks
```

**Response:**
```json
{
  "status": "success",
  "action_id": "xyz789-uvw456-rst123",
  "intent_id": "abc123-def456-ghi789",
  "tasks_created": 5,
  "project_created": true,
  "project_id": "proj-123",
  "task_ids": ["task-1", "task-2", "task-3", "task-4", "task-5"],
  "message": "Created 5 tasks and 1 project"
}
```

**When to use:** Convert approved actions into executable tasks

---

### Analytics & Training Data

#### Get Agent Performance Summary
```bash
GET /analytics/agents/summary?time_range={7d|30d|90d|all}
```

**What it does:** Returns performance metrics for all agents

**Query Parameters:**
- `time_range` (optional): 7d, 30d, 90d, or all (default: 30d)

**Example:**
```bash
curl "https://web-production-3d888.up.railway.app/analytics/agents/summary?time_range=30d"
```

**Response:**
```json
{
  "status": "success",
  "time_range": "30d",
  "agents": {
    "The Entrepreneur": {
      "total_analyses": 45,
      "avg_acceptance_rate": 0.82,
      "total_tokens": 125000,
      "trend": "improving"
    },
    "The Auditor": {
      "total_analyses": 38,
      "avg_acceptance_rate": 0.75,
      "total_tokens": 98000,
      "trend": "stable"
    }
  }
}
```

**When to use:** Review agent performance, identify which agents need prompt tuning

---

#### Get Agent Improvement Opportunities
```bash
GET /analytics/agent/{agent_name}/improvements?time_range={7d|30d|90d|all}
```

**What it does:** Identifies areas where a specific agent's prompts can be improved

**Required Parameters:**
- `agent_name` (path): "The Entrepreneur", "The Quant", or "The Auditor"

**Query Parameters:**
- `time_range` (optional): 7d, 30d, 90d, or all (default: 30d)

**Example:**
```bash
curl "https://web-production-3d888.up.railway.app/analytics/agent/The%20Entrepreneur/improvements?time_range=30d"
```

**Response:**
```json
{
  "status": "success",
  "agent": "The Entrepreneur",
  "time_range": "30d",
  "avg_acceptance_rate": 0.82,
  "common_edits": [
    "Users often add more conservative timelines",
    "Resource estimates frequently adjusted downward"
  ],
  "low_acceptance_intents": [
    {
      "intent_id": "abc123",
      "acceptance_rate": 0.45,
      "category": "product_launch"
    }
  ]
}
```

**When to use:** Identify patterns in user edits, prioritize prompt improvements

---

#### Compare Agents
```bash
GET /analytics/compare?agent_a={name}&agent_b={name}&time_range={7d|30d|90d|all}
```

**What it does:** Head-to-head comparison of two agents

**Query Parameters:**
- `agent_a` (required): First agent name
- `agent_b` (required): Second agent name
- `time_range` (optional): 7d, 30d, 90d, or all (default: 30d)

**Example:**
```bash
curl "https://web-production-3d888.up.railway.app/analytics/compare?agent_a=The%20Entrepreneur&agent_b=The%20Auditor&time_range=30d"
```

**Response:**
```json
{
  "status": "success",
  "comparison": {
    "agent_a": {
      "name": "The Entrepreneur",
      "acceptance_rate": 0.82,
      "total_analyses": 45
    },
    "agent_b": {
      "name": "The Auditor",
      "acceptance_rate": 0.75,
      "total_analyses": 38
    },
    "winner": "The Entrepreneur",
    "difference": 0.07
  }
}
```

**When to use:** Compare agent effectiveness, decide which agent to use for similar intents

---

#### Export Fine-Tuning Data
```bash
POST /analytics/export/fine-tuning
```

**What it does:** Exports training data as JSONL for Claude fine-tuning

**Query Parameters:**
- `min_acceptance_rate` (optional): Filter by acceptance rate 0-1 (default: 0.7)
- `agent_name` (optional): Filter to specific agent
- `time_range` (optional): 7d, 30d, 90d, or all (default: all)
- `output_path` (optional): File path (default: data/finetuning_export.jsonl)

**Example:**
```bash
curl -X POST "https://web-production-3d888.up.railway.app/analytics/export/fine-tuning?min_acceptance_rate=0.8&agent_name=The%20Entrepreneur&time_range=all"
```

**Response:**
```json
{
  "status": "success",
  "output_path": "data/finetuning_export.jsonl",
  "examples_exported": 32,
  "avg_acceptance_rate": 0.87,
  "validation_report": {
    "valid_examples": 32,
    "invalid_examples": 0,
    "warnings": []
  }
}
```

**When to use:** Generate training datasets for Claude fine-tuning API

---

#### Log Settlement Diff
```bash
POST /log-settlement
```

**What it does:** Manually log the difference between AI plan and human-edited plan

**Request Body:**
```json
{
  "intent_id": "abc123-def456-ghi789",
  "original_plan": {
    "tasks": ["Task A", "Task B", "Task C"]
  },
  "final_plan": {
    "tasks": ["Task A", "Task B (modified)", "Task D"]
  }
}
```

**Example:**
```bash
curl -X POST https://web-production-3d888.up.railway.app/log-settlement \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id": "abc123",
    "original_plan": {"tasks": ["A", "B", "C"]},
    "final_plan": {"tasks": ["A", "B_modified", "D"]}
  }'
```

**Response:**
```json
{
  "status": "success",
  "intent_id": "abc123-def456-ghi789",
  "modifications": 3,
  "acceptance_rate": "67.0%",
  "timestamp": "2026-02-19T10:30:45Z"
}
```

**When to use:** Manually capture training data (note: automatically captured on approval)

---

### Command Center

#### Setup Command Center
```bash
POST /command-center/setup?force={true|false}
```

**What it does:** One-time setup creating the Command Center page structure with placeholders for linked database views

**Query Parameters:**
- `force` (optional): Set to true to overwrite existing content (default: false)

**Example:**
```bash
# First time setup
curl -X POST https://web-production-3d888.up.railway.app/command-center/setup

# Force overwrite (WARNING: deletes existing content)
curl -X POST "https://web-production-3d888.up.railway.app/command-center/setup?force=true"
```

**Response:**
```json
{
  "status": "success",
  "message": "Command Center structure created with placeholders",
  "url": "https://notion.so/abc123def456ghi789",
  "next_steps": "Open the Command Center and add linked database views as instructed"
}
```

**When to use:** Initial setup or rebuilding Command Center structure

---

#### Update Command Center Metrics
```bash
POST /command-center/update-metrics
```

**What it does:** Refreshes only the metrics callout (database views update automatically)

**Example:**
```bash
curl -X POST https://web-production-3d888.up.railway.app/command-center/update-metrics
```

**Response:**
```json
{
  "status": "success",
  "message": "Metrics updated",
  "metrics": {
    "total_intents": 45,
    "pending_actions": 12,
    "active_tasks": 38,
    "completion_rate": 0.73
  }
}
```

**When to use:** Periodically refresh metrics without rebuilding entire page

---

### Manual Triggers

#### Analyze Intent with Specific Agent
```bash
POST /analyze-intent/{intent_id}
```

**What it does:** Manually trigger single-agent analysis for a specific intent

**Required Parameters:**
- `intent_id` (path): The Notion page ID of the Executive Intent
- `agent` (query): The agent persona to use

**Query Parameters:**
- `agent`: "The Entrepreneur", "The Quant", or "The Auditor"

**Example:**
```bash
curl -X POST "https://web-production-3d888.up.railway.app/analyze-intent/abc123?agent=The%20Quant"
```

**Response:**
```json
{
  "status": "queued",
  "intent_id": "abc123-def456-ghi789",
  "agent": "The Quant",
  "message": "Analysis queued in background"
}
```

**When to use:** Override automatic agent assignment, test specific agent personas

---

#### Get Agent Metrics
```bash
GET /metrics/agent/{agent_name}
```

**What it does:** Get performance metrics for a specific agent from training data

**Required Parameters:**
- `agent_name` (path): The agent name

**Example:**
```bash
curl https://web-production-3d888.up.railway.app/metrics/agent/The%20Entrepreneur
```

**Response:**
```json
{
  "status": "success",
  "agent": "The Entrepreneur",
  "metrics": {
    "total_analyses": 45,
    "average_acceptance_rate": 0.82,
    "total_tokens_used": 125000,
    "recent_trend": "improving"
  }
}
```

**When to use:** Quick check on single agent performance

---

## Development Commands

### Local Development

#### Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

#### Run Application Locally
```bash
# Standard run
python main_enhanced.py

# Or with uvicorn directly (with auto-reload)
uvicorn main_enhanced:app --reload --host 0.0.0.0 --port 8000

# With specific log level
uvicorn main_enhanced:app --reload --log-level debug
```

**Access locally at:** `http://localhost:8000`

---

#### Run Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_notion_poller.py

# Run with verbose output
pytest -v
```

---

#### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env  # or vim, code, etc.

# Validate environment variables
python scripts/validate-env.py

# Test connections
python scripts/test-connections.py
```

---

## Docker Commands

### Standard Docker

#### Build Image
```bash
# Development build
docker build -t executive-mind-matrix .

# Production build (optimized)
docker build -f Dockerfile.production -t executive-mind-matrix:prod .

# Railway build
docker build -f Dockerfile.railway -t executive-mind-matrix:railway .
```

---

#### Run Container
```bash
# Run with environment file
docker run -p 8000:8000 --env-file .env executive-mind-matrix

# Run in background
docker run -d -p 8000:8000 --env-file .env executive-mind-matrix

# Run with custom name
docker run -d -p 8000:8000 --name emm --env-file .env executive-mind-matrix

# View logs
docker logs emm

# Follow logs
docker logs -f emm

# Stop container
docker stop emm

# Remove container
docker rm emm
```

---

### Docker Compose

#### Run with Docker Compose
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

---

## Git & Deployment

### Git Workflow

#### Commit Changes
```bash
# Check status
git status

# View changes
git diff

# Add files
git add .

# Commit with message
git commit -m "feat: add new feature"

# Push to remote
git push origin main
```

---

#### Branch Management
```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

---

### Railway Deployment

#### Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project (first time)
railway init

# Link to existing project
railway link

# Set environment variables (from .env file)
railway variables set NOTION_API_KEY=secret_xxx
railway variables set ANTHROPIC_API_KEY=sk-ant-xxx
# ... (repeat for all variables)

# Or upload from file
railway variables set --file .env

# Deploy
railway up

# View logs
railway logs

# Open in browser
railway open
```

---

#### Using Railway Dashboard

1. **Connect Repository:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment Variables:**
   - Go to service settings
   - Click "Variables" tab
   - Add all variables from `.env`
   - **Never commit `.env` to git!**

3. **Configure Deployment:**
   - Railway auto-detects `Dockerfile`
   - Or specify in `railway.json`
   - Deployments trigger automatically on push to main

4. **Generate Domain:**
   - Go to "Settings" tab
   - Under "Domains", click "Generate Domain"
   - Or add custom domain

---

#### Deployment Checklist

```bash
# Before deploying
python scripts/validate-env.py
bash scripts/pre-deploy-check.sh
pytest

# Deploy
git add .
git commit -m "deploy: ready for production"
git push origin main

# After deploying
curl https://web-production-3d888.up.railway.app/health
python scripts/smoke-test.py https://web-production-3d888.up.railway.app
```

---

## Notion Operations

### Database Overview

**All 10 Databases:**

| Database | Purpose | Key Properties |
|----------|---------|----------------|
| **System Inbox** | Entry point for all requests | Input_Title, Content, Status, Triage_Destination |
| **Executive Intents** | Strategic decisions | Name, Status, Risk_Level, Projected_Impact, Agent_Persona |
| **Action Pipes** | Decision execution plans | Action_Title, Approval_Status, Recommended_Option, Intent (relation) |
| **Agent Registry** | AI agent definitions | Agent_Name, Persona_Type, Prompt_Template |
| **Execution Log** | Audit trail | Log_Entry_Title, Action_Taken, Decision_Date, Intent (relation) |
| **Training Data** | Fine-tuning dataset | Intent (relation), Agent_Name, Acceptance_Rate, User_Modifications |
| **Tasks** | Operational todos | Task_Title, Status, Priority, Intent (relation), Project (relation) |
| **Projects** | Task groupings | Project_Name, Status, Intent (relation), Area (relation) |
| **Areas** | Life/work domains | Area_Name, Description, Icon |
| **Nodes** | Knowledge graph | Node_Title, Category, Tags, Related_Intents (relation) |

---

### Key Relations

**How databases link together:**

```
System Inbox
  └─> Routed_to_Intent ──> Executive Intents
  └─> Routed_to_Task ──> Tasks
  └─> Routed_to_Node ──> Nodes

Executive Intents
  ├─> Agent_Persona ──> Agent Registry
  ├─> Source ──> System Inbox
  ├─> Area ──> Areas
  ├─> Related_Actions ──> Action Pipes
  └─> Related_Knowledge ──> Nodes

Action Pipes
  ├─> Intent ──> Executive Intents
  └─> Agent ──> Agent Registry

Tasks
  ├─> Intent ──> Executive Intents
  ├─> Project ──> Projects
  └─> Area ──> Areas

Projects
  ├─> Intent ──> Executive Intents
  └─> Area ──> Areas

Training Data
  ├─> Intent ──> Executive Intents
  └─> Agent relation via Intent

Execution Log
  └─> Intent ──> Executive Intents
```

---

### Finding Database IDs

**Method 1: From Database URL**
1. Open database as full page in Notion
2. Copy URL: `https://notion.so/workspace/DATABASE_ID?v=...`
3. The `DATABASE_ID` is the 32-character hex string

**Example URL:**
```
https://notion.so/myworkspace/abc123def456ghi789jkl012mno345pq?v=xyz789
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                             This is your database ID
```

**Method 2: Using Script**
```bash
python scripts/audit_database_properties.py
```

---

### Manual Schema Operations

**When needed:** Rarely - schema is mostly automated

**Add Property to Database:**
```bash
# Use Notion UI to add properties
# Or use audit script to check schema
python scripts/audit_database_properties.py

# Check property logs
tail -f logs/property_changes.jsonl
```

**Common Manual Additions:**
- Adding new agent personas to Agent Registry
- Creating new Areas
- Setting up initial Node categories

---

## Monitoring & Observability

### Prometheus Metrics

#### Access Metrics Endpoint
```bash
# View raw metrics
curl https://web-production-3d888.up.railway.app/metrics
```

**Available Metrics:**
- `http_requests_total` - Total HTTP requests by endpoint
- `http_request_duration_seconds` - Request latency histogram
- `notion_api_requests_total` - Notion API call counter
- `anthropic_api_requests_total` - Claude API call counter
- `anthropic_tokens_used_total` - Token usage tracking
- `poll_cycles_total` - Completed poll cycles
- `poller_status` - Poller active/inactive (gauge)
- `errors_total` - Error counter by type and component

---

#### Configure Prometheus Scraping

**Add to `prometheus.yml`:**
```yaml
scrape_configs:
  - job_name: 'executive-mind-matrix'
    static_configs:
      - targets: ['web-production-3d888.up.railway.app']
    metrics_path: '/metrics'
    scheme: 'https'
    scrape_interval: 30s
```

---

### Sentry Error Tracking

#### Setup Sentry

1. **Create Sentry Project:**
   - Go to [sentry.io](https://sentry.io)
   - Create new project (Python platform)
   - Copy DSN

2. **Configure in Railway:**
   ```bash
   railway variables set SENTRY_DSN=https://xxxx@xxxx.ingest.sentry.io/xxxx
   railway variables set SENTRY_TRACES_SAMPLE_RATE=0.1
   ```

3. **Verify:**
   - Deploy application
   - Check Sentry dashboard for events
   - Errors automatically captured and grouped

---

#### Test Sentry Integration
```bash
# Trigger an error endpoint (if exists)
# Or check Sentry dashboard for errors

# View Sentry events
# Go to: sentry.io > Projects > executive-mind-matrix > Issues
```

---

### Railway Logs

#### View Logs in Dashboard
1. Go to Railway project
2. Click service
3. Click "Deployments" tab
4. Select active deployment
5. View real-time logs

---

#### View Logs via CLI
```bash
# Follow logs
railway logs

# View last 100 lines
railway logs --tail 100

# Filter by level (if JSON logs enabled)
railway logs | grep "ERROR"
```

---

### Health Check Procedures

#### Quick Health Check
```bash
curl https://web-production-3d888.up.railway.app/health
```

**Expected response should show:**
- `status: "healthy"`
- `poller_active: true`
- All databases: `true`

---

#### Full System Check
```bash
# 1. Health endpoint
curl https://web-production-3d888.up.railway.app/health

# 2. Test manual poll
curl -X POST https://web-production-3d888.up.railway.app/trigger-poll

# 3. Check metrics
curl https://web-production-3d888.up.railway.app/metrics | grep poller_status

# 4. Run smoke tests
python scripts/smoke-test.py https://web-production-3d888.up.railway.app
```

---

## Troubleshooting

### Check Poller Status

```bash
# Method 1: Health endpoint
curl https://web-production-3d888.up.railway.app/health | jq '.poller_active'

# Method 2: Metrics endpoint
curl https://web-production-3d888.up.railway.app/metrics | grep poller_status

# Method 3: Railway logs
railway logs | grep "Poll cycle"
```

**Expected output:**
- Health endpoint: `"poller_active": true`
- Metrics: `poller_status 1.0`
- Logs: Regular "Poll cycle completed" messages every 2 minutes

---

### Manually Trigger Poll

```bash
# Force immediate poll
curl -X POST https://web-production-3d888.up.railway.app/trigger-poll

# Check response
# Should return: {"status": "success", "message": "Poll cycle completed"}
```

**When to use:**
- Testing triage logic
- Processing stuck items immediately
- Debugging classification issues

---

### Test Connections

#### Test Notion Connection
```bash
python scripts/test-connections.py

# Or manually
curl https://web-production-3d888.up.railway.app/health | jq '.databases_configured'
```

**All should be `true`**

---

#### Test Anthropic Connection
```bash
# Check recent logs for API calls
railway logs | grep "anthropic"

# Or trigger a test analysis
curl -X POST "https://web-production-3d888.up.railway.app/analyze-intent/TEST_ID?agent=The%20Entrepreneur"
```

---

### Check for Errors

#### View Application Errors
```bash
# Railway logs
railway logs | grep ERROR

# Or check Sentry dashboard
# Go to: sentry.io > Projects > executive-mind-matrix > Issues
```

---

#### Common Error Patterns

**Error: Poller not running**
```bash
# Check environment variables
railway variables

# Verify NOTION_API_KEY and ANTHROPIC_API_KEY are set
# Restart service
railway restart
```

**Error: Database not configured**
```bash
# Check database IDs in environment
railway variables | grep NOTION_DB

# Verify all 10 database IDs are set
# Verify API key has access to databases
```

**Error: Rate limiting**
```bash
# Check rate limit settings
railway variables | grep RATE_LIMIT

# Adjust if needed
railway variables set RATE_LIMIT_PER_MINUTE=120

# Or disable temporarily
railway variables set RATE_LIMIT_ENABLED=false
```

**Error: High latency**
```bash
# Check metrics
curl https://web-production-3d888.up.railway.app/metrics | grep duration

# Check Railway resource usage
railway status

# Consider scaling up or increasing workers
```

---

### Reset Procedures

#### Restart Application
```bash
# Via Railway CLI
railway restart

# Or via Railway dashboard
# Go to service > Settings > Restart
```

---

#### Clear Logs (Local Development)
```bash
# Clear local logs
rm logs/*.log
rm logs/*.jsonl

# Restart application
python main_enhanced.py
```

---

#### Redeploy
```bash
# Force redeploy without code changes
railway up --force

# Or redeploy specific commit
git revert HEAD~1
git push origin main
```

---

## Quick Reference Card

### Most Common Commands

```bash
# Check health
curl https://web-production-3d888.up.railway.app/health

# Force poll
curl -X POST https://web-production-3d888.up.railway.app/trigger-poll

# Run dialectic
curl -X POST https://web-production-3d888.up.railway.app/dialectic/{intent_id}

# Approve action
curl -X POST https://web-production-3d888.up.railway.app/action/{action_id}/approve

# Spawn tasks
curl -X POST https://web-production-3d888.up.railway.app/action/{action_id}/spawn-tasks

# View logs
railway logs

# Deploy
git push origin main
```

---

### Environment Variables Quick List

**Required:**
- `NOTION_API_KEY`
- `ANTHROPIC_API_KEY`
- `NOTION_DB_SYSTEM_INBOX`
- `NOTION_DB_EXECUTIVE_INTENTS`
- `NOTION_DB_ACTION_PIPES`
- `NOTION_DB_AGENT_REGISTRY`
- `NOTION_DB_EXECUTION_LOG`
- `NOTION_DB_TRAINING_DATA`
- `NOTION_DB_TASKS`
- `NOTION_DB_PROJECTS`
- `NOTION_DB_AREAS`
- `NOTION_DB_NODES`

**Optional (Recommended):**
- `SENTRY_DSN`
- `API_KEY`
- `ANTHROPIC_MODEL` (default: claude-3-haiku-20240307)
- `ENVIRONMENT` (default: development)
- `LOG_LEVEL` (default: INFO)

---

## Additional Resources

- **Full Documentation:** `/home/rippere/Projects/executive-mind-matrix/README.md`
- **Deployment Guide:** `/home/rippere/Projects/executive-mind-matrix/DEPLOYMENT_GUIDE.md`
- **API Documentation:** `https://web-production-3d888.up.railway.app/docs`
- **Alternative API Docs:** `https://web-production-3d888.up.railway.app/redoc`

---

**Last Updated:** 2026-02-19
**Version:** 1.0.0
