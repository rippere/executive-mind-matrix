#!/bin/bash
# Webhook Test Examples for P3.1.2
# Quick reference for testing webhook endpoints

# Set your configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
API_KEY="${WEBHOOK_API_KEY:-your_api_key_here}"

echo "============================================"
echo "Webhook Receivers Test Suite (P3.1.2)"
echo "============================================"
echo ""

# 1. Health Check
echo "1. Testing webhook health endpoint..."
curl -X GET "$BASE_URL/webhooks/health" \
  -H "Content-Type: application/json" | jq .
echo ""
echo ""

# 2. Generic Webhook Test
echo "2. Testing generic webhook (with API key)..."
curl -X POST "$BASE_URL/webhooks/generic" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "title": "Test Strategic Intent from Webhook",
    "content": "This is a test intent created via the generic webhook endpoint. It should appear in the System Inbox and be processed in the next poll cycle.",
    "priority": "high",
    "source_system": "Manual Test",
    "metadata": {
      "test_run": true,
      "timestamp": "'$(date -Iseconds)'",
      "tester": "webhook_test_script"
    }
  }' | jq .
echo ""
echo ""

# 3. Email Webhook Test
echo "3. Testing email webhook..."
curl -X POST "$BASE_URL/webhooks/email" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Email Intent",
    "body": "This is a test email intent. It simulates an email forwarded via Zapier or Make.",
    "from_email": "test@example.com",
    "from_name": "Test User",
    "received_date": "'$(date -Iseconds)'"
  }' | jq .
echo ""
echo ""

# 4. Slack Webhook Test (without signature - will fail if SLACK_SIGNING_SECRET is set)
echo "4. Testing Slack webhook (without signature - may fail)..."
echo "   Note: This will fail if SLACK_SIGNING_SECRET is configured."
echo "   For real Slack testing, use the Slack app."
curl -X POST "$BASE_URL/webhooks/slack" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Test+Slack+intent+from+command+line&user_name=test_user&channel_name=test_channel&command=/intent" | jq .
echo ""
echo ""

# 5. Test without API key (should fail for generic webhook)
echo "5. Testing generic webhook without API key (should fail)..."
curl -X POST "$BASE_URL/webhooks/generic" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "This should fail",
    "content": "No API key provided"
  }' | jq .
echo ""
echo ""

# 6. Test with invalid priority (should fail validation)
echo "6. Testing generic webhook with invalid priority (should fail)..."
curl -X POST "$BASE_URL/webhooks/generic" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "title": "Invalid priority test",
    "content": "This has an invalid priority",
    "priority": "super_urgent"
  }' | jq .
echo ""
echo ""

# 7. Test main app health to verify webhook integration
echo "7. Testing main app status (should show webhook_receivers: true)..."
curl -X GET "$BASE_URL/" | jq .
echo ""
echo ""

echo "============================================"
echo "Test Suite Complete"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Check System Inbox in Notion for new entries"
echo "2. Wait for next poll cycle (~2 minutes)"
echo "3. Verify intents are processed correctly"
echo "4. Check logs: logs/app.log"
echo "5. Check metrics: $BASE_URL/metrics"
echo ""
