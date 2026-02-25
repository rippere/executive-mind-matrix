# Executive Mind Matrix - Deployment Guide

Complete step-by-step guide to deploying your own instance of Executive Mind Matrix.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Notion Setup](#notion-setup)
3. [Getting API Keys](#getting-api-keys)
4. [Local Testing](#local-testing)
5. [Railway Deployment](#railway-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)
10. [Maintenance](#maintenance)

---

## Prerequisites

### Required Accounts

- [ ] **Notion** - Free or paid workspace
- [ ] **Anthropic** - API access for Claude (free tier available)
- [ ] **Railway** - Deployment platform (free tier: $5/month credit)
- [ ] **GitHub** - Optional, for easier deployment

### Technical Requirements

- **Time**: 1-2 hours for first-time setup
- **Skill Level**: Basic command-line comfort
- **Cost**: ~$15-20/month ongoing

### Tools You'll Need

- Terminal/command line
- Web browser
- Text editor (VS Code, Sublime, etc.)

---

## Notion Setup

### Step 1: Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it: "Executive Mind Matrix"
4. Associated workspace: Select your workspace
5. Capabilities:
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
6. Click "Submit"
7. **Copy the Integration Token** (starts with `secret_...`)
   - ⚠️ Save this securely - you'll need it as `NOTION_API_KEY`

### Step 2: Create Notion Databases

You need 10 databases. Use these templates:

#### 2.1: System Inbox

**Properties**:
- `Input_Title` (Title)
- `Content` (Text)
- `Source` (Select): Email, Slack, Meeting, Manual, Other
- `Received_Date` (Date)
- `Status` (Select): Unprocessed, Processing, Triaged_to_Intent, Triaged_to_Task, Triaged_to_Node
- `Triage_Destination` (Select): Strategic (Intent), Operational (Task), Reference (Node)
- `Routed_to_Intent` (Relation → Executive Intents)
- `Routed_to_Task` (Relation → Tasks)
- `Routed_to_Node` (Relation → Knowledge Nodes)
- `Related_Nodes` (Relation → Knowledge Nodes)
- `Auto_Tags` (Text)

#### 2.2: Executive Intents

**Properties**:
- `Name` (Title)
- `Description` (Text)
- `Status` (Select): Ready, Analyzed, Approved, Executed
- `Risk_Level` (Select): Low, Medium, High
- `Projected_Impact` (Number): 1-10
- `Priority` (Select): P0, P1, P2
- `Intent ID` (Number)
- `Created_Date` (Date)
- `Due_Date` (Date)
- `Success_Criteria` (Text)
- `Decision_Made` (Text)
- `Conflict_Level` (Select): None - Full Consensus, Low - Minor Disagreement, Medium - Split Opinion, High - Major Conflict
- `Agent_Persona` (Relation → Agent Registry)
- `Source` (Relation → System Inbox)
- `Related_Actions` (Relation → Action Pipes)
- `Area` (Relation → Areas)
- `Related_Knowledge` (Relation → Knowledge Nodes)

#### 2.3: Action Pipes

**Properties**:
- `Action_Title` (Title)
- `Intent` (Relation → Executive Intents)
- `Agent` (Relation → Agent Registry)
- `Recommended_Option` (Select): Option A, Option B, Option C
- `Scenario_Options` (Text)
- `Risk_Assessment` (Text)
- `Required_Resources` (Text)
- `Task_Generation_Template` (Text)
- `Approval_Status` (Select): Pending, Approved, Rejected
- `Consensus` (Checkbox)
- `Approved_Date` (Date)
- `Diff_Logged` (Checkbox)

#### 2.4: Tasks

**Properties**:
- `Name` (Title)
- `Status` (Select): Not started, In progress, Completed
- `Project` (Relation → Projects)
- `Area` (Relation → Areas)
- `Related Intents` (Relation → Executive Intents)
- `Due Date` (Date)
- `Priority` (Select): High, Medium, Low

#### 2.5: Projects

**Properties**:
- `Name` (Title)
- `Description` (Text)
- `Status` (Select): Not started, In progress, Completed
- `Tasks` (Relation → Tasks)
- `Related_Intent` (Relation → Executive Intents)
- `Area` (Relation → Areas)
- `Start_Date` (Date)
- `Target_Date` (Date)

#### 2.6: Areas

**Properties**:
- `Area_Name` (Title)
- `Description` (Text)
- `Icon` (Text): emoji for visual identification
- `Active` (Checkbox)

**Pre-populate with**:
```
- Career (💼, Active: ✓)
- Finance (💰, Active: ✓)
- Health (🏃, Active: ✓)
- Relationships (👥, Active: ✓)
- Learning (📚, Active: ✓)
- Projects (🚀, Active: ✓)
- Operations (⚙️, Active: ✓)
```

#### 2.7: Knowledge Nodes

**Properties**:
- `Concept` (Title)
- `Node_Type` (Select): Framework, Tool, Person, Company, Principle, Strategy, Metric
- `Description` (Text)
- `Related_Intents` (Relation → Executive Intents)
- `Source_Inbox` (Relation → System Inbox)
- `Tags` (Multi-select)

#### 2.8: Agent Registry

**Properties**:
- `Agent_Name` (Title)
- `Persona_Description` (Text)
- `Focus_Areas` (Multi-select): Growth, Risk, Compliance, Finance, Operations
- `Active` (Checkbox)

**Pre-populate with**:

| Agent Name | Persona Description | Focus Areas | Active |
|------------|-------------------|-------------|--------|
| The Entrepreneur | Growth-focused operator. Analyzes revenue potential, scalability, and market opportunity. | Growth, Finance, Operations | ✓ |
| The Quant | Quantitative analyst. Evaluates risk-adjusted returns using mathematical rigor. | Finance, Risk | ✓ |
| The Auditor | Risk and compliance officer. Ensures governance, ethics, and mission alignment. | Risk, Compliance | ✓ |

**IMPORTANT**: Copy the page IDs for each agent:
1. Open each agent's page
2. Copy URL (e.g., `https://notion.so/abc123`)
3. Extract ID from URL
4. Save these for later:
   - The Entrepreneur: `_______________`
   - The Quant: `_______________`
   - The Auditor: `_______________`

#### 2.9: Execution Log

**Properties**:
- `Log_Entry_Title` (Title)
- `Log_ID` (Number)
- `Action_Taken` (Text)
- `Decision_Date` (Date)
- `Intent` (Relation → Executive Intents)

#### 2.10: Training Data

**Properties**:
- `Entry_Title` (Title)
- `Intent_ID` (Text)
- `Agent_Name` (Select): The Entrepreneur, The Quant, The Auditor
- `Timestamp` (Date)
- `Original_Plan` (Text)
- `Final_Plan` (Text)
- `User_Modifications` (Text)
- `Acceptance_Rate` (Number): 0-1
- `Diff_Summary` (Text)

### Step 3: Share Databases with Integration

For EACH of the 10 databases:

1. Open the database in Notion
2. Click "..." (top right)
3. Click "Add connections"
4. Select "Executive Mind Matrix" integration
5. Click "Confirm"

### Step 4: Get Database IDs

For EACH database:

1. Open database in Notion
2. Copy the URL
3. Extract the database ID (32-character hex string)
   - URL format: `https://notion.so/{workspace}/{DATABASE_ID}?v=...`
   - Example: `https://notion.so/myworkspace/abc123def456` → ID is `abc123def456`

**Save these IDs** - you'll need them for environment variables:

```
DB_System_Inbox: ________________________________
DB_Executive_Intents: ________________________________
DB_Action_Pipes: ________________________________
DB_Agent_Registry: ________________________________
DB_Execution_Log: ________________________________
DB_Training_Data: ________________________________
DB_Tasks: ________________________________
DB_Projects: ________________________________
DB_Areas: ________________________________
DB_Nodes: ________________________________
```

---

## Getting API Keys

### Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Name it: "Executive Mind Matrix"
6. **Copy the key** (starts with `sk-ant-...`)
   - ⚠️ Save this securely - shown only once
7. (Optional) Set spending limits for cost control

**Cost estimate**: $5-10/month for typical usage (~10 intents/day)

---

## Local Testing

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/executive-mind-matrix.git
cd executive-mind-matrix
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create .env File

Create `.env` in the project root:

```bash
# Notion Configuration
NOTION_API_KEY=secret_your_notion_integration_token_here
NOTION_DB_SYSTEM_INBOX=your_system_inbox_database_id
NOTION_DB_EXECUTIVE_INTENTS=your_executive_intents_database_id
NOTION_DB_ACTION_PIPES=your_action_pipes_database_id
NOTION_DB_AGENT_REGISTRY=your_agent_registry_database_id
NOTION_DB_EXECUTION_LOG=your_execution_log_database_id
NOTION_DB_TRAINING_DATA=your_training_data_database_id
NOTION_DB_TASKS=your_tasks_database_id
NOTION_DB_PROJECTS=your_projects_database_id
NOTION_DB_AREAS=your_areas_database_id
NOTION_DB_NODES=your_knowledge_nodes_database_id

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
POLLING_INTERVAL_SECONDS=120

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Step 5: Validate Configuration

```bash
python scripts/validate-env.py
```

Expected output:
```
✓ All environment variables are set
✓ Notion API key is valid
✓ Anthropic API key is valid
✓ All database IDs are valid format
```

### Step 6: Test Database Connections

```bash
python scripts/test-connections.py
```

Expected output:
```
Testing Notion connection...
✓ Connected to Notion successfully
✓ DB_System_Inbox: Connected (0 items)
✓ DB_Executive_Intents: Connected (0 items)
[... all 10 databases ...]

Testing Anthropic connection...
✓ Connected to Anthropic successfully
✓ Model: claude-3-haiku-20240307

All systems operational!
```

### Step 7: Run Local Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

Expected output:
```
INFO:     Starting Executive Mind Matrix
INFO:     Environment: development
INFO:     Polling interval: 120s
INFO:     Application started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 8: Test Health Check

In another terminal:
```bash
curl http://localhost:8000/health
```

Expected response:
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

### Step 9: Test End-to-End

1. Add a test intent to System Inbox in Notion:
   ```
   Title: Test intent - hire engineer or outsource?
   Content: Simple test to verify system is working
   Status: Unprocessed
   ```

2. Trigger manual poll:
   ```bash
   curl -X POST http://localhost:8000/trigger-poll
   ```

3. Check System Inbox:
   - Status should change to "Triaged_to_Intent"
   - Triage_Destination should be "Strategic (Intent)"

4. Check Executive Intents:
   - New intent should appear
   - Should have AI classification results

If all checks pass, local setup is complete!

---

## Railway Deployment

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Or use Homebrew (Mac):
```bash
brew install railway
```

### Step 2: Login to Railway

```bash
railway login
```

Opens browser for authentication.

### Step 3: Initialize Project

```bash
railway init
```

- Choose "Create new project"
- Name: "Executive Mind Matrix"

### Step 4: Add Environment Variables

**Option A: Via CLI (Tedious but scriptable)**

```bash
railway variables set NOTION_API_KEY="secret_your_token"
railway variables set ANTHROPIC_API_KEY="sk-ant-your_key"
railway variables set NOTION_DB_SYSTEM_INBOX="database_id"
# ... repeat for all variables
```

**Option B: Via Dashboard (Recommended)**

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Open your project
3. Click "Variables" tab
4. Click "New Variable"
5. Add all variables from your `.env` file

**Required Variables**:
- All `NOTION_*` variables (11 total)
- All `ANTHROPIC_*` variables (2 total)
- All `APP_*` variables (optional)

**Production Overrides**:
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
POLLING_INTERVAL_SECONDS=120
```

### Step 5: Deploy

```bash
railway up
```

Expected output:
```
Building...
Deploying...
Deployment successful!
URL: https://executive-mind-matrix-production-xxxx.up.railway.app
```

### Step 6: Check Deployment

```bash
railway logs
```

Look for:
```
Starting Executive Mind Matrix
Environment: production
Polling interval: 120s
Application started successfully
```

### Step 7: Test Production Health Check

```bash
curl https://your-app.up.railway.app/health
```

Expected: Same as local health check response.

---

## Environment Configuration

### Required Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `NOTION_API_KEY` | `secret_abc123...` | Notion integration token |
| `ANTHROPIC_API_KEY` | `sk-ant-abc123...` | Claude API key |
| `NOTION_DB_SYSTEM_INBOX` | `abc123def456...` | System Inbox database ID |
| `NOTION_DB_EXECUTIVE_INTENTS` | `def456ghi789...` | Executive Intents database ID |
| `NOTION_DB_ACTION_PIPES` | `ghi789jkl012...` | Action Pipes database ID |
| `NOTION_DB_AGENT_REGISTRY` | `jkl012mno345...` | Agent Registry database ID |
| `NOTION_DB_EXECUTION_LOG` | `mno345pqr678...` | Execution Log database ID |
| `NOTION_DB_TRAINING_DATA` | `pqr678stu901...` | Training Data database ID |
| `NOTION_DB_TASKS` | `stu901vwx234...` | Tasks database ID |
| `NOTION_DB_PROJECTS` | `vwx234yz567...` | Projects database ID |
| `NOTION_DB_AREAS` | `yz567abc890...` | Areas database ID |
| `NOTION_DB_NODES` | `abc890def123...` | Knowledge Nodes database ID |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_MODEL` | `claude-3-haiku-20240307` | Model to use (Haiku/Sonnet) |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `POLLING_INTERVAL_SECONDS` | `120` | How often to poll (seconds) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

### Security Variables (Recommended for Production)

| Variable | Example | Description |
|----------|---------|-------------|
| `API_KEY` | `your-secret-key` | Protect endpoints with API key |
| `ALLOWED_ORIGINS` | `https://notion.so` | CORS allowed origins |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_PER_MINUTE` | `60` | Max requests per minute |

---

## Verification & Testing

### Post-Deployment Checklist

#### 1. Health Check
```bash
curl https://your-app.up.railway.app/health
```
✅ Should return `"status": "healthy"`

#### 2. Test Poll Trigger
```bash
curl -X POST https://your-app.up.railway.app/trigger-poll
```
✅ Should return `"status": "success"`

#### 3. Add Test Intent

Add to System Inbox in Notion:
```
Title: Production test - Should I test this system?
Content: This is a test to verify the production deployment is working correctly.
Status: Unprocessed
```

Wait 2-3 minutes, then check:
- ✅ Status changed to "Triaged_to_Intent"
- ✅ New entry in Executive Intents
- ✅ AI analysis present on intent page

#### 4. Test Dialectic Flow

Get intent ID from URL, then:
```bash
curl -X POST https://your-app.up.railway.app/dialectic/{intent_id}
```

✅ Should return dialectic synthesis

#### 5. Monitor Logs

```bash
railway logs --tail 100
```

Look for errors or warnings. Healthy logs show:
```
Starting poll cycle
Found X pending intents
Processed X/X intents successfully
```

---

## Troubleshooting

### Deployment Issues

#### Error: "Failed to build"

**Cause**: Missing dependencies or Python version mismatch

**Solution**:
```bash
# Verify Python version in runtime.txt
echo "python-3.11" > runtime.txt

# Rebuild
railway up
```

#### Error: "Application failed to start"

**Cause**: Missing environment variables

**Solution**:
```bash
# Check which variables are set
railway variables

# Verify all required variables are present
python scripts/validate-env.py
```

#### Error: "Notion API authentication failed"

**Cause**: Invalid Notion API key or wrong permissions

**Solution**:
1. Regenerate integration token in Notion
2. Verify all 10 databases are shared with integration
3. Update `NOTION_API_KEY` in Railway

#### Error: "Anthropic API rate limit exceeded"

**Cause**: Too many requests to Claude API

**Solution**:
1. Increase `POLLING_INTERVAL_SECONDS` to 300 (5 minutes)
2. Check Anthropic console for rate limits
3. Consider upgrading Anthropic plan

### Runtime Issues

#### Poller Not Running

**Symptoms**: Intents stay "Unprocessed" for >5 minutes

**Check**:
```bash
curl https://your-app.up.railway.app/health
# Look for "poller_active": true
```

**Solution**:
```bash
# Restart the service
railway restart

# Or trigger manual poll
curl -X POST https://your-app.up.railway.app/trigger-poll
```

#### Database Connection Errors

**Symptoms**: "Failed to fetch pending intents" in logs

**Check**:
- Verify database IDs are correct
- Ensure databases are shared with integration
- Check Notion API status

**Solution**:
```bash
# Test connections locally first
python scripts/test-connections.py
```

### Performance Issues

#### Slow Response Times

**Cause**: Railway free tier limitations (512MB RAM)

**Solution**:
- Upgrade to Railway Pro ($20/month for 2GB RAM)
- Reduce polling frequency
- Use Haiku model instead of Sonnet

#### High Anthropic Costs

**Cause**: Too many API calls or using expensive model

**Solution**:
```bash
# Switch to Haiku (10x cheaper than Sonnet)
railway variables set ANTHROPIC_MODEL="claude-3-haiku-20240307"

# Increase polling interval to reduce API calls
railway variables set POLLING_INTERVAL_SECONDS=300
```

---

## Security Best Practices

### API Keys

- ✅ Never commit `.env` to Git (add to `.gitignore`)
- ✅ Rotate keys every 90 days
- ✅ Use Railway's built-in secrets management
- ✅ Set up spending alerts in Anthropic Console

### Access Control

```bash
# Set API key for protected endpoints
railway variables set API_KEY="your-strong-random-key"
railway variables set API_KEY_HEADER="X-API-Key"
```

Then access protected endpoints:
```bash
curl -H "X-API-Key: your-strong-random-key" \
  https://your-app.up.railway.app/protected-endpoint
```

### CORS Configuration

```bash
# Restrict to Notion only
railway variables set ALLOWED_ORIGINS='["https://notion.so", "https://www.notion.so"]'
```

### Rate Limiting

```bash
railway variables set RATE_LIMIT_ENABLED=true
railway variables set RATE_LIMIT_PER_MINUTE=60
```

### Monitoring

**Sentry Integration** (Optional):
```bash
railway variables set SENTRY_DSN="your-sentry-dsn"
railway variables set SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

## Maintenance

### Daily Monitoring

```bash
# Check system health
curl https://your-app.up.railway.app/health

# Review logs for errors
railway logs --tail 50 | grep ERROR
```

### Weekly Tasks

- [ ] Review Execution Log for anomalies
- [ ] Check Training Data acceptance rates
- [ ] Review Railway usage/costs
- [ ] Backup Notion databases (export to Markdown)

### Monthly Tasks

- [ ] Review agent performance metrics
- [ ] Consider fine-tuning if acceptance rate <70%
- [ ] Update dependencies (`pip install --upgrade`)
- [ ] Rotate API keys (security best practice)
- [ ] Review and archive old intents

### Backup Strategy

**Notion** (Built-in):
1. Settings → Exports
2. Export all content (Markdown & CSV)
3. Save to secure location

**Railway** (Environment):
1. Download all environment variables
   ```bash
   railway variables > env-backup.txt
   ```
2. Save securely (encrypted storage)

**Code** (Git):
```bash
# Tag stable versions
git tag -a v1.0.0 -m "Stable production release"
git push origin v1.0.0
```

---

## Upgrade Paths

### Upgrading Claude Model

From Haiku to Sonnet (better quality, 10x cost):

```bash
railway variables set ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
```

**Cost impact**: $50-100/month (vs. $5-10/month for Haiku)

### Scaling Railway

| Plan | RAM | CPU | Price | Use Case |
|------|-----|-----|-------|----------|
| Free | 512MB | Shared | $5/mo credit | Testing (<10 intents/day) |
| Pro | 2GB | 2 vCPU | $20/mo | Production (<50 intents/day) |
| Enterprise | Custom | Custom | Custom | High volume (>100 intents/day) |

### Adding Custom Agents

See [ARCHITECTURE.md](ARCHITECTURE.md) for details on creating custom agent personas.

---

## Cost Breakdown

### Monthly Costs (Typical Usage: 10-20 intents/day)

| Service | Tier | Monthly Cost |
|---------|------|-------------|
| Railway | Free → Pro | $0-20 |
| Anthropic (Haiku) | Pay-as-go | $5-10 |
| Anthropic (Sonnet) | Pay-as-go | $50-100 |
| Notion | Free/Personal | $0-10 |
| **Total (Haiku)** | | **$5-30** |
| **Total (Sonnet)** | | **$55-130** |

**Recommendation**: Start with Haiku, upgrade to Sonnet if acceptance rate <70%.

---

## Next Steps

1. ✅ Complete deployment
2. 📖 Read [User Guide](USER-GUIDE.md) for daily usage
3. 🧠 Review [Architecture Guide](ARCHITECTURE.md) for deeper understanding
4. 🚀 Add 5-10 test intents and monitor results
5. 📊 Check agent performance after 1 week
6. 🎯 Fine-tune prompts based on acceptance rates

---

**Congratulations! Your Executive Mind Matrix is now live and operational.**

For ongoing support, see [Troubleshooting](#troubleshooting) or review logs in Railway dashboard.
