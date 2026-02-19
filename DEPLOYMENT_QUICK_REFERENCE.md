# Railway Deployment Quick Reference

**Status**: NOT READY - 1 Critical Issue
**Date**: 2026-02-11

---

## STOP - Action Required Before Deployment

### CRITICAL ISSUE: Missing Environment Variables

You need to add 4 environment variables that are currently missing:

```bash
NOTION_DB_TASKS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_PROJECTS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_AREAS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_NODES=xxxxxxxxxxxxxxxxxxxx
```

**Action Required**:
1. Create these 4 databases in Notion
2. Get their 32-character database IDs
3. Add to Railway environment variables

**DO NOT DEPLOY until this is fixed** - the app will crash!

---

## Quick Validation Commands

```bash
# Validate environment variables
python scripts/validate-env.py

# Run smoke tests (after deployment)
python scripts/smoke-test.py https://your-app.railway.app

# Check health
curl https://your-app.railway.app/health

# View logs
railway logs
```

---

## Complete Environment Variables List

### Required (15 variables)

```bash
# Notion - All 10 databases required
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxx
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

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
POLLING_INTERVAL_SECONDS=120
```

### Optional but Recommended

```bash
# Monitoring
SENTRY_DSN=https://xxxx@xxxx.ingest.sentry.io/xxxx
ENABLE_METRICS=true
JSON_LOGS=true

# Security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
ALLOWED_ORIGINS=https://yourdomain.com
API_KEY=your-secure-api-key
```

---

## Railway Deployment Steps (After Fixing Critical Issue)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Create Railway Project**
   - Go to https://railway.app
   - New Project → Deploy from GitHub repo
   - Select your repository

3. **Add Environment Variables**
   - Variables tab in Railway
   - Add ALL 15+ variables listed above
   - Save

4. **Deploy**
   - Railway auto-deploys after variables are set
   - Monitor deployment logs

5. **Verify**
   ```bash
   curl https://your-app.railway.app/health
   python scripts/smoke-test.py https://your-app.railway.app
   ```

---

## Health Check Endpoints

```bash
# Root - Basic status
GET https://your-app.railway.app/

# Health - Detailed health check
GET https://your-app.railway.app/health

# API Docs - Swagger UI
GET https://your-app.railway.app/docs

# Metrics - Prometheus metrics
GET https://your-app.railway.app/metrics
```

---

## Expected Health Check Response

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

---

## Rollback Commands

```bash
# Via Railway CLI
railway rollback

# Via Railway Dashboard
# Deployments tab → Previous deployment → Redeploy
```

---

## Common Issues & Quick Fixes

### Issue: Deployment Fails Immediately
**Cause**: Missing environment variables
**Fix**: Check all 15+ required variables are set in Railway

### Issue: Health Check Failing
**Cause**: Invalid Notion or Anthropic API keys
**Fix**: Verify keys in Railway variables

### Issue: Poller Not Active
**Cause**: Database IDs incorrect or databases not shared with integration
**Fix**: Verify all 10 database IDs and integration permissions

### Issue: 500 Errors
**Cause**: Application error, check logs
**Fix**: `railway logs` to see error details

---

## Performance Notes

### Current Configuration
- Dockerfile: 2 workers
- Railway.json: Uses standard Dockerfile

### Recommended for Production
Update railway.json to use Dockerfile.production:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.production"
  }
}
```

Benefits: 4 workers (2x performance), smaller image, access logging

---

## Documentation Links

### Full Guides
- **Comprehensive Guide**: RAILWAY_DEPLOYMENT.md (complete procedures)
- **Validation Summary**: PRE_DEPLOYMENT_VALIDATION_SUMMARY.md (findings)
- **Interactive Checklist**: DEPLOYMENT_READINESS_CHECKLIST.md (step-by-step)
- **General Deployment**: DEPLOYMENT_GUIDE.md (existing guide)
- **Quick Deploy**: QUICK_DEPLOY.md (fast-track)

### Validation Scripts
- Environment: `scripts/validate-env.py`
- Smoke Tests: `scripts/smoke-test.py`
- Connections: `scripts/test-connections.py`

---

## Critical Reminder

**BEFORE YOU DEPLOY**:
- [ ] All 10 Notion databases created
- [ ] All 10 database IDs obtained
- [ ] All environment variables configured in Railway
- [ ] `python scripts/validate-env.py` passes
- [ ] This checklist completed

**AFTER DEPLOYMENT**:
- [ ] Health endpoint returns healthy
- [ ] Smoke tests pass
- [ ] Poller is active
- [ ] No errors in logs

---

## Support

**Railway Issues**: https://railway.app/help
**Notion Status**: https://status.notion.so
**Anthropic Status**: https://status.anthropic.com

---

**Quick Reference Version**: 1.0.0
**Last Updated**: 2026-02-11
