# Executive Brain: Exact Setup Guide (REVISED CHRONOLOGICAL ORDER)
## Complete Step-by-Step Implementation

**IMPORTANT: Follow this guide in EXACT ORDER. Dependencies matter!**

This guide is now structured so you can follow it step-by-step without skipping sections or remembering to come back to things later.

---

# PART 1: CREATE NEW DATABASES

These databases have no dependencies on each other, but MUST be created before enhancing your existing databases.

---

## 1.1 DB_Agent_Registry (Agent Configurations)

**Create this FIRST - it has no dependencies.**

### Create Database
1. In Notion, type `/database` → "Table - Full page"
2. Name: `DB_Agent_Registry`

### Add Properties

**Auto-created**:
- `Name` (Text) - Rename to `Agent_Name`

**Property 1: Focus_Area**
1. Name: `Focus_Area`
2. Type: **Text**

**Property 2: Risk_Tolerance**
1. Name: `Risk_Tolerance`
2. Type: **Select**
3. Options:
   - `Conservative` (Green)
   - `Moderate` (Yellow)
   - `Aggressive` (Red)

**Property 3: System_Prompt**
1. Name: `System_Prompt`
2. Type: **Text** (will expand to long text)

**Property 4: Auto_Route_Criteria**
1. Name: `Auto_Route_Criteria`
2. Type: **Text**

**Property 5: Output_Template**
1. Name: `Output_Template`
2. Type: **Text**

**Property 6: Active**
1. Name: `Active`
2. Type: **Checkbox**

**Property 7: API_Model**
1. Name: `API_Model`
2. Type: **Select**
3. Options:
   - `claude-sonnet-4-5` (Default)
   - `claude-opus-4-5` (Premium)
   - `gpt-4o` (OpenAI)
   - `gpt-4o-mini` (Fast)

**Property 8: Assigned_Intents** (Relation - will auto-create)
- This will appear automatically when you create DB_Executive_Intents
- Leave blank for now

**Property 9: Generated_Actions** (Relation - will auto-create)
- This will appear automatically when you create DB_Action_Pipes
- Leave blank for now

### Seed Data - Create 3 Agent Entries

**Entry 1: The Entrepreneur**
1. Click "+ New" in DB_Agent_Registry
2. Fill in:
   - **Agent_Name**: `The Entrepreneur`
   - **Focus_Area**: `Scale to $100k/mo - Revenue, Growth, Scalability`
   - **Risk_Tolerance**: `Aggressive`
   - **Active**: ✅ Checked
   - **API_Model**: `claude-sonnet-4-5`
   - **System_Prompt**:
```
You are The Entrepreneur, a growth-focused operator in a personal Aladdin system.

FOCUS: Revenue generation, audience reach, and scalability. Your job is to analyze opportunities that move the needle toward $100k/mo.

When evaluating options, prioritize:
- Revenue potential (direct and indirect monetization)
- Scalability (can this 10x without linear resource increase?)
- Speed to market (how fast can we launch and iterate?)
- Competitive moats (defensibility, unique advantages)
- Customer acquisition efficiency (CAC, LTV)

Red flags to call out:
- Low-margin businesses (<30% gross margin)
- Over-reliance on single customer or channel
- High operational complexity with low automation potential
- Commoditized offerings with no differentiation

Provide 3 distinct strategic options with clear revenue projections.
```
   - **Output_Template**:
```json
{
  "scenario_options": [
    {
      "option": "A",
      "description": "2-3 sentence description of approach",
      "pros": ["Revenue potential: $X/mo", "Scalability factor: X", "Other advantage"],
      "cons": ["Risk or limitation", "Resource requirement", "Other concern"],
      "risk": 2,
      "impact": 8
    }
  ],
  "recommended_option": "A",
  "recommendation_rationale": "Why this option best achieves growth goals",
  "risk_assessment": "Overall risk analysis across options",
  "required_resources": {
    "time": "X hours/week for Y weeks",
    "money": "$X upfront, $Y recurring",
    "tools": ["Tool 1", "Tool 2"],
    "people": ["Role or person needed"]
  },
  "revenue_projection": "Expected revenue: $X/mo by month Y",
  "task_generation_template": ["Task 1", "Task 2", "Task 3"]
}
```
   - **Auto_Route_Criteria**: `Risk = Low OR Risk = Medium`

**Entry 2: The Quant**
1. Create new entry
2. Fill in:
   - **Agent_Name**: `The Quant`
   - **Focus_Area**: `Alpha generation, risk-adjusted returns, Euclidean decision models`
   - **Risk_Tolerance**: `Conservative`
   - **Active**: ✅ Checked
   - **API_Model**: `claude-sonnet-4-5`
   - **System_Prompt**:
```
You are The Quant, a quantitative analyst in a personal Aladdin system.

FOCUS: Financial decisions, portfolio optimization, risk-adjusted returns. You evaluate using mathematical rigor and probabilistic thinking.

When evaluating options, calculate:
- Expected Value (EV = Probability × Outcome for each scenario)
- Downside protection (maximum loss in worst-case scenario)
- Sharpe ratio equivalent (return per unit of risk)
- Correlation with existing portfolio/income streams
- Time horizon and compounding effects
- Kelly Criterion for position sizing (where applicable)

Use Euclidean decision models:
- Map options in risk/return space
- Calculate distance from optimal frontier
- Identify dominated strategies (worse on all dimensions)

Terminology:
- "Alpha": Returns above market/benchmark
- "Beta": Correlation with broader market
- "Drawdown": Peak-to-trough decline
- "Volatility": Standard deviation of returns

Provide 3 options with quantitative risk/reward profiles.
```
   - **Output_Template**: (Same JSON structure as Entrepreneur, including task_generation_template)
   - **Auto_Route_Criteria**: `Risk = Low AND Impact >= 5`

**Entry 3: The Auditor**
1. Create new entry
2. Fill in:
   - **Agent_Name**: `The Auditor`
   - **Focus_Area**: `Governance, compliance, mission alignment, long-term sustainability`
   - **Risk_Tolerance**: `Conservative`
   - **Active**: ✅ Checked
   - **API_Model**: `claude-sonnet-4-5`
   - **System_Prompt**:
```
You are The Auditor, the risk and compliance officer in a personal Aladdin system.

FOCUS: Governance, ethical alignment, mission integrity, long-term reputation. You are the "should we?" agent, not just the "can we?" agent.

When evaluating options, check against:
- Mission alignment: Does this serve the 2026 vision? (Refer to Knowledge Vault if available)
- Ethical considerations: Impact on others, sustainability, social good
- Legal/regulatory compliance: Licensing, taxes, disclosure requirements
- Long-term reputation risk: How does this look in 5 years?
- Dependency risk: Does this compromise autonomy or create lock-in?
- Reversibility: Can we undo this decision if it goes wrong?

Automatic REJECT signals (flag these prominently):
- Violates stated core values
- Creates existential risk (financial, legal, reputational)
- Requires unethical behavior or regulatory violations
- Locks into non-reversible dependencies

For financial decisions, validate:
- Tax implications are understood
- Legal structure is appropriate
- Regulatory requirements are met

Provide 3 options with clear pass/fail governance assessment.
```
   - **Output_Template**: (Same JSON structure, including task_generation_template)
   - **Auto_Route_Criteria**: `Risk = High` (Auditor reviews all high-risk)

---

## 1.2 DB_Executive_Intents (The Command Center)

**Create this SECOND - depends on DB_Agent_Registry.**

### Create Database
1. In Notion, click "+ New Page" or type `/database` → "Table - Full page"
2. Name: `DB_Executive_Intents`

### Add Properties (in order)

**Auto-created**:
- `Name` (Text) - **Rename this to `Title`**

**Property 1: Intent_ID**
1. Click "+ Add property"
2. Name: `Intent_ID`
3. Type: **Number** → Format: **Number with commas**
4. You'll manually number these (1, 2, 3...)

**Property 2: Description**
1. Name: `Description`
2. Type: **Text** (will auto-expand to long text)

**Property 3: Agent_Persona**
1. Name: `Agent_Persona`
2. Type: **Relation**
3. Target: **DB_Agent_Registry** (select the database you just created)
4. ✅ Enable "Show on DB_Agent_Registry" (appears as `Assigned_Intents`)

**Property 4: Status**
1. Name: `Status`
2. Type: **Select**
3. Add Options (in this exact order):
   - `Inbox` (Gray)
   - `Ready` (Blue)
   - `Assigned` (Yellow)
   - `In_Analysis` (Orange)
   - `Pending_Approval` (Purple)
   - `Approved` (Green)
   - `Executed` (Dark Green)
   - `Archived` (Light Gray)

**Property 5: Risk_Level**
1. Name: `Risk_Level`
2. Type: **Select**
3. Add Options:
   - `Low` (Green)
   - `Medium` (Yellow)
   - `High` (Red)

**Property 6: Projected_Impact**
1. Name: `Projected_Impact`
2. Type: **Number**
3. Format: Number (1-10 scale)

**Property 7: Success_Criteria**
1. Name: `Success_Criteria`
2. Type: **Text**

**Property 8: Due_Date**
1. Name: `Due_Date`
2. Type: **Date**

**Property 9: Created_Date**
1. Name: `Created_Date`
2. Type: **Created time**

**Property 10: Priority**
1. Name: `Priority`
2. Type: **Select**
3. Add Options:
   - `P0` (Red) - Critical
   - `P1` (Orange) - High
   - `P2` (Yellow) - Normal
   - `P3` (Green) - Low

**Property 11: Area**
1. Name: `Area`
2. Type: **Relation**
3. Target: **DB_Areas** (your existing database)
4. ✅ Enable "Show on DB_Areas" (appears as `Related_Intents`)

### Formula Properties

**Property 12: Days_Since_Creation**
1. Click "+ Add property"
2. Name: `Days_Since_Creation`
3. Type: **Formula**
4. Formula:
```
dateBetween(now(), prop("Created_Date"), "days")
```

**Property 13: Urgency_Score**
1. Name: `Urgency_Score`
2. Type: **Formula**
3. Formula:
```
if(prop("Priority") == "P0", 100, if(prop("Priority") == "P1", 75, if(prop("Priority") == "P2", 50, 25))) + prop("Days_Since_Creation")
```

**Property 14: Status_Indicator**
1. Name: `Status_Indicator`
2. Type: **Formula**
3. Formula:
```
if(prop("Status") == "Pending_Approval", "🟡 " + prop("Status"), if(prop("Status") == "Executed", "🟢 " + prop("Status"), if(prop("Status") == "In_Analysis", "🔵 " + prop("Status"), if(prop("Status") == "Assigned", "🟠 " + prop("Status"), "⚪ " + prop("Status")))))
```

### Auto-Created Relations (will appear later)

These properties will auto-create when you build the other databases. Don't worry about them now:
- `Source` (from DB_System_Inbox - creates later)
- `Related_Actions` (from DB_Action_Pipes - creates later)
- `Execution_Record` (from DB_Execution_Log - creates later)
- `Spawned_Tasks` (from DB_Tasks - creates in Part 2)
- `Spawned_Project` (from DB_Projects - creates in Part 2)
- `Related_Nodes` (from DB_Nodes - creates in Part 2)

### Create Views

**View 1: All Intents** (Default Table)
- Already exists
- Sort by: `Created_Date` (newest first)

**View 2: Inbox**
1. Click "+ New" → "Table view"
2. Name: "Inbox"
3. Filter: `Status` → `is` → `Inbox` OR `Status` → `is` → `Ready`
4. Sort: `Priority` descending, then `Created_Date` descending

**View 3: Active Intents**
1. Create new Table view: "Active"
2. Filter: `Status` → `is any of` → Select: `Assigned`, `In_Analysis`
3. Sort: `Urgency_Score` descending

**View 4: Pending Approval**
1. Create new Table view: "⏳ Pending Approval"
2. Filter: `Status` → `is` → `Pending_Approval`
3. Sort: `Created_Date` descending

**View 5: By Agent** (Board)
1. Create new Board view: "By Agent"
2. Group by: `Agent_Persona`
3. Filter: `Status` → `is not` → `Executed` AND `is not` → `Archived`

**View 6: By Risk**
1. Create new Board view: "By Risk"
2. Group by: `Risk_Level`
3. Filter: `Status` → `is not` → `Executed`

**View 7: Completed**
1. Create new Table view: "Completed"
2. Filter: `Status` → `is` → `Executed`
3. Sort: `Created_Date` descending

---

## 1.3 DB_Action_Pipes (Agent Output Staging)

**Create this THIRD.**

### Create Database
1. Type `/database` → "Table - Full page"
2. Name: `DB_Action_Pipes`

### Add Properties

**Auto-created**:
- `Name` (Text) - **Rename to `Action_Title`**

**Property 1: Action_ID**
1. Name: `Action_ID`
2. Type: **Number** → Unique ID or auto-number

**Property 2: Intent**
1. Name: `Intent`
2. Type: **Relation**
3. Target: **DB_Executive_Intents**
4. ✅ Enable "Show on DB_Executive_Intents" (appears as `Related_Actions`)

**Property 3: Agent**
1. Name: `Agent`
2. Type: **Relation**
3. Target: **DB_Agent_Registry**
4. ✅ Enable "Show on DB_Agent_Registry" (appears as `Generated_Actions`)

**Property 4: Analysis_Date**
1. Name: `Analysis_Date`
2. Type: **Created time**

**Property 5: Scenario_Options**
1. Name: `Scenario_Options`
2. Type: **Text** (will expand for markdown table)

**Property 6: Recommended_Option**
1. Name: `Recommended_Option`
2. Type: **Select**
3. Options:
   - `Option A`
   - `Option B`
   - `Option C`

**Property 7: Risk_Assessment**
1. Name: `Risk_Assessment`
2. Type: **Text**

**Property 8: Required_Resources**
1. Name: `Required_Resources`
2. Type: **Text**

**Property 9: Task_Generation_Template**
1. Name: `Task_Generation_Template`
2. Type: **Text**
3. This will contain checklist of tasks to create on approval

**Property 10: Approval_Status**
1. Name: `Approval_Status`
2. Type: **Select**
3. Options:
   - `Pending` (Yellow) - Default
   - `Approved` (Green)
   - `Rejected` (Red)
   - `Needs_Revision` (Orange)

**Property 11: User_Notes**
1. Name: `User_Notes`
2. Type: **Text**

**Property 12: Approved_Date**
1. Name: `Approved_Date`
2. Type: **Date**

### Create Views

**View 1: Pending Approval**
1. Create Table view: "Pending"
2. Filter: `Approval_Status` → `is` → `Pending`
3. Sort: `Analysis_Date` descending

**View 2: Approved (Ready for Settlement)**
1. Create Table view: "Approved"
2. Filter: `Approval_Status` → `is` → `Approved`
3. Sort: `Approved_Date` descending

**View 3: By Agent**
1. Create Board view: "By Agent"
2. Group by: `Agent`
3. Filter: `Approval_Status` → `is not` → `Rejected`

---

## 1.4 DB_Execution_Log (Audit Trail)

**Create this FOURTH.**

### Create Database
1. Type `/database` → "Table - Full page"
2. Name: `DB_Execution_Log`

### Add Properties

**Auto-created**:
- `Name` (Text) - **Rename to `Log_Entry_Title`**

**Property 1: Log_ID**
1. Name: `Log_ID`
2. Type: **Number** (auto-increment manually)

**Property 2: Intent**
1. Name: `Intent`
2. Type: **Relation**
3. Target: **DB_Executive_Intents**
4. ✅ Enable "Show on DB_Executive_Intents" (appears as `Execution_Record`)

**Property 3: Action_Taken**
1. Name: `Action_Taken`
2. Type: **Text**

**Property 4: Decision_Date**
1. Name: `Decision_Date`
2. Type: **Date**

**Property 5: Executor**
1. Name: `Executor`
2. Type: **Select**
3. Options:
   - `You` (your name)
   - `The Entrepreneur`
   - `The Quant`
   - `The Auditor`
   - `External Party`

**Property 6: Outcome**
1. Name: `Outcome`
2. Type: **Text**

**Property 7: Actual_vs_Projected**
1. Name: `Actual_vs_Projected`
2. Type: **Text**
3. Document: Did results match the scenario prediction?

**Property 8: Lessons_Learned**
1. Name: `Lessons_Learned`
2. Type: **Text**

**Property 9: Settlement_Date**
1. Name: `Settlement_Date`
2. Type: **Created time**

### Create Views

**View 1: Recent Executions**
1. Default Table view
2. Sort: `Settlement_Date` descending

**View 2: By Intent**
1. Create Table view: "By Intent"
2. Group by: `Intent`

---

## 1.5 DB_System_Inbox (Input Queue)

**Create this FIFTH.**

### Create Database
1. Type `/database` → "Table - Full page"
2. Name: `DB_System_Inbox`

### Add Properties

**Auto-created**:
- `Name` (Text) - **Rename to `Input_Title`**

**Property 1: Inbox_ID**
1. Name: `Inbox_ID`
2. Type: **Number**

**Property 2: Content**
1. Name: `Content`
2. Type: **Text**

**Property 3: Source**
1. Name: `Source`
2. Type: **Select**
3. Options:
   - `Email`
   - `Web Clipper`
   - `Quick Add`
   - `API`
   - `Voice Note`
   - `Manual Entry`

**Property 4: Received_Date**
1. Name: `Received_Date`
2. Type: **Created time**

**Property 5: Status**
1. Name: `Status`
2. Type: **Select**
3. Options:
   - `Unprocessed` (Red)
   - `Triaged_to_Intent` (Blue)
   - `Triaged_to_Task` (Green)
   - `Triaged_to_Node` (Purple)
   - `Archived` (Gray)

**Property 6: Triage_Destination**
1. Name: `Triage_Destination`
2. Type: **Select**
3. Options:
   - `Strategic (Intent)`
   - `Operational (Task)`
   - `Reference (Node)`

**Property 7: Routed_to_Intent**
1. Name: `Routed_to_Intent`
2. Type: **Relation**
3. Target: **DB_Executive_Intents**
4. ✅ Enable "Show on DB_Executive_Intents" (appears as `Source`)

**Property 8: Routed_to_Task**
1. Name: `Routed_to_Task`
2. Type: **Relation**
3. Target: **DB_Tasks** (your existing database)

**Property 9: Routed_to_Node**
1. Name: `Routed_to_Node`
2. Type: **Relation**
3. Target: **DB_Nodes** (your existing database)

### Create Views

**View 1: Unprocessed**
1. Create Table view: "🔴 Unprocessed"
2. Filter: `Status` → `is` → `Unprocessed`
3. Sort: `Received_Date` ascending (oldest first)

**View 2: Processed Today**
1. Create Table view: "Today"
2. Filter: `Received_Date` → `is today`
3. Sort: `Received_Date` descending

---

# PART 2: ENHANCE EXISTING DATABASES

**Now that all new databases exist, we can add the relations and rollups to your existing databases.**

---

## 2.1 DB_Tasks (Enhancements)

### New Properties to Add

**Property 1: Source_Intent**
1. Open DB_Tasks in Notion
2. Click "+ Add a property"
3. Property Name: `Source_Intent`
4. Property Type: **Relation**
5. Select relation target: **DB_Executive_Intents**
6. ✅ Enable "Show on DB_Executive_Intents" (this creates bidirectional relation)
7. In DB_Executive_Intents, this will appear as: `Spawned_Tasks`

**Property 2: Auto_Generated**
1. In DB_Tasks, click "+ Add a property"
2. Property Name: `Auto_Generated`
3. Property Type: **Checkbox**
4. Default: Unchecked

**Property 3: Agent_Context** (Rollup)
1. In DB_Tasks, click "+ Add a property"
2. Property Name: `Agent_Context`
3. Property Type: **Rollup**
4. Relation: Select `Source_Intent`
5. Property: Select `Agent_Persona` (this now exists!)
6. Calculate: "Show original"
7. This will show which agent created the task (e.g., "The Entrepreneur")

---

## 2.2 DB_Projects (Enhancements)

### New Properties to Add

**Property 1: Source_Intent**
1. Open DB_Projects
2. Click "+ Add a property"
3. Property Name: `Source_Intent`
4. Property Type: **Relation**
5. Target: **DB_Executive_Intents**
6. ✅ Enable "Show on DB_Executive_Intents"
7. In DB_Executive_Intents, this appears as: `Spawned_Project`

**Property 2: Strategic_Outcome** (Rollup)
1. In DB_Projects, click "+ Add a property"
2. Property Name: `Strategic_Outcome`
3. Property Type: **Rollup**
4. Relation: `Source_Intent`
5. Property: `Success_Criteria` (this now exists!)
6. Calculate: "Show original"

---

## 2.3 DB_Nodes (Enhancements)

### New Properties to Add

**Property 1: Node_Type**
1. Open DB_Nodes
2. Click "+ Add a property"
3. Property Name: `Node_Type`
4. Property Type: **Select**
5. Add Options (click "+ New option"):
   - `Entity_Person` (color: Blue)
   - `Entity_Company` (color: Purple)
   - `Knowledge_Asset` (color: Green)
   - `System_Component` (color: Gray)

**Property 2: Related_Intents**
1. In DB_Nodes, click "+ Add a property"
2. Property Name: `Related_Intents`
3. Property Type: **Relation**
4. Target: **DB_Executive_Intents**
5. ✅ Enable "Show on DB_Executive_Intents"
6. In DB_Executive_Intents, this appears as: `Related_Nodes`

**Property 3: Entity_Relationship** (Optional, for Entity types)
1. In DB_Nodes, click "+ Add a property"
2. Property Name: `Entity_Relationship`
3. Property Type: **Select**
4. Add Options:
   - `Client` (Green)
   - `Partner` (Blue)
   - `Mentor` (Yellow)
   - `Competitor` (Red)
   - `Vendor` (Orange)

**Property 4: Knowledge_Tags** (Optional, for Knowledge types)
1. In DB_Nodes, click "+ Add a property"
2. Property Name: `Knowledge_Tags`
3. Property Type: **Multi-select**
4. Add Options (customize to your needs):
   - `Finance`
   - `Marketing`
   - `Strategy`
   - `Technical`
   - `Process_SOP`

### New Views in DB_Nodes

**View 1: Entities**
1. In DB_Nodes, click "+ New" → "Table view"
2. Name: "Entities"
3. Click "..." → "Filter"
4. Add filter: `Node_Type` → `contains` → `Entity`
5. This shows all Entity_Person and Entity_Company entries

**View 2: Knowledge Base**
1. Create new Table view: "Knowledge Base"
2. Filter: `Node_Type` → `is` → `Knowledge_Asset`

**View 3: System Components**
1. Create new Table view: "System Map"
2. Filter: `Node_Type` → `is` → `System_Component`

---

## 2.4 DB_Areas (No Changes Needed)

Your existing DB_Areas stays as-is. It now has a relation from DB_Executive_Intents (the `Area` property you added earlier).

---

# PART 3: MAKE.COM WORKFLOW SETUP

(Continue with the rest of the original guide - workflows section)

---

# SUMMARY OF CHANGES IN THIS REVISED GUIDE

**Key Improvements:**
1. ✅ Proper chronological order - no more "create this later"
2. ✅ Dependencies are respected - parent databases created before child relations
3. ✅ No skipping sections - follow top to bottom
4. ✅ All rollups work because their source properties exist when you create them

**The correct order is now:**
- PART 1: Create all 5 new databases (Agent Registry → Executive Intents → Action Pipes → Execution Log → System Inbox)
- PART 2: Enhance existing 3 databases with relations to the new ones (Tasks → Projects → Nodes)
- PART 3: Build Make.com workflows

Follow this revised guide and you won't hit any dependency issues!
