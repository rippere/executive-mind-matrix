# Sentry Error Tracking Setup Guide

**Time required:** 5 minutes
**Cost:** Free (up to 5,000 errors/month)

---

## Step 1: Create Sentry Account

1. Go to https://sentry.io/signup/
2. Sign up with GitHub (or email)
3. Select **"Free" plan** (5K errors/month, 1 project)

---

## Step 2: Create New Project

1. After signup, click **"Create Project"**
2. Select platform: **Python**
3. Framework: **FastAPI**
4. Project name: `executive-mind-matrix`
5. Click **"Create Project"**

---

## Step 3: Copy DSN

After project creation, Sentry shows installation instructions.

**Find this line:**
```python
sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    # ...
)
```

**Copy the DSN** (the URL starting with `https://`)

Example: `https://abc123def456@o123456.ingest.sentry.io/7890123`

---

## Step 4: Add DSN to Railway

### Option A: Railway Dashboard (Easiest)

1. Go to https://railway.app
2. Open your `executive-mind-matrix` project
3. Click on your service
4. Go to **"Variables"** tab
5. Click **"New Variable"**
6. Name: `SENTRY_DSN`
7. Value: Paste your DSN from Step 3
8. Click **"Add"**

Railway will automatically redeploy with Sentry enabled.

### Option B: Railway CLI

```bash
railway variables set SENTRY_DSN="https://your-dsn-here"
```

---

## Step 5: Verify It's Working

Wait ~2 minutes for Railway to redeploy, then:

### Test Error Capture

```bash
# Trigger a test error (this endpoint doesn't exist)
curl -X POST https://web-production-3d888.up.railway.app/trigger-sentry-test
```

### Check Sentry Dashboard

1. Go to https://sentry.io
2. Click on your **executive-mind-matrix** project
3. Go to **"Issues"** tab
4. You should see the 404 error appear within ~30 seconds

---

## What Sentry Captures

Once configured, Sentry automatically tracks:

- ✅ **Unhandled exceptions** (with full stack traces)
- ✅ **API endpoint failures** (500 errors)
- ✅ **Performance issues** (slow requests)
- ✅ **Error frequency** (how often each error occurs)
- ✅ **User impact** (how many users affected)

### Example Use Cases

**Scenario 1: Notion API Rate Limit**
- Sentry alert: `HTTPException: 429 Too Many Requests`
- Stack trace shows: `notion_poller.py:147`
- You can see which endpoint hit the limit

**Scenario 2: Agent Analysis Timeout**
- Sentry alert: `anthropic.APITimeoutError`
- Stack trace shows: `agent_router.py:213`
- You can see which intent caused the timeout

**Scenario 3: Database Connection Lost**
- Sentry alert: `notion_client.errors.APIResponseError`
- Context shows: Which database, which operation
- You get notified within 1 minute

---

## Sentry Dashboard Features

### Issues View
- **New Issues** - Errors that appeared recently
- **Trending** - Errors increasing in frequency
- **For Review** - Unresolved issues

### Alerts (Optional Setup)

Configure notifications:
1. Go to **Settings → Alerts**
2. Create rule: "Send notification when new issue is created"
3. Choose notification channel: Email, Slack, Discord, etc.

### Performance Monitoring (Optional)

Already enabled in `main_enhanced.py`:
- Request duration tracking
- Slow endpoint detection
- Database query timing

---

## Sentry in Your Code

Already configured in `main_enhanced.py` (lines 22-32):

```python
# Sentry integration (only if DSN is set)
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1,  # 10% of requests tracked for performance
        integrations=[FastApiIntegration()]
    )
    logger.info("Sentry initialized")
```

**Note:** If `SENTRY_DSN` is not set, Sentry is disabled (no impact on performance).

---

## Cost & Limits

**Free Tier:**
- 5,000 errors/month
- 10,000 performance transactions/month
- 1 project
- 30-day data retention

**When you might upgrade:**
- If you exceed 5K errors/month (unlikely for this system)
- If you want longer retention (90+ days)
- If you need more projects

**Current expected usage:** ~50-200 errors/month (mostly API timeouts/rate limits)

---

## Troubleshooting

### Sentry Not Capturing Errors

**Check Railway logs:**
```bash
railway logs | grep -i sentry
```

**Expected output:**
```
Sentry initialized
```

**If missing:** DSN not set or invalid

### Test Sentry Manually

Add this to any endpoint in `main_enhanced.py`:
```python
@app.get("/test-sentry")
async def test_sentry():
    raise Exception("Test error from Sentry integration")
```

Redeploy and hit the endpoint - should appear in Sentry immediately.

---

## Next Steps After Setup

1. ✅ Configure email/Slack alerts for new issues
2. ✅ Set up weekly error digest emails
3. ✅ Review performance monitoring data
4. ✅ Create alert rules for critical errors (e.g., database connection failures)

---

**Setup complete!** Your system now has production-grade error tracking.
