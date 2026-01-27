"""
Unit tests for app/models.py

Tests model validation, enums, and Pydantic schema validation.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models import (
    IntentStatus, RiskLevel, AgentPersona,
    ScenarioOption, AgentAnalysis, NotionIntent,
    SettlementDiff, DialecticOutput
)


# ============================================================================
# ENUM TESTS
# ============================================================================

class TestEnums:
    """Test enum definitions and values."""

    def test_intent_status_values(self):
        """Test IntentStatus enum has correct values."""
        assert IntentStatus.PENDING == "Pending"
        assert IntentStatus.PROCESSING == "Processing"
        assert IntentStatus.ASSIGNED == "Assigned"
        assert IntentStatus.IN_ANALYSIS == "In_Analysis"
        assert IntentStatus.PENDING_APPROVAL == "Pending_Approval"
        assert IntentStatus.APPROVED == "Approved"
        assert IntentStatus.EXECUTED == "Executed"
        assert IntentStatus.DONE == "Done"

    def test_risk_level_values(self):
        """Test RiskLevel enum has correct values."""
        assert RiskLevel.LOW == "Low"
        assert RiskLevel.MEDIUM == "Medium"
        assert RiskLevel.HIGH == "High"

    def test_agent_persona_values(self):
        """Test AgentPersona enum has correct values."""
        assert AgentPersona.ENTREPRENEUR == "The Entrepreneur"
        assert AgentPersona.QUANT == "The Quant"
        assert AgentPersona.AUDITOR == "The Auditor"

    def test_enum_iteration(self):
        """Test enums can be iterated."""
        statuses = list(IntentStatus)
        assert len(statuses) == 8

        risks = list(RiskLevel)
        assert len(risks) == 3

        agents = list(AgentPersona)
        assert len(agents) == 3


# ============================================================================
# SCENARIO OPTION TESTS
# ============================================================================

class TestScenarioOption:
    """Test ScenarioOption model validation."""

    def test_valid_scenario_option(self):
        """Test creating valid ScenarioOption."""
        option = ScenarioOption(
            option="A",
            description="Test description",
            pros=["Pro 1", "Pro 2"],
            cons=["Con 1"],
            risk=3,
            impact=7
        )

        assert option.option == "A"
        assert len(option.pros) == 2
        assert len(option.cons) == 1
        assert option.risk == 3
        assert option.impact == 7

    def test_risk_validation_minimum(self):
        """Test risk must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            ScenarioOption(
                option="A",
                description="Test",
                pros=["Pro"],
                cons=["Con"],
                risk=0,  # Invalid: too low
                impact=5
            )

        assert "risk" in str(exc_info.value)

    def test_risk_validation_maximum(self):
        """Test risk must be <= 5."""
        with pytest.raises(ValidationError) as exc_info:
            ScenarioOption(
                option="A",
                description="Test",
                pros=["Pro"],
                cons=["Con"],
                risk=6,  # Invalid: too high
                impact=5
            )

        assert "risk" in str(exc_info.value)

    def test_impact_validation_minimum(self):
        """Test impact must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            ScenarioOption(
                option="A",
                description="Test",
                pros=["Pro"],
                cons=["Con"],
                risk=3,
                impact=0  # Invalid: too low
            )

        assert "impact" in str(exc_info.value)

    def test_impact_validation_maximum(self):
        """Test impact must be <= 10."""
        with pytest.raises(ValidationError) as exc_info:
            ScenarioOption(
                option="A",
                description="Test",
                pros=["Pro"],
                cons=["Con"],
                risk=3,
                impact=11  # Invalid: too high
            )

        assert "impact" in str(exc_info.value)

    def test_empty_lists_allowed(self):
        """Test empty pros/cons lists are valid."""
        option = ScenarioOption(
            option="A",
            description="Test",
            pros=[],
            cons=[],
            risk=1,
            impact=1
        )

        assert option.pros == []
        assert option.cons == []


# ============================================================================
# AGENT ANALYSIS TESTS
# ============================================================================

class TestAgentAnalysis:
    """Test AgentAnalysis model validation."""

    def test_valid_agent_analysis(self, sample_scenario_option):
        """Test creating valid AgentAnalysis."""
        analysis = AgentAnalysis(
            scenario_options=[sample_scenario_option],
            recommended_option="A",
            recommendation_rationale="Because it's best",
            risk_assessment="Low risk",
            required_resources={
                "time": "2 weeks",
                "money": "$1000",
                "tools": ["Tool1"],
                "people": []
            },
            task_generation_template=["Task 1", "Task 2"]
        )

        assert len(analysis.scenario_options) == 1
        assert analysis.recommended_option == "A"
        assert len(analysis.task_generation_template) == 2

    def test_multiple_scenario_options(self):
        """Test analysis with multiple scenario options."""
        options = [
            ScenarioOption(
                option=f"Option {i}",
                description=f"Description {i}",
                pros=[f"Pro {i}"],
                cons=[f"Con {i}"],
                risk=i,
                impact=i * 2
            )
            for i in range(1, 4)
        ]

        analysis = AgentAnalysis(
            scenario_options=options,
            recommended_option="Option 2",
            recommendation_rationale="Middle option is balanced",
            risk_assessment="Medium risk",
            required_resources={},
            task_generation_template=[]
        )

        assert len(analysis.scenario_options) == 3
        assert analysis.scenario_options[1].option == "Option 2"

    def test_required_resources_flexible(self):
        """Test required_resources accepts any dict structure."""
        analysis = AgentAnalysis(
            scenario_options=[],
            recommended_option="A",
            recommendation_rationale="Test",
            risk_assessment="Test",
            required_resources={
                "custom_field": "custom_value",
                "nested": {"key": "value"}
            },
            task_generation_template=[]
        )

        assert "custom_field" in analysis.required_resources
        assert analysis.required_resources["nested"]["key"] == "value"


# ============================================================================
# NOTION INTENT TESTS
# ============================================================================

class TestNotionIntent:
    """Test NotionIntent model validation."""

    def test_valid_minimal_intent(self):
        """Test creating intent with only required fields."""
        intent = NotionIntent(
            id="test_123",
            title="Test Intent",
            description="Test description",
            status=IntentStatus.PENDING
        )

        assert intent.id == "test_123"
        assert intent.status == IntentStatus.PENDING
        assert intent.risk_level is None
        assert intent.agent_persona is None
        assert intent.projected_impact is None

    def test_valid_complete_intent(self):
        """Test creating intent with all fields."""
        intent = NotionIntent(
            id="test_123",
            title="Test Intent",
            description="Test description",
            status=IntentStatus.IN_ANALYSIS,
            risk_level=RiskLevel.HIGH,
            agent_persona=AgentPersona.ENTREPRENEUR,
            projected_impact=9,
            success_criteria="Achieve goal X"
        )

        assert intent.risk_level == RiskLevel.HIGH
        assert intent.agent_persona == AgentPersona.ENTREPRENEUR
        assert intent.projected_impact == 9
        assert intent.success_criteria == "Achieve goal X"

    def test_status_enum_validation(self):
        """Test status must be valid IntentStatus."""
        with pytest.raises(ValidationError):
            NotionIntent(
                id="test_123",
                title="Test",
                description="Test",
                status="InvalidStatus"  # Invalid status
            )

    def test_risk_level_enum_validation(self):
        """Test risk_level must be valid RiskLevel."""
        with pytest.raises(ValidationError):
            NotionIntent(
                id="test_123",
                title="Test",
                description="Test",
                status=IntentStatus.PENDING,
                risk_level="ExtremelyHigh"  # Invalid risk
            )

    def test_agent_persona_enum_validation(self):
        """Test agent_persona must be valid AgentPersona."""
        with pytest.raises(ValidationError):
            NotionIntent(
                id="test_123",
                title="Test",
                description="Test",
                status=IntentStatus.PENDING,
                agent_persona="The Wizard"  # Invalid agent
            )


# ============================================================================
# SETTLEMENT DIFF TESTS
# ============================================================================

class TestSettlementDiff:
    """Test SettlementDiff model validation."""

    def test_valid_settlement_diff(self):
        """Test creating valid SettlementDiff."""
        now = datetime.utcnow()
        diff = SettlementDiff(
            intent_id="intent_123",
            timestamp=now,
            original_plan={"option": "A"},
            final_plan={"option": "B"},
            diff_summary={"changes": ["option changed"]},
            user_modifications=["Changed option"],
            acceptance_rate=0.75
        )

        assert diff.intent_id == "intent_123"
        assert diff.timestamp == now
        assert diff.acceptance_rate == 0.75
        assert len(diff.user_modifications) == 1

    def test_acceptance_rate_range(self):
        """Test acceptance rate can be 0.0 to 1.0."""
        # Test 0% acceptance
        diff_zero = SettlementDiff(
            intent_id="test",
            timestamp=datetime.utcnow(),
            original_plan={},
            final_plan={},
            diff_summary={},
            user_modifications=[],
            acceptance_rate=0.0
        )
        assert diff_zero.acceptance_rate == 0.0

        # Test 100% acceptance
        diff_full = SettlementDiff(
            intent_id="test",
            timestamp=datetime.utcnow(),
            original_plan={},
            final_plan={},
            diff_summary={},
            user_modifications=[],
            acceptance_rate=1.0
        )
        assert diff_full.acceptance_rate == 1.0

    def test_complex_plan_structures(self):
        """Test diff handles complex nested plan structures."""
        diff = SettlementDiff(
            intent_id="test",
            timestamp=datetime.utcnow(),
            original_plan={
                "option": "A",
                "tasks": [
                    {"id": 1, "name": "Task 1", "subtasks": ["a", "b"]},
                    {"id": 2, "name": "Task 2", "subtasks": []}
                ],
                "metadata": {"created_by": "AI"}
            },
            final_plan={
                "option": "B",
                "tasks": [
                    {"id": 1, "name": "Task 1 Modified", "subtasks": ["a", "b", "c"]},
                    {"id": 3, "name": "Task 3", "subtasks": []}
                ],
                "metadata": {"created_by": "AI", "edited_by": "Human"}
            },
            diff_summary={"multiple": "changes"},
            user_modifications=["Changed option", "Modified tasks"],
            acceptance_rate=0.5
        )

        assert diff.original_plan["option"] == "A"
        assert diff.final_plan["option"] == "B"
        assert len(diff.final_plan["tasks"]) == 2


# ============================================================================
# DIALECTIC OUTPUT TESTS
# ============================================================================

class TestDialecticOutput:
    """Test DialecticOutput model validation."""

    def test_valid_dialectic_output(self, sample_agent_analysis):
        """Test creating valid DialecticOutput."""
        output = DialecticOutput(
            intent_id="intent_123",
            growth_perspective=sample_agent_analysis,
            risk_perspective=sample_agent_analysis,
            synthesis="Balanced recommendation",
            recommended_path="Option A with modifications",
            conflict_points=["Speed vs Quality", "Cost vs Features"]
        )

        assert output.intent_id == "intent_123"
        assert output.growth_perspective is not None
        assert output.risk_perspective is not None
        assert len(output.conflict_points) == 2

    def test_optional_perspectives(self):
        """Test perspectives are optional (for error cases)."""
        output = DialecticOutput(
            intent_id="intent_123",
            growth_perspective=None,
            risk_perspective=None,
            synthesis="Error occurred",
            recommended_path="Manual review required",
            conflict_points=["Analysis failed"]
        )

        assert output.growth_perspective is None
        assert output.risk_perspective is None
        assert "Error" in output.synthesis

    def test_empty_conflict_points(self):
        """Test dialectic can have no conflicts (rare but valid)."""
        output = DialecticOutput(
            intent_id="intent_123",
            synthesis="Both agents agree",
            recommended_path="Option A",
            conflict_points=[]  # No conflicts
        )

        assert len(output.conflict_points) == 0

    def test_model_serialization(self, sample_agent_analysis):
        """Test dialectic output can be serialized to dict/json."""
        output = DialecticOutput(
            intent_id="intent_123",
            growth_perspective=sample_agent_analysis,
            risk_perspective=sample_agent_analysis,
            synthesis="Test",
            recommended_path="Option A",
            conflict_points=["Conflict 1"]
        )

        # Test dict conversion
        output_dict = output.model_dump()
        assert output_dict["intent_id"] == "intent_123"
        assert "growth_perspective" in output_dict

        # Test JSON serialization
        output_json = output.model_dump_json()
        assert isinstance(output_json, str)
        assert "intent_123" in output_json
