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


class TaskSpawnResult(BaseModel):
    """Result of spawning tasks from an intent"""
    task_ids: List[str]
    project_id: Optional[str] = None
    area_id: str
    tasks_created: int
    project_created: bool


class ProjectDetails(BaseModel):
    """Details for creating a project"""
    name: str
    description: str
    task_ids: List[str]
    source_intent_id: str
    area_id: Optional[str] = None


class ConceptMatch(BaseModel):
    """A concept extracted for knowledge linking"""
    concept: str
    node_type: str  # "Entity_Person", "Entity_Company", "Knowledge_Asset", "System_Component"
    confidence: float = Field(ge=0.0, le=1.0)


class AreaAssignment(BaseModel):
    """Area classification result"""
    area_name: str
    area_id: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


# --- Fine-Tuning Pipeline Models ---

class TrainingRecord(BaseModel):
    """A parsed record from DB_Training_Data"""
    notion_page_id: str
    intent_id: str
    timestamp: datetime
    acceptance_rate: float
    modifications_count: int
    modifications: List[str]
    original_plan: Dict[str, Any]
    final_plan: Dict[str, Any]
    agent_name: Optional[str] = None  # Populated via intent lookup


class AgentPerformanceSummary(BaseModel):
    """Aggregated performance metrics for a single agent"""
    agent_name: str
    time_range: str
    total_settlements: int
    avg_acceptance_rate: float
    min_acceptance_rate: float
    max_acceptance_rate: float
    acceptance_trend: List[float] = Field(default_factory=list)  # chronological
    common_modification_types: Dict[str, int] = Field(default_factory=dict)
    low_acceptance_count: int = 0  # settlements below 70%


class EditPattern(BaseModel):
    """A detected pattern in user edits across settlements"""
    pattern_type: str  # "deletion", "addition", "tone_shift"
    pattern_text: str
    frequency: float  # 0.0 - 1.0, fraction of records containing this
    occurrence_count: int
    agent_name: Optional[str] = None
    recommendation: str


class AgentComparison(BaseModel):
    """Head-to-head comparison of two agents"""
    agent_a: str
    agent_b: str
    agent_a_avg_acceptance: float
    agent_b_avg_acceptance: float
    agent_a_total_settlements: int
    agent_b_total_settlements: int
    winner: str  # agent name or "tie"
    delta: float  # acceptance rate difference


class FinetuningExample(BaseModel):
    """A single JSONL example for Claude fine-tuning"""
    messages: List[Dict[str, str]]  # role + content pairs
    source_intent_id: str
    acceptance_rate: float


class DatasetValidationReport(BaseModel):
    """Validation results for a fine-tuning JSONL dataset"""
    jsonl_path: str
    total_examples: int
    valid_examples: int
    invalid_examples: int
    errors: List[str] = Field(default_factory=list)
    avg_acceptance_rate: float
    ready_for_finetuning: bool
