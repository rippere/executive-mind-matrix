# Production Readiness Checklist

This document provides a comprehensive checklist to ensure the Executive Mind Matrix application is ready for production deployment.

## Pre-Deployment Checklist

### Environment Configuration

- [ ] All required environment variables are set
- [ ] API keys are valid and not placeholders
- [ ] Database IDs are correct
- [ ] Environment is set to `production`
- [ ] Log level is appropriate (INFO or WARNING)
- [ ] JSON logs are enabled for production
- [ ] Secrets are not committed to git

**Validation:**
```bash
python scripts/validate-env.py
bash scripts/pre-deploy-check.sh
```

### Security

- [ ] API key authentication configured (if required)
- [ ] CORS origins are restricted (not `*`)
- [ ] Rate limiting is enabled
- [ ] Security headers are configured
- [ ] `.env` file is in `.gitignore`
- [ ] No hardcoded secrets in code
- [ ] HTTPS is enabled (handled by Railway)

**Review:**
- Check `ALLOWED_ORIGINS` setting
- Verify `API_KEY` is set and secure
- Review `RATE_LIMIT_PER_MINUTE` setting

### Monitoring

- [ ] Sentry DSN configured (optional but recommended)
- [ ] Metrics endpoint enabled
- [ ] Log aggregation configured
- [ ] Alert rules reviewed
- [ ] Monitoring dashboard setup (if using)

**Setup:**
- Configure Sentry account and DSN
- Set `ENABLE_METRICS=true`
- Review `config/alerts.yaml`

### Testing

- [ ] Local tests pass
- [ ] Docker build succeeds
- [ ] Connection tests pass
- [ ] Health endpoint works
- [ ] API endpoints tested
- [ ] Poller starts correctly

**Commands:**
```bash
# Run connection tests
python scripts/test-connections.py

# Build Docker image
docker build -t executive-mind-matrix .

# Run locally
uvicorn main:app --host 0.0.0.0 --port 8000

# Test health
curl http://localhost:8000/health
```

### Documentation

- [ ] README is up to date
- [ ] Deployment guide reviewed
- [ ] Environment variables documented
- [ ] API documentation accessible
- [ ] Runbooks prepared

**Files to review:**
- `README.md`
- `DEPLOYMENT_GUIDE.md`
- `MONITORING_SETUP.md`
- `.env.production.example`

### Infrastructure

- [ ] Railway account configured
- [ ] GitHub repository connected
- [ ] Domain configured (if using custom domain)
- [ ] Backup procedures documented
- [ ] Rollback procedures tested

---

## Deployment Checklist

### Pre-Deployment

- [ ] Run pre-deployment checks
- [ ] Review recent code changes
- [ ] Check for open issues
- [ ] Backup current configuration
- [ ] Notify team of deployment

### During Deployment

- [ ] Push code to GitHub
- [ ] Verify Railway starts build
- [ ] Monitor build logs
- [ ] Watch deployment progress
- [ ] Check for errors

### Post-Deployment

- [ ] Health check passes
- [ ] Poller is running
- [ ] Smoke tests pass
- [ ] Metrics are being collected
- [ ] Logs are being generated
- [ ] No critical errors in logs
- [ ] API endpoints responsive
- [ ] Monitor for 30 minutes

**Verification:**
```bash
# Health check
curl https://your-app.railway.app/health

# Smoke tests
python scripts/smoke-test.py https://your-app.railway.app

# Check poller status
curl https://your-app.railway.app/ | jq .poller_running
```

---

## Production Configuration

### Recommended Settings

**Application:**
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
JSON_LOGS=true
POLLING_INTERVAL_SECONDS=120
```

**Security:**
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
ALLOWED_ORIGINS=https://yourdomain.com
API_KEY=<secure-random-key>
```

**Monitoring:**
```bash
SENTRY_DSN=<your-sentry-dsn>
SENTRY_TRACES_SAMPLE_RATE=0.1
ENABLE_METRICS=true
```

**Model Selection:**
```bash
# For best quality (higher cost)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# For cost optimization (lower quality)
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

### Performance Tuning

**Worker Configuration:**

In `Dockerfile` or `railway.json`, adjust workers based on instance size:

- **Small instance (512MB)**: 2 workers
- **Medium instance (1GB)**: 4 workers
- **Large instance (2GB+)**: 8 workers

**Polling Interval:**

Adjust based on load and API limits:

- **High frequency**: 60 seconds (more responsive, higher API usage)
- **Standard**: 120 seconds (balanced)
- **Low frequency**: 300 seconds (reduced API usage)

**Rate Limiting:**

Based on expected traffic:

- **Low traffic**: 30 requests/minute
- **Standard**: 60 requests/minute
- **High traffic**: 120 requests/minute

---

## Monitoring Checklist

### Health Metrics

Monitor these key metrics:

- [ ] Uptime > 99.9%
- [ ] Response time (p95) < 2 seconds
- [ ] Error rate < 1%
- [ ] Poller is active
- [ ] No critical errors in logs

### API Metrics

- [ ] Notion API success rate > 95%
- [ ] Anthropic API success rate > 95%
- [ ] API latencies within SLAs
- [ ] Token usage within budget

### System Metrics

- [ ] CPU usage < 80%
- [ ] Memory usage < 80%
- [ ] No memory leaks
- [ ] Disk usage < 80%

### Business Metrics

- [ ] Items processed per hour
- [ ] Agent analysis success rate
- [ ] Dialectic flow completions
- [ ] User acceptance rate (from training data)

---

## Operational Readiness

### Runbooks

Create runbooks for common scenarios:

1. **Service Down**: Troubleshooting steps
2. **High Error Rate**: Investigation process
3. **API Failures**: Fallback procedures
4. **Performance Issues**: Optimization steps
5. **Deployment Issues**: Rollback procedures

### On-Call Procedures

- [ ] On-call rotation defined
- [ ] Escalation path documented
- [ ] Alert channels configured
- [ ] Contact information updated
- [ ] Access credentials shared securely

### Incident Response

- [ ] Incident severity levels defined
- [ ] Response time SLAs established
- [ ] Communication templates prepared
- [ ] Post-mortem process defined

---

## Maintenance Checklist

### Daily

- [ ] Check error rates in Sentry
- [ ] Monitor resource usage
- [ ] Review critical alerts
- [ ] Verify poller is running

### Weekly

- [ ] Review performance metrics
- [ ] Check for dependency updates
- [ ] Review application logs
- [ ] Verify backups

### Monthly

- [ ] Security audit
- [ ] Cost analysis
- [ ] Performance review
- [ ] Update documentation
- [ ] Test rollback procedures
- [ ] Review alert thresholds

### Quarterly

- [ ] Disaster recovery drill
- [ ] Architecture review
- [ ] Capacity planning
- [ ] Security assessment
- [ ] Dependency upgrades

---

## Rollback Readiness

### Rollback Triggers

Rollback if:

- [ ] Critical errors affecting all users
- [ ] Data corruption detected
- [ ] Security vulnerability introduced
- [ ] Performance degradation > 50%
- [ ] Unable to resolve issue within 30 minutes

### Rollback Procedure

1. Identify last known good deployment
2. Access Railway dashboard
3. Select previous deployment
4. Click "Redeploy"
5. Monitor deployment
6. Verify health checks
7. Run smoke tests
8. Document incident

**Time to rollback:** < 5 minutes

---

## Success Criteria

Deployment is successful when:

- [x] All health checks pass
- [x] Poller is active and processing
- [x] No critical errors in logs
- [x] Response times within SLA
- [x] Monitoring is collecting data
- [x] Smoke tests pass
- [x] No alerts triggered
- [x] Service stable for 30+ minutes

---

## Post-Deployment Tasks

Within 24 hours:

- [ ] Monitor error rates
- [ ] Review performance metrics
- [ ] Check token usage and costs
- [ ] Verify all integrations working
- [ ] Update status page (if applicable)
- [ ] Send deployment notification
- [ ] Schedule post-mortem (if issues)

Within 1 week:

- [ ] Review logs for patterns
- [ ] Optimize based on real traffic
- [ ] Update documentation
- [ ] Collect user feedback
- [ ] Plan next iteration

---

## Support Resources

### Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Monitoring Setup](MONITORING_SETUP.md)
- [Quick Deploy Guide](QUICK_DEPLOY.md)
- [Notion Setup](NOTION_DASHBOARD_SETUP.md)

### External Resources

- Railway: [docs.railway.app](https://docs.railway.app)
- Sentry: [docs.sentry.io](https://docs.sentry.io)
- Notion API: [developers.notion.com](https://developers.notion.com)
- Anthropic API: [docs.anthropic.com](https://docs.anthropic.com)

### Contact

- On-call: [Define your contact method]
- Team lead: [Define contact]
- DevOps: [Define contact]

---

## Sign-off

Before going to production, ensure sign-off from:

- [ ] Developer
- [ ] QA/Testing
- [ ] DevOps/SRE
- [ ] Security team
- [ ] Product owner

---

**Document Version**: 1.0.0
**Last Updated**: 2025-01-27
**Next Review**: [Set review date]
