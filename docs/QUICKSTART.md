# Executive Mind Matrix - Quick Start Guide

Get up and running in 5 minutes. This is your cheat sheet for daily use.

---

## 5-Minute Setup (If Already Deployed)

### 1. Access Your Notion Workspace

Open these databases:
- **System Inbox** (your primary input)
- **Executive Intents** (strategic decisions)
- **Tasks** (your action items)

### 2. Add Your First Intent

In **System Inbox**:
```
Title: Test - Should I use this system?
Content: I want to see how the AI analyzes decisions
Status: [Leave empty]
```

### 3. Wait 2-3 Minutes

The poller runs every 2 minutes. Watch the magic:
- Status changes to "Triaged_to_Intent"
- New entry appears in **Executive Intents**
- AI analysis automatically added to the intent page

### 4. Review the Analysis

Open the new intent in **Executive Intents**:
- See AI classification (risk, impact, agent assignment)
- Review 3 scenario options with pros/cons
- Check recommended option and rationale

### 5. Make Your Decision

- Approve the recommendation as-is, OR
- Edit fields to match your preference, OR
- Run dialectic analysis for more perspectives

**Done!** You've completed your first intent workflow.

---

## Daily Workflow Cheat Sheet

### Morning Ritual (5-10 min)

```
1. [ ] Add 3-5 intents to System Inbox
2. [ ] Review yesterday's analyzed intents
3. [ ] Check Tasks for today's priorities
```

### Midday Check (10 min)

```
1. [ ] Review new Executive Intents
2. [ ] Run dialectic on high-stakes decisions (impact 8+)
3. [ ] Approve ready actions
```

### End of Day (5 min)

```
1. [ ] Update task statuses
2. [ ] Archive completed intents
3. [ ] Quick glance at Execution Log
```

---

## Common Commands

### Health Check

```bash
curl https://your-app.up.railway.app/health
```

Good response: `"status": "healthy", "poller_active": true`

### Manual Poll (Force Processing)

```bash
curl -X POST https://your-app.up.railway.app/trigger-poll
```

Use when: Intent not processing after 5 minutes

### Run Dialectic Analysis

```bash
# Get intent ID from Notion URL
curl -X POST https://your-app.up.railway.app/dialectic/{intent_id}
```

Use when: High-stakes decision, need multiple perspectives

### Approve Action

```bash
curl -X POST https://your-app.up.railway.app/action/{action_id}/approve
```

Or: Just set `Approval_Status = "Approved"` in Notion

### Spawn Tasks from Action

```bash
curl -X POST https://your-app.up.railway.app/action/{action_id}/spawn-tasks
```

Creates individual tasks and project automatically

---

## Dashboard URLs

### Primary Databases (Bookmark These)

```
System Inbox:
https://notion.so/{workspace}/[your_database_id]

Executive Intents:
https://notion.so/{workspace}/[your_database_id]

Tasks:
https://notion.so/{workspace}/[your_database_id]

Action Pipes:
https://notion.so/{workspace}/[your_database_id]
```

### API Health Dashboard

```
https://your-app.up.railway.app/health
```

### Railway Logs

```
https://railway.app/project/{your_project_id}/deployments
```

---

## Notion Database Quick Reference

| Database | When to Use | What You Do |
|----------|-------------|-------------|
| **System Inbox** | Daily | Add all requests here |
| **Executive Intents** | Daily | Review AI analysis, make decisions |
| **Action Pipes** | Weekly | Approve decisions, review synthesis |
| **Tasks** | Daily | Update status, complete items |
| **Projects** | Weekly | Track multi-task initiatives |
| **Areas** | Setup only | Define life/work domains |
| **Knowledge Nodes** | Passive | Auto-populated from reference content |
| **Agent Registry** | Setup only | Define AI agent personas |
| **Execution Log** | Analytics | Audit trail of all actions |
| **Training Data** | Analytics | AI learning history |

---

## Intent Classification Quick Guide

### How to Write Strategic Intents

**Pattern**: "Should I [Option A] or [Option B]?"

**Examples**:
- "Should I hire in-house or outsource?"
- "Which feature should we build: payments or analytics?"
- "Should I invest in VTI or Bitcoin?"

**Include**:
- 2-3 clear options
- Budget/constraints
- Timeline
- Current state

### How to Write Operational Tasks

**Pattern**: "[Action verb] [specific thing]"

**Examples**:
- "Schedule Q1 team offsite"
- "Send contract to legal for review"
- "Follow up with prospect about proposal"

**Include**:
- Clear action required
- Deadline (if time-sensitive)
- Context (who, what, where)

### How to Write Reference Content

**Pattern**: "[Type]: [Topic/Title]"

**Examples**:
- "Article: Zero-based budgeting framework"
- "Notes: Key takeaways from CEO conference"
- "Research: Best practices for remote hiring"

**Include**:
- Source/link
- Key concepts
- Why it's relevant

---

## Keyboard Shortcuts

### Notion Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + N` | New page |
| `Cmd/Ctrl + K` | Link to another page |
| `@` | Mention/link |
| `//` | Insert block |
| `/table` | Create database |
| `Cmd/Ctrl + Shift + P` | Move to different database |

### Shell Aliases (Optional)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Executive Mind Matrix shortcuts
export EMM_URL="https://your-app.up.railway.app"

alias emm-health="curl $EMM_URL/health"
alias emm-poll="curl -X POST $EMM_URL/trigger-poll"
alias emm-logs="railway logs --tail 50"

function emm-dialectic() {
    curl -X POST "$EMM_URL/dialectic/$1"
}

function emm-approve() {
    curl -X POST "$EMM_URL/action/$1/approve"
}
```

Usage:
```bash
emm-health
emm-poll
emm-dialectic abc123def456
emm-approve def456ghi789
```

---

## Troubleshooting Quick Fixes

### Intent Not Processing

**Symptom**: Status stays "Unprocessed" for >5 minutes

**Quick Fix**:
```bash
# Check if poller is running
curl https://your-app.up.railway.app/health

# Manually trigger
curl -X POST https://your-app.up.railway.app/trigger-poll
```

### Wrong Classification

**Symptom**: Strategic intent classified as Operational

**Quick Fix**:
1. Rephrase to include multiple options
2. Add "Should I...?" to the beginning
3. Manually move to Executive Intents in Notion

### Agent Analysis Seems Off

**Symptom**: Recommendations don't match expectations

**Quick Fix**:
1. Run dialectic for second opinion
2. Check if enough context was provided
3. Edit the recommendation (system learns from this)

### Tasks Not Creating

**Symptom**: Approved action doesn't spawn tasks

**Quick Fix**:
```bash
# Manually trigger task spawning
curl -X POST https://your-app.up.railway.app/action/{action_id}/spawn-tasks
```

### System Slow

**Symptom**: Everything takes >5 minutes

**Quick Fix**:
1. Check Railway metrics (RAM/CPU)
2. Check Anthropic API status
3. Increase polling interval temporarily:
   ```bash
   railway variables set POLLING_INTERVAL_SECONDS=300
   ```

---

## Performance Tips

### Speed Up Analysis

- **Use Haiku model** (10x faster, 10x cheaper than Sonnet)
- **Skip dialectic** for low-stakes decisions (impact <7)
- **Batch intents** (add multiple at once, let poller process all)

### Reduce Costs

```bash
# Switch to Haiku if using Sonnet
railway variables set ANTHROPIC_MODEL="claude-3-haiku-20240307"

# Reduce polling frequency
railway variables set POLLING_INTERVAL_SECONDS=300  # 5 minutes
```

**Cost impact**: ~$5/month (vs. $50/month for Sonnet)

### Improve Accuracy

- **Provide more context** in Content field
- **Run dialectic** for critical decisions
- **Edit recommendations** (trains the system)
- **Review acceptance rates** monthly and fine-tune

---

## Best Practices Cheat Sheet

### DO

- ✅ Add intents daily (make it a habit)
- ✅ Provide clear context and constraints
- ✅ Run dialectic for decisions >$5k or impact 8+
- ✅ Edit recommendations thoughtfully (system learns)
- ✅ Update task statuses daily
- ✅ Review agent performance weekly

### DON'T

- ❌ Write vague intents ("Need help with X")
- ❌ Skip context (budget, timeline, options)
- ❌ Approve blindly without reading analysis
- ❌ Ignore conflict points in dialectic
- ❌ Let tasks pile up without status updates
- ❌ Forget to check Execution Log for patterns

---

## Weekly Maintenance (10 min)

```
1. [ ] Review agent performance metrics
       curl https://your-app.up.railway.app/analytics/agents/summary?time_range=7d

2. [ ] Check Execution Log for anomalies
       (Open in Notion, sort by Decision_Date desc)

3. [ ] Archive completed intents
       (Move to "Done" status or separate database)

4. [ ] Review Railway usage
       (Dashboard → Metrics → Check RAM/CPU)

5. [ ] Update task statuses
       (Mark completed tasks as "Completed")
```

---

## Quick Reference: Decision Matrix

Use this to decide which workflow to follow:

| Decision Type | Budget | Impact | Timeline | Workflow |
|---------------|--------|--------|----------|----------|
| Strategic (multi-option) | >$1k | 7+ | >1 week | Executive Intent → Dialectic → Action |
| Strategic (simple) | <$1k | 5-6 | <1 week | Executive Intent → Single Agent |
| Operational | Any | <5 | <1 day | Direct to Tasks |
| Reference | N/A | N/A | N/A | Knowledge Nodes |

---

## Getting More Help

### Documentation

- **User Guide**: Detailed daily usage → [USER-GUIDE.md](USER-GUIDE.md)
- **Deployment**: Setup instructions → [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)
- **Architecture**: Technical deep dive → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Executive Summary**: High-level overview → [README-EXECUTIVE.md](README-EXECUTIVE.md)

### Logs & Monitoring

```bash
# Railway logs (last 100 lines)
railway logs --tail 100

# Local logs (if running locally)
tail -f logs/app.log

# Health check
curl https://your-app.up.railway.app/health
```

### Common Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `"poller_active": false` | Poller crashed | Restart: `railway restart` |
| `"status": "unhealthy"` | Database connection issue | Check Notion API key |
| `429 Too Many Requests` | Rate limit hit | Wait 60 seconds, reduce frequency |
| `404 Not Found` | Intent/Action not found | Check ID is correct |
| `500 Internal Server Error` | Backend crash | Check Railway logs |

---

## Example Workflows

### Scenario 1: Hiring Decision (Strategic, High Stakes)

**Input** (System Inbox):
```
Title: Should I hire senior engineer or outsource?
Content:
Need engineering capacity. Budget: $150k/year.
Options:
- Hire senior engineer ($150k)
- Outsource to agency ($75/hr)
- Hybrid (junior + agency)
Timeline: 3 months
```

**Workflow**:
1. Wait 2 min → Intent auto-created
2. Review Entrepreneur's analysis
3. Run dialectic for Risk perspective
4. Review synthesis and conflicts
5. Approve hybrid option
6. Spawn tasks: interview, contract, onboard

**Time**: 15 minutes decision → 30 minutes total

---

### Scenario 2: Team Event (Operational, Simple)

**Input** (System Inbox):
```
Title: Schedule Q1 team offsite
Content: Plan offsite for 25 people in Austin, Q1 2026
```

**Workflow**:
1. Wait 2 min → Task auto-created
2. Check Tasks database
3. Add details and set due date
4. Complete task steps

**Time**: 2 minutes decision → execute over days

---

### Scenario 3: Learning Note (Reference, Passive)

**Input** (System Inbox):
```
Title: Article - Zero-based budgeting
Content: [Paste article or key points]
```

**Workflow**:
1. Wait 2 min → Knowledge Nodes auto-created
2. AI extracts concepts and categories
3. Auto-tagged for future reference
4. No further action needed

**Time**: 0 minutes (passive)

---

## Success Metrics (Track These)

### Weekly

- Number of intents processed
- Average acceptance rate
- Tasks completed vs. created
- Dialectic analyses run

### Monthly

- Agent performance trends
- Decisions by category (Strategic/Operational/Reference)
- Time saved vs. manual analysis
- Cost (Railway + Anthropic)

### Quarterly

- Consider fine-tuning if acceptance rate <70%
- Review and update agent prompts
- Evaluate ROI (time saved vs. cost)

---

## Emergency Contacts

### System Down

```bash
# Check Railway status
railway status

# Restart service
railway restart

# View logs for errors
railway logs --tail 100
```

### Data Issues

- **Notion backup**: Settings → Export all content
- **Environment backup**: `railway variables > backup.txt`
- **Code backup**: Git commit + push

### Cost Spike

- Check Anthropic usage: https://console.anthropic.com
- Reduce polling frequency
- Switch to Haiku model
- Set spending alerts

---

**Keep this guide bookmarked for quick reference. Most common tasks take <2 minutes once you're familiar with the system.**

---

## Next Steps

Now that you have the quick reference:

1. **Bookmark** the Notion databases you use daily
2. **Set up** shell aliases for common commands
3. **Add** your first real strategic decision
4. **Review** results after 1 week of use
5. **Adjust** agent prompts based on acceptance rates

**Happy deciding! The system learns as you use it, so consistency is key.**
