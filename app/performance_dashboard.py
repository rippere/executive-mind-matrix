"""
Performance Dashboard - Real-time agent performance metrics

Provides dashboard-ready data visualizations:
- Agent performance comparison table
- Acceptance rate trends over time
- Improvement opportunity analysis
- Head-to-head agent comparisons
- Fine-tuning readiness status

Designed for consumption by:
- Notion dashboards
- External BI tools
- Frontend applications
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from loguru import logger

from app.training_analytics import TrainingAnalytics
from config.settings import settings


class PerformanceDashboard:
    """Formats training analytics into dashboard-ready visualizations"""

    def __init__(self):
        self.analytics = TrainingAnalytics()

    async def get_dashboard_overview(
        self,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get complete dashboard overview with all key metrics.

        Returns data optimized for dashboard visualization with:
        - Overall system performance
        - Per-agent summaries with trends
        - Top performers and improvement areas
        - Fine-tuning readiness status

        Args:
            time_range: "7d", "30d", "90d", or "all"

        Returns:
            Dashboard-ready data structure
        """
        logger.info(f"Generating dashboard overview for {time_range}")

        # Get raw performance data
        perf_summary = await self.analytics.get_agent_performance_summary(
            time_range=time_range
        )

        if not perf_summary.get("agents"):
            return {
                "status": "no_data",
                "message": "No training data available. Start collecting settlements via /log-settlement.",
                "time_range": time_range,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        # Extract agent summaries
        agents = perf_summary["agents"]
        overall = perf_summary["overall"]

        # Identify top performer
        top_performer = None
        highest_rate = 0.0
        for agent_name, summary in agents.items():
            if summary["avg_acceptance_rate"] > highest_rate:
                highest_rate = summary["avg_acceptance_rate"]
                top_performer = agent_name

        # Identify needs improvement
        needs_improvement = []
        for agent_name, summary in agents.items():
            if summary["avg_acceptance_rate"] < 0.7:
                needs_improvement.append({
                    "agent": agent_name,
                    "acceptance_rate": summary["avg_acceptance_rate"],
                    "low_acceptance_count": summary.get("low_acceptance_count", 0)
                })

        # Calculate improvement trends
        agent_trends = {}
        for agent_name, summary in agents.items():
            trend_data = summary.get("acceptance_trend", [])
            if len(trend_data) >= 2:
                recent = trend_data[-5:]  # Last 5 data points
                older = trend_data[:5]    # First 5 data points

                recent_avg = sum(recent) / len(recent) if recent else 0
                older_avg = sum(older) / len(older) if older else 0

                trend_direction = "improving" if recent_avg > older_avg + 0.05 else \
                                 "declining" if recent_avg < older_avg - 0.05 else \
                                 "stable"

                agent_trends[agent_name] = {
                    "direction": trend_direction,
                    "delta": round(recent_avg - older_avg, 3),
                    "recent_avg": round(recent_avg, 3),
                    "older_avg": round(older_avg, 3)
                }
            else:
                agent_trends[agent_name] = {
                    "direction": "insufficient_data",
                    "delta": 0,
                    "recent_avg": summary["avg_acceptance_rate"],
                    "older_avg": summary["avg_acceptance_rate"]
                }

        # Fine-tuning readiness
        total_settlements = overall["total_settlements"]
        finetuning_ready = total_settlements >= 100
        records_needed = max(0, 100 - total_settlements)

        dashboard = {
            "status": "success",
            "time_range": time_range,
            "generated_at": perf_summary["generated_at"],

            "overall_metrics": {
                "avg_acceptance_rate": overall["avg_acceptance_rate"],
                "total_settlements": total_settlements,
                "untagged_settlements": overall.get("untagged_settlements", 0),
                "agents_count": len(agents)
            },

            "top_performer": {
                "agent": top_performer,
                "acceptance_rate": highest_rate
            } if top_performer else None,

            "needs_improvement": needs_improvement,

            "agent_summaries": [
                {
                    "agent_name": agent_name,
                    "acceptance_rate": summary["avg_acceptance_rate"],
                    "total_settlements": summary["total_settlements"],
                    "min_acceptance": summary.get("min_acceptance_rate", 0),
                    "max_acceptance": summary.get("max_acceptance_rate", 0),
                    "trend": agent_trends.get(agent_name, {}),
                    "common_modifications": summary.get("common_modification_types", {}),
                    "low_acceptance_count": summary.get("low_acceptance_count", 0)
                }
                for agent_name, summary in agents.items()
            ],

            "fine_tuning_status": {
                "ready": finetuning_ready,
                "total_records": total_settlements,
                "records_needed": records_needed,
                "recommendation": self._get_finetuning_recommendation(
                    total_settlements,
                    overall["avg_acceptance_rate"]
                )
            },

            "visualization_data": {
                "acceptance_trends": {
                    agent_name: summary.get("acceptance_trend", [])
                    for agent_name, summary in agents.items()
                },
                "agent_comparison": [
                    {
                        "agent": agent_name,
                        "rate": summary["avg_acceptance_rate"]
                    }
                    for agent_name, summary in agents.items()
                ]
            }
        }

        logger.success(f"Dashboard generated: {len(agents)} agents, {total_settlements} settlements")

        return dashboard

    async def get_agent_deep_dive(
        self,
        agent_name: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get detailed analysis for a specific agent.

        Returns:
            - Performance metrics
            - Improvement opportunities
            - Pattern analysis
            - Actionable recommendations
        """
        logger.info(f"Generating deep dive for agent: {agent_name}")

        # Get performance summary
        perf_summary = await self.analytics.get_agent_performance_summary(
            time_range=time_range
        )

        agent_summary = perf_summary.get("agents", {}).get(agent_name)
        if not agent_summary:
            return {
                "status": "no_data",
                "agent": agent_name,
                "message": f"No data found for agent '{agent_name}' in time range {time_range}"
            }

        # Get improvement opportunities
        opportunities = await self.analytics.identify_improvement_opportunities(
            agent_name=agent_name,
            time_range=time_range
        )

        return {
            "status": "success",
            "agent": agent_name,
            "time_range": time_range,
            "generated_at": datetime.now(timezone.utc).isoformat(),

            "performance_summary": agent_summary,

            "improvement_opportunities": {
                "records_analyzed": opportunities.get("records_analyzed", 0),
                "deletion_patterns": opportunities.get("deletion_patterns", []),
                "addition_patterns": opportunities.get("addition_patterns", []),
                "tone_shifts": opportunities.get("tone_shifts", {}),
                "recommendations": opportunities.get("recommendations", [])
            },

            "action_items": self._generate_action_items(
                agent_summary,
                opportunities
            )
        }

    async def compare_agents_dashboard(
        self,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Generate head-to-head comparisons for all agent pairs.

        Returns comparison matrix showing which agents outperform others.
        """
        logger.info(f"Generating agent comparison matrix for {time_range}")

        perf_summary = await self.analytics.get_agent_performance_summary(
            time_range=time_range
        )

        agents = list(perf_summary.get("agents", {}).keys())

        if len(agents) < 2:
            return {
                "status": "insufficient_data",
                "message": "Need at least 2 agents with training data for comparison",
                "agents_found": len(agents)
            }

        # Generate all pairwise comparisons
        comparisons = []
        for i, agent_a in enumerate(agents):
            for agent_b in agents[i+1:]:
                comparison = await self.analytics.compare_agents(
                    agent_a=agent_a,
                    agent_b=agent_b,
                    time_range=time_range
                )
                comparisons.append(comparison.model_dump())

        # Create leaderboard
        agent_scores = {}
        for agent in agents:
            wins = sum(1 for c in comparisons if c["winner"] == agent)
            agent_scores[agent] = {
                "wins": wins,
                "avg_acceptance": perf_summary["agents"][agent]["avg_acceptance_rate"],
                "total_settlements": perf_summary["agents"][agent]["total_settlements"]
            }

        leaderboard = sorted(
            [{"agent": k, **v} for k, v in agent_scores.items()],
            key=lambda x: (x["wins"], x["avg_acceptance"]),
            reverse=True
        )

        return {
            "status": "success",
            "time_range": time_range,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "comparisons": comparisons,
            "leaderboard": leaderboard,
            "agents_analyzed": len(agents)
        }

    def _get_finetuning_recommendation(
        self,
        total_records: int,
        avg_acceptance: float
    ) -> str:
        """Generate actionable fine-tuning recommendation"""
        if total_records < 50:
            return f"Collect {50 - total_records} more settlements before considering fine-tuning"
        elif total_records < 100:
            return f"Almost ready! Collect {100 - total_records} more settlements for optimal fine-tuning"
        elif avg_acceptance < 0.6:
            return "Dataset ready, but low acceptance rates. Review prompts before fine-tuning"
        elif avg_acceptance >= 0.8:
            return "Excellent dataset! Fine-tuning may provide marginal improvements"
        else:
            return "Dataset ready for fine-tuning. Expected 5-15% improvement in acceptance rates"

    def _generate_action_items(
        self,
        agent_summary: Dict[str, Any],
        opportunities: Dict[str, Any]
    ) -> List[str]:
        """Generate prioritized action items from analysis"""
        actions = []

        # Low acceptance rate
        if agent_summary["avg_acceptance_rate"] < 0.6:
            actions.append(
                f"URGENT: Acceptance rate at {agent_summary['avg_acceptance_rate']:.1%}. "
                "Review system prompt and examples"
            )

        # High modification count
        if agent_summary.get("low_acceptance_count", 0) > 5:
            actions.append(
                f"Review {agent_summary['low_acceptance_count']} low-acceptance settlements "
                "for common failure patterns"
            )

        # Recommendations from pattern analysis
        recommendations = opportunities.get("recommendations", [])
        if recommendations:
            actions.extend(recommendations[:3])  # Top 3 recommendations

        # Default guidance
        if not actions:
            actions.append(
                f"Agent performing well ({agent_summary['avg_acceptance_rate']:.1%} acceptance). "
                "Continue monitoring trends"
            )

        return actions
