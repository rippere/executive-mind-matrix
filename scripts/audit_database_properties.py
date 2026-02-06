#!/usr/bin/env python3
"""
Database Property Auditor
Prevents redundant property creation by checking existing schema
"""

import asyncio
import json
from typing import Dict, List, Any
from notion_client import AsyncClient
from loguru import logger
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


class PropertyAuditor:
    """Audits Notion databases to prevent redundant property creation"""

    def __init__(self):
        self.client = AsyncClient(auth=settings.notion_api_key)
        self.databases = {
            "Executive Intents": settings.notion_db_executive_intents,
            "Action Pipes": settings.notion_db_action_pipes,
            "Agent Registry": settings.notion_db_agent_registry,
            "Execution Log": settings.notion_db_execution_log,
            "System Inbox": settings.notion_db_system_inbox,
            "Training Data": settings.notion_db_training_data,
            "Tasks": settings.notion_db_tasks,
            "Projects": settings.notion_db_projects,
            "Areas": settings.notion_db_areas,
            "Nodes": settings.notion_db_nodes
        }

    async def audit_all_databases(self) -> Dict[str, Dict[str, str]]:
        """Audit all databases and return property schemas"""

        schemas = {}

        for db_name, db_id in self.databases.items():
            try:
                logger.info(f"Auditing {db_name}...")
                schema = await self.get_database_schema(db_id)
                schemas[db_name] = schema

                print(f"\n{'='*60}")
                print(f"📊 {db_name} ({len(schema)} properties)")
                print(f"{'='*60}")

                for prop_name, prop_type in sorted(schema.items()):
                    print(f"  {prop_name:40} : {prop_type}")

            except Exception as e:
                logger.error(f"Error auditing {db_name}: {e}")

        return schemas

    async def get_database_schema(self, db_id: str) -> Dict[str, str]:
        """Get property names and types for a database"""

        db = await self.client.databases.retrieve(database_id=db_id)
        properties = db.get("properties", {})

        return {
            name: prop["type"]
            for name, prop in properties.items()
        }

    async def check_property_exists(
        self,
        db_name: str,
        property_name: str
    ) -> bool:
        """Check if a property already exists in a database"""

        db_id = self.databases.get(db_name)
        if not db_id:
            logger.error(f"Database {db_name} not found")
            return False

        schema = await self.get_database_schema(db_id)
        exists = property_name in schema

        if exists:
            logger.warning(
                f"Property '{property_name}' already exists in {db_name} "
                f"(type: {schema[property_name]})"
            )

        return exists

    async def suggest_existing_property(
        self,
        db_name: str,
        intended_use: str
    ) -> List[str]:
        """Suggest existing properties that might serve the intended use"""

        db_id = self.databases.get(db_name)
        if not db_id:
            return []

        schema = await self.get_database_schema(db_id)

        # Simple keyword matching
        keywords = intended_use.lower().split()
        suggestions = []

        for prop_name in schema.keys():
            prop_lower = prop_name.lower()
            if any(keyword in prop_lower for keyword in keywords):
                suggestions.append(f"{prop_name} ({schema[prop_name]})")

        return suggestions

    def generate_mapping_doc(self, schemas: Dict[str, Dict[str, str]]):
        """Generate markdown documentation of database schemas"""

        doc = "# Executive Mind Matrix - Database Property Map\n\n"
        doc += "**Auto-generated property reference**\n\n"
        doc += "*Use this to check existing properties before creating new ones*\n\n"

        for db_name, schema in sorted(schemas.items()):
            doc += f"## {db_name}\n\n"
            doc += f"**{len(schema)} properties**\n\n"
            doc += "| Property Name | Type | Notes |\n"
            doc += "|---------------|------|-------|\n"

            for prop_name, prop_type in sorted(schema.items()):
                # Add usage notes for key properties
                notes = ""
                if "recommendation" in prop_name.lower():
                    notes = "Agent recommendation"
                elif "status" in prop_name.lower():
                    notes = "Workflow status"
                elif "date" in prop_name.lower():
                    notes = "Temporal tracking"

                doc += f"| {prop_name} | `{prop_type}` | {notes} |\n"

            doc += "\n"

        return doc


async def main():
    """Run property audit"""

    auditor = PropertyAuditor()

    print("\n🔍 Executive Mind Matrix - Property Audit")
    print("=" * 60)

    schemas = await auditor.audit_all_databases()

    # Generate documentation
    doc = auditor.generate_mapping_doc(schemas)

    # Save to file
    doc_path = "/home/rippere/Projects/executive-mind-matrix/DATABASE_PROPERTY_MAP.md"
    with open(doc_path, "w") as f:
        f.write(doc)

    print(f"\n📄 Property map saved to: {doc_path}")

    # Check for redundancies in Action Pipes
    print(f"\n{'='*60}")
    print("🔍 Checking for Redundant Properties in Action Pipes")
    print(f"{'='*60}")

    action_pipes_schema = schemas.get("Action Pipes", {})

    redundancy_check = [
        ("Entrepreneur_Recommendation", "Could use existing: Recommended_Option"),
        ("Auditor_Recommendation", "Could use existing: Recommended_Option"),
        ("Final_Decision", "REDUNDANT - Recommended_Option already exists"),
        ("Synthesis_Summary", "Could use existing: Risk_Assessment or Scenario_Options"),
        ("Consensus", "NEW - but could be derived from comparing recommendations")
    ]

    for prop, note in redundancy_check:
        if prop in action_pipes_schema:
            print(f"  ⚠️  {prop}: {note}")

    print(f"\n{'='*60}")
    print("💡 Recommendation: Update workflow to use existing properties")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
