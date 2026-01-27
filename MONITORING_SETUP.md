# Monitoring Setup Guide

This guide covers setting up monitoring and observability for the Executive Mind Matrix application.

## Table of Contents

1. [Overview](#overview)
2. [Sentry Error Tracking](#sentry-error-tracking)
3. [Prometheus Metrics](#prometheus-metrics)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Logging](#logging)
6. [Alerting](#alerting)

---

## Overview

The Executive Mind Matrix includes comprehensive monitoring capabilities:

- **Sentry**: Error tracking and performance monitoring
- **Prometheus**: Metrics collection and aggregation
- **Grafana**: Visualization and dashboards (optional)
- **Structured Logging**: JSON-formatted logs for easy parsing

### Architecture

```
Application
    ├── Sentry SDK (errors & traces)
    ├── Prometheus Client (metrics)
    └── Loguru (structured logs)
```

---

## Sentry Error Tracking

### Setup

1. **Create Sentry Account**
   - Go to [sentry.io](https://sentry.io)
   - Create new project
   - Select "Python" platform

2. **Get DSN**
   - Copy the DSN from project settings
   - Format: `https://xxxx@xxxx.ingest.sentry.io/xxxx`

3. **Configure Application**

   Add to `.env`:
   ```bash
   SENTRY_DSN=https://xxxx@xxxx.ingest.sentry.io/xxxx
   SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
   ```

4. **Verify Setup**

   The application will automatically:
   - Initialize Sentry on startup
   - Capture exceptions
   - Track performance
   - Record breadcrumbs

### What Sentry Captures

**Automatic:**
- Unhandled exceptions
- FastAPI route performance
- Request context
- User actions (breadcrumbs)

**Custom Events:**
```python
from sentry_sdk import capture_message, capture_exception

# Log a message
capture_message("Custom event", level="info")

# Log an exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e)
```

### Sentry Dashboard

View in Sentry dashboard:
- **Issues**: Grouped errors with stack traces
- **Performance**: Transaction traces and slow queries
- **Releases**: Track errors by deployment
- **Alerts**: Configure notifications

### Best Practices

- Use lower sample rates in production (0.1 = 10%)
- Set up alerts for critical errors
- Create releases to track which version had issues
- Use tags to categorize errors

---

## Prometheus Metrics

### Available Metrics

#### Application Info
- `executive_mind_matrix_info` - Application version and metadata

#### HTTP Metrics
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_inprogress` - Current in-progress requests

#### Notion API Metrics
- `notion_api_requests_total{operation, status}` - API request counter
- `notion_api_request_duration_seconds{operation}` - Request duration

#### Anthropic API Metrics
- `anthropic_api_requests_total{model, status}` - API request counter
- `anthropic_api_request_duration_seconds{model}` - Request duration
- `anthropic_tokens_used_total{model, type}` - Token usage (input/output)

#### Polling Metrics
- `poll_cycles_total{status}` - Polling cycle counter
- `poll_cycle_duration_seconds` - Cycle duration
- `items_processed_total{type}` - Items processed counter

#### Agent Metrics
- `agent_analyses_total{agent, status}` - Agent analysis counter
- `agent_analysis_duration_seconds{agent}` - Analysis duration

#### Dialectic Metrics
- `dialectic_flows_total{status}` - Dialectic flow counter
- `dialectic_flow_duration_seconds` - Flow duration

#### System Health
- `poller_status` - Poller running status (1=running, 0=stopped)
- `active_tasks` - Number of active background tasks

#### Error Metrics
- `errors_total{type, component}` - Error counter

### Accessing Metrics

**Enable metrics in `.env`:**
```bash
ENABLE_METRICS=true
```

**Access metrics endpoint:**
```
http://localhost:8000/metrics
```

**Example output:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1523.0

# HELP anthropic_tokens_used_total Total tokens used
# TYPE anthropic_tokens_used_total counter
anthropic_tokens_used_total{model="claude-3-5-sonnet",type="input"} 45231.0
```

### Recording Custom Metrics

```python
from app.monitoring import metrics

# Record Notion API request
metrics.record_notion_request(
    operation="query_database",
    status="success",
    duration=1.23
)

# Record Anthropic API request
metrics.record_anthropic_request(
    model="claude-3-5-sonnet",
    status="success",
    duration=2.45,
    input_tokens=150,
    output_tokens=300
)

# Record error
metrics.record_error(
    error_type="APIError",
    component="notion_poller"
)
```

---

## Grafana Dashboards

### Local Setup with Docker Compose

1. **Start monitoring stack:**

   ```bash
   docker-compose --profile monitoring up -d
   ```

   This starts:
   - Application (port 8000)
   - Prometheus (port 9090)
   - Grafana (port 3000)

2. **Access Grafana:**

   - URL: `http://localhost:3000`
   - Username: `admin`
   - Password: `admin` (or set via `GRAFANA_PASSWORD`)

3. **Prometheus is pre-configured** as a data source

### Creating Dashboards

#### Example: Request Rate Dashboard

1. Create new dashboard
2. Add panel
3. Query:
   ```promql
   rate(http_requests_total[5m])
   ```

#### Example: API Latency Dashboard

Query:
```promql
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
```

#### Example: Token Usage Dashboard

Query:
```promql
rate(anthropic_tokens_used_total[1h])
```

### Useful Queries

**Request rate by status code:**
```promql
sum by (status) (rate(http_requests_total[5m]))
```

**Notion API error rate:**
```promql
rate(notion_api_requests_total{status="error"}[5m])
```

**Average poll cycle duration:**
```promql
avg(poll_cycle_duration_seconds)
```

**Active vs failed analyses:**
```promql
sum by (status) (agent_analyses_total)
```

**Token cost estimation:**
```promql
# Input tokens (typically ~$3 per 1M tokens for Sonnet)
rate(anthropic_tokens_used_total{type="input"}[1h]) * 3600 * 24 * 3 / 1000000

# Output tokens (typically ~$15 per 1M tokens for Sonnet)
rate(anthropic_tokens_used_total{type="output"}[1h]) * 3600 * 24 * 15 / 1000000
```

---

## Logging

### Configuration

Logging is configured via environment variables:

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# JSON logs for production (easier to parse)
JSON_LOGS=true
```

### Log Formats

**Human-readable (development):**
```
2025-01-27 10:30:45 | INFO     | notion_poller:poll_cycle - Poll cycle completed
```

**JSON (production):**
```json
{
  "timestamp": "2025-01-27T10:30:45Z",
  "level": "INFO",
  "message": "Poll cycle completed",
  "module": "notion_poller",
  "function": "poll_cycle",
  "line": 123,
  "extra": {
    "items_processed": 5,
    "duration": 2.3
  }
}
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (failures)
- **CRITICAL**: Critical errors (service disruption)

### Log Files

Logs are written to:
- **Console**: stdout (captured by Railway)
- **File**: `logs/app.log` (with rotation)

**Rotation policy:**
- Rotate at 100 MB
- Keep 30 days
- Compress old logs (gzip)

### Adding Context to Logs

```python
from loguru import logger

# Simple log
logger.info("Processing intent")

# With context
logger.info(
    "Processing intent",
    extra={
        "intent_id": "123",
        "agent": "growth",
        "duration": 2.5
    }
)

# With exception
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")
```

### Log Aggregation

For production, use a log aggregation service:

**Options:**
- **Railway Logs**: Built-in (no setup needed)
- **Datadog**: Full observability platform
- **Elasticsearch + Kibana**: Self-hosted
- **Logtail**: Simple cloud logging

**Integration:**

Most services can ingest JSON logs from stdout. With `JSON_LOGS=true`, logs are already formatted for easy parsing.

---

## Alerting

### Alert Rules

Pre-configured alerts are in `config/alerts.yaml`.

#### Critical Alerts

**Service Down:**
```yaml
- alert: ServiceDown
  expr: up{job="executive-mind-matrix"} == 0
  for: 1m
```

**Poller Not Running:**
```yaml
- alert: PollerNotRunning
  expr: poller_status == 0
  for: 5m
```

#### Warning Alerts

**High Error Rate:**
```yaml
- alert: HighErrorRate
  expr: rate(errors_total[5m]) > 0.1
  for: 5m
```

**High API Latency:**
```yaml
- alert: HighNotionAPILatency
  expr: histogram_quantile(0.95, rate(notion_api_request_duration_seconds_bucket[5m])) > 5
  for: 10m
```

**High Token Usage:**
```yaml
- alert: HighTokenUsage
  expr: rate(anthropic_tokens_used_total[1h]) > 100000
  for: 1h
```

### Alert Channels

#### Railway Webhooks

1. Go to Railway Project Settings
2. Click "Webhooks"
3. Add webhook URL
4. Configure for deployment events

**Slack integration:**
```
https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### Sentry Alerts

1. Go to Sentry Project Settings
2. Click "Alerts"
3. Create new alert rule
4. Configure conditions and actions

**Example conditions:**
- Error count > 10 in 5 minutes
- New issue detected
- Performance degradation

#### Prometheus Alertmanager

For self-hosted Prometheus:

1. Install Alertmanager
2. Configure receivers (email, Slack, PagerDuty)
3. Update `prometheus.yml` with Alertmanager URL
4. Load alert rules from `config/alerts.yaml`

**Example Alertmanager config:**
```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        text: '{{ .CommonAnnotations.summary }}'
```

### Testing Alerts

**Trigger test error:**
```python
# Add to your code temporarily
@app.get("/test-error")
async def test_error():
    raise Exception("Test error for monitoring")
```

**Trigger high latency:**
```python
@app.get("/test-slow")
async def test_slow():
    import time
    time.sleep(10)
    return {"status": "slow"}
```

---

## Monitoring Checklist

After deployment, verify:

- [ ] Sentry is receiving events
- [ ] Metrics endpoint is accessible
- [ ] Logs are being generated
- [ ] Poller status metric is updating
- [ ] Request metrics are incrementing
- [ ] API metrics are recording
- [ ] Error metrics are available
- [ ] Alerts are configured
- [ ] Dashboards are working (if using Grafana)

---

## Best Practices

### Metrics

- Use labels wisely (high cardinality = high cost)
- Monitor trends over absolute values
- Set up alerts on rates, not counts
- Use histograms for latency tracking

### Logging

- Use structured logging in production
- Include correlation IDs for request tracking
- Log at appropriate levels (don't spam DEBUG in prod)
- Sanitize sensitive data before logging

### Alerts

- Alert on symptoms, not causes
- Use appropriate thresholds (avoid alert fatigue)
- Include runbooks in alert descriptions
- Test alerts regularly

### Performance

- Use lower Sentry sample rates in production
- Aggregate metrics before sending
- Rotate logs to prevent disk issues
- Monitor monitoring overhead

---

## Troubleshooting

### Metrics not appearing

1. Check `ENABLE_METRICS=true`
2. Verify `/metrics` endpoint is accessible
3. Check Prometheus scrape config
4. Review application logs for errors

### Sentry not capturing errors

1. Verify `SENTRY_DSN` is set
2. Check Sentry quota limits
3. Review sample rates
4. Test with manual error trigger

### High memory usage

1. Check log rotation is working
2. Review metrics cardinality
3. Adjust Sentry sample rate
4. Monitor Prometheus retention

### Missing logs

1. Check `LOG_LEVEL` setting
2. Verify log file permissions
3. Check disk space
4. Review log rotation settings

---

## Additional Resources

- [Sentry Python SDK Docs](https://docs.sentry.io/platforms/python/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [FastAPI Monitoring Guide](https://fastapi.tiangolo.com/advanced/monitoring/)

---

**Last Updated**: 2025-01-27
**Version**: 1.0.0
