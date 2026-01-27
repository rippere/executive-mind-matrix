"""
Unit tests for config/settings.py

Tests configuration loading, validation, and environment variable handling.
"""

import pytest
from unittest.mock import patch
import os

from config.settings import Settings


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_required_fields(self):
        """Test that required fields must be present."""
        with pytest.raises(Exception):
            # Should fail without required environment variables
            Settings()

    def test_settings_from_env(self, monkeypatch):
        """Test loading settings from environment variables."""
        # Set required environment variables
        env_vars = {
            "NOTION_API_KEY": "test_notion_key",
            "NOTION_DB_SYSTEM_INBOX": "inbox_db_id",
            "NOTION_DB_EXECUTIVE_INTENTS": "intents_db_id",
            "NOTION_DB_ACTION_PIPES": "pipes_db_id",
            "NOTION_DB_AGENT_REGISTRY": "registry_db_id",
            "NOTION_DB_EXECUTION_LOG": "execution_db_id",
            "NOTION_DB_TRAINING_DATA": "training_db_id",
            "ANTHROPIC_API_KEY": "test_anthropic_key"
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        assert settings.notion_api_key == "test_notion_key"
        assert settings.anthropic_api_key == "test_anthropic_key"
        assert settings.notion_db_system_inbox == "inbox_db_id"

    def test_settings_default_values(self, monkeypatch):
        """Test that default values are applied correctly."""
        # Set required fields
        required = {
            "NOTION_API_KEY": "key1",
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "NOTION_DB_EXECUTIVE_INTENTS": "db2",
            "NOTION_DB_ACTION_PIPES": "db3",
            "NOTION_DB_AGENT_REGISTRY": "db4",
            "NOTION_DB_EXECUTION_LOG": "db5",
            "NOTION_DB_TRAINING_DATA": "db6",
            "ANTHROPIC_API_KEY": "key2"
        }

        for key, value in required.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        # Test default values
        assert settings.anthropic_model == "claude-3-haiku-20240307"
        assert settings.environment == "development"
        assert settings.log_level == "INFO"
        assert settings.polling_interval_seconds == 120
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000

    def test_settings_override_defaults(self, monkeypatch):
        """Test that environment variables override defaults."""
        required = {
            "NOTION_API_KEY": "key1",
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "NOTION_DB_EXECUTIVE_INTENTS": "db2",
            "NOTION_DB_ACTION_PIPES": "db3",
            "NOTION_DB_AGENT_REGISTRY": "db4",
            "NOTION_DB_EXECUTION_LOG": "db5",
            "NOTION_DB_TRAINING_DATA": "db6",
            "ANTHROPIC_API_KEY": "key2",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "WARNING",
            "POLLING_INTERVAL_SECONDS": "60",
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "ANTHROPIC_MODEL": "claude-3-sonnet-20240229"
        }

        for key, value in required.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        assert settings.environment == "production"
        assert settings.log_level == "WARNING"
        assert settings.polling_interval_seconds == 60
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.anthropic_model == "claude-3-sonnet-20240229"

    def test_settings_case_insensitive(self, monkeypatch):
        """Test that environment variables are case insensitive."""
        required = {
            "notion_api_key": "key1",  # lowercase
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "notion_db_executive_intents": "db2",  # lowercase
            "NOTION_DB_ACTION_PIPES": "db3",
            "notion_db_agent_registry": "db4",  # lowercase
            "NOTION_DB_EXECUTION_LOG": "db5",
            "notion_db_training_data": "db6",  # lowercase
            "anthropic_api_key": "key2"  # lowercase
        }

        for key, value in required.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        assert settings.notion_api_key == "key1"
        assert settings.anthropic_api_key == "key2"

    def test_settings_notion_database_ids(self, monkeypatch):
        """Test all Notion database IDs are loaded."""
        db_ids = {
            "NOTION_API_KEY": "key",
            "NOTION_DB_SYSTEM_INBOX": "inbox_id",
            "NOTION_DB_EXECUTIVE_INTENTS": "intents_id",
            "NOTION_DB_ACTION_PIPES": "pipes_id",
            "NOTION_DB_AGENT_REGISTRY": "registry_id",
            "NOTION_DB_EXECUTION_LOG": "execution_id",
            "NOTION_DB_TRAINING_DATA": "training_id",
            "ANTHROPIC_API_KEY": "key2"
        }

        for key, value in db_ids.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        assert settings.notion_db_system_inbox == "inbox_id"
        assert settings.notion_db_executive_intents == "intents_id"
        assert settings.notion_db_action_pipes == "pipes_id"
        assert settings.notion_db_agent_registry == "registry_id"
        assert settings.notion_db_execution_log == "execution_id"
        assert settings.notion_db_training_data == "training_id"

    def test_settings_type_conversion(self, monkeypatch):
        """Test that types are converted correctly from strings."""
        required = {
            "NOTION_API_KEY": "key1",
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "NOTION_DB_EXECUTIVE_INTENTS": "db2",
            "NOTION_DB_ACTION_PIPES": "db3",
            "NOTION_DB_AGENT_REGISTRY": "db4",
            "NOTION_DB_EXECUTION_LOG": "db5",
            "NOTION_DB_TRAINING_DATA": "db6",
            "ANTHROPIC_API_KEY": "key2",
            "POLLING_INTERVAL_SECONDS": "300",  # String that should become int
            "PORT": "8080"  # String that should become int
        }

        for key, value in required.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        assert isinstance(settings.polling_interval_seconds, int)
        assert settings.polling_interval_seconds == 300

        assert isinstance(settings.port, int)
        assert settings.port == 8080

    def test_settings_singleton_pattern(self):
        """Test that importing settings uses the same instance."""
        from config.settings import settings as settings1
        from config.settings import settings as settings2

        # Both imports should reference the same object
        assert settings1 is settings2

    def test_settings_env_file_loading(self, tmp_path, monkeypatch):
        """Test loading settings from .env file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_content = """
NOTION_API_KEY=env_file_notion_key
NOTION_DB_SYSTEM_INBOX=env_file_db1
NOTION_DB_EXECUTIVE_INTENTS=env_file_db2
NOTION_DB_ACTION_PIPES=env_file_db3
NOTION_DB_AGENT_REGISTRY=env_file_db4
NOTION_DB_EXECUTION_LOG=env_file_db5
NOTION_DB_TRAINING_DATA=env_file_db6
ANTHROPIC_API_KEY=env_file_anthropic_key
ENVIRONMENT=testing
LOG_LEVEL=DEBUG
"""
        env_file.write_text(env_content)

        # Change to the temp directory so .env is found
        monkeypatch.chdir(tmp_path)

        settings = Settings()

        assert settings.notion_api_key == "env_file_notion_key"
        assert settings.environment == "testing"
        assert settings.log_level == "DEBUG"

    def test_settings_validation_empty_strings(self, monkeypatch):
        """Test that empty strings are not accepted for required fields."""
        env_vars = {
            "NOTION_API_KEY": "",  # Empty string
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "NOTION_DB_EXECUTIVE_INTENTS": "db2",
            "NOTION_DB_ACTION_PIPES": "db3",
            "NOTION_DB_AGENT_REGISTRY": "db4",
            "NOTION_DB_EXECUTION_LOG": "db5",
            "NOTION_DB_TRAINING_DATA": "db6",
            "ANTHROPIC_API_KEY": "key2"
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(Exception):
            Settings()


class TestSettingsIntegration:
    """Integration tests for settings in actual usage scenarios."""

    def test_settings_used_for_notion_client(self, monkeypatch):
        """Test settings can be used to initialize Notion client."""
        required = {
            "NOTION_API_KEY": "test_key_123",
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "NOTION_DB_EXECUTIVE_INTENTS": "db2",
            "NOTION_DB_ACTION_PIPES": "db3",
            "NOTION_DB_AGENT_REGISTRY": "db4",
            "NOTION_DB_EXECUTION_LOG": "db5",
            "NOTION_DB_TRAINING_DATA": "db6",
            "ANTHROPIC_API_KEY": "key2"
        }

        for key, value in required.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        # Test that the API key is valid format
        assert len(settings.notion_api_key) > 0
        assert isinstance(settings.notion_api_key, str)

    def test_settings_used_for_anthropic_client(self, monkeypatch):
        """Test settings can be used to initialize Anthropic client."""
        required = {
            "NOTION_API_KEY": "key1",
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "NOTION_DB_EXECUTIVE_INTENTS": "db2",
            "NOTION_DB_ACTION_PIPES": "db3",
            "NOTION_DB_AGENT_REGISTRY": "db4",
            "NOTION_DB_EXECUTION_LOG": "db5",
            "NOTION_DB_TRAINING_DATA": "db6",
            "ANTHROPIC_API_KEY": "sk-ant-test123"
        }

        for key, value in required.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        assert settings.anthropic_api_key.startswith("sk-ant-")
        assert settings.anthropic_model in [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229"
        ]

    def test_settings_polling_interval_reasonable(self, monkeypatch):
        """Test polling interval is set to reasonable value."""
        required = {
            "NOTION_API_KEY": "key1",
            "NOTION_DB_SYSTEM_INBOX": "db1",
            "NOTION_DB_EXECUTIVE_INTENTS": "db2",
            "NOTION_DB_ACTION_PIPES": "db3",
            "NOTION_DB_AGENT_REGISTRY": "db4",
            "NOTION_DB_EXECUTION_LOG": "db5",
            "NOTION_DB_TRAINING_DATA": "db6",
            "ANTHROPIC_API_KEY": "key2",
            "POLLING_INTERVAL_SECONDS": "120"
        }

        for key, value in required.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        # Polling interval should be reasonable (not too fast, not too slow)
        assert 1 <= settings.polling_interval_seconds <= 3600
