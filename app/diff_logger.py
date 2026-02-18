from typing import Dict, Any, List
from datetime import datetime
from deepdiff import DeepDiff
from notion_client import AsyncClient
from loguru import logger
import json

from config.settings import settings
from app.models import SettlementDiff


class DiffLogger:
    """Captures and logs the delta between AI suggestions and human edits"""

    def __init__(self):
        self.client = AsyncClient(auth=settings.notion_api_key)

    async def log_settlement_diff(
        self,
        intent_id: str,
        original_plan: Dict[str, Any],
        final_plan: Dict[str, Any],
        agent_name: str = None,
    ) -> SettlementDiff:
        """
        Compare AI-generated plan vs human-edited final plan.
        This is the core training data asset.
        """

        logger.info(f"Logging settlement diff for intent {intent_id[:8]}")

        # Calculate deep diff
        diff = DeepDiff(original_plan, final_plan, ignore_order=True)

        # Extract human modifications
        modifications = self._extract_modifications(diff)

        # Calculate acceptance rate (how much of AI suggestion was kept)
        acceptance_rate = self._calculate_acceptance_rate(original_plan, final_plan, diff)

        # Create SettlementDiff object
        settlement_diff = SettlementDiff(
            intent_id=intent_id,
            timestamp=datetime.utcnow(),
            original_plan=original_plan,
            final_plan=final_plan,
            diff_summary=json.loads(diff.to_json()),
            user_modifications=modifications,
            acceptance_rate=acceptance_rate
        )

        # Save to Notion Training Data database
        await self._save_to_notion(settlement_diff, agent_name=agent_name)

        # Also save to local JSON log (backup)
        await self._save_to_json_log(settlement_diff)

        logger.info(
            f"Settlement diff logged: {len(modifications)} modifications, "
            f"{acceptance_rate:.1%} acceptance rate"
        )

        return settlement_diff

    def _extract_modifications(self, diff: DeepDiff) -> List[str]:
        """Extract human-readable list of what the user changed"""
        modifications = []

        # Values changed
        if "values_changed" in diff:
            for path, change in diff["values_changed"].items():
                modifications.append(
                    f"Modified {path}: {change['old_value']} → {change['new_value']}"
                )

        # Items added
        if "dictionary_item_added" in diff:
            for item in diff["dictionary_item_added"]:
                modifications.append(f"Added: {item}")

        # Items removed
        if "dictionary_item_removed" in diff:
            for item in diff["dictionary_item_removed"]:
                modifications.append(f"Removed: {item}")

        # Type changes
        if "type_changes" in diff:
            for path, change in diff["type_changes"].items():
                modifications.append(
                    f"Type changed at {path}: {change['old_type']} → {change['new_type']}"
                )

        return modifications

    def _calculate_acceptance_rate(
        self,
        original: Dict[str, Any],
        final: Dict[str, Any],
        diff: DeepDiff
    ) -> float:
        """
        Calculate what percentage of AI suggestion was accepted.
        Higher = user made fewer changes = AI was more aligned
        """

        # Simple heuristic: count total keys in original
        total_keys = self._count_leaf_keys(original)

        if total_keys == 0:
            return 0.0

        # Count changed keys
        changed_keys = (
            len(diff.get("values_changed", {})) +
            len(diff.get("dictionary_item_added", set())) +
            len(diff.get("dictionary_item_removed", set())) +
            len(diff.get("type_changes", {}))
        )

        # Acceptance rate = (total - changed) / total
        acceptance_rate = max(0.0, (total_keys - changed_keys) / total_keys)

        return acceptance_rate

    def _count_leaf_keys(self, obj: Any, count: int = 0) -> int:
        """Recursively count leaf nodes in nested dict/list structure"""
        if isinstance(obj, dict):
            for value in obj.values():
                count = self._count_leaf_keys(value, count)
        elif isinstance(obj, list):
            for item in obj:
                count = self._count_leaf_keys(item, count)
        else:
            count += 1
        return count

    async def _save_to_notion(self, diff: SettlementDiff, agent_name: str = None):
        """Save settlement diff to Notion Training Data database"""
        try:
            properties = {
                "Title": {
                    "title": [{
                        "text": {
                            "content": f"Settlement Diff - {diff.intent_id[:8]} - {diff.timestamp.isoformat()}"
                        }
                    }]
                },
                "Intent_ID": {
                    "rich_text": [{
                        "text": {"content": diff.intent_id}
                    }]
                },
                "Timestamp": {
                    "date": {
                        "start": diff.timestamp.isoformat()
                    }
                },
                "Acceptance_Rate": {
                    "number": round(diff.acceptance_rate * 100, 2)
                },
                "Modifications_Count": {
                    "number": len(diff.user_modifications)
                },
                "Modifications": {
                    "rich_text": [{
                        "text": {
                            "content": "\n".join(diff.user_modifications)[:2000]  # Notion limit
                        }
                    }]
                },
                "Original_Plan": {
                    "rich_text": [{
                        "text": {
                            "content": json.dumps(diff.original_plan, indent=2)[:2000]
                        }
                    }]
                },
                "Final_Plan": {
                    "rich_text": [{
                        "text": {
                            "content": json.dumps(diff.final_plan, indent=2)[:2000]
                        }
                    }]
                }
            }

            # Tag with agent name — requires Agent_Name (Select) in DB_Training_Data schema
            # Fails silently if property not yet added to Notion
            if agent_name:
                properties["Agent_Name"] = {
                    "select": {"name": agent_name}
                }

            await self.client.pages.create(
                parent={"database_id": settings.notion_db_training_data},
                properties=properties
            )

            logger.debug(f"Saved settlement diff to Notion: {diff.intent_id[:8]}")

        except Exception as e:
            logger.error(f"Error saving settlement diff to Notion: {e}")
            # Don't raise - we have JSON backup

    async def _save_to_json_log(self, diff: SettlementDiff):
        """Save settlement diff to local JSON file (backup)"""
        import aiofiles
        import os

        log_file = "logs/settlement_diffs.jsonl"
        os.makedirs("logs", exist_ok=True)

        try:
            async with aiofiles.open(log_file, mode='a') as f:
                await f.write(diff.model_dump_json() + "\n")

            logger.debug(f"Saved settlement diff to JSON log: {diff.intent_id[:8]}")

        except Exception as e:
            logger.error(f"Error saving settlement diff to JSON: {e}")

    async def get_agent_performance_metrics(self, agent_name: str) -> Dict[str, Any]:
        """
        Query training data to analyze how well a specific agent performs.
        This enables continuous improvement.
        """
        try:
            response = await self.client.databases.query(
                database_id=settings.notion_db_training_data,
                # Filter by agent if we add that property
                sorts=[
                    {
                        "property": "Timestamp",
                        "direction": "descending"
                    }
                ]
            )

            results = response.get("results", [])

            if not results:
                return {
                    "agent": agent_name,
                    "total_settlements": 0,
                    "avg_acceptance_rate": 0.0
                }

            # Calculate metrics
            acceptance_rates = []
            for page in results:
                props = page.get("properties", {})
                rate = props.get("Acceptance_Rate", {}).get("number", 0)
                if rate:
                    acceptance_rates.append(rate / 100)

            # 🛡️ SAFETY CHECK: Handle empty data to prevent ZeroDivisionError
            if not acceptance_rates:
                return {
                    "agent": agent_name,
                    "total_settlements": len(results),
                    "avg_acceptance_rate": 0.0,
                    "min_acceptance_rate": 0.0,
                    "max_acceptance_rate": 0.0
                }

            # Safe calculation with populated data
            return {
                "agent": agent_name,
                "total_settlements": len(results),
                "avg_acceptance_rate": sum(acceptance_rates) / len(acceptance_rates),
                "min_acceptance_rate": min(acceptance_rates),
                "max_acceptance_rate": max(acceptance_rates)
            }

        except Exception as e:
            logger.error(f"Error fetching agent performance metrics: {e}")
            return {}
