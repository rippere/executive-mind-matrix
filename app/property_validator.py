"""
Property Validator - Prevents redundant property creation
Run this before adding new properties to any database
"""

from notion_client import AsyncClient
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import json
import os


class PropertyValidator:
    """Validates property additions to prevent redundancy"""

    def __init__(self, notion_client: AsyncClient):
        self.client = notion_client

    async def check_before_create(
        self,
        database_id: str,
        database_name: str,
        proposed_property: str,
        proposed_type: str,
        intended_use: str
    ) -> Dict[str, any]:
        """
        Pre-flight check before creating a new property.

        Returns:
            {
                "should_create": bool,
                "reason": str,
                "alternatives": List[str],
                "existing_schema": Dict[str, str]
            }
        """

        logger.info(f"Pre-flight check: '{proposed_property}' in {database_name}")

        # Get current schema
        db = await self.client.databases.retrieve(database_id=database_id)
        existing_props = db.get("properties", {})
        existing_schema = {name: prop["type"] for name, prop in existing_props.items()}

        # Check 1: Exact name match
        if proposed_property in existing_schema:
            return {
                "should_create": False,
                "reason": f"Property '{proposed_property}' already exists (type: {existing_schema[proposed_property]})",
                "alternatives": [f"Use existing: {proposed_property}"],
                "existing_schema": existing_schema
            }

        # Check 2: Similar name (fuzzy match)
        similar = self._find_similar_names(proposed_property, list(existing_schema.keys()))
        if similar:
            return {
                "should_create": False,
                "reason": f"Similar properties found: {', '.join(similar)}",
                "alternatives": [f"Consider using: {prop}" for prop in similar],
                "existing_schema": existing_schema
            }

        # Check 3: Semantic overlap (keyword matching)
        semantic_matches = self._find_semantic_matches(
            intended_use,
            existing_schema
        )
        if semantic_matches:
            return {
                "should_create": False,
                "reason": f"Existing properties can serve this purpose",
                "alternatives": semantic_matches,
                "existing_schema": existing_schema
            }

        # Passed all checks
        return {
            "should_create": True,
            "reason": "No conflicts or alternatives found",
            "alternatives": [],
            "existing_schema": existing_schema
        }

    def _find_similar_names(
        self,
        proposed: str,
        existing: List[str],
        threshold: float = 0.7
    ) -> List[str]:
        """Find properties with similar names"""

        similar = []
        proposed_lower = proposed.lower().replace("_", " ")

        for existing_prop in existing:
            existing_lower = existing_prop.lower().replace("_", " ")

            # Check if words overlap
            proposed_words = set(proposed_lower.split())
            existing_words = set(existing_lower.split())

            overlap = len(proposed_words & existing_words)
            total_unique = len(proposed_words | existing_words)

            if total_unique > 0 and (overlap / total_unique) >= threshold:
                similar.append(existing_prop)

        return similar

    def _find_semantic_matches(
        self,
        intended_use: str,
        existing_schema: Dict[str, str]
    ) -> List[str]:
        """Find existing properties that might serve the intended purpose"""

        matches = []
        keywords = intended_use.lower().split()

        for prop_name, prop_type in existing_schema.items():
            prop_lower = prop_name.lower()

            # Check if any keyword appears in property name
            if any(keyword in prop_lower for keyword in keywords):
                matches.append(f"{prop_name} ({prop_type}) - contains keywords from intent")

        # Semantic mappings for common use cases
        semantic_map = {
            "recommendation": ["Recommended_Option", "Final_Decision"],
            "decision": ["Recommended_Option", "Decision_Made"],
            "analysis": ["Scenario_Options", "Risk_Assessment"],
            "synthesis": ["Scenario_Options", "Risk_Assessment"],
            "consensus": ["Recommended_Option"],
            "agent": ["Agent", "Agent_Persona"],
            "status": ["Status", "Approval_Status"],
        }

        for keyword, alternatives in semantic_map.items():
            if keyword in intended_use.lower():
                for alt in alternatives:
                    if alt in existing_schema and f"{alt}" not in [m.split()[0] for m in matches]:
                        matches.append(f"{alt} ({existing_schema[alt]}) - semantically related")

        return matches

    def log_property_addition(
        self,
        database_name: str,
        property_name: str,
        property_type: str,
        justification: str
    ):
        """Log when a new property is added (audit trail)"""

        # Create log entry with ISO timestamp
        log_entry = {
            "database": database_name,
            "property": property_name,
            "type": property_type,
            "justification": justification,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.warning(f"NEW PROPERTY CREATED: {log_entry}")

        # Write to structured JSONL log file for audit trail
        try:
            log_file = "logs/property_changes.jsonl"

            # Ensure logs directory exists
            os.makedirs("logs", exist_ok=True)

            # Append to JSONL file (one JSON object per line)
            with open(log_file, mode='a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")

            logger.debug(f"Property addition logged to {log_file}")

        except Exception as e:
            logger.error(f"Error writing property change to log file: {e}")
            # Don't raise - logging failure shouldn't break property creation

        return log_entry


async def validate_property_creation(
    client: AsyncClient,
    database_id: str,
    database_name: str,
    proposed_property: str,
    proposed_type: str,
    intended_use: str
) -> bool:
    """
    Convenience function to validate before creating property.

    Usage:
        from app.property_validator import validate_property_creation

        should_create = await validate_property_creation(
            client=notion_client,
            database_id=settings.notion_db_action_pipes,
            database_name="Action Pipes",
            proposed_property="New_Field",
            proposed_type="rich_text",
            intended_use="Store agent recommendations"
        )

        if should_create:
            # Create the property
        else:
            # Use existing property instead
    """

    validator = PropertyValidator(client)
    result = await validator.check_before_create(
        database_id=database_id,
        database_name=database_name,
        proposed_property=proposed_property,
        proposed_type=proposed_type,
        intended_use=intended_use
    )

    if not result["should_create"]:
        logger.error(f"Property creation blocked: {result['reason']}")
        logger.info(f"Alternatives: {result['alternatives']}")

    return result["should_create"]
