# Webhook Receivers - Quick Reference Card

## Endpoints

### Health Check
```bash
GET /webhooks/health
```

### Slack Webhook
```bash
POST /webhooks/slack
Content-Type: application/x-www-form-urlencoded
X-Slack-Request-Timestamp: <timestamp>
X-Slack-Signature: <signature>

text=Create+strategic+initiative
```

### Email Webhook
```bash
POST /webhooks/email
Content-Type: application/json

{
  "subject": "New Idea",
  "body": "Description of the idea",
  "from_email": "user@example.com"
}
```

### Generic Webhook
```bash
POST /webhooks/generic
Content-Type: application/json
X-API-Key: <your_api_key>

{
  "title": "Intent Title",
  "content": "Intent description",
  "priority": "high"
}
```

## Environment Variables

```bash
ENABLE_WEBHOOKS=true
SLACK_SIGNING_SECRET=<slack_secret>
WEBHOOK_API_KEY=<api_key>
```

## Generate API Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Test Commands

### Health Check
```bash
curl http://localhost:8000/webhooks/health
```

### Generic Webhook Test
```bash
curl -X POST http://localhost:8000/webhooks/generic \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"title":"Test","content":"Test content","priority":"medium"}'
```

### Email Webhook Test
```bash
curl -X POST http://localhost:8000/webhooks/email \
  -H "Content-Type: application/json" \
  -d '{"subject":"Test","body":"Test body","from_email":"test@example.com"}'
```

## Response Format

### Success
```json
{
  "status": "success",
  "message": "Intent created successfully",
  "page_id": "abc123...",
  "notion_url": "https://notion.so/abc123...",
  "next_steps": "Intent will be processed in the next poll cycle"
}
```

### Error
```json
{
  "detail": "Error message"
}
```

## Priority Levels

- `low`
- `medium` (default)
- `high`

## Monitoring

### Metrics
```bash
curl http://localhost:8000/metrics | grep webhook
```

### Logs
```bash
tail -f logs/app.log | grep webhook
```

## URLs (Production)

Replace `localhost:8000` with your domain:

- Slack: `https://your-domain.com/webhooks/slack`
- Email: `https://your-domain.com/webhooks/email`
- Generic: `https://your-domain.com/webhooks/generic`
- Health: `https://your-domain.com/webhooks/health`

## Common Issues

| Issue | Solution |
|-------|----------|
| 503: Webhooks disabled | Set `ENABLE_WEBHOOKS=true` |
| 401: Unauthorized | Check API key in `X-API-Key` header |
| 401: Invalid signature | Verify `SLACK_SIGNING_SECRET` |
| 422: Validation error | Check payload format |

## Documentation

- Full Setup Guide: `docs/WEBHOOK_SETUP.md`
- Implementation Summary: `docs/P3.1.2_IMPLEMENTATION_SUMMARY.md`
- Test Suite: `docs/WEBHOOK_TEST_EXAMPLES.sh`
- Interactive API Docs: `http://localhost:8000/docs`
