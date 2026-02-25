#!/usr/bin/env python3
"""
Show the actual Notion database URLs and titles for each configured database ID.
This helps verify that the environment variable mappings are correct.
"""

import asyncio
from notion_client import AsyncClient
from config.settings import settings


async def get_database_info(notion: AsyncClient, db_id: str, env_var_name: str):
    """Get database title and URL from Notion API."""
    try:
        db_info = await notion.databases.retrieve(database_id=db_id)

        # Get database title
        title_prop = db_info.get("title", [])
        title = title_prop[0]["plain_text"] if title_prop else "Untitled"

        # Get database URL
        url = db_info.get("url", f"https://notion.so/{db_id.replace('-', '')}")

        # Get property count
        properties = db_info.get("properties", {})
        prop_count = len(properties)

        return {
            "env_var": env_var_name,
            "database_id": db_id,
            "title": title,
            "url": url,
            "property_count": prop_count,
            "properties": list(properties.keys())
        }
    except Exception as e:
        return {
            "env_var": env_var_name,
            "database_id": db_id,
            "error": str(e)
        }


async def main():
    """Show mapping for all configured databases."""
    notion = AsyncClient(auth=settings.notion_api_key)

    # Database ID mappings from settings
    databases = {
        "NOTION_DB_SYSTEM_INBOX": settings.notion_db_system_inbox,
        "NOTION_DB_EXECUTIVE_INTENTS": settings.notion_db_executive_intents,
        "NOTION_DB_ACTION_PIPES": settings.notion_db_action_pipes,
        "NOTION_DB_TASKS": settings.notion_db_tasks,
        "NOTION_DB_PROJECTS": settings.notion_db_projects,
        "NOTION_DB_AREAS": settings.notion_db_areas,
        "NOTION_DB_NODES": settings.notion_db_nodes,
        "NOTION_DB_AGENT_REGISTRY": settings.notion_db_agent_registry,
        "NOTION_DB_EXECUTION_LOG": settings.notion_db_execution_log,
        "NOTION_DB_TRAINING_DATA": settings.notion_db_training_data
    }

    print("=" * 100)
    print("NOTION DATABASE MAPPING - Environment Variables → Actual Databases")
    print("=" * 100)
    print()

    # Get info for all databases
    results = []
    for env_var, db_id in databases.items():
        info = await get_database_info(notion, db_id, env_var)
        results.append(info)

    # Display results
    for info in results:
        if "error" in info:
            print(f"❌ {info['env_var']}")
            print(f"   Database ID: {info['database_id']}")
            print(f"   Error: {info['error']}")
            print()
        else:
            print(f"📋 {info['env_var']}")
            print(f"   ↳ Database ID: {info['database_id']}")
            print(f"   ↳ Title in Notion: \"{info['title']}\"")
            print(f"   ↳ URL: {info['url']}")
            print(f"   ↳ Properties: {info['property_count']}")

            # Show first few properties to help identify the database
            first_props = info['properties'][:5]
            print(f"   ↳ Sample props: {', '.join(first_props)}")
            print()

    print("=" * 100)
    print("SUSPECTED ISSUES BASED ON PROPERTY ANALYSIS:")
    print("=" * 100)
    print()

    # Analysis based on what we found earlier
    for info in results:
        if "error" not in info:
            env_var = info['env_var']
            title = info['title']
            props = set(info['properties'])

            # Check for mismatched properties
            if env_var == "NOTION_DB_TASKS":
                # Tasks should have: Name, Status, Source Intent, Area, Auto Generated
                if "Vision" in props or "Related_Intents" in props:
                    print(f"⚠️  {env_var} (\"{title}\")")
                    print(f"   This doesn't look like a Tasks database!")
                    print(f"   It has properties like: {', '.join(list(props)[:8])}")
                    print()

            elif env_var == "NOTION_DB_PROJECTS":
                # Projects should have: Name, Status, Tasks, Area
                if "Auto Generated" in props and "Priority" in props and "Energy" in props:
                    print(f"⚠️  {env_var} (\"{title}\")")
                    print(f"   This looks like a TASKS database, not Projects!")
                    print(f"   It has task-specific properties like: Auto Generated, Priority, Energy, Time Estimate")
                    print()

            elif env_var == "NOTION_DB_AREAS":
                # Areas should have: Name, Related Intents, Tasks, Projects
                if "Node_Type" in props or "Entity_Relationship" in props or "Knowledge_Tags" in props:
                    print(f"⚠️  {env_var} (\"{title}\")")
                    print(f"   This looks like a KNOWLEDGE NODES database, not Areas!")
                    print(f"   It has node-specific properties like: Node_Type, Entity_Relationship, Knowledge_Tags")
                    print()

            elif env_var == "NOTION_DB_NODES":
                # Nodes should have: Name, Content, Node_Type, Related_Intents
                if "% Accomplished" in props or "Generate plan" in props or "Strategic Outcome" in props:
                    print(f"⚠️  {env_var} (\"{title}\")")
                    print(f"   This looks like a PROJECTS database, not Knowledge Nodes!")
                    print(f"   It has project-specific properties like: % Accomplished, Generate plan, Strategic Outcome")
                    print()

    print()
    print("=" * 100)
    print("RECOMMENDED FIX:")
    print("=" * 100)
    print()
    print("Based on the property analysis, update your .env file or Railway environment variables:")
    print()

    # Find the correct mappings
    tasks_db = next((r for r in results if "Auto Generated" in r.get("properties", []) and "Priority" in r.get("properties", [])), None)
    projects_db = next((r for r in results if "% Accomplished" in r.get("properties", []) and "Generate plan" in r.get("properties", [])), None)
    nodes_db = next((r for r in results if "Node_Type" in r.get("properties", []) and "Entity_Relationship" in r.get("properties", [])), None)
    areas_db = next((r for r in results if "Vision" in r.get("properties", []) and r['env_var'] not in ["NOTION_DB_PROJECTS", "NOTION_DB_NODES"]), None)

    if tasks_db:
        print(f"NOTION_DB_TASKS={tasks_db['database_id']}")
        print(f"  # Currently mapped as: {tasks_db['env_var']}")
        print(f"  # Notion title: \"{tasks_db['title']}\"")
        print()

    if projects_db:
        print(f"NOTION_DB_PROJECTS={projects_db['database_id']}")
        print(f"  # Currently mapped as: {projects_db['env_var']}")
        print(f"  # Notion title: \"{projects_db['title']}\"")
        print()

    if areas_db:
        print(f"NOTION_DB_AREAS={areas_db['database_id']}")
        print(f"  # Currently mapped as: {areas_db['env_var']}")
        print(f"  # Notion title: \"{areas_db['title']}\"")
        print()

    if nodes_db:
        print(f"NOTION_DB_NODES={nodes_db['database_id']}")
        print(f"  # Currently mapped as: {nodes_db['env_var']}")
        print(f"  # Notion title: \"{nodes_db['title']}\"")
        print()


if __name__ == "__main__":
    asyncio.run(main())
