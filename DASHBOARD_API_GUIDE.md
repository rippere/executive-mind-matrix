# Agent Performance Dashboard API Guide

Real-time agent performance metrics and analytics for the Executive Mind Matrix.

---

## 📊 Overview

The Performance Dashboard provides comprehensive analytics on agent performance, training data quality, and fine-tuning readiness. All endpoints return JSON data optimized for dashboard visualization.

---

## 🔌 API Endpoints

### 1. Dashboard Overview

**Endpoint**: `GET /dashboard/overview`

**Description**: Complete dashboard with all key metrics, trends, and visualizations.

**Query Parameters**:
- `time_range` (optional): `"7d"`, `"30d"` (default), `"90d"`, or `"all"`

**Response Structure**:
```json
{
  "status": "success",
  "time_range": "30d",
  "generated_at": "2026-02-23T...",

  "overall_metrics": {
    "avg_acceptance_rate": 0.75,
    "total_settlements": 150,
    "untagged_settlements": 5,
    "agents_count": 3
  },

  "top_performer": {
    "agent": "The Quant",
    "acceptance_rate": 0.82
  },

  "needs_improvement": [
    {
      "agent": "The Entrepreneur",
      "acceptance_rate": 0.65,
      "low_acceptance_count": 8
    }
  ],

  "agent_summaries": [
    {
      "agent_name": "The Entrepreneur",
      "acceptance_rate": 0.75,
      "total_settlements": 50,
      "min_acceptance": 0.45,
      "max_acceptance": 0.95,
      "trend": {
        "direction": "improving",
        "delta": 0.08,
        "recent_avg": 0.79,
        "older_avg": 0.71
      },
      "common_modifications": {
        "modified": 15,
        "added": 8,
        "removed": 12
      },
      "low_acceptance_count": 5
    }
  ],

  "fine_tuning_status": {
    "ready": true,
    "total_records": 150,
    "records_needed": 0,
    "recommendation": "Dataset ready for fine-tuning. Expected 5-15% improvement"
  },

  "visualization_data": {
    "acceptance_trends": {
      "The Entrepreneur": [0.65, 0.70, 0.72, 0.75, 0.79],
      "The Quant": [0.80, 0.81, 0.82, 0.83, 0.82],
      "The Auditor": [0.70, 0.72, 0.73, 0.71, 0.74]
    },
    "agent_comparison": [
      {"agent": "The Quant", "rate": 0.82},
      {"agent": "The Entrepreneur", "rate": 0.75},
      {"agent": "The Auditor", "rate": 0.72}
    ]
  }
}
```

**Example Request**:
```bash
curl "https://web-production-3d888.up.railway.app/dashboard/overview?time_range=30d"
```

---

### 2. Agent Deep Dive

**Endpoint**: `GET /dashboard/agent/{agent_name}`

**Description**: Detailed analysis for a specific agent with improvement opportunities.

**Path Parameters**:
- `agent_name` (required): Agent persona name
  - `"The Entrepreneur"`
  - `"The Quant"`
  - `"The Auditor"`

**Query Parameters**:
- `time_range` (optional): `"7d"`, `"30d"` (default), `"90d"`, or `"all"`

**Response Structure**:
```json
{
  "status": "success",
  "agent": "The Entrepreneur",
  "time_range": "30d",
  "generated_at": "2026-02-23T...",

  "performance_summary": {
    "agent_name": "The Entrepreneur",
    "total_settlements": 50,
    "avg_acceptance_rate": 0.75,
    "min_acceptance_rate": 0.45,
    "max_acceptance_rate": 0.95,
    "acceptance_trend": [0.65, 0.70, 0.72, 0.75, 0.79],
    "common_modification_types": {
      "modified": 15,
      "added": 8,
      "removed": 12
    },
    "low_acceptance_count": 5
  },

  "improvement_opportunities": {
    "records_analyzed": 50,
    "deletion_patterns": [
      {
        "pattern": "risk_mitigation",
        "frequency": 12,
        "example": "User consistently removes risk analysis sections"
      }
    ],
    "addition_patterns": [
      {
        "pattern": "market_research",
        "frequency": 8,
        "example": "User adds market research data to plans"
      }
    ],
    "tone_shifts": {
      "formal_to_casual": 5,
      "technical_to_business": 3
    },
    "recommendations": [
      "Reduce risk analysis depth - users consistently remove it",
      "Include market research prompts in initial generation",
      "Adjust tone to be more business-focused, less technical"
    ]
  },

  "action_items": [
    "Review 5 low-acceptance settlements for common failure patterns",
    "Update system prompt to reduce risk analysis verbosity",
    "Add market research context to agent persona"
  ]
}
```

**Example Request**:
```bash
curl "https://web-production-3d888.up.railway.app/dashboard/agent/The%20Entrepreneur?time_range=30d"
```

---

### 3. Agent Comparison Matrix

**Endpoint**: `GET /dashboard/compare`

**Description**: Head-to-head comparisons for all agent pairs with leaderboard.

**Query Parameters**:
- `time_range` (optional): `"7d"`, `"30d"` (default), `"90d"`, or `"all"`

**Response Structure**:
```json
{
  "status": "success",
  "time_range": "30d",
  "generated_at": "2026-02-23T...",

  "comparisons": [
    {
      "agent_a": "The Quant",
      "agent_b": "The Entrepreneur",
      "agent_a_avg_acceptance": 0.82,
      "agent_b_avg_acceptance": 0.75,
      "agent_a_total_settlements": 60,
      "agent_b_total_settlements": 50,
      "winner": "The Quant",
      "delta": 0.07
    },
    {
      "agent_a": "The Quant",
      "agent_b": "The Auditor",
      "agent_a_avg_acceptance": 0.82,
      "agent_b_avg_acceptance": 0.72,
      "agent_a_total_settlements": 60,
      "agent_b_total_settlements": 40,
      "winner": "The Quant",
      "delta": 0.10
    },
    {
      "agent_a": "The Entrepreneur",
      "agent_b": "The Auditor",
      "agent_a_avg_acceptance": 0.75,
      "agent_b_avg_acceptance": 0.72,
      "agent_a_total_settlements": 50,
      "agent_b_total_settlements": 40,
      "winner": "The Entrepreneur",
      "delta": 0.03
    }
  ],

  "leaderboard": [
    {
      "agent": "The Quant",
      "wins": 2,
      "avg_acceptance": 0.82,
      "total_settlements": 60
    },
    {
      "agent": "The Entrepreneur",
      "wins": 1,
      "avg_acceptance": 0.75,
      "total_settlements": 50
    },
    {
      "agent": "The Auditor",
      "wins": 0,
      "avg_acceptance": 0.72,
      "total_settlements": 40
    }
  ],

  "agents_analyzed": 3
}
```

**Example Request**:
```bash
curl "https://web-production-3d888.up.railway.app/dashboard/compare?time_range=30d"
```

---

## 📈 Dashboard Visualizations

### Trend Charts

Use `visualization_data.acceptance_trends` from the overview endpoint to plot line charts:

```javascript
// Example: Chart.js configuration
{
  labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
  datasets: [
    {
      label: 'The Quant',
      data: [0.80, 0.81, 0.82, 0.83, 0.82],
      borderColor: 'rgb(75, 192, 192)'
    },
    {
      label: 'The Entrepreneur',
      data: [0.65, 0.70, 0.72, 0.75, 0.79],
      borderColor: 'rgb(255, 99, 132)'
    }
  ]
}
```

### Comparison Bar Chart

Use `visualization_data.agent_comparison` for horizontal bar charts showing acceptance rates.

### Status Indicators

- **Trend Direction**:
  - 🟢 `improving`: Recent avg > older avg by 5%+
  - 🔴 `declining`: Recent avg < older avg by 5%+
  - 🟡 `stable`: Within ±5%
  - ⚪ `insufficient_data`: Less than 2 data points

- **Fine-tuning Readiness**:
  - ✅ `ready: true` + avg > 0.6: Ready to fine-tune
  - ⚠️ `ready: true` + avg < 0.6: Review prompts first
  - ❌ `ready: false`: Need more settlements

---

## 🎯 Use Cases

### 1. Notion Dashboard Integration

Create a Notion page with embedded API calls (via webhook or Zapier):

```markdown
# Agent Performance Dashboard

## Overall Metrics
- **Average Acceptance Rate**: 75%
- **Total Settlements**: 150
- **Top Performer**: The Quant (82%)

## Agent Trends
- The Quant: 🟢 Improving (+8%)
- The Entrepreneur: 🟡 Stable
- The Auditor: 🔴 Declining (-3%)

## Action Items
- [ ] Review Auditor's low-acceptance patterns
- [ ] Fine-tune dataset is ready (150 records)
```

### 2. Automated Reporting

Combine with Daily Digest to include performance metrics:

```python
# In daily_digest.py
dashboard = PerformanceDashboard()
overview = await dashboard.get_dashboard_overview(time_range="7d")

# Include in digest
digest["agent_performance"] = overview["agent_summaries"]
```

### 3. Real-time Monitoring

Set up alerts based on dashboard metrics:

```yaml
# alerting_rules.yml
- alert: LowAgentAcceptance
  expr: agent_acceptance_rate < 0.6
  annotations:
    summary: "Agent {{ $labels.agent_name }} has low acceptance rate"
```

---

## 🔧 Technical Details

### Data Source

All dashboard data comes from:
- **Notion DB_Training_Data**: Settlement diffs and acceptance rates
- **TrainingAnalytics**: Pre-computed aggregations and trends
- **EditPatternAnalyzer**: Pattern detection in user modifications

### Performance

- **Caching**: Consider caching dashboard data for 5-10 minutes
- **Query Time**: ~2-5 seconds for 30-day overview with 150 records
- **Rate Limits**: Notion API (3 req/sec) applies to data fetching

### Data Quality

Dashboard accuracy depends on:
- ✅ Settlement diffs logged via `/log-settlement`
- ✅ `Agent_Name` property configured in DB_Training_Data
- ✅ `Diff_Logged` checkbox used to prevent duplicates

---

## 🚀 Getting Started

1. **Collect Training Data**:
   ```bash
   # Log settlement after each AI generation
   curl -X POST https://web-production-3d888.up.railway.app/log-settlement \
     -H "Content-Type: application/json" \
     -d '{"intent_id": "...", "original_plan": {...}, "final_plan": {...}}'
   ```

2. **View Dashboard**:
   ```bash
   curl https://web-production-3d888.up.railway.app/dashboard/overview
   ```

3. **Analyze Specific Agent**:
   ```bash
   curl https://web-production-3d888.up.railway.app/dashboard/agent/The%20Entrepreneur
   ```

4. **Compare All Agents**:
   ```bash
   curl https://web-production-3d888.up.railway.app/dashboard/compare
   ```

---

## 📝 Response Status Codes

- `200`: Success
- `404`: Agent not found (check agent name spelling)
- `500`: Server error (check logs)

### Special Status Values

- `status: "no_data"`: No training records found
- `status: "insufficient_data"`: Less than 2 agents with data (for comparisons)
- `status: "success"`: Dashboard generated successfully

---

## 💡 Tips

1. **Time Ranges**: Use shorter ranges (7d) for recent trends, longer (90d/all) for overall patterns
2. **Trend Direction**: Requires at least 10 settlements per agent for accuracy
3. **Agent Names**: Must match exact values from Agent Registry (use `/agents` to list)
4. **URL Encoding**: Use `%20` for spaces in agent names (e.g., `The%20Entrepreneur`)

---

## 📞 Support

For questions or issues:
- Check application logs: `Railway Logs`
- Verify training data: `GET /training-data/summary`
- Test agent analytics: `GET /analytics/agents`

---

**Last Updated**: 2026-02-23
**API Version**: 1.0.0
