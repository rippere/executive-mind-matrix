# Missing Notion Properties Setup Guide

Two properties need to be manually added to your Notion databases for full functionality.

---

## Property 1: Agent_Name (DB_Training_Data)

**Purpose**: Tags settlement diffs with which agent generated the original plan, enabling per-agent performance analysis.

### Setup Steps:

1. **Open DB_Training_Data in Notion**
   - Navigate to your Training Data database
   - Click **"..."** (three dots) in top right
   - Select **"Customize page"**

2. **Add Agent_Name Property**
   - Click **"+ New property"**
   - Property name: `Agent_Name`
   - Property type: **Select**
   - Options (add all 3):
     - `The Entrepreneur`
     - `The Quant`
     - `The Auditor`
   - Click **"Create"**

3. **Position in View**
   - Drag `Agent_Name` column to appear after `Timestamp`
   - Recommended width: 150px

### Expected Result:

When settlement diffs are logged, the system will automatically tag them:
```
| Timestamp | Agent_Name       | Acceptance_Rate |
|-----------|------------------|-----------------|
| 2026-...  | The Entrepreneur | 85%             |
| 2026-...  | The Quant        | 92%             |
```

### Verification:

After adding, the property should appear in:
- `POST /training-data/summary` response (per-agent breakdown)
- `GET /training-data/agent/{agent_name}/improvements` filtering

---

## Property 2: Diff_Logged (DB_Action_Pipes)

**Purpose**: Prevents duplicate settlement diff logging when actions are re-processed by the poller.

### Setup Steps:

1. **Open DB_Action_Pipes in Notion**
   - Navigate to your Action Pipes database
   - Click **"..."** → **"Customize page"**

2. **Add Diff_Logged Property**
   - Click **"+ New property"**
   - Property name: `Diff_Logged`
   - Property type: **Checkbox**
   - Click **"Create"**

3. **Position in View**
   - Drag `Diff_Logged` to appear after `Approval_Status`
   - This helps visualize which actions have been captured

### Expected Result:

When an action is approved and settlement diff is logged:
```
| Action Title | Approval_Status | Diff_Logged |
|--------------|-----------------|-------------|
| Launch YT    | Approved        | ✅          |
| Review Q1    | Pending         |             |
```

### Verification:

After adding, you can:
- Filter view: `Diff_Logged` is not checked → See which approved actions haven't been logged yet
- Create automation: When `Approval_Status` = Approved AND `Diff_Logged` = unchecked → Log settlement

---

## Why These Are Manual

These properties require **schema changes** in Notion, which:
1. Cannot be done via API (Notion limitation)
2. Require database owner permissions
3. Are non-destructive (safe to add anytime)

The system will work without these properties, but with reduced functionality:
- **Without Agent_Name**: Training analytics won't show per-agent breakdowns
- **Without Diff_Logged**: Poller may log duplicate settlement diffs (wastes API quota)

---

## Alternative: Use Property Aliases

If you prefer different property names, update these files:

### For Agent_Name:
**File**: `app/diff_logger.py:189-192`
```python
# Change this:
properties["Agent_Name"] = {
    "select": {"name": agent_name}
}

# To your preferred name:
properties["Your_Custom_Name"] = {
    "select": {"name": agent_name}
}
```

### For Diff_Logged:
**File**: `app/workflow_integration.py:1007-1012`
```python
# Change this:
await self.client.pages.update(
    page_id=action_id,
    properties={"Diff_Logged": {"checkbox": True}}
)

# To your preferred name:
await self.client.pages.update(
    page_id=action_id,
    properties={"Your_Custom_Checkbox": {"checkbox": True}}
)
```

---

## Verification Commands

After adding properties, verify they're accessible:

### Test Agent_Name:
```bash
# Check DB_Training_Data schema
curl -X POST https://api.notion.com/v1/databases/YOUR_TRAINING_DB_ID/query \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  | jq '.results[0].properties | keys'

# Should include "Agent_Name"
```

### Test Diff_Logged:
```bash
# Check DB_Action_Pipes schema
curl -X POST https://api.notion.com/v1/databases/YOUR_ACTION_PIPES_ID/query \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  | jq '.results[0].properties | keys'

# Should include "Diff_Logged"
```

---

## Impact Timeline

### Without Properties (Current):
- ✅ Settlement diffs logged successfully
- ⚠️ No agent attribution (can't analyze which agent performs best)
- ⚠️ Potential duplicate logging (minor API quota waste)

### With Properties (After Adding):
- ✅ Full agent performance analytics
- ✅ Per-agent improvement detection
- ✅ No duplicate logging (idempotent operations)
- ✅ Ready for A/B testing different agent prompts

---

## Quick Add Checklist

- [ ] Open DB_Training_Data in Notion
- [ ] Add `Agent_Name` (Select: Entrepreneur, Quant, Auditor)
- [ ] Verify column appears in table view
- [ ] Open DB_Action_Pipes in Notion
- [ ] Add `Diff_Logged` (Checkbox)
- [ ] Verify column appears in table view
- [ ] Test by approving an action and checking if it gets checked
- [ ] Run training analytics endpoint to verify agent breakdown

**Time required**: 2-3 minutes per property = ~5 minutes total

---

*Last updated: 2026-02-23*
