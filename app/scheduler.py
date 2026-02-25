"""
Task Scheduler - Automated Background Jobs

Manages scheduled tasks:
- Daily digest generation (8am daily)
- Weekly summary (Monday 9am)
- Command Center metrics refresh (every 15 minutes, configurable)
- Training data exports (monthly)
- System health checks (hourly)

Uses APScheduler for reliable scheduling.
"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from config.settings import settings
from app.daily_digest import DailyDigest


class TaskScheduler:
    """Manages scheduled background tasks"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.digest = DailyDigest()
        self.notion_client = None  # Will be set via set_notion_client()

    async def generate_and_send_daily_digest(self):
        """Generate and send daily digest (called by scheduler)"""
        try:
            logger.info("Starting scheduled daily digest")

            # Generate digest
            digest = await self.digest.generate_digest(time_range="24h")

            # Send to configured channels
            if settings.slack_webhook_url:
                await self.digest.send_to_slack(
                    webhook_url=settings.slack_webhook_url,
                    digest=digest
                )

            if settings.discord_webhook_url:
                await self.digest.send_to_discord(
                    webhook_url=settings.discord_webhook_url,
                    digest=digest
                )

            logger.success("Daily digest sent successfully")

        except Exception as e:
            logger.error(f"Error in scheduled daily digest: {e}")

    async def generate_weekly_summary(self):
        """Generate and send weekly summary (called by scheduler)"""
        try:
            logger.info("Starting scheduled weekly summary")

            digest = await self.digest.generate_digest(time_range="7d")

            if settings.slack_webhook_url:
                await self.digest.send_to_slack(
                    webhook_url=settings.slack_webhook_url,
                    digest=digest
                )

            logger.success("Weekly summary sent successfully")

        except Exception as e:
            logger.error(f"Error in scheduled weekly summary: {e}")

    async def refresh_command_center_metrics(self):
        """
        Refresh Command Center metrics in Notion.

        This updates the metrics without recreating the entire command center.
        Runs automatically based on configured interval.
        """
        try:
            from datetime import datetime
            start_time = datetime.now()

            logger.info("Starting scheduled Command Center metrics refresh")

            if not self.notion_client:
                logger.warning("Notion client not set. Skipping Command Center refresh.")
                return

            from app.command_center_final import FinalCommandCenter

            # Create command center instance
            command_center = FinalCommandCenter(self.notion_client)

            # Update only the metrics (lightweight operation)
            metrics = await command_center.update_metrics_only()

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            logger.success(
                f"Command Center metrics refreshed successfully in {execution_time:.2f}s"
            )
            logger.info(f"Metrics: {metrics}")

            # Record metrics for monitoring
            try:
                from app.monitoring import metrics as prom_metrics
                prom_metrics.record_command_center_refresh(
                    success=True,
                    execution_time=execution_time
                )
            except Exception as metric_err:
                logger.debug(f"Failed to record Prometheus metrics: {metric_err}")

        except Exception as e:
            logger.error(f"Error in scheduled Command Center refresh: {e}")

            # Record failure metric
            try:
                from app.monitoring import metrics as prom_metrics
                prom_metrics.record_command_center_refresh(
                    success=False,
                    execution_time=0
                )
            except Exception as metric_err:
                logger.debug(f"Failed to record Prometheus metrics: {metric_err}")

    def set_notion_client(self, client):
        """Set the Notion client for Command Center operations"""
        self.notion_client = client
        logger.debug("Notion client set for scheduler")

    def start(self):
        """Start the scheduler with all configured jobs"""
        try:
            logger.info("Starting task scheduler")

            # Daily digest - 8am every day
            self.scheduler.add_job(
                self.generate_and_send_daily_digest,
                CronTrigger(hour=8, minute=0),
                id="daily_digest",
                name="Daily Digest",
                replace_existing=True
            )

            # Weekly summary - Monday 9am
            self.scheduler.add_job(
                self.generate_weekly_summary,
                CronTrigger(day_of_week="mon", hour=9, minute=0),
                id="weekly_summary",
                name="Weekly Summary",
                replace_existing=True
            )

            # Command Center metrics refresh - every N minutes (configurable)
            if settings.command_center_refresh_enabled:
                self.schedule_command_center_refresh()
                logger.info(
                    f"Command Center auto-refresh enabled "
                    f"(every {settings.command_center_refresh_interval} minutes)"
                )
            else:
                logger.info("Command Center auto-refresh disabled")

            # Start scheduler
            self.scheduler.start()

            logger.success("Task scheduler started")

            # Log next run times (with error handling)
            try:
                daily_job = self.scheduler.get_job('daily_digest')
                if daily_job and daily_job.next_run_time:
                    logger.info(f"Next daily digest: {daily_job.next_run_time}")

                weekly_job = self.scheduler.get_job('weekly_summary')
                if weekly_job and weekly_job.next_run_time:
                    logger.info(f"Next weekly summary: {weekly_job.next_run_time}")

                cc_job = self.scheduler.get_job('command_center_refresh')
                if cc_job and cc_job.next_run_time:
                    logger.info(f"Next Command Center refresh: {cc_job.next_run_time}")
            except Exception as e:
                logger.warning(f"Could not get job next run times: {e}")

        except Exception as e:
            logger.error(f"Failed to start task scheduler: {e}")
            raise

    def schedule_command_center_refresh(self):
        """Schedule automatic Command Center metrics refresh"""
        interval = settings.command_center_refresh_interval

        self.scheduler.add_job(
            self.refresh_command_center_metrics,
            CronTrigger(minute=f'*/{interval}'),  # Every N minutes
            id='command_center_refresh',
            name='Command Center Metrics Refresh',
            replace_existing=True
        )

        logger.debug(f"Scheduled Command Center refresh every {interval} minutes")

    def stop(self):
        """Stop the scheduler gracefully"""
        logger.info("Stopping task scheduler")
        self.scheduler.shutdown(wait=True)
        logger.success("Task scheduler stopped")

    def list_jobs(self):
        """List all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
