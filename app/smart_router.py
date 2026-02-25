"""
Smart Router - Automatic Agent Assignment

Automatically assigns the best agent persona to intents based on:
- Intent classification (strategic/operational/reference)
- Risk level
- Impact score
- Content keywords

Rules:
- Financial decisions → The Quant
- Growth/revenue opportunities → The Entrepreneur
- Governance/ethics/compliance → The Auditor
- High risk + high impact → The Auditor (safety first)
"""

from typing import Optional
from loguru import logger

from app.models import AgentPersona, RiskLevel


class SmartRouter:
    """Automatically routes intents to the best agent persona"""

    # Keywords that indicate which agent should handle the intent
    QUANT_KEYWORDS = [
        "financial", "money", "invest", "budget", "cost", "revenue", "profit",
        "roi", "valuation", "portfolio", "stock", "crypto", "fund", "capital",
        "pricing", "forecast", "metrics", "kpi", "analytics", "data"
    ]

    ENTREPRENEUR_KEYWORDS = [
        "growth", "scale", "launch", "product", "market", "customer", "user",
        "acquisition", "marketing", "brand", "sales", "expand", "opportunity",
        "partnership", "competitor", "strategy", "vision", "innovation"
    ]

    AUDITOR_KEYWORDS = [
        "compliance", "legal", "regulation", "governance", "policy", "ethics",
        "risk", "security", "privacy", "audit", "contract", "terms", "liability",
        "insurance", "tax", "lawsuit", "dispute", "fraud", "breach"
    ]

    @staticmethod
    def assign_agent(
        intent_title: str,
        intent_description: str,
        risk_level: Optional[RiskLevel] = None,
        projected_impact: Optional[int] = None
    ) -> AgentPersona:
        """
        Assign the best agent persona for an intent.

        Args:
            intent_title: Intent title
            intent_description: Full intent description
            risk_level: Risk assessment (Low/Medium/High)
            projected_impact: Impact score (1-10)

        Returns:
            AgentPersona: The assigned agent
        """

        # Combine title + description for keyword analysis
        content = f"{intent_title} {intent_description}".lower()

        # Rule 1: High risk + high impact → Always Auditor (safety first)
        if risk_level == RiskLevel.HIGH and projected_impact and projected_impact >= 8:
            logger.info(f"Smart Router: High risk + high impact → The Auditor")
            return AgentPersona.AUDITOR

        # Rule 2: Legal/compliance keywords → Always Auditor
        auditor_matches = sum(1 for keyword in SmartRouter.AUDITOR_KEYWORDS if keyword in content)
        if auditor_matches >= 2:
            logger.info(f"Smart Router: {auditor_matches} compliance keywords → The Auditor")
            return AgentPersona.AUDITOR

        # Rule 3: Financial keywords → The Quant
        quant_matches = sum(1 for keyword in SmartRouter.QUANT_KEYWORDS if keyword in content)
        if quant_matches >= 2:
            logger.info(f"Smart Router: {quant_matches} financial keywords → The Quant")
            return AgentPersona.QUANT

        # Rule 4: Growth/marketing keywords → The Entrepreneur
        entrepreneur_matches = sum(1 for keyword in SmartRouter.ENTREPRENEUR_KEYWORDS if keyword in content)
        if entrepreneur_matches >= 2:
            logger.info(f"Smart Router: {entrepreneur_matches} growth keywords → The Entrepreneur")
            return AgentPersona.ENTREPRENEUR

        # Rule 5: High impact but low risk → The Entrepreneur (opportunity)
        if projected_impact and projected_impact >= 7 and risk_level == RiskLevel.LOW:
            logger.info(f"Smart Router: High impact + low risk → The Entrepreneur")
            return AgentPersona.ENTREPRENEUR

        # Rule 6: Medium/high risk regardless of impact → The Auditor
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
            logger.info(f"Smart Router: {risk_level} risk → The Auditor")
            return AgentPersona.AUDITOR

        # Rule 7: Tie-breaker based on keyword counts
        max_matches = max(quant_matches, entrepreneur_matches, auditor_matches)

        if max_matches > 0:
            if quant_matches == max_matches:
                logger.info(f"Smart Router: Most financial keywords → The Quant")
                return AgentPersona.QUANT
            elif entrepreneur_matches == max_matches:
                logger.info(f"Smart Router: Most growth keywords → The Entrepreneur")
                return AgentPersona.ENTREPRENEUR
            else:
                logger.info(f"Smart Router: Most compliance keywords → The Auditor")
                return AgentPersona.AUDITOR

        # Default: The Entrepreneur (optimistic default for general strategic decisions)
        logger.info(f"Smart Router: No strong signals → The Entrepreneur (default)")
        return AgentPersona.ENTREPRENEUR

    @staticmethod
    def explain_assignment(
        agent: AgentPersona,
        intent_title: str,
        intent_description: str,
        risk_level: Optional[RiskLevel] = None,
        projected_impact: Optional[int] = None
    ) -> str:
        """
        Generate human-readable explanation for why an agent was assigned.

        Returns:
            str: Explanation text
        """

        content = f"{intent_title} {intent_description}".lower()

        # Count keyword matches
        quant_count = sum(1 for kw in SmartRouter.QUANT_KEYWORDS if kw in content)
        entrepreneur_count = sum(1 for kw in SmartRouter.ENTREPRENEUR_KEYWORDS if kw in content)
        auditor_count = sum(1 for kw in SmartRouter.AUDITOR_KEYWORDS if kw in content)

        if agent == AgentPersona.QUANT:
            return (
                f"**The Quant** was assigned because this intent involves financial analysis. "
                f"Detected {quant_count} financial keywords (e.g., 'investment', 'budget', 'ROI'). "
                f"The Quant specializes in risk-adjusted quantitative analysis."
            )
        elif agent == AgentPersona.ENTREPRENEUR:
            if entrepreneur_count >= 2:
                return (
                    f"**The Entrepreneur** was assigned because this intent focuses on growth opportunities. "
                    f"Detected {entrepreneur_count} growth keywords (e.g., 'launch', 'scale', 'market'). "
                    f"The Entrepreneur specializes in revenue-generating strategies."
                )
            else:
                return (
                    f"**The Entrepreneur** was assigned as the default strategic advisor. "
                    f"This persona is optimistic and focuses on execution and opportunity. "
                    f"Override if you need risk-focused or quantitative analysis."
                )
        elif agent == AgentPersona.AUDITOR:
            if risk_level == RiskLevel.HIGH and projected_impact and projected_impact >= 8:
                return (
                    f"**The Auditor** was assigned due to high risk + high impact ({projected_impact}/10). "
                    f"For critical decisions with significant downside, The Auditor ensures compliance "
                    f"and long-term sustainability."
                )
            elif auditor_count >= 2:
                return (
                    f"**The Auditor** was assigned because this intent involves governance or compliance. "
                    f"Detected {auditor_count} compliance keywords (e.g., 'legal', 'policy', 'risk'). "
                    f"The Auditor specializes in ethical and regulatory considerations."
                )
            elif risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
                return (
                    f"**The Auditor** was assigned due to {risk_level.value} risk level. "
                    f"The Auditor takes a conservative, risk-aware approach to protect against downsides."
                )
            else:
                return (
                    f"**The Auditor** was assigned to provide a cautious perspective. "
                    f"This persona focuses on compliance, governance, and risk mitigation."
                )

        return f"**{agent.value}** was assigned based on intent characteristics."

    @staticmethod
    def suggest_alternative_agent(
        assigned_agent: AgentPersona,
        risk_level: Optional[RiskLevel] = None,
        projected_impact: Optional[int] = None
    ) -> Optional[AgentPersona]:
        """
        Suggest an alternative agent if the user might want a second opinion.

        Returns:
            AgentPersona or None: Alternative agent suggestion
        """

        # If assigned Entrepreneur but high impact, suggest Quant for numbers
        if assigned_agent == AgentPersona.ENTREPRENEUR and projected_impact and projected_impact >= 8:
            return AgentPersona.QUANT

        # If assigned Auditor but low risk, suggest Entrepreneur for growth focus
        if assigned_agent == AgentPersona.AUDITOR and risk_level == RiskLevel.LOW:
            return AgentPersona.ENTREPRENEUR

        # If assigned Quant, suggest running Auditor for risk check
        if assigned_agent == AgentPersona.QUANT:
            return AgentPersona.AUDITOR

        return None
