"""
Shared fixtures and test configuration for Executive Mind Matrix tests.

This module provides:
- Mock Notion API clients and responses
- Mock Anthropic API clients and responses
- Common test data fixtures
- Test utilities and helpers
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List
from datetime import datetime
import json

from app.models import (
    AgentPersona, IntentStatus, RiskLevel,
    NotionIntent, AgentAnalysis, ScenarioOption,
    DialecticOutput, SettlementDiff
)


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# NOTION API MOCKS
# ============================================================================

@pytest.fixture
def mock_notion_client():
    """Mock Notion AsyncClient with common methods."""
    client = AsyncMock()

    # Mock databases.query
    client.databases.query = AsyncMock(return_value={
        "results": [],
        "has_more": False,
        "next_cursor": None
    })

    # Mock pages.create
    client.pages.create = AsyncMock(return_value={
        "id": "test_page_id_12345",
        "created_time": datetime.utcnow().isoformat(),
        "properties": {}
    })

    # Mock pages.update
    client.pages.update = AsyncMock(return_value={
        "id": "test_page_id_12345",
        "last_edited_time": datetime.utcnow().isoformat()
    })

    return client


@pytest.fixture
def sample_notion_inbox_page() -> Dict[str, Any]:
    """Sample Notion inbox page data."""
    return {
        "id": "inbox_page_123",
        "created_time": "2024-01-15T10:00:00.000Z",
        "properties": {
            "Content": {
                "rich_text": [{
                    "plain_text": "Build a new SaaS product for project management",
                    "text": {"content": "Build a new SaaS product for project management"}
                }]
            },
            "Source": {
                "select": {
                    "name": "Email"
                }
            },
            "Status": {
                "select": {
                    "name": "Unprocessed"
                }
            },
            "Received_Date": {
                "date": {
                    "start": "2024-01-15"
                }
            }
        }
    }


@pytest.fixture
def sample_notion_intent_page() -> Dict[str, Any]:
    """Sample Notion Executive Intent page data."""
    return {
        "id": "intent_page_456",
        "created_time": "2024-01-15T10:30:00.000Z",
        "properties": {
            "Name": {
                "title": [{
                    "plain_text": "Launch SaaS Product",
                    "text": {"content": "Launch SaaS Product"}
                }]
            },
            "Description": {
                "rich_text": [{
                    "plain_text": "Build and launch a project management SaaS",
                    "text": {"content": "Build and launch a project management SaaS"}
                }]
            },
            "Status": {
                "select": {
                    "name": "Ready"
                }
            },
            "Risk_Level": {
                "select": {
                    "name": "High"
                }
            },
            "Projected_Impact": {
                "number": 9
            },
            "Priority": {
                "select": {
                    "name": "P0"
                }
            }
        }
    }


@pytest.fixture
def sample_notion_agent_page() -> Dict[str, Any]:
    """Sample Notion Agent Registry page data."""
    return {
        "id": "agent_page_789",
        "properties": {
            "Agent_Name": {
                "title": [{
                    "plain_text": "The Entrepreneur",
                    "text": {"content": "The Entrepreneur"}
                }]
            },
            "Description": {
                "rich_text": [{
                    "plain_text": "Growth-focused operator",
                    "text": {"content": "Growth-focused operator"}
                }]
            }
        }
    }


# ============================================================================
# ANTHROPIC API MOCKS
# ============================================================================

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic AsyncAnthropic client."""
    client = AsyncMock()

    # Default response structure
    default_response = MagicMock()
    default_response.content = [
        MagicMock(text='{"type": "strategic", "title": "Test Intent", "agent": "The Entrepreneur", "risk": "Medium", "impact": 7, "rationale": "Test"}')
    ]

    client.messages.create = AsyncMock(return_value=default_response)

    return client


@pytest.fixture
def sample_agent_analysis_json() -> str:
    """Sample agent analysis response as JSON string."""
    return json.dumps({
        "scenario_options": [
            {
                "option": "A",
                "description": "Move fast and launch MVP in 30 days",
                "pros": ["Quick to market", "Low initial cost", "Fast validation"],
                "cons": ["Limited features", "Technical debt", "May need rebuild"],
                "risk": 2,
                "impact": 8
            },
            {
                "option": "B",
                "description": "Build robust solution over 6 months",
                "pros": ["Scalable architecture", "Better UX", "Enterprise ready"],
                "cons": ["Higher cost", "Slower to market", "More complex"],
                "risk": 4,
                "impact": 9
            },
            {
                "option": "C",
                "description": "Partner with existing platform",
                "pros": ["Fast market entry", "Lower risk", "Proven tech"],
                "cons": ["Revenue sharing", "Less control", "Dependency"],
                "risk": 3,
                "impact": 6
            }
        ],
        "recommended_option": "A",
        "recommendation_rationale": "Speed to market is critical for validation",
        "risk_assessment": "Low technical risk, medium market risk",
        "required_resources": {
            "time": "40 hours/week for 4 weeks",
            "money": "$5000 for infrastructure and tools",
            "tools": ["AWS", "Stripe", "Next.js"],
            "people": ["Full-stack developer"]
        },
        "task_generation_template": [
            "Set up development environment",
            "Design database schema",
            "Build authentication system",
            "Implement core features",
            "Deploy to production"
        ]
    })


@pytest.fixture
def sample_synthesis_json() -> str:
    """Sample dialectic synthesis response as JSON string."""
    return json.dumps({
        "synthesis": "The Growth agent favors rapid MVP launch while the Risk agent prefers thorough planning. A hybrid approach balances both.",
        "recommended_path": "Launch MVP with core features in 60 days, then iterate",
        "conflict_points": [
            "Speed vs Quality tradeoff",
            "Technical debt vs Time to market",
            "Resource allocation"
        ]
    })


# ============================================================================
# MODEL FIXTURES
# ============================================================================

@pytest.fixture
def sample_scenario_option() -> ScenarioOption:
    """Sample ScenarioOption instance."""
    return ScenarioOption(
        option="A",
        description="Test option description",
        pros=["Pro 1", "Pro 2"],
        cons=["Con 1", "Con 2"],
        risk=3,
        impact=7
    )


@pytest.fixture
def sample_agent_analysis(sample_scenario_option) -> AgentAnalysis:
    """Sample AgentAnalysis instance."""
    return AgentAnalysis(
        scenario_options=[sample_scenario_option],
        recommended_option="A",
        recommendation_rationale="This is the best option because...",
        risk_assessment="Medium risk with good upside",
        required_resources={
            "time": "2 weeks",
            "money": "$1000",
            "tools": ["Tool1"],
            "people": ["Developer"]
        },
        task_generation_template=["Task 1", "Task 2"]
    )


@pytest.fixture
def sample_notion_intent() -> NotionIntent:
    """Sample NotionIntent instance."""
    return NotionIntent(
        id="intent_123",
        title="Test Intent",
        description="This is a test intent",
        status=IntentStatus.PENDING,
        risk_level=RiskLevel.MEDIUM,
        agent_persona=AgentPersona.ENTREPRENEUR,
        projected_impact=7,
        success_criteria="Achieve X goal"
    )


@pytest.fixture
def sample_dialectic_output(sample_agent_analysis) -> DialecticOutput:
    """Sample DialecticOutput instance."""
    return DialecticOutput(
        intent_id="intent_123",
        growth_perspective=sample_agent_analysis,
        risk_perspective=sample_agent_analysis,
        synthesis="Balanced approach recommended",
        recommended_path="Option A with risk mitigation",
        conflict_points=["Point 1", "Point 2"]
    )


@pytest.fixture
def sample_settlement_diff() -> SettlementDiff:
    """Sample SettlementDiff instance."""
    return SettlementDiff(
        intent_id="intent_123",
        timestamp=datetime.utcnow(),
        original_plan={"option": "A", "tasks": ["Task 1", "Task 2"]},
        final_plan={"option": "B", "tasks": ["Task 1", "Task 3"]},
        diff_summary={"values_changed": {"option": {"old": "A", "new": "B"}}},
        user_modifications=["Changed option from A to B"],
        acceptance_rate=0.75
    )


# ============================================================================
# PATCH FIXTURES
# ============================================================================

@pytest.fixture
def mock_notion_client_patch(mock_notion_client):
    """Patch notion_client.AsyncClient globally."""
    with patch('notion_client.AsyncClient', return_value=mock_notion_client):
        yield mock_notion_client


@pytest.fixture
def mock_anthropic_client_patch(mock_anthropic_client):
    """Patch anthropic.AsyncAnthropic globally."""
    with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
        yield mock_anthropic_client


# ============================================================================
# FILE SYSTEM MOCKS
# ============================================================================

@pytest.fixture
def temp_logs_dir(tmp_path):
    """Create temporary logs directory."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    return logs_dir


@pytest.fixture
def mock_aiofiles(tmp_path):
    """Mock aiofiles for testing file operations."""
    test_file = tmp_path / "test.jsonl"

    class MockAiofilesContext:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def write(self, content):
            test_file.write_text(content)

    def mock_open(*args, **kwargs):
        return MockAiofilesContext()

    with patch('aiofiles.open', side_effect=mock_open):
        yield test_file


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@pytest.fixture
def assert_notion_page_created():
    """Helper to assert Notion page was created with correct properties."""
    def _assert(mock_client, expected_db_id: str, expected_properties: Dict[str, Any]):
        mock_client.pages.create.assert_called_once()
        call_args = mock_client.pages.create.call_args

        assert call_args.kwargs["parent"]["database_id"] == expected_db_id

        for prop_name, expected_value in expected_properties.items():
            actual_value = call_args.kwargs["properties"].get(prop_name)
            assert actual_value is not None, f"Property {prop_name} not found"

    return _assert


@pytest.fixture
def assert_anthropic_called():
    """Helper to assert Anthropic API was called correctly."""
    def _assert(mock_client, expected_model: str = None, min_tokens: int = None):
        mock_client.messages.create.assert_called()
        call_args = mock_client.messages.create.call_args

        if expected_model:
            assert call_args.kwargs.get("model") == expected_model

        if min_tokens:
            assert call_args.kwargs.get("max_tokens", 0) >= min_tokens

    return _assert
