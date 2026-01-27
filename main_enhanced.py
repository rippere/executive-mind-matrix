import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from loguru import logger
import sys

from config.settings import settings
from app.notion_poller import NotionPoller
from app.agent_router import AgentRouter
from app.diff_logger import DiffLogger
from app.models import AgentPersona
from app.monitoring import (
    SentryConfig,
    StructuredLogger,
    setup_instrumentator,
    metrics
)
from app.security import (
    SecurityHeadersMiddleware,
    APIKeyMiddleware,
    RequestLoggingMiddleware,
    setup_cors,
    setup_rate_limiting,
)

# Configure structured logging
StructuredLogger.configure(
    log_level=settings.log_level,
    json_logs=settings.json_logs,
    log_file="logs/app.log"
)

# Initialize Sentry if configured
if settings.sentry_dsn:
    SentryConfig.initialize(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=settings.sentry_traces_sample_rate
    )
    logger.info("Sentry error tracking enabled")
else:
    logger.warning("Sentry DSN not configured. Error tracking disabled.")

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

    # Update metrics
    metrics.update_poller_status(False)

    # Start the poller in background
    poller = NotionPoller()
    poller_task = asyncio.create_task(poller.start())
    metrics.update_poller_status(True)

    logger.success("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Executive Mind Matrix")
    if poller:
        poller.stop()
        metrics.update_poller_status(False)
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

# Setup CORS
setup_cors(app, settings.allowed_origins)

# Setup rate limiting
if settings.rate_limit_enabled:
    limiter = setup_rate_limiting(app, settings.rate_limit_per_minute)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add API key middleware if configured
if settings.api_key:
    app.add_middleware(
        APIKeyMiddleware,
        api_key=settings.api_key,
        api_key_header=settings.api_key_header
    )
    logger.info("API key authentication enabled")

# Setup Prometheus instrumentation
if settings.enable_metrics:
    instrumentator = setup_instrumentator(app)
    instrumentator.expose(app, endpoint="/metrics")
    logger.info("Prometheus metrics enabled at /metrics")


@app.get("/")
async def root():
    """Root endpoint with basic service information"""
    return {
        "status": "running",
        "service": "Executive Mind Matrix",
        "version": "1.0.0",
        "environment": settings.environment,
        "poller_running": poller.is_running if poller else False
    }


@app.get("/health")
async def health():
    """Detailed health check endpoint"""
    health_status = {
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

    # Update metrics
    metrics.update_poller_status(poller.is_running if poller else False)

    return health_status


@app.post("/trigger-poll")
async def trigger_poll():
    """Manually trigger a poll cycle (for testing)"""
    if not poller:
        metrics.record_error("poller_not_initialized", "poller")
        raise HTTPException(status_code=503, detail="Poller not initialized")

    try:
        await poller.poll_cycle()
        return {"status": "success", "message": "Poll cycle completed"}
    except Exception as e:
        logger.error(f"Manual poll trigger failed: {e}")
        metrics.record_error("poll_trigger_failed", "poller")
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
        router = AgentRouter()

        return {
            "status": "queued",
            "intent_id": intent_id,
            "agent": agent.value,
            "message": "Analysis queued in background"
        }

    except Exception as e:
        logger.error(f"Error queueing analysis: {e}")
        metrics.record_error("analyze_intent_failed", "agent_router")
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
        metrics.record_error("dialectic_failed", "agent_router")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/agent/{agent_name}")
async def get_agent_metrics(agent_name: str):
    """
    Get performance metrics for a specific agent based on training data.
    Shows acceptance rate and other learning metrics.
    """

    try:
        diff_logger = DiffLogger()
        agent_metrics = await diff_logger.get_agent_performance_metrics(agent_name)

        return {
            "status": "success",
            "agent": agent_name,
            "metrics": agent_metrics
        }

    except Exception as e:
        logger.error(f"Error fetching agent metrics: {e}")
        metrics.record_error("agent_metrics_failed", "diff_logger")
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
        metrics.record_error("log_settlement_failed", "diff_logger")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
