#!/usr/bin/env python3

"""
Environment variable validation script for Executive Mind Matrix.
Validates that all required environment variables are set and properly formatted.
"""

import os
import sys
import re
from typing import Dict, List, Tuple
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


class EnvValidator:
    """Environment variable validator"""

    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.env_vars: Dict[str, str] = {}

    def load_env_file(self) -> bool:
        """Load environment variables from .env file"""
        env_path = Path(self.env_file)

        if not env_path.exists():
            self.errors.append(f"{self.env_file} file not found")
            return False

        try:
            with open(env_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        self.env_vars[key] = value
                    else:
                        self.warnings.append(
                            f"Line {line_num}: Invalid format (expected KEY=VALUE)"
                        )

            return True

        except Exception as e:
            self.errors.append(f"Error reading {self.env_file}: {str(e)}")
            return False

    def validate_required_vars(self) -> bool:
        """Validate that all required environment variables are set"""
        required_vars = [
            # Notion Configuration
            ("NOTION_API_KEY", self._validate_notion_key),
            ("NOTION_DB_SYSTEM_INBOX", self._validate_notion_db_id),
            ("NOTION_DB_EXECUTIVE_INTENTS", self._validate_notion_db_id),
            ("NOTION_DB_ACTION_PIPES", self._validate_notion_db_id),
            ("NOTION_DB_AGENT_REGISTRY", self._validate_notion_db_id),
            ("NOTION_DB_EXECUTION_LOG", self._validate_notion_db_id),
            ("NOTION_DB_TRAINING_DATA", self._validate_notion_db_id),

            # Anthropic Configuration
            ("ANTHROPIC_API_KEY", self._validate_anthropic_key),
            ("ANTHROPIC_MODEL", self._validate_anthropic_model),
        ]

        all_valid = True

        for var_name, validator in required_vars:
            value = self.env_vars.get(var_name)

            if not value:
                self.errors.append(f"{var_name} is not set")
                all_valid = False
            elif not validator(var_name, value):
                all_valid = False

        return all_valid

    def validate_optional_vars(self):
        """Validate optional environment variables if they are set"""
        optional_vars = [
            ("ENVIRONMENT", self._validate_environment),
            ("LOG_LEVEL", self._validate_log_level),
            ("POLLING_INTERVAL_SECONDS", self._validate_positive_int),
            ("HOST", self._validate_host),
            ("PORT", self._validate_port),
            ("SENTRY_DSN", self._validate_sentry_dsn),
            ("RATE_LIMIT_PER_MINUTE", self._validate_positive_int),
        ]

        for var_name, validator in optional_vars:
            value = self.env_vars.get(var_name)
            if value:
                validator(var_name, value)

    def _validate_notion_key(self, name: str, value: str) -> bool:
        """Validate Notion API key format"""
        if value.startswith('secret_') and len(value) > 20:
            return True
        elif 'xxxx' in value or 'your' in value.lower():
            self.errors.append(f"{name} appears to be a placeholder value")
            return False
        else:
            self.warnings.append(
                f"{name} format may be incorrect (expected: secret_...)"
            )
            return True

    def _validate_notion_db_id(self, name: str, value: str) -> bool:
        """Validate Notion database ID format"""
        # Notion database IDs are 32 characters (hex)
        if re.match(r'^[a-f0-9]{32}$', value):
            return True
        elif 'xxxx' in value or 'your' in value.lower():
            self.errors.append(f"{name} appears to be a placeholder value")
            return False
        else:
            self.warnings.append(
                f"{name} format may be incorrect (expected: 32 hex characters)"
            )
            return True

    def _validate_anthropic_key(self, name: str, value: str) -> bool:
        """Validate Anthropic API key format"""
        if value.startswith('sk-ant-') and len(value) > 20:
            return True
        elif 'xxxx' in value or 'your' in value.lower():
            self.errors.append(f"{name} appears to be a placeholder value")
            return False
        else:
            self.errors.append(
                f"{name} format is incorrect (expected: sk-ant-...)"
            )
            return False

    def _validate_anthropic_model(self, name: str, value: str) -> bool:
        """Validate Anthropic model name"""
        valid_models = [
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20250219",
            "claude-3-opus-20240229",
        ]

        if value in valid_models:
            return True
        else:
            self.warnings.append(
                f"{name} '{value}' may not be a valid model name. "
                f"Valid models: {', '.join(valid_models)}"
            )
            return True

    def _validate_environment(self, name: str, value: str) -> bool:
        """Validate environment setting"""
        valid_envs = ["development", "staging", "production"]

        if value in valid_envs:
            if value == "production":
                self.warnings.append(
                    "ENVIRONMENT is set to 'production'. "
                    "Ensure all production settings are configured."
                )
            return True
        else:
            self.warnings.append(
                f"{name} '{value}' is not a standard environment. "
                f"Valid values: {', '.join(valid_envs)}"
            )
            return True

    def _validate_log_level(self, name: str, value: str) -> bool:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        if value.upper() in valid_levels:
            return True
        else:
            self.warnings.append(
                f"{name} '{value}' is not a valid log level. "
                f"Valid values: {', '.join(valid_levels)}"
            )
            return True

    def _validate_positive_int(self, name: str, value: str) -> bool:
        """Validate positive integer"""
        try:
            int_value = int(value)
            if int_value > 0:
                return True
            else:
                self.errors.append(f"{name} must be a positive integer")
                return False
        except ValueError:
            self.errors.append(f"{name} must be an integer")
            return False

    def _validate_host(self, name: str, value: str) -> bool:
        """Validate host address"""
        if value in ["0.0.0.0", "127.0.0.1", "localhost"]:
            return True
        elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value):
            return True
        else:
            self.warnings.append(
                f"{name} '{value}' may not be a valid host address"
            )
            return True

    def _validate_port(self, name: str, value: str) -> bool:
        """Validate port number"""
        try:
            port = int(value)
            if 1 <= port <= 65535:
                return True
            else:
                self.errors.append(f"{name} must be between 1 and 65535")
                return False
        except ValueError:
            self.errors.append(f"{name} must be an integer")
            return False

    def _validate_sentry_dsn(self, name: str, value: str) -> bool:
        """Validate Sentry DSN format"""
        if value.startswith('https://') and '@' in value:
            return True
        else:
            self.warnings.append(
                f"{name} format may be incorrect (expected: https://...@...)"
            )
            return True

    def check_security_issues(self):
        """Check for common security issues"""
        # Check if DEBUG mode is enabled in production
        if self.env_vars.get('ENVIRONMENT') == 'production':
            if self.env_vars.get('LOG_LEVEL') == 'DEBUG':
                self.warnings.append(
                    "LOG_LEVEL is set to DEBUG in production environment"
                )

        # Check if API keys are exposed
        for key, value in self.env_vars.items():
            if 'KEY' in key or 'SECRET' in key or 'TOKEN' in key:
                if len(value) < 20:
                    self.warnings.append(
                        f"{key} seems too short for a secure API key"
                    )

    def print_results(self):
        """Print validation results"""
        print("\n" + "=" * 50)
        print("Environment Variable Validation Results")
        print("=" * 50 + "\n")

        if not self.errors and not self.warnings:
            print(f"{Colors.GREEN}✓ All environment variables are valid!{Colors.NC}\n")
            return True

        if self.errors:
            print(f"{Colors.RED}Errors found:{Colors.NC}")
            for error in self.errors:
                print(f"  {Colors.RED}✗{Colors.NC} {error}")
            print()

        if self.warnings:
            print(f"{Colors.YELLOW}Warnings:{Colors.NC}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}⚠{Colors.NC} {warning}")
            print()

        return len(self.errors) == 0

    def validate(self) -> bool:
        """Run all validations"""
        if not self.load_env_file():
            return False

        self.validate_required_vars()
        self.validate_optional_vars()
        self.check_security_issues()

        return self.print_results()


def main():
    """Main entry point"""
    validator = EnvValidator()

    if validator.validate():
        print("Environment validation passed!")
        sys.exit(0)
    else:
        print("Environment validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
