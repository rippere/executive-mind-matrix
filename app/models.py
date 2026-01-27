from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class IntentStatus(str, Enum):
    """Status values for Executive Intents"""
    PENDING = "Pending"
    PROCESSING = "Processing"
    ASSIGNED = "Assigned"
    IN_ANALYSIS = "In_Analysis"
    PENDING_APPROVAL = "Pending_Approval"
    APPROVED = "Approved"
    EXECUTED = "Executed"
    DONE = "Done"


class RiskLevel(str, Enum):
    """Risk levels for intents"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class AgentPersona(str, Enum):
    """Available AI agent personas"""
    ENTREPRENEUR = "The Entrepreneur"
    QUANT = "The Quant"
    AUDITOR = "The Auditor"


class ScenarioOption(BaseModel):
    """A single scenario option from agent analysis"""
    option: str
    description: str
    pros: List[str]
    cons: List[str]
    risk: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=10)


class AgentAnalysis(BaseModel):
    """Complete agent analysis response"""
    scenario_options: List[ScenarioOption]
    recommended_option: str
    recommendation_rationale: str
    risk_assessment: str
    required_resources: Dict[str, Any]
    task_generation_template: List[str]


class NotionIntent(BaseModel):
    """Executive Intent from Notion"""
    id: str
    title: str
    description: str
    status: IntentStatus
    risk_level: Optional[RiskLevel] = None
    agent_persona: Optional[AgentPersona] = None
    projected_impact: Optional[int] = None
    success_criteria: Optional[str] = None


class SettlementDiff(BaseModel):
    """Captures differences between AI suggestion and human edit"""
    intent_id: str
    timestamp: datetime
    original_plan: Dict[str, Any]
    final_plan: Dict[str, Any]
    diff_summary: Dict[str, Any]
    user_modifications: List[str]
    acceptance_rate: float


class DialecticOutput(BaseModel):
    """Output from adversarial agent dialectic"""
    intent_id: str
    growth_perspective: Optional[AgentAnalysis] = None
    risk_perspective: Optional[AgentAnalysis] = None
    synthesis: str
    recommended_path: str
    conflict_points: List[str]
