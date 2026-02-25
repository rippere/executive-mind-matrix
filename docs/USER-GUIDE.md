# Executive Mind Matrix - User Guide

Complete guide to using the system effectively on a daily basis.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Submitting Intents](#submitting-intents)
3. [Understanding Classifications](#understanding-classifications)
4. [Reading Agent Analysis](#reading-agent-analysis)
5. [Running Dialectic Analysis](#running-dialectic-analysis)
6. [Approving Actions](#approving-actions)
7. [Tracking Tasks](#tracking-tasks)
8. [Using the Performance Dashboard](#using-the-performance-dashboard)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Your Notion Workspace

The system uses 10 interconnected Notion databases:

| Database | Purpose | You Interact With |
|----------|---------|-------------------|
| **System Inbox** | Input queue for all requests | ✅ Primary |
| **Executive Intents** | Strategic decisions requiring analysis | ✅ Often |
| **Action Pipes** | Approved decisions ready for execution | ✅ Often |
| **Tasks** | Individual action items | ✅ Daily |
| **Projects** | Multi-task initiatives | ✅ Weekly |
| **Areas** | Life/work domains (e.g., Career, Finance) | ⚙️ Setup only |
| **Knowledge Nodes** | Reference concepts and frameworks | 📖 Reference |
| **Agent Registry** | AI agent personas | ⚙️ Setup only |
| **Execution Log** | Audit trail of all actions | 📊 Analytics |
| **Training Data** | AI learning history | 📊 Analytics |

### Daily Workflow

1. **Morning**: Add intents to System Inbox (5-10 min)
2. **Midday**: Review analyzed intents in Executive Intents (10-15 min)
3. **Afternoon**: Approve actions and check tasks (5-10 min)
4. **Evening**: Quick check for new completions (2 min)

**Total time**: ~30 minutes/day

---

## Submitting Intents

### How to Submit

1. Open your **System Inbox** database in Notion
2. Click "New" to create a new page
3. Fill in these fields:
   - **Input_Title**: Brief description (e.g., "Hire senior engineer?")
   - **Content**: Full context and details
   - **Source**: Where this came from (Email, Slack, Meeting, etc.)
   - **Received_Date**: Today's date
   - **Status**: Leave empty or set to "Unprocessed"

4. Save the page

The system polls every 2 minutes. Within 2-4 minutes, your intent will be processed.

### Writing Good Intents

#### Strategic Decisions

**Good**:
```
Title: Should I hire a full-time engineer or outsource to an agency?

Content:
We're scaling the product and need more engineering capacity. Budget is
$150k/year. Need to decide between:
- Hiring a senior full-stack engineer ($150k salary)
- Outsourcing to an agency ($75/hr, ~$120k/year)
- Hybrid approach (junior engineer + agency)

Current team: 2 engineers. Timeline: next 3 months.
```

**Why good**: Clear options, budget context, timeline, current state.

**Bad**:
```
Title: Engineering help

Content: Need more engineers
```

**Why bad**: No options, no context, no constraints.

#### Operational Tasks

**Good**:
```
Title: Schedule Q1 team offsite

Content:
Plan team offsite for Q1 2026. Need to:
- Find venue in Austin (25 people)
- Book flights for remote team
- Plan 2-day agenda
- Budget: $15k
```

**Why good**: Clear action, specific requirements, constraints.

#### Reference Content

**Good**:
```
Title: Zero-based budgeting framework

Content:
[Paste article or notes]

Key concepts:
- Justify every expense from zero base
- No carryover from previous budget
- Forces priority thinking
```

**Why good**: Clear that this is reference material, includes key takeaways.

---

## Understanding Classifications

After processing (2-4 minutes), check the **Triage_Destination** field in System Inbox:

### Strategic (Intent)

- **Indicator**: `Triage_Destination = "Strategic (Intent)"`
- **What happens**: Creates Executive Intent with AI analysis
- **Your action**: Review in Executive Intents database
- **Examples**:
  - "Should I hire X or Y?"
  - "Which product feature to build next?"
  - "Invest in stocks or crypto?"

### Operational (Task)

- **Indicator**: `Triage_Destination = "Operational (Task)"`
- **What happens**: Creates task directly in Tasks database
- **Your action**: Review and complete in Tasks
- **Examples**:
  - "Schedule team dinner"
  - "Send contract to legal"
  - "Follow up with client"

### Reference (Knowledge Node)

- **Indicator**: `Triage_Destination = "Reference (Node)"`
- **What happens**: Extracts concepts and creates knowledge nodes
- **Your action**: None required (stored for future reference)
- **Examples**:
  - "Article about OKR frameworks"
  - "Notes from conference talk"
  - "Research on hiring best practices"

---

## Reading Agent Analysis

### Where to Find It

1. Open **Executive Intents** database
2. Find your intent (status will be "Ready" or "Analyzed")
3. Open the page

### What You'll See

#### 1. AI Classification Results (Callout Box)

```
Original Request: Should I hire a senior engineer or outsource?

🟡 Risk Assessment: Medium
⚡ Impact Score: 7/10
🚀 Recommended Agent: The Entrepreneur

AI Rationale:
Hiring is a strategic decision with financial and team-building implications.
Medium risk due to cost commitment. High impact on team capability.
```

#### 2. Agent's Analysis

The assigned agent (Entrepreneur, Quant, or Auditor) provides:

**Recommended Option**: Option A (with rationale)

**Scenario Options**: 3 options with:
- Description
- Pros (3-5)
- Cons (3-5)
- Risk score (1-5)
- Impact score (1-10)

#### 3. Next Steps Checklist

- [ ] Review AI classification above
- [ ] Run dialectic analysis for multi-agent perspectives
- [ ] Review synthesis and make decision
- [ ] Create action items if needed

### How to Read Options

Each option looks like this:

```
Option A: Hire Senior Engineer ($150k/yr)

📝 Build internal capability with experienced hire. Invest in long-term
   team growth and knowledge retention.

✅ Pros:
   - Knowledge stays in-house
   - Builds team culture
   - Mentors junior engineers

⚠️ Cons:
   - Higher fixed cost ($150k/yr)
   - Recruitment time (2-3 months)
   - Risk of bad hire

Risk: 3/5 | Impact: 8/10
```

---

## Running Dialectic Analysis

### When to Use It

Run dialectic analysis when:
- **High stakes** (Impact 8+, or budget >$10k)
- **Conflicting priorities** (growth vs. risk vs. compliance)
- **You're unsure** which option is best
- **Team alignment** needed (share multiple perspectives)

### How to Trigger

#### Option 1: Via API (Recommended)

Find your intent ID:
1. Open the intent page in Notion
2. Copy the page URL (e.g., `https://notion.so/abc123def456`)
3. Extract the ID (last part of URL): `abc123def456`

Run the command:
```bash
curl -X POST https://your-railway-app.up.railway.app/dialectic/abc123def456
```

#### Option 2: Via Quick Actions (in Intent page)

Scroll to bottom of intent page, copy-paste the curl command shown.

### What Happens

1. **Growth Agent (Entrepreneur)** analyzes your intent
2. **Risk Agent (Auditor)** analyzes the same intent
3. **Synthesis AI** identifies conflicts and recommends a path

**Time**: ~45-60 seconds total

### Reading Dialectic Results

You'll see a new section added to your intent page:

#### Multi-Agent Dialectic Analysis

**Growth Perspective (The Entrepreneur)**
```
Recommendation: Option A
Focus: Revenue potential, scalability, market opportunity
```

**Risk Perspective (The Auditor)**
```
Recommendation: Option B
Focus: Compliance, governance, long-term sustainability
```

**Synthesis**
```
Both agents agree on the need for engineering capacity but disagree
on approach. Entrepreneur prioritizes team building; Auditor prioritizes
cost flexibility. Recommended path: Option C (hybrid approach) balances
both perspectives.
```

**Key Conflicts**
- Growth wants long-term capability; Risk wants short-term flexibility
- Growth accepts higher fixed costs; Risk minimizes financial commitment

---

## Approving Actions

### When an Intent is Ready

After reviewing analysis (single or dialectic), you make your decision.

### Creating an Action Pipe

#### Option 1: Via API
```bash
curl -X POST https://your-app.up.railway.app/intent/{intent_id}/create-action \
  -H "Content-Type: application/json" \
  -d '{
    "action_title": "Implement Hybrid Engineering Team",
    "action_description": "Execute Option C: Junior hire + agency support"
  }'
```

#### Option 2: Manual in Notion

1. Open **Action Pipes** database
2. Create new page
3. Link to your intent via "Intent" relation field
4. Fill in:
   - Action_Title
   - Recommended_Option
   - Task_Generation_Template (tasks to create)
   - Required_Resources

### Approving an Action

#### Option 1: Via API
```bash
curl -X POST https://your-app.up.railway.app/action/{action_id}/approve
```

#### Option 2: In Notion
1. Open Action Pipe page
2. Change `Approval_Status` to "Approved"
3. Set `Approved_Date` to today

**What happens**:
- Action marked as approved
- Settlement diff logged (AI learns from your edits)
- System ready to spawn tasks

### Spawning Tasks

Once approved, spawn tasks:

```bash
curl -X POST https://your-app.up.railway.app/action/{action_id}/spawn-tasks
```

**What happens**:
- Creates individual tasks in Tasks database
- Creates a project in Projects database (if multiple tasks)
- Links tasks to your intent for traceability

---

## Tracking Tasks

### Tasks Database

All tasks live in **Tasks** database:

- **Auto-generated tasks**: Have "Related Intents" linked
- **Manual tasks**: You can create these directly
- **Status**: Not started → In progress → Completed

### Projects Database

Multi-task initiatives:

- **Auto-generated**: When action spawns 3+ tasks
- **Linked to Intent**: Full traceability
- **Status tracking**: Overall progress bar

### Best Practices

1. **Daily review**: Check Tasks database every morning
2. **Update status**: Mark tasks "In progress" when started
3. **Complete promptly**: Mark "Completed" when done
4. **Add notes**: Document blockers or learnings in task body

---

## Using the Performance Dashboard

### Agent Performance

See which agents give the best recommendations:

```bash
GET /analytics/agents/summary?time_range=30d
```

**Returns**:
- Acceptance rate per agent (% of recommendations you kept)
- Total analyses run
- Top performers

### Improvement Opportunities

Identify where agents need better prompts:

```bash
GET /analytics/agent/The%20Entrepreneur/improvements?time_range=30d
```

**Returns**:
- Common rejection patterns
- Low-acceptance examples
- Suggested prompt improvements

### Agent Comparison

Head-to-head comparison:

```bash
GET /analytics/compare?agent_a=The%20Entrepreneur&agent_b=The%20Auditor
```

**Returns**:
- Acceptance rates
- Decision characteristics
- When to use each agent

---

## Best Practices

### For Strategic Decisions

1. **Be specific**: Include budget, timeline, options
2. **Provide context**: Current state, constraints, goals
3. **Run dialectic**: For decisions >$5k or impact 7+
4. **Review synthesis**: Don't just pick Option A blindly
5. **Edit thoughtfully**: Your edits train the system

### For Operational Tasks

1. **Keep it simple**: One clear action per task
2. **Include deadline**: Set due date if time-sensitive
3. **Link context**: Connect to related intents or projects
4. **Update status**: Keep Tasks database current

### For Reference Content

1. **Extract key points**: Don't just paste full articles
2. **Tag properly**: Help the AI categorize accurately
3. **Review nodes**: Check Knowledge Nodes for connections

### System Hygiene

**Daily**:
- [ ] Review new intents in Executive Intents
- [ ] Update task statuses

**Weekly**:
- [ ] Clean up completed tasks
- [ ] Review agent performance
- [ ] Archive old intents

**Monthly**:
- [ ] Review Execution Log for patterns
- [ ] Check Training Data for acceptance rates
- [ ] Consider fine-tuning if acceptance rate <70%

---

## Troubleshooting

### Intent Not Processing

**Symptoms**: Status stays "Unprocessed" for >5 minutes

**Solutions**:
1. Check Railway logs: `railway logs`
2. Verify poller is running: `GET /health`
3. Manually trigger: `POST /trigger-poll`
4. Check Status field is empty or "Unprocessed"

### Wrong Classification

**Symptoms**: Strategic decision classified as Operational

**Solutions**:
1. Rephrase input to be more explicit (e.g., "Should I..." not "Do this")
2. Include multiple options in Content field
3. Manually move to correct database
4. Log as training example for future improvement

### Agent Analysis Seems Off

**Symptoms**: Recommendations don't match your context

**Solutions**:
1. Check if you provided enough context
2. Try different agent: `POST /intent/{id}/assign-agent`
3. Run dialectic for multiple perspectives
4. Edit the recommendation (system learns from this)

### Tasks Not Spawning

**Symptoms**: Approved action doesn't create tasks

**Solutions**:
1. Verify Task_Generation_Template is filled
2. Manually trigger: `POST /action/{id}/spawn-tasks`
3. Check Tasks database for errors
4. Review Railway logs for exceptions

### System Slow

**Symptoms**: Polling takes >5 minutes

**Solutions**:
1. Check Railway metrics (RAM/CPU usage)
2. Reduce polling frequency in settings
3. Upgrade Railway plan if needed
4. Check Anthropic API rate limits

---

## Advanced Features

### Smart Router

Auto-assign best agent based on keywords:

```bash
POST /intent/{intent_id}/assign-agent
```

**Rules**:
- Financial keywords → The Quant
- Growth keywords → The Entrepreneur
- Compliance keywords → The Auditor
- High risk + high impact → The Auditor (safety first)

### Custom Agent Assignment

Override automatic assignment:

```bash
POST /intent/{intent_id}/assign-agent?projected_impact=9&risk_level=High
```

### Fine-Tuning Export

Export training data for model fine-tuning:

```bash
POST /analytics/export/fine-tuning?min_acceptance_rate=0.7
```

Creates JSONL file for Anthropic fine-tuning console.

---

## Keyboard Shortcuts & Tips

### Notion Shortcuts

- `Cmd/Ctrl + K`: Quick link to database
- `Cmd/Ctrl + Shift + P`: Move page to different database
- `@`: Mention/link to another page
- `//`: Insert block type

### API Shortcuts

Save these as shell aliases for faster access:

```bash
# In ~/.bashrc or ~/.zshrc
alias emm-health="curl https://your-app.up.railway.app/health"
alias emm-poll="curl -X POST https://your-app.up.railway.app/trigger-poll"
alias emm-dialectic="curl -X POST https://your-app.up.railway.app/dialectic/"
```

---

## Getting Help

### Documentation
- **Executive Overview**: [README-EXECUTIVE.md](README-EXECUTIVE.md)
- **Deployment Guide**: [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)
- **Architecture Deep Dive**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Quick Reference**: [QUICKSTART.md](QUICKSTART.md)

### Logs
- **Railway logs**: `railway logs --tail 100`
- **Local logs**: `logs/app.log`
- **Execution Log**: Check DB_Execution_Log in Notion

### Health Check
```bash
curl https://your-app.up.railway.app/health
```

Good response:
```json
{
  "status": "healthy",
  "poller_active": true,
  "polling_interval": 120
}
```

---

**You're now ready to use Executive Mind Matrix effectively. Start by adding 2-3 intents to System Inbox and see the magic happen!**
