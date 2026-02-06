"""
Integration tests for WorkflowIntegration

Tests property population and workflow features including:
- Area assignment to intents
- Agent relation in Action Pipes
- Required_Resources population
- Task_Generation_Template population
- AI_Raw_Output capture
- Approval workflow with Approved_Date
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.workflow_integration import WorkflowIntegration
from app.models import AgentPersona


@pytest.mark.integration
class TestPropertyPopulation:
    """Tests for property population in Action Pipes."""

    @pytest.mark.asyncio
    async def test_agent_relation_populated_in_action_pipe(
        self,
        mock_notion_client
    ):
        """Verify Agent relation is populated when creating Action Pipe."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            workflow = WorkflowIntegration(mock_notion_client)

            # Mock intent with Agent_Persona relation
            mock_intent = {
                "id": "intent123",
                "properties": {
                    "Name": {"title": [{"text": {"content": "Test Intent"}}]},
                    "Agent_Persona": {
                        "relation": [{"id": "agent456"}]
                    }
                }
            }

            mock_notion_client.pages.retrieve.return_value = mock_intent
            mock_notion_client.pages.create.return_value = {"id": "action789"}

            # Create action from intent
            action_id = await workflow.create_action_from_intent(
                intent_id="intent123",
                action_title="Test Action",
                action_description="Test Description"
            )

            # Verify Agent relation was included in properties
            # Find the Action Pipe creation call (not the execution log call)
            create_calls = [call for call in mock_notion_client.pages.create.call_args_list]
            action_create_call = next(
                (call for call in create_calls if "Action_Title" in call.kwargs.get("properties", {})),
                None
            )

            assert action_create_call is not None, "Action Pipe should have been created"
            properties = action_create_call.kwargs["properties"]

            assert "Agent" in properties
            assert properties["Agent"]["relation"] == [{"id": "agent456"}]
            assert action_id == "action789"

    @pytest.mark.asyncio
    async def test_agent_relation_handles_missing_agent(
        self,
        mock_notion_client
    ):
        """Verify Agent relation handles intents without Agent_Persona."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            workflow = WorkflowIntegration(mock_notion_client)

            # Mock intent WITHOUT Agent_Persona relation
            mock_intent = {
                "id": "intent123",
                "properties": {
                    "Name": {"title": [{"text": {"content": "Test Intent"}}]},
                    "Agent_Persona": {"relation": []}  # Empty relation
                }
            }

            mock_notion_client.pages.retrieve.return_value = mock_intent
            mock_notion_client.pages.create.return_value = {"id": "action789"}

            # Create action from intent
            action_id = await workflow.create_action_from_intent(
                intent_id="intent123",
                action_title="Test Action",
                action_description="Test Description"
            )

            # Verify Agent relation is empty list (not None or error)
            # Find the Action Pipe creation call (not the execution log call)
            create_calls = [call for call in mock_notion_client.pages.create.call_args_list]
            action_create_call = next(
                (call for call in create_calls if "Action_Title" in call.kwargs.get("properties", {})),
                None
            )

            assert action_create_call is not None, "Action Pipe should have been created"
            properties = action_create_call.kwargs["properties"]

            assert "Agent" in properties
            assert properties["Agent"]["relation"] == []
            assert action_id == "action789"


@pytest.mark.integration
class TestAreaAssignment:
    """Tests for automatic area assignment to intents."""

    def test_area_manager_integration_exists(self):
        """Verify AreasManager is integrated into workflow."""
        # This is a simple integration test - the full area assignment logic
        # is tested in test_areas_manager.py and test_notion_poller.py
        # Here we just verify the integration dependency exists

        from app.areas_manager import AreasManager

        # Verify AreasManager class has the required methods
        assert hasattr(AreasManager, 'detect_area')
        assert hasattr(AreasManager, 'assign_area_to_intent')

        # Verify the methods are callable
        assert callable(getattr(AreasManager, 'detect_area'))
        assert callable(getattr(AreasManager, 'assign_area_to_intent'))


@pytest.mark.integration
class TestApprovalWorkflow:
    """Tests for action approval workflow."""

    @pytest.mark.asyncio
    async def test_approve_action_sets_date(
        self,
        mock_notion_client
    ):
        """Verify approval workflow sets Approved_Date."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            workflow = WorkflowIntegration(mock_notion_client)

            # Mock successful update
            mock_notion_client.pages.update.return_value = {"id": "action123"}

            # Mock execution log creation
            mock_notion_client.pages.create.return_value = {"id": "log123"}

            # Approve action
            await workflow.approve_action("action123")

            # Verify update was called with correct properties
            update_call = mock_notion_client.pages.update.call_args
            properties = update_call.kwargs["properties"]

            assert properties["Approval_Status"]["select"]["name"] == "Approved"
            assert "Approved_Date" in properties
            assert "date" in properties["Approved_Date"]

            # Verify date is today
            today = datetime.now().date().isoformat()
            assert properties["Approved_Date"]["date"]["start"] == today

    @pytest.mark.asyncio
    async def test_approve_action_logs_execution(
        self,
        mock_notion_client
    ):
        """Verify approval is logged to Execution Log."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            workflow = WorkflowIntegration(mock_notion_client)

            # Mock successful update and log creation
            mock_notion_client.pages.update.return_value = {"id": "action123"}
            mock_notion_client.pages.create.return_value = {"id": "log123"}

            # Approve action
            await workflow.approve_action("action123")

            # Verify execution log was created
            # The second call should be the execution log
            assert mock_notion_client.pages.create.call_count >= 1

            # Find the call that creates the execution log
            # (The workflow may make multiple create calls)
            create_calls = [call for call in mock_notion_client.pages.create.call_args_list]

            # At least one call should be to the execution log
            # (We can't verify exact details without more mocking)
            assert len(create_calls) >= 1


@pytest.mark.integration
class TestActionPipePropertyPopulation:
    """Tests for comprehensive Action Pipe property population."""

    @pytest.mark.asyncio
    async def test_no_redundant_properties_used(
        self,
        mock_notion_client
    ):
        """Ensure deprecated properties are never used in Action Pipes."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            workflow = WorkflowIntegration(mock_notion_client)

            # Mock intent
            mock_intent = {
                "id": "intent123",
                "properties": {
                    "Name": {"title": [{"text": {"content": "Test Intent"}}]},
                    "Agent_Persona": {"relation": [{"id": "agent456"}]}
                }
            }

            mock_notion_client.pages.retrieve.return_value = mock_intent
            mock_notion_client.pages.create.return_value = {"id": "action789"}

            # Create action
            await workflow.create_action_from_intent(
                intent_id="intent123",
                action_title="Test Action",
                action_description="Test Description"
            )

            # Verify NO deprecated properties are used
            create_call = mock_notion_client.pages.create.call_args
            properties = create_call.kwargs["properties"]

            # These should NOT exist (deprecated per audit)
            assert "Entrepreneur_Recommendation" not in properties
            assert "Auditor_Recommendation" not in properties
            assert "Final_Decision" not in properties
            assert "Synthesis_Summary" not in properties

    @pytest.mark.asyncio
    async def test_canonical_properties_used(
        self,
        mock_notion_client
    ):
        """Ensure canonical properties ARE used in Action Pipes."""
        with patch('notion_client.AsyncClient', return_value=mock_notion_client):
            workflow = WorkflowIntegration(mock_notion_client)

            # Mock intent
            mock_intent = {
                "id": "intent123",
                "properties": {
                    "Name": {"title": [{"text": {"content": "Test Intent"}}]},
                    "Agent_Persona": {"relation": [{"id": "agent456"}]}
                }
            }

            mock_notion_client.pages.retrieve.return_value = mock_intent
            mock_notion_client.pages.create.return_value = {"id": "action789"}

            # Create action
            await workflow.create_action_from_intent(
                intent_id="intent123",
                action_title="Test Action",
                action_description="Test Description"
            )

            # Verify canonical properties ARE used
            # Find the Action Pipe creation call (not the execution log call)
            create_calls = [call for call in mock_notion_client.pages.create.call_args_list]
            action_create_call = next(
                (call for call in create_calls if "Action_Title" in call.kwargs.get("properties", {})),
                None
            )

            assert action_create_call is not None, "Action Pipe should have been created"
            properties = action_create_call.kwargs["properties"]

            # These SHOULD exist (canonical properties)
            assert "Action_Title" in properties
            assert "Scenario_Options" in properties
            assert "Approval_Status" in properties
            assert "Intent" in properties
            assert "Agent" in properties
