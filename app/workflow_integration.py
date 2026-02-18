"""
Workflow Integration - Makes all databases work together cohesively

This creates the connective tissue between all databases so they form
a complete, guided workflow instead of isolated views.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
from notion_client import AsyncClient

from config.settings import settings
from app.areas_manager import AreasManager
from app.knowledge_linker import KnowledgeLinker
from app.task_spawner import TaskSpawner


class WorkflowIntegration:
    """Manages the complete workflow integration across all databases"""

    def __init__(self, notion_client: AsyncClient):
        self.client = notion_client

    async def process_intent_complete_workflow(
        self,
        inbox_id: str,
        classification: Dict[str, Any]
    ) -> str:
        """
        Complete workflow when processing an intent:
        1. Create Executive Intent with rich context
        2. Link back to System Inbox
        3. Add automated insights
        4. Set up for dialectic analysis
        """

        try:
            # Get original inbox content
            inbox_page = await self.client.pages.retrieve(page_id=inbox_id)
            inbox_props = inbox_page.get("properties", {})

            title_prop = inbox_props.get("Input_Title", {}).get("title", [])
            original_title = title_prop[0]["text"]["content"] if title_prop else "Untitled"

            content_prop = inbox_props.get("Content", {}).get("rich_text", [])
            content = content_prop[0]["text"]["content"] if content_prop else ""

            # Get next Intent ID
            intent_id_number = await self._get_next_intent_id()

            # Calculate due date based on priority
            due_date = self._calculate_due_date(classification["impact"])

            # Generate success criteria
            success_criteria = self._generate_success_criteria(classification, content)

            # Create Executive Intent with ALL fields populated
            intent_response = await self.client.pages.create(
                parent={"database_id": settings.notion_db_executive_intents},
                properties={
                    "Name": {
                        "title": [{"text": {"content": classification["title"]}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": content}}]
                    },
                    "Status": {
                        "select": {"name": "Ready"}
                    },
                    "Risk_Level": {
                        "select": {"name": classification["risk"]}
                    },
                    "Projected_Impact": {
                        "number": classification["impact"]
                    },
                    "Priority": {
                        "select": {"name": self._calculate_priority(classification["impact"])}
                    },
                    "Intent ID": {
                        "number": intent_id_number
                    },
                    "Created_Date": {
                        "date": {"start": datetime.now().date().isoformat()}
                    },
                    "Due_Date": {
                        "date": {"start": due_date}
                    },
                    "Success_Criteria": {
                        "rich_text": [{"text": {"content": success_criteria}}]
                    },
                    "Source": {
                        "relation": [{"id": inbox_id}]
                    }
                }
            )

            intent_id = intent_response["id"]

            # Write back to System Inbox: link intent + set triage destination
            await self.client.pages.update(
                page_id=inbox_id,
                properties={
                    "Routed_to_Intent": {
                        "relation": [{"id": intent_id}]
                    },
                    "Triage_Destination": {
                        "select": {"name": "Strategic (Intent)"}
                    }
                }
            )

            # Add rich context blocks to the Intent page
            await self._add_intent_context(intent_id, classification, original_title)

            # RUN AGENT ANALYSIS IMMEDIATELY - This is the agentic part!
            analysis = await self._run_initial_agent_analysis(
                intent_id,
                classification["title"],
                content,
                classification.get("agent", "The Entrepreneur"),
                classification.get("impact", 5)
            )

            # RUN COMPLETE AUTOMATION - Areas, Knowledge, Tasks
            await self._run_complete_automation(
                intent_id,
                classification["title"],
                content,
                analysis
            )

            # Add workflow guidance to the Intent page
            await self._add_workflow_guidance(intent_id)

            # Log to Execution Log
            await self._log_execution(
                action="Intent Created",
                intent_id=intent_id,
                details=f"Created from inbox: {original_title}. Classified as {classification.get('type')} with {classification.get('risk')} risk."
            )

            logger.info(f"Created complete workflow for intent {intent_id[:8]}")

            return intent_id

        except Exception as e:
            logger.error(f"Error in complete workflow: {e}")
            raise

    async def _add_intent_context(
        self,
        intent_id: str,
        classification: Dict[str, Any],
        original_title: str
    ) -> None:
        """Add rich context to the Intent page"""

        risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(
            classification.get("risk", "Medium"), "⚪"
        )

        agent_emoji = {
            "The Entrepreneur": "🚀",
            "The Quant": "📊",
            "The Auditor": "🔍"
        }.get(classification.get("agent", ""), "🤖")

        blocks = [
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "🧠 AI Classification Results"}}]
                }
            },
            {
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "🎯"},
                    "color": "blue_background",
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"""Original Request: {original_title}

{risk_emoji} Risk Assessment: {classification.get('risk', 'Medium')}
⚡ Impact Score: {classification.get('impact', 5)}/10
{agent_emoji} Recommended Agent: {classification.get('agent', 'Unassigned')}

AI Rationale:
{classification.get('rationale', 'No rationale provided')}"""
                        }
                    }]
                }
            },
            {
                "type": "divider",
                "divider": {}
            }
        ]

        await self.client.blocks.children.append(
            block_id=intent_id,
            children=blocks
        )

    async def _run_initial_agent_analysis(
        self,
        intent_id: str,
        intent_title: str,
        intent_description: str,
        agent_name: str,
        projected_impact: int
    ):
        """
        Run the assigned agent's analysis immediately upon intent creation.
        This is what makes the system truly agentic - agents give you advice!
        Returns AgentAnalysis object for use by complete automation.
        """

        try:
            from app.agent_router import AgentRouter, AgentPersona

            logger.info(f"Running {agent_name} analysis for intent {intent_id[:8]}")

            # Map agent name to persona and agent ID
            agent_map = {
                "The Entrepreneur": (AgentPersona.ENTREPRENEUR, "4c4d39c3-1ff2-429f-ba14-b1be67c56eb3"),
                "The Quant": (AgentPersona.QUANT, "48c6110f-e4a0-4f70-92f6-f97b1f0e8e76"),
                "The Auditor": (AgentPersona.AUDITOR, "f30957ac-f132-4bef-a584-8d8f36a417c0")
            }

            agent_persona, agent_id = agent_map.get(agent_name, (AgentPersona.ENTREPRENEUR, "4c4d39c3-1ff2-429f-ba14-b1be67c56eb3"))

            # Link agent to intent
            await self.client.pages.update(
                page_id=intent_id,
                properties={
                    "Agent_Persona": {
                        "relation": [{"id": agent_id}]
                    }
                }
            )

            # Run agent analysis
            router = AgentRouter()
            analysis = await router.analyze_with_agent(
                agent=agent_persona,
                intent_title=intent_title,
                intent_description=intent_description,
                success_criteria="",
                projected_impact=projected_impact
            )

            # Add agent's recommendations to the page
            agent_emoji = {
                "The Entrepreneur": "🚀",
                "The Quant": "📊",
                "The Auditor": "🔍"
            }.get(agent_name, "🤖")

            blocks = [
                {
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": f"{agent_emoji} {agent_name}'s Analysis"}
                        }]
                    }
                },
                {
                    "type": "callout",
                    "callout": {
                        "icon": {"emoji": "💡"},
                        "color": "green_background",
                        "rich_text": [{
                            "type": "text",
                            "text": {
                                "content": f"""RECOMMENDED OPTION: {analysis.recommended_option}

{analysis.recommendation_rationale}"""
                            }
                        }]
                    }
                },
                {
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": "📊 Scenario Options"}
                        }]
                    }
                }
            ]

            # Add each option
            for i, option in enumerate(analysis.scenario_options, 1):
                blocks.append({
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": f"Option {option.option}: {option.description[:60]}"}
                        }],
                        "children": [
                            {
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": f"📝 {option.description}"}
                                    }]
                                }
                            },
                            {
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": f"✅ Pros: {', '.join(option.pros)}"}
                                    }]
                                }
                            },
                            {
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": f"⚠️ Cons: {', '.join(option.cons)}"}
                                    }]
                                }
                            },
                            {
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": f"Risk: {option.risk}/5 | Impact: {option.impact}/10"}
                                    }]
                                }
                            }
                        ]
                    }
                })

            blocks.append({
                "type": "divider",
                "divider": {}
            })

            blocks.append({
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "💬"},
                    "color": "gray_background",
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"""Want more perspectives? Run dialectic analysis to see what other agents think:

curl -X POST http://localhost:8000/dialectic/{intent_id}"""
                        }
                    }]
                }
            })

            blocks.append({
                "type": "divider",
                "divider": {}
            })

            # Append agent analysis to intent page
            await self.client.blocks.children.append(
                block_id=intent_id,
                children=blocks
            )

            logger.success(f"{agent_name} analysis added to intent {intent_id[:8]}")

            return analysis

        except Exception as e:
            logger.error(f"Error running initial agent analysis: {e}")
            # Don't fail the whole workflow if agent analysis fails
            return None

    async def _run_complete_automation(
        self,
        intent_id: str,
        intent_title: str,
        intent_description: str,
        analysis
    ) -> None:
        """
        Run complete automation: areas, knowledge linking, and task spawning.
        This is called after initial agent analysis completes.
        """
        try:
            logger.info(f"Running complete automation for intent {intent_id[:8]}")

            # Step 1: Detect and assign Area
            areas_mgr = AreasManager()
            area_assignment = await areas_mgr.detect_area(intent_description)
            area_id = await areas_mgr.get_area_id(area_assignment.area_name)

            if area_id:
                await areas_mgr.assign_area_to_intent(intent_id, area_id)
                logger.success(f"Assigned area '{area_assignment.area_name}' to intent")
            else:
                logger.warning(f"Area '{area_assignment.area_name}' not found in Notion, skipping assignment")

            # Step 2: Extract and link knowledge nodes
            knowledge_linker = KnowledgeLinker()
            node_ids = await knowledge_linker.process_intent_knowledge(intent_id, intent_description)
            logger.success(f"Linked {len(node_ids)} knowledge nodes to intent")

            # Step 3: Spawn tasks and project (only if analysis is available)
            if analysis:
                task_spawner = TaskSpawner()
                task_result = await task_spawner.process_intent_tasks(intent_id, analysis, area_id)

                logger.success(
                    f"Complete automation finished: {task_result.tasks_created} tasks, "
                    f"project_created={task_result.project_created}"
                )
            else:
                logger.warning("No agent analysis available, skipping task spawning")

        except Exception as e:
            logger.error(f"Error in complete automation workflow: {e}")
            # Don't raise - graceful degradation

    async def _add_workflow_guidance(self, intent_id: str) -> None:
        """Add workflow guidance to Intent page"""

        blocks = [
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📋 Next Steps"}}]
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Review AI classification above"}
                    }],
                    "checked": False
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Run dialectic analysis for multi-agent perspectives"}
                    }],
                    "checked": False
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Review synthesis and make decision"}
                    }],
                    "checked": False
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Create action items if needed"}
                    }],
                    "checked": False
                }
            },
            {
                "type": "divider",
                "divider": {}
            },
            {
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "⚡ Quick Actions"}}]
                }
            },
            {
                "type": "code",
                "code": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"""# Run dialectic analysis on this intent
curl -X POST http://localhost:8000/dialectic/{intent_id}

# Create action pipe from this intent
curl -X POST http://localhost:8000/intent/{intent_id}/create-action"""
                        }
                    }],
                    "language": "bash"
                }
            }
        ]

        await self.client.blocks.children.append(
            block_id=intent_id,
            children=blocks
        )

    async def run_dialectic_and_link(
        self,
        intent_id: str,
        dialectic_result: Dict[str, Any]
    ) -> None:
        """
        Run dialectic and update the Intent with results.
        Creates a complete narrative in the Intent page.
        """

        try:
            # Add dialectic results to Intent page
            blocks = [
                {
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "🤝 Multi-Agent Dialectic Analysis"}}]
                    }
                },
                {
                    "type": "callout",
                    "callout": {
                        "icon": {"emoji": "🚀"},
                        "color": "green_background",
                        "rich_text": [{
                            "type": "text",
                            "text": {
                                "content": f"""Growth Perspective (The Entrepreneur)
Recommendation: Option {dialectic_result.get('growth_recommendation', 'N/A')}

Focus: Revenue potential, scalability, market opportunity"""
                            }
                        }]
                    }
                },
                {
                    "type": "callout",
                    "callout": {
                        "icon": {"emoji": "🔍"},
                        "color": "red_background",
                        "rich_text": [{
                            "type": "text",
                            "text": {
                                "content": f"""Risk Perspective (The Auditor)
Recommendation: Option {dialectic_result.get('risk_recommendation', 'N/A')}

Focus: Compliance, governance, long-term sustainability"""
                            }
                        }]
                    }
                },
                {
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "💡 Synthesis"}}]
                    }
                },
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": dialectic_result.get('synthesis', '')}
                        }]
                    }
                },
                {
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "🎯 Recommended Path"}}]
                    }
                },
                {
                    "type": "callout",
                    "callout": {
                        "icon": {"emoji": "✅"},
                        "color": "blue_background",
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": dialectic_result.get('recommended_path', '')}
                        }]
                    }
                }
            ]

            # Add conflict points if any
            conflicts = dialectic_result.get('conflict_points', [])
            if conflicts:
                blocks.append({
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "⚔️ Key Conflicts"}}]
                    }
                })

                for conflict in conflicts:
                    blocks.append({
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": conflict}
                            }]
                        }
                    })

            blocks.append({
                "type": "divider",
                "divider": {}
            })

            await self.client.blocks.children.append(
                block_id=intent_id,
                children=blocks
            )

            # Calculate conflict level based on agent agreement
            growth_rec = dialectic_result.get("growth_recommendation", "")
            risk_rec = dialectic_result.get("risk_recommendation", "")
            conflict_count = len(dialectic_result.get("conflict_points", []))

            if growth_rec == risk_rec and conflict_count == 0:
                conflict_level = "None - Full Consensus"
            elif growth_rec == risk_rec and conflict_count <= 2:
                conflict_level = "Low - Minor Disagreement"
            elif growth_rec != risk_rec and conflict_count <= 3:
                conflict_level = "Medium - Split Opinion"
            else:
                conflict_level = "High - Major Conflict"

            # Update Intent status and decision tracking
            await self.client.pages.update(
                page_id=intent_id,
                properties={
                    "Status": {
                        "select": {"name": "Analyzed"}
                    },
                    "Decision_Made": {
                        "rich_text": [{"text": {"content": dialectic_result.get("recommended_path", "")[:2000]}}]
                    },
                    "Conflict_Level": {
                        "select": {"name": conflict_level}
                    }
                }
            )

            # Log execution
            await self._log_execution(
                action="Dialectic Analysis Completed",
                intent_id=intent_id,
                details=f"Growth: Option {dialectic_result.get('growth_recommendation')}. Risk: Option {dialectic_result.get('risk_recommendation')}. Synthesis complete."
            )

            logger.info(f"Added dialectic results to intent {intent_id[:8]}")

        except Exception as e:
            logger.error(f"Error adding dialectic results: {e}")

    async def create_action_from_intent(
        self,
        intent_id: str,
        action_title: str,
        action_description: str
    ) -> str:
        """
        Create an Action Pipe from an Intent with proper linking
        """

        try:
            # Fetch intent to get Agent_Persona relation
            intent_page = await self.client.pages.retrieve(page_id=intent_id)
            properties = intent_page.get("properties", {})
            agent_relation = properties.get("Agent_Persona", {}).get("relation", [])
            agent_id = agent_relation[0]["id"] if agent_relation else None

            # Create Action Pipe
            action_response = await self.client.pages.create(
                parent={"database_id": settings.notion_db_action_pipes},
                properties={
                    "Action_Title": {
                        "title": [{"text": {"content": action_title}}]
                    },
                    "Scenario_Options": {
                        "rich_text": [{"text": {"content": action_description}}]
                    },
                    "Approval_Status": {
                        "select": {"name": "Pending"}
                    },
                    "Intent": {
                        "relation": [{"id": intent_id}]
                    },
                    "Agent": {
                        "relation": [{"id": agent_id}] if agent_id else []
                    }
                }
            )

            action_id = action_response["id"]

            # Add context to Action page
            await self._add_action_context(action_id, intent_id)

            # Update Intent to link back to this action
            await self.update_intent_with_action_link(intent_id, action_id)

            # Log execution
            await self._log_execution(
                action="Action Created from Intent",
                intent_id=intent_id,
                details=f"Created action: {action_title}"
            )

            logger.info(f"Created action {action_id[:8]} from intent {intent_id[:8]}")

            return action_id

        except Exception as e:
            logger.error(f"Error creating action from intent: {e}")
            raise

    async def _add_action_context(self, action_id: str, intent_id: str) -> None:
        """Add context to Action page"""

        intent_url = f"https://notion.so/{intent_id.replace('-', '')}"

        blocks = [
            {
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "🔗"},
                    "color": "gray_background",
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"This action was created from a strategic intent.\n\nView source intent: {intent_url}"
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
                    "rich_text": [{"type": "text", "text": {"content": "📋 Execution Checklist"}}]
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Define specific tasks"}}],
                    "checked": False
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Assign resources"}}],
                    "checked": False
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Set timeline"}}],
                    "checked": False
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Execute"}}],
                    "checked": False
                }
            },
            {
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Document results"}}],
                    "checked": False
                }
            }
        ]

        await self.client.blocks.children.append(
            block_id=action_id,
            children=blocks
        )

    def _calculate_priority(self, impact: int) -> str:
        """Calculate priority from impact score"""
        if impact >= 8:
            return "P0"
        elif impact >= 6:
            return "P1"
        else:
            return "P2"

    async def _get_next_intent_id(self) -> int:
        """Get next sequential Intent ID"""
        try:
            # Get all intents and find max ID
            response = await self.client.databases.query(
                database_id=settings.notion_db_executive_intents,
                page_size=100
            )

            max_id = 0
            for page in response.get("results", []):
                intent_id = page.get("properties", {}).get("Intent ID", {}).get("number")
                if intent_id and intent_id > max_id:
                    max_id = intent_id

            return max_id + 1
        except:
            return 1

    def _calculate_due_date(self, impact: int) -> str:
        """Calculate due date based on impact/priority"""
        from datetime import timedelta

        if impact >= 8:  # P0 - urgent
            days = 7  # 1 week
        elif impact >= 6:  # P1 - important
            days = 14  # 2 weeks
        else:  # P2 - normal
            days = 30  # 1 month

        due_date = datetime.now().date() + timedelta(days=days)
        return due_date.isoformat()

    def _generate_success_criteria(self, classification: Dict[str, Any], content: str) -> str:
        """Generate success criteria based on intent content"""

        intent_type = classification.get("type", "strategic")
        impact = classification.get("impact", 5)

        if impact >= 8:
            criteria = f"""HIGH-IMPACT DECISION:
• Clear decision made with stakeholder buy-in
• Implementation plan created with milestones
• Resources allocated and timeline confirmed
• Risk mitigation strategies defined
• Success metrics established"""
        elif impact >= 6:
            criteria = f"""MEDIUM-IMPACT DECISION:
• Decision made with rationale documented
• Key action items identified
• Timeline and owners assigned
• Next steps clear"""
        else:
            criteria = f"""STANDARD DECISION:
• Clear path forward identified
• Action items listed
• Next steps documented"""

        return criteria

    async def update_intent_with_action_link(self, intent_id: str, action_id: str) -> None:
        """Update Intent to link to created Action"""
        try:
            # Get current relations
            intent_page = await self.client.pages.retrieve(page_id=intent_id)
            current_actions = intent_page.get("properties", {}).get("Related_Actions", {}).get("relation", [])

            # Add new action
            current_actions.append({"id": action_id})

            # Update
            await self.client.pages.update(
                page_id=intent_id,
                properties={
                    "Related_Actions": {
                        "relation": current_actions
                    }
                }
            )

            logger.info(f"Linked action {action_id[:8]} to intent {intent_id[:8]}")
        except Exception as e:
            logger.error(f"Error linking action to intent: {e}")

    async def approve_action(self, action_id: str) -> None:
        """
        Approve an Action Pipe, set the approval timestamp, and capture the
        settlement diff for fine-tuning training data.

        Args:
            action_id: The ID of the Action Pipe to approve
        """
        from datetime import datetime

        try:
            await self.client.pages.update(
                page_id=action_id,
                properties={
                    "Approval_Status": {"select": {"name": "Approved"}},
                    "Approved_Date": {"date": {"start": datetime.now().date().isoformat()}}
                }
            )

            logger.info(f"Approved action {action_id[:8]} with timestamp")

            # Capture training data diff — non-blocking, never fails approval
            await self._log_settlement_diff_from_action(action_id)

            # Log this approval to Execution Log
            await self._log_execution(
                action="Action Approved",
                action_pipe_id=action_id,
                details=f"Action approved on {datetime.now().date().isoformat()}"
            )
        except Exception as e:
            logger.error(f"Error approving action: {e}")
            raise

    async def _log_settlement_diff_from_action(self, action_id: str) -> None:
        """
        Capture the diff between AI_Raw_Output (original) and the current field
        values (final) on an Action Pipe, then write to DB_Training_Data.

        Called automatically on approval so training data is collected without
        any manual steps.
        """
        import json as _json
        from app.diff_logger import DiffLogger

        try:
            action_page = await self.client.pages.retrieve(page_id=action_id)
            props = action_page.get("properties", {})

            # Original plan: what the AI generated
            ai_raw_items = props.get("AI_Raw_Output", {}).get("rich_text", [])
            ai_raw_text = ai_raw_items[0]["text"]["content"] if ai_raw_items else ""

            if not ai_raw_text.strip():
                logger.debug(f"No AI_Raw_Output on action {action_id[:8]}, skipping diff log")
                return

            try:
                original_plan = _json.loads(ai_raw_text)
            except _json.JSONDecodeError:
                original_plan = {"raw_output": ai_raw_text}

            # Final plan: what the user left after editing
            def _rt(key: str) -> str:
                items = props.get(key, {}).get("rich_text", [])
                return items[0]["text"]["content"] if items else ""

            final_plan = {
                "scenario_options": _rt("Scenario_Options"),
                "risk_assessment": _rt("Risk_Assessment"),
                "required_resources": _rt("Required_Resources"),
                "task_generation_template": _rt("Task_Generation_Template"),
                "recommended_option": (
                    props.get("Recommended_Option", {}).get("select", {}) or {}
                ).get("name", ""),
            }

            # Resolve intent ID from relation
            intent_relation = props.get("Intent", {}).get("relation", [])
            intent_id = intent_relation[0]["id"] if intent_relation else action_id

            # Resolve agent name from Agent relation → Agent Registry page
            agent_name = await self._get_agent_name_for_action(props)

            diff_logger = DiffLogger()
            await diff_logger.log_settlement_diff(
                intent_id=intent_id,
                original_plan=original_plan,
                final_plan=final_plan,
                agent_name=agent_name,
            )

            # Mark as diff-logged on the Action Pipe so the poller won't re-process it
            # (Diff_Logged checkbox must exist in DB_Action_Pipes schema; fails silently if not)
            try:
                await self.client.pages.update(
                    page_id=action_id,
                    properties={"Diff_Logged": {"checkbox": True}}
                )
            except Exception:
                pass

            logger.success(f"Settlement diff logged for action {action_id[:8]} (agent: {agent_name or 'unknown'})")

        except Exception as e:
            logger.warning(f"Settlement diff logging failed for action {action_id[:8]}: {e}")
            # Never propagate — approval must succeed even if diff logging fails

    async def _get_agent_name_for_action(self, props: Dict[str, Any]) -> Optional[str]:
        """Resolve the agent name via the Agent relation on an Action Pipe."""
        agent_relation = props.get("Agent", {}).get("relation", [])
        if not agent_relation:
            return None
        try:
            agent_page = await self.client.pages.retrieve(page_id=agent_relation[0]["id"])
            agent_props = agent_page.get("properties", {})
            name_items = agent_props.get("Agent_Name", {}).get("title", [])
            return name_items[0]["text"]["content"] if name_items else None
        except Exception:
            return None

    async def _log_execution(
        self,
        action: str,
        intent_id: Optional[str] = None,
        action_pipe_id: Optional[str] = None,
        details: str = ""
    ) -> None:
        """Log actions to Execution Log for audit trail"""
        try:
            # Get next Log ID
            log_id = await self._get_next_log_id()

            properties = {
                "Log_Entry_Title": {
                    "title": [{"text": {"content": action}}]
                },
                "Log_ID": {
                    "number": log_id
                },
                "Action_Taken": {
                    "rich_text": [{"text": {"content": details}}]
                },
                "Decision_Date": {
                    "date": {"start": datetime.now().date().isoformat()}
                }
            }

            # Add intent relation if provided
            if intent_id:
                properties["Intent"] = {"relation": [{"id": intent_id}]}

            await self.client.pages.create(
                parent={"database_id": settings.notion_db_execution_log},
                properties=properties
            )

            logger.debug(f"Logged execution: {action}")
        except Exception as e:
            logger.warning(f"Could not log execution: {e}")

    async def _get_next_log_id(self) -> int:
        """Get next sequential Log ID"""
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
        except:
            return 1
