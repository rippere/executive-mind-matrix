# Notion Property Setup Guide

## Critical Database Property: AI_Raw_Output

### Overview
The `AI_Raw_Output` property is essential for maintaining training data integrity. It stores the original AI-generated analysis in a read-only field, preventing data corruption when users edit the human-facing fields.

---

## Why This Property is Critical

### The Problem Without It:
1. AI generates analysis → Saves to `Scenario_Options` field
2. User edits `Scenario_Options` directly
3. Original AI output is **LOST**
4. Diff logger compares "Edited" vs "Edited"
5. **Result**: Diff = 0, acceptance rate = 100% (FALSE DATA)

This corrupts the entire training data asset and makes it impossible to learn from user preferences.

### The Solution:
Store AI output in TWO places:
- **User-facing fields** (editable): `Scenario_Options`, `Recommended_Option`
- **Locked field** (read-only): `AI_Raw_Output`

The diff logger compares `AI_Raw_Output` (original) vs `Scenario_Options` (edited) to get accurate metrics.

---

## Setup Instructions

### Database: DB_Action_Pipes

**Add New Property:**

```
Property Name: AI_Raw_Output
Property Type: Text (Rich Text)
Description: 🔒 LOCKED - Original AI output for diff comparison. DO NOT EDIT.
```

### Configuration in Notion UI:

1. Open your **Action Pipes** database in Notion
2. Click the `+` icon to add a new property
3. Name it: `AI_Raw_Output`
4. Select type: **Text** (or Rich Text)
5. Add description:
   ```
   🔒 LOCKED - Original AI output for training data analysis.
   DO NOT EDIT THIS FIELD - Used for calculating acceptance rates.
   ```

### Visual Indicator (Optional but Recommended):

Add an emoji prefix to make it visually clear this field is special:
```
🔒 AI_Raw_Output
```

Or use Notion's property color:
- Set property color to **Red** to indicate "do not edit"

---

## How It Works

### When AI Generates Analysis:

```python
# System writes to BOTH fields:
action_pipe = {
    "Scenario_Options": "Readable AI analysis for user review",
    "Recommended_Option": "Option A",
    "AI_Raw_Output": "{\"growth_perspective\": {...}, \"risk_perspective\": {...}}"
}
```

### When User Reviews and Edits:

User modifies:
- ✅ `Scenario_Options` (edit the analysis)
- ✅ `Recommended_Option` (change recommendation)
- ✅ `User_Notes` (add comments)
- ❌ `AI_Raw_Output` (DO NOT TOUCH - system field)

### When System Calculates Diff:

```python
# diff_logger compares:
original = parse_json(action_pipe["AI_Raw_Output"])  # Preserved
final = parse_text(action_pipe["Scenario_Options"])   # Edited

diff = calculate_diff(original, final)
acceptance_rate = calculate_acceptance(diff)  # Accurate!
```

---

## Data Format in AI_Raw_Output

The field stores a JSON string with this structure:

```json
{
  "growth_recommendation": "Option A - High upside potential",
  "risk_recommendation": "Option B - Conservative approach",
  "synthesis": "Balance growth and safety with 70/30 allocation",
  "recommended_path": "Start with Option B, transition to A after 6 months",
  "conflict_points": [
    "Risk tolerance mismatch",
    "Time horizon disagreement"
  ],
  "timestamp": "2026-01-27T14:30:00Z"
}
```

**Note**: Notion Text fields have a 2000 character limit. The system automatically truncates to fit.

---

## Migration for Existing Action Pipes

**Good News**: This is a non-breaking change!

- Existing Action Pipes without `AI_Raw_Output` will continue to work
- New Action Pipes will automatically populate the field
- Old entries can't be retroactively analyzed (no original data)
- Only new dialectic flows after adding this property will benefit from accurate diff logging

**No data loss** - you don't need to modify existing entries.

---

## Verification Checklist

After adding the property, verify it's working:

### 1. Check Property Exists
```bash
# Run a test dialectic flow
curl -X POST http://localhost:8000/dialectic/test_intent_123

# Check the Action Pipe in Notion
# Verify AI_Raw_Output field is populated with JSON
```

### 2. Test User Edit Flow
1. Create a test intent
2. Run dialectic analysis
3. Open resulting Action Pipe in Notion
4. Edit the `Scenario_Options` field
5. Check `AI_Raw_Output` field is unchanged

### 3. Test Diff Logger
```bash
# After editing, trigger settlement
curl -X POST http://localhost:8000/log-settlement \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id": "test_123",
    "original_plan": {...},
    "final_plan": {...}
  }'

# Check Training Data database
# Verify diff is accurately captured
```

---

## Troubleshooting

### Issue: Property Not Showing Up

**Solution**: Refresh Notion page, check spelling exactly matches `AI_Raw_Output`

### Issue: Field is Empty After Dialectic

**Possible Causes**:
1. Code hasn't been deployed yet (check if `_save_raw_ai_output` method exists in `app/agent_router.py`)
2. API error during save (check logs: `tail -f logs/app.log`)
3. Property name mismatch in code

**Fix**: Verify the code at `app/agent_router.py:366-425` has the property save logic.

### Issue: JSON is Truncated

**Expected Behavior**: Notion Text fields max out at 2000 chars. The system truncates with `[:2000]`.

**If you need more space**:
- Use a different property type (though Text is recommended for performance)
- Store only essential fields in the property
- Use external storage (S3, file system) with a reference ID in the property

---

## Security Considerations

### Access Control

Recommend setting property permissions (if using Notion's team features):
- **AI Bot**: Read/Write access
- **Admin Users**: Read/Write access (for troubleshooting only)
- **Regular Users**: Read-only access (enforced by documentation, not technical limitation)

**Note**: Notion doesn't have field-level permissions, so this relies on team discipline.

### Data Privacy

The `AI_Raw_Output` field contains:
- AI-generated recommendations
- Timestamp of analysis
- System metadata

**Does NOT contain**:
- User personal information
- API keys
- Sensitive credentials

Safe to store in Notion.

---

## Maintenance

### Regular Checks (Monthly):

1. **Verify data integrity**:
   ```bash
   curl http://localhost:8000/metrics/agent/The%20Entrepreneur
   # Check acceptance rates are varying (not stuck at 100%)
   ```

2. **Audit sample entries**:
   - Open 5-10 random Action Pipes
   - Verify `AI_Raw_Output` is populated
   - Check format matches expected JSON structure

3. **Review logs for errors**:
   ```bash
   grep "AI_Raw_Output" logs/app.log | grep -i error
   ```

---

## Related Documentation

- **Security Audit**: See `SECURITY_AUDIT_FIXES.md` (Issue #3)
- **Diff Logger**: See `app/diff_logger.py`
- **Agent Router**: See `app/agent_router.py:366-425`
- **Implementation Notes**: See `IMPLEMENTATION_IMPROVEMENTS.md`

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║  AI_Raw_Output - Quick Reference                          ║
╟───────────────────────────────────────────────────────────╢
║ Database:        DB_Action_Pipes                          ║
║ Type:            Text (Rich Text)                         ║
║ Purpose:         Store original AI output for diff logger ║
║ User Action:     DO NOT EDIT                              ║
║ System Action:   Auto-populated by dialectic flow         ║
║ Data Format:     JSON string (truncated at 2000 chars)    ║
║ Critical:        YES - Required for training data         ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Summary

**Action Required**: Add `AI_Raw_Output` property to **DB_Action_Pipes** in Notion.

**Impact**: Enables accurate training data capture and acceptance rate calculations.

**Effort**: 2 minutes

**Risk**: None (non-breaking change)

**Priority**: HIGH (required for training data integrity)

---

**Last Updated**: 2026-01-27
**Status**: Ready for Implementation
