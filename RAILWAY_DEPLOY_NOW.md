# Railway Deployment Guide - Executive Mind Matrix
**Copy-Paste Ready | 15-Minute Setup**

---

## Phase Overview

This guide assumes:
- ✅ All 10 database IDs are configured in `.env.production.example`
- ✅ You have Notion API key ready
- ✅ You have Anthropic API key ready
- ✅ Railway account is created and active

**Estimated Time**: 10-15 minutes

---

## Prerequisites Checklist

Before you start, gather these items:

- [ ] **Notion Integration API Key**
  - Get at: https://www.notion.so/my-integrations
  - Click "Create new integration" → Name it "Executive Mind Matrix" → Copy the token
  - Must start with: `secret_`

- [ ] **Anthropic API Key**
  - Get at: https://console.anthropic.com/
  - Click "Get API key" → Create new secret key → Copy it
  - Must start with: `sk-ant-`

- [ ] **Railway Account**
  - Sign up at: https://railway.app/
  - Can use GitHub login (recommended)

- [ ] **GitHub Account** (optional but recommended)
  - Connect to Railway for automatic deploys
  - Fork/clone: https://github.com/rippere/executive-mind-matrix

- [ ] **All 10 Notion Database IDs**
  - [ ] NOTION_DB_SYSTEM_INBOX
  - [ ] NOTION_DB_EXECUTIVE_INTENTS
  - [ ] NOTION_DB_ACTION_PIPES
  - [ ] NOTION_DB_AGENT_REGISTRY
  - [ ] NOTION_DB_EXECUTION_LOG
  - [ ] NOTION_DB_TRAINING_DATA
  - [ ] NOTION_DB_TASKS = `ac9e946ba1894b4bb2cbb7a846279ad5`
  - [ ] NOTION_DB_PROJECTS = `72511ef6118349189e3a0871576f5f09`
  - [ ] NOTION_DB_AREAS = `2d2c88542aed80d89497e943afb2b005`
  - [ ] NOTION_DB_NODES = `b2b0e6766cd44565bae738f98960794e`

---

## Complete Environment Variables Reference

Copy all 15+ variables below. **Fill in API keys from prerequisites.**

```env
# ============================================
# NOTION API CONFIGURATION
# ============================================
# Get from: https://www.notion.so/my-integrations
NOTION_API_KEY=secret_YOUR_NOTION_API_KEY_HERE

# 10 Required Database IDs (32-character hex strings)
NOTION_DB_SYSTEM_INBOX=YOUR_SYSTEM_INBOX_ID
NOTION_DB_EXECUTIVE_INTENTS=YOUR_EXECUTIVE_INTENTS_ID
NOTION_DB_ACTION_PIPES=YOUR_ACTION_PIPES_ID
NOTION_DB_AGENT_REGISTRY=YOUR_AGENT_REGISTRY_ID
NOTION_DB_EXECUTION_LOG=YOUR_EXECUTION_LOG_ID
NOTION_DB_TRAINING_DATA=YOUR_TRAINING_DATA_ID
NOTION_DB_TASKS=ac9e946ba1894b4bb2cbb7a846279ad5
NOTION_DB_PROJECTS=72511ef6118349189e3a0871576f5f09
NOTION_DB_AREAS=2d2c88542aed80d89497e943afb2b005
NOTION_DB_NODES=b2b0e6766cd44565bae738f98960794e

# ============================================
# ANTHROPIC API CONFIGURATION
# ============================================
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_API_KEY_HERE

# Model selection (recommended: claude-3-5-sonnet-20241022 for production)
# OPTIONS: claude-3-5-sonnet-20241022 (best) or claude-3-haiku-20240307 (fast/cheap)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# ============================================
# APPLICATION SETTINGS
# ============================================
ENVIRONMENT=production
LOG_LEVEL=INFO
POLLING_INTERVAL_SECONDS=120

# ============================================
# SERVER CONFIGURATION
# ============================================
# Railway will override PORT automatically - leave as is
HOST=0.0.0.0
PORT=8000

# ============================================
# MONITORING CONFIGURATION (OPTIONAL)
# ============================================
# Error tracking - skip if not using Sentry
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1

# Metrics
ENABLE_METRICS=true

# JSON logging for production log aggregation
JSON_LOGS=true

# ============================================
# SECURITY CONFIGURATION
# ============================================
# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# CORS - Update with your actual domain
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# API authentication (optional)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEY=
API_KEY_HEADER=X-API-Key
```

---

## Step-by-Step Railway Deployment

### Step 1: Create Railway Project

1. Go to **https://railway.app/dashboard**
2. Click **"+ New Project"** (top right)
3. Select **"Deploy from GitHub"** OR **"Empty Project"**
   - If GitHub: Authorize and select your fork of executive-mind-matrix
   - If Empty: We'll upload manually next
4. Name it: **executive-mind-matrix**
5. Click **Create Project**

**Expected Screen**: You should see a blank project dashboard with "Add a service" button.

---

### Step 2: Add Service

#### Option A: From GitHub (Recommended)

1. Click **"+ Add"** → **"From GitHub"**
2. Select **executive-mind-matrix** repository
3. Railway will auto-detect Dockerfile
4. Click **Deploy**

#### Option B: Manual Upload

1. Click **"+ Add"** → **"Empty Service"**
2. In the new service, go to **Settings** tab
3. Under "Deploy", change builder to **Dockerfile**
4. Ensure Dockerfile path is: `Dockerfile.production`

---

### Step 3: Configure Environment Variables

1. Still in Railway dashboard, click your service
2. Go to **"Variables"** tab
3. Click **"Raw Editor"** (recommended for bulk paste)
4. **Paste the complete environment variables list above**
5. **CRITICAL**: Replace placeholder values with your actual keys:
   - `NOTION_API_KEY` → Your actual Notion token
   - `ANTHROPIC_API_KEY` → Your actual Anthropic key
   - `NOTION_DB_*` → Your actual database IDs
6. Click **"Save"** (looks like a disk icon or button at bottom)

**Visual Check**:
- Should see 18+ variables in the list
- All variables should be green/valid
- No red warning icons

---

### Step 4: Configure Build & Deployment

1. In the service dashboard, go to **"Settings"** tab
2. Scroll to **"Build"** section:
   - Builder: `DOCKERFILE`
   - Dockerfile Path: `Dockerfile.production`
3. Scroll to **"Deploy"** section:
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2 --log-level info --proxy-headers --forwarded-allow-ips '*'`
   - Restart Policy: `ON_FAILURE`
   - Max Retries: `10`
4. Scroll to **"Health Check"** section:
   - Health Check Path: `/health`
   - Health Check Timeout: `100s`
5. Click **"Save"** at bottom right

---

### Step 5: Deploy

1. Go to **"Deploy"** tab in service
2. Click **"Deploy Latest"** button (blue button, top right)
3. Watch the build logs stream in real-time

**Expected Log Sequence**:
```
[Build] Step 1/15: FROM python:3.11-slim
...
[Build] Step 15/15: CMD ["uvicorn", ...]
[Build] Built successfully
[Deploy] Starting container...
[Deploy] Container started
[Deploy] Health check passed
[Deploy] Deployment successful ✓
```

**Status Indicator**: Should show "Active" (green dot) next to service name.

---

## Post-Deployment Verification

### Verification Command 1: Check Health Endpoint

```bash
# Get your Railway deployment URL
# In Railway dashboard → Click service → "Public Domain" (top right)
curl https://your-railway-url.up.railway.app/health

# Expected response (200 OK):
{
  "status": "healthy",
  "timestamp": "2026-02-12T10:30:45.123456",
  "environment": "production",
  "notion_connected": true
}
```

### Verification Command 2: Check Logs

1. In Railway dashboard, click your service
2. Go to **"Deployments"** tab
3. Click the latest deployment
4. Scroll through logs - should see:
   ```
   [INFO] Application startup complete
   [INFO] Uvicorn running on 0.0.0.0:8000
   [INFO] Notion connection established
   ```

### Verification Command 3: Trigger a Poll

```bash
# Trigger manual polling cycle
curl -X POST https://your-railway-url.up.railway.app/trigger-poll \
  -H "Content-Type: application/json" \
  -d '{}'

# Expected response (200 OK):
{
  "message": "Poll triggered successfully",
  "timestamp": "2026-02-12T10:32:15.654321"
}
```

### Verification Command 4: Check Metrics

```bash
curl https://your-railway-url.up.railway.app/metrics

# Should return Prometheus-format metrics (text, not JSON)
# Look for lines like:
# emm_polls_total 5.0
# emm_notion_calls_total 42.0
```

### Verification Checklist

After deployment, verify:

- [ ] Health endpoint returns 200 OK
- [ ] Logs show "Application startup complete"
- [ ] Metrics endpoint returns data
- [ ] No error messages in recent logs
- [ ] Service status is "Active" (green)
- [ ] CPU and memory usage are reasonable (<50% each)

---

## Troubleshooting Quick Fixes

### Problem: Deployment Fails During Build

**Error**: `requirements.txt not found` or similar

**Fix**:
1. Check Dockerfile path is correct: `Dockerfile.production`
2. Ensure all files are in repository root
3. Try redeploying: Click "Deploy Latest" again

---

### Problem: Health Check Fails (Red X on service)

**Error**: Container keeps restarting, health check times out

**Possible Causes & Fixes**:

1. **Missing Environment Variable**
   - Check all required variables are set
   - Especially: `NOTION_API_KEY` and `ANTHROPIC_API_KEY`
   - Go to Variables tab, click "Raw Editor" and verify

2. **Invalid API Keys**
   - Notion API key must start with `secret_`
   - Anthropic key must start with `sk-ant-`
   - Check for copy/paste errors (extra spaces, newlines)

3. **Invalid Database ID**
   - Database IDs must be 32-character hex strings
   - No hyphens or special characters
   - Compare against provided IDs for TASKS, PROJECTS, AREAS, NODES

4. **Network/Connectivity Issue**
   - Wait 30-60 seconds and try deploying again
   - Check Railway status: https://status.railway.app/

**Debug**: Check logs for specific error:
- Go to Deployments tab
- Click latest deployment
- Read error messages carefully
- Search for "ERROR" or "CRITICAL" lines

---

### Problem: Application Runs But Returns 500 Errors

**Error**: Health check passes but API calls fail with 500

**Fix**:
1. Check logs for "ERROR" or "Exception"
2. Common causes:
   - Database ID typo → Fix in Variables tab
   - API key invalid → Regenerate from Notion/Anthropic
   - Missing database in Notion → Create in Notion and get actual ID

---

### Problem: Slow Startup (Takes > 2 minutes)

**Normal**: First deployment takes 2-3 minutes to build image
**If Persistent**:
1. Check logs for "Installing" lines - dependencies take time
2. Consider smaller model: Change `ANTHROPIC_MODEL` to `claude-3-haiku-20240307`
3. Ensure database IDs are all correct (invalid IDs cause timeouts)

---

## Monitoring & Maintenance

### View Live Logs

```bash
# In Railway dashboard:
# 1. Click service
# 2. "Deployments" tab
# 3. Click active deployment
# 4. Logs stream live
```

### Check Resource Usage

In Railway dashboard:
1. Click service
2. Go to **"Metrics"** tab
3. Monitor:
   - **CPU**: Should be < 30% at rest, < 70% under load
   - **Memory**: Should be < 256MB at rest
   - **Network**: Should show request patterns

### View Active Deployments

1. Go to **"Deployments"** tab
2. Green checkmark = Active
3. Click to view logs for that deployment

---

## Rollback Instructions

### Quick Rollback (1-2 minutes)

If deployment has issues:

**Option 1: Railway Dashboard**
1. Go to **"Deployments"** tab
2. Find the previous (working) deployment
3. Click the **"⟳ Redeploy"** button next to it
4. Confirm

**Option 2: Command Line** (if Railway CLI is installed)
```bash
railway rollback
# Redeploys the previous stable version
```

### Manual Rollback

If rollback doesn't work:

1. Go to **"Variables"** tab
2. Temporarily comment out problematic variables by prefixing with `#`
3. Click **Deploy Latest**
4. Diagnose the issue offline
5. Once fixed, redeploy

---

## Success Criteria Checklist

After deployment, you should have:

- [ ] Service shows "Active" status (green)
- [ ] Health check passes at `/health`
- [ ] Logs show "Application startup complete"
- [ ] Can trigger polls at `/trigger-poll`
- [ ] Metrics available at `/metrics`
- [ ] Response time < 1 second for most requests
- [ ] No critical errors in logs

---

## Additional Resources

| Need | Link |
|------|------|
| Railway Dashboard | https://railway.app/dashboard |
| Notion Integration Setup | https://www.notion.so/my-integrations |
| Anthropic Console | https://console.anthropic.com/ |
| Railway Docs | https://docs.railway.app/ |
| Project GitHub Repo | https://github.com/rippere/executive-mind-matrix |
| Health Check Endpoint | `https://your-url/health` |

---

## Database IDs Reference

Keep this handy for troubleshooting:

```
NOTION_DB_TASKS=ac9e946ba1894b4bb2cbb7a846279ad5
NOTION_DB_PROJECTS=72511ef6118349189e3a0871576f5f09
NOTION_DB_AREAS=2d2c88542aed80d89497e943afb2b005
NOTION_DB_NODES=b2b0e6766cd44565bae738f98960794e
```

---

## Support & Next Steps

After successful deployment:

1. **Monitor for 24 hours** - Check logs daily
2. **Set up alerts** - Use Railway's alert feature
3. **Schedule backups** - Ensure Notion backups are enabled
4. **Document custom configs** - Keep track of any changes made

For issues:
- Check logs first (Deployments tab)
- Verify all environment variables are set
- Compare settings against this guide
- Test API keys independently before deploying

---

**Last Updated**: 2026-02-12
**Status**: Ready for Production
**Database IDs**: Confirmed & Updated
**Version**: 1.0 (Final)
