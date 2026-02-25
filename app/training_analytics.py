"""
TrainingAnalytics: Aggregates and analyzes training data from Notion DB_Training_Data.

Provides:
- Agent performance summaries with trend data
- Improvement opportunity detection via EditPatternAnalyzer
- Head-to-head agent comparisons
- JSONL export for Claude fine-tuning via FineTuningDataPrep
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from notion_client import AsyncClient
from loguru import logger

from config.settings import settings
from app.models import (
    TrainingRecord,
    AgentPerformanceSummary,
    EditPattern,
    AgentComparison,
    DatasetValidationReport,
)
from app.fine_tuning.pattern_analysis import EditPatternAnalyzer
from app.fine_tuning.data_export import FineTuningDataPrep


_TIME_RANGE_DAYS: Dict[str, Optional[int]] = {
    "7d": 7,
    "30d": 30,
    "90d": 90,
    "all": None,
}


class TrainingAnalytics:
    """
    Central analytics engine for the fine-tuning pipeline.

    Queries Notion DB_Training_Data, parses settlement diffs, and surfaces
    actionable insights for prompt engineering and fine-tuning.
    """

    def __init__(self):
        self.client = AsyncClient(auth=settings.notion_api_key)
        self._pattern_analyzer = EditPatternAnalyzer()
        self._exporter = FineTuningDataPrep()

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    async def get_agent_performance_summary(
        self,
        time_range: str = "30d",
    ) -> Dict[str, Any]:
        """
        Returns performance metrics for all three agents.

        Response shape:
        {
            "time_range": "30d",
            "generated_at": "<iso>",
            "overall": { avg_acceptance_rate, total_settlements },
            "agents": { "The Entrepreneur": AgentPerformanceSummary, ... }
        }
        """
        records = await self._fetch_training_records(time_range=time_range)

        if not records:
            return {
                "time_range": time_range,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "overall": {"avg_acceptance_rate": 0.0, "total_settlements": 0},
                "agents": {},
                "message": "No training data found. Start collecting settlements via /log-settlement.",
            }

        # Group by agent (agent_name may be None if not enriched)
        agent_groups: Dict[str, List[TrainingRecord]] = {}
        untagged: List[TrainingRecord] = []

        for record in records:
            if record.agent_name:
                agent_groups.setdefault(record.agent_name, []).append(record)
            else:
                untagged.append(record)

        summaries: Dict[str, Any] = {}
        all_rates: List[float] = []

        for agent_name, agent_records in agent_groups.items():
            summary = self._build_agent_summary(agent_name, agent_records, time_range)
            summaries[agent_name] = summary.model_dump()
            all_rates.extend([r.acceptance_rate for r in agent_records])

        # Include untagged records in overall stats
        for r in untagged:
            all_rates.append(r.acceptance_rate)

        overall_avg = sum(all_rates) / len(all_rates) if all_rates else 0.0

        return {
            "time_range": time_range,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall": {
                "avg_acceptance_rate": round(overall_avg, 3),
                "total_settlements": len(records),
                "untagged_settlements": len(untagged),
            },
            "agents": summaries,
        }

    async def identify_improvement_opportunities(
        self,
        agent_name: str,
        time_range: str = "30d",
    ) -> Dict[str, Any]:
        """
        Analyze where a specific agent consistently fails.

        Returns deletion patterns, addition patterns, tone shifts,
        and synthesized recommendations.
        """
        records = await self._fetch_training_records(
            time_range=time_range, agent_name=agent_name
        )

        if not records:
            return {
                "agent": agent_name,
                "time_range": time_range,
                "message": f"No training data for '{agent_name}' in this time range.",
                "recommendations": [],
            }

        deletions = self._pattern_analyzer.analyze_deletion_patterns(records)
        additions = self._pattern_analyzer.analyze_addition_patterns(records)
        tone_shifts = self._pattern_analyzer.detect_tone_shifts(records)
        recommendations = self._pattern_analyzer.get_improvement_recommendations(
            deletions, additions, tone_shifts
        )

        return {
            "agent": agent_name,
            "time_range": time_range,
            "records_analyzed": len(records),
            "deletion_patterns": [p.model_dump() for p in deletions],
            "addition_patterns": [p.model_dump() for p in additions],
            "tone_shifts": tone_shifts,
            "recommendations": recommendations,
        }

    async def compare_agents(
        self,
        agent_a: str,
        agent_b: str,
        time_range: str = "30d",
    ) -> AgentComparison:
        """
        Head-to-head performance comparison between two agents.
        """
        records_a = await self._fetch_training_records(
            time_range=time_range, agent_name=agent_a
        )
        records_b = await self._fetch_training_records(
            time_range=time_range, agent_name=agent_b
        )

        avg_a = self._avg_acceptance(records_a)
        avg_b = self._avg_acceptance(records_b)

        if avg_a > avg_b + 0.02:
            winner = agent_a
        elif avg_b > avg_a + 0.02:
            winner = agent_b
        else:
            winner = "tie"

        return AgentComparison(
            agent_a=agent_a,
            agent_b=agent_b,
            agent_a_avg_acceptance=round(avg_a, 3),
            agent_b_avg_acceptance=round(avg_b, 3),
            agent_a_total_settlements=len(records_a),
            agent_b_total_settlements=len(records_b),
            winner=winner,
            delta=round(abs(avg_a - avg_b), 3),
        )

    async def export_for_fine_tuning(
        self,
        output_path: str = "data/finetuning_export.jsonl",
        min_acceptance_rate: float = 0.7,
        agent_name: Optional[str] = None,
        time_range: str = "all",
        enrich_with_intent_descriptions: bool = True,
    ) -> Dict[str, Any]:
        """
        Export training data as JSONL for Claude fine-tuning.

        Optionally looks up the Executive Intent page for each record to
        inject the original intent description into the user turn.

        Returns a dict with path, count, and validation report.
        """
        records = await self._fetch_training_records(
            time_range=time_range, agent_name=agent_name
        )

        intent_descriptions: Optional[Dict[str, str]] = None
        if enrich_with_intent_descriptions:
            intent_ids = list({r.intent_id for r in records})
            intent_descriptions = await self._lookup_intent_descriptions(intent_ids)

        jsonl_path = self._exporter.export_to_jsonl(
            records=records,
            output_path=output_path,
            min_acceptance_rate=min_acceptance_rate,
            agent_name=agent_name,
            intent_descriptions=intent_descriptions,
        )

        validation = self._exporter.validate_dataset(jsonl_path)

        return {
            "path": jsonl_path,
            "validation": validation.model_dump(),
        }

    # -------------------------------------------------------------------------
    # Notion data fetching
    # -------------------------------------------------------------------------

    async def _fetch_training_records(
        self,
        time_range: str = "30d",
        agent_name: Optional[str] = None,
    ) -> List[TrainingRecord]:
        """
        Query DB_Training_Data and parse results into TrainingRecord objects.

        Optionally filters to a date range. Agent name filtering is applied
        post-fetch since it's stored in a related database.
        """
        days = _TIME_RANGE_DAYS.get(time_range)
        filters: List[Dict] = []

        if days is not None:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            filters.append({
                "property": "Timestamp",
                "date": {"on_or_after": cutoff},
            })

        query_params: Dict[str, Any] = {
            "database_id": settings.notion_db_training_data,
            "sorts": [{"property": "Timestamp", "direction": "descending"}],
        }
        if filters:
            query_params["filter"] = (
                filters[0] if len(filters) == 1
                else {"and": filters}
            )

        records: List[TrainingRecord] = []
        cursor: Optional[str] = None

        while True:
            if cursor:
                query_params["start_cursor"] = cursor

            try:
                response = await self.client.databases.query(**query_params)
            except Exception as e:
                logger.error(f"Notion query failed for DB_Training_Data: {e}")
                break

            for page in response.get("results", []):
                record = self._parse_training_page(page)
                if record:
                    records.append(record)

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        logger.info(f"Fetched {len(records)} training records (time_range={time_range})")

        if agent_name:
            records = [r for r in records if r.agent_name == agent_name]

        return records

    def _parse_training_page(self, page: Dict[str, Any]) -> Optional[TrainingRecord]:
        """Parse a Notion page from DB_Training_Data into a TrainingRecord."""
        try:
            props = page.get("properties", {})

            intent_id = self._get_rich_text(props, "Intent_ID")
            if not intent_id:
                return None

            timestamp_raw = props.get("Timestamp", {}).get("date", {}).get("start")
            timestamp = (
                datetime.fromisoformat(timestamp_raw)
                if timestamp_raw
                else datetime.now(timezone.utc)
            )

            acceptance_rate = props.get("Acceptance_Rate", {}).get("number", 0) or 0
            # Stored as 0–100 in Notion, normalize to 0–1
            if acceptance_rate > 1:
                acceptance_rate = acceptance_rate / 100.0

            modifications_count = props.get("Modifications_Count", {}).get("number", 0) or 0

            modifications_text = self._get_rich_text(props, "Modifications")
            modifications = (
                [m.strip() for m in modifications_text.splitlines() if m.strip()]
                if modifications_text
                else []
            )

            original_plan = self._parse_json_property(props, "Original_Plan")
            final_plan = self._parse_json_property(props, "Final_Plan")

            return TrainingRecord(
                notion_page_id=page["id"],
                intent_id=intent_id,
                timestamp=timestamp,
                acceptance_rate=acceptance_rate,
                modifications_count=modifications_count,
                modifications=modifications,
                original_plan=original_plan,
                final_plan=final_plan,
                agent_name=None,  # enriched separately if needed
            )

        except Exception as e:
            logger.warning(f"Failed to parse training page {page.get('id', '?')}: {e}")
            return None

    async def _lookup_intent_descriptions(
        self,
        intent_ids: List[str],
    ) -> Dict[str, str]:
        """
        Look up the title/description of each Executive Intent by ID.
        Returns a mapping of intent_id → description string.
        """
        descriptions: Dict[str, str] = {}

        for intent_id in intent_ids:
            try:
                page = await self.client.pages.retrieve(page_id=intent_id)
                props = page.get("properties", {})

                title_parts = props.get("Name", {}).get("title", [])
                title = title_parts[0]["text"]["content"] if title_parts else ""

                desc_parts = props.get("Description", {}).get("rich_text", [])
                description = desc_parts[0]["text"]["content"] if desc_parts else ""

                descriptions[intent_id] = (
                    f"{title}\n\n{description}".strip() if description else title
                )

            except Exception as e:
                logger.debug(f"Could not look up intent {intent_id[:8]}: {e}")

        return descriptions

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _build_agent_summary(
        self,
        agent_name: str,
        records: List[TrainingRecord],
        time_range: str,
    ) -> AgentPerformanceSummary:
        rates = [r.acceptance_rate for r in records]
        avg = sum(rates) / len(rates) if rates else 0.0

        # Chronological trend (most recent last)
        sorted_records = sorted(records, key=lambda r: r.timestamp)
        trend = [round(r.acceptance_rate, 3) for r in sorted_records]

        # Count modification type frequencies
        mod_type_counter: Dict[str, int] = {}
        for record in records:
            for mod in record.modifications:
                if mod.startswith("Modified"):
                    mod_type_counter["modified"] = mod_type_counter.get("modified", 0) + 1
                elif mod.startswith("Added"):
                    mod_type_counter["added"] = mod_type_counter.get("added", 0) + 1
                elif mod.startswith("Removed"):
                    mod_type_counter["removed"] = mod_type_counter.get("removed", 0) + 1

        low_acceptance = sum(1 for r in rates if r < 0.7)

        return AgentPerformanceSummary(
            agent_name=agent_name,
            time_range=time_range,
            total_settlements=len(records),
            avg_acceptance_rate=round(avg, 3),
            min_acceptance_rate=round(min(rates), 3) if rates else 0.0,
            max_acceptance_rate=round(max(rates), 3) if rates else 0.0,
            acceptance_trend=trend,
            common_modification_types=mod_type_counter,
            low_acceptance_count=low_acceptance,
        )

    @staticmethod
    def _avg_acceptance(records: List[TrainingRecord]) -> float:
        if not records:
            return 0.0
        return sum(r.acceptance_rate for r in records) / len(records)

    @staticmethod
    def _get_rich_text(props: Dict[str, Any], key: str) -> str:
        items = props.get(key, {}).get("rich_text", [])
        return items[0]["text"]["content"] if items else ""

    @staticmethod
    def _parse_json_property(props: Dict[str, Any], key: str) -> Dict[str, Any]:
        """Parse a Notion rich_text property that contains JSON."""
        raw = TrainingAnalytics._get_rich_text(props, key)
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"raw_text": raw}
