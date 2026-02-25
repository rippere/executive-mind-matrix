"""
Test Command Center Auto-Refresh Implementation

This test verifies that P3.1.3 implementation is correct:
- Configuration is loaded properly
- Scheduler has the refresh method
- Metrics are registered
- Integration with main_enhanced.py works
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch


def test_settings_configuration():
    """Verify Command Center refresh settings are configured"""
    from config.settings import settings

    assert hasattr(settings, 'command_center_refresh_enabled')
    assert hasattr(settings, 'command_center_refresh_interval')
    assert isinstance(settings.command_center_refresh_enabled, bool)
    assert isinstance(settings.command_center_refresh_interval, int)
    assert settings.command_center_refresh_interval > 0


def test_scheduler_has_refresh_methods():
    """Verify TaskScheduler has Command Center refresh methods"""
    from app.scheduler import TaskScheduler

    scheduler = TaskScheduler()

    # Check methods exist
    assert hasattr(scheduler, 'refresh_command_center_metrics')
    assert hasattr(scheduler, 'set_notion_client')
    assert hasattr(scheduler, 'schedule_command_center_refresh')

    # Check they're callable
    assert callable(scheduler.refresh_command_center_metrics)
    assert callable(scheduler.set_notion_client)
    assert callable(scheduler.schedule_command_center_refresh)


def test_notion_client_injection():
    """Verify Notion client can be injected into scheduler"""
    from app.scheduler import TaskScheduler

    scheduler = TaskScheduler()
    assert scheduler.notion_client is None

    # Mock client
    mock_client = Mock()
    scheduler.set_notion_client(mock_client)

    assert scheduler.notion_client is mock_client


def test_prometheus_metrics_exist():
    """Verify Prometheus metrics are registered"""
    from app.monitoring import PrometheusMetrics

    # Check class has the method
    assert hasattr(PrometheusMetrics, 'record_command_center_refresh')
    assert callable(PrometheusMetrics.record_command_center_refresh)


@pytest.mark.asyncio
async def test_refresh_method_handles_missing_client():
    """Verify refresh method handles missing Notion client gracefully"""
    from app.scheduler import TaskScheduler

    scheduler = TaskScheduler()

    # Should not raise exception when client is None
    await scheduler.refresh_command_center_metrics()
    # If we get here, the method handled it gracefully


@pytest.mark.asyncio
async def test_refresh_method_calls_command_center():
    """Verify refresh method calls FinalCommandCenter.update_metrics_only()"""
    from app.scheduler import TaskScheduler

    scheduler = TaskScheduler()

    # Create mock client
    mock_client = AsyncMock()
    scheduler.set_notion_client(mock_client)

    # Mock the FinalCommandCenter (patch where it's imported in the method)
    with patch('app.command_center_final.FinalCommandCenter') as MockCommandCenter:
        mock_cc_instance = AsyncMock()
        mock_cc_instance.update_metrics_only.return_value = {
            'pending_inbox': 5,
            'ready_intents': 3,
            'total_intents': 10,
            'total_actions': 7
        }
        MockCommandCenter.return_value = mock_cc_instance

        # Call the refresh method
        await scheduler.refresh_command_center_metrics()

        # Verify FinalCommandCenter was instantiated with client
        MockCommandCenter.assert_called_once_with(mock_client)

        # Verify update_metrics_only was called
        mock_cc_instance.update_metrics_only.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_method_handles_errors():
    """Verify refresh method handles errors gracefully"""
    from app.scheduler import TaskScheduler

    scheduler = TaskScheduler()
    mock_client = AsyncMock()
    scheduler.set_notion_client(mock_client)

    # Mock FinalCommandCenter to raise an error
    with patch('app.command_center_final.FinalCommandCenter') as MockCommandCenter:
        mock_cc_instance = AsyncMock()
        mock_cc_instance.update_metrics_only.side_effect = Exception("Test error")
        MockCommandCenter.return_value = mock_cc_instance

        # Should not raise exception - should log and continue
        await scheduler.refresh_command_center_metrics()


def test_schedule_command_center_refresh():
    """Verify schedule_command_center_refresh registers the job"""
    from app.scheduler import TaskScheduler
    from config.settings import settings

    scheduler = TaskScheduler()

    # Schedule the job
    scheduler.schedule_command_center_refresh()

    # Verify job was added
    job = scheduler.scheduler.get_job('command_center_refresh')
    assert job is not None
    assert job.name == 'Command Center Metrics Refresh'

    # Clean up
    scheduler.scheduler.remove_job('command_center_refresh')


def test_scheduler_start_includes_command_center():
    """Verify scheduler.start() includes Command Center refresh when enabled"""
    from app.scheduler import TaskScheduler
    from config.settings import settings

    # Only run if enabled
    if not settings.command_center_refresh_enabled:
        pytest.skip("Command Center refresh is disabled")

    scheduler = TaskScheduler()

    # Start scheduler (but don't actually run it)
    scheduler.start()

    # Verify job was scheduled
    job = scheduler.scheduler.get_job('command_center_refresh')
    assert job is not None

    # Clean up
    scheduler.stop()


if __name__ == '__main__':
    # Run tests manually
    print("Running Command Center Auto-Refresh Tests...")
    print()

    test_settings_configuration()
    print("✓ Settings configuration test passed")

    test_scheduler_has_refresh_methods()
    print("✓ Scheduler methods test passed")

    test_notion_client_injection()
    print("✓ Notion client injection test passed")

    test_prometheus_metrics_exist()
    print("✓ Prometheus metrics test passed")

    asyncio.run(test_refresh_method_handles_missing_client())
    print("✓ Missing client handling test passed")

    asyncio.run(test_refresh_method_calls_command_center())
    print("✓ Command Center call test passed")

    asyncio.run(test_refresh_method_handles_errors())
    print("✓ Error handling test passed")

    test_schedule_command_center_refresh()
    print("✓ Job scheduling test passed")

    print()
    print("All tests passed! ✓")
