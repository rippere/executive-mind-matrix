"""
Unit tests for app/agent_router.py

Tests classification logic, agent analysis, and dialectic synthesis.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from app.agent_router import AgentRouter
from app.models import AgentPersona, AgentAnalysis, DialecticOutput


@pytest.fixture
def agent_router(mock_notion_client, mock_anthropic_client):
    """Create AgentRouter instance with mocked clients."""
    with patch('notion_client.AsyncClient', return_value=mock_notion_client):
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            router = AgentRouter()
            router.client = mock_anthropic_client
            router.notion = mock_notion_client
            return router


class TestAgentRouterInit:
    """Test AgentRouter initialization."""

    def test_init_creates_clients(self):
        """Test that AgentRouter initializes with Notion and Anthropic clients."""
        with patch('notion_client.AsyncClient') as mock_notion:
            with patch('anthropic.AsyncAnthropic') as mock_anthropic:
                router = AgentRouter()

                mock_notion.assert_called_once()
                mock_anthropic.assert_called_once()

    def test_init_loads_agent_prompts(self):
        """Test that agent prompts are loaded correctly."""
        with patch('notion_client.AsyncClient'):
            with patch('anthropic.AsyncAnthropic'):
                router = AgentRouter()

                assert AgentPersona.ENTREPRENEUR in router.agent_prompts
                assert AgentPersona.QUANT in router.agent_prompts
                assert AgentPersona.AUDITOR in router.agent_prompts

    def test_agent_prompts_contain_focus(self):
        """Test that each agent prompt has a clear focus."""
        with patch('notion_client.AsyncClient'):
            with patch('anthropic.AsyncAnthropic'):
                router = AgentRouter()

                for agent, prompt in router.agent_prompts.items():
                    assert "FOCUS:" in prompt or "You are" in prompt
                    assert len(prompt) > 100  # Prompts should be substantial


class TestClassifyIntent:
    """Test intent classification."""

    @pytest.mark.asyncio
    async def test_classify_strategic_intent(self, agent_router, mock_anthropic_client):
        """Test classifying a strategic intent."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps({
            "type": "strategic",
            "title": "Launch New Product",
            "agent": "The Entrepreneur",
            "risk": "High",
            "impact": 9,
            "rationale": "High-impact business decision"
        }))]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = await agent_router.classify_intent(
            "Should I launch a new SaaS product targeting enterprise clients?"
        )

        assert result["type"] == "strategic"
        assert result["title"] == "Launch New Product"
        assert result["agent"] == "The Entrepreneur"
        assert result["risk"] == "High"
        assert result["impact"] == 9

    @pytest.mark.asyncio
    async def test_classify_operational_intent(self, agent_router, mock_anthropic_client):
        """Test classifying an operational intent."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps({
            "type": "operational",
            "title": "Update Dependencies",
            "agent": "The Entrepreneur",
            "risk": "Low",
            "impact": 3,
            "next_action": "Run npm update",
            "rationale": "Clear next step"
        }))]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = await agent_router.classify_intent(
            "Update npm dependencies in the project"
        )

        assert result["type"] == "operational"
        assert "next_action" in result

    @pytest.mark.asyncio
    async def test_classify_reference_intent(self, agent_router, mock_anthropic_client):
        """Test classifying a reference intent."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps({
            "type": "reference",
            "title": "API Documentation",
            "agent": "The Entrepreneur",
            "risk": "Low",
            "impact": 1,
            "rationale": "Knowledge to store"
        }))]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = await agent_router.classify_intent(
            "Here's the link to the new API docs: https://example.com/api"
        )

        assert result["type"] == "reference"
        assert result["impact"] <= 2

    @pytest.mark.asyncio
    async def test_classify_calls_anthropic_correctly(self, agent_router, mock_anthropic_client):
        """Test that classification calls Anthropic with correct parameters."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"type": "strategic", "title": "Test", "agent": "The Entrepreneur", "risk": "Medium", "impact": 5, "rationale": "test"}')]
        mock_anthropic_client.messages.create.return_value = mock_response

        await agent_router.classify_intent("Test content")

        mock_anthropic_client.messages.create.assert_called_once()
        call_args = mock_anthropic_client.messages.create.call_args
        assert "messages" in call_args.kwargs
        assert len(call_args.kwargs["messages"]) > 0

    @pytest.mark.asyncio
    async def test_classify_fallback_on_error(self, agent_router, mock_anthropic_client):
        """Test fallback classification when API fails."""
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")

        result = await agent_router.classify_intent("Test content")

        # Should return fallback classification
        assert result["type"] == "strategic"
        assert "NEEDS MANUAL REVIEW" in result["title"]
        assert "Classification failed" in result["rationale"]


class TestAnalyzeWithAgent:
    """Test agent analysis."""

    @pytest.mark.asyncio
    async def test_analyze_with_entrepreneur(
        self, agent_router, mock_anthropic_client, sample_agent_analysis_json
    ):
        """Test analysis with Entrepreneur agent."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=sample_agent_analysis_json)]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = await agent_router.analyze_with_agent(
            agent=AgentPersona.ENTREPRENEUR,
            intent_title="Launch SaaS Product",
            intent_description="Build and launch a project management tool",
            success_criteria="Get 100 paying customers",
            projected_impact=8
        )

        assert isinstance(result, AgentAnalysis)
        assert len(result.scenario_options) == 3
        assert result.recommended_option in ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_analyze_uses_correct_system_prompt(
        self, agent_router, mock_anthropic_client, sample_agent_analysis_json
    ):
        """Test that analysis uses the correct agent system prompt."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=sample_agent_analysis_json)]
        mock_anthropic_client.messages.create.return_value = mock_response

        await agent_router.analyze_with_agent(
            agent=AgentPersona.QUANT,
            intent_title="Test",
            intent_description="Test",
            success_criteria="Test",
            projected_impact=5
        )

        call_args = mock_anthropic_client.messages.create.call_args
        system_prompt = call_args.kwargs.get("system", "")

        # Quant prompt should mention quantitative analysis
        assert "Quant" in system_prompt or "quantitative" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_analyze_handles_markdown_wrapped_json(self, agent_router, mock_anthropic_client):
        """Test that analysis handles JSON wrapped in markdown code blocks."""
        json_response = '{"scenario_options": [{"option": "A", "description": "Test", "pros": ["P"], "cons": ["C"], "risk": 2, "impact": 5}], "recommended_option": "A", "recommendation_rationale": "Test", "risk_assessment": "Test", "required_resources": {}, "task_generation_template": []}'

        # Test with ```json wrapper
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=f"```json\n{json_response}\n```")]
        mock_anthropic_client.messages.create.return_value = mock_response

        result = await agent_router.analyze_with_agent(
            agent=AgentPersona.ENTREPRENEUR,
            intent_title="Test",
            intent_description="Test"
        )

        assert isinstance(result, AgentAnalysis)

    @pytest.mark.asyncio
    async def test_analyze_raises_on_invalid_json(self, agent_router, mock_anthropic_client):
        """Test that analysis raises error on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not valid JSON")]
        mock_anthropic_client.messages.create.return_value = mock_response

        with pytest.raises(Exception):
            await agent_router.analyze_with_agent(
                agent=AgentPersona.ENTREPRENEUR,
                intent_title="Test",
                intent_description="Test"
            )

    @pytest.mark.asyncio
    async def test_analyze_with_all_agents(
        self, agent_router, mock_anthropic_client, sample_agent_analysis_json
    ):
        """Test analysis works with all three agent personas."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=sample_agent_analysis_json)]
        mock_anthropic_client.messages.create.return_value = mock_response

        for agent in [AgentPersona.ENTREPRENEUR, AgentPersona.QUANT, AgentPersona.AUDITOR]:
            result = await agent_router.analyze_with_agent(
                agent=agent,
                intent_title="Test Intent",
                intent_description="Test Description"
            )

            assert isinstance(result, AgentAnalysis)
            assert len(result.scenario_options) > 0


class TestDialecticFlow:
    """Test adversarial dialectic flow."""

    @pytest.mark.asyncio
    async def test_dialectic_flow_success(
        self,
        agent_router,
        mock_anthropic_client,
        sample_agent_analysis_json,
        sample_synthesis_json
    ):
        """Test successful dialectic flow."""
        # Mock responses for both agent analyses and synthesis
        responses = [
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),  # Growth
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),  # Risk
            MagicMock(content=[MagicMock(text=sample_synthesis_json)])  # Synthesis
        ]
        mock_anthropic_client.messages.create.side_effect = responses

        result = await agent_router.dialectic_flow(
            intent_id="test_intent_123",
            intent_title="Launch Product",
            intent_description="Build and launch SaaS",
            success_criteria="Get customers",
            projected_impact=8
        )

        assert isinstance(result, DialecticOutput)
        assert result.intent_id == "test_intent_123"
        assert result.growth_perspective is not None
        assert result.risk_perspective is not None
        assert len(result.synthesis) > 0
        assert len(result.conflict_points) > 0

    @pytest.mark.asyncio
    async def test_dialectic_calls_both_agents(
        self,
        agent_router,
        mock_anthropic_client,
        sample_agent_analysis_json,
        sample_synthesis_json
    ):
        """Test that dialectic calls both Entrepreneur and Auditor."""
        responses = [
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
            MagicMock(content=[MagicMock(text=sample_synthesis_json)])
        ]
        mock_anthropic_client.messages.create.side_effect = responses

        await agent_router.dialectic_flow(
            intent_id="test_123",
            intent_title="Test",
            intent_description="Test"
        )

        # Should be called 3 times: growth, risk, synthesis
        assert mock_anthropic_client.messages.create.call_count == 3

    @pytest.mark.asyncio
    async def test_dialectic_saves_raw_output(
        self,
        agent_router,
        mock_anthropic_client,
        mock_notion_client,
        sample_agent_analysis_json,
        sample_synthesis_json
    ):
        """Test that dialectic saves raw AI output to Notion."""
        responses = [
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
            MagicMock(content=[MagicMock(text=sample_synthesis_json)])
        ]
        mock_anthropic_client.messages.create.side_effect = responses

        # Mock finding action pipe
        mock_notion_client.databases.query.return_value = {
            "results": [{"id": "action_pipe_123"}]
        }

        await agent_router.dialectic_flow(
            intent_id="test_123",
            intent_title="Test",
            intent_description="Test"
        )

        # Should update action pipe with raw output
        mock_notion_client.pages.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_dialectic_fallback_on_growth_failure(
        self, agent_router, mock_anthropic_client
    ):
        """Test dialectic fallback when growth analysis fails."""
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")

        result = await agent_router.dialectic_flow(
            intent_id="test_123",
            intent_title="Test",
            intent_description="Test"
        )

        # Should return fallback output
        assert isinstance(result, DialecticOutput)
        assert result.growth_perspective is None
        assert "Error" in result.synthesis or "failed" in result.synthesis.lower()

    @pytest.mark.asyncio
    async def test_dialectic_fallback_on_risk_failure(
        self,
        agent_router,
        mock_anthropic_client,
        sample_agent_analysis_json
    ):
        """Test dialectic fallback when risk analysis fails."""
        responses = [
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),  # Growth succeeds
            Exception("API Error")  # Risk fails
        ]
        mock_anthropic_client.messages.create.side_effect = responses

        result = await agent_router.dialectic_flow(
            intent_id="test_123",
            intent_title="Test",
            intent_description="Test"
        )

        assert isinstance(result, DialecticOutput)
        assert result.growth_perspective is not None
        assert result.risk_perspective is None

    @pytest.mark.asyncio
    async def test_dialectic_fallback_on_synthesis_failure(
        self,
        agent_router,
        mock_anthropic_client,
        sample_agent_analysis_json
    ):
        """Test dialectic fallback when synthesis fails."""
        responses = [
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),  # Growth
            MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),  # Risk
            Exception("Synthesis failed")  # Synthesis fails
        ]
        mock_anthropic_client.messages.create.side_effect = responses

        result = await agent_router.dialectic_flow(
            intent_id="test_123",
            intent_title="Test",
            intent_description="Test"
        )

        assert isinstance(result, DialecticOutput)
        assert result.growth_perspective is not None
        assert result.risk_perspective is not None


class TestSaveRawAiOutput:
    """Test saving raw AI output to Notion."""

    @pytest.mark.asyncio
    async def test_save_raw_output_queries_action_pipes(
        self, agent_router, mock_notion_client, sample_dialectic_output
    ):
        """Test that save_raw_output queries for action pipe."""
        mock_notion_client.databases.query.return_value = {
            "results": [{"id": "pipe_123"}]
        }

        await agent_router._save_raw_ai_output("intent_123", sample_dialectic_output)

        mock_notion_client.databases.query.assert_called_once()
        call_args = mock_notion_client.databases.query.call_args
        assert "filter" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_save_raw_output_updates_page(
        self, agent_router, mock_notion_client, sample_dialectic_output
    ):
        """Test that raw output updates the action pipe page."""
        mock_notion_client.databases.query.return_value = {
            "results": [{"id": "pipe_123"}]
        }

        await agent_router._save_raw_ai_output("intent_123", sample_dialectic_output)

        # AI_Raw_Output is now stored as page blocks, not properties
        mock_notion_client.blocks.children.append.assert_called_once()
        call_args = mock_notion_client.blocks.children.append.call_args
        assert call_args.kwargs["block_id"] == "pipe_123"
        # Verify it contains a callout and code block
        children = call_args.kwargs["children"]
        assert len(children) == 2
        assert children[0]["type"] == "callout"
        assert children[1]["type"] == "code"

    @pytest.mark.asyncio
    async def test_save_raw_output_handles_no_action_pipe(
        self, agent_router, mock_notion_client, sample_dialectic_output
    ):
        """Test graceful handling when no action pipe found."""
        mock_notion_client.databases.query.return_value = {"results": []}

        # Should not raise error
        await agent_router._save_raw_ai_output("intent_123", sample_dialectic_output)

        # Should not attempt to append blocks since no action pipe was found
        mock_notion_client.blocks.children.append.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_raw_output_handles_errors(
        self, agent_router, mock_notion_client, sample_dialectic_output
    ):
        """Test that save errors don't crash the system."""
        mock_notion_client.databases.query.side_effect = Exception("Notion API error")

        # Should not raise error (it's a backup feature)
        await agent_router._save_raw_ai_output("intent_123", sample_dialectic_output)
