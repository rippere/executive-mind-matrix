"""
API endpoint tests for main.py

Tests FastAPI endpoints, request/response handling, and error cases.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from app.models import AgentPersona


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_poller():
    """Mock NotionPoller for API tests."""
    poller = MagicMock()
    poller.is_running = True
    poller.poll_cycle = AsyncMock()
    return poller


@pytest.mark.api
class TestRootEndpoint:
    """Test root health check endpoint."""

    def test_root_returns_status(self, test_client):
        """Test that root endpoint returns service status."""
        # Note: This test won't work without proper lifespan handling
        # We'll need to mock the poller
        with patch('main.poller', MagicMock(is_running=True)):
            response = test_client.get("/")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "running"
            assert data["service"] == "Executive Mind Matrix"
            assert data["version"] == "1.0.0"
            assert "environment" in data

    def test_root_shows_poller_status(self, test_client):
        """Test that root endpoint shows poller running state."""
        with patch('main.poller', MagicMock(is_running=False)):
            response = test_client.get("/")

            data = response.json()
            assert data["poller_running"] is False


@pytest.mark.api
class TestHealthEndpoint:
    """Test detailed health check endpoint."""

    def test_health_returns_detailed_status(self, test_client):
        """Test that health endpoint returns detailed information."""
        with patch('main.poller', MagicMock(is_running=True)):
            response = test_client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "healthy"
            assert "poller_active" in data
            assert "polling_interval" in data
            assert "databases_configured" in data

    def test_health_shows_database_configuration(self, test_client):
        """Test that health shows all 10 configured databases."""
        with patch('main.poller', MagicMock(is_running=True)):
            response = test_client.get("/health")

            data = response.json()
            databases = data["databases_configured"]

            assert "system_inbox" in databases
            assert "executive_intents" in databases
            assert "action_pipes" in databases
            assert "agent_registry" in databases
            assert "execution_log" in databases
            assert "training_data" in databases
            assert "tasks" in databases
            assert "projects" in databases
            assert "areas" in databases
            assert "nodes" in databases

    def test_health_databases_match_settings(self, test_client):
        """Enforce that every DB field in settings is reported in the health endpoint.

        This test prevents regression: if a new database is added to settings.py
        but not to the health endpoint, this test will fail.
        """
        from config.settings import Settings
        import inspect

        db_fields = [
            name.replace("notion_db_", "")
            for name in Settings.model_fields
            if name.startswith("notion_db_")
        ]

        with patch('main.poller', MagicMock(is_running=True)):
            response = test_client.get("/health")
            databases = response.json()["databases_configured"]

        for field in db_fields:
            assert field in databases, (
                f"Database '{field}' is defined in settings.py but missing from /health response. "
                f"Add it to the health endpoint in main.py."
            )


@pytest.mark.api
class TestTriggerPollEndpoint:
    """Test manual poll trigger endpoint."""

    def test_trigger_poll_success(self, test_client, mock_poller):
        """Test successful manual poll trigger."""
        with patch('main.poller', mock_poller):
            response = test_client.post("/trigger-poll")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "success"
            assert "Poll cycle completed" in data["message"]

            mock_poller.poll_cycle.assert_called_once()

    def test_trigger_poll_when_poller_not_initialized(self, test_client):
        """Test poll trigger when poller is not initialized."""
        with patch('main.poller', None):
            response = test_client.post("/trigger-poll")

            assert response.status_code == 503
            data = response.json()

            assert "Poller not initialized" in data["detail"]

    def test_trigger_poll_handles_errors(self, test_client, mock_poller):
        """Test poll trigger handles errors gracefully."""
        mock_poller.poll_cycle.side_effect = Exception("Poll failed")

        with patch('main.poller', mock_poller):
            response = test_client.post("/trigger-poll")

            assert response.status_code == 500
            data = response.json()

            assert "Poll failed" in data["detail"]


@pytest.mark.api
class TestAnalyzeIntentEndpoint:
    """Test manual intent analysis endpoint."""

    def test_analyze_intent_queues_analysis(self, test_client):
        """Test that analyze intent endpoint queues the analysis."""
        with patch('main.AgentRouter') as mock_router_class:
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            response = test_client.post(
                "/analyze-intent/test_intent_123",
                params={"agent": "The Entrepreneur"}
            )

            # Note: This endpoint currently returns placeholder
            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "queued"
            assert data["intent_id"] == "test_intent_123"
            assert data["agent"] == "The Entrepreneur"

    def test_analyze_intent_validates_agent_enum(self, test_client):
        """Test that invalid agent persona is rejected."""
        response = test_client.post(
            "/analyze-intent/test_intent_123",
            params={"agent": "Invalid Agent"}
        )

        # Should fail validation
        assert response.status_code == 422


@pytest.mark.api
class TestDialecticEndpoint:
    """Test adversarial dialectic endpoint."""

    @pytest.mark.asyncio
    async def test_dialectic_success(
        self,
        sample_agent_analysis_json,
        sample_synthesis_json
    ):
        """Test successful dialectic flow via API."""
        with patch('app.agent_router.AsyncAnthropic') as mock_anthropic_class:
            with patch('app.agent_router.AsyncClient') as mock_notion_class:
                mock_anthropic = AsyncMock()
                mock_anthropic_class.return_value = mock_anthropic

                responses = [
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
                    MagicMock(content=[MagicMock(text=sample_synthesis_json)])
                ]
                mock_anthropic.messages.create.side_effect = responses

                mock_notion = AsyncMock()
                mock_notion_class.return_value = mock_notion
                mock_notion.databases.query.return_value = {
                    "results": [{"id": "pipe_123"}]
                }

                async with AsyncClient(app=app, base_url="http://test") as ac:
                    response = await ac.post("/dialectic/test_intent_123")

                assert response.status_code == 200
                data = response.json()

                assert data["status"] == "success"
                assert data["intent_id"] == "test_intent_123"
                assert "synthesis" in data
                assert "recommended_path" in data
                assert "conflict_points" in data

    @pytest.mark.asyncio
    async def test_dialectic_handles_errors(self):
        """Test dialectic endpoint handles errors gracefully."""
        with patch('app.agent_router.AsyncAnthropic') as mock_anthropic_class:
            with patch('app.agent_router.AsyncClient'):
                mock_anthropic = AsyncMock()
                mock_anthropic_class.return_value = mock_anthropic
                mock_anthropic.messages.create.side_effect = Exception("API Error")

                async with AsyncClient(app=app, base_url="http://test") as ac:
                    response = await ac.post("/dialectic/test_intent_123")

                assert response.status_code == 500


@pytest.mark.api
class TestAgentMetricsEndpoint:
    """Test agent performance metrics endpoint."""

    @pytest.mark.asyncio
    async def test_get_agent_metrics_success(self):
        """Test successful metrics retrieval."""
        with patch('app.diff_logger.AsyncClient') as mock_notion_class:
            mock_notion = AsyncMock()
            mock_notion_class.return_value = mock_notion

            mock_notion.databases.query.return_value = {
                "results": [
                    {"properties": {"Acceptance_Rate": {"number": 80.0}}},
                    {"properties": {"Acceptance_Rate": {"number": 75.0}}}
                ]
            }

            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.get("/metrics/agent/The%20Entrepreneur")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "success"
            assert data["agent"] == "The Entrepreneur"
            assert "metrics" in data
            assert data["metrics"]["total_settlements"] == 2

    @pytest.mark.asyncio
    async def test_get_agent_metrics_handles_errors(self):
        """Test metrics endpoint handles errors."""
        with patch('app.diff_logger.AsyncClient') as mock_notion_class:
            mock_notion = AsyncMock()
            mock_notion_class.return_value = mock_notion
            mock_notion.databases.query.side_effect = Exception("Database error")

            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.get("/metrics/agent/The%20Quant")

            assert response.status_code == 500


@pytest.mark.api
class TestLogSettlementEndpoint:
    """Test settlement diff logging endpoint."""

    @pytest.mark.asyncio
    async def test_log_settlement_success(self):
        """Test successful settlement logging."""
        with patch('app.diff_logger.AsyncClient') as mock_notion_class:
            with patch('aiofiles.open', create=True):
                with patch('os.makedirs'):
                    mock_notion = AsyncMock()
                    mock_notion_class.return_value = mock_notion

                    original_plan = {"option": "A", "tasks": ["Task 1"]}
                    final_plan = {"option": "B", "tasks": ["Task 2"]}

                    async with AsyncClient(app=app, base_url="http://test") as ac:
                        response = await ac.post(
                            "/log-settlement",
                            params={"intent_id": "intent_123"},
                            json={
                                "original_plan": original_plan,
                                "final_plan": final_plan
                            }
                        )

                    assert response.status_code == 200
                    data = response.json()

                    assert data["status"] == "success"
                    assert data["intent_id"] == "intent_123"
                    assert "modifications" in data
                    assert "acceptance_rate" in data

    @pytest.mark.asyncio
    async def test_log_settlement_validates_input(self):
        """Test that settlement logging validates input."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Missing required fields
            response = await ac.post(
                "/log-settlement",
                params={"intent_id": "intent_123"},
                json={}
            )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_log_settlement_handles_errors(self):
        """Test settlement logging handles errors."""
        with patch('app.diff_logger.AsyncClient') as mock_notion_class:
            mock_notion = AsyncMock()
            mock_notion_class.return_value = mock_notion
            mock_notion.pages.create.side_effect = Exception("Database error")

            with patch('aiofiles.open', side_effect=Exception("File error")):
                async with AsyncClient(app=app, base_url="http://test") as ac:
                    response = await ac.post(
                        "/log-settlement",
                        params={"intent_id": "intent_123"},
                        json={
                            "original_plan": {"test": "data"},
                            "final_plan": {"test": "modified"}
                        }
                    )

                assert response.status_code == 500


@pytest.mark.api
class TestAPIErrorHandling:
    """Test API error handling and edge cases."""

    def test_404_on_invalid_route(self, test_client):
        """Test 404 response on invalid route."""
        response = test_client.get("/invalid-route")
        assert response.status_code == 404

    def test_method_not_allowed(self, test_client):
        """Test 405 response on wrong HTTP method."""
        # GET on POST endpoint
        response = test_client.get("/trigger-poll")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_request_validation_errors(self):
        """Test that invalid request bodies are rejected."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Invalid JSON
            response = await ac.post(
                "/log-settlement",
                params={"intent_id": "test"},
                content="not valid json"
            )

        assert response.status_code == 422


@pytest.mark.api
class TestAPIAuthentication:
    """Test API authentication and security (if implemented)."""

    def test_api_allows_requests_without_auth(self, test_client):
        """Test that API currently allows unauthenticated requests."""
        # Note: Add authentication tests when auth is implemented
        with patch('main.poller', MagicMock(is_running=True)):
            response = test_client.get("/")
            assert response.status_code == 200


@pytest.mark.api
class TestAPICORS:
    """Test CORS configuration (if needed)."""

    def test_cors_headers(self, test_client):
        """Test CORS headers if configured."""
        # Note: Add CORS tests if CORS middleware is added
        with patch('main.poller', MagicMock(is_running=True)):
            response = test_client.get("/")
            # Check for CORS headers when implemented
            assert response.status_code == 200


@pytest.mark.api
class TestActionPipePropertyPopulation:
    """Test that Action Pipes are created with all required properties."""

    @pytest.mark.asyncio
    async def test_dialectic_populates_all_properties(
        self,
        sample_agent_analysis_json,
        sample_synthesis_json
    ):
        """Test that dialectic endpoint populates Agent, Required_Resources, Task_Generation_Template, and AI_Raw_Output."""
        with patch('app.agent_router.AsyncAnthropic') as mock_anthropic_class:
            with patch('notion_client.AsyncClient') as mock_notion_class:
                mock_anthropic = AsyncMock()
                mock_anthropic_class.return_value = mock_anthropic

                responses = [
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
                    MagicMock(content=[MagicMock(text=sample_agent_analysis_json)]),
                    MagicMock(content=[MagicMock(text=sample_synthesis_json)])
                ]
                mock_anthropic.messages.create.side_effect = responses

                mock_notion = AsyncMock()
                mock_notion_class.return_value = mock_notion

                # Mock intent with Agent_Persona relation
                mock_notion.pages.retrieve.return_value = {
                    "id": "intent123",
                    "properties": {
                        "Name": {"title": [{"text": {"content": "Test Intent"}}]},
                        "Description": {"rich_text": [{"text": {"content": "Test description"}}]},
                        "Agent_Persona": {"relation": [{"id": "agent456"}]}
                    }
                }

                # Mock Action Pipe creation
                mock_notion.pages.create.return_value = {"id": "action789"}
                mock_notion.pages.update.return_value = {"id": "intent123"}
                mock_notion.databases.query.return_value = {"results": [{"id": "pipe_123"}]}

                async with AsyncClient(app=app, base_url="http://test") as ac:
                    response = await ac.post("/dialectic/intent123")

                assert response.status_code == 200

                # Verify Action Pipe was created with all properties
                create_calls = [call for call in mock_notion.pages.create.call_args_list
                               if "Action_Title" in str(call)]

                assert len(create_calls) > 0, "Action Pipe should have been created"

                # Get the Action Pipe creation call
                action_create_call = create_calls[0]
                properties = action_create_call.kwargs["properties"]

                # Verify all critical properties are populated
                assert "Agent" in properties, "Agent relation should be populated"
                assert properties["Agent"]["relation"] == [{"id": "agent456"}], "Agent should link to agent456"

                assert "Required_Resources" in properties, "Required_Resources should be populated"
                assert len(properties["Required_Resources"]["rich_text"]) > 0, "Required_Resources should have content"

                assert "Task_Generation_Template" in properties, "Task_Generation_Template should be populated"
                assert len(properties["Task_Generation_Template"]["rich_text"]) > 0, "Task_Generation_Template should have content"

                # AI_Raw_Output is now stored in page blocks, not properties
                # Verify that blocks.children.append was called to store it
                append_calls = [call for call in mock_notion.blocks.children.append.call_args_list]
                assert len(append_calls) > 0, "AI_Raw_Output should be saved as page blocks"


@pytest.mark.api
class TestApprovalEndpoint:
    """Test action approval endpoint."""

    @pytest.mark.asyncio
    async def test_approve_action_endpoint(self):
        """Test that POST /action/{action_id}/approve works correctly."""
        with patch('notion_client.AsyncClient') as mock_notion_class:
            mock_notion = AsyncMock()
            mock_notion_class.return_value = mock_notion

            # Mock successful update and log creation
            mock_notion.pages.update.return_value = {"id": "action123"}
            mock_notion.pages.create.return_value = {"id": "log123"}

            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post("/action/action123/approve")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "success"
            assert data["action_id"] == "action123"
            assert "message" in data

            # Verify approval was called
            update_call = mock_notion.pages.update.call_args
            assert update_call is not None
