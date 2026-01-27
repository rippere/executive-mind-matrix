"""
Monitoring and observability utilities for Executive Mind Matrix.
Includes Sentry error tracking, Prometheus metrics, and structured logging.
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger
from typing import Optional
import sys
import json
from datetime import datetime


class SentryConfig:
    """Sentry error tracking configuration"""

    @staticmethod
    def initialize(
        dsn: Optional[str],
        environment: str = "production",
        traces_sample_rate: float = 0.1,
        enable_tracing: bool = True
    ):
        """
        Initialize Sentry SDK with FastAPI integration.

        Args:
            dsn: Sentry DSN (Data Source Name)
            environment: Environment name (production, staging, development)
            traces_sample_rate: Percentage of transactions to trace (0.0 to 1.0)
            enable_tracing: Enable performance monitoring
        """
        if not dsn:
            logger.warning("Sentry DSN not provided. Error tracking disabled.")
            return

        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                LoguruIntegration(),
            ],
            traces_sample_rate=traces_sample_rate,
            enable_tracing=enable_tracing,
            # Send user feedback
            send_default_pii=False,
            # Set release version
            release="executive-mind-matrix@1.0.0",
            # Additional options
            attach_stacktrace=True,
            # Performance monitoring
            profiles_sample_rate=0.1,
        )

        logger.info(f"Sentry initialized for environment: {environment}")


class PrometheusMetrics:
    """Prometheus metrics for monitoring application performance"""

    def __init__(self):
        # Application info
        self.app_info = Info('executive_mind_matrix_info', 'Application information')
        self.app_info.info({
            'version': '1.0.0',
            'service': 'executive-mind-matrix'
        })

        # Notion API metrics
        self.notion_requests = Counter(
            'notion_api_requests_total',
            'Total number of Notion API requests',
            ['operation', 'status']
        )

        self.notion_request_duration = Histogram(
            'notion_api_request_duration_seconds',
            'Duration of Notion API requests',
            ['operation']
        )

        # Anthropic API metrics
        self.anthropic_requests = Counter(
            'anthropic_api_requests_total',
            'Total number of Anthropic API requests',
            ['model', 'status']
        )

        self.anthropic_request_duration = Histogram(
            'anthropic_api_request_duration_seconds',
            'Duration of Anthropic API requests',
            ['model']
        )

        self.anthropic_tokens_used = Counter(
            'anthropic_tokens_used_total',
            'Total tokens used in Anthropic API calls',
            ['model', 'type']  # type: input or output
        )

        # Polling metrics
        self.poll_cycles = Counter(
            'poll_cycles_total',
            'Total number of polling cycles completed',
            ['status']
        )

        self.poll_cycle_duration = Histogram(
            'poll_cycle_duration_seconds',
            'Duration of polling cycles'
        )

        self.items_processed = Counter(
            'items_processed_total',
            'Total number of items processed',
            ['type']  # type: intent, action_pipe, etc.
        )

        # Agent metrics
        self.agent_analyses = Counter(
            'agent_analyses_total',
            'Total number of agent analyses',
            ['agent', 'status']
        )

        self.agent_analysis_duration = Histogram(
            'agent_analysis_duration_seconds',
            'Duration of agent analyses',
            ['agent']
        )

        # Dialectic flow metrics
        self.dialectic_flows = Counter(
            'dialectic_flows_total',
            'Total number of dialectic flows',
            ['status']
        )

        self.dialectic_flow_duration = Histogram(
            'dialectic_flow_duration_seconds',
            'Duration of dialectic flows'
        )

        # System health metrics
        self.poller_status = Gauge(
            'poller_status',
            'Current status of the poller (1=running, 0=stopped)'
        )

        self.active_tasks = Gauge(
            'active_tasks',
            'Number of currently active background tasks'
        )

        # Error metrics
        self.errors = Counter(
            'errors_total',
            'Total number of errors',
            ['type', 'component']
        )

    def record_notion_request(self, operation: str, status: str, duration: float):
        """Record a Notion API request"""
        self.notion_requests.labels(operation=operation, status=status).inc()
        self.notion_request_duration.labels(operation=operation).observe(duration)

    def record_anthropic_request(
        self,
        model: str,
        status: str,
        duration: float,
        input_tokens: int = 0,
        output_tokens: int = 0
    ):
        """Record an Anthropic API request"""
        self.anthropic_requests.labels(model=model, status=status).inc()
        self.anthropic_request_duration.labels(model=model).observe(duration)
        if input_tokens > 0:
            self.anthropic_tokens_used.labels(model=model, type='input').inc(input_tokens)
        if output_tokens > 0:
            self.anthropic_tokens_used.labels(model=model, type='output').inc(output_tokens)

    def record_poll_cycle(self, status: str, duration: float):
        """Record a polling cycle"""
        self.poll_cycles.labels(status=status).inc()
        self.poll_cycle_duration.observe(duration)

    def record_item_processed(self, item_type: str):
        """Record an item processed"""
        self.items_processed.labels(type=item_type).inc()

    def record_agent_analysis(self, agent: str, status: str, duration: float):
        """Record an agent analysis"""
        self.agent_analyses.labels(agent=agent, status=status).inc()
        self.agent_analysis_duration.labels(agent=agent).observe(duration)

    def record_dialectic_flow(self, status: str, duration: float):
        """Record a dialectic flow"""
        self.dialectic_flows.labels(status=status).inc()
        self.dialectic_flow_duration.observe(duration)

    def update_poller_status(self, is_running: bool):
        """Update poller status"""
        self.poller_status.set(1 if is_running else 0)

    def update_active_tasks(self, count: int):
        """Update active tasks count"""
        self.active_tasks.set(count)

    def record_error(self, error_type: str, component: str):
        """Record an error"""
        self.errors.labels(type=error_type, component=component).inc()


class StructuredLogger:
    """Enhanced structured logging with JSON output for production"""

    @staticmethod
    def configure(
        log_level: str = "INFO",
        json_logs: bool = False,
        log_file: str = "logs/app.log"
    ):
        """
        Configure structured logging.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            json_logs: Whether to output logs in JSON format
            log_file: Path to log file
        """
        # Remove default logger
        logger.remove()

        if json_logs:
            # JSON structured logging for production
            def json_formatter(record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record["level"].name,
                    "message": record["message"],
                    "module": record["name"],
                    "function": record["function"],
                    "line": record["line"],
                }

                # Add extra context if available
                if record["extra"]:
                    log_entry["extra"] = record["extra"]

                # Add exception info if available
                if record["exception"]:
                    log_entry["exception"] = {
                        "type": record["exception"].type.__name__,
                        "value": str(record["exception"].value),
                        "traceback": record["exception"].traceback
                    }

                return json.dumps(log_entry)

            logger.add(
                sys.stdout,
                format=json_formatter,
                level=log_level,
                serialize=False
            )
        else:
            # Human-readable logging for development
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
                level=log_level
            )

        # File logging with rotation
        logger.add(
            log_file,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )

        logger.info(f"Logging configured: level={log_level}, json={json_logs}")


def setup_instrumentator(app):
    """
    Setup Prometheus FastAPI Instrumentator.

    Args:
        app: FastAPI application instance

    Returns:
        Instrumentator instance
    """
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.instrument(app)

    return instrumentator


# Global metrics instance
metrics = PrometheusMetrics()
