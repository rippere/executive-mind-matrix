# Executive Mind Matrix - Production Deployment Guide

This guide covers deploying the Executive Mind Matrix application to production using Railway, including monitoring setup, security configuration, and operational procedures.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Railway Deployment](#railway-deployment)
4. [Monitoring Setup](#monitoring-setup)
5. [Security Configuration](#security-configuration)
6. [Operational Procedures](#operational-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Required Accounts

- **Railway Account**: Sign up at [railway.app](https://railway.app)
- **Notion Account**: With admin access to workspace
- **Anthropic Account**: API access at [console.anthropic.com](https://console.anthropic.com)
- **Sentry Account** (Optional): For error tracking at [sentry.io](https://sentry.io)

### Required Tools

- Git (for repository management)
- Railway CLI (optional): `npm install -g @railway/cli`
- Python 3.11+ (for local testing)

### Notion Setup

Ensure you have created the following databases in Notion:

1. System Inbox
2. Executive Intents
3. Action Pipes
4. Agent Registry
5. Execution Log
6. Training Data

Refer to `NOTION_DASHBOARD_SETUP.md` for detailed setup instructions.

---

## Environment Configuration

### Step 1: Copy Environment Template

```bash
cp .env.production.example .env
```

### Step 2: Configure Required Variables

Edit `.env` and fill in your actual values:

#### Notion Configuration

```bash
# Get your integration token from https://www.notion.so/my-integrations
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxx

# Database IDs (found in database URLs)
NOTION_DB_SYSTEM_INBOX=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_EXECUTIVE_INTENTS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_ACTION_PIPES=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_AGENT_REGISTRY=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_EXECUTION_LOG=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_TRAINING_DATA=xxxxxxxxxxxxxxxxxxxx
```

**Finding Database IDs:**
1. Open your Notion database as a full page
2. Copy the URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`
3. The DATABASE_ID is the 32-character hex string

#### Anthropic Configuration

```bash
# Get your API key from https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx

# Choose model based on needs:
# - claude-3-5-sonnet-20241022 (best reasoning, higher cost)
# - claude-3-haiku-20240307 (fast, cost-effective)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

#### Application Settings

```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
POLLING_INTERVAL_SECONDS=120
```

#### Monitoring Configuration (Optional but Recommended)

```bash
# Sentry for error tracking
SENTRY_DSN=https://xxxx@xxxx.ingest.sentry.io/xxxx
SENTRY_TRACES_SAMPLE_RATE=0.1

# Enable metrics
ENABLE_METRICS=true
JSON_LOGS=true
```

#### Security Configuration

```bash
# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# CORS (specify your domains in production)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Optional API key for additional authentication
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEY=your-secure-api-key-here
API_KEY_HEADER=X-API-Key
```

### Step 3: Validate Configuration

Run the validation script to ensure all variables are properly configured:

```bash
# Validate environment variables
python scripts/validate-env.py

# Run pre-deployment checks
bash scripts/pre-deploy-check.sh
```

---

## Railway Deployment

### Option 1: Deploy via GitHub Integration (Recommended)

1. **Push Code to GitHub**

   ```bash
   git add .
   git commit -m "Prepare for production deployment"
   git push origin main
   ```

2. **Create Railway Project**

   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect the Dockerfile

3. **Configure Environment Variables**

   - In Railway dashboard, go to your service
   - Click "Variables" tab
   - Add all environment variables from your `.env` file
   - **Important**: Do NOT commit `.env` to git!

4. **Configure Custom Domain (Optional)**

   - Go to "Settings" tab
   - Under "Domains", click "Generate Domain" for a Railway subdomain
   - Or add your custom domain

5. **Deploy**

   - Railway will automatically deploy on push to main
   - Monitor deployment logs in the dashboard

### Option 2: Deploy via Railway CLI

1. **Install Railway CLI**

   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**

   ```bash
   railway login
   ```

3. **Initialize Project**

   ```bash
   railway init
   ```

4. **Link to Project**

   ```bash
   railway link
   ```

5. **Set Environment Variables**

   ```bash
   # Upload variables from .env file
   railway variables set --file .env
   ```

6. **Deploy**

   ```bash
   railway up
   ```

### Deployment Configuration

Railway uses these files for deployment:

- **`Dockerfile`**: Standard Docker build (2 workers)
- **`Dockerfile.production`**: Optimized multi-stage build (4 workers)
- **`railway.json`**: Railway-specific configuration

To use the production Dockerfile, update `railway.json`:

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.production"
  }
}
```

---

## Monitoring Setup

### Sentry Error Tracking

1. **Create Sentry Project**

   - Go to [sentry.io](https://sentry.io)
   - Create new project
   - Select "Python" as platform
   - Copy the DSN

2. **Configure in Railway**

   - Add environment variable: `SENTRY_DSN=<your-dsn>`
   - Optionally adjust: `SENTRY_TRACES_SAMPLE_RATE=0.1`

3. **Verify Setup**

   - Deploy the application
   - Check Sentry dashboard for incoming events
   - Test by triggering an error endpoint

### Prometheus Metrics

The application exposes Prometheus metrics at `/metrics` endpoint.

**Available Metrics:**

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `notion_api_requests_total` - Notion API request counter
- `anthropic_api_requests_total` - Anthropic API request counter
- `anthropic_tokens_used_total` - Token usage counter
- `poll_cycles_total` - Polling cycle counter
- `poller_status` - Poller status gauge
- `errors_total` - Error counter

**Scraping Metrics:**

Add to your Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'executive-mind-matrix'
    static_configs:
      - targets: ['your-app-url.railway.app']
    metrics_path: '/metrics'
    scheme: 'https'
```

### Railway Metrics

Railway provides built-in metrics:

- CPU usage
- Memory usage
- Network traffic
- Request logs

Access via Railway dashboard under "Metrics" tab.

### Setting Up Alerts

1. **Configure Alerting** (if using Prometheus with Alertmanager)

   - See `config/alerts.yaml` for pre-configured alert rules
   - Customize thresholds based on your needs

2. **Railway Webhooks**

   - Go to Project Settings > Webhooks
   - Add webhook URL for deployment notifications
   - Can integrate with Slack, Discord, or custom endpoints

---

## Security Configuration

### API Key Authentication

If you configured `API_KEY` in environment variables:

**Making Authenticated Requests:**

```bash
curl -H "X-API-Key: your-api-key" https://your-app.railway.app/trigger-poll
```

**Public Endpoints** (no API key required):
- `/` - Root/status
- `/health` - Health check
- `/metrics` - Prometheus metrics
- `/docs` - API documentation
- `/redoc` - Alternative API docs

### CORS Configuration

Update `ALLOWED_ORIGINS` to restrict cross-origin requests:

```bash
# Development (allow all)
ALLOWED_ORIGINS=*

# Production (specific domains)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Rate Limiting

Configured via environment variables:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

When rate limit is exceeded, API returns `429 Too Many Requests`.

### Security Headers

The application automatically adds these security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Secrets Management

**Never commit secrets to git!**

✅ **Good practices:**
- Use Railway's environment variables
- Use `.env` file locally (in `.gitignore`)
- Rotate API keys regularly
- Use separate keys for development and production

❌ **Bad practices:**
- Hardcoding secrets in code
- Committing `.env` to git
- Sharing secrets via email or chat
- Using same keys across environments

---

## Operational Procedures

### Health Checks

**Check Application Health:**

```bash
curl https://your-app.railway.app/health
```

**Expected Response:**

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

### Smoke Tests

Run smoke tests against deployed instance:

```bash
# Basic smoke test
python scripts/smoke-test.py https://your-app.railway.app

# With API key
python scripts/smoke-test.py https://your-app.railway.app your-api-key

# Using environment variables
export SMOKE_TEST_URL=https://your-app.railway.app
export API_KEY=your-api-key
python scripts/smoke-test.py
```

### Manual Polling

Trigger a manual poll cycle (useful for testing):

```bash
curl -X POST https://your-app.railway.app/trigger-poll \
  -H "X-API-Key: your-api-key"
```

### Viewing Logs

**Via Railway Dashboard:**
1. Go to your service
2. Click "Deployments" tab
3. Select active deployment
4. View real-time logs

**Via Railway CLI:**

```bash
railway logs
```

**Structured Logs:**

When `JSON_LOGS=true`, logs are in JSON format for easy parsing:

```json
{
  "timestamp": "2025-01-27T10:30:45Z",
  "level": "INFO",
  "message": "Poll cycle completed",
  "module": "notion_poller",
  "function": "poll_cycle",
  "extra": {
    "items_processed": 5,
    "duration": 2.3
  }
}
```

### Scaling

**Railway Auto-Scaling:**

Railway automatically scales based on traffic. For manual scaling:

1. Go to Service Settings
2. Adjust "Instances" or "Resources"
3. Redeploy if needed

**Application Workers:**

The application uses Uvicorn workers. To adjust:

Edit `Dockerfile` or `railway.json` start command:

```bash
uvicorn main:app --workers 4  # Adjust worker count
```

**Recommended workers:**
- Small instances: 2 workers
- Medium instances: 4 workers
- Large instances: 8 workers

---

## Troubleshooting

### Common Issues

#### 1. Poller Not Running

**Symptoms:**
- `poller_active: false` in health check
- No items being processed

**Solutions:**
- Check Notion API key is valid
- Verify database IDs are correct
- Check logs for specific errors
- Restart the service

#### 2. High Latency

**Symptoms:**
- Slow response times
- Request timeouts

**Solutions:**
- Check Notion/Anthropic API status
- Review polling interval (may need to increase)
- Check Railway resource usage
- Consider scaling up

#### 3. API Key Errors

**Symptoms:**
- 401 Unauthorized errors
- "Invalid API key" messages

**Solutions:**
- Verify environment variables are set correctly
- Check for typos in keys
- Ensure keys haven't been rotated
- Verify database permissions in Notion

#### 4. Rate Limiting Issues

**Symptoms:**
- 429 Too Many Requests errors
- Frequent Anthropic API errors

**Solutions:**
- Increase `RATE_LIMIT_PER_MINUTE`
- Adjust `POLLING_INTERVAL_SECONDS`
- Review token usage in metrics
- Consider upgrading API tier

### Debug Mode

Enable detailed logging:

```bash
# In Railway variables
LOG_LEVEL=DEBUG
```

**Warning:** Debug logs can be verbose and may expose sensitive information. Use only for troubleshooting and disable in production.

### Getting Help

1. Check application logs in Railway dashboard
2. Review Sentry error reports (if configured)
3. Check Notion API status: [status.notion.so](https://status.notion.so)
4. Check Anthropic API status: [status.anthropic.com](https://status.anthropic.com)
5. Review Railway status: [status.railway.app](https://status.railway.app)

---

## Rollback Procedures

### Railway Rollback

1. **Via Dashboard:**
   - Go to "Deployments" tab
   - Find previous successful deployment
   - Click "Redeploy"

2. **Via CLI:**

   ```bash
   railway rollback
   ```

### Git Rollback

If you need to rollback code changes:

```bash
# Find previous commit
git log --oneline

# Revert to specific commit
git revert <commit-hash>

# Or reset (use with caution)
git reset --hard <commit-hash>

# Force push (if already deployed)
git push origin main --force
```

### Environment Variable Rollback

1. Go to Railway dashboard
2. Click "Variables" tab
3. View variable history
4. Restore previous values
5. Redeploy the service

### Database Rollback

**Important:** There's no automatic database rollback for Notion.

For critical changes:

1. Backup Notion databases regularly
2. Document database schema changes
3. Test changes in staging environment first
4. Have manual reversion procedures ready

### Emergency Procedures

**If service is completely down:**

1. Check Railway status dashboard
2. Check application health endpoint
3. Review recent deployments and changes
4. Rollback to last known good deployment
5. Check external service status (Notion, Anthropic)
6. Contact support if needed

**Notification Channels:**

- Set up Railway webhooks for deployment notifications
- Configure Sentry alerts for critical errors
- Use Prometheus alerting if configured

---

## Post-Deployment Checklist

After deploying, verify:

- [ ] Health endpoint returns healthy status
- [ ] Poller is active and running
- [ ] All database connections successful
- [ ] Metrics endpoint is accessible
- [ ] Sentry is receiving events (if configured)
- [ ] API documentation is accessible
- [ ] Rate limiting is working correctly
- [ ] Security headers are present
- [ ] Manual poll trigger works
- [ ] Smoke tests pass
- [ ] Logs are being generated correctly
- [ ] No errors in Railway logs
- [ ] Resource usage is within expected range

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error rates in Sentry
- Check Railway resource usage
- Review application logs for anomalies

**Weekly:**
- Review metrics and performance trends
- Check for dependency updates
- Verify backup procedures

**Monthly:**
- Rotate API keys (if required by security policy)
- Review and update alert thresholds
- Conduct security audit
- Test rollback procedures

### Updates and Patches

**Updating Dependencies:**

```bash
# Update requirements.txt
pip install --upgrade package-name

# Test locally
python -m pytest

# Run pre-deployment checks
bash scripts/pre-deploy-check.sh

# Deploy
git commit -am "Update dependencies"
git push origin main
```

**Applying Security Patches:**

1. Review security advisories
2. Update affected packages
3. Test in staging environment
4. Deploy during maintenance window
5. Monitor for issues

---

## Additional Resources

- **Project Documentation**: `README.md`
- **Notion Setup Guide**: `NOTION_DASHBOARD_SETUP.md`
- **Security Audit**: `SECURITY_AUDIT_FIXES.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

## Support

For issues or questions:

1. Check this deployment guide
2. Review application logs
3. Check external service status pages
4. Contact your team lead or administrator

---

**Last Updated**: 2025-01-27
**Version**: 1.0.0
