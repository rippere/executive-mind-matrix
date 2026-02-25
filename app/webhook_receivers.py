"""
Webhook Receivers for External Triggers (P3.1.2)

This module provides webhook endpoints that allow external systems
(Slack, email, Zapier, etc.) to create intents in the System Inbox.

Security Features:
- Slack: HMAC signature validation
- Generic: API key authentication
- Rate limiting (inherited from main app)
- Comprehensive error handling and logging
"""

import hashlib
import hmac
import time
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import parse_qs

from fastapi import APIRouter, Request, HTTPException, status, Header
from fastapi.responses import JSONResponse
from loguru import logger
from notion_client import AsyncClient
from pydantic import BaseModel, Field, validator

from config.settings import settings
from app.monitoring import metrics


# ----------------------------------------------------------------------------------
# Request Models
# ----------------------------------------------------------------------------------

class SlackCommandPayload(BaseModel):
    """Slack slash command payload model"""
    token: Optional[str] = None
    team_id: Optional[str] = None
    team_domain: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    command: Optional[str] = None
    text: str
    response_url: Optional[str] = None
    trigger_id: Optional[str] = None


class EmailWebhookPayload(BaseModel):
    """Email webhook payload (from Zapier/Make)"""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    from_email: Optional[str] = Field(None, description="Sender email address")
    from_name: Optional[str] = Field(None, description="Sender name")
    received_date: Optional[str] = Field(None, description="Email received timestamp")

    @validator('body')
    def clean_body(cls, v):
        """Clean up email body (strip excessive whitespace)"""
        if v:
            return v.strip()
        return v


class GenericWebhookPayload(BaseModel):
    """Generic webhook payload for any external trigger"""
    title: str = Field(..., description="Intent title", max_length=200)
    content: str = Field(..., description="Intent content/description")
    priority: Optional[str] = Field("medium", description="Priority level")
    source_system: Optional[str] = Field(None, description="Source system name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority level"""
        if v and v.lower() not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v.lower() if v else 'medium'


# ----------------------------------------------------------------------------------
# Router Setup
# ----------------------------------------------------------------------------------

router = APIRouter()

# Initialize Notion client
notion_client = AsyncClient(auth=settings.notion_api_key)


# ----------------------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------------------

async def create_system_inbox_entry(
    content: str,
    source: str,
    source_metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create an entry in the System Inbox database.

    Args:
        content: The intent content
        source: Source tag (Slack, Email, Webhook, etc.)
        source_metadata: Optional metadata about the source

    Returns:
        Created page ID

    Raises:
        HTTPException: If creation fails
    """
    try:
        logger.info(f"Creating System Inbox entry from {source}")

        # Build properties
        properties = {
            "Content": {
                "rich_text": [{"text": {"content": content[:2000]}}]  # Notion limit
            },
            "Source": {
                "select": {"name": source}
            },
            "Received_Date": {
                "date": {"start": datetime.now().date().isoformat()}
            },
            "Status": {
                "select": {"name": "Unprocessed"}
            }
        }

        # Add metadata if provided
        if source_metadata:
            metadata_text = "\n".join([f"{k}: {v}" for k, v in source_metadata.items()])
            properties["Source_Metadata"] = {
                "rich_text": [{"text": {"content": metadata_text[:2000]}}]
            }

        # Create page
        response = await notion_client.pages.create(
            parent={"database_id": settings.notion_db_system_inbox},
            properties=properties
        )

        page_id = response["id"]
        logger.success(f"Created System Inbox entry: {page_id[:8]} from {source}")

        # Record metrics
        metrics.record_item_processed(f"webhook_{source.lower()}")

        return page_id

    except Exception as e:
        logger.error(f"Failed to create System Inbox entry from {source}: {e}")
        metrics.record_error("inbox_creation_failed", "webhook")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create inbox entry: {str(e)}"
        )


def verify_slack_signature(
    timestamp: str,
    body: bytes,
    signature: str,
    signing_secret: str
) -> bool:
    """
    Verify Slack request signature using HMAC SHA256.

    Args:
        timestamp: Request timestamp from X-Slack-Request-Timestamp header
        body: Raw request body
        signature: Signature from X-Slack-Signature header
        signing_secret: Slack signing secret

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Reject old requests (replay attack prevention)
        request_timestamp = int(timestamp)
        if abs(time.time() - request_timestamp) > 60 * 5:  # 5 minutes
            logger.warning(f"Slack request timestamp too old: {timestamp}")
            return False

        # Create signature base string
        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"

        # Calculate expected signature
        expected_signature = 'v0=' + hmac.new(
            signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)

    except Exception as e:
        logger.error(f"Slack signature verification failed: {e}")
        return False


# ----------------------------------------------------------------------------------
# Webhook Endpoints
# ----------------------------------------------------------------------------------

@router.post("/slack", status_code=status.HTTP_200_OK)
async def slack_webhook(
    request: Request,
    x_slack_request_timestamp: Optional[str] = Header(None),
    x_slack_signature: Optional[str] = Header(None)
):
    """
    Receive Slack slash commands and create System Inbox entries.

    Example Slack command: /intent Create a new strategic initiative

    Security: Validates Slack HMAC signature to ensure request authenticity.

    Returns:
        Immediate response to Slack (required within 3 seconds)
    """
    if not settings.enable_webhooks:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhooks are disabled"
        )

    try:
        # Get raw body for signature verification
        body = await request.body()

        # Verify Slack signature if signing secret is configured
        if settings.slack_signing_secret:
            if not x_slack_request_timestamp or not x_slack_signature:
                logger.warning("Missing Slack signature headers")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing signature headers"
                )

            if not verify_slack_signature(
                x_slack_request_timestamp,
                body,
                x_slack_signature,
                settings.slack_signing_secret
            ):
                logger.warning("Invalid Slack signature")
                metrics.record_error("invalid_signature", "webhook_slack")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature"
                )

            logger.debug("Slack signature verified successfully")
        else:
            logger.warning("Slack signing secret not configured - skipping signature verification")

        # Parse form data
        form_data = parse_qs(body.decode('utf-8'))

        # Extract text from command
        text_list = form_data.get('text', [''])
        text = text_list[0] if text_list else ''

        if not text or not text.strip():
            return JSONResponse(
                content={
                    "response_type": "ephemeral",
                    "text": "❌ Please provide intent text. Usage: /intent <your intent description>"
                }
            )

        # Extract metadata
        user_name = form_data.get('user_name', [None])[0]
        channel_name = form_data.get('channel_name', [None])[0]
        command = form_data.get('command', [None])[0]

        metadata = {
            "user": user_name,
            "channel": channel_name,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }

        # Create System Inbox entry
        page_id = await create_system_inbox_entry(
            content=text.strip(),
            source="Slack",
            source_metadata=metadata
        )

        # Generate Notion URL
        notion_url = f"https://notion.so/{page_id.replace('-', '')}"

        # Return immediate response to Slack
        return JSONResponse(
            content={
                "response_type": "ephemeral",
                "text": f"✅ Intent created successfully!\n\n*Intent:* {text[:100]}{'...' if len(text) > 100 else ''}\n*Status:* Queued for processing\n*View in Notion:* {notion_url}\n\nYour intent will be processed within the next poll cycle (typically 2 minutes)."
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slack webhook error: {e}")
        metrics.record_error("webhook_failed", "webhook_slack")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "response_type": "ephemeral",
                "text": f"❌ Error creating intent: {str(e)}"
            }
        )


@router.post("/email", status_code=status.HTTP_200_OK)
async def email_webhook(payload: EmailWebhookPayload):
    """
    Receive forwarded emails (via Zapier/Make) and create System Inbox entries.

    Expected payload from Zapier/Make:
    ```json
    {
        "subject": "Email subject",
        "body": "Email content",
        "from_email": "sender@example.com",
        "from_name": "Sender Name",
        "received_date": "2024-01-01T12:00:00Z"
    }
    ```

    Returns:
        Confirmation with created page ID
    """
    if not settings.enable_webhooks:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhooks are disabled"
        )

    try:
        logger.info(f"Received email webhook from {payload.from_email}")

        # Combine subject and body for content
        content = f"Subject: {payload.subject}\n\n{payload.body}"

        # Build metadata
        metadata = {
            "from_email": payload.from_email,
            "from_name": payload.from_name,
            "subject": payload.subject,
            "received_date": payload.received_date or datetime.now().isoformat()
        }

        # Create System Inbox entry
        page_id = await create_system_inbox_entry(
            content=content,
            source="Email",
            source_metadata=metadata
        )

        # Generate Notion URL
        notion_url = f"https://notion.so/{page_id.replace('-', '')}"

        return {
            "status": "success",
            "message": "Email intent created successfully",
            "page_id": page_id,
            "notion_url": notion_url,
            "subject": payload.subject,
            "next_steps": "Intent will be processed in the next poll cycle (typically 2 minutes)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email webhook error: {e}")
        metrics.record_error("webhook_failed", "webhook_email")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process email webhook: {str(e)}"
        )


@router.post("/generic", status_code=status.HTTP_200_OK)
async def generic_webhook(
    payload: GenericWebhookPayload,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Generic webhook endpoint for any external trigger.

    Requires API key authentication via X-API-Key header.

    Expected payload:
    ```json
    {
        "title": "Intent title",
        "content": "Intent description and details",
        "priority": "high",  // Optional: low, medium, high
        "source_system": "Custom System",  // Optional
        "metadata": {  // Optional
            "custom_field": "value"
        }
    }
    ```

    Returns:
        Confirmation with created page ID
    """
    if not settings.enable_webhooks:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhooks are disabled"
        )

    # Validate API key
    if settings.webhook_api_key:
        if not x_api_key:
            logger.warning("Generic webhook called without API key")
            metrics.record_error("missing_api_key", "webhook_generic")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-API-Key header"
            )

        # Use constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(x_api_key, settings.webhook_api_key):
            logger.warning("Generic webhook called with invalid API key")
            metrics.record_error("invalid_api_key", "webhook_generic")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    else:
        logger.warning("Webhook API key not configured - skipping authentication")

    try:
        logger.info(f"Received generic webhook: {payload.title}")

        # Combine title and content
        content = f"{payload.title}\n\n{payload.content}"

        # Build metadata
        metadata = {
            "title": payload.title,
            "priority": payload.priority,
            "source_system": payload.source_system or "Generic Webhook",
            "received_timestamp": datetime.now().isoformat()
        }

        # Add custom metadata
        if payload.metadata:
            metadata.update(payload.metadata)

        # Determine source tag
        source = payload.source_system or "Webhook"

        # Create System Inbox entry
        page_id = await create_system_inbox_entry(
            content=content,
            source=source,
            source_metadata=metadata
        )

        # Generate Notion URL
        notion_url = f"https://notion.so/{page_id.replace('-', '')}"

        return {
            "status": "success",
            "message": "Intent created successfully",
            "page_id": page_id,
            "notion_url": notion_url,
            "title": payload.title,
            "priority": payload.priority,
            "next_steps": "Intent will be processed in the next poll cycle (typically 2 minutes)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generic webhook error: {e}")
        metrics.record_error("webhook_failed", "webhook_generic")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process generic webhook: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def webhook_health():
    """
    Health check endpoint for webhook service.

    Returns:
        Service status and configuration
    """
    return {
        "status": "healthy",
        "service": "webhook_receivers",
        "webhooks_enabled": settings.enable_webhooks,
        "endpoints": {
            "slack": {
                "enabled": True,
                "signature_verification": settings.slack_signing_secret is not None
            },
            "email": {
                "enabled": True
            },
            "generic": {
                "enabled": True,
                "api_key_required": settings.webhook_api_key is not None
            }
        },
        "notion_db": {
            "system_inbox": bool(settings.notion_db_system_inbox)
        }
    }
