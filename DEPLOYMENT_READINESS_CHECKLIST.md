# Deployment Readiness Checklist

**Project**: Executive Mind Matrix
**Target Platform**: Railway
**Validation Date**: 2026-02-11
**Status**: BLOCKED - Critical Issues Must Be Resolved

---

## Quick Status Summary

### Overall Status: NOT READY FOR DEPLOYMENT

**Blocking Issues**: 1 Critical
**Advisory Issues**: 2
**Passed Checks**: 5

---

## Phase 1: Pre-Deployment Validation Results

### Configuration Validation

| Component | Status | Details |
|-----------|--------|---------|
| Python Syntax | PASS | All core files compile successfully |
| Docker Configuration | PASS | Dockerfile and Dockerfile.production valid |
| Railway Configuration | PASS | railway.json valid JSON and structure |
| Dependencies | PASS | requirements.txt properly formatted |
| Environment Variables | FAIL | Missing 4 required database IDs |
| Application Startup | BLOCKED | Cannot test until env vars complete |

### Code Quality Checks

- [x] Python syntax validation passed
- [x] No circular import dependencies detected
- [x] Main application files validated:
  - /home/rippere/Projects/executive-mind-matrix/main.py
  - /home/rippere/Projects/executive-mind-matrix/config/settings.py
  - /home/rippere/Projects/executive-mind-matrix/app/models.py
  - /home/rippere/Projects/executive-mind-matrix/app/agent_router.py
  - /home/rippere/Projects/executive-mind-matrix/app/notion_poller.py

### Docker Configuration

- [x] Dockerfile exists and is valid
- [x] Dockerfile.production exists with optimizations
- [x] .dockerignore configured properly
- [x] Health checks configured (30s interval)
- [x] Non-root user configured (appuser, uid 1000)
- [x] Port 8000 exposed
- [ ] ADVISORY: Railway uses standard Dockerfile, not production version

### Railway Configuration

- [x] railway.json exists
- [x] Valid JSON format
- [x] Health check endpoint configured (/health)
- [x] Restart policy configured (ON_FAILURE, 10 retries)
- [x] Dynamic port configuration ($PORT)
- [ ] ADVISORY: Uses 2 workers instead of 4 (Dockerfile vs Dockerfile.production)

---

## Critical Issues (MUST FIX BEFORE DEPLOY)

### Issue 1: Missing Required Environment Variables

**Severity**: CRITICAL - BLOCKING
**Status**: UNRESOLVED

**Problem**:
The application requires 10 Notion database environment variables, but only 6 are documented in the .env.example files.

**Missing Variables**:
1. NOTION_DB_TASKS
2. NOTION_DB_PROJECTS
3. NOTION_DB_AREAS
4. NOTION_DB_NODES

**Required Action**:
1. Create these 4 databases in Notion workspace
2. Share each database with your Notion integration
3. Obtain the 32-character hex database ID for each
4. Add to Railway environment variables before deployment

**Verification**:
```bash
# Once added to .env, run:
python scripts/validate-env.py
```

**Impact if Not Fixed**:
- Application will fail to start
- Pydantic validation error will occur
- Container will crash and restart indefinitely
- Deployment will fail health checks

---

## Advisory Issues (SHOULD FIX)

### Issue 2: Railway Uses Standard Dockerfile Instead of Production

**Severity**: ADVISORY
**Current**: Dockerfile (2 workers, single-stage build)
**Recommended**: Dockerfile.production (4 workers, multi-stage build)

**Impact**:
- Lower concurrency (2 workers vs 4)
- Larger image size (no multi-stage build optimization)
- No access logging in production

**Recommended Fix**:
Update railway.json:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.production"
  }
}
```

### Issue 3: Documentation Files Excluded from Docker Image

**Severity**: LOW
**Impact**: README.md not available inside container

**Current .dockerignore**:
```
*.md
docs/
```

**Impact**: Minimal - documentation not needed for runtime operation

**Optional Fix**: Remove `*.md` from .dockerignore if you want in-container docs

---

## Phase 2: Environment Configuration

### Required Environment Variables

#### Core Notion Configuration (10 variables)
- [ ] NOTION_API_KEY
- [ ] NOTION_DB_SYSTEM_INBOX
- [ ] NOTION_DB_EXECUTIVE_INTENTS
- [ ] NOTION_DB_ACTION_PIPES
- [ ] NOTION_DB_AGENT_REGISTRY
- [ ] NOTION_DB_EXECUTION_LOG
- [ ] NOTION_DB_TRAINING_DATA
- [ ] NOTION_DB_TASKS (MISSING)
- [ ] NOTION_DB_PROJECTS (MISSING)
- [ ] NOTION_DB_AREAS (MISSING)
- [ ] NOTION_DB_NODES (MISSING)

#### Anthropic Configuration (2 variables)
- [ ] ANTHROPIC_API_KEY
- [ ] ANTHROPIC_MODEL

#### Application Settings (3 variables)
- [ ] ENVIRONMENT=production
- [ ] LOG_LEVEL=INFO
- [ ] POLLING_INTERVAL_SECONDS=120

#### Optional Monitoring (3 variables)
- [ ] SENTRY_DSN (optional)
- [ ] ENABLE_METRICS=true
- [ ] JSON_LOGS=true

#### Optional Security (4 variables)
- [ ] RATE_LIMIT_ENABLED=true
- [ ] RATE_LIMIT_PER_MINUTE=60
- [ ] ALLOWED_ORIGINS (comma-separated)
- [ ] API_KEY (optional)

### Environment Variable Validation

Run before deploying:
```bash
# Create .env file with all variables
cp .env.production.example .env
# Edit .env with your actual values

# Validate
python scripts/validate-env.py
```

Expected output:
```
==================================================
Environment Variable Validation Results
==================================================

✓ All environment variables are valid!
```

---

## Phase 3: Railway Deployment Steps

### Pre-Deployment Checklist

- [ ] All 10 Notion databases created in workspace
- [ ] Notion integration created and shared with all databases
- [ ] All database IDs obtained (32-character hex strings)
- [ ] Anthropic API key obtained
- [ ] Environment validation script passed
- [ ] Code committed and pushed to GitHub
- [ ] .env file NOT committed (in .gitignore)

### Deployment Steps

1. **Create Railway Project**
   - [ ] Go to https://railway.app
   - [ ] Click "New Project"
   - [ ] Select "Deploy from GitHub repo"
   - [ ] Choose your repository

2. **Configure Environment Variables**
   - [ ] Go to Variables tab in Railway
   - [ ] Add all required environment variables
   - [ ] Double-check all 10 NOTION_DB_* variables
   - [ ] Save variables

3. **Deploy**
   - [ ] Railway auto-deploys after variables are set
   - [ ] Monitor deployment logs
   - [ ] Wait for health check to pass

4. **Verify Deployment**
   - [ ] Check health endpoint: `curl https://your-app.railway.app/health`
   - [ ] Verify poller is active
   - [ ] Run smoke tests: `python scripts/smoke-test.py https://your-app.railway.app`

---

## Phase 4: Post-Deployment Validation

### Critical Health Checks

- [ ] Health endpoint returns HTTP 200
- [ ] Health endpoint shows `"status": "healthy"`
- [ ] Poller is active: `"poller_active": true`
- [ ] All 6 databases show configured (tasks/projects/areas/nodes not checked in health endpoint)
- [ ] No errors in Railway logs
- [ ] Application responds within 1 second

### API Endpoint Tests

- [ ] Root endpoint accessible: `GET /`
- [ ] Health endpoint accessible: `GET /health`
- [ ] API docs accessible: `GET /docs`
- [ ] Metrics accessible: `GET /metrics` (if enabled)
- [ ] Manual poll trigger works: `POST /trigger-poll`

### Smoke Tests

Run comprehensive tests:
```bash
export SMOKE_TEST_URL=https://your-app.railway.app
python scripts/smoke-test.py
```

Expected results:
- [ ] Root Endpoint (/): PASS
- [ ] Health Endpoint (/health): PASS
- [ ] Response Time: PASS (< 1000ms)
- [ ] Security Headers: PASS or acceptable warnings
- [ ] Metrics Endpoint (/metrics): PASS (if enabled)
- [ ] API Docs (/docs): PASS

### Monitoring Setup

- [ ] Sentry receiving events (if configured)
- [ ] Prometheus metrics accessible (if enabled)
- [ ] Railway logs showing structured output
- [ ] No ERROR level messages in logs
- [ ] Poll cycles completing successfully

---

## Phase 5: Operational Readiness

### Documentation

- [ ] RAILWAY_DEPLOYMENT.md reviewed
- [ ] Team aware of deployment
- [ ] Environment variables documented
- [ ] Rollback procedures understood

### Monitoring & Alerting

- [ ] Sentry project created (optional)
- [ ] Railway webhooks configured (optional)
- [ ] Health check monitoring enabled
- [ ] Log aggregation configured (optional)

### Security

- [ ] API keys rotated if needed
- [ ] ALLOWED_ORIGINS configured for production
- [ ] Rate limiting enabled
- [ ] Security headers verified
- [ ] .env file NOT in git repository

### Backup & Recovery

- [ ] Notion databases exported as backup
- [ ] Rollback procedure documented
- [ ] Previous deployment available for rollback
- [ ] Emergency contacts identified

---

## Deployment Decision

### Current Status: DO NOT DEPLOY

**Reason**: Critical Issue 1 (Missing Environment Variables) must be resolved first.

### After Fixing Critical Issues:

Once all checkboxes in the following sections are complete, you may proceed:
1. Critical Issues (Must Fix Before Deploy)
2. Phase 2: Environment Configuration - Required Variables
3. Phase 3: Pre-Deployment Checklist

### Recommended Timeline:

1. **Immediately**: Create missing Notion databases
2. **Within 1 hour**: Obtain all database IDs and configure in Railway
3. **After configuration**: Run validation script
4. **If validation passes**: Proceed with deployment
5. **After deployment**: Complete Phase 4 validation

---

## Quick Reference Commands

### Validation
```bash
# Validate environment variables
python scripts/validate-env.py

# Test Python syntax
python -m py_compile main.py config/settings.py

# Test connections (requires .env)
python scripts/test-connections.py
```

### Deployment
```bash
# Push to GitHub (triggers Railway deploy)
git push origin main

# Monitor Railway logs
railway logs

# Run smoke tests
python scripts/smoke-test.py https://your-app.railway.app
```

### Health Checks
```bash
# Check health
curl https://your-app.railway.app/health

# Check root
curl https://your-app.railway.app/

# Trigger manual poll
curl -X POST https://your-app.railway.app/trigger-poll \
  -H "X-API-Key: your-api-key"
```

### Rollback
```bash
# Via Railway CLI
railway rollback

# Via Railway Dashboard
# Deployments tab → Select previous deployment → Redeploy
```

---

## Support Resources

### Documentation
- Comprehensive Guide: /home/rippere/Projects/executive-mind-matrix/RAILWAY_DEPLOYMENT.md
- Quick Deploy: /home/rippere/Projects/executive-mind-matrix/QUICK_DEPLOY.md
- Full Deployment Guide: /home/rippere/Projects/executive-mind-matrix/DEPLOYMENT_GUIDE.md
- Notion Setup: /home/rippere/Projects/executive-mind-matrix/NOTION_DASHBOARD_SETUP.md

### Validation Scripts
- Environment Validator: /home/rippere/Projects/executive-mind-matrix/scripts/validate-env.py
- Smoke Tests: /home/rippere/Projects/executive-mind-matrix/scripts/smoke-test.py
- Connection Tests: /home/rippere/Projects/executive-mind-matrix/scripts/test-connections.py

### External Resources
- Railway Docs: https://docs.railway.app
- Railway Status: https://status.railway.app
- Notion API: https://developers.notion.com
- Anthropic API: https://docs.anthropic.com

---

## Sign-Off

### Before Deploying to Production, Confirm:

- [ ] I have resolved all CRITICAL issues
- [ ] I have obtained all 10 Notion database IDs
- [ ] I have configured all required environment variables in Railway
- [ ] I have run and passed the validation script
- [ ] I have reviewed the comprehensive RAILWAY_DEPLOYMENT.md guide
- [ ] I understand the rollback procedures
- [ ] I am prepared to monitor the deployment
- [ ] I have a backup of critical Notion data

**Deployment Authorized By**: _______________
**Date**: _______________

---

**Checklist Version**: 1.0.0
**Last Updated**: 2026-02-11
**Generated By**: Claude Code Pre-Deployment Validation System
