from typing import List, Optional
from notion_client import AsyncClient
from loguru import logger
import asyncio

from config.settings import settings
from app.models import TaskSpawnResult, ProjectDetails, AgentAnalysis


class TaskSpawner:
    """Automatically spawns tasks and projects from Executive Intents"""

    def __init__(self):
        self.notion = AsyncClient(auth=settings.notion_api_key)

    async def spawn_tasks_from_intent(
        self,
        intent_id: str,
        task_template: List[str],
        area_id: Optional[str] = None
    ) -> TaskSpawnResult:
        """
        Create tasks from template list.
        Returns TaskSpawnResult with created task IDs.
        """
        logger.info(f"Spawning {len(task_template)} tasks from intent {intent_id[:8]}")

        if not task_template:
            logger.warning("Empty task template provided, no tasks to create")
            return TaskSpawnResult(
                task_ids=[],
                project_id=None,
                area_id=area_id or "",
                tasks_created=0,
                project_created=False
            )

        # Create tasks concurrently using asyncio.gather
        task_creation_coros = [
            self._create_task(
                description=task_description,
                intent_id=intent_id,
                area_id=area_id
            )
            for task_description in task_template
        ]

        task_results = await asyncio.gather(*task_creation_coros, return_exceptions=True)

        # Filter successful task IDs from results
        task_ids = []
        for i, result in enumerate(task_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to create task '{task_template[i]}': {result}")
            elif result is not None:
                task_ids.append(result)
            else:
                logger.warning(f"Task creation returned None for '{task_template[i]}'")

        logger.success(f"Successfully created {len(task_ids)}/{len(task_template)} tasks")

        # Detect if project is needed
        project_created = False
        project_id = None

        if self.detect_project_need(task_ids):
            logger.info(f"Project creation needed for {len(task_ids)} tasks")
            try:
                # Retrieve intent details for project name
                intent_page = await self.notion.pages.retrieve(page_id=intent_id)
                intent_title = self._extract_title(intent_page)

                project_details = ProjectDetails(
                    name=f"Project: {intent_title}" if intent_title else "Auto-Generated Project",
                    description="Auto-generated project from Executive Intent",
                    task_ids=task_ids,
                    source_intent_id=intent_id,
                    area_id=area_id
                )

                project_id = await self.spawn_project_from_intent(intent_id, project_details)

                # Link tasks to project
                await self.link_tasks_to_project(project_id, task_ids)

                project_created = True
                logger.success(f"Created project {project_id[:8]} and linked {len(task_ids)} tasks")

            except Exception as e:
                logger.error(f"Failed to create project, tasks remain unlinked: {e}")
                # Tasks still exist - graceful degradation

        return TaskSpawnResult(
            task_ids=task_ids,
            project_id=project_id,
            area_id=area_id or "",
            tasks_created=len(task_ids),
            project_created=project_created
        )

    async def _create_task(
        self,
        description: str,
        intent_id: str,
        area_id: Optional[str] = None
    ) -> str:
        """
        Create a single task in DB_Tasks.
        Returns task_id.
        """
        try:
            logger.debug(f"Creating task: '{description[:50]}...'")

            properties = {
                "Name": {
                    "title": [{"text": {"content": description}}]
                },
                "Status": {
                    "status": {"name": "Not started"}
                },
                "Source Intent": {
                    "relation": [{"id": intent_id}]
                },
                "Auto Generated": {
                    "checkbox": True
                }
            }

            # Only add Area if provided
            if area_id:
                properties["Area"] = {"relation": [{"id": area_id}]}

            response = await self.notion.pages.create(
                parent={"database_id": settings.notion_db_tasks},
                properties=properties
            )

            task_id = response["id"]
            logger.debug(f"Created task {task_id[:8]}: '{description[:50]}...'")
            return task_id

        except Exception as e:
            logger.error(f"Error creating task '{description[:50]}...': {e}")
            raise  # Re-raise to be caught by gather

    async def spawn_project_from_intent(
        self,
        intent_id: str,
        project_details: ProjectDetails
    ) -> str:
        """
        Create project in DB_Projects.
        Returns project_id.
        """
        try:
            logger.info(f"Creating project: '{project_details.name}'")

            properties = {
                "Name": {
                    "title": [{"text": {"content": project_details.name}}]
                },
                "Source Intent": {
                    "relation": [{"id": intent_id}]
                },
                "Status": {
                    "select": {"name": "Planning"}
                }
            }

            # Optional: add description
            if project_details.description:
                properties["Description"] = {
                    "rich_text": [{"text": {"content": project_details.description}}]
                }

            # Optional: add area
            if project_details.area_id:
                properties["Area"] = {"relation": [{"id": project_details.area_id}]}

            response = await self.notion.pages.create(
                parent={"database_id": settings.notion_db_projects},
                properties=properties
            )

            project_id = response["id"]
            logger.success(f"Created project {project_id[:8]}: '{project_details.name}'")
            return project_id

        except Exception as e:
            logger.error(f"Error creating project '{project_details.name}': {e}")
            raise

    def detect_project_need(self, task_ids: List[str]) -> bool:
        """
        Simple heuristic: 3+ tasks = project needed.
        Can be enhanced later with AI-based detection.
        """
        needs_project = len(task_ids) >= 3
        if needs_project:
            logger.info(f"Project recommended: {len(task_ids)} tasks detected")
        return needs_project

    async def link_tasks_to_project(self, project_id: str, task_ids: List[str]) -> None:
        """
        Link tasks to project via Project relation.
        Updates all tasks concurrently.
        """
        if not task_ids:
            logger.warning("No task IDs provided to link to project")
            return

        try:
            logger.info(f"Linking {len(task_ids)} tasks to project {project_id[:8]}")

            # Update all tasks concurrently
            update_coros = [
                self.notion.pages.update(
                    page_id=task_id,
                    properties={
                        "Project": {
                            "relation": [{"id": project_id}]
                        }
                    }
                )
                for task_id in task_ids
            ]

            results = await asyncio.gather(*update_coros, return_exceptions=True)

            # Count successes and failures
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            failure_count = len(results) - success_count

            if failure_count > 0:
                logger.warning(f"Linked {success_count}/{len(task_ids)} tasks to project (partial success)")
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to link task {task_ids[i][:8]}: {result}")
            else:
                logger.success(f"Successfully linked all {len(task_ids)} tasks to project {project_id[:8]}")

        except Exception as e:
            logger.error(f"Error linking tasks to project: {e}")
            # Don't raise - graceful degradation

    async def process_intent_tasks(
        self,
        intent_id: str,
        analysis: AgentAnalysis,
        area_id: Optional[str] = None
    ) -> TaskSpawnResult:
        """
        Complete task spawning workflow for an intent.
        Spawns tasks, creates project if needed, links everything.
        Returns TaskSpawnResult with full details.
        """
        logger.info(f"Processing task spawning workflow for intent {intent_id[:8]}")

        # Step 1: Spawn tasks from analysis template
        task_result = await self.spawn_tasks_from_intent(
            intent_id,
            analysis.task_generation_template,
            area_id
        )

        logger.success(
            f"Task spawning complete for intent {intent_id[:8]}: "
            f"{task_result.tasks_created} tasks, "
            f"project_created={task_result.project_created}"
        )

        return task_result

    def _extract_title(self, page: dict) -> Optional[str]:
        """
        Extract title text from a Notion page.
        Returns None if title cannot be extracted.
        """
        try:
            title_property = page.get("properties", {}).get("Name", {})
            title_array = title_property.get("title", [])

            if title_array and len(title_array) > 0:
                return title_array[0].get("text", {}).get("content", "")

            return None

        except Exception as e:
            logger.debug(f"Error extracting title from page: {e}")
            return None
