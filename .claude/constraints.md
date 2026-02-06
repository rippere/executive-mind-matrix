# Claude Agent Constraints - Executive Mind Matrix

## CRITICAL: Property Creation Protocol

**BEFORE suggesting or creating ANY new Notion property, Claude MUST:**

### 1. Read the Property Map
```
Read: /home/rippere/Projects/executive-mind-matrix/DATABASE_PROPERTY_MAP.md
```

### 2. Check for Existing Properties
- Search the relevant database section for similar properties
- Check property names, types, and semantic overlaps
- Look for properties that could serve the same purpose

### 3. Justify New Properties
Only create new properties if:
- ✅ No existing property can serve the purpose
- ✅ The new property adds unique, non-redundant value
- ✅ It's explicitly requested by the user
- ✅ You've explicitly stated what existing properties you checked

### 4. Document Decision
When creating a new property, state:
- What existing properties were considered
- Why they can't be reused
- What unique value the new property adds

## Example: GOOD Process

```
User: "Add a field to track agent recommendations"

Claude: Let me check DATABASE_PROPERTY_MAP.md...

I found these existing properties in Action Pipes:
- Recommended_Option (select) - stores recommendations
- Scenario_Options (rich_text) - stores analysis
- Risk_Assessment (rich_text) - stores risk evaluation

Instead of creating a new property, we should use:
- Recommended_Option for the final decision
- Scenario_Options to include which agent said what

This avoids redundancy.
```

## Example: BAD Process (DO NOT DO THIS)

```
User: "Add a field to track agent recommendations"

Claude: I'll add these new properties:
- Entrepreneur_Recommendation
- Auditor_Recommendation
- Final_Decision

[Creates redundant properties without checking]
```

## Historical Mistakes to Avoid

**Past redundancy created on 2026-02-02:**
- Created `Entrepreneur_Recommendation`, `Auditor_Recommendation`, `Final_Decision`, `Synthesis_Summary`
- All were redundant with existing `Recommended_Option`, `Scenario_Options`, `Risk_Assessment`
- Should have checked DATABASE_PROPERTY_MAP.md first

## Workflow for Database Modifications

**EVERY TIME** before modifying database structure:

1. **Read** `DATABASE_PROPERTY_MAP.md`
2. **Identify** existing properties in target database
3. **Evaluate** if existing properties can be reused
4. **Propose** solution using existing properties first
5. **Only if necessary**, suggest new properties with full justification

## User Preference

The user prefers:
- ✅ Reusing existing properties
- ✅ Checking first, creating second
- ✅ Functional over "fluff" (icons, emojis)
- ✅ Practical implementation over unnecessary features
- ❌ Creating redundant properties
- ❌ Not checking what exists first

## Enforcement

This is a **HARD CONSTRAINT**. Violating this protocol creates technical debt and clutters the database schema. The user has explicitly requested this be part of Claude's operational guidelines.
