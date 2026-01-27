# Executive Brain + Existing GTD System: Integration Architecture

## System Layers

```
┌─────────────────────────────────────────────────────────────┐
│           LAYER 1: EXECUTIVE BRAIN (Strategic)              │
│  DB_Executive_Intents → DB_Action_Pipes → DB_Execution_Log  │
│              ↓ (generates)                                   │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│        LAYER 2: OPERATIONAL SYSTEM (Tactical/GTD)           │
│      DB_Tasks ← DB_Projects ← DB_Areas ← DB_Nodes           │
└─────────────────────────────────────────────────────────────┘
```

**Flow**: Executive Intent → Agent Analysis → Approved Action → Generated Task/Project in GTD system

---

## Database Mapping (What to Keep vs. Create)

### Keep & Enhance (Existing)
1. **DB_Tasks** - Keep as-is
   - Add new relation: `Source_Intent` (links to DB_Executive_Intents)
   - Add property: `Generated_by_Agent` (checkbox) - marks auto-generated tasks

2. **DB_Projects** - Keep as-is
   - Add relation: `Source_Intent` (links to DB_Executive_Intents)
   - Strategic intents can spawn entire projects

3. **DB_Areas** - Keep as-is
   - Use for categorizing both Tasks and Intents
   - Add relation to DB_Executive_Intents

4. **DB_Nodes** - Dual-purpose enhancement
   - **Add Type property**: Select (Entity, System_Component, Knowledge)
   - Serves as both DB_Entities_CRM and system metadata
   - Add relations to DB_Executive_Intents

### Create New (Executive Brain Layer)
5. **DB_Executive_Intents** - NEW (the command center)
   - See original spec from plan
   - Add relation: `Outputs_to_Project` (links to DB_Projects)
   - Add relation: `Outputs_to_Tasks` (links to DB_Tasks)

6. **DB_Agent_Registry** - NEW (agent configs)
   - See original spec from plan

7. **DB_Action_Pipes** - NEW (staging area)
   - See original spec from plan

8. **DB_Execution_Log** - NEW (audit trail)
   - See original spec from plan

9. **DB_System_Inbox** - NEW (input triage)
   - See original spec from plan
   - Can route to DB_Tasks (operational) OR DB_Executive_Intents (strategic)

### Optional (Can Merge)
10. **DB_Knowledge_Vault** → **Merge into DB_Nodes**
    - Add `Type = "Knowledge"` filter view in DB_Nodes
    - DB_Nodes already handles system components, just add knowledge assets

---

## Revised Database Schemas

### 1. DB_Executive_Intents (NEW - Strategic Layer)

**Core Properties** (unchanged from plan):
- Intent_ID, Title, Description, Agent_Persona, Status, Risk_Level
- Projected_Impact, Success_Criteria, Due_Date, Priority

**NEW Integration Properties**:
- `Area` (Relation to DB_Areas) - Which life domain?
- `Spawned_Project` (Relation to DB_Projects) - If intent created a project
- `Spawned_Tasks` (Relation to DB_Tasks) - Tasks generated from this intent
- `Related_Nodes` (Relation to DB_Nodes) - Entities/concepts involved

**Example Intent**:
- Title: "Launch YouTube channel for brand awareness"
- Agent: The Entrepreneur
- Spawned_Project: "Q1 2026 YouTube Strategy" (in DB_Projects)
- Spawned_Tasks: "Research competitor channels", "Script first video" (in DB_Tasks)

---

### 2. DB_Nodes (ENHANCED - Hybrid Entity/Knowledge/Meta)

**Existing Properties**: (keep whatever you have)

**NEW Properties to Add**:
- `Node_Type` (Select) - Options: Entity_Person, Entity_Company, Knowledge_Asset, System_Component
- `Related_Intents` (Relation to DB_Executive_Intents)
- `Entity_Relationship` (Select) - Client, Partner, Mentor, Competitor (only for Entity types)
- `Knowledge_Tags` (Multi-select) - For Knowledge_Asset types

**Views**:
- **Entities View**: Filter Node_Type contains "Entity"
- **Knowledge Base**: Filter Node_Type = "Knowledge_Asset"
- **System Map**: Filter Node_Type = "System_Component"

---

### 3. DB_Tasks (ENHANCED - Add Intent Tracking)

**Existing Properties**: (keep all)

**NEW Properties to Add**:
- `Source_Intent` (Relation to DB_Executive_Intents) - Links back to strategic decision
- `Auto_Generated` (Checkbox) - Was this created by agent workflow?
- `Agent_Context` (Rollup from Source_Intent → Agent_Persona) - Which agent created this?

**Why This Matters**:
- You can filter: "Show me all tasks from The Entrepreneur agent"
- You can trace: "This task came from Intent #47"

---

### 4. DB_Projects (ENHANCED - Add Intent Tracking)

**Existing Properties**: (keep all)

**NEW Properties to Add**:
- `Source_Intent` (Relation to DB_Executive_Intents)
- `Strategic_Outcome` (Rollup from Source_Intent → Success_Criteria)

---

### 5. DB_Action_Pipes (NEW - Agent Output Staging)

**All Properties**: (see original plan - unchanged)

**NEW Property**:
- `Task_Generation_Template` (Long Text) - When approved, what tasks should be created?
  - Example: "[ ] Research X\n[ ] Build Y\n[ ] Test Z"

---

### 6. DB_System_Inbox (NEW - Input Queue)

**Core Properties**: (see original plan)

**NEW Property**:
- `Triage_Destination` (Select) - Strategic (Intent), Operational (Task), Reference (Node)

---

## Make.com Workflow Revisions

### Workflow 1: Inbox Triage (Enhanced)
**Changes**: Now routes to 3 destinations instead of 2

```
If Claude determines:
- "Strategic decision needed" → Create DB_Executive_Intents entry
- "Quick action" → Create DB_Tasks entry directly
- "Reference/knowledge" → Create DB_Nodes entry (Type = Knowledge_Asset)
```

**API Prompt**:
```json
{
  "content": "Triage this input:\n\n{inbox_content}\n\nClassify as:\n- 'strategic' (requires decision analysis, multiple options, or high impact)\n- 'operational' (clear next action, can execute immediately)\n- 'reference' (knowledge to store)\n\nRespond in JSON:\n{\n  \"type\": \"strategic|operational|reference\",\n  \"title\": \"...\",\n  \"agent\": \"Entrepreneur|Quant|Auditor\" (if strategic),\n  \"risk\": \"Low|Medium|High\" (if strategic),\n  \"impact\": 1-10,\n  \"next_action\": \"...\" (if operational)\n}"
}
```

---

### Workflow 3: Agent Executor (Enhanced)
**Changes**: Now includes task generation template

**Steps** (revised):
1-6. (Same as original plan)
7. **NEW**: When creating DB_Action_Pipes entry, agent also provides `Task_Generation_Template`
8. Send notification

**Agent Prompt Addition**:
```
In your response JSON, also include:

"task_generation_template": [
  "Research X competitor strategies",
  "Draft Y proposal",
  "Schedule Z meeting"
]
```

---

### Workflow 4: Settlement Processor (Enhanced - Now Creates Tasks/Projects)
**Changes**: Executes the approved action by generating GTD entities

**Steps** (revised):
1. Fetch approved Action Pipe record
2. Create entry in DB_Execution_Log
3. **NEW**: Parse `Task_Generation_Template` from Action Pipe
4. **NEW**: For each task in template:
   - Create entry in DB_Tasks
   - Set `Source_Intent` = current Intent
   - Set `Auto_Generated` = TRUE
5. **NEW (Optional)**: If action requires a project:
   - Create entry in DB_Projects
   - Link to Intent via `Source_Intent`
6. Update Intent status to "Executed"
7. Update Intent relations: `Spawned_Tasks`, `Spawned_Project`

**Make.com Module Example** (Create Task):
```json
{
  "Title": "{task_from_template}",
  "Source_Intent": "{intent_id}",
  "Auto_Generated": true,
  "Area": "{intent_area}",
  "Status": "Next Actions"
}
```

---

## Example End-to-End Flow

### Scenario: "Should I invest $5k in index funds or crypto?"

**Step 1: Inbox Entry**
- You dump this question into DB_System_Inbox

**Step 2: Triage (Workflow 1)**
- Claude classifies as "strategic" (financial decision, needs analysis)
- Creates DB_Executive_Intents:
  - Title: "Invest $5k: Index Funds vs Crypto"
  - Agent: The Quant
  - Risk: Medium
  - Status: Ready

**Step 3: Smart Router (Workflow 2)**
- Detects Status = "Ready", Risk = "Medium"
- Auto-assigns to The Quant agent
- Status → "Assigned"

**Step 4: Agent Analysis (Workflow 3)**
- Fetches Intent + Quant's system prompt
- Calls Claude API
- Quant agent responds with 3 options:
  - **Option A**: 80% VTI, 20% BTC (balanced)
  - **Option B**: 100% VOO (conservative)
  - **Option C**: 50% ETH, 50% BTC (aggressive)
- Creates DB_Action_Pipes entry with scenario table + task template:
  ```
  [ ] Open Vanguard account
  [ ] Set up recurring buys
  [ ] Document allocation in portfolio tracker
  ```
- Status → "Pending_Approval"

**Step 5: You Review in Notion**
- Open DB_Action_Pipes → "Pending Approval" view
- Read scenario analysis
- Add User_Notes: "Go with Option A, but 85/15 split"
- Change Approval_Status → "Approved"

**Step 6: Settlement (Workflow 4)**
- Creates DB_Execution_Log entry
- Generates 3 tasks in DB_Tasks:
  - "Open Vanguard account" (Source_Intent = #47, Auto_Generated = TRUE)
  - "Set up recurring buys"
  - "Document allocation in portfolio tracker"
- Updates Intent: Status → "Executed", Spawned_Tasks → [3 task links]

**Step 7: You Execute in GTD**
- See 3 new tasks in DB_Tasks → "Next Actions" view
- Complete them as normal
- Each task links back to Intent #47 for context

---

## Revised Implementation Checklist

### Phase 1: Enhance Existing Databases (1 hour)
- [ ] Add `Source_Intent` relation to DB_Tasks
- [ ] Add `Auto_Generated` checkbox to DB_Tasks
- [ ] Add `Source_Intent` relation to DB_Projects
- [ ] Add `Node_Type` select to DB_Nodes
- [ ] Add `Related_Intents` relation to DB_Nodes
- [ ] Create "Entities", "Knowledge", "System" views in DB_Nodes

### Phase 2: Create New Executive Databases (2 hours)
- [ ] Create DB_Executive_Intents (with Area relation to DB_Areas)
- [ ] Create DB_Agent_Registry
- [ ] Create DB_Action_Pipes
- [ ] Create DB_Execution_Log
- [ ] Create DB_System_Inbox
- [ ] Set up all relations (Intents ↔ Action_Pipes, Intents → Tasks, etc.)

### Phase 3: Seed Data (30 min)
- [ ] Populate DB_Agent_Registry with 3 agents
- [ ] Create test Intent manually
- [ ] Verify relations work (create test task linked to Intent)

### Phase 4: Make.com Workflows (5 hours)
- [ ] Workflow 1: Enhanced Triage (3-way routing)
- [ ] Workflow 2: Smart Router
- [ ] Workflow 3: Agent Executor (with task template generation)
- [ ] Workflow 4: Enhanced Settlement (creates tasks in DB_Tasks)
- [ ] Workflow 5: Daily Digest

### Phase 5: Testing (1 hour)
- [ ] Test strategic input → Intent → Analysis → Tasks
- [ ] Test operational input → Direct to DB_Tasks
- [ ] Test reference input → DB_Nodes
- [ ] Verify task links back to source Intent

---

## Key Differences from Original Plan

1. **DB_Knowledge_Vault** merged into DB_Nodes (Type = "Knowledge_Asset")
2. **Settlement now generates tasks** in your existing DB_Tasks (not just logs)
3. **Inbox triages to 3 destinations** (Intent, Task, Node)
4. **All layers connected** via Source_Intent relations for full traceability

---

## Visual Map

```
INPUT LAYER:
DB_System_Inbox
    ├─ Strategic → DB_Executive_Intents (new)
    ├─ Operational → DB_Tasks (existing)
    └─ Reference → DB_Nodes (existing)

STRATEGIC LAYER:
DB_Executive_Intents
    ├─ Analyzed by → DB_Agent_Registry (new)
    ├─ Outputs to → DB_Action_Pipes (new)
    ├─ Logged in → DB_Execution_Log (new)
    └─ Generates ↓

OPERATIONAL LAYER:
DB_Projects (existing, enhanced)
    └─ Contains → DB_Tasks (existing, enhanced)
                     └─ Linked to → DB_Nodes (existing, enhanced)
                                       └─ Grouped by → DB_Areas (existing)
```

---

## What to Build Next

Based on your existing structure, here's the priority order:

**Immediate (Phase 1)**:
1. Add 5 new properties to existing databases (30 min)
2. Create DB_Executive_Intents (30 min)
3. Create DB_Action_Pipes (15 min)

**Next (Phase 2)**:
4. Build Make.com Workflow 3 (Agent Executor) first - this is the core value
5. Test manually by creating an Intent and triggering the workflow

**Later (Phase 3)**:
6. Add Workflow 4 (Settlement → Task Generation)
7. Add Workflow 1 (Inbox Triage)
8. Add Workflow 2 (Smart Router)
9. Add Workflow 5 (Daily Digest)

Want me to provide specific Notion property configs or Make.com module JSON for any of these?
