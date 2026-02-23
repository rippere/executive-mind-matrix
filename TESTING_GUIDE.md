# Executive Mind Matrix - Testing Guide

Quick guides for testing each system component.

---

## Test 1: Poller (2 minutes)

**Verify the 2-minute polling loop works end-to-end.**

### Steps

1. **Create a test intent in Notion**
   - Open your **DB_System_Inbox** database in Notion
   - Click **"New"** to create a new page
   - Fill in:
     - **Title:** "Test Strategic Intent - [Your Name]"
     - **Content:** "Evaluate expanding our product line to include AI-powered analytics tools"
     - **Type:** Select "Strategic" (or whatever triggers intent routing)
   - **Save** the page

2. **Wait 2 minutes** (one polling cycle)

3. **Check DB_Executive_Intents**
   - Open **DB_Executive_Intents** database
   - Look for your test intent
   - Should appear with:
     - Status: "Pending" or "In_Analysis"
     - Source link back to System Inbox
     - Agent assigned

4. **Check Railway logs** (optional)
   ```bash
   railway logs --tail 50 | grep -i "processing.*intent"
   ```

   **Expected output:**
   ```
   Processing intent: Test Strategic Intent
   Created Executive Intent: [intent-id]
   ```

### Success Criteria

- ✅ Intent moved from System Inbox to Executive Intents
- ✅ System Inbox shows "Triaged_to_Intent" status
- ✅ Executive Intent has Source relation back to inbox
- ✅ Agent assigned to intent

### Troubleshooting

**Intent not processed after 2 minutes:**
- Check poller status: `curl https://web-production-3d888.up.railway.app/health`
- Verify `"poller_active": true`
- Check Railway logs for errors: `railway logs --tail 100`

**Intent created but missing fields:**
- Check Notion schema matches expected properties
- Verify all required properties exist in DB_Executive_Intents

---

## Test 2: Dialectic Analysis (3 minutes)

**Test the full adversarial agent workflow: Entrepreneur vs Quant vs Auditor.**

### Prerequisites

- Have an Executive Intent created (from Test 1, or existing)
- Know the Intent ID (copy from Notion URL)

### Steps

1. **Get an Intent ID**
   - Open an Executive Intent in Notion
   - Copy the ID from the URL:
     ```
     https://notion.so/workspace/[intent-id-here]
                               ^^^^^^^^^^^^^^^^
     ```

2. **Trigger dialectic analysis**
   ```bash
   curl -X POST https://web-production-3d888.up.railway.app/dialectic/[intent-id] | jq
   ```

   Replace `[intent-id]` with your actual ID.

3. **Wait 30-60 seconds** (LLM processing time)

4. **Check the response**
   ```json
   {
     "status": "success",
     "intent_id": "...",
     "action_id": "...",
     "message": "Dialectic analysis complete and Action Pipe created",
     "synthesis": "...",
     "recommended_path": "...",
     "conflict_points": [...],
     "growth_recommendation": "Option 1",
     "risk_recommendation": "Option 2"
   }
   ```

5. **Verify in Notion**
   - Open **DB_Action_Pipes**
   - Find the new Action Pipe
   - Should contain:
     - **Scenario_Options** - Full dialectic analysis
     - **Recommended_Option** - Growth perspective choice
     - **Risk_Assessment** - Conflict analysis
     - **AI Raw Output** - Page body with full JSON (🔒 callout)
     - **Approval_Status** - "Pending"
     - **Consensus** - True/False (did agents agree?)

### Success Criteria

- ✅ Action Pipe created in < 60 seconds
- ✅ Synthesis includes all 3 agent perspectives
- ✅ Conflict points identified (if agents disagreed)
- ✅ AI Raw Output stored as page blocks (not truncated)
- ✅ Intent links to Action Pipe

### Troubleshooting

**Timeout (> 60 seconds):**
- Anthropic API may be slow - wait up to 2 minutes
- Check Railway logs: `railway logs --tail 50 | grep -i error`

**Missing AI Raw Output:**
- Should be in page body as a 🔒 callout + code block
- If missing, check Railway logs for block append errors

**Agent assignment missing:**
- Verify DB_Agent_Registry has pages for The Entrepreneur, The Quant, The Auditor
- Check that Agent_Persona relation exists on Executive Intents

---

## Test 3: Action Approval & Task Spawning (2 minutes)

**Complete the workflow: Approve action → Spawn tasks.**

### Steps

1. **Get an Action Pipe ID**
   - From Test 2 response, copy `action_id`
   - Or open an Action Pipe in Notion and copy ID from URL

2. **Approve the action**
   ```bash
   curl -X POST https://web-production-3d888.up.railway.app/action/[action-id]/approve
   ```

3. **Spawn tasks from the action**
   ```bash
   curl -X POST https://web-production-3d888.up.railway.app/action/[action-id]/spawn-tasks | jq
   ```

4. **Check response**
   ```json
   {
     "status": "success",
     "action_id": "...",
     "intent_id": "...",
     "tasks_created": 5,
     "project_created": true,
     "project_id": "...",
     "task_ids": ["...", "...", ...],
     "message": "Created 5 tasks and 1 project"
   }
   ```

5. **Verify in Notion**
   - Open **DB_Tasks** - Should see 5 new tasks
   - Open **DB_Projects** - Should see 1 new project
   - Tasks should link to the project
   - Tasks should link to the source intent

### Success Criteria

- ✅ Action approval updates Approval_Status to "Approved"
- ✅ Tasks created with proper titles from template
- ✅ Project created and linked to tasks
- ✅ Tasks link back to source intent

---

## Test 4: Training Data Collection (5 minutes)

**Verify diff logging captures human edits vs AI suggestions.**

### Steps

1. **Complete Test 2** (create an Action Pipe)

2. **Edit the Action Pipe in Notion**
   - Open the Action Pipe page
   - Change **Recommended_Option** from "Option 1" to "Option 2"
   - Edit **Scenario_Options** text (add/remove a sentence)
   - Save changes

3. **Approve the action** (this triggers diff logging)
   ```bash
   curl -X POST https://web-production-3d888.up.railway.app/action/[action-id]/approve
   ```

4. **Check DB_Training_Data**
   - Open **DB_Training_Data** database
   - Find the newest entry
   - Should contain:
     - **Intent** relation to source
     - **Agent_Name** (e.g., "The Entrepreneur")
     - **User_Modifications** (JSON list of changes)
     - **Acceptance_Rate** (percentage accepted)
     - **Original_Plan** (AI suggestion)
     - **Final_Plan** (your edits)

5. **Verify analytics**
   ```bash
   curl https://web-production-3d888.up.railway.app/analytics/agents/summary | jq
   ```

   Should now show non-zero settlements:
   ```json
   {
     "overall": {
       "total_settlements": 1,
       "avg_acceptance_rate": 0.75
     },
     "agents": {
       "The Entrepreneur": {
         "total_analyses": 1,
         "avg_acceptance_rate": 0.75
       }
     }
   }
   ```

### Success Criteria

- ✅ Training record created in DB_Training_Data
- ✅ Agent_Name populated correctly
- ✅ User_Modifications shows your edits
- ✅ Acceptance_Rate calculated (0.0 - 1.0)
- ✅ Analytics endpoint returns data

---

## Test 5: Prometheus Metrics (1 minute)

**Verify monitoring data is being collected.**

### Steps

1. **Fetch metrics**
   ```bash
   curl -s https://web-production-3d888.up.railway.app/metrics | grep -E "poller|anthropic|notion"
   ```

2. **Check for custom metrics**
   ```bash
   # Poller metrics
   curl -s https://web-production-3d888.up.railway.app/metrics | grep poller_status

   # Anthropic API usage
   curl -s https://web-production-3d888.up.railway.app/metrics | grep anthropic_api_calls

   # Error tracking
   curl -s https://web-production-3d888.up.railway.app/metrics | grep errors_total
   ```

### Expected Output

```
# HELP poller_status Current status of the poller (1=running, 0=stopped)
# TYPE poller_status gauge
poller_status 1.0

# HELP anthropic_api_calls_total Total Anthropic API calls
# TYPE anthropic_api_calls_total counter
anthropic_api_calls_total 15.0

# HELP errors_total Total errors by component
# TYPE errors_total counter
errors_total{component="notion_poller"} 0.0
errors_total{component="agent_router"} 2.0
```

### Success Criteria

- ✅ Metrics endpoint returns data
- ✅ Custom metrics (poller_status, anthropic_api_calls) present
- ✅ Error counters tracking failures

---

## Full Integration Test (10 minutes)

**End-to-end workflow test combining all components.**

### Workflow

1. **Create intent in System Inbox** → Wait 2 min → Verify in Executive Intents
2. **Trigger dialectic** → Wait 1 min → Verify Action Pipe created
3. **Edit the action in Notion** (change recommendation)
4. **Approve action** → Verify training data logged
5. **Spawn tasks** → Verify in DB_Tasks and DB_Projects
6. **Check analytics** → Verify settlement recorded

### Full Success Criteria

- ✅ Intent routed from Inbox → Intents (poller)
- ✅ Dialectic created Action Pipe (agent router)
- ✅ Human edits captured (diff logger)
- ✅ Tasks spawned from action (task spawner)
- ✅ All metrics incremented (monitoring)
- ✅ No errors in Railway logs

### Timing

- Inbox → Intent: **2 minutes** (polling)
- Intent → Action: **30-60 seconds** (LLM)
- Approval → Training: **< 5 seconds** (database)
- Action → Tasks: **< 5 seconds** (database)
- **Total:** ~5-10 minutes end-to-end

---

## Common Issues & Solutions

### Poller Not Running

```bash
# Check health
curl https://web-production-3d888.up.railway.app/health | jq '.poller_active'

# If false, check Railway logs
railway logs --tail 100 | grep -i "poller"

# Look for startup errors
railway logs --tail 100 | grep -i error
```

### Anthropic API Errors

```bash
# Check API key is set
railway variables | grep ANTHROPIC

# Check for rate limits
railway logs | grep -i "429\|rate limit"

# Check for quota errors
railway logs | grep -i "quota\|billing"
```

### Notion API Errors

```bash
# Check all database IDs are set
curl https://web-production-3d888.up.railway.app/health | jq '.databases_configured'

# All should be true
# If false, check Railway variables
railway variables | grep NOTION_DB
```

### Training Data Not Captured

**Check Notion schema:**
- DB_Training_Data has `Agent_Name` property (Select type)
- DB_Action_Pipes has `Diff_Logged` property (Checkbox type, capital L)

**Check code:**
```bash
railway logs | grep -i "settlement\|diff"
```

---

## Testing Checklist

Use this for regular system verification:

- [ ] Health check returns `poller_active: true`
- [ ] System Inbox intent routes to Executive Intents (< 2 min)
- [ ] Dialectic creates Action Pipe with full analysis (< 60 sec)
- [ ] Action approval logs training data
- [ ] Task spawning creates tasks + project
- [ ] Analytics endpoint returns settlement data
- [ ] Prometheus metrics update
- [ ] No errors in Railway logs (last 100 lines)

---

**All tests passing?** Your system is fully operational! 🎉
