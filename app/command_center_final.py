"""
Final Command Center - One-time setup with all database views
After setup, everything is live and no rebuilding needed
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
from loguru import logger
from notion_client import AsyncClient

from config.settings import settings


class FinalCommandCenter:
    """One-time setup for a truly live Command Center"""

    def __init__(self, notion_client: AsyncClient):
        self.client = notion_client
        self.command_center_id = "2eac8854-2aed-80cd-8f2a-e96b2e5d52c8"

    async def initial_setup(self) -> str:
        """
        One-time setup: Creates the complete structure with instructions
        to add linked database views. After this, you never rebuild -
        everything updates live!
        """

        try:
            logger.info("Setting up Command Center (one-time)...")

            # Clear page
            await self._clear_page()

            # Create structure
            blocks = []

            # Status Banner
            blocks.append(self._block_callout(
                "🎯",
                "blue_background",
                "⚡ EXECUTIVE MIND MATRIX\n\n🟢 System Operational • Click 'Update Metrics' below to refresh"
            ))

            blocks.append(self._block_divider())

            # Instructions
            blocks.append(self._block_heading2("📋 One-Time Setup Instructions"))
            blocks.append(self._block_paragraph(
                "Add linked database views below each section (just once!). After setup, everything updates live in real-time."
            ))

            blocks.append(self._block_toggle(
                "🔧 How to Add Linked Database Views",
                [
                    self._block_paragraph("1. Position your cursor under a section heading"),
                    self._block_paragraph("2. Type /linked and press Enter"),
                    self._block_paragraph("3. Select 'Linked view of database'"),
                    self._block_paragraph("4. Search for and select the database name shown"),
                    self._block_paragraph("5. Choose your preferred view (Table, Board, Gallery, etc.)"),
                    self._block_paragraph("6. Repeat for each section below")
                ]
            ))

            blocks.append(self._block_divider())

            # Section 1: System Inbox (Create New Items)
            blocks.append(self._block_heading2("➕ Create New Items"))
            blocks.append(self._block_paragraph(
                "👇 Add linked view: DB_System_Inbox (Table view recommended)"
            ))
            blocks.append(self._block_callout(
                "📝",
                "purple_background",
                "This is where you CREATE new items. They'll auto-triage within 2 minutes."
            ))

            blocks.append(self._block_divider())

            # Section 2: Active Strategic Decisions
            blocks.append(self._block_heading2("🎯 Active Strategic Decisions"))
            blocks.append(self._block_paragraph(
                "👇 Add linked view: DB_Executive_Intents"
            ))
            blocks.append(self._block_paragraph(
                "Filter: Status = 'Ready' | Sort: Created Time (Descending)"
            ))

            blocks.append(self._block_divider())

            # Section 3: Action Pipes
            blocks.append(self._block_heading2("⚡ Action Pipes"))
            blocks.append(self._block_paragraph(
                "👇 Add linked view: DB_Action_Pipes"
            ))
            blocks.append(self._block_paragraph(
                "Shows all action items and their approval status"
            ))

            blocks.append(self._block_divider())

            # Section 4: AI Agents
            blocks.append(self._block_heading2("🤖 AI Agents"))
            blocks.append(self._block_paragraph(
                "👇 Add linked view: DB_Agent_Registry"
            ))
            blocks.append(self._block_paragraph(
                "Your adversarial agent personas: Entrepreneur, Quant, Auditor"
            ))

            blocks.append(self._block_divider())

            # Section 5: Training Data
            blocks.append(self._block_heading2("📚 Training Data"))
            blocks.append(self._block_paragraph(
                "👇 Add linked view: DB_Training_Data"
            ))
            blocks.append(self._block_paragraph(
                "Learning from your edits to AI suggestions"
            ))

            blocks.append(self._block_divider())

            # Section 6: Execution Log
            blocks.append(self._block_heading2("📜 Execution History"))
            blocks.append(self._block_paragraph(
                "👇 Add linked view: DB_Execution_Log"
            ))
            blocks.append(self._block_paragraph(
                "Track all system actions and decisions"
            ))

            blocks.append(self._block_divider())

            # System Metrics (will be updated via API)
            blocks.append(self._block_heading2("📊 System Metrics"))
            blocks.append(self._block_callout(
                "📊",
                "gray_background",
                "Calculating metrics...\n\nRun: curl -X POST http://localhost:8000/command-center/update-metrics"
            ))

            blocks.append(self._block_divider())

            # Quick Commands
            blocks.append(self._block_heading2("⚡ Quick Commands"))
            blocks.append({
                "type": "code",
                "code": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": """# Update metrics banner (lightweight, fast)
curl -X POST http://localhost:8000/command-center/update-metrics

# Trigger immediate triage
curl -X POST http://localhost:8000/trigger-poll

# Run dialectic analysis
curl -X POST http://localhost:8000/dialectic/{INTENT_ID}"""
                        }
                    }],
                    "language": "bash"
                }
            })

            # Add all blocks
            await self.client.blocks.children.append(
                block_id=self.command_center_id,
                children=blocks
            )

            logger.success("Command Center setup complete!")

            return "Setup complete! Now manually add the linked database views as instructed."

        except Exception as e:
            logger.error(f"Error setting up Command Center: {e}")
            raise

    async def update_metrics_only(self) -> Dict[str, Any]:
        """
        Lightweight update - only refreshes the metrics callout.
        Everything else is live database views that update automatically.
        """

        try:
            logger.info("Updating metrics...")

            # Get metrics
            metrics = await self._get_metrics()

            # Find the metrics block
            blocks_response = await self.client.blocks.children.list(
                block_id=self.command_center_id,
                page_size=100
            )

            # Find the "System Metrics" heading and the callout after it
            blocks = blocks_response.get("results", [])
            metrics_block_id = None

            for i, block in enumerate(blocks):
                if block["type"] == "heading_2":
                    heading_text = block.get("heading_2", {}).get("rich_text", [])
                    if heading_text and "System Metrics" in heading_text[0].get("text", {}).get("content", ""):
                        # The callout should be next
                        if i + 1 < len(blocks) and blocks[i + 1]["type"] == "callout":
                            metrics_block_id = blocks[i + 1]["id"]
                            break

            if metrics_block_id:
                # Update the callout
                await self.client.blocks.update(
                    block_id=metrics_block_id,
                    callout={
                        "rich_text": [{
                            "type": "text",
                            "text": {
                                "content": f"""📊 Live System Metrics

📥 Inbox: {metrics['pending_inbox']} pending
🎯 Intents: {metrics['total_intents']} total ({metrics['ready_intents']} ready)
⚡ Actions: {metrics['total_actions']} total

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: 🟢 All Systems Operational"""
                            }
                        }],
                        "icon": {"emoji": "📊"},
                        "color": "gray_background"
                    }
                )

                logger.success("Metrics updated!")
            else:
                logger.warning("Metrics block not found")

            return metrics

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            return {}

    async def _clear_page(self) -> None:
        """Clear all blocks"""
        try:
            blocks_response = await self.client.blocks.children.list(
                block_id=self.command_center_id
            )

            for block in blocks_response.get("results", []):
                try:
                    await self.client.blocks.delete(block_id=block["id"])
                except:
                    pass
        except:
            pass

    async def _get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            inbox = await self.client.databases.query(
                database_id=settings.notion_db_system_inbox,
                filter={"property": "Status", "select": {"equals": "Unprocessed"}}
            )

            intents_ready = await self.client.databases.query(
                database_id=settings.notion_db_executive_intents,
                filter={"property": "Status", "select": {"equals": "Ready"}}
            )

            intents_all = await self.client.databases.query(
                database_id=settings.notion_db_executive_intents
            )

            actions_all = await self.client.databases.query(
                database_id=settings.notion_db_action_pipes
            )

            return {
                "pending_inbox": len(inbox.get("results", [])),
                "ready_intents": len(intents_ready.get("results", [])),
                "total_intents": len(intents_all.get("results", [])),
                "total_actions": len(actions_all.get("results", []))
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {"pending_inbox": 0, "ready_intents": 0, "total_intents": 0, "total_actions": 0}

    def _block_heading2(self, text: str) -> Dict:
        return {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }

    def _block_paragraph(self, text: str) -> Dict:
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }

    def _block_callout(self, emoji: str, color: str, text: str) -> Dict:
        return {
            "type": "callout",
            "callout": {
                "icon": {"emoji": emoji},
                "color": color,
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }

    def _block_divider(self) -> Dict:
        return {
            "type": "divider",
            "divider": {}
        }

    def _block_toggle(self, summary: str, children: list) -> Dict:
        return {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": summary}}],
                "children": children
            }
        }
