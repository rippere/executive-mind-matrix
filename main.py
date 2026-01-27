import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from config.settings import settings
from app.notion_poller import NotionPoller
from app.agent_router import AgentRouter
from app.diff_logger import DiffLogger
from app.models import AgentPersona

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
            "training_data": bool(settings.notion_db_training_data)
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
    Returns synthesis of Growth vs Risk perspectives.
    """

    try:
        router = AgentRouter()

        # In production, fetch intent details from Notion
        # For now, use placeholder
        result = await router.dialectic_flow(
            intent_id=intent_id,
            intent_title="Sample Intent",
            intent_description="This is a test intent for dialectic analysis",
            success_criteria="Achieve desired outcome",
            projected_impact=7
        )

        return {
            "status": "success",
            "intent_id": intent_id,
            "synthesis": result.synthesis,
            "recommended_path": result.recommended_path,
            "conflict_points": result.conflict_points,
            "growth_recommendation": result.growth_perspective.recommended_option,
            "risk_recommendation": result.risk_perspective.recommended_option
        }

    except Exception as e:
        logger.error(f"Error running dialectic: {e}")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
