from typing import Optional, Dict
from datetime import datetime, timedelta
from anthropic import AsyncAnthropic
from notion_client import AsyncClient
from loguru import logger
import json

from config.settings import settings
from app.models import AreaAssignment


class AreasManager:
    """Manages Area detection and assignment for workflow entities"""

    def __init__(self):
        self.claude = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.notion = AsyncClient(auth=settings.notion_api_key)
        self.area_cache: Dict[str, tuple] = {}  # {area_name: (area_id, timestamp)}
        self.cache_ttl = timedelta(hours=1)

    async def detect_area(self, intent_description: str) -> AreaAssignment:
        """
        Detect Area from intent description using Claude.
        Returns AreaAssignment with area_name and confidence.
        """
        logger.info("Detecting area classification from intent description")

        prompt = f"""Analyze the following intent and classify it into ONE of these life/work areas:

AVAILABLE AREAS:
- Work: Career, business, professional projects, income generation
- Health: Fitness, nutrition, medical, wellness, mental health
- Finance: Investments, savings, budgeting, financial planning, taxes
- Relationships: Family, friends, networking, partnerships
- Learning: Education, skill development, courses, personal growth
- Home: Housing, household management, living environment
- Hobbies: Recreation, creative pursuits, entertainment
- Travel: Trips, vacations, exploration
- Community: Volunteering, social causes, local involvement
- Fraternity: Social, Rush, Risk, Philo, PR, Brotherhood

INTENT:
{intent_description}

Respond with ONLY valid JSON (no markdown, no backticks):
{{
  "area": "Work",
  "confidence": 0.95
}}

Choose the MOST relevant area. Confidence should be 0.0-1.0 based on how clearly the intent fits that category."""

        try:
            response = await self.claude.messages.create(
                model=settings.anthropic_model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # Clean potential markdown
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            area_assignment = AreaAssignment(
                area_name=result["area"],
                confidence=result["confidence"]
            )

            logger.info(f"Classified into area: {area_assignment.area_name} (confidence: {area_assignment.confidence})")
            return area_assignment

        except Exception as e:
            logger.error(f"Error detecting area: {e}")
            # Graceful fallback - return "Work" as default with low confidence
            return AreaAssignment(
                area_name="Work",
                confidence=0.3
            )

    async def get_area_id(self, area_name: str) -> Optional[str]:
        """
        Get Area ID from Notion, with caching.
        Returns None if area doesn't exist.
        """
        # Check cache first
        if area_name in self.area_cache:
            cached_id, timestamp = self.area_cache[area_name]
            if self._is_cache_valid(timestamp):
                logger.debug(f"Cache hit for area: {area_name}")
                return cached_id
            else:
                # Cache expired, remove it
                del self.area_cache[area_name]

        # Query Notion for Area by name
        try:
            logger.info(f"Querying Notion for area: {area_name}")

            response = await self.notion.databases.query(
                database_id=settings.notion_db_areas,
                filter={
                    "property": "Name",
                    "title": {
                        "equals": area_name
                    }
                }
            )

            results = response.get("results", [])

            if not results:
                logger.warning(f"Area '{area_name}' not found in Notion")
                return None

            area_id = results[0]["id"]

            # Cache the result
            self.area_cache[area_name] = (area_id, datetime.now())

            logger.info(f"Found area '{area_name}': {area_id[:8]}")
            return area_id

        except Exception as e:
            logger.error(f"Error querying area from Notion: {e}")
            return None

    async def assign_area_to_intent(self, intent_id: str, area_id: str) -> None:
        """
        Assign Area to an Intent via relation.
        """
        try:
            logger.info(f"Assigning area {area_id[:8]} to intent {intent_id[:8]}")

            await self.notion.pages.update(
                page_id=intent_id,
                properties={
                    "Area": {
                        "relation": [{"id": area_id}]
                    }
                }
            )

            logger.success(f"Successfully assigned area to intent {intent_id[:8]}")

        except Exception as e:
            logger.error(f"Error assigning area to intent: {e}")
            raise

    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cached entry is still valid"""
        return datetime.now() - timestamp < self.cache_ttl
