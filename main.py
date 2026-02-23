import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from config.settings import settings
from app.notion_poller import NotionPoller
from app.agent_router import AgentRouter
from app.diff_logger import DiffLogger
from app.models import AgentPersona, RiskLevel
from app.security import setup_cors, setup_rate_limiting
from app.smart_router import SmartRouter
from slowapi.errors import RateLimitExceeded

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG"
)

# Global poller instance
poller: NotionPoller = None
poller_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global poller, poller_task

    # Startup
    logger.info("Starting Executive Mind Matrix")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Polling interval: {settings.polling_interval_seconds}s")

    # Start the poller in background
    poller = NotionPoller()
    poller_task = asyncio.create_task(poller.start())

    logger.success("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Executive Mind Matrix")
    if poller:
        poller.stop()
    if poller_task:
        poller_task.cancel()
        try:
            await poller_task
        except asyncio.CancelledError:
            pass

    logger.success("Application shut down successfully")


# Initialize FastAPI app
app = FastAPI(
    title="Executive Mind Matrix",
    description="AI-powered decision intelligence system with adversarial agent dialectics",
    version="1.0.0",
    lifespan=lifespan
)

# Setup security middleware
setup_cors(app, settings.allowed_origins)

# Setup rate limiting
if settings.rate_limit_enabled:
    limiter = setup_rate_limiting(app, settings.rate_limit_per_minute)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": "Rate limit exceeded. Please try again later."
            }
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Executive Mind Matrix",
        "version": "1.0.0",
        "environment": settings.environment,
        "poller_running": poller.is_running if poller else False
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "poller_active": poller.is_running if poller else False,
        "polling_interval": settings.polling_interval_seconds,
        "databases_configured": {
            "system_inbox": bool(settings.notion_db_system_inbox),
            "executive_intents": bool(settings.notion_db_executive_intents),
            "action_pipes": bool(settings.notion_db_action_pipes),
            "agent_registry": bool(settings.notion_db_agent_registry),
            "execution_log": bool(settings.notion_db_execution_log),
            "training_data": bool(settings.notion_db_training_data),
            "tasks": bool(settings.notion_db_tasks),
            "projects": bool(settings.notion_db_projects),
            "areas": bool(settings.notion_db_areas),
            "nodes": bool(settings.notion_db_nodes)
        }
    }


@app.post("/trigger-poll")
async def trigger_poll():
    """Manually trigger a poll cycle (for testing)"""
    if not poller:
        raise HTTPException(status_code=503, detail="Poller not initialized")

    try:
        await poller.poll_cycle()
        return {"status": "success", "message": "Poll cycle completed"}
    except Exception as e:
        logger.error(f"Manual poll trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-intent/{intent_id}")
async def analyze_intent(
    intent_id: str,
    agent: AgentPersona,
    background_tasks: BackgroundTasks
):
    """
    Manually trigger analysis for a specific intent with a specific agent.
    Useful for testing or manual overrides.
    """

    try:
        # This would fetch intent details from Notion and run analysis
        # For now, return placeholder
        router = AgentRouter()

        return {
            "status": "queued",
            "intent_id": intent_id,
            "agent": agent.value,
            "message": "Analysis queued in background"
        }

    except Exception as e:
        logger.error(f"Error queueing analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dialectic/{intent_id}")
async def run_dialectic(intent_id: str):
    """
    Run adversarial dialectic flow for a specific intent.
    Adds results directly to the Intent page with proper workflow integration.
    """

    try:
        from app.workflow_integration import WorkflowIntegration
        from notion_client import AsyncClient

        router = AgentRouter()
        client = AsyncClient(auth=settings.notion_api_key)
        workflow = WorkflowIntegration(client)

        # Fetch intent details from Notion
        intent_page = await client.pages.retrieve(page_id=intent_id)
        properties = intent_page.get("properties", {})

        # Extract title and description
        title_prop = properties.get("Name", {}).get("title", [])
        title = title_prop[0]["text"]["content"] if title_prop else "Untitled"

        desc_prop = properties.get("Description", {}).get("rich_text", [])
        description = desc_prop[0]["text"]["content"] if desc_prop else ""

        # Extract Agent_Persona relation for linking to Action Pipe
        agent_relation = properties.get("Agent_Persona", {}).get("relation", [])
        agent_id = agent_relation[0]["id"] if agent_relation else None

        # Run dialectic analysis
        result = await router.dialectic_flow(
            intent_id=intent_id,
            intent_title=title,
            intent_description=description,
            success_criteria="",
            projected_impact=7
        )

        # Add formatted results using workflow integration
        dialectic_result = {
            "synthesis": result.synthesis,
            "recommended_path": result.recommended_path,
            "conflict_points": result.conflict_points,
            "growth_recommendation": result.growth_perspective.recommended_option if result.growth_perspective else "N/A",
            "risk_recommendation": result.risk_perspective.recommended_option if result.risk_perspective else "N/A"
        }

        await workflow.run_dialectic_and_link(intent_id, dialectic_result)

        # Create Action Pipe using EXISTING properties (avoid redundancy)
        consensus = dialectic_result['growth_recommendation'] == dialectic_result['risk_recommendation']

        # Format comprehensive scenario analysis for existing Scenario_Options field
        scenario_text = f"""DIALECTIC ANALYSIS

Growth Perspective (Entrepreneur): Option {dialectic_result['growth_recommendation']}
Risk Perspective (Auditor): Option {dialectic_result['risk_recommendation']}
Consensus: {'YES' if consensus else 'NO - Conflict detected'}

SYNTHESIS:
{result.synthesis}

RECOMMENDED PATH:
{dialectic_result['recommended_path']}

CONFLICT POINTS:
{chr(10).join(f"- {point}" for point in dialectic_result['conflict_points'])}
"""

        # Use Risk_Assessment for qualitative analysis
        risk_text = f"""Agent Agreement: {'Full consensus' if consensus else 'Split opinion'}

Growth-oriented risks: {result.growth_perspective.risk_assessment if result.growth_perspective else 'N/A'}

Governance-oriented risks: {result.risk_perspective.risk_assessment if result.risk_perspective else 'N/A'}
"""

        # Extract Required_Resources and Task_Generation_Template from growth perspective (primary analysis)
        import json
        required_resources = result.growth_perspective.required_resources if result.growth_perspective else {}
        resources_text = json.dumps(required_resources, indent=2) if required_resources else "Not specified"

        task_template = result.growth_perspective.task_generation_template if result.growth_perspective else []
        task_template_text = "\n".join(f"- {task}" for task in task_template) if task_template else "No tasks specified"

        # Preserve FULL AI output for debugging and training (no truncation)
        ai_raw_output = {
            "growth_analysis": result.growth_perspective.dict() if result.growth_perspective else None,
            "risk_analysis": result.risk_perspective.dict() if result.risk_perspective else None,
            "synthesis": result.synthesis,
            "recommended_path": result.recommended_path,
            "conflict_points": result.conflict_points
        }
        ai_raw_text = json.dumps(ai_raw_output, indent=2)

        action_response = await client.pages.create(
            parent={"database_id": settings.notion_db_action_pipes},
            properties={
                "Action_Title": {
                    "title": [{"text": {"content": f"Decision: {title}"}}]
                },
                "Intent": {
                    "relation": [{"id": intent_id}]
                },
                "Agent": {
                    "relation": [{"id": agent_id}] if agent_id else []
                },
                "Recommended_Option": {
                    "select": {"name": f"Option {dialectic_result['growth_recommendation']}"}
                },
                "Scenario_Options": {
                    "rich_text": [{"text": {"content": scenario_text[:2000]}}]
                },
                "Risk_Assessment": {
                    "rich_text": [{"text": {"content": risk_text[:2000]}}]
                },
                "Required_Resources": {
                    "rich_text": [{"text": {"content": resources_text[:2000]}}]
                },
                "Task_Generation_Template": {
                    "rich_text": [{"text": {"content": task_template_text[:2000]}}]
                },
                "Approval_Status": {
                    "select": {"name": "Pending"}
                },
                "Consensus": {
                    "checkbox": consensus
                }
            }
        )
        action_id = action_response["id"]

        # Store AI_Raw_Output as page body blocks (no character limit)
        # This prevents truncation that was corrupting training data
        try:
            await client.blocks.children.append(
                block_id=action_id,
                children=[
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": "🔒 AI Raw Output (Do Not Edit)"}
                            }],
                            "icon": {"emoji": "🔒"},
                            "color": "gray_background"
                        }
                    },
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": ai_raw_text}
                            }],
                            "language": "json"
                        }
                    }
                ]
            )
            logger.info(f"Saved raw AI output as page blocks ({len(ai_raw_text)} chars)")
        except Exception as e:
            logger.warning(f"Failed to save AI raw output blocks: {e}")
            # Don't fail the whole request if this fails

        return {
            "status": "success",
            "intent_id": intent_id,
            "action_id": action_id,
            "message": "Dialectic analysis complete and Action Pipe created",
            **dialectic_result
        }

    except Exception as e:
        logger.error(f"Error running dialectic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/action/{action_id}/approve")
async def approve_action(action_id: str):
    """
    Approve an Action Pipe and set the approval timestamp.

    This endpoint updates the Approval_Status to "Approved" and sets
    the Approved_Date to today's date. It also logs the approval to
    the Execution Log for audit trail purposes.
    """

    try:
        from app.workflow_integration import WorkflowIntegration
        from notion_client import AsyncClient

        client = AsyncClient(auth=settings.notion_api_key)
        workflow = WorkflowIntegration(client)

        await workflow.approve_action(action_id)

        return {
            "status": "success",
            "action_id": action_id,
            "message": "Action approved successfully"
        }

    except Exception as e:
        logger.error(f"Error approving action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/agent/{agent_name}")
async def get_agent_metrics(agent_name: str):
    """
    Get performance metrics for a specific agent based on training data.
    Shows acceptance rate and other learning metrics.
    """

    try:
        diff_logger = DiffLogger()
        metrics = await diff_logger.get_agent_performance_metrics(agent_name)

        return {
            "status": "success",
            "agent": agent_name,
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Error fetching agent metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/log-settlement")
async def log_settlement(
    intent_id: str,
    original_plan: dict,
    final_plan: dict
):
    """
    Log the difference between AI-generated plan and human-edited final plan.
    This is the core training data capture endpoint.
    """

    try:
        diff_logger = DiffLogger()
        result = await diff_logger.log_settlement_diff(
            intent_id=intent_id,
            original_plan=original_plan,
            final_plan=final_plan
        )

        return {
            "status": "success",
            "intent_id": intent_id,
            "modifications": len(result.user_modifications),
            "acceptance_rate": f"{result.acceptance_rate:.1%}",
            "timestamp": result.timestamp.isoformat()
        }

    except Exception as e:
        logger.error(f"Error logging settlement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/command-center/setup")
async def setup_command_center(force: bool = False):
    """
    ONE-TIME SETUP: Creates the Command Center structure with placeholders
    for linked database views. After running this once, you manually add
    the database views and never need to rebuild again.

    WARNING: This will DELETE all existing content on the Command Center page.
    Pass ?force=true to confirm you want to overwrite an existing page.
    """

    try:
        from app.command_center_final import FinalCommandCenter
        from notion_client import AsyncClient

        client = AsyncClient(auth=settings.notion_api_key)
        command_center = FinalCommandCenter(client)

        # Guard: check if page already has content
        existing = await client.blocks.children.list(block_id=command_center.command_center_id)
        if existing.get("results") and not force:
            raise HTTPException(
                status_code=409,
                detail="Command Center page already has content. Pass ?force=true to overwrite. WARNING: this will permanently delete the existing layout."
            )

        message = await command_center.initial_setup()

        return {
            "status": "success",
            "message": message,
            "url": f"https://notion.so/{command_center.command_center_id.replace('-', '')}",
            "next_steps": "Open the Command Center and add linked database views as instructed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up Command Center: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/intent/{intent_id}/create-action")
async def create_action_from_intent(
    intent_id: str,
    action_title: str = "Action from Intent",
    action_description: str = "Implement the decisions from this strategic intent"
):
    """
    Create an Action Pipe from an Executive Intent.
    This completes the workflow: Intent → Analysis → Decision → Action
    """

    try:
        from app.workflow_integration import WorkflowIntegration
        from notion_client import AsyncClient

        client = AsyncClient(auth=settings.notion_api_key)
        workflow = WorkflowIntegration(client)

        action_id = await workflow.create_action_from_intent(
            intent_id=intent_id,
            action_title=action_title,
            action_description=action_description
        )

        return {
            "status": "success",
            "intent_id": intent_id,
            "action_id": action_id,
            "message": "Action Pipe created and linked to Intent",
            "url": f"https://notion.so/{action_id.replace('-', '')}"
        }

    except Exception as e:
        logger.error(f"Error creating action from intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/command-center/update-metrics")
async def update_command_center_metrics():
    """
    Lightweight update - only refreshes the metrics callout.
    All database views update automatically in real-time, so this
    is the only thing you need to refresh periodically.
    """

    try:
        from app.command_center_final import FinalCommandCenter
        from notion_client import AsyncClient

        client = AsyncClient(auth=settings.notion_api_key)
        command_center = FinalCommandCenter(client)

        metrics = await command_center.update_metrics_only()

        return {
            "status": "success",
            "message": "Metrics updated",
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Error updating Command Center metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/action/{action_id}/spawn-tasks")
async def spawn_tasks_from_action(action_id: str):
    """
    Spawn tasks from an approved Action Pipe.
    This completes the workflow: Intent → Analysis → Approval → Task Generation
    """

    try:
        from app.task_spawner import TaskSpawner
        from notion_client import AsyncClient

        client = AsyncClient(auth=settings.notion_api_key)

        # Fetch action details
        action_page = await client.pages.retrieve(page_id=action_id)
        properties = action_page.get("properties", {})

        # Get task template from action
        task_template_prop = properties.get("Task_Generation_Template", {}).get("rich_text", [])
        task_template_text = task_template_prop[0]["text"]["content"] if task_template_prop else ""

        # Parse task template (assuming newline-separated tasks)
        task_list = [task.strip() for task in task_template_text.split("\n") if task.strip()]

        # Get related intent
        intent_relation = properties.get("Intent", {}).get("relation", [])
        intent_id = intent_relation[0]["id"] if intent_relation else None

        if not intent_id:
            raise HTTPException(status_code=400, detail="Action has no linked Intent")

        if not task_list:
            raise HTTPException(status_code=400, detail="Action has no task template")

        # Spawn tasks
        spawner = TaskSpawner()
        result = await spawner.spawn_tasks_from_intent(
            intent_id=intent_id,
            task_template=task_list,
            area_id=None  # Could extract from intent if needed
        )

        return {
            "status": "success",
            "action_id": action_id,
            "intent_id": intent_id,
            "tasks_created": result.tasks_created,
            "project_created": result.project_created,
            "project_id": result.project_id,
            "task_ids": result.task_ids,
            "message": f"Created {result.tasks_created} tasks" + (f" and 1 project" if result.project_created else "")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error spawning tasks from action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Fine-Tuning Analytics Endpoints
# ---------------------------------------------------------------------------

@app.get("/analytics/agents/summary")
async def get_agents_summary(time_range: str = "30d"):
    """
    Performance summary for all agents.

    time_range options: 7d | 30d | 90d | all
    """
    if time_range not in ("7d", "30d", "90d", "all"):
        raise HTTPException(status_code=400, detail="time_range must be 7d, 30d, 90d, or all")

    try:
        from app.training_analytics import TrainingAnalytics
        analytics = TrainingAnalytics()
        summary = await analytics.get_agent_performance_summary(time_range=time_range)
        return {"status": "success", **summary}
    except Exception as e:
        logger.error(f"Error fetching agent summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/agent/{agent_name}/improvements")
async def get_improvement_opportunities(
    agent_name: str,
    time_range: str = "30d",
):
    """
    Identify prompt improvement opportunities for a specific agent.

    agent_name: "The Entrepreneur" | "The Quant" | "The Auditor"
    """
    if time_range not in ("7d", "30d", "90d", "all"):
        raise HTTPException(status_code=400, detail="time_range must be 7d, 30d, 90d, or all")

    try:
        from app.training_analytics import TrainingAnalytics
        analytics = TrainingAnalytics()
        result = await analytics.identify_improvement_opportunities(
            agent_name=agent_name,
            time_range=time_range,
        )
        return {"status": "success", **result}
    except Exception as e:
        logger.error(f"Error identifying improvements for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/compare")
async def compare_agents(
    agent_a: str,
    agent_b: str,
    time_range: str = "30d",
):
    """
    Head-to-head comparison of two agents.

    Example: /analytics/compare?agent_a=The Entrepreneur&agent_b=The Auditor
    """
    if time_range not in ("7d", "30d", "90d", "all"):
        raise HTTPException(status_code=400, detail="time_range must be 7d, 30d, 90d, or all")

    try:
        from app.training_analytics import TrainingAnalytics
        analytics = TrainingAnalytics()
        comparison = await analytics.compare_agents(
            agent_a=agent_a,
            agent_b=agent_b,
            time_range=time_range,
        )
        return {"status": "success", "comparison": comparison.model_dump()}
    except Exception as e:
        logger.error(f"Error comparing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analytics/export/fine-tuning")
async def export_fine_tuning_data(
    min_acceptance_rate: float = 0.7,
    agent_name: str = None,
    time_range: str = "all",
    output_path: str = "data/finetuning_export.jsonl",
):
    """
    Export training data as JSONL for Claude fine-tuning.

    Only includes records at or above min_acceptance_rate (0–1).
    Optionally filter to a specific agent and/or time range.
    Returns path, example count, and validation report.
    """
    if not 0.0 <= min_acceptance_rate <= 1.0:
        raise HTTPException(status_code=400, detail="min_acceptance_rate must be between 0.0 and 1.0")

    if time_range not in ("7d", "30d", "90d", "all"):
        raise HTTPException(status_code=400, detail="time_range must be 7d, 30d, 90d, or all")

    try:
        from app.training_analytics import TrainingAnalytics
        analytics = TrainingAnalytics()
        result = await analytics.export_for_fine_tuning(
            output_path=output_path,
            min_acceptance_rate=min_acceptance_rate,
            agent_name=agent_name,
            time_range=time_range,
        )
        return {"status": "success", **result}
    except Exception as e:
        logger.error(f"Error exporting fine-tuning data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
# New endpoints to add to main.py after line ~700

@app.post("/intent/{intent_id}/assign-agent")
async def auto_assign_agent(
    intent_id: str,
    risk_level: Optional[str] = None,
    projected_impact: Optional[int] = None
):
    """
    Automatically assign the best agent persona to an intent using Smart Router.

    Args:
        intent_id: Intent to assign agent to
        risk_level: Optional risk level override (Low/Medium/High)
        projected_impact: Optional impact score override (1-10)

    Returns:
        Assigned agent, explanation, and alternative suggestion
    """
    try:
        from notion_client import AsyncClient
        client = AsyncClient(auth=settings.notion_api_key)

        # Fetch intent details
        intent_page = await client.pages.retrieve(page_id=intent_id)
        props = intent_page.get("properties", {})

        # Extract title
        title_prop = props.get("Name", {}).get("title", [])
        title = title_prop[0]["text"]["content"] if title_prop else ""

        # Extract description
        desc_prop = props.get("Description", {}).get("rich_text", [])
        description = desc_prop[0]["text"]["content"] if desc_prop else ""

        # Extract or use provided risk level
        if not risk_level:
            risk_prop = props.get("Risk_Level", {}).get("select", {})
            risk_level = risk_prop.get("name", "Medium")

        # Extract or use provided impact
        if not projected_impact:
            projected_impact = props.get("Projected_Impact", {}).get("number", 5)

        # Convert risk string to enum
        risk_enum = RiskLevel(risk_level) if risk_level else None

        # Assign agent
        assigned_agent = SmartRouter.assign_agent(
            intent_title=title,
            intent_description=description,
            risk_level=risk_enum,
            projected_impact=projected_impact
        )

        # Get explanation
        explanation = SmartRouter.explain_assignment(
            agent=assigned_agent,
            intent_title=title,
            intent_description=description,
            risk_level=risk_enum,
            projected_impact=projected_impact
        )

        # Get alternative suggestion
        alternative = SmartRouter.suggest_alternative_agent(
            assigned_agent=assigned_agent,
            risk_level=risk_enum,
            projected_impact=projected_impact
        )

        # Map agent to registry ID
        agent_map = {
            AgentPersona.ENTREPRENEUR: "4c4d39c3-1ff2-429f-ba14-b1be67c56eb3",
            AgentPersona.QUANT: "48c6110f-e4a0-4f70-92f6-f97b1f0e8e76",
            AgentPersona.AUDITOR: "f30957ac-f132-4bef-a584-8d8f36a417c0"
        }

        agent_id = agent_map.get(assigned_agent)

        # Update intent with assigned agent
        if agent_id:
            await client.pages.update(
                page_id=intent_id,
                properties={
                    "Agent_Persona": {
                        "relation": [{"id": agent_id}]
                    }
                }
            )

        logger.success(f"Auto-assigned {assigned_agent.value} to intent {intent_id[:8]}")

        return {
            "status": "success",
            "intent_id": intent_id,
            "assigned_agent": assigned_agent.value,
            "explanation": explanation,
            "alternative_agent": alternative.value if alternative else None,
            "agent_id": agent_id
        }

    except Exception as e:
        logger.error(f"Error auto-assigning agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/training-data/retrain")
async def trigger_fine_tuning_retrain(background_tasks: BackgroundTasks):
    """
    Trigger fine-tuning model retraining.

    This endpoint:
    1. Exports training data to JSONL format
    2. Validates dataset quality
    3. Returns upload instructions for Anthropic Console

    Note: Actual model fine-tuning happens in Anthropic Console.
    This endpoint prepares the training data.

    Returns:
        Dataset stats, validation report, and next steps
    """
    try:
        from app.fine_tuning.data_export import DataExporter
        from app.training_analytics import TrainingAnalytics

        # Step 1: Get performance summary
        analytics = TrainingAnalytics()
        summary = await analytics.get_performance_summary()

        if not summary:
            raise HTTPException(
                status_code=400,
                detail="No training data available. Need at least 10 settlement diffs."
            )

        # Step 2: Export to JSONL
        exporter = DataExporter()
        output_path = await exporter.export_to_anthropic_jsonl(
            agent_filter=None,  # Export all agents
            min_acceptance_rate=0.6,  # Only include decent examples
            output_dir="exports"
        )

        # Step 3: Validate dataset
        validation = await exporter.validate_jsonl(output_path)

        if not validation.ready_for_finetuning:
            raise HTTPException(
                status_code=400,
                detail=f"Dataset validation failed: {validation.errors}"
            )

        # Step 4: Generate upload instructions
        instructions = f"""
Fine-tuning dataset ready!

📊 **Dataset Stats**:
- Total examples: {validation.total_examples}
- Valid examples: {validation.valid_examples}
- Average acceptance rate: {validation.avg_acceptance_rate:.1%}
- File: {output_path}

🚀 **Next Steps**:

1. **Upload to Anthropic Console**:
   - Go to https://console.anthropic.com/settings/fine-tuning
   - Click "Create Fine-Tuning Job"
   - Upload: {output_path}
   - Base model: claude-3-haiku-20240307 (recommended for cost)

2. **Configure Job**:
   - Training split: 80/20
   - Epochs: 3-5 (start with 3)
   - Learning rate: Auto

3. **Monitor Training**:
   - Training takes 2-4 hours
   - Check validation loss curve
   - Wait for "Completed" status

4. **Deploy Fine-Tuned Model**:
   - Get model ID from console
   - Update .env: ANTHROPIC_MODEL=<your-fine-tuned-model-id>
   - Redeploy to Railway

5. **A/B Test**:
   - Run both models for 1 week
   - Compare acceptance rates
   - Keep the better performer

📈 **Expected Improvement**:
Based on current avg acceptance rate of {summary[0].avg_acceptance_rate:.1%},
fine-tuning typically improves by 5-15 percentage points.

💰 **Cost Estimate**:
- Training: ~$10-30 (one-time)
- Inference: +20% vs base model
- Worth it if acceptance rate improves significantly
"""

        logger.success(f"Fine-tuning dataset prepared: {output_path}")

        return {
            "status": "success",
            "dataset_path": output_path,
            "validation": validation.model_dump(),
            "summary": [s.model_dump() for s in summary],
            "instructions": instructions,
            "ready_for_upload": validation.ready_for_finetuning
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error preparing fine-tuning data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/smart-router/explain")
async def explain_smart_router(
    intent_title: str,
    intent_description: str,
    risk_level: Optional[str] = "Medium",
    projected_impact: Optional[int] = 5
):
    """
    Preview Smart Router assignment without modifying anything.

    Useful for understanding why an agent would be assigned before committing.

    Args:
        intent_title: Intent title
        intent_description: Intent description
        risk_level: Risk level (Low/Medium/High)
        projected_impact: Impact score (1-10)

    Returns:
        Agent assignment, explanation, and alternative
    """
    try:
        risk_enum = RiskLevel(risk_level) if risk_level else RiskLevel.MEDIUM

        assigned_agent = SmartRouter.assign_agent(
            intent_title=intent_title,
            intent_description=intent_description,
            risk_level=risk_enum,
            projected_impact=projected_impact
        )

        explanation = SmartRouter.explain_assignment(
            agent=assigned_agent,
            intent_title=intent_title,
            intent_description=intent_description,
            risk_level=risk_enum,
            projected_impact=projected_impact
        )

        alternative = SmartRouter.suggest_alternative_agent(
            assigned_agent=assigned_agent,
            risk_level=risk_enum,
            projected_impact=projected_impact
        )

        return {
            "assigned_agent": assigned_agent.value,
            "explanation": explanation,
            "alternative_agent": alternative.value if alternative else None,
            "confidence": "high" if any([
                risk_level == "High",
                projected_impact >= 8,
                len([kw for kw in SmartRouter.QUANT_KEYWORDS if kw in intent_description.lower()]) >= 3
            ]) else "medium"
        }

    except Exception as e:
        logger.error(f"Error explaining smart router: {e}")
        raise HTTPException(status_code=500, detail=str(e))
