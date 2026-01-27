"""
Integration tests for Executive Mind Matrix

Tests end-to-end workflows including:
- Full poller cycle (inbox -> classification -> intent creation)
- Dialectic flow (growth + risk analysis + synthesis)
- Training data logging (diff capture)
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock

from app.notion_poller import NotionPoller
from app.agent_router import AgentRouter
from app.diff_logger import DiffLogger
from app.models import AgentPersona, IntentStatus


@pytest.mark.integration
class TestFullPollerCycle:
    """Integration tests for complete poller workflow."""

    @pytest.mark.asyncio
    async def test_inbox_to_executive_intent_flow(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_notion_inbox_page,
        sample_agent_analysis_json
    ):
        """Test complete flow from inbox to executive intent creation."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                # Setup mocks
                mock_notion_client.databases.query.return_value = {
                    "results": [sample_notion_inbox_page]
                }

                mock_response = MagicMock()
                mock_response.content = [MagicMock(text=json.dumps({
                    "type": "strategic",
                    "title": "Launch SaaS Product",
                    "agent": "The Entrepreneur",
                    "risk": "High",
                    "impact": 9,
                    "rationale": "High-impact business opportunity"
                }))]
                mock_anthropic_client.messages.create.return_value = mock_response

                # Create poller and run one cycle
                poller = NotionPoller()
                poller.client = mock_notion_client

                # Mock find_agent_by_name
                poller.find_agent_by_name = AsyncMock(return_value="agent_123")

                await poller.poll_cycle()

                # Verify classification was called
                mock_anthropic_client.messages.create.assert_called()

                # Verify executive intent was created
                create_calls = [
                    call for call in mock_notion_client.pages.create.call_args_list
                ]
                assert len(create_calls) > 0

                # Verify status updates
                update_calls = mock_notion_client.pages.update.call_args_list
                assert len(update_calls) >= 2  # Processing + Final status

    @pytest.mark.asyncio
    async def test_multiple_intents_processed_concurrently(
        self,
        mock_notion_client,
        mock_anthropic_client
    ):
        """Test that multiple intents are processed in parallel."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                # Create multiple inbox items
                intents = [
                    {
                        "id": f"intent_{i}",
                        "properties": {
                            "Content": {"rich_text": [{"plain_text": f"Intent {i}"}]},
                            "Source": {"select": {"name": "Email"}},
                            "Status": {"select": {"name": "Unprocessed"}}
                        }
                    }
                    for i in range(5)
                ]

                mock_notion_client.databases.query.return_value = {"results": intents}

                mock_response = MagicMock()
                mock_response.content = [MagicMock(text=json.dumps({
                    "type": "strategic",
                    "title": "Test",
                    "agent": "The Entrepreneur",
                    "risk": "Medium",
                    "impact": 5,
                    "rationale": "Test"
                }))]
                mock_anthropic_client.messages.create.return_value = mock_response

                poller = NotionPoller()
                poller.client = mock_notion_client
                poller.find_agent_by_name = AsyncMock(return_value="agent_123")

                await poller.poll_cycle()

                # Verify all intents were processed
                assert mock_anthropic_client.messages.create.call_count == 5

    @pytest.mark.asyncio
    async def test_operational_intent_routing(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_notion_inbox_page
    ):
        """Test that operational intents are routed correctly."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                mock_notion_client.databases.query.return_value = {
                    "results": [sample_notion_inbox_page]
                }

                # Classify as operational
                mock_response = MagicMock()
                mock_response.content = [MagicMock(text=json.dumps({
                    "type": "operational",
                    "title": "Update Dependencies",
                    "agent": "The Entrepreneur",
                    "risk": "Low",
                    "impact": 2,
                    "next_action": "Run npm update",
                    "rationale": "Clear next step"
                }))]
                mock_anthropic_client.messages.create.return_value = mock_response

                poller = NotionPoller()
                poller.client = mock_notion_client

                await poller.poll_cycle()

                # Verify status was updated to Triaged_to_Task
                update_calls = mock_notion_client.pages.update.call_args_list
                final_status = update_calls[-1].kwargs["properties"]["Status"]["select"]["name"]
                assert "Task" in final_status


@pytest.mark.integration
class TestDialecticFlow:
    """Integration tests for adversarial dialectic flow."""

    @pytest.mark.asyncio
    async def test_full_dialectic_flow(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_agent_analysis_json,
        sample_synthesis_json
    ):
        """Test complete dialectic flow: growth + risk + synthesis."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                # Setup mocks for both analyses and synthesis
                responses = [
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),  # Growth
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),  # Risk
                    MagicMock(content=[MagicMock(text=sample_synthesis_json)])  # Synthesis
                ]
                mock_anthropic_client.messages.create.side_effect = responses

                # Mock action pipe query
                mock_notion_client.databases.query.return_value = {
                    "results": [{"id": "pipe_123"}]
                }

                router = AgentRouter()
                router.client = mock_anthropic_client
                router.notion = mock_notion_client

                result = await router.dialectic_flow(
                    intent_id="test_intent_123",
                    intent_title="Launch SaaS Product",
                    intent_description="Build and launch project management tool",
                    success_criteria="Get 100 paying customers",
                    projected_impact=9
                )

                # Verify both agents were called
                assert mock_anthropic_client.messages.create.call_count == 3

                # Verify result structure
                assert result.intent_id == "test_intent_123"
                assert result.growth_perspective is not None
                assert result.risk_perspective is not None
                assert len(result.synthesis) > 0
                assert len(result.conflict_points) > 0

                # Verify raw output was saved
                mock_notion_client.pages.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_dialectic_with_different_recommendations(
        self,
        mock_notion_client,
        mock_anthropic_client
    ):
        """Test dialectic when agents recommend different options."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                # Growth agent recommends A
                growth_response = json.dumps({
                    "scenario_options": [
                        {
                            "option": "A",
                            "description": "Move fast",
                            "pros": ["Speed"],
                            "cons": ["Risk"],
                            "risk": 2,
                            "impact": 9
                        }
                    ],
                    "recommended_option": "A",
                    "recommendation_rationale": "Speed to market",
                    "risk_assessment": "Low risk",
                    "required_resources": {},
                    "task_generation_template": []
                })

                # Risk agent recommends B
                risk_response = json.dumps({
                    "scenario_options": [
                        {
                            "option": "B",
                            "description": "Move carefully",
                            "pros": ["Safe"],
                            "cons": ["Slow"],
                            "risk": 1,
                            "impact": 6
                        }
                    ],
                    "recommended_option": "B",
                    "recommendation_rationale": "Reduce risk",
                    "risk_assessment": "Very low risk",
                    "required_resources": {},
                    "task_generation_template": []
                })

                synthesis_response = json.dumps({
                    "synthesis": "Agents disagree on risk vs speed",
                    "recommended_path": "Hybrid approach",
                    "conflict_points": ["Speed vs Safety", "Risk tolerance"]
                })

                responses = [
                    MagicMock(content=[MagicMock(text=growth_response)]),
                    MagicMock(content=[MagicMock(text=risk_response)]),
                    MagicMock(content=[MagicMock(text=synthesis_response)])
                ]
                mock_anthropic_client.messages.create.side_effect = responses

                mock_notion_client.databases.query.return_value = {
                    "results": [{"id": "pipe_123"}]
                }

                router = AgentRouter()
                router.client = mock_anthropic_client
                router.notion = mock_notion_client

                result = await router.dialectic_flow(
                    intent_id="test_123",
                    intent_title="Test",
                    intent_description="Test"
                )

                # Verify different recommendations
                assert result.growth_perspective.recommended_option == "A"
                assert result.risk_perspective.recommended_option == "B"
                assert len(result.conflict_points) >= 2

    @pytest.mark.asyncio
    async def test_dialectic_fallback_on_partial_failure(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_agent_analysis_json
    ):
        """Test dialectic handles partial failures gracefully."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                # Growth succeeds, Risk fails, no synthesis
                responses = [
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
                    Exception("Risk analysis failed")
                ]
                mock_anthropic_client.messages.create.side_effect = responses

                router = AgentRouter()
                router.client = mock_anthropic_client
                router.notion = mock_notion_client

                result = await router.dialectic_flow(
                    intent_id="test_123",
                    intent_title="Test",
                    intent_description="Test"
                )

                # Should return fallback with partial data
                assert result.growth_perspective is not None
                assert result.risk_perspective is None
                assert "Error" in result.synthesis or "failed" in result.synthesis.lower()


@pytest.mark.integration
class TestTrainingDataCapture:
    """Integration tests for training data logging."""

    @pytest.mark.asyncio
    async def test_settlement_diff_full_workflow(
        self,
        mock_notion_client
    ):
        """Test complete diff logging workflow."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('aiofiles.open', create=True):
                with patch('os.makedirs'):
                    diff_logger = DiffLogger()
                    diff_logger.client = mock_notion_client

                    original_plan = {
                        "option": "A",
                        "tasks": [
                            {"id": 1, "name": "Task 1", "done": False},
                            {"id": 2, "name": "Task 2", "done": False}
                        ],
                        "budget": 5000
                    }

                    final_plan = {
                        "option": "B",  # Changed
                        "tasks": [
                            {"id": 1, "name": "Task 1 Modified", "done": False},  # Modified
                            {"id": 3, "name": "Task 3", "done": False}  # Replaced task 2
                        ],
                        "budget": 7500  # Changed
                    }

                    result = await diff_logger.log_settlement_diff(
                        intent_id="test_intent_123",
                        original_plan=original_plan,
                        final_plan=final_plan
                    )

                    # Verify diff was calculated
                    assert len(result.user_modifications) > 0
                    assert result.acceptance_rate < 1.0

                    # Verify saved to Notion
                    mock_notion_client.pages.create.assert_called_once()

                    call_args = mock_notion_client.pages.create.call_args
                    properties = call_args.kwargs["properties"]

                    assert "Intent_ID" in properties
                    assert "Acceptance_Rate" in properties
                    assert "Modifications_Count" in properties

    @pytest.mark.asyncio
    async def test_training_data_enables_metrics(
        self,
        mock_notion_client
    ):
        """Test that logged diffs enable agent performance metrics."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            # Mock training data results
            mock_notion_client.databases.query.return_value = {
                "results": [
                    {
                        "properties": {
                            "Acceptance_Rate": {"number": 80.0}
                        }
                    },
                    {
                        "properties": {
                            "Acceptance_Rate": {"number": 75.0}
                        }
                    },
                    {
                        "properties": {
                            "Acceptance_Rate": {"number": 85.0}
                        }
                    }
                ]
            }

            diff_logger = DiffLogger()
            diff_logger.client = mock_notion_client

            metrics = await diff_logger.get_agent_performance_metrics("The Entrepreneur")

            # Verify metrics calculation
            assert metrics["total_settlements"] == 3
            assert metrics["avg_acceptance_rate"] == 0.80  # (80 + 75 + 85) / 3 / 100
            assert metrics["min_acceptance_rate"] == 0.75
            assert metrics["max_acceptance_rate"] == 0.85


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end scenario tests."""

    @pytest.mark.asyncio
    async def test_high_impact_strategic_intent_workflow(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_agent_analysis_json,
        sample_synthesis_json
    ):
        """Test complete workflow for high-impact strategic intent."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                # 1. Intent arrives in System Inbox
                inbox_item = {
                    "id": "inbox_123",
                    "properties": {
                        "Content": {
                            "rich_text": [{
                                "plain_text": "Should I acquire a competitor for $2M?"
                            }]
                        },
                        "Source": {"select": {"name": "Email"}},
                        "Status": {"select": {"name": "Unprocessed"}}
                    }
                }

                mock_notion_client.databases.query.return_value = {
                    "results": [inbox_item]
                }

                # 2. Classification identifies as strategic
                classification_response = json.dumps({
                    "type": "strategic",
                    "title": "Acquire Competitor",
                    "agent": "The Quant",
                    "risk": "High",
                    "impact": 10,
                    "rationale": "Major financial decision"
                })

                # 3. Dialectic analysis
                responses = [
                    MagicMock(content=[MagicMock(text=classification_response)]),
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
                    MagicMock(content=[MagicMock(text=sample_synthesis_json)])
                ]
                mock_anthropic_client.messages.create.side_effect = responses

                # Run poller
                poller = NotionPoller()
                poller.client = mock_notion_client
                poller.find_agent_by_name = AsyncMock(return_value="quant_agent_123")

                await poller.poll_cycle()

                # Verify workflow
                # 1. Status updated to Processing
                # 2. Classification called
                # 3. Executive Intent created
                assert mock_anthropic_client.messages.create.call_count >= 1
                assert mock_notion_client.pages.create.call_count >= 1

                # Verify high impact -> P0 priority
                create_call = mock_notion_client.pages.create.call_args
                priority = create_call.kwargs["properties"]["Priority"]["select"]["name"]
                assert priority == "P0"

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(
        self,
        mock_notion_client,
        mock_anthropic_client
    ):
        """Test that system recovers gracefully from errors."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
                # Setup inbox with intent
                mock_notion_client.databases.query.return_value = {
                    "results": [{
                        "id": "inbox_123",
                        "properties": {
                            "Content": {"rich_text": [{"plain_text": "Test"}]},
                            "Source": {"select": {"name": "Email"}},
                            "Status": {"select": {"name": "Unprocessed"}}
                        }
                    }]
                }

                # First attempt fails
                mock_anthropic_client.messages.create.side_effect = Exception("API Error")

                poller = NotionPoller()
                poller.client = mock_notion_client

                # Should not crash
                await poller.poll_cycle()

                # Verify status was reset to Unprocessed
                update_calls = mock_notion_client.pages.update.call_args_list
                if len(update_calls) > 1:
                    final_status = update_calls[-1].kwargs["properties"]["Status"]["select"]["name"]
                    assert final_status == "Unprocessed"
