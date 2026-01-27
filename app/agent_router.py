from typing import Dict, Any, List, Optional
from datetime import datetime
from anthropic import AsyncAnthropic
from notion_client import AsyncClient
from loguru import logger
import json

from config.settings import settings
from app.models import (
    AgentAnalysis, AgentPersona, DialecticOutput,
    ScenarioOption, RiskLevel
)


class AgentRouter:
    """
    Adversarial Agent Router implementing dialectic reasoning.
    Routes intents to competing AI personas, then synthesizes their outputs.
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.notion = AsyncClient(auth=settings.notion_api_key)
        self.model = settings.anthropic_model

        # Agent system prompts (from your documentation)
        self.agent_prompts = {
            AgentPersona.ENTREPRENEUR: """You are The Entrepreneur, a growth-focused operator in a personal Aladdin system.

FOCUS: Revenue generation, audience reach, and scalability. Your job is to analyze opportunities that move the needle toward $100k/mo.

When evaluating options, prioritize:
- Revenue potential (direct and indirect monetization)
- Scalability (can this 10x without linear resource increase?)
- Speed to market (how fast can we launch and iterate?)
- Competitive moats (defensibility, unique advantages)
- Customer acquisition efficiency (CAC, LTV)

Red flags to call out:
- Low-margin businesses (<30% gross margin)
- Over-reliance on single customer or channel
- High operational complexity with low automation potential
- Commoditized offerings with no differentiation

Provide 3 distinct strategic options with clear revenue projections.""",

            AgentPersona.QUANT: """You are The Quant, a quantitative analyst in a personal Aladdin system.

FOCUS: Financial decisions, portfolio optimization, risk-adjusted returns. You evaluate using mathematical rigor and probabilistic thinking.

When evaluating options, calculate:
- Expected Value (EV = Probability × Outcome for each scenario)
- Downside protection (maximum loss in worst-case scenario)
- Sharpe ratio equivalent (return per unit of risk)
- Correlation with existing portfolio/income streams
- Time horizon and compounding effects
- Kelly Criterion for position sizing (where applicable)

Use Euclidean decision models:
- Map options in risk/return space
- Calculate distance from optimal frontier
- Identify dominated strategies (worse on all dimensions)

Terminology:
- "Alpha": Returns above market/benchmark
- "Beta": Correlation with broader market
- "Drawdown": Peak-to-trough decline
- "Volatility": Standard deviation of returns

Provide 3 options with quantitative risk/reward profiles.""",

            AgentPersona.AUDITOR: """You are The Auditor, the risk and compliance officer in a personal Aladdin system.

FOCUS: Governance, ethical alignment, mission integrity, long-term reputation. You are the "should we?" agent, not just the "can we?" agent.

When evaluating options, check against:
- Mission alignment: Does this serve the 2026 vision?
- Ethical considerations: Impact on others, sustainability, social good
- Legal/regulatory compliance: Licensing, taxes, disclosure requirements
- Long-term reputation risk: How does this look in 5 years?
- Dependency risk: Does this compromise autonomy or create lock-in?
- Reversibility: Can we undo this decision if it goes wrong?

Automatic REJECT signals (flag these prominently):
- Violates stated core values
- Creates existential risk (financial, legal, reputational)
- Requires unethical behavior or regulatory violations
- Locks into non-reversible dependencies

For financial decisions, validate:
- Tax implications are understood
- Legal structure is appropriate
- Regulatory requirements are met

Provide 3 options with clear pass/fail governance assessment."""
        }

    async def classify_intent(self, content: str) -> Dict[str, Any]:
        """
        Classify incoming intent as strategic, operational, or reference.
        Also assigns appropriate agent and risk level.
        """

        prompt = f"""Triage this input from my system inbox:

{content}

Classify as:
- 'strategic' (requires decision analysis, multiple options, or high impact > $1000)
- 'operational' (clear next action, can execute immediately)
- 'reference' (knowledge to store for later)

Respond ONLY with valid JSON (no markdown):
{{
  "type": "strategic|operational|reference",
  "title": "...",
  "agent": "The Entrepreneur|The Quant|The Auditor",
  "risk": "Low|Medium|High",
  "impact": 1-10,
  "next_action": "..." (if operational),
  "rationale": "Why this classification"
}}"""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text
            classification = json.loads(result_text)

            logger.info(f"Classified intent as: {classification['type']}")
            return classification

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            # Fallback classification - default to strategic so it goes to Executive Intents for manual review
            return {
                "type": "strategic",
                "title": "⚠️ NEEDS MANUAL REVIEW - Classification Failed",
                "agent": "The Entrepreneur",
                "risk": "Medium",
                "impact": 5,
                "rationale": f"Classification failed: {e}. Defaulting to strategic for manual review."
            }

    async def analyze_with_agent(
        self,
        agent: AgentPersona,
        intent_title: str,
        intent_description: str,
        success_criteria: str = "",
        projected_impact: int = 5
    ) -> AgentAnalysis:
        """
        Route intent to specific agent for analysis.
        Returns structured scenario options.
        """

        logger.info(f"Routing to agent: {agent.value}")

        system_prompt = self.agent_prompts[agent]

        user_prompt = f"""INTENT DETAILS:
Title: {intent_title}
Description: {intent_description}
Success Criteria: {success_criteria or "Not specified"}
Projected Impact: {projected_impact}/10

TASK: Analyze this intent and provide 3 strategic options. You MUST respond with ONLY valid JSON, no other text.

REQUIRED JSON FORMAT (copy this structure exactly):
{{
  "scenario_options": [
    {{
      "option": "A",
      "description": "Brief 2-3 sentence description",
      "pros": ["Pro 1", "Pro 2", "Pro 3"],
      "cons": ["Con 1", "Con 2", "Con 3"],
      "risk": 2,
      "impact": 8
    }},
    {{
      "option": "B",
      "description": "Brief 2-3 sentence description",
      "pros": ["Pro 1", "Pro 2", "Pro 3"],
      "cons": ["Con 1", "Con 2", "Con 3"],
      "risk": 3,
      "impact": 7
    }},
    {{
      "option": "C",
      "description": "Brief 2-3 sentence description",
      "pros": ["Pro 1", "Pro 2", "Pro 3"],
      "cons": ["Con 1", "Con 2", "Con 3"],
      "risk": 5,
      "impact": 9
    }}
  ],
  "recommended_option": "A",
  "recommendation_rationale": "One paragraph explaining why this option is best",
  "risk_assessment": "One paragraph assessing overall risks",
  "required_resources": {{
    "time": "X hours/week for Y weeks",
    "money": "$X total budget",
    "tools": ["Tool 1", "Tool 2"],
    "people": ["Role needed"]
  }},
  "task_generation_template": ["Task 1", "Task 2", "Task 3"]
}}

IMPORTANT: Respond with ONLY the JSON object above. No explanations, no markdown, just pure JSON."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            result_text = response.content[0].text

            # Handle potential markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            analysis_dict = json.loads(result_text)
            analysis = AgentAnalysis(**analysis_dict)

            logger.info(f"{agent.value} analysis complete: recommends Option {analysis.recommended_option}")
            return analysis

        except Exception as e:
            logger.error(f"Error getting {agent.value} analysis: {e}")
            raise

    async def dialectic_flow(
        self,
        intent_id: str,
        intent_title: str,
        intent_description: str,
        success_criteria: str = "",
        projected_impact: int = 5
    ) -> DialecticOutput:
        """
        ADVERSARIAL DIALECTIC FLOW:
        1. Run Growth agent (Entrepreneur)
        2. Run Risk agent (Auditor)
        3. Synthesize their competing perspectives
        4. Return unified recommendation with conflict analysis
        """

        logger.info(f"Starting dialectic flow for intent {intent_id[:8]}")

        # 🛡️ Initialize variables to None for safe fallback
        growth_analysis = None
        risk_analysis = None

        try:
            # Phase 1: Get Growth perspective
            growth_analysis = await self.analyze_with_agent(
                AgentPersona.ENTREPRENEUR,
                intent_title,
                intent_description,
                success_criteria,
                projected_impact
            )

            # Phase 2: Get Risk perspective
            risk_analysis = await self.analyze_with_agent(
                AgentPersona.AUDITOR,
                intent_title,
                intent_description,
                success_criteria,
                projected_impact
            )

            # Phase 3: Synthesize with meta-prompt
            synthesis_prompt = f"""You are a strategic synthesizer. Two AI agents have analyzed the same intent from opposing perspectives:

GROWTH PERSPECTIVE (The Entrepreneur):
- Recommended: Option {growth_analysis.recommended_option}
- Rationale: {growth_analysis.recommendation_rationale}
- Key pros: {growth_analysis.scenario_options[0].pros}
- Key cons: {growth_analysis.scenario_options[0].cons}

RISK PERSPECTIVE (The Auditor):
- Recommended: Option {risk_analysis.recommended_option}
- Rationale: {risk_analysis.recommendation_rationale}
- Key concerns: {risk_analysis.risk_assessment}

Your task:
1. Identify conflict points where these agents disagree
2. Synthesize a balanced recommendation that honors both perspectives
3. Suggest a path forward that maximizes upside while managing risks

Respond in JSON:
{{
  "synthesis": "2-3 sentence synthesis of both perspectives",
  "recommended_path": "Which option or hybrid approach to take",
  "conflict_points": ["Point 1 where they disagree", "Point 2", ...]
}}"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": synthesis_prompt}]
            )

            result_text = response.content[0].text

            # Clean markdown if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            synthesis_data = json.loads(result_text)

            dialectic_output = DialecticOutput(
                intent_id=intent_id,
                growth_perspective=growth_analysis,
                risk_perspective=risk_analysis,
                synthesis=synthesis_data["synthesis"],
                recommended_path=synthesis_data["recommended_path"],
                conflict_points=synthesis_data["conflict_points"]
            )

            # 🛡️ DATA ASSET PROTECTION: Save raw AI output to locked field
            # This preserves the "before" state so diff_logger can compare accurately
            await self._save_raw_ai_output(intent_id, dialectic_output)

            logger.info(f"Dialectic synthesis complete: {dialectic_output.recommended_path}")
            return dialectic_output

        except Exception as e:
            logger.error(f"Error in dialectic flow: {e}")

            # 🛡️ ROBUST FALLBACK: Safe handling even if variables are unbound
            error_context = f"Error at stage: "
            if growth_analysis is None:
                error_context += "Growth analysis failed"
            elif risk_analysis is None:
                error_context += "Risk analysis failed"
            else:
                error_context += "Synthesis failed"

            logger.error(error_context)

            # Build safe fallback output
            safe_synthesis = f"{error_context}. {str(e)}"
            safe_recommendation = "Manual review required"

            if growth_analysis:
                safe_recommendation = growth_analysis.recommended_option

            return DialecticOutput(
                intent_id=intent_id,
                growth_perspective=growth_analysis,
                risk_perspective=risk_analysis,
                synthesis=safe_synthesis,
                recommended_path=safe_recommendation,
                conflict_points=[f"System error: {error_context}"]
            )

    async def _save_raw_ai_output(
        self,
        intent_id: str,
        dialectic_output: DialecticOutput
    ):
        """
        🔒 CRITICAL: Save raw AI output to a LOCKED property in Notion.
        This prevents data loss when users edit the human-facing fields.
        The diff_logger needs this baseline to calculate accurate acceptance rates.
        """
        try:
            # Find the Action Pipe for this intent
            response = await self.notion.databases.query(
                database_id=settings.notion_db_action_pipes,
                filter={
                    "property": "Intent",
                    "relation": {
                        "contains": intent_id
                    }
                }
            )

            if not response.get("results"):
                logger.warning(f"No Action Pipe found for intent {intent_id[:8]}")
                return

            action_pipe_id = response["results"][0]["id"]

            # Serialize the raw AI output as JSON
            raw_output = {
                "growth_recommendation": dialectic_output.growth_perspective.recommended_option if dialectic_output.growth_perspective else None,
                "risk_recommendation": dialectic_output.risk_perspective.recommended_option if dialectic_output.risk_perspective else None,
                "synthesis": dialectic_output.synthesis,
                "recommended_path": dialectic_output.recommended_path,
                "conflict_points": dialectic_output.conflict_points,
                "timestamp": datetime.now().isoformat()
            }

            # Save to a read-only field (user should NOT edit this)
            await self.notion.pages.update(
                page_id=action_pipe_id,
                properties={
                    # This field stores the ORIGINAL AI output
                    # Users edit Scenario_Options and Recommended_Option
                    # But AI_Raw_Output stays locked for diff comparison
                    "AI_Raw_Output": {
                        "rich_text": [{
                            "text": {
                                "content": json.dumps(raw_output, indent=2)[:2000]
                            }
                        }]
                    }
                }
            )

            logger.info(f"Saved raw AI output for intent {intent_id[:8]}")

        except Exception as e:
            logger.error(f"Error saving raw AI output: {e}")
            # Don't raise - this is a backup/audit feature
