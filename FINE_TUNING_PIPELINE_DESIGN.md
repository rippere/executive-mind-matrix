# Fine-Tuning Pipeline Design

## Overview

Transform the training data captured by the Diff Logger into actionable insights for improving agent performance through prompt refinement and eventual model fine-tuning.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Training Data Flow                        │
└─────────────────────────────────────────────────────────────┘

1. USER EDITS AI SUGGESTION
   ↓
2. DIFF LOGGER CAPTURES
   - Original AI output (from AI_Raw_Output)
   - Final user version (from Scenario_Options)
   - Modifications list
   - Acceptance rate
   ↓
3. TRAINING DATA DATABASE (Notion)
   - Stores all settlements
   - Indexed by agent, intent type, timestamp
   ↓
4. AGGREGATION SERVICE (New)
   - Periodic batch processing
   - Pattern extraction
   - Metric calculation
   ↓
5. INSIGHTS DASHBOARD (New)
   - Agent performance comparison
   - Common rejection patterns
   - Improvement recommendations
   ↓
6. PROMPT REFINEMENT (Semi-Automated)
   - Identify low-performing agents
   - Generate prompt variations
   - A/B testing framework
   ↓
7. FINE-TUNING PIPELINE (Future)
   - Export to JSONL format
   - Fine-tune Claude models
   - Deployment and validation
```

---

## Phase 1: Data Aggregation Service (Immediate)

### Purpose
Extract insights from training data without manual analysis.

### Implementation

**New Module**: `app/training_analytics.py`

```python
class TrainingAnalytics:
    """
    Aggregates and analyzes training data from Notion DB_Training_Data
    to provide insights for prompt engineering and agent improvement.
    """

    async def get_agent_performance_summary(
        self,
        time_range: str = "30d"  # "7d", "30d", "90d", "all"
    ) -> Dict[str, Any]:
        """
        Returns comprehensive performance metrics for all agents.

        Metrics:
        - Average acceptance rate
        - Total settlements
        - Common rejection patterns
        - Performance trends over time
        - Best/worst performing intent types
        """
        pass

    async def identify_improvement_opportunities(
        self,
        agent_name: str
    ) -> List[Dict[str, Any]]:
        """
        Analyzes patterns in user edits to identify where agent fails.

        Returns:
        - Common phrases users remove
        - Common additions users make
        - Categories of consistent failures
        - Suggested prompt adjustments
        """
        pass

    async def compare_agents(
        self,
        agent_a: str,
        agent_b: str
    ) -> Dict[str, Any]:
        """
        Head-to-head comparison of two agents.

        Useful for A/B testing after prompt changes.
        """
        pass

    async def export_for_fine_tuning(
        self,
        min_acceptance_rate: float = 0.7
    ) -> str:
        """
        Exports high-quality training pairs to JSONL format.

        Format:
        {
          "messages": [
            {"role": "user", "content": "Intent description"},
            {"role": "assistant", "content": "Human-approved output"}
          ]
        }
        """
        pass
```

### API Endpoints

Add to `main.py`:

```python
@app.get("/analytics/agents/summary")
async def get_agents_summary(time_range: str = "30d"):
    """Get performance summary for all agents"""
    pass

@app.get("/analytics/agent/{agent_name}/improvements")
async def get_improvement_opportunities(agent_name: str):
    """Identify improvement opportunities for specific agent"""
    pass

@app.post("/analytics/export/fine-tuning")
async def export_fine_tuning_data(
    min_acceptance_rate: float = 0.7
):
    """Export training data in JSONL format for fine-tuning"""
    pass
```

---

## Phase 2: Pattern Recognition (Week 2-3)

### Automated Pattern Detection

**Identify Common User Edits**:

```python
class EditPatternAnalyzer:
    """
    Analyzes user modifications to identify systematic issues.
    """

    def analyze_deletion_patterns(self, settlements: List[Dict]) -> List[Pattern]:
        """
        Find phrases/words users consistently remove.

        Example Output:
        {
          "pattern": "Let me analyze this",
          "frequency": 0.85,  # 85% of edits remove this
          "agent": "The Entrepreneur",
          "recommendation": "Remove filler phrases from prompts"
        }
        """
        pass

    def analyze_addition_patterns(self, settlements: List[Dict]) -> List[Pattern]:
        """
        Find content users consistently add.

        Example Output:
        {
          "pattern": "Consider regulatory compliance",
          "frequency": 0.72,
          "agent": "The Entrepreneur",
          "recommendation": "Add compliance considerations to prompts"
        }
        """
        pass

    def detect_tone_shifts(self, settlements: List[Dict]) -> List[ToneShift]:
        """
        Identify systematic tone changes (formal ↔ casual, etc.)

        Uses sentiment analysis and formality detection.
        """
        pass
```

### NLP Tools Required:

```python
# requirements.txt additions
spacy>=3.7.0
transformers>=4.35.0
nltk>=3.8.0
scikit-learn>=1.3.0
```

---

## Phase 3: Prompt Engineering Assistant (Week 3-4)

### Automated Prompt Suggestions

```python
class PromptOptimizer:
    """
    Generates prompt improvement suggestions based on training data.
    """

    async def generate_prompt_variants(
        self,
        current_prompt: str,
        issues: List[Pattern]
    ) -> List[PromptVariant]:
        """
        Creates alternative prompts addressing identified issues.

        Uses Claude to generate variations based on patterns.
        """
        pass

    async def evaluate_prompt_variant(
        self,
        old_prompt: str,
        new_prompt: str,
        test_intents: List[str]
    ) -> PromptEvaluation:
        """
        A/B test prompt variants on historical intents.

        Compares:
        - Acceptance rate (predicted)
        - Response quality
        - Alignment with user preferences
        """
        pass
```

### Workflow:

1. System identifies agent with low acceptance rate (< 70%)
2. Analyzes last 30 settlements for that agent
3. Identifies common patterns in user edits
4. Generates 3-5 prompt variants
5. Presents to admin for review
6. Admin selects variant to test
7. System logs performance under new prompt
8. After 10 settlements, compares performance

---

## Phase 4: A/B Testing Framework (Week 4-5)

### Split Testing Infrastructure

```python
class ABTestManager:
    """
    Manages A/B testing of prompt variants.
    """

    async def create_experiment(
        self,
        agent_name: str,
        variant_a_prompt: str,
        variant_b_prompt: str,
        traffic_split: float = 0.5
    ) -> str:
        """
        Creates new A/B test.

        Returns experiment_id for tracking.
        """
        pass

    async def route_to_variant(
        self,
        agent_name: str,
        intent_id: str
    ) -> str:
        """
        Routes intent to prompt variant based on traffic split.

        Returns: "variant_a" or "variant_b"
        """
        pass

    async def get_experiment_results(
        self,
        experiment_id: str
    ) -> ExperimentResults:
        """
        Statistical analysis of A/B test.

        Returns:
        - Variant A acceptance rate
        - Variant B acceptance rate
        - Statistical significance (p-value)
        - Winner recommendation
        """
        pass
```

### Database Schema Addition

**New Notion Database**: `DB_AB_Tests`

Properties:
- **Experiment ID** (Title): Unique identifier
- **Agent Name** (Select): Which agent is being tested
- **Variant A Prompt** (Text): Original prompt
- **Variant B Prompt** (Text): New prompt
- **Variant A Settlements** (Number): Count
- **Variant B Settlements** (Number): Count
- **Variant A Acceptance** (Number): Avg acceptance rate
- **Variant B Acceptance** (Number): Avg acceptance rate
- **Status** (Select): Running, Completed, Winner_Deployed
- **Winner** (Select): Variant A, Variant B, Inconclusive
- **Created Date** (Date)
- **Completed Date** (Date)

---

## Phase 5: Fine-Tuning Pipeline (Month 2+)

### Prerequisites

- At least 100 high-quality settlements (acceptance rate > 70%)
- Consistent user editing patterns identified
- Prompt engineering has reached diminishing returns

### Data Preparation

```python
class FineTuningDataPrep:
    """
    Prepares training data for Claude fine-tuning.
    """

    async def export_to_jsonl(
        self,
        output_path: str,
        filters: Dict[str, Any]
    ):
        """
        Exports training data in Claude fine-tuning format.

        Filters:
        - min_acceptance_rate: Only include high-quality edits
        - agent_name: Filter by specific agent
        - date_range: Time range
        - intent_type: strategic/operational/reference
        """

        # Format:
        # {"messages": [
        #   {"role": "system", "content": "You are The Entrepreneur..."},
        #   {"role": "user", "content": "Intent description"},
        #   {"role": "assistant", "content": "User-approved output"}
        # ]}
        pass

    async def validate_dataset(
        self,
        jsonl_path: str
    ) -> ValidationReport:
        """
        Validates dataset for fine-tuning.

        Checks:
        - Format correctness
        - Minimum examples (50+)
        - Content quality
        - Diversity of examples
        """
        pass
```

### Fine-Tuning Workflow

```bash
# 1. Export training data
curl -X POST http://localhost:8000/analytics/export/fine-tuning \
  -d '{"min_acceptance_rate": 0.75, "agent": "The Entrepreneur"}' \
  -o entrepreneur_training.jsonl

# 2. Validate dataset
python -m app.fine_tuning.validate entrepreneur_training.jsonl

# 3. Upload to Anthropic
# (Use Anthropic's fine-tuning API when available)
# Currently in beta - request access from Anthropic

# 4. Monitor training
# Track via Anthropic dashboard

# 5. Deploy fine-tuned model
# Update .env: ANTHROPIC_MODEL_ENTREPRENEUR=ft:custom-model-id

# 6. Monitor performance
# Compare fine-tuned vs base model acceptance rates
```

---

## Phase 6: Continuous Learning Loop (Ongoing)

### Automated Monitoring

```python
class ContinuousLearning:
    """
    Automates the improvement cycle.
    """

    async def weekly_performance_report(self):
        """
        Generates weekly email/Slack report with:
        - Agent performance trends
        - Detected issues
        - Recommended actions
        """
        pass

    async def auto_detect_regression(self):
        """
        Alerts when agent performance drops.

        Triggers:
        - Acceptance rate drops > 10% in 7 days
        - New failure patterns emerge
        - User complaints increase
        """
        pass

    async def suggest_experiments(self):
        """
        Proactively suggests A/B tests based on data.

        Example: "The Auditor shows 20% lower acceptance on
        operational intents. Test adding 'Keep it concise' to prompt."
        """
        pass
```

---

## Metrics Dashboard

### Key Performance Indicators

**Agent-Level**:
- Acceptance Rate (7d, 30d, 90d, all-time)
- Total Settlements
- Average Processing Time
- Error Rate
- User Satisfaction Score (derived from edits)

**System-Level**:
- Overall Acceptance Rate
- Intents Processed
- Training Data Quality Score
- A/B Test Success Rate
- Fine-Tuning ROI

**Trend Analysis**:
- Week-over-week change
- Best/worst performing days
- Seasonal patterns
- Correlation with intent types

---

## Implementation Priorities

### Sprint 1 (2026-02-18) — COMPLETE ✅
- ✅ Ensure AI_Raw_Output property is set up
- ✅ Verify diff_logger is capturing data correctly
- ✅ Build `TrainingAnalytics` module (`app/training_analytics.py`)
- ✅ Add analytics API endpoints (`/analytics/*`)
- ✅ Build `EditPatternAnalyzer` (`app/fine_tuning/pattern_analysis.py`)
- ✅ Build `FineTuningDataPrep` + JSONL export (`app/fine_tuning/data_export.py`)
- ✅ Close training data collection loop (auto-logging on approval + poller sweep)
- ✅ Tag training records with agent name

### Sprint 1 Pending (Notion schema — manual):
- ⬜ Add `Agent_Name` (Select) to Training Data database
- ⬜ Add `Diff_Logged` (Checkbox) to Action Pipes database

### Sprint 2 (Next):
- ⬜ Collect real settlements — run dialectics, approve Action Pipes, verify data flows
- ⬜ Hit `/analytics/agents/summary` and confirm per-agent metrics appear
- ⬜ Review `/analytics/agent/{name}/improvements` output quality on real data
- ⬜ Create alert when any agent drops below 70% acceptance rate

### Sprint 3:
- ⬜ Build `PromptOptimizer` module (`app/fine_tuning/prompt_optimizer.py`)
- ⬜ Create prompt variant generator using Claude
- ⬜ Manual testing of prompt improvements

### Sprint 4:
- ⬜ Implement A/B testing framework (`app/fine_tuning/ab_testing.py`)
- ⬜ Create `DB_AB_Tests` in Notion
- ⬜ Run first A/B test

### Sprint 5 (100+ settlements required):
- ⬜ Export training data via `POST /analytics/export/fine-tuning`
- ⬜ Validate dataset (50+ examples, format check)
- ⬜ Request Anthropic fine-tuning access
- ⬜ Prepare fine-tuning dataset

### Sprint 6:
- ⬜ Deploy fine-tuned models
- ⬜ Continuous monitoring and iteration

---

## Cost Estimates

### Prompt Engineering Phase:
- **Development Time**: 40-60 hours
- **Claude API Usage**: ~$20/month (for generating prompt variants)
- **Total**: ~$20/month ongoing

### Fine-Tuning Phase:
- **Dataset Preparation**: 10-20 hours
- **Anthropic Fine-Tuning**: $TBD (pricing not public yet)
- **Inference Cost**: Similar to base model
- **Total**: ~$50-100 one-time + ongoing inference

### ROI Calculation:
- **Current**: Manual review + editing of every AI suggestion
- **With Fine-Tuning**: 30-50% reduction in manual edits
- **Time Saved**: 5-10 hours/month
- **Break-Even**: 2-3 months

---

## Success Criteria

### Short-Term (3 months):
- Average acceptance rate > 75%
- At least one successful prompt optimization
- A/B testing framework operational

### Medium-Term (6 months):
- Average acceptance rate > 85%
- Fine-tuned model for at least one agent
- 50% reduction in manual editing time

### Long-Term (12 months):
- Average acceptance rate > 90%
- All agents fine-tuned
- Automated continuous learning loop operational
- System recommends improvements proactively

---

## Technical Dependencies

### Python Libraries:
```txt
# Analytics
pandas>=2.1.0
numpy>=1.24.0
scipy>=1.11.0

# NLP
spacy>=3.7.0
transformers>=4.35.0
nltk>=3.8.0

# Visualization (for dashboard)
plotly>=5.17.0
matplotlib>=3.8.0

# Statistical Testing
statsmodels>=0.14.0
```

### External Services:
- Anthropic API (fine-tuning access)
- Optional: Weights & Biases for experiment tracking
- Optional: Metabase for advanced analytics

---

## Security Considerations

### Data Privacy:
- Training data may contain sensitive user decisions
- **Action**: Implement PII redaction before export
- **Action**: Encrypt training datasets at rest

### Access Control:
- Fine-tuning dashboard should be admin-only
- **Action**: Add authentication to analytics endpoints
- **Action**: Log all access to training data

### Model Security:
- Fine-tuned models could be proprietary IP
- **Action**: Store model IDs securely (env variables)
- **Action**: Restrict deployment to authorized systems

---

## Alternative Approaches

### If Anthropic Fine-Tuning is Unavailable:

1. **Prompt Library Approach**:
   - Build library of proven prompt patterns
   - Dynamically compose prompts based on intent type
   - Use retrieval-augmented generation (RAG)

2. **Ensemble Method**:
   - Run multiple prompt variants
   - Use voting or confidence scoring
   - Return highest-quality response

3. **External Fine-Tuning**:
   - Use OpenAI GPT-4 fine-tuning
   - Compare performance vs Claude
   - Keep Claude for inference, use GPT-4 for specialized tasks

---

## Documentation & Handoff

### For Future Developers:

```
📁 Fine-Tuning Documentation
├── FINE_TUNING_PIPELINE_DESIGN.md (this file)
├── app/training_analytics.py (implementation)
├── app/fine_tuning/ (dedicated module)
│   ├── pattern_analysis.py
│   ├── prompt_optimizer.py
│   ├── ab_testing.py
│   └── data_export.py
└── notebooks/ (Jupyter notebooks for analysis)
    ├── explore_training_data.ipynb
    ├── pattern_detection.ipynb
    └── prompt_testing.ipynb
```

---

## Next Steps

1. **Immediate**: Review this design doc with team
2. **Week 1**: Implement `TrainingAnalytics` module
3. **Week 2**: Build basic analytics dashboard
4. **Week 3**: Test pattern detection on real data
5. **Month 2**: Launch first A/B test
6. **Month 3**: Evaluate fine-tuning readiness

---

**Author**: Claude Sonnet 4.5
**Date**: 2026-01-27
**Status**: Design Complete - Ready for Implementation
**Priority**: Medium (after core system is stable)
