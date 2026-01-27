#!/usr/bin/env python3

"""
Connection testing script for Executive Mind Matrix.
Tests connections to Notion and Anthropic APIs.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from notion_client import AsyncClient as NotionClient
from anthropic import Anthropic
from loguru import logger
import httpx


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


async def test_notion_connection():
    """Test Notion API connection"""
    test_name = "Notion API Connection"
    print(f"\n{Colors.BLUE}Testing {test_name}...{Colors.NC}")

    try:
        # Initialize Notion client
        notion = NotionClient(auth=settings.notion_api_key)

        # Test API connection by listing users
        response = await notion.users.list()

        if response:
            print(f"{Colors.GREEN}✓ {test_name} successful{Colors.NC}")
            print(f"  Workspace has {len(response['results'])} user(s)")
            return True
        else:
            print(f"{Colors.RED}✗ {test_name} failed - No response{Colors.NC}")
            return False

    except Exception as e:
        print(f"{Colors.RED}✗ {test_name} failed{Colors.NC}")
        print(f"  Error: {str(e)}")
        return False


async def test_notion_databases():
    """Test Notion database access"""
    test_name = "Notion Database Access"
    print(f"\n{Colors.BLUE}Testing {test_name}...{Colors.NC}")

    databases = {
        "System Inbox": settings.notion_db_system_inbox,
        "Executive Intents": settings.notion_db_executive_intents,
        "Action Pipes": settings.notion_db_action_pipes,
        "Agent Registry": settings.notion_db_agent_registry,
        "Execution Log": settings.notion_db_execution_log,
        "Training Data": settings.notion_db_training_data,
    }

    notion = NotionClient(auth=settings.notion_api_key)
    all_success = True

    for db_name, db_id in databases.items():
        try:
            # Try to retrieve database
            response = await notion.databases.retrieve(database_id=db_id)

            if response:
                print(f"{Colors.GREEN}✓ {db_name}: accessible{Colors.NC}")
                print(f"  ID: {db_id}")
            else:
                print(f"{Colors.RED}✗ {db_name}: not accessible{Colors.NC}")
                all_success = False

        except Exception as e:
            print(f"{Colors.RED}✗ {db_name}: error{Colors.NC}")
            print(f"  Error: {str(e)}")
            all_success = False

    return all_success


def test_anthropic_connection():
    """Test Anthropic API connection"""
    test_name = "Anthropic API Connection"
    print(f"\n{Colors.BLUE}Testing {test_name}...{Colors.NC}")

    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=settings.anthropic_api_key)

        # Test API connection with a minimal request
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=10,
            messages=[
                {"role": "user", "content": "Hello"}
            ]
        )

        if response and response.content:
            print(f"{Colors.GREEN}✓ {test_name} successful{Colors.NC}")
            print(f"  Model: {settings.anthropic_model}")
            print(f"  Response tokens: {response.usage.output_tokens}")
            print(f"  Input tokens: {response.usage.input_tokens}")
            return True
        else:
            print(f"{Colors.RED}✗ {test_name} failed - No response{Colors.NC}")
            return False

    except Exception as e:
        print(f"{Colors.RED}✗ {test_name} failed{Colors.NC}")
        print(f"  Error: {str(e)}")

        # Check for common errors
        error_str = str(e).lower()
        if "api key" in error_str or "authentication" in error_str:
            print(f"  {Colors.YELLOW}Hint: Check your ANTHROPIC_API_KEY{Colors.NC}")
        elif "model" in error_str:
            print(f"  {Colors.YELLOW}Hint: Check your ANTHROPIC_MODEL setting{Colors.NC}")
        elif "rate limit" in error_str:
            print(f"  {Colors.YELLOW}Hint: Rate limit exceeded, try again later{Colors.NC}")

        return False


async def test_network_connectivity():
    """Test general network connectivity"""
    test_name = "Network Connectivity"
    print(f"\n{Colors.BLUE}Testing {test_name}...{Colors.NC}")

    endpoints = [
        ("Notion API", "https://api.notion.com"),
        ("Anthropic API", "https://api.anthropic.com"),
    ]

    all_success = True

    async with httpx.AsyncClient() as client:
        for name, url in endpoints:
            try:
                response = await client.get(url, timeout=10.0)

                # Any response (even 401/403) means we can reach the server
                if response.status_code:
                    print(f"{Colors.GREEN}✓ {name}: reachable (HTTP {response.status_code}){Colors.NC}")
                else:
                    print(f"{Colors.RED}✗ {name}: not reachable{Colors.NC}")
                    all_success = False

            except Exception as e:
                print(f"{Colors.RED}✗ {name}: connection failed{Colors.NC}")
                print(f"  Error: {str(e)}")
                all_success = False

    return all_success


def test_environment_variables():
    """Test that all required environment variables are set"""
    test_name = "Environment Variables"
    print(f"\n{Colors.BLUE}Testing {test_name}...{Colors.NC}")

    required_vars = [
        ("NOTION_API_KEY", settings.notion_api_key),
        ("NOTION_DB_SYSTEM_INBOX", settings.notion_db_system_inbox),
        ("NOTION_DB_EXECUTIVE_INTENTS", settings.notion_db_executive_intents),
        ("NOTION_DB_ACTION_PIPES", settings.notion_db_action_pipes),
        ("NOTION_DB_AGENT_REGISTRY", settings.notion_db_agent_registry),
        ("NOTION_DB_EXECUTION_LOG", settings.notion_db_execution_log),
        ("NOTION_DB_TRAINING_DATA", settings.notion_db_training_data),
        ("ANTHROPIC_API_KEY", settings.anthropic_api_key),
        ("ANTHROPIC_MODEL", settings.anthropic_model),
    ]

    all_set = True

    for var_name, var_value in required_vars:
        if var_value:
            # Mask sensitive values
            if "KEY" in var_name or "SECRET" in var_name:
                masked = var_value[:8] + "..." + var_value[-4:]
                print(f"{Colors.GREEN}✓ {var_name}: set ({masked}){Colors.NC}")
            else:
                print(f"{Colors.GREEN}✓ {var_name}: set{Colors.NC}")
        else:
            print(f"{Colors.RED}✗ {var_name}: not set{Colors.NC}")
            all_set = False

    return all_set


async def main():
    """Main entry point"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}Executive Mind Matrix - Connection Tests{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")

    # Run all tests
    results = {}

    results["Environment Variables"] = test_environment_variables()
    results["Network Connectivity"] = await test_network_connectivity()
    results["Notion Connection"] = await test_notion_connection()
    results["Notion Databases"] = await test_notion_databases()
    results["Anthropic Connection"] = test_anthropic_connection()

    # Summary
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}Summary{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, success in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if success else f"{Colors.RED}✗ FAIL{Colors.NC}"
        print(f"  {status} - {test_name}")

    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.NC}\n")

    if passed == total:
        print(f"{Colors.GREEN}All connection tests passed!{Colors.NC}")
        print(f"{Colors.GREEN}Your environment is ready for deployment.{Colors.NC}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}Some connection tests failed.{Colors.NC}")
        print(f"{Colors.RED}Please fix the issues before deploying.{Colors.NC}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
