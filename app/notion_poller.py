import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from notion_client import AsyncClient
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from app.models import NotionIntent, IntentStatus
from app.command_center import CommandCenterSync


class NotionPoller:
    """Async poller service for Notion databases - checks every 2 minutes"""

    def __init__(self):
        self.client = AsyncClient(auth=settings.notion_api_key)
        self.polling_interval = settings.polling_interval_seconds
        self.is_running = False
        self.command_center = CommandCenterSync(self.client)

    async def start(self):
        """Start the polling loop"""
        self.is_running = True
        logger.info(f"Starting Notion poller (interval: {self.polling_interval}s)")

        while self.is_running:
            try:
                await self.poll_cycle()
            except Exception as e:
                logger.error(f"Polling cycle error: {e}")

            await asyncio.sleep(self.polling_interval)

    def stop(self):
        """Stop the polling loop"""
        self.is_running = False
        logger.info("Stopping Notion poller")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def poll_cycle(self):
        """Single polling cycle - fetch and process pending intents"""
        logger.debug("Starting poll cycle")

        # Fetch pending intents from System Inbox
        pending_intents = await self.fetch_pending_intents()

        if not pending_intents:
            logger.debug("No pending intents found")
            return

        logger.info(f"Found {len(pending_intents)} pending intents")

        # Process intents concurrently
        tasks = [self.process_intent(intent) for intent in pending_intents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        successful = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Processed {successful}/{len(pending_intents)} intents successfully")

    async def fetch_pending_intents(self) -> List[Dict[str, Any]]:
        """Fetch all intents with Status == 'Pending' from System Inbox"""
        try:
            response = await self.client.databases.query(
                database_id=settings.notion_db_system_inbox,
                filter={
                    "property": "Status",
                    "select": {
                        "equals": "Unprocessed"
                    }
                },
                sorts=[
                    {
                        "property": "Received_Date",
                        "direction": "ascending"
                    }
                ]
            )

            return response.get("results", [])

        except Exception as e:
            logger.error(f"Error fetching pending intents: {e}")
            return []

    async def process_intent(self, intent_page: Dict[str, Any]) -> bool:
        """Process a single intent: classify, route, update status"""
        intent_id = intent_page["id"]

        try:
            # Update status to Processing
            await self.update_status(intent_id, "Processing")
            logger.info(f"Processing intent {intent_id[:8]}...")

            # Extract intent data
            properties = intent_page.get("properties", {})
            content = self.extract_text_property(properties.get("Content", {}))
            source = self.extract_select_property(properties.get("Source", {}))

            # Import here to avoid circular dependency
            from app.agent_router import AgentRouter
            router = AgentRouter()

            # Classify and route the intent
            classification = await router.classify_intent(content)

            # Create appropriate database entry based on classification
            if classification["type"] == "strategic":
                # Use workflow integration for complete, cohesive processing
                from app.workflow_integration import WorkflowIntegration
                workflow = WorkflowIntegration(self.client)

                created_intent_id = await workflow.process_intent_complete_workflow(
                    inbox_id=intent_id,
                    classification=classification
                )

                await self.update_status(intent_id, "Triaged_to_Intent")

            elif classification["type"] == "operational":
                # Create Task directly
                # TODO: Implement task creation
                await self.update_status(intent_id, "Triaged_to_Task")

            else:  # reference
                # Create Knowledge Node
                # TODO: Implement node creation
                await self.update_status(intent_id, "Triaged_to_Node")

            logger.info(f"Intent {intent_id[:8]} processed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing intent {intent_id[:8]}: {e}")
            # Reset status on error
            await self.update_status(intent_id, "Unprocessed")
            return False

    async def update_status(self, page_id: str, status: str):
        """Update the status property of a Notion page"""
        try:
            await self.client.pages.update(
                page_id=page_id,
                properties={
                    "Status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error updating status for {page_id[:8]}: {e}")
            raise

    async def create_executive_intent(
        self,
        title: str,
        description: str,
        agent: str,
        risk: str,
        impact: int,
        source_inbox_id: str
    ) -> str:
        """Create a new Executive Intent in Notion"""
        try:
            # First, get agent ID by name
            agent_id = await self.find_agent_by_name(agent)

            # Map impact to priority
            if impact >= 8:
                priority = "P0"
            elif impact >= 6:
                priority = "P1"
            else:
                priority = "P2"

            response = await self.client.pages.create(
                parent={"database_id": settings.notion_db_executive_intents},
                properties={
                    "Name": {
                        "title": [{"text": {"content": title}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": description}}]
                    },
                    "Status": {
                        "select": {"name": "Ready"}
                    },
                    "Risk_Level": {
                        "select": {"name": risk}
                    },
                    "Projected_Impact": {
                        "number": impact
                    },
                    "Priority": {
                        "select": {"name": priority}
                    },
                    "Agent_Persona": {
                        "relation": [{"id": agent_id}] if agent_id else []
                    },
                    "Source": {
                        "relation": [{"id": source_inbox_id}]
                    }
                }
            )

            created_id = response["id"]
            logger.info(f"Created Executive Intent: {created_id[:8]}")
            return created_id

        except Exception as e:
            logger.error(f"Error creating Executive Intent: {e}")
            raise

    async def find_agent_by_name(self, agent_name: str) -> Optional[str]:
        """Find agent ID by name from Agent Registry"""
        try:
            response = await self.client.databases.query(
                database_id=settings.notion_db_agent_registry,
                filter={
                    "property": "Agent_Name",
                    "title": {
                        "equals": agent_name
                    }
                }
            )

            results = response.get("results", [])
            if results:
                return results[0]["id"]
            return None

        except Exception as e:
            logger.error(f"Error finding agent {agent_name}: {e}")
            return None

    @staticmethod
    def extract_text_property(prop: Dict[str, Any]) -> str:
        """Extract text from Notion rich_text or title property"""
        if "rich_text" in prop:
            texts = prop["rich_text"]
        elif "title" in prop:
            texts = prop["title"]
        else:
            return ""

        return "".join([t.get("plain_text", "") for t in texts])

    @staticmethod
    def extract_select_property(prop: Dict[str, Any]) -> Optional[str]:
        """Extract value from Notion select property"""
        select = prop.get("select")
        return select.get("name") if select else None
