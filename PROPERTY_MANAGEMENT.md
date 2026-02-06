# Property Management Guidelines

## Rule: NEVER Create New Properties Without Checking

Before adding ANY new property to a Notion database, you MUST:

### 1. Run the Property Audit

```bash
./venv/bin/python scripts/audit_database_properties.py
```

This generates `DATABASE_PROPERTY_MAP.md` showing all existing properties.

### 2. Check Existing Properties First

Consult `DATABASE_PROPERTY_MAP.md` to see what already exists in the target database.

### 3. Use the Property Validator (in code)

```python
from app.property_validator import validate_property_creation
from notion_client import AsyncClient

client = AsyncClient(auth=settings.notion_api_key)

# Before creating a new property
should_create = await validate_property_creation(
    client=client,
    database_id=settings.notion_db_action_pipes,
    database_name="Action Pipes",
    proposed_property="Agent_Recommendation",
    proposed_type="select",
    intended_use="Store which agent recommended what"
)

if not should_create:
    # Use existing property instead!
    # Check the alternatives suggested
    pass
```

## Identified Redundancies

### Action Pipes Database

**REDUNDANT (created unnecessarily):**
- ❌ `Entrepreneur_Recommendation` → Use `Recommended_Option` instead
- ❌ `Auditor_Recommendation` → Use `Recommended_Option` instead
- ❌ `Final_Decision` → Use `Recommended_Option` instead
- ❌ `Synthesis_Summary` → Use `Scenario_Options` or `Risk_Assessment` instead

**KEEP (has unique value):**
- ✅ `Consensus` → New boolean, not redundant (indicates agent agreement)

**EXISTING (should be used):**
- ✅ `Recommended_Option` - The canonical recommendation field
- ✅ `Scenario_Options` - Rich text for detailed analysis
- ✅ `Risk_Assessment` - Rich text for risk analysis
- ✅ `Required_Resources` - Resource requirements
- ✅ `Task_Generation_Template` - Action items

### Executive Intents Database

**NEW (acceptable):**
- ✅ `Decision_Made` - Short-form decision for table views (useful)
- ✅ `Conflict_Level` - Categorical conflict indicator (useful)

These are NOT redundant because they provide at-a-glance info in table views that doesn't exist elsewhere.

## Proper Property Usage

### When Creating Actions from Dialectic

**DON'T DO THIS:**
```python
properties={
    "Final_Decision": {...},           # REDUNDANT
    "Synthesis_Summary": {...},        # REDUNDANT
}
```

**DO THIS:**
```python
properties={
    "Recommended_Option": {            # EXISTING field
        "select": {"name": f"Option {result}"}
    },
    "Scenario_Options": {              # EXISTING field - use for full analysis
        "rich_text": [{"text": {"content": full_dialectic_text}}]
    },
    "Risk_Assessment": {               # EXISTING field - use for risk summary
        "rich_text": [{"text": {"content": risk_analysis}}]
    },
    "Consensus": {                     # NEW but justified - quick boolean check
        "checkbox": entrepreneur_rec == auditor_rec
    }
}
```

## Pre-Flight Checklist

Before adding a new property, answer:

1. ☑️ Does a property with this exact name already exist?
2. ☑️ Does a property with a similar name exist?
3. ☑️ Can an existing property serve this purpose?
4. ☑️ Have I consulted DATABASE_PROPERTY_MAP.md?
5. ☑️ Have I run the property validator?

Only create new properties if ALL checks pass.

## Deprecated Properties

**Status: As of 2026-02-02, these properties are DEPRECATED**

The following properties exist in Notion but are NO LONGER used in the codebase:

### Action Pipes - DEPRECATED
- ❌ `Entrepreneur_Recommendation` (select) - Use `Recommended_Option` instead
- ❌ `Auditor_Recommendation` (select) - Use `Recommended_Option` instead
- ❌ `Final_Decision` (select) - Use `Recommended_Option` instead
- ❌ `Synthesis_Summary` (rich_text) - Use `Scenario_Options` instead

**What happened:**
- Removed from main.py on 2026-02-02
- Code now only uses `Recommended_Option`, `Scenario_Options`, `Risk_Assessment`, `Consensus`
- Properties still exist in Notion but are not populated by any workflow

**Next steps:**
1. ✅ **DONE**: Removed from active code (main.py, workflow_integration.py)
2. **FUTURE**: After verifying no manual data entry, can be deleted from Notion schema

## Cleanup History

### 2026-02-02: Code Bloat Cleanup
- **Deleted dead Python files**:
  - `app/command_center_smart.py` (12.8KB)
  - `app/command_center_central.py` (19.6KB)
  - `app/command_center_fixed.py` (10.5KB)
- **Removed redundant property usage**:
  - Cleaned up main.py `/dialectic` endpoint
  - Now using only canonical properties
- **Total savings**: 43KB of dead code removed
