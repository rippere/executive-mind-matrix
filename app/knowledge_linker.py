from typing import List, Optional
from anthropic import AsyncAnthropic
from notion_client import AsyncClient
from loguru import logger
import json
import asyncio
from difflib import SequenceMatcher

from config.settings import settings
from app.models import ConceptMatch


class KnowledgeLinker:
    """Extracts concepts and links them to Knowledge Nodes"""

    def __init__(self):
        self.claude = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.notion = AsyncClient(auth=settings.notion_api_key)

    async def extract_concepts(self, text: str, max_concepts: int = 5) -> List[ConceptMatch]:
        """
        Extract key concepts from text using Claude.
        Returns top N concepts with types and confidence.
        """
        logger.info(f"Extracting up to {max_concepts} concepts from text")

        prompt = f"""Analyze this text and extract the most important concepts, entities, or knowledge assets mentioned.

TEXT:
{text}

Extract up to {max_concepts} key concepts. For each concept, classify its type:
- Entity_Person: People, individuals
- Entity_Company: Organizations, companies, institutions
- Knowledge_Asset: Technologies, methodologies, frameworks, tools
- System_Component: Systems, platforms, infrastructure

Respond with ONLY valid JSON (no markdown):
{{
  "concepts": [
    {{"concept": "React", "node_type": "Knowledge_Asset", "confidence": 0.95}},
    {{"concept": "Tesla", "node_type": "Entity_Company", "confidence": 0.90}}
  ]
}}

Only include concepts that are important and worth tracking. Ignore common words."""

        try:
            response = await self.claude.messages.create(
                model=settings.anthropic_model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # Clean markdown if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            concepts = [ConceptMatch(**c) for c in result["concepts"]]

            logger.info(f"Extracted {len(concepts)} concepts: {[c.concept for c in concepts]}")
            return concepts

        except Exception as e:
            logger.error(f"Error extracting concepts: {e}")
            return []  # Graceful fallback

    async def find_or_create_node(self, concept: ConceptMatch) -> Optional[str]:
        """
        Find existing node or create new one.
        Uses fuzzy matching to avoid duplicates.
        Returns node_id, or None if creation fails.
        """
        try:
            logger.info(f"Finding or creating node for concept: {concept.concept}")

            # Step 1: Query all nodes from DB_Nodes
            response = await self.notion.databases.query(
                database_id=settings.notion_db_nodes
            )

            # Step 2: Check for exact match (case-insensitive)
            for page in response.get("results", []):
                existing_name = self._extract_title(page)
                if existing_name and existing_name.lower() == concept.concept.lower():
                    logger.info(f"Exact match found: '{existing_name}' for '{concept.concept}'")
                    return page["id"]

            # Step 3: Check for fuzzy match (95% threshold)
            for page in response.get("results", []):
                existing_name = self._extract_title(page)
                if existing_name:
                    similarity = self._fuzzy_match(existing_name, concept.concept)
                    if similarity >= 0.95:
                        logger.info(f"Fuzzy match: '{existing_name}' ≈ '{concept.concept}' ({similarity:.2%})")
                        return page["id"]

            # Step 4: Create new node
            logger.info(f"Creating new node: '{concept.concept}' (type: {concept.node_type})")
            new_page = await self.notion.pages.create(
                parent={"database_id": settings.notion_db_nodes},
                properties={
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": concept.concept
                                }
                            }
                        ]
                    }
                }
            )

            logger.success(f"Created new node: '{concept.concept}' ({new_page['id'][:8]})")
            return new_page["id"]

        except Exception as e:
            logger.error(f"Error finding/creating node for '{concept.concept}': {e}")
            return None  # Graceful fallback - skip this node

    async def link_nodes_to_intent(self, intent_id: str, node_ids: List[str]) -> None:
        """
        Link nodes to intent via Related_Nodes relation.
        Batch updates all nodes at once.
        """
        if not node_ids:
            logger.warning("No node IDs provided to link")
            return

        try:
            logger.info(f"Linking {len(node_ids)} nodes to intent {intent_id[:8]}")

            await self.notion.pages.update(
                page_id=intent_id,
                properties={
                    "Routed_to_Node": {
                        "relation": [{"id": node_id} for node_id in node_ids]
                    }
                }
            )

            logger.success(f"Successfully linked {len(node_ids)} nodes to intent {intent_id[:8]}")

        except Exception as e:
            logger.error(f"Error linking nodes to intent: {e}")
            # Don't raise - graceful degradation

    async def suggest_related_nodes(self, intent_id: str) -> List[str]:
        """
        STUB: Suggest related nodes based on existing links.
        Can be implemented later for enhanced knowledge discovery.
        """
        logger.debug(f"suggest_related_nodes not yet implemented for intent {intent_id[:8]}")
        return []

    async def process_intent_knowledge(self, intent_id: str, intent_description: str) -> List[str]:
        """
        Complete knowledge linking workflow for an intent.
        Extracts concepts, creates/finds nodes, and links them.
        Returns list of node IDs that were linked.
        """
        logger.info(f"Processing knowledge linking for intent {intent_id[:8]}")

        # Step 1: Extract concepts
        concepts = await self.extract_concepts(intent_description)

        if not concepts:
            logger.warning("No concepts extracted, skipping knowledge linking")
            return []

        # Step 2: Find or create nodes concurrently
        logger.info(f"Finding or creating {len(concepts)} nodes concurrently")
        node_id_tasks = [self.find_or_create_node(concept) for concept in concepts]
        node_ids_results = await asyncio.gather(*node_id_tasks, return_exceptions=True)

        # Filter out None values and exceptions
        node_ids = []
        for i, result in enumerate(node_ids_results):
            if isinstance(result, Exception):
                logger.error(f"Exception creating node for '{concepts[i].concept}': {result}")
            elif result is not None:
                node_ids.append(result)
            else:
                logger.warning(f"Failed to create node for '{concepts[i].concept}'")

        if not node_ids:
            logger.warning("No nodes were successfully created/found")
            return []

        # Step 3: Link nodes to intent
        await self.link_nodes_to_intent(intent_id, node_ids)

        logger.success(f"Knowledge linking complete: {len(node_ids)} nodes linked to intent {intent_id[:8]}")
        return node_ids

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

    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings.
        Returns 0.0-1.0 (1.0 = identical)
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
