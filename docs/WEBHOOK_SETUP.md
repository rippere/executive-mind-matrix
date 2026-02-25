# Webhook Receivers Setup Guide (P3.1.2)

## Overview

The Webhook Receivers feature allows external systems (Slack, email via Zapier/Make, or any custom system) to create intents in the System Inbox. This enables seamless integration with your existing workflows.

## Configuration

### Environment Variables

Add these environment variables to your `.env` file:

```bash
# Webhook Configuration (P3.1.2)
ENABLE_WEBHOOKS=true                    # Enable/disable webhook endpoints
SLACK_SIGNING_SECRET=your_secret_here   # Optional: Slack signing secret for signature verification
WEBHOOK_API_KEY=your_api_key_here       # Optional: API key for generic webhook endpoint
```

### Generate API Key

To generate a secure API key for the generic webhook endpoint:

```python
import secrets
api_key = secrets.token_urlsafe(32)
print(api_key)
```

## Available Endpoints

### 1. Slack Webhook (`POST /webhooks/slack`)

Receives Slack slash commands and creates System Inbox entries.

#### Setup in Slack

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create a new app or select existing app
3. Navigate to "Slash Commands"
4. Create a new command:
   - **Command**: `/intent`
   - **Request URL**: `https://your-domain.com/webhooks/slack`
   - **Short Description**: `Create a new strategic intent`
   - **Usage Hint**: `[your intent description]`
5. Navigate to "Basic Information" → "App Credentials"
6. Copy the **Signing Secret** and add to `.env` as `SLACK_SIGNING_SECRET`
7. Install the app to your workspace

#### Usage

In any Slack channel:
```
/intent Create a strategic initiative to improve customer retention
```

Response:
```
✅ Intent created successfully!

Intent: Create a strategic initiative to improve customer retention
Status: Queued for processing
View in Notion: [link]

Your intent will be processed within the next poll cycle (typically 2 minutes).
```

#### Security

- HMAC SHA256 signature verification using Slack signing secret
- Replay attack prevention (rejects requests older than 5 minutes)
- Constant-time signature comparison

---

### 2. Email Webhook (`POST /webhooks/email`)

Receives forwarded emails (via Zapier/Make) and creates System Inbox entries.

#### Setup with Zapier

1. Create a new Zap
2. **Trigger**: Email by Zapier (or Gmail, Outlook, etc.)
3. **Action**: Webhooks by Zapier
   - **Event**: POST
   - **URL**: `https://your-domain.com/webhooks/email`
   - **Payload Type**: JSON
   - **Data**:
     ```json
     {
       "subject": "{{subject}}",
       "body": "{{body_plain}}",
       "from_email": "{{from__email}}",
       "from_name": "{{from__name}}",
       "received_date": "{{date}}"
     }
     ```
4. Test and activate the Zap

#### Setup with Make (Integromat)

1. Create a new scenario
2. **Trigger**: Email (Gmail, Outlook, etc.)
3. **Action**: HTTP - Make a request
   - **URL**: `https://your-domain.com/webhooks/email`
   - **Method**: POST
   - **Headers**:
     - `Content-Type: application/json`
   - **Body**:
     ```json
     {
       "subject": "{{subject}}",
       "body": "{{body}}",
       "from_email": "{{from.address}}",
       "from_name": "{{from.name}}",
       "received_date": "{{date}}"
     }
     ```
4. Test and activate the scenario

#### Example Request

```bash
curl -X POST https://your-domain.com/webhooks/email \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "New product idea",
    "body": "We should consider building a mobile app version",
    "from_email": "john@example.com",
    "from_name": "John Doe",
    "received_date": "2024-01-15T10:30:00Z"
  }'
```

#### Response

```json
{
  "status": "success",
  "message": "Email intent created successfully",
  "page_id": "abc123...",
  "notion_url": "https://notion.so/abc123...",
  "subject": "New product idea",
  "next_steps": "Intent will be processed in the next poll cycle (typically 2 minutes)"
}
```

---

### 3. Generic Webhook (`POST /webhooks/generic`)

Generic webhook endpoint for any external trigger. Requires API key authentication.

#### Setup

1. Generate an API key (see above)
2. Add `WEBHOOK_API_KEY` to your `.env` file
3. Configure your external system to send POST requests to `/webhooks/generic`

#### Request Format

```bash
curl -X POST https://your-domain.com/webhooks/generic \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "title": "Implement new feature",
    "content": "We need to add dark mode support to the application",
    "priority": "high",
    "source_system": "Project Management Tool",
    "metadata": {
      "project_id": "PRJ-123",
      "assignee": "john@example.com",
      "due_date": "2024-02-01"
    }
  }'
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Intent title (max 200 chars) |
| `content` | string | Yes | Intent description/details |
| `priority` | string | No | Priority level: `low`, `medium`, `high` (default: `medium`) |
| `source_system` | string | No | Name of source system |
| `metadata` | object | No | Additional key-value metadata |

#### Response

```json
{
  "status": "success",
  "message": "Intent created successfully",
  "page_id": "abc123...",
  "notion_url": "https://notion.so/abc123...",
  "title": "Implement new feature",
  "priority": "high",
  "next_steps": "Intent will be processed in the next poll cycle (typically 2 minutes)"
}
```

#### Security

- API key authentication via `X-API-Key` header
- Constant-time API key comparison
- Rate limiting (inherited from application-wide settings)

---

### 4. Health Check (`GET /webhooks/health`)

Check webhook service status and configuration.

#### Request

```bash
curl https://your-domain.com/webhooks/health
```

#### Response

```json
{
  "status": "healthy",
  "service": "webhook_receivers",
  "webhooks_enabled": true,
  "endpoints": {
    "slack": {
      "enabled": true,
      "signature_verification": true
    },
    "email": {
      "enabled": true
    },
    "generic": {
      "enabled": true,
      "api_key_required": true
    }
  },
  "notion_db": {
    "system_inbox": true
  }
}
```

---

## Integration Examples

### IFTTT Integration

Use the generic webhook endpoint with IFTTT:

1. Create a new applet
2. **If This**: Choose your trigger (e.g., "New email with specific subject")
3. **Then That**: Webhooks - Make a web request
   - **URL**: `https://your-domain.com/webhooks/generic`
   - **Method**: POST
   - **Content Type**: `application/json`
   - **Additional Headers**: `X-API-Key: your_api_key_here`
   - **Body**:
     ```json
     {
       "title": "{{Subject}}",
       "content": "{{Body}}",
       "priority": "medium",
       "source_system": "IFTTT"
     }
     ```

### n8n Integration

1. Create a new workflow
2. **Trigger**: Choose your trigger node
3. **HTTP Request Node**:
   - **Method**: POST
   - **URL**: `https://your-domain.com/webhooks/generic`
   - **Authentication**: Generic Credential Type → Header Auth
     - **Name**: `X-API-Key`
     - **Value**: `your_api_key_here`
   - **Body Content Type**: JSON
   - **Body**: Map your trigger fields to the webhook schema

### Notion Automation (Button)

You can create a button in Notion that triggers the webhook:

```javascript
// Notion Button Action (using Notion API)
fetch('https://your-domain.com/webhooks/generic', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your_api_key_here'
  },
  body: JSON.stringify({
    title: 'Button-triggered intent',
    content: 'This was created from a Notion button',
    priority: 'medium',
    source_system: 'Notion Button'
  })
});
```

---

## Monitoring

### Prometheus Metrics

The webhook endpoints automatically record Prometheus metrics:

- `items_processed_total{type="webhook_slack"}` - Number of Slack intents processed
- `items_processed_total{type="webhook_email"}` - Number of email intents processed
- `items_processed_total{type="webhook_webhook"}` - Number of generic webhook intents processed
- `errors_total{type="*",component="webhook*"}` - Webhook-related errors

### Logs

All webhook activity is logged with structured logging:

```log
2024-01-15 10:30:00 | INFO | webhook_receivers:slack_webhook - Received Slack webhook
2024-01-15 10:30:00 | DEBUG | webhook_receivers:verify_slack_signature - Slack signature verified successfully
2024-01-15 10:30:00 | INFO | webhook_receivers:create_system_inbox_entry - Creating System Inbox entry from Slack
2024-01-15 10:30:01 | SUCCESS | webhook_receivers:create_system_inbox_entry - Created System Inbox entry: abc123 from Slack
```

---

## Troubleshooting

### Slack: "Invalid signature" error

1. Verify `SLACK_SIGNING_SECRET` is correct in `.env`
2. Check that the request is reaching your server within 5 minutes (clock sync issues)
3. Ensure your server is receiving the raw request body (not parsed)

### Generic Webhook: 401 Unauthorized

1. Verify `WEBHOOK_API_KEY` is set in `.env`
2. Check that `X-API-Key` header is included in the request
3. Ensure the API key matches exactly (case-sensitive)

### Webhook: "Webhooks are disabled"

1. Verify `ENABLE_WEBHOOKS=true` in `.env`
2. Restart the application to reload settings

### Intent not appearing in System Inbox

1. Check the webhook response - was it successful?
2. Verify the Notion database ID is correct: `NOTION_DB_SYSTEM_INBOX`
3. Check application logs for errors
4. Wait for the next poll cycle (up to 2 minutes)

### Rate limiting

If you're hitting rate limits:
1. Adjust `RATE_LIMIT_PER_MINUTE` in `.env`
2. Consider batching requests
3. Use background processing for high-volume integrations

---

## Security Best Practices

1. **Always use HTTPS** in production
2. **Keep secrets secure**: Never commit `.env` to version control
3. **Rotate API keys** regularly
4. **Use Slack signature verification** - don't skip it
5. **Monitor webhook logs** for suspicious activity
6. **Implement IP whitelisting** if possible (via reverse proxy)
7. **Set appropriate rate limits** to prevent abuse

---

## Testing

### Test Slack Webhook Locally

```bash
# Generate test signature (requires Python)
python -c "
import hmac, hashlib, time
timestamp = str(int(time.time()))
body = 'text=test+intent'
secret = 'your_slack_signing_secret'
sig_basestring = f'v0:{timestamp}:{body}'
signature = 'v0=' + hmac.new(secret.encode(), sig_basestring.encode(), hashlib.sha256).hexdigest()
print(f'X-Slack-Request-Timestamp: {timestamp}')
print(f'X-Slack-Signature: {signature}')
"

# Then make request
curl -X POST http://localhost:8000/webhooks/slack \
  -H "X-Slack-Request-Timestamp: <timestamp>" \
  -H "X-Slack-Signature: <signature>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=test+intent"
```

### Test Email Webhook

```bash
curl -X POST http://localhost:8000/webhooks/email \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Intent",
    "body": "This is a test intent from the webhook",
    "from_email": "test@example.com"
  }'
```

### Test Generic Webhook

```bash
curl -X POST http://localhost:8000/webhooks/generic \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "title": "Test Intent",
    "content": "This is a test intent",
    "priority": "medium"
  }'
```

---

## API Documentation

Once the application is running, you can view interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Navigate to the "webhooks" tag to see all webhook endpoints with request/response schemas.

---

## Success Criteria

- ✅ Can create intent via Slack webhook
- ✅ Can create intent via email webhook (Zapier/Make)
- ✅ Can create intent via generic webhook
- ✅ Intent appears in System Inbox within 2 minutes (next poll cycle)
- ✅ Proper security validation (Slack HMAC, API key)
- ✅ Detailed logging and error handling
- ✅ Prometheus metrics tracking
- ✅ Comprehensive error messages

---

## Support

For issues or questions:
1. Check the application logs: `logs/app.log`
2. Review Prometheus metrics: `http://localhost:8000/metrics`
3. Test with the health endpoint: `http://localhost:8000/webhooks/health`
4. Consult the interactive API docs: `http://localhost:8000/docs`
