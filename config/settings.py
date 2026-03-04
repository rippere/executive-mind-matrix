from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Notion Configuration
    notion_api_key: str
    notion_db_system_inbox: str
    notion_db_executive_intents: str
    notion_db_action_pipes: str
    notion_db_agent_registry: str
    notion_db_execution_log: str
    notion_db_training_data: str
    notion_db_tasks: str
    notion_db_projects: str
    notion_db_areas: str
    notion_db_nodes: str

    # Anthropic Configuration
    anthropic_api_key: str
    anthropic_model: str = "claude-3-haiku-20240307"

    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    polling_interval_seconds: int = 120

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Monitoring Configuration
    sentry_dsn: Optional[str] = None
    sentry_traces_sample_rate: float = 0.1
    enable_metrics: bool = True
    json_logs: bool = False

    # Security Configuration
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    allowed_origins: list[str] = ["https://web-production-3d888.up.railway.app"]
    api_key_header: str = "X-API-Key"
    api_key: Optional[str] = None

    # Daily Digest Configuration
    digest_enabled: bool = False  # Temporarily disabled for debugging
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None

    # Auto-Dialectic Configuration
    enable_auto_dialectic: bool = True  # Automatically run dialectic for high-impact intents

    # Command Center Auto-Refresh Configuration
    command_center_refresh_enabled: bool = True
    command_center_refresh_interval: int = 15  # minutes

    # Webhook Receivers Configuration (P3.1.2)
    enable_webhooks: bool = True
    slack_signing_secret: Optional[str] = None
    webhook_api_key: Optional[str] = None

    # Notion Page IDs (workspace-specific, set via env)
    notion_page_command_center: Optional[str] = None
    notion_agent_entrepreneur_id: Optional[str] = None
    notion_agent_quant_id: Optional[str] = None
    notion_agent_auditor_id: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow environment variables to override .env file
        # This is crucial for Railway deployment
        env_prefix = ""


# Initialize settings with better error handling
try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"FATAL: Failed to load settings: {e}", file=sys.stderr)
    print("Required environment variables:", file=sys.stderr)
    print("- NOTION_API_KEY", file=sys.stderr)
    print("- ANTHROPIC_API_KEY", file=sys.stderr)
    print("- NOTION_DB_* (11 database IDs)", file=sys.stderr)
    raise
