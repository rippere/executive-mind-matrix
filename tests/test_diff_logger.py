"""
Unit tests for app/diff_logger.py

Tests diff calculation, acceptance rate computation, and training data logging.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from deepdiff import DeepDiff

from app.diff_logger import DiffLogger
from app.models import SettlementDiff


@pytest.fixture
def diff_logger(mock_notion_client):
    """Create DiffLogger instance with mocked Notion client."""
    with patch('notion_client.AsyncClient', return_value=mock_notion_client):
        logger = DiffLogger()
        logger.client = mock_notion_client
        return logger


class TestDiffLoggerInit:
    """Test DiffLogger initialization."""

    def test_init_creates_notion_client(self):
        """Test that DiffLogger initializes with Notion client."""
        with patch('notion_client.AsyncClient') as mock_client:
            logger = DiffLogger()
            mock_client.assert_called_once()


class TestExtractModifications:
    """Test extraction of human modifications from DeepDiff."""

    def test_extract_values_changed(self, diff_logger):
        """Test extracting changed values."""
        original = {"option": "A", "value": 10}
        final = {"option": "B", "value": 20}
        diff = DeepDiff(original, final)

        modifications = diff_logger._extract_modifications(diff)

        assert len(modifications) >= 2
        assert any("option" in mod for mod in modifications)
        assert any("value" in mod for mod in modifications)

    def test_extract_items_added(self, diff_logger):
        """Test extracting added items."""
        original = {"key1": "value1"}
        final = {"key1": "value1", "key2": "value2"}
        diff = DeepDiff(original, final)

        modifications = diff_logger._extract_modifications(diff)

        assert any("Added" in mod and "key2" in mod for mod in modifications)

    def test_extract_items_removed(self, diff_logger):
        """Test extracting removed items."""
        original = {"key1": "value1", "key2": "value2"}
        final = {"key1": "value1"}
        diff = DeepDiff(original, final)

        modifications = diff_logger._extract_modifications(diff)

        assert any("Removed" in mod and "key2" in mod for mod in modifications)

    def test_extract_type_changes(self, diff_logger):
        """Test extracting type changes."""
        original = {"value": "123"}
        final = {"value": 123}
        diff = DeepDiff(original, final)

        modifications = diff_logger._extract_modifications(diff)

        # DeepDiff should detect type change
        if "type_changes" in diff:
            assert any("Type changed" in mod for mod in modifications)

    def test_extract_no_changes(self, diff_logger):
        """Test with no changes returns empty list."""
        original = {"key": "value"}
        final = {"key": "value"}
        diff = DeepDiff(original, final)

        modifications = diff_logger._extract_modifications(diff)

        assert len(modifications) == 0


class TestCountLeafKeys:
    """Test counting leaf keys in nested structures."""

    def test_count_simple_dict(self, diff_logger):
        """Test counting keys in simple dict."""
        data = {"a": 1, "b": 2, "c": 3}
        count = diff_logger._count_leaf_keys(data)
        assert count == 3

    def test_count_nested_dict(self, diff_logger):
        """Test counting keys in nested dict."""
        data = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            }
        }
        count = diff_logger._count_leaf_keys(data)
        assert count == 3  # a, c, d are leaf nodes

    def test_count_with_list(self, diff_logger):
        """Test counting with list values."""
        data = {
            "items": [1, 2, 3],
            "name": "test"
        }
        count = diff_logger._count_leaf_keys(data)
        assert count == 4  # 3 list items + 1 name

    def test_count_complex_structure(self, diff_logger):
        """Test counting in complex nested structure."""
        data = {
            "option": "A",
            "tasks": [
                {"id": 1, "name": "Task 1"},
                {"id": 2, "name": "Task 2"}
            ],
            "metadata": {
                "created": "2024-01-01",
                "tags": ["tag1", "tag2"]
            }
        }
        # Leaf keys: option, id, name, id, name, created, tag1, tag2
        count = diff_logger._count_leaf_keys(data)
        assert count == 8

    def test_count_empty_dict(self, diff_logger):
        """Test counting empty dict returns 0."""
        count = diff_logger._count_leaf_keys({})
        assert count == 0


class TestCalculateAcceptanceRate:
    """Test acceptance rate calculation."""

    def test_acceptance_rate_no_changes(self, diff_logger):
        """Test 100% acceptance when no changes made."""
        original = {"option": "A", "value": 10}
        final = {"option": "A", "value": 10}
        diff = DeepDiff(original, final)

        rate = diff_logger._calculate_acceptance_rate(original, final, diff)

        assert rate == 1.0

    def test_acceptance_rate_all_changed(self, diff_logger):
        """Test low acceptance when everything changed."""
        original = {"option": "A", "value": 10}
        final = {"option": "B", "value": 20}
        diff = DeepDiff(original, final)

        rate = diff_logger._calculate_acceptance_rate(original, final, diff)

        # Should be 0% since both values changed
        assert rate == 0.0

    def test_acceptance_rate_partial_changes(self, diff_logger):
        """Test partial acceptance rate."""
        original = {"a": 1, "b": 2, "c": 3, "d": 4}
        final = {"a": 1, "b": 2, "c": 99, "d": 4}  # Only c changed
        diff = DeepDiff(original, final)

        rate = diff_logger._calculate_acceptance_rate(original, final, diff)

        # 3 out of 4 keys unchanged = 75%
        assert rate == 0.75

    def test_acceptance_rate_empty_original(self, diff_logger):
        """Test acceptance rate with empty original."""
        original = {}
        final = {"key": "value"}
        diff = DeepDiff(original, final)

        rate = diff_logger._calculate_acceptance_rate(original, final, diff)

        assert rate == 0.0

    def test_acceptance_rate_never_negative(self, diff_logger):
        """Test acceptance rate never goes negative."""
        original = {"a": 1}
        final = {"a": 2, "b": 3, "c": 4}  # More changes than original keys
        diff = DeepDiff(original, final)

        rate = diff_logger._calculate_acceptance_rate(original, final, diff)

        assert rate >= 0.0


class TestLogSettlementDiff:
    """Test main log_settlement_diff method."""

    @pytest.mark.asyncio
    async def test_log_settlement_diff_success(self, diff_logger, mock_notion_client):
        """Test successful settlement diff logging."""
        original_plan = {"option": "A", "tasks": ["Task 1", "Task 2"]}
        final_plan = {"option": "B", "tasks": ["Task 1", "Task 3"]}

        with patch('aiofiles.open', create=True):
            with patch('os.makedirs'):
                result = await diff_logger.log_settlement_diff(
                    intent_id="test_intent_123",
                    original_plan=original_plan,
                    final_plan=final_plan
                )

        assert isinstance(result, SettlementDiff)
        assert result.intent_id == "test_intent_123"
        assert result.original_plan == original_plan
        assert result.final_plan == final_plan
        assert len(result.user_modifications) > 0
        assert 0 <= result.acceptance_rate <= 1.0

    @pytest.mark.asyncio
    async def test_log_settlement_diff_calculates_modifications(self, diff_logger):
        """Test that modifications are calculated correctly."""
        original_plan = {"option": "A"}
        final_plan = {"option": "B"}

        with patch('aiofiles.open', create=True):
            with patch('os.makedirs'):
                result = await diff_logger.log_settlement_diff(
                    intent_id="test_123",
                    original_plan=original_plan,
                    final_plan=final_plan
                )

        assert len(result.user_modifications) > 0
        assert any("option" in mod for mod in result.user_modifications)

    @pytest.mark.asyncio
    async def test_log_settlement_diff_saves_to_notion(self, diff_logger, mock_notion_client):
        """Test that diff is saved to Notion."""
        original_plan = {"test": "data"}
        final_plan = {"test": "modified"}

        with patch('aiofiles.open', create=True):
            with patch('os.makedirs'):
                await diff_logger.log_settlement_diff(
                    intent_id="test_123",
                    original_plan=original_plan,
                    final_plan=final_plan
                )

        mock_notion_client.pages.create.assert_called_once()

        call_args = mock_notion_client.pages.create.call_args
        assert call_args.kwargs["parent"]["database_id"]
        assert "Title" in call_args.kwargs["properties"]

    @pytest.mark.asyncio
    async def test_log_settlement_diff_complex_structures(self, diff_logger):
        """Test logging diff with complex nested structures."""
        original_plan = {
            "option": "A",
            "tasks": [
                {"id": 1, "name": "Task 1", "subtasks": ["a", "b"]},
                {"id": 2, "name": "Task 2", "subtasks": []}
            ],
            "metadata": {"version": 1}
        }
        final_plan = {
            "option": "B",
            "tasks": [
                {"id": 1, "name": "Task 1 Modified", "subtasks": ["a", "b", "c"]},
                {"id": 3, "name": "Task 3", "subtasks": []}
            ],
            "metadata": {"version": 2, "editor": "human"}
        }

        with patch('aiofiles.open', create=True):
            with patch('os.makedirs'):
                result = await diff_logger.log_settlement_diff(
                    intent_id="test_complex",
                    original_plan=original_plan,
                    final_plan=final_plan
                )

        assert result.acceptance_rate < 1.0  # Should have changes
        assert len(result.user_modifications) > 0


class TestSaveToNotion:
    """Test saving settlement diff to Notion."""

    @pytest.mark.asyncio
    async def test_save_to_notion_creates_page(self, diff_logger, mock_notion_client, sample_settlement_diff):
        """Test that save_to_notion creates a Notion page."""
        await diff_logger._save_to_notion(sample_settlement_diff)

        mock_notion_client.pages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_to_notion_includes_required_properties(
        self, diff_logger, mock_notion_client, sample_settlement_diff
    ):
        """Test that all required properties are included."""
        await diff_logger._save_to_notion(sample_settlement_diff)

        call_args = mock_notion_client.pages.create.call_args
        properties = call_args.kwargs["properties"]

        assert "Title" in properties
        assert "Intent_ID" in properties
        assert "Timestamp" in properties
        assert "Acceptance_Rate" in properties
        assert "Modifications_Count" in properties

    @pytest.mark.asyncio
    async def test_save_to_notion_handles_errors(self, diff_logger, mock_notion_client, sample_settlement_diff):
        """Test that Notion save errors are handled gracefully."""
        mock_notion_client.pages.create.side_effect = Exception("Notion API error")

        # Should not raise exception
        await diff_logger._save_to_notion(sample_settlement_diff)


class TestSaveToJsonLog:
    """Test saving settlement diff to JSON log file."""

    @pytest.mark.asyncio
    async def test_save_to_json_log_creates_file(self, diff_logger, sample_settlement_diff, tmp_path):
        """Test that JSON log file is created."""
        log_file = tmp_path / "settlement_diffs.jsonl"

        with patch('aiofiles.open', create=True) as mock_open:
            mock_file = AsyncMock()
            mock_open.return_value.__aenter__.return_value = mock_file

            with patch('os.makedirs'):
                await diff_logger._save_to_json_log(sample_settlement_diff)

            mock_file.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_to_json_log_handles_errors(self, diff_logger, sample_settlement_diff):
        """Test that JSON save errors are handled gracefully."""
        with patch('aiofiles.open', side_effect=Exception("File error")):
            # Should not raise exception
            await diff_logger._save_to_json_log(sample_settlement_diff)


class TestGetAgentPerformanceMetrics:
    """Test agent performance metrics retrieval."""

    @pytest.mark.asyncio
    async def test_get_metrics_with_data(self, diff_logger, mock_notion_client):
        """Test retrieving metrics when data exists."""
        mock_notion_client.databases.query.return_value = {
            "results": [
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

        metrics = await diff_logger.get_agent_performance_metrics("The Entrepreneur")

        assert metrics["agent"] == "The Entrepreneur"
        assert metrics["total_settlements"] == 2
        assert metrics["avg_acceptance_rate"] == 0.80  # (75 + 85) / 2 / 100

    @pytest.mark.asyncio
    async def test_get_metrics_no_data(self, diff_logger, mock_notion_client):
        """Test retrieving metrics when no data exists."""
        mock_notion_client.databases.query.return_value = {"results": []}

        metrics = await diff_logger.get_agent_performance_metrics("The Quant")

        assert metrics["agent"] == "The Quant"
        assert metrics["total_settlements"] == 0
        assert metrics["avg_acceptance_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_get_metrics_with_empty_acceptance_rates(self, diff_logger, mock_notion_client):
        """Test metrics calculation with empty acceptance rate data."""
        mock_notion_client.databases.query.return_value = {
            "results": [
                {
                    "properties": {
                        "Acceptance_Rate": {"number": None}
                    }
                },
                {
                    "properties": {
                        "Acceptance_Rate": {"number": 0}
                    }
                }
            ]
        }

        metrics = await diff_logger.get_agent_performance_metrics("The Auditor")

        # Should handle empty/null values gracefully
        assert metrics["agent"] == "The Auditor"
        assert metrics["total_settlements"] == 2

    @pytest.mark.asyncio
    async def test_get_metrics_handles_api_errors(self, diff_logger, mock_notion_client):
        """Test that API errors are handled gracefully."""
        mock_notion_client.databases.query.side_effect = Exception("API error")

        metrics = await diff_logger.get_agent_performance_metrics("The Entrepreneur")

        assert metrics == {}
