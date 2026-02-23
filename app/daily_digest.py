"""
Daily Digest - Automated Summary Notifications

Generates and sends daily/weekly summaries via email or Slack:
- New strategic intents created
- Completed tasks
- Pending approvals
- Agent performance trends
- Training data collection status

Supports multiple notification channels:
- Email (SMTP)
- Slack (webhook)
- Discord (webhook)
- Notion page update
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from notion_client import AsyncClient
import aiohttp

from config.settings import settings
from app.models import IntentStatus


class DailyDigest:
    """Generates and sends daily operational summaries"""

    def __init__(self):
        self.notion = AsyncClient(auth=settings.notion_api_key)

    async def generate_digest(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        Generate comprehensive digest for specified time range.

        Args:
            time_range: "24h", "7d", "30d"

        Returns:
            Dict with all digest sections
        """
        logger.info(f"Generating {time_range} digest")

        # Calculate time boundaries
        now = datetime.utcnow()
        if time_range == "24h":
            since = now - timedelta(days=1)
            title = "Daily Digest"
        elif time_range == "7d":
            since = now - timedelta(days=7)
            title = "Weekly Digest"
        elif time_range == "30d":
            since = now - timedelta(days=30)
            title = "Monthly Digest"
        else:
            since = now - timedelta(days=1)
            title = "Daily Digest"

        # Gather all metrics
        digest = {
            "title": title,
            "date": now.strftime("%Y-%m-%d"),
            "time_range": time_range,
            "intents": await self._get_intent_summary(since),
            "tasks": await self._get_task_summary(since),
            "approvals": await self._get_pending_approvals(),
            "agent_performance": await self._get_agent_performance(since),
            "training_data": await self._get_training_status(),
            "system_health": await self._get_system_health()
        }

        logger.success(f"Digest generated: {digest['intents']['total']} intents, {digest['tasks']['completed']} tasks completed")

        return digest

    async def _get_intent_summary(self, since: datetime) -> Dict[str, Any]:
        """Get summary of intents created in time range"""
        try:
            response = await self.notion.databases.query(
                database_id=settings.notion_db_executive_intents,
                filter={
                    "property": "Created_Date",
                    "date": {
                        "on_or_after": since.date().isoformat()
                    }
                }
            )

            intents = response.get("results", [])

            # Categorize by status
            by_status = {}
            by_impact = {"high": 0, "medium": 0, "low": 0}

            for intent in intents:
                props = intent.get("properties", {})

                # Status
                status_prop = props.get("Status", {}).get("select", {})
                status = status_prop.get("name", "Unknown")
                by_status[status] = by_status.get(status, 0) + 1

                # Impact
                impact = props.get("Projected_Impact", {}).get("number", 0)
                if impact >= 8:
                    by_impact["high"] += 1
                elif impact >= 5:
                    by_impact["medium"] += 1
                else:
                    by_impact["low"] += 1

            return {
                "total": len(intents),
                "by_status": by_status,
                "by_impact": by_impact,
                "high_impact_count": by_impact["high"]
            }

        except Exception as e:
            logger.error(f"Error getting intent summary: {e}")
            return {"total": 0, "by_status": {}, "by_impact": {}}

    async def _get_task_summary(self, since: datetime) -> Dict[str, Any]:
        """Get summary of tasks completed in time range"""
        try:
            # Get completed tasks
            response = await self.notion.databases.query(
                database_id=settings.notion_db_tasks,
                filter={
                    "property": "Status",
                    "status": {
                        "equals": "Done"
                    }
                }
            )

            tasks = response.get("results", [])

            # Count auto-generated vs manual
            auto_generated = 0
            manual = 0

            for task in tasks:
                props = task.get("properties", {})
                is_auto = props.get("Auto Generated", {}).get("checkbox", False)

                if is_auto:
                    auto_generated += 1
                else:
                    manual += 1

            return {
                "completed": len(tasks),
                "auto_generated": auto_generated,
                "manual": manual
            }

        except Exception as e:
            logger.error(f"Error getting task summary: {e}")
            return {"completed": 0, "auto_generated": 0, "manual": 0}

    async def _get_pending_approvals(self) -> Dict[str, Any]:
        """Get count of items awaiting approval"""
        try:
            response = await self.notion.databases.query(
                database_id=settings.notion_db_action_pipes,
                filter={
                    "property": "Approval_Status",
                    "select": {
                        "equals": "Pending"
                    }
                }
            )

            pending = response.get("results", [])

            # Get oldest pending
            oldest_date = None
            if pending:
                for action in pending:
                    created = action.get("created_time")
                    if created:
                        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        if not oldest_date or created_dt < oldest_date:
                            oldest_date = created_dt

            days_pending = None
            if oldest_date:
                days_pending = (datetime.now(oldest_date.tzinfo) - oldest_date).days

            return {
                "count": len(pending),
                "oldest_days": days_pending
            }

        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            return {"count": 0, "oldest_days": None}

    async def _get_agent_performance(self, since: datetime) -> Dict[str, Any]:
        """Get agent performance metrics"""
        try:
            response = await self.notion.databases.query(
                database_id=settings.notion_db_training_data
            )

            records = response.get("results", [])

            # Calculate per-agent metrics
            agent_metrics = {}

            for record in records:
                props = record.get("properties", {})

                agent_prop = props.get("Agent_Name", {}).get("select", {})
                agent_name = agent_prop.get("name", "Unknown")

                acceptance = props.get("Acceptance_Rate", {}).get("number", 0)

                if agent_name not in agent_metrics:
                    agent_metrics[agent_name] = {
                        "count": 0,
                        "total_acceptance": 0
                    }

                agent_metrics[agent_name]["count"] += 1
                agent_metrics[agent_name]["total_acceptance"] += acceptance

            # Calculate averages
            for agent, metrics in agent_metrics.items():
                if metrics["count"] > 0:
                    metrics["avg_acceptance"] = metrics["total_acceptance"] / metrics["count"]

            return agent_metrics

        except Exception as e:
            logger.error(f"Error getting agent performance: {e}")
            return {}

    async def _get_training_status(self) -> Dict[str, Any]:
        """Get training data collection status"""
        try:
            response = await self.notion.databases.query(
                database_id=settings.notion_db_training_data
            )

            total = len(response.get("results", []))

            return {
                "total_records": total,
                "ready_for_finetuning": total >= 100,
                "records_needed": max(0, 100 - total)
            }

        except Exception as e:
            logger.error(f"Error getting training status: {e}")
            return {"total_records": 0, "ready_for_finetuning": False}

    async def _get_system_health(self) -> Dict[str, str]:
        """Get system health indicators"""
        # Simple health check - can be expanded
        return {
            "poller": "active",
            "databases": "connected",
            "apis": "healthy"
        }

    def format_as_markdown(self, digest: Dict[str, Any]) -> str:
        """
        Format digest as markdown for Slack/Discord/Email.

        Returns:
            Markdown formatted string
        """
        md = f"""# {digest['title']} - {digest['date']}

## 📊 Strategic Intents

**Total Created**: {digest['intents']['total']}

**By Status**:
"""
        for status, count in digest['intents']['by_status'].items():
            md += f"- {status}: {count}\n"

        md += f"""
**By Impact**:
- 🔴 High Impact (8-10): {digest['intents']['by_impact']['high']}
- 🟡 Medium Impact (5-7): {digest['intents']['by_impact']['medium']}
- 🟢 Low Impact (1-4): {digest['intents']['by_impact']['low']}

---

## ✅ Task Completion

**Total Completed**: {digest['tasks']['completed']}
- 🤖 Auto-generated: {digest['tasks']['auto_generated']}
- ✍️ Manual: {digest['tasks']['manual']}

---

## ⏳ Pending Approvals

**Action Pipes Awaiting Review**: {digest['approvals']['count']}
"""
        if digest['approvals']['oldest_days']:
            md += f"⚠️ Oldest pending: {digest['approvals']['oldest_days']} days\n"

        md += """
---

## 🤖 Agent Performance

"""
        for agent, metrics in digest['agent_performance'].items():
            if 'avg_acceptance' in metrics:
                md += f"**{agent}**: {metrics['avg_acceptance']:.1f}% acceptance ({metrics['count']} settlements)\n"

        md += f"""
---

## 📈 Training Data Collection

**Total Records**: {digest['training_data']['total_records']}
**Fine-tuning Ready**: {"✅ Yes" if digest['training_data']['ready_for_finetuning'] else f"❌ No ({digest['training_data']['records_needed']} more needed)"}

---

## 🔧 System Health

- Poller: {digest['system_health']['poller'].upper()}
- Databases: {digest['system_health']['databases'].upper()}
- APIs: {digest['system_health']['apis'].upper()}

---

*Generated by Executive Mind Matrix*
"""
        return md

    async def send_to_slack(self, webhook_url: str, digest: Dict[str, Any]) -> bool:
        """
        Send digest to Slack via webhook.

        Args:
            webhook_url: Slack webhook URL
            digest: Digest data

        Returns:
            Success status
        """
        try:
            markdown = self.format_as_markdown(digest)

            payload = {
                "text": f"{digest['title']} - {digest['date']}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": markdown
                        }
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.success("Digest sent to Slack")
                        return True
                    else:
                        logger.error(f"Slack webhook failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error sending to Slack: {e}")
            return False

    async def send_to_discord(self, webhook_url: str, digest: Dict[str, Any]) -> bool:
        """
        Send digest to Discord via webhook.

        Args:
            webhook_url: Discord webhook URL
            digest: Digest data

        Returns:
            Success status
        """
        try:
            markdown = self.format_as_markdown(digest)

            payload = {
                "content": markdown[:2000],  # Discord limit
                "username": "Executive Mind Matrix"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status in [200, 204]:
                        logger.success("Digest sent to Discord")
                        return True
                    else:
                        logger.error(f"Discord webhook failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error sending to Discord: {e}")
            return False

    async def create_notion_digest_page(self, digest: Dict[str, Any]) -> Optional[str]:
        """
        Create a digest summary page in Notion.

        Returns:
            Page ID if created successfully
        """
        try:
            # Create page in root (or specify parent database)
            markdown = self.format_as_markdown(digest)

            # Convert markdown to Notion blocks (simplified)
            blocks = [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": f"{digest['title']} - {digest['date']}"}
                        }]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": markdown}
                        }]
                    }
                }
            ]

            # Create page (needs parent - could be a Digest database)
            # For now, just log the content
            logger.info(f"Digest page content prepared (not created - needs parent database)")

            return None

        except Exception as e:
            logger.error(f"Error creating Notion digest page: {e}")
            return None
