# Railway Deployment Guide for Executive Mind Matrix

**Project Status**: Pre-Deployment Validation Complete
**Date**: 2026-02-11
**Version**: 1.0.0

---

## Executive Summary

This document provides a comprehensive guide for deploying the Executive Mind Matrix application to Railway. The pre-deployment validation has been completed, and several critical issues have been identified that must be addressed before deployment.

---

## Table of Contents

1. [Pre-Deployment Validation Results](#pre-deployment-validation-results)
2. [Critical Issues & Required Fixes](#critical-issues--required-fixes)
3. [Prerequisites](#prerequisites)
4. [Environment Variables Configuration](#environment-variables-configuration)
5. [Railway Deployment Steps](#railway-deployment-steps)
6. [Post-Deployment Validation](#post-deployment-validation)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Validation Results

### Status: BLOCKED - Critical Issues Found

#### Validation Checks Performed

| Check | Status | Details |
|-------|--------|---------|
| Python Syntax | PASS | All main Python files compile successfully |
| Docker Configuration | PASS | Dockerfile and Dockerfile.production are valid |
| Railway Config | PASS | railway.json is valid |
| Dependencies | PASS | requirements.txt properly formatted |
| Environment Variables | FAIL | Missing 4 required database variables |
| Settings Validation | BLOCKED | Cannot validate without complete environment |

### Python Environment

- **Local Python Version**: 3.13.7
- **Docker Python Version**: 3.11-slim
- **All main files validated**: main.py, config/settings.py, app/models.py, app/agent_router.py, app/notion_poller.py

### Docker Configuration Analysis

**Standard Dockerfile** (Dockerfile):
- Workers: 2
- Image: python:3.11-slim
- Non-root user: appuser (uid 1000)
- Health check: Enabled (30s interval)
- Port: 8000

**Production Dockerfile** (Dockerfile.production):
- Workers: 4 (optimized for production)
- Multi-stage build: Yes (smaller image size)
- Image: python:3.11-slim
- Non-root user: appuser (uid 1000)
- Health check: Enabled (30s interval)
- Port: 8000
- Additional flags: --access-log enabled

**Railway Configuration** (railway.json):
- Builder: DOCKERFILE
- Dockerfile: Dockerfile (standard, not production)
- Workers: 2
- Port: Dynamic ($PORT)
- Health check: /health endpoint (100s timeout)
- Restart policy: ON_FAILURE (max 10 retries)

---

## Critical Issues & Required Fixes

### Issue 1: Missing Environment Variables (CRITICAL)

**Severity**: BLOCKING
**Impact**: Application will fail to start

**Problem**: The `config/settings.py` file defines 10 required Notion database fields, but the `.env.example` and `.env.production.example` files only include 6.

**Required Databases in settings.py**:
1. notion_db_system_inbox
2. notion_db_executive_intents
3. notion_db_action_pipes
4. notion_db_agent_registry
5. notion_db_execution_log
6. notion_db_training_data
7. **notion_db_tasks** (MISSING from .env examples)
8. **notion_db_projects** (MISSING from .env examples)
9. **notion_db_areas** (MISSING from .env examples)
10. **notion_db_nodes** (MISSING from .env examples)

**Resolution Required**:
Before deploying to Railway, you MUST:
1. Create these 4 additional databases in Notion (if not already created)
2. Add their IDs to your Railway environment variables
3. Update .env.example and .env.production.example files to include these variables

**Usage in Application**:
- `notion_db_tasks`: Used by task spawning functionality (app/task_spawner.py, app/notion_poller.py)
- `notion_db_projects`: Used by project creation (app/task_spawner.py)
- `notion_db_areas`: Used by areas management (app/areas_manager.py)
- `notion_db_nodes`: Used by knowledge linking (app/knowledge_linker.py)

### Issue 2: Railway Configuration Uses Standard Dockerfile

**Severity**: ADVISORY
**Impact**: Suboptimal performance in production

**Problem**: The `railway.json` file is configured to use the standard `Dockerfile` with 2 workers, but `Dockerfile.production` with 4 workers would be better for production deployments.

**Current Configuration**:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  }
}
```

**Recommended Configuration**:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.production"
  }
}
```

**Benefits of Using Dockerfile.production**:
- Multi-stage build (smaller final image)
- 4 workers instead of 2 (better concurrency)
- Access logging enabled for better monitoring
- Optimized for production environment variables

### Issue 3: .dockerignore Excludes Markdown Files

**Severity**: LOW
**Impact**: README.md and documentation won't be in container

**Problem**: The `.dockerignore` file excludes all markdown files (`*.md`) and the `docs/` directory. This means documentation won't be available inside the container.

**Current .dockerignore**:
```
# Documentation
*.md
docs/
```

**Impact**: Not critical for operation, but means in-container documentation is unavailable. Consider whether you need README.md or other docs accessible inside the container.

### Issue 4: Port Configuration Inconsistency

**Severity**: ADVISORY
**Impact**: Potential confusion, but Railway overrides correctly

**Problem**: The Dockerfile hardcodes port 8000, while Railway uses dynamic $PORT variable.

**Analysis**: This is actually handled correctly in railway.json's startCommand which uses `--port $PORT`, so Railway will override the Dockerfile's default. No action required, but be aware of this.

---

## Prerequisites

### Required Accounts

1. **Railway Account**
   - Sign up at: https://railway.app
   - GitHub authentication recommended for easy deployments

2. **Notion Account**
   - Workspace admin access required
   - Integration must be created at: https://www.notion.so/my-integrations
   - Integration must be shared with all 10 databases

3. **Anthropic Account**
   - API key required from: https://console.anthropic.com
   - Recommended: Tier 2+ for production usage

4. **Sentry Account** (Optional but Recommended)
   - Error tracking: https://sentry.io
   - Create a Python/FastAPI project

### Required Notion Databases

You MUST create and configure these 10 databases in Notion:

1. **System Inbox** - Incoming tasks/items
2. **Executive Intents** - Strategic decisions to be made
3. **Action Pipes** - Approved actions/decisions
4. **Agent Registry** - AI agent personas and configurations
5. **Execution Log** - Audit trail of actions
6. **Training Data** - AI learning/feedback data
7. **Tasks** - Individual actionable tasks
8. **Projects** - Project management
9. **Areas** - Life/work areas (PARA method)
10. **Nodes** - Knowledge graph nodes

For detailed database setup, see: `NOTION_DASHBOARD_SETUP.md`

### Required Tools

- **Git**: For version control and deployment
- **Railway CLI** (optional): `npm install -g @railway/cli`
- **Python 3.11+**: For local testing
- **Docker** (optional): For local container testing

---

## Environment Variables Configuration

### Complete Environment Variables List

Below is the complete list of environment variables you need to configure in Railway.

#### Core Notion Configuration (REQUIRED)

```bash
# Notion API Key - Get from https://www.notion.so/my-integrations
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxx

# All 10 Required Database IDs (32-character hex strings)
NOTION_DB_SYSTEM_INBOX=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_EXECUTIVE_INTENTS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_ACTION_PIPES=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_AGENT_REGISTRY=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_EXECUTION_LOG=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_TRAINING_DATA=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_TASKS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_PROJECTS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_AREAS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_NODES=xxxxxxxxxxxxxxxxxxxx
```

**How to Find Database IDs**:
1. Open your Notion database as a full page
2. Look at the URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`
3. The DATABASE_ID is the 32-character hex string (before the `?v=`)
4. Copy without dashes if present

#### Anthropic Configuration (REQUIRED)

```bash
# Anthropic API Key - Get from https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx

# Model Selection
# Options:
#   - claude-3-5-sonnet-20241022 (best reasoning, production recommended)
#   - claude-3-haiku-20240307 (fast, cost-effective)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

#### Application Settings (REQUIRED)

```bash
# Environment
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# Polling interval for checking Notion (in seconds)
POLLING_INTERVAL_SECONDS=120
```

#### Server Configuration (AUTO-CONFIGURED BY RAILWAY)

```bash
# Railway automatically sets PORT
# These are optional overrides if needed
HOST=0.0.0.0
PORT=8000  # Railway will override this with $PORT
```

#### Monitoring Configuration (OPTIONAL)

```bash
# Sentry Error Tracking
SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxx@xxxxxxxxxxxxxxxxxxxx.ingest.sentry.io/xxxxxxxxxxxxxxxxxxxx
SENTRY_TRACES_SAMPLE_RATE=0.1

# Metrics
ENABLE_METRICS=true
JSON_LOGS=true
```

#### Security Configuration (RECOMMENDED)

```bash
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# CORS Configuration
# In production, specify exact domains instead of "*"
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Optional API Key for Additional Authentication
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEY=your-secure-api-key-here
API_KEY_HEADER=X-API-Key
```

### Validation Before Deployment

Before deploying, validate your environment variables locally:

1. **Create local .env file** (DO NOT COMMIT):
   ```bash
   cp .env.production.example .env
   # Edit .env with your actual values
   ```

2. **Run validation script**:
   ```bash
   python scripts/validate-env.py
   ```

   This will check:
   - All required variables are set
   - API keys are in correct format
   - Database IDs are valid 32-character hex strings
   - No placeholder values remain

3. **Expected output**:
   ```
   ==================================================
   Environment Variable Validation Results
   ==================================================

   ✓ All environment variables are valid!
   ```

---

## Railway Deployment Steps

### Step 1: Prepare Your Repository

1. **Ensure all changes are committed**:
   ```bash
   git status
   # Commit any pending changes
   git add .
   git commit -m "Prepare for Railway deployment"
   ```

2. **Push to GitHub**:
   ```bash
   git push origin main
   ```

3. **Verify .gitignore excludes sensitive files**:
   ```bash
   # Ensure .env is NOT committed
   git ls-files | grep .env
   # Should return nothing or only .env.example
   ```

### Step 2: Create Railway Project

1. **Go to Railway**: https://railway.app

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authenticate with GitHub if needed
   - Select your repository

3. **Railway will**:
   - Detect the Dockerfile automatically
   - Start building the container
   - FAIL on first deploy (because env vars not set yet)

### Step 3: Configure Environment Variables

1. **In Railway Dashboard**:
   - Click on your service
   - Go to "Variables" tab

2. **Add ALL environment variables**:
   - Use the complete list from the "Environment Variables Configuration" section above
   - DO NOT include quotes around values
   - Railway handles variable substitution automatically

3. **Important Variables to Double-Check**:
   - All 10 NOTION_DB_* variables must be set
   - NOTION_API_KEY must start with `secret_`
   - ANTHROPIC_API_KEY must start with `sk-ant-`

4. **Save Variables**:
   - Click "Add Variable" for each
   - Or use "Raw Editor" to paste multiple at once

### Step 4: Deploy

1. **Trigger Deployment**:
   - Railway will auto-deploy after variables are saved
   - OR click "Deploy" button manually

2. **Monitor Deployment**:
   - Go to "Deployments" tab
   - Watch build logs in real-time
   - Look for:
     ```
     ✓ Building Docker image
     ✓ Pushing to registry
     ✓ Deploying
     ✓ Health check passed
     ```

3. **Deployment Time**: Typically 3-5 minutes

### Step 5: Verify Deployment

1. **Check Health Endpoint**:
   ```bash
   curl https://your-service.railway.app/health
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
       "training_data": true
     }
   }
   ```

2. **Check Root Endpoint**:
   ```bash
   curl https://your-service.railway.app/
   ```

3. **Run Smoke Tests** (from local machine):
   ```bash
   python scripts/smoke-test.py https://your-service.railway.app
   ```

### Step 6: Configure Custom Domain (Optional)

1. **In Railway Dashboard**:
   - Go to "Settings" tab
   - Under "Domains" section

2. **Options**:
   - **Railway Subdomain**: Click "Generate Domain" (free)
   - **Custom Domain**: Add your domain and configure DNS

3. **SSL Certificate**:
   - Automatically provisioned by Railway
   - No additional configuration needed

---

## Post-Deployment Validation

### Comprehensive Validation Checklist

Run through this checklist after deployment:

- [ ] Health endpoint returns `"status": "healthy"`
- [ ] Root endpoint returns application info
- [ ] Poller is active (`"poller_active": true`)
- [ ] All 6 databases show as configured in health check
- [ ] API documentation accessible at `/docs`
- [ ] Metrics endpoint accessible at `/metrics` (if enabled)
- [ ] Manual poll trigger works: `POST /trigger-poll`
- [ ] Railway logs show no errors
- [ ] Sentry receiving events (if configured)
- [ ] Response times are acceptable (< 1000ms)
- [ ] Security headers present in responses
- [ ] Rate limiting functional (test with multiple requests)

### Validation Scripts

1. **Run Comprehensive Smoke Tests**:
   ```bash
   export SMOKE_TEST_URL=https://your-service.railway.app
   export API_KEY=your-api-key  # If configured
   python scripts/smoke-test.py
   ```

2. **Test Manual Polling**:
   ```bash
   curl -X POST https://your-service.railway.app/trigger-poll \
     -H "X-API-Key: your-api-key"
   ```

3. **Monitor Logs**:
   ```bash
   # Via Railway CLI
   railway logs

   # Or watch in Railway dashboard
   ```

### Expected Behavior

After successful deployment:

1. **Poller Service**:
   - Starts automatically on application startup
   - Polls Notion every 120 seconds (or your configured interval)
   - Processes new items in System Inbox

2. **API Endpoints**:
   - All endpoints respond within 1 second
   - No 500 errors in logs
   - Rate limiting active (if enabled)

3. **Logging**:
   - Structured logs appear in Railway dashboard
   - No ERROR level messages
   - INFO level shows poll cycles completing

---

## Rollback Procedures

### When to Rollback

Rollback if you observe:
- Health check failing consistently
- High error rates in logs
- Poller not starting
- Database connection failures
- Unexpected behavior in production

### Railway Dashboard Rollback

1. **Go to "Deployments" tab**
2. **Find last known good deployment**
3. **Click "Redeploy"**
4. **Monitor health check**

**Rollback time**: ~2-3 minutes

### Railway CLI Rollback

```bash
railway rollback
```

This will:
- Revert to previous deployment
- Keep environment variables unchanged
- Maintain same infrastructure

### Git-Based Rollback

If you need to rollback code changes:

```bash
# 1. Find the commit to rollback to
git log --oneline

# 2. Create a revert commit (safe)
git revert <commit-hash>

# 3. Push to trigger Railway redeploy
git push origin main
```

**Do NOT use `git reset --hard` on main branch**

### Environment Variable Rollback

If deployment fails due to environment variable changes:

1. Go to Railway dashboard
2. Click "Variables" tab
3. Review recent changes
4. Update variables to previous values
5. Railway will auto-redeploy

### Emergency Procedures

If service is completely down:

1. **Check Railway Status**: https://status.railway.app
2. **Check Notion Status**: https://status.notion.so
3. **Check Anthropic Status**: https://status.anthropic.com
4. **Review Recent Changes**: In Railway deployments tab
5. **Rollback to Last Known Good State**
6. **Check Logs for Root Cause**
7. **Fix Issue in Development Environment**
8. **Redeploy with Fix**

---

## Troubleshooting

### Issue: Deployment Fails with "ModuleNotFoundError"

**Symptoms**: Build fails, logs show missing Python modules

**Solution**:
1. Check `requirements.txt` is committed to repository
2. Verify all dependencies are listed
3. Check for typos in package names
4. Ensure no development-only dependencies

### Issue: Health Check Failing

**Symptoms**: Deployment shows as unhealthy, container restarts

**Causes & Solutions**:

1. **Missing Environment Variables**:
   - Check all 10 NOTION_DB_* variables are set
   - Verify NOTION_API_KEY and ANTHROPIC_API_KEY

2. **Invalid Database IDs**:
   - Must be exactly 32 characters
   - Must be valid hex (0-9, a-f)
   - No dashes or special characters

3. **Notion API Connection Failed**:
   - Verify Notion integration is active
   - Check databases are shared with integration
   - Test API key with curl

4. **Port Binding Issue**:
   - Railway sets $PORT automatically
   - Verify railway.json uses `--port $PORT`

### Issue: "Poller Not Active"

**Symptoms**: Health check shows `"poller_active": false`

**Solution**:
1. Check Railway logs for startup errors
2. Verify Notion database IDs are correct
3. Test Notion API connection manually
4. Check POLLING_INTERVAL_SECONDS is valid integer
5. Restart deployment

### Issue: High Memory Usage

**Symptoms**: Container OOM (Out of Memory) kills, restarts

**Solution**:
1. Reduce worker count in Dockerfile
2. Increase Railway plan resources
3. Check for memory leaks in logs
4. Review POLLING_INTERVAL_SECONDS (longer = less memory)

### Issue: Slow Response Times

**Symptoms**: Requests taking > 5 seconds, timeouts

**Solution**:
1. Check Notion API response times
2. Check Anthropic API response times
3. Verify worker count is appropriate
4. Review database query efficiency
5. Consider caching strategies

### Issue: Rate Limiting Errors from Anthropic

**Symptoms**: 429 errors in logs, failed AI analysis

**Solution**:
1. Increase POLLING_INTERVAL_SECONDS
2. Upgrade Anthropic API tier
3. Implement request queuing
4. Review usage patterns

### Issue: CORS Errors

**Symptoms**: Browser-based requests fail with CORS error

**Solution**:
1. Update ALLOWED_ORIGINS environment variable
2. Add your frontend domain
3. Use comma-separated list for multiple domains
4. Redeploy after updating

### Debugging Commands

```bash
# View real-time logs
railway logs

# SSH into container (if needed)
railway run bash

# Test health locally with same env
docker run -p 8000:8000 --env-file .env your-image

# Test Notion connection
python scripts/test-connections.py

# Validate environment
python scripts/validate-env.py
```

---

## Best Practices

### Security

1. **Never commit .env files** - Always in .gitignore
2. **Rotate API keys regularly** - Every 90 days minimum
3. **Use separate keys for dev/prod** - Different Notion/Anthropic keys
4. **Enable rate limiting** - Protect against abuse
5. **Set specific ALLOWED_ORIGINS** - Don't use "*" in production
6. **Monitor Sentry errors** - Set up alerts for critical issues

### Monitoring

1. **Set up health check alerts** - Use Railway webhooks
2. **Monitor Sentry daily** - Review error rates
3. **Check metrics weekly** - Review /metrics endpoint
4. **Review logs regularly** - Look for patterns
5. **Test manually monthly** - Run smoke tests

### Maintenance

1. **Update dependencies monthly** - Security patches
2. **Test in staging first** - Before production deploy
3. **Document all changes** - Update this guide
4. **Keep backups of Notion** - Export databases regularly
5. **Review Railway usage** - Optimize costs

---

## Additional Resources

### Project Documentation
- Main README: `/home/rippere/Projects/executive-mind-matrix/README.md`
- Deployment Guide: `/home/rippere/Projects/executive-mind-matrix/DEPLOYMENT_GUIDE.md`
- Quick Deploy: `/home/rippere/Projects/executive-mind-matrix/QUICK_DEPLOY.md`
- Notion Setup: `/home/rippere/Projects/executive-mind-matrix/NOTION_DASHBOARD_SETUP.md`

### Validation Scripts
- Environment Validator: `/home/rippere/Projects/executive-mind-matrix/scripts/validate-env.py`
- Smoke Tests: `/home/rippere/Projects/executive-mind-matrix/scripts/smoke-test.py`
- Connection Tests: `/home/rippere/Projects/executive-mind-matrix/scripts/test-connections.py`

### External Resources
- Railway Documentation: https://docs.railway.app
- Railway Status: https://status.railway.app
- Notion API Docs: https://developers.notion.com
- Anthropic API Docs: https://docs.anthropic.com
- FastAPI Documentation: https://fastapi.tiangolo.com

---

## Support & Escalation

### Getting Help

1. **Review This Document First**
2. **Check Railway Logs** - Most issues visible here
3. **Check External Status Pages** - Notion, Anthropic, Railway
4. **Review Sentry Errors** - If configured
5. **Test Locally** - Reproduce issue with Docker
6. **Contact Railway Support** - For infrastructure issues

### Contact Information

- **Railway Support**: https://railway.app/help
- **Project Repository**: Check CONTRIBUTING.md for guidelines

---

## Deployment Readiness Summary

### CURRENT STATUS: NOT READY FOR DEPLOYMENT

Before you can deploy to Railway, you MUST resolve this critical issue:

**BLOCKING ISSUE**: Missing 4 Required Environment Variables

You need to:
1. Create 4 additional Notion databases: Tasks, Projects, Areas, Nodes
2. Get their database IDs
3. Add these 4 variables to Railway:
   - NOTION_DB_TASKS
   - NOTION_DB_PROJECTS
   - NOTION_DB_AREAS
   - NOTION_DB_NODES

### Once the above is resolved, you can proceed with deployment.

### Deployment Checklist

- [ ] All 10 Notion databases created in Notion workspace
- [ ] All 10 NOTION_DB_* environment variables obtained
- [ ] NOTION_API_KEY obtained and tested
- [ ] ANTHROPIC_API_KEY obtained and tested
- [ ] All environment variables validated with scripts/validate-env.py
- [ ] Repository pushed to GitHub
- [ ] Railway project created
- [ ] All environment variables configured in Railway
- [ ] Deployment triggered
- [ ] Health check passed
- [ ] Smoke tests passed
- [ ] Monitoring configured (Sentry, metrics)
- [ ] Custom domain configured (optional)
- [ ] Documentation reviewed
- [ ] Team notified of deployment

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-11
**Prepared By**: Claude Code Pre-Deployment Validation

---
