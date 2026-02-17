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
                    "or": [
                        {
                            "property": "Status",
                            "select": {"equals": "Unprocessed"}
                        },
                        {
                            "property": "Status",
                            "select": {"is_empty": True}
                        }
                    ]
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
                # Create Task directly - operational intents bypass strategic workflow
                try:
                    logger.info(f"Creating operational task for intent {intent_id[:8]}")

                    # Extract task title from classification or use content summary
                    task_title = classification.get("title", content[:100])

                    # Create task in DB_Tasks
                    task_response = await self.client.pages.create(
                        parent={"database_id": settings.notion_db_tasks},
                        properties={
                            "Name": {
                                "title": [{"text": {"content": task_title}}]
                            },
                            "Status": {
                                "select": {"name": "Not started"}
                            },
                            "Related Intents": {
                                "relation": [{"id": intent_id}]
                            }
                        }
                    )

                    task_id = task_response["id"]
                    logger.success(f"Created operational task {task_id[:8]}: '{task_title[:50]}...'")

                    # Add context to the task page
                    await self._add_operational_task_context(
                        task_id=task_id,
                        inbox_id=intent_id,
                        classification=classification,
                        original_content=content
                    )

                    # Log to Execution Log for audit trail
                    await self._log_task_creation(
                        task_id=task_id,
                        inbox_id=intent_id,
                        task_title=task_title
                    )

                    # Update System Inbox status
                    await self.update_status(intent_id, "Triaged_to_Task")
                    logger.info(f"Operational intent {intent_id[:8]} triaged to task successfully")

                except Exception as e:
                    logger.error(f"Error creating operational task for {intent_id[:8]}: {e}")
                    # Don't update status if task creation failed
                    raise

            else:  # reference
                # Create Knowledge Node for reference content
                try:
                    logger.info(f"Creating knowledge node for reference content: {intent_id[:8]}")

                    # Extract concepts from content using AI
                    from app.knowledge_linker import KnowledgeLinker
                    knowledge_linker = KnowledgeLinker()

                    concepts = await knowledge_linker.extract_concepts(content, max_concepts=3)

                    node_ids = []
                    if concepts:
                        logger.info(f"Extracted {len(concepts)} concepts: {[c.concept for c in concepts]}")

                        # Create or find nodes for each concept
                        for concept in concepts:
                            node_id = await knowledge_linker.find_or_create_node(concept)
                            if node_id:
                                node_ids.append(node_id)

                        # Link the System Inbox to the created nodes
                        if node_ids:
                            await self.client.pages.update(
                                page_id=intent_id,
                                properties={
                                    "Related_Nodes": {
                                        "relation": [{"id": node_id} for node_id in node_ids]
                                    }
                                }
                            )
                            logger.success(f"Created/linked {len(node_ids)} knowledge nodes")

                        # Auto-tag with categories based on node types
                        categories = list(set([c.node_type for c in concepts]))
                        category_str = ", ".join(categories)

                        # Update System Inbox with auto-generated tags
                        await self.client.pages.update(
                            page_id=intent_id,
                            properties={
                                "Auto_Tags": {
                                    "rich_text": [{"text": {"content": category_str[:2000]}}]
                                }
                            }
                        )
                        logger.info(f"Auto-tagged with categories: {category_str}")

                    else:
                        logger.warning("No concepts extracted from reference content")

                    # Log to Execution Log for audit trail
                    await self._log_knowledge_node_creation(
                        inbox_id=intent_id,
                        node_count=len(node_ids),
                        concepts=[c.concept for c in concepts] if concepts else []
                    )

                    # Update System Inbox status
                    await self.update_status(intent_id, "Triaged_to_Node")
                    logger.info(f"Reference intent {intent_id[:8]} triaged to knowledge nodes successfully")

                except Exception as node_error:
                    logger.error(f"Error creating knowledge node for {intent_id[:8]}: {node_error}")
                    # Still update status to mark as processed, even if node creation partially failed
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

    async def _add_operational_task_context(
        self,
        task_id: str,
        inbox_id: str,
        classification: Dict[str, Any],
        original_content: str
    ) -> None:
        """Add context and metadata to operational task page"""
        try:
            logger.debug(f"Adding context to operational task {task_id[:8]}")

            # Create source URL for System Inbox
            inbox_url = f"https://notion.so/{inbox_id.replace('-', '')}"

            blocks = [
                {
                    "type": "callout",
                    "callout": {
                        "icon": {"emoji": "🤖"},
                        "color": "blue_background",
                        "rich_text": [{
                            "type": "text",
                            "text": {
                                "content": f"""Auto-Generated Operational Task

This task was automatically created from System Inbox.

Source: {inbox_url}
Classification: {classification.get('type', 'operational')}
Priority: {classification.get('impact', 5)}/10"""
                            }
                        }]
                    }
                },
                {
                    "type": "divider",
                    "divider": {}
                },
                {
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": "📋 Original Request"}
                        }]
                    }
                },
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": original_content[:1900]}  # Notion limit
                        }]
                    }
                }
            ]

            # Add rationale if available
            if classification.get("rationale"):
                blocks.extend([
                    {
                        "type": "divider",
                        "divider": {}
                    },
                    {
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": "🧠 AI Classification"}
                            }]
                        }
                    },
                    {
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": classification["rationale"][:1900]}
                            }]
                        }
                    }
                ])

            await self.client.blocks.children.append(
                block_id=task_id,
                children=blocks
            )

            logger.debug(f"Context added to task {task_id[:8]}")

        except Exception as e:
            logger.warning(f"Could not add context to task {task_id[:8]}: {e}")
            # Don't raise - task creation still succeeded

    async def _log_task_creation(
        self,
        task_id: str,
        inbox_id: str,
        task_title: str
    ) -> None:
        """Log operational task creation to Execution Log"""
        try:
            logger.debug(f"Logging task creation to Execution Log")

            # Get next Log ID
            log_id = await self._get_next_log_id()

            # Create task URL for reference
            task_url = f"https://notion.so/{task_id.replace('-', '')}"

            await self.client.pages.create(
                parent={"database_id": settings.notion_db_execution_log},
                properties={
                    "Log_Entry_Title": {
                        "title": [{"text": {"content": "Operational Task Created"}}]
                    },
                    "Log_ID": {
                        "number": log_id
                    },
                    "Action_Taken": {
                        "rich_text": [{
                            "text": {
                                "content": f"Auto-created task from System Inbox: '{task_title[:100]}...'\n\nTask: {task_url}\nSource: Operational intent classification"
                            }
                        }]
                    },
                    "Decision_Date": {
                        "date": {"start": datetime.now().date().isoformat()}
                    }
                }
            )

            logger.debug(f"Task creation logged with Log_ID {log_id}")

        except Exception as e:
            logger.warning(f"Could not log task creation: {e}")
            # Don't raise - task creation still succeeded

    async def _get_next_log_id(self) -> int:
        """Get next sequential Log ID from Execution Log"""
        try:
            response = await self.client.databases.query(
                database_id=settings.notion_db_execution_log,
                page_size=100
            )

            max_id = 0
            for page in response.get("results", []):
                log_id = page.get("properties", {}).get("Log_ID", {}).get("number")
                if log_id and log_id > max_id:
                    max_id = log_id

            return max_id + 1
        except Exception as e:
            logger.warning(f"Error getting next log ID, defaulting to 1: {e}")
            return 1

    async def _log_knowledge_node_creation(
        self,
        inbox_id: str,
        node_count: int,
        concepts: List[str]
    ) -> None:
        """Log knowledge node creation to Execution Log"""
        try:
            logger.debug(f"Logging knowledge node creation to Execution Log")

            # Get next Log ID
            log_id = await self._get_next_log_id()

            # Create inbox URL for reference
            inbox_url = f"https://notion.so/{inbox_id.replace('-', '')}"

            # Format concepts list
            concepts_str = ", ".join(concepts) if concepts else "No concepts extracted"

            await self.client.pages.create(
                parent={"database_id": settings.notion_db_execution_log},
                properties={
                    "Log_Entry_Title": {
                        "title": [{"text": {"content": "Knowledge Nodes Created"}}]
                    },
                    "Log_ID": {
                        "number": log_id
                    },
                    "Action_Taken": {
                        "rich_text": [{
                            "text": {
                                "content": f"Created {node_count} knowledge node(s) from reference content.\n\nConcepts: {concepts_str[:1800]}\n\nSource: {inbox_url}\nClassification: Reference intent"
                            }
                        }]
                    },
                    "Decision_Date": {
                        "date": {"start": datetime.now().date().isoformat()}
                    }
                }
            )

            logger.debug(f"Knowledge node creation logged with Log_ID {log_id}")

        except Exception as e:
            logger.warning(f"Could not log knowledge node creation: {e}")
            # Don't raise - node creation still succeeded

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
