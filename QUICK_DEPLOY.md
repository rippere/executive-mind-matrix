# Quick Deployment Guide

Fast-track guide to deploy Executive Mind Matrix to Railway.

## Prerequisites

- Railway account
- Notion workspace with databases configured
- Anthropic API key
- GitHub repository

## 5-Minute Deployment

### 1. Prepare Environment Variables

Create `.env` file:

```bash
# Copy template
cp .env.production.example .env

# Edit with your values
nano .env
```

**Required variables:**

```bash
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxx
NOTION_DB_SYSTEM_INBOX=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_EXECUTIVE_INTENTS=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_ACTION_PIPES=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_AGENT_REGISTRY=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_EXECUTION_LOG=xxxxxxxxxxxxxxxxxxxx
NOTION_DB_TRAINING_DATA=xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ENVIRONMENT=production
```

### 2. Validate Configuration

```bash
# Validate environment
python scripts/validate-env.py

# Run pre-deployment checks
bash scripts/pre-deploy-check.sh
```

### 3. Push to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 4. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Add environment variables from `.env` (in Railway dashboard)
6. Wait for deployment to complete

### 5. Verify Deployment

```bash
# Check health
curl https://your-app.railway.app/health

# Run smoke tests
python scripts/smoke-test.py https://your-app.railway.app
```

## Quick Commands

```bash
# Local development
uvicorn main:app --reload

# Local testing with Docker
docker build -t executive-mind-matrix .
docker run -p 8000:8000 --env-file .env executive-mind-matrix

# Docker Compose (with monitoring)
docker-compose up

# Railway CLI deployment
railway login
railway init
railway up

# View logs
railway logs

# Rollback
railway rollback
```

## Health Check URLs

- Root: `https://your-app.railway.app/`
- Health: `https://your-app.railway.app/health`
- Metrics: `https://your-app.railway.app/metrics`
- API Docs: `https://your-app.railway.app/docs`

## Troubleshooting

### Poller not running
- Check Notion API key and database IDs
- Review logs: `railway logs`

### API errors
- Verify Anthropic API key
- Check rate limits

### Deployment fails
- Run `bash scripts/pre-deploy-check.sh`
- Check Railway build logs

## Next Steps

- [ ] Configure custom domain in Railway
- [ ] Set up Sentry error tracking
- [ ] Configure monitoring alerts
- [ ] Test all endpoints
- [ ] Set up backup procedures

**Full documentation:** See `DEPLOYMENT_GUIDE.md`
