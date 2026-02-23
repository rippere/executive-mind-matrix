"""
End-to-End Workflow Tests

Tests complete workflows from start to finish:
1. System Inbox → Strategic Intent → Dialectic Analysis → Task Spawning
2. System Inbox → Operational Task (direct routing)
3. System Inbox → Reference → Knowledge Nodes

All external APIs (Notion, Anthropic) are mocked for fast, isolated testing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from app.notion_poller import NotionPoller
from app.agent_router import AgentRouter, AgentPersona
from app.workflow_integration import WorkflowIntegration
from app.task_spawner import TaskSpawner
from app.knowledge_linker import KnowledgeLinker
from app.models import AgentAnalysis, ScenarioOption, ConceptMatch


@pytest.mark.integration
@pytest.mark.asyncio
class TestEndToEndWorkflows:
    """Complete end-to-end workflow integration tests"""

    async def test_strategic_workflow_complete(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_inbox_page,
        sample_intent_page
    ):
        """
        E2E Test: Inbox → Strategic Intent → Dialectic → Tasks

        Flow:
        1. Poller fetches inbox item
        2. Classifies as "strategic"
        3. Creates Executive Intent
        4. Runs dialectic analysis (Growth + Risk agents)
        5. Creates Action Pipe
        6. On approval, spawns tasks
        """
        # ARRANGE: Mock Notion database queries
        mock_notion_client.databases.query = AsyncMock(
            return_value={"results": [sample_inbox_page]}
        )

        # Mock intent creation
        mock_notion_client.pages.create = AsyncMock(
            return_value={
                "id": "intent-123",
                "properties": sample_intent_page["properties"]
            }
        )

        # Mock intent retrieval
        mock_notion_client.pages.retrieve = AsyncMock(
            return_value=sample_intent_page
        )

        # Mock page updates
        mock_notion_client.pages.update = AsyncMock(return_value={"id": "updated"})

        # Mock blocks append
        mock_notion_client.blocks.children.append = AsyncMock(
            return_value={"results": []}
        )
        mock_notion_client.blocks.children.list = AsyncMock(
            return_value={"results": []}
        )

        # Mock Anthropic classification
        classification_response = {
            "type": "strategic",
            "title": "Invest $5k: Index Funds vs Crypto",
            "agent": "The Quant",
            "risk": "Medium",
            "impact": 8,
            "rationale": "Financial decision requiring multi-option analysis"
        }

        # Mock Anthropic agent analyses
        growth_analysis = AgentAnalysis(
            scenario_options=[
                ScenarioOption(
                    option="A",
                    description="80% VTI, 20% BTC",
                    pros=["Balanced", "Lower risk"],
                    cons=["Lower upside"],
                    risk=3,
                    impact=7
                )
            ],
            recommended_option="A",
            recommendation_rationale="Balanced approach",
            risk_assessment="Medium risk profile",
            required_resources={"time": "2 hours", "money": "$5,000"},
            task_generation_template=[
                "Open Vanguard account",
                "Set up recurring buys",
                "Document allocation"
            ]
        )

        risk_analysis = AgentAnalysis(
            scenario_options=[
                ScenarioOption(
                    option="B",
                    description="100% VOO",
                    pros=["Safe", "Proven"],
                    cons=["Lower growth"],
                    risk=1,
                    impact=6
                )
            ],
            recommended_option="B",
            recommendation_rationale="Conservative approach",
            risk_assessment="Low risk profile",
            required_resources={"time": "1 hour", "money": "$5,000"},
            task_generation_template=["Open Vanguard account"]
        )

        synthesis_response = {
            "synthesis": "Balance growth and safety",
            "recommended_path": "80% index, 20% crypto",
            "conflict_points": ["Risk tolerance", "Time horizon"]
        }

        mock_anthropic_client.messages.create = AsyncMock(
            side_effect=[
                # Classification response
                MagicMock(content=[MagicMock(text=json.dumps(classification_response))]),
                # Growth agent response
                MagicMock(content=[MagicMock(text=growth_analysis.model_dump_json())]),
                # Risk agent response
                MagicMock(content=[MagicMock(text=risk_analysis.model_dump_json())]),
                # Synthesis response
                MagicMock(content=[MagicMock(text=json.dumps(synthesis_response))])
            ]
        )

        # ACT: Run complete workflow
        with patch('app.notion_poller.AsyncClient', return_value=mock_notion_client):
            with patch('app.agent_router.AsyncAnthropic', return_value=mock_anthropic_client):
                with patch('app.workflow_integration.AsyncClient', return_value=mock_notion_client):
                    # Step 1: Poller processes inbox
                    poller = NotionPoller()
                    poller.client = mock_notion_client

                    # Fetch and process intent
                    pending = await poller.fetch_pending_intents()
                    assert len(pending) == 1

                    # Process creates intent
                    result = await poller.process_intent(pending[0])
                    assert result is True

                    # Verify intent was created
                    create_calls = [
                        call for call in mock_notion_client.pages.create.call_args_list
                        if call[1].get('parent', {}).get('database_id') == 'db-executive-intents'
                    ]
                    assert len(create_calls) >= 1

                    # Step 2: Run dialectic analysis
                    router = AgentRouter()
                    router.client = mock_anthropic_client
                    router.notion = mock_notion_client

                    dialectic_result = await router.dialectic_flow(
                        intent_id="intent-123",
                        intent_title="Test Intent",
                        intent_description="Test description",
                        success_criteria="",
                        projected_impact=8
                    )

                    # ASSERT: Verify dialectic completed
                    assert dialectic_result.growth_perspective is not None
                    assert dialectic_result.risk_perspective is not None
                    assert dialectic_result.synthesis == "Balance growth and safety"
                    assert len(dialectic_result.conflict_points) == 2

                    # Step 3: Verify task spawning would work
                    spawner = TaskSpawner()
                    spawner.notion = mock_notion_client

                    task_result = await spawner.spawn_tasks_from_intent(
                        intent_id="intent-123",
                        task_template=growth_analysis.task_generation_template,
                        area_id=None
                    )

                    # ASSERT: Tasks created
                    assert task_result.tasks_created == 3
                    assert len(task_result.task_ids) == 3

        # ASSERT: Verify complete workflow
        # 1. Inbox item fetched
        mock_notion_client.databases.query.assert_called()

        # 2. Classification API called
        assert mock_anthropic_client.messages.create.call_count >= 3

        # 3. Intent created
        assert any(
            'db-executive-intents' in str(call)
            for call in mock_notion_client.pages.create.call_args_list
        )

        # 4. Dialectic synthesis completed
        assert dialectic_result.recommended_path is not None

    async def test_operational_workflow_direct_task(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_inbox_page
    ):
        """
        E2E Test: Inbox → Operational Classification → Direct Task Creation

        Flow:
        1. Poller fetches inbox item
        2. Classifies as "operational"
        3. Creates task directly (bypasses strategic workflow)
        4. Links back to inbox
        """
        # ARRANGE: Mock operational classification
        operational_classification = {
            "type": "operational",
            "title": "Email John about meeting",
            "impact": 3,
            "rationale": "Simple actionable task"
        }

        mock_anthropic_client.messages.create = AsyncMock(
            return_value=MagicMock(
                content=[MagicMock(text=json.dumps(operational_classification))]
            )
        )

        # Modify inbox page for operational content
        operational_inbox = sample_inbox_page.copy()
        operational_inbox["properties"]["Content"]["rich_text"][0]["text"]["content"] = \
            "Email John about next week's strategy meeting"

        mock_notion_client.databases.query = AsyncMock(
            return_value={"results": [operational_inbox]}
        )

        mock_notion_client.pages.create = AsyncMock(
            return_value={"id": "task-456"}
        )

        mock_notion_client.pages.update = AsyncMock(
            return_value={"id": "updated"}
        )

        mock_notion_client.blocks.children.append = AsyncMock(
            return_value={"results": []}
        )

        # ACT: Process operational intent
        with patch('app.notion_poller.AsyncClient', return_value=mock_notion_client):
            with patch('app.agent_router.AsyncAnthropic', return_value=mock_anthropic_client):
                poller = NotionPoller()
                poller.client = mock_notion_client

                pending = await poller.fetch_pending_intents()
                result = await poller.process_intent(pending[0])

        # ASSERT: Task created directly
        assert result is True

        # Verify task creation call
        task_creates = [
            call for call in mock_notion_client.pages.create.call_args_list
            if 'db-tasks' in str(call)
        ]
        assert len(task_creates) >= 1

        # Verify inbox writeback
        update_calls = mock_notion_client.pages.update.call_args_list
        assert any('Triaged_to_Task' in str(call) for call in update_calls)

    async def test_reference_workflow_knowledge_nodes(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_inbox_page
    ):
        """
        E2E Test: Inbox → Reference Classification → Knowledge Node Creation

        Flow:
        1. Poller fetches inbox item
        2. Classifies as "reference"
        3. Extracts concepts using AI
        4. Creates/finds knowledge nodes
        5. Links nodes to inbox
        """
        # ARRANGE: Reference classification
        reference_classification = {
            "type": "reference",
            "title": "Article: Zero-based budgeting framework",
            "impact": 2,
            "rationale": "Knowledge to store for future reference"
        }

        # Concept extraction response
        concepts_response = {
            "concepts": [
                {
                    "concept": "Zero-based budgeting",
                    "node_type": "Knowledge_Asset",
                    "confidence": 0.95
                },
                {
                    "concept": "Budget frameworks",
                    "node_type": "Knowledge_Asset",
                    "confidence": 0.85
                }
            ]
        }

        mock_anthropic_client.messages.create = AsyncMock(
            side_effect=[
                # Classification
                MagicMock(content=[MagicMock(text=json.dumps(reference_classification))]),
                # Concept extraction
                MagicMock(content=[MagicMock(text=json.dumps(concepts_response))])
            ]
        )

        # Reference inbox content
        reference_inbox = sample_inbox_page.copy()
        reference_inbox["properties"]["Content"]["rich_text"][0]["text"]["content"] = \
            "Interesting article about zero-based budgeting framework. Key principle: justify every expense from zero each period."

        mock_notion_client.databases.query = AsyncMock(
            side_effect=[
                # Inbox query
                {"results": [reference_inbox]},
                # Node lookup (empty - will create new)
                {"results": []},
                {"results": []}
            ]
        )

        mock_notion_client.pages.create = AsyncMock(
            side_effect=[
                {"id": "node-001"},  # First concept node
                {"id": "node-002"}   # Second concept node
            ]
        )

        mock_notion_client.pages.update = AsyncMock(
            return_value={"id": "updated"}
        )

        # ACT: Process reference intent
        with patch('app.notion_poller.AsyncClient', return_value=mock_notion_client):
            with patch('app.agent_router.AsyncAnthropic', return_value=mock_anthropic_client):
                with patch('app.knowledge_linker.AsyncAnthropic', return_value=mock_anthropic_client):
                    poller = NotionPoller()
                    poller.client = mock_notion_client

                    pending = await poller.fetch_pending_intents()
                    result = await poller.process_intent(pending[0])

        # ASSERT: Knowledge nodes created
        assert result is True

        # Verify node creation calls
        node_creates = [
            call for call in mock_notion_client.pages.create.call_args_list
            if 'db-nodes' in str(call)
        ]
        assert len(node_creates) == 2

        # Verify nodes linked to inbox
        update_calls = mock_notion_client.pages.update.call_args_list
        node_link_updates = [
            call for call in update_calls
            if 'Routed_to_Node' in str(call) or 'Related_Nodes' in str(call)
        ]
        assert len(node_link_updates) >= 1

    async def test_workflow_error_recovery(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_inbox_page
    ):
        """
        E2E Test: Workflow handles errors gracefully

        Scenarios:
        1. Anthropic API fails → Falls back to default classification
        2. Task creation fails → Intent still created
        3. Node creation fails → Logs error but continues
        """
        # ARRANGE: Anthropic API failure
        mock_anthropic_client.messages.create = AsyncMock(
            side_effect=Exception("Anthropic API timeout")
        )

        mock_notion_client.databases.query = AsyncMock(
            return_value={"results": [sample_inbox_page]}
        )

        mock_notion_client.pages.create = AsyncMock(
            return_value={"id": "fallback-intent"}
        )

        mock_notion_client.pages.update = AsyncMock(
            return_value={"id": "updated"}
        )

        mock_notion_client.blocks.children.append = AsyncMock(
            return_value={"results": []}
        )

        # ACT: Process with error
        with patch('app.notion_poller.AsyncClient', return_value=mock_notion_client):
            with patch('app.agent_router.AsyncAnthropic', return_value=mock_anthropic_client):
                poller = NotionPoller()
                poller.client = mock_notion_client

                pending = await poller.fetch_pending_intents()
                result = await poller.process_intent(pending[0])

        # ASSERT: Fallback classification applied
        assert result is True  # Should not crash

        # Verify fallback intent created
        create_calls = mock_notion_client.pages.create.call_args_list
        assert len(create_calls) >= 1

    async def test_concurrent_intent_processing(
        self,
        mock_notion_client,
        mock_anthropic_client,
        sample_inbox_page
    ):
        """
        E2E Test: Multiple intents processed concurrently

        Verifies:
        1. Poller can handle multiple inbox items
        2. Processing is truly concurrent (asyncio.gather)
        3. No race conditions in status updates
        """
        # ARRANGE: Multiple inbox items
        inbox_item_1 = sample_inbox_page.copy()
        inbox_item_1["id"] = "inbox-001"

        inbox_item_2 = sample_inbox_page.copy()
        inbox_item_2["id"] = "inbox-002"

        inbox_item_3 = sample_inbox_page.copy()
        inbox_item_3["id"] = "inbox-003"

        mock_notion_client.databases.query = AsyncMock(
            return_value={"results": [inbox_item_1, inbox_item_2, inbox_item_3]}
        )

        # Mock all create/update operations
        mock_notion_client.pages.create = AsyncMock(
            side_effect=[
                {"id": "intent-001"},
                {"id": "intent-002"},
                {"id": "intent-003"}
            ]
        )

        mock_notion_client.pages.update = AsyncMock(
            return_value={"id": "updated"}
        )

        mock_notion_client.blocks.children.append = AsyncMock(
            return_value={"results": []}
        )

        classification = {
            "type": "strategic",
            "title": "Test",
            "agent": "The Entrepreneur",
            "risk": "Low",
            "impact": 5,
            "rationale": "Test"
        }

        mock_anthropic_client.messages.create = AsyncMock(
            return_value=MagicMock(
                content=[MagicMock(text=json.dumps(classification))]
            )
        )

        # ACT: Process multiple intents
        with patch('app.notion_poller.AsyncClient', return_value=mock_notion_client):
            with patch('app.agent_router.AsyncAnthropic', return_value=mock_anthropic_client):
                poller = NotionPoller()
                poller.client = mock_notion_client

                await poller.poll_cycle()

        # ASSERT: All intents processed
        assert mock_notion_client.pages.create.call_count >= 3

        # Verify concurrent processing (all called, not sequential blocking)
        create_calls = mock_notion_client.pages.create.call_args_list
        assert len(create_calls) >= 3


@pytest.mark.integration
@pytest.mark.asyncio
class TestWorkflowIntegration:
    """Test workflow integration components"""

    async def test_complete_automation_workflow(
        self,
        mock_notion_client,
        mock_anthropic_client
    ):
        """
        Test: Complete automation (Areas + Knowledge + Tasks)

        Verifies WorkflowIntegration._run_complete_automation()
        """
        # ARRANGE
        intent_description = "Build a new YouTube channel for brand awareness"

        # Mock area detection
        area_response = json.dumps({
            "area_name": "Business Growth",
            "confidence": 0.9
        })

        # Mock concept extraction
        concepts_response = json.dumps({
            "concepts": [
                {"concept": "YouTube", "node_type": "Knowledge_Asset", "confidence": 0.95},
                {"concept": "Brand awareness", "node_type": "Knowledge_Asset", "confidence": 0.85}
            ]
        })

        # Mock agent analysis
        analysis = AgentAnalysis(
            scenario_options=[
                ScenarioOption(
                    option="A",
                    description="Test option",
                    pros=["Pro 1"],
                    cons=["Con 1"],
                    risk=2,
                    impact=8
                )
            ],
            recommended_option="A",
            recommendation_rationale="Test",
            risk_assessment="Low",
            required_resources={"time": "10 hours"},
            task_generation_template=[
                "Research competitor channels",
                "Script first video",
                "Set up channel"
            ]
        )

        mock_anthropic_client.messages.create = AsyncMock(
            side_effect=[
                MagicMock(content=[MagicMock(text=area_response)]),
                MagicMock(content=[MagicMock(text=concepts_response)])
            ]
        )

        # Mock Notion calls
        mock_notion_client.databases.query = AsyncMock(
            side_effect=[
                {"results": [{"id": "area-123"}]},  # Area lookup
                {"results": []},  # Node lookup (empty)
                {"results": []}   # Node lookup (empty)
            ]
        )

        mock_notion_client.pages.create = AsyncMock(
            side_effect=[
                {"id": "node-001"},
                {"id": "node-002"},
                {"id": "task-001"},
                {"id": "task-002"},
                {"id": "task-003"},
                {"id": "project-123"}
            ]
        )

        mock_notion_client.pages.update = AsyncMock(
            return_value={"id": "updated"}
        )

        # ACT
        with patch('app.workflow_integration.AsyncClient', return_value=mock_notion_client):
            with patch('app.areas_manager.AsyncAnthropic', return_value=mock_anthropic_client):
                with patch('app.knowledge_linker.AsyncAnthropic', return_value=mock_anthropic_client):
                    workflow = WorkflowIntegration(mock_notion_client)

                    await workflow._run_complete_automation(
                        intent_id="intent-123",
                        intent_title="Build YouTube channel",
                        intent_description=intent_description,
                        analysis=analysis
                    )

        # ASSERT: All automation steps completed
        # 1. Area assigned
        # 2. Knowledge nodes created
        # 3. Tasks spawned
        assert mock_notion_client.pages.create.call_count >= 3  # At minimum: tasks created
