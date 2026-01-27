"""
Unit tests for app/notion_poller.py

Tests polling logic, intent processing, and Notion database operations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock, call

from app.notion_poller import NotionPoller
from app.models import IntentStatus


@pytest.fixture
def notion_poller(mock_notion_client):
    """Create NotionPoller instance with mocked Notion client."""
    with patch('notion_client.AsyncClient', return_value=mock_notion_client):
        poller = NotionPoller()
        poller.client = mock_notion_client
        return poller


class TestNotionPollerInit:
    """Test NotionPoller initialization."""

    def test_init_creates_notion_client(self):
        """Test that NotionPoller initializes with Notion client."""
        with patch('notion_client.AsyncClient') as mock_client:
            poller = NotionPoller()
            mock_client.assert_called_once()

    def test_init_sets_polling_interval(self):
        """Test that polling interval is set from settings."""
        with patch('notion_client.AsyncClient'):
            poller = NotionPoller()
            assert poller.polling_interval > 0
            assert isinstance(poller.polling_interval, int)

    def test_init_sets_is_running_false(self):
        """Test that poller starts in not-running state."""
        with patch('notion_client.AsyncClient'):
            poller = NotionPoller()
            assert poller.is_running is False


class TestPollerStartStop:
    """Test poller start and stop functionality."""

    @pytest.mark.asyncio
    async def test_start_sets_is_running(self, notion_poller):
        """Test that start() sets is_running to True."""
        # Create a task that we can cancel quickly
        start_task = asyncio.create_task(notion_poller.start())

        # Give it a moment to start
        await asyncio.sleep(0.1)

        assert notion_poller.is_running is True

        # Clean up
        notion_poller.stop()
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass

    def test_stop_sets_is_running_false(self, notion_poller):
        """Test that stop() sets is_running to False."""
        notion_poller.is_running = True
        notion_poller.stop()
        assert notion_poller.is_running is False

    @pytest.mark.asyncio
    async def test_start_calls_poll_cycle(self, notion_poller):
        """Test that start() repeatedly calls poll_cycle."""
        poll_count = 0

        async def mock_poll_cycle():
            nonlocal poll_count
            poll_count += 1
            if poll_count >= 2:
                notion_poller.stop()

        notion_poller.poll_cycle = mock_poll_cycle
        notion_poller.polling_interval = 0.1  # Fast for testing

        await notion_poller.start()

        assert poll_count >= 2


class TestFetchPendingIntents:
    """Test fetching pending intents from Notion."""

    @pytest.mark.asyncio
    async def test_fetch_pending_intents_queries_database(self, notion_poller, mock_notion_client):
        """Test that fetch queries the correct database."""
        mock_notion_client.databases.query.return_value = {"results": []}

        await notion_poller.fetch_pending_intents()

        mock_notion_client.databases.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_pending_intents_filters_unprocessed(
        self, notion_poller, mock_notion_client
    ):
        """Test that fetch filters for Unprocessed status."""
        mock_notion_client.databases.query.return_value = {"results": []}

        await notion_poller.fetch_pending_intents()

        call_args = mock_notion_client.databases.query.call_args
        filter_prop = call_args.kwargs["filter"]

        assert filter_prop["property"] == "Status"
        assert filter_prop["select"]["equals"] == "Unprocessed"

    @pytest.mark.asyncio
    async def test_fetch_pending_intents_returns_results(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that fetch returns intent pages."""
        mock_notion_client.databases.query.return_value = {
            "results": [sample_notion_inbox_page]
        }

        results = await notion_poller.fetch_pending_intents()

        assert len(results) == 1
        assert results[0]["id"] == sample_notion_inbox_page["id"]

    @pytest.mark.asyncio
    async def test_fetch_pending_intents_handles_errors(
        self, notion_poller, mock_notion_client
    ):
        """Test that fetch handles API errors gracefully."""
        mock_notion_client.databases.query.side_effect = Exception("API Error")

        results = await notion_poller.fetch_pending_intents()

        assert results == []


class TestPollCycle:
    """Test poll cycle execution."""

    @pytest.mark.asyncio
    async def test_poll_cycle_fetches_intents(self, notion_poller, mock_notion_client):
        """Test that poll_cycle fetches pending intents."""
        mock_notion_client.databases.query.return_value = {"results": []}

        await notion_poller.poll_cycle()

        mock_notion_client.databases.query.assert_called()

    @pytest.mark.asyncio
    async def test_poll_cycle_processes_intents(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that poll_cycle processes found intents."""
        mock_notion_client.databases.query.return_value = {
            "results": [sample_notion_inbox_page]
        }

        # Mock the process_intent method
        notion_poller.process_intent = AsyncMock(return_value=True)

        await notion_poller.poll_cycle()

        notion_poller.process_intent.assert_called_once_with(sample_notion_inbox_page)

    @pytest.mark.asyncio
    async def test_poll_cycle_handles_no_intents(self, notion_poller, mock_notion_client):
        """Test that poll_cycle handles empty results gracefully."""
        mock_notion_client.databases.query.return_value = {"results": []}

        # Should not raise error
        await notion_poller.poll_cycle()

    @pytest.mark.asyncio
    async def test_poll_cycle_processes_multiple_intents(
        self, notion_poller, mock_notion_client
    ):
        """Test processing multiple intents concurrently."""
        intents = [
            {"id": "intent_1", "properties": {}},
            {"id": "intent_2", "properties": {}},
            {"id": "intent_3", "properties": {}}
        ]
        mock_notion_client.databases.query.return_value = {"results": intents}

        notion_poller.process_intent = AsyncMock(return_value=True)

        await notion_poller.poll_cycle()

        assert notion_poller.process_intent.call_count == 3


class TestProcessIntent:
    """Test individual intent processing."""

    @pytest.mark.asyncio
    async def test_process_intent_updates_status_to_processing(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that processing starts by updating status."""
        # Mock the agent router to prevent actual API calls
        with patch('app.notion_poller.AgentRouter') as mock_router_class:
            mock_router = AsyncMock()
            mock_router.classify_intent.return_value = {
                "type": "strategic",
                "title": "Test",
                "agent": "The Entrepreneur",
                "risk": "Medium",
                "impact": 5
            }
            mock_router_class.return_value = mock_router

            await notion_poller.process_intent(sample_notion_inbox_page)

            # Should update status to Processing
            status_calls = [
                call for call in mock_notion_client.pages.update.call_args_list
                if "Status" in str(call)
            ]
            assert len(status_calls) > 0

    @pytest.mark.asyncio
    async def test_process_intent_calls_classify(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that processing classifies the intent."""
        with patch('app.notion_poller.AgentRouter') as mock_router_class:
            mock_router = AsyncMock()
            mock_router.classify_intent.return_value = {
                "type": "strategic",
                "title": "Test",
                "agent": "The Entrepreneur",
                "risk": "Medium",
                "impact": 5
            }
            mock_router_class.return_value = mock_router

            await notion_poller.process_intent(sample_notion_inbox_page)

            mock_router.classify_intent.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_strategic_creates_executive_intent(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that strategic intents create Executive Intent."""
        with patch('app.notion_poller.AgentRouter') as mock_router_class:
            mock_router = AsyncMock()
            mock_router.classify_intent.return_value = {
                "type": "strategic",
                "title": "Launch Product",
                "agent": "The Entrepreneur",
                "risk": "High",
                "impact": 9
            }
            mock_router_class.return_value = mock_router

            # Mock find_agent_by_name
            notion_poller.find_agent_by_name = AsyncMock(return_value="agent_id_123")

            await notion_poller.process_intent(sample_notion_inbox_page)

            # Should create executive intent
            create_calls = [
                call for call in mock_notion_client.pages.create.call_args_list
            ]
            assert len(create_calls) > 0

    @pytest.mark.asyncio
    async def test_process_operational_updates_status(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that operational intents are marked correctly."""
        with patch('app.notion_poller.AgentRouter') as mock_router_class:
            mock_router = AsyncMock()
            mock_router.classify_intent.return_value = {
                "type": "operational",
                "title": "Update Dependencies",
                "agent": "The Entrepreneur",
                "risk": "Low",
                "impact": 2,
                "next_action": "Run update"
            }
            mock_router_class.return_value = mock_router

            await notion_poller.process_intent(sample_notion_inbox_page)

            # Should update status to Triaged_to_Task
            # Check final status update
            update_calls = mock_notion_client.pages.update.call_args_list
            final_call = update_calls[-1]
            assert "Status" in final_call.kwargs["properties"]

    @pytest.mark.asyncio
    async def test_process_reference_updates_status(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that reference intents are marked correctly."""
        with patch('app.notion_poller.AgentRouter') as mock_router_class:
            mock_router = AsyncMock()
            mock_router.classify_intent.return_value = {
                "type": "reference",
                "title": "API Docs",
                "agent": "The Entrepreneur",
                "risk": "Low",
                "impact": 1
            }
            mock_router_class.return_value = mock_router

            await notion_poller.process_intent(sample_notion_inbox_page)

            # Should update status to Triaged_to_Node
            update_calls = mock_notion_client.pages.update.call_args_list
            assert len(update_calls) >= 2  # Processing + Final

    @pytest.mark.asyncio
    async def test_process_intent_handles_errors(
        self, notion_poller, mock_notion_client, sample_notion_inbox_page
    ):
        """Test that processing errors are handled gracefully."""
        with patch('app.notion_poller.AgentRouter') as mock_router_class:
            mock_router = AsyncMock()
            mock_router.classify_intent.side_effect = Exception("Classification failed")
            mock_router_class.return_value = mock_router

            result = await notion_poller.process_intent(sample_notion_inbox_page)

            assert result is False


class TestUpdateStatus:
    """Test status update functionality."""

    @pytest.mark.asyncio
    async def test_update_status_calls_pages_update(self, notion_poller, mock_notion_client):
        """Test that update_status calls Notion API correctly."""
        await notion_poller.update_status("page_123", "Processing")

        mock_notion_client.pages.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_sets_correct_status(self, notion_poller, mock_notion_client):
        """Test that status is set correctly."""
        await notion_poller.update_status("page_123", "Done")

        call_args = mock_notion_client.pages.update.call_args
        status = call_args.kwargs["properties"]["Status"]["select"]["name"]
        assert status == "Done"

    @pytest.mark.asyncio
    async def test_update_status_raises_on_error(self, notion_poller, mock_notion_client):
        """Test that update errors are raised."""
        mock_notion_client.pages.update.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            await notion_poller.update_status("page_123", "Processing")


class TestCreateExecutiveIntent:
    """Test creating Executive Intent in Notion."""

    @pytest.mark.asyncio
    async def test_create_executive_intent_calls_pages_create(
        self, notion_poller, mock_notion_client
    ):
        """Test that executive intent creation calls Notion API."""
        notion_poller.find_agent_by_name = AsyncMock(return_value="agent_123")

        await notion_poller.create_executive_intent(
            title="Launch Product",
            description="Build SaaS",
            agent="The Entrepreneur",
            risk="High",
            impact=9,
            source_inbox_id="inbox_123"
        )

        mock_notion_client.pages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_executive_intent_sets_properties(
        self, notion_poller, mock_notion_client
    ):
        """Test that all required properties are set."""
        notion_poller.find_agent_by_name = AsyncMock(return_value="agent_123")

        await notion_poller.create_executive_intent(
            title="Test Intent",
            description="Test Description",
            agent="The Entrepreneur",
            risk="Medium",
            impact=7,
            source_inbox_id="inbox_123"
        )

        call_args = mock_notion_client.pages.create.call_args
        properties = call_args.kwargs["properties"]

        assert "Name" in properties
        assert "Description" in properties
        assert "Status" in properties
        assert "Risk_Level" in properties
        assert "Projected_Impact" in properties
        assert "Priority" in properties

    @pytest.mark.asyncio
    async def test_create_executive_intent_maps_impact_to_priority(
        self, notion_poller, mock_notion_client
    ):
        """Test that impact is correctly mapped to priority."""
        notion_poller.find_agent_by_name = AsyncMock(return_value="agent_123")

        # High impact -> P0
        await notion_poller.create_executive_intent(
            title="High Impact",
            description="Test",
            agent="The Entrepreneur",
            risk="Medium",
            impact=9,
            source_inbox_id="inbox_123"
        )

        call_args = mock_notion_client.pages.create.call_args
        priority = call_args.kwargs["properties"]["Priority"]["select"]["name"]
        assert priority == "P0"

    @pytest.mark.asyncio
    async def test_create_executive_intent_returns_page_id(
        self, notion_poller, mock_notion_client
    ):
        """Test that created page ID is returned."""
        notion_poller.find_agent_by_name = AsyncMock(return_value="agent_123")
        mock_notion_client.pages.create.return_value = {"id": "new_page_123"}

        page_id = await notion_poller.create_executive_intent(
            title="Test",
            description="Test",
            agent="The Entrepreneur",
            risk="Low",
            impact=5,
            source_inbox_id="inbox_123"
        )

        assert page_id == "new_page_123"


class TestFindAgentByName:
    """Test finding agent by name."""

    @pytest.mark.asyncio
    async def test_find_agent_by_name_queries_registry(
        self, notion_poller, mock_notion_client
    ):
        """Test that agent search queries the registry."""
        mock_notion_client.databases.query.return_value = {"results": []}

        await notion_poller.find_agent_by_name("The Entrepreneur")

        mock_notion_client.databases.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_agent_by_name_returns_id(
        self, notion_poller, mock_notion_client, sample_notion_agent_page
    ):
        """Test that agent ID is returned when found."""
        mock_notion_client.databases.query.return_value = {
            "results": [sample_notion_agent_page]
        }

        agent_id = await notion_poller.find_agent_by_name("The Entrepreneur")

        assert agent_id == sample_notion_agent_page["id"]

    @pytest.mark.asyncio
    async def test_find_agent_by_name_returns_none_when_not_found(
        self, notion_poller, mock_notion_client
    ):
        """Test that None is returned when agent not found."""
        mock_notion_client.databases.query.return_value = {"results": []}

        agent_id = await notion_poller.find_agent_by_name("Unknown Agent")

        assert agent_id is None

    @pytest.mark.asyncio
    async def test_find_agent_by_name_handles_errors(
        self, notion_poller, mock_notion_client
    ):
        """Test that errors are handled gracefully."""
        mock_notion_client.databases.query.side_effect = Exception("API Error")

        agent_id = await notion_poller.find_agent_by_name("The Entrepreneur")

        assert agent_id is None


class TestPropertyExtraction:
    """Test Notion property extraction helpers."""

    def test_extract_text_property_from_rich_text(self, notion_poller):
        """Test extracting text from rich_text property."""
        prop = {
            "rich_text": [
                {"plain_text": "Hello "},
                {"plain_text": "World"}
            ]
        }

        text = notion_poller.extract_text_property(prop)

        assert text == "Hello World"

    def test_extract_text_property_from_title(self, notion_poller):
        """Test extracting text from title property."""
        prop = {
            "title": [
                {"plain_text": "Test Title"}
            ]
        }

        text = notion_poller.extract_text_property(prop)

        assert text == "Test Title"

    def test_extract_text_property_empty(self, notion_poller):
        """Test extracting from empty property."""
        prop = {"rich_text": []}

        text = notion_poller.extract_text_property(prop)

        assert text == ""

    def test_extract_select_property(self, notion_poller):
        """Test extracting select property value."""
        prop = {
            "select": {
                "name": "High"
            }
        }

        value = notion_poller.extract_select_property(prop)

        assert value == "High"

    def test_extract_select_property_null(self, notion_poller):
        """Test extracting null select property."""
        prop = {"select": None}

        value = notion_poller.extract_select_property(prop)

        assert value is None
