# Executive Brain: Exact Setup Guide
## Complete Step-by-Step Implementation

**IMPORTANT: Follow this guide in exact order. The sequence matters because later steps depend on earlier ones.**

---

# PART 1: CREATE NEW DATABASES (No Dependencies)

## 1.1 DB_Tasks (Enhancements)

### New Properties to Add

**Property 1: Source_Intent**
1. Open DB_Tasks in Notion
2. Click "+ Add a property" (or click "..." in table header)
3. Property Name: `Source_Intent`
4. Property Type: **Relation**
5. Select relation target: DB_Executive_Intents (you'll create this later)
6. Relation Type: Keep default (DB_Tasks can relate to multiple DB_Executive_Intents)
7. ✅ Enable "Show on DB_Executive_Intents" (this creates bidirectional relation)
8. In DB_Executive_Intents, this will appear as: `Spawned_Tasks`

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
5. Property: Select `Agent_Persona`
6. Calculate: "Show original"
7. This will show which agent created the task (e.g., "The Entrepreneur")

---

## 1.2 DB_Projects (Enhancements)

### New Properties to Add

**Property 1: Source_Intent**
1. Open DB_Projects
2. Click "+ Add a property"
3. Property Name: `Source_Intent`
4. Property Type: **Relation**
5. Target: DB_Executive_Intents
6. ✅ Enable "Show on DB_Executive_Intents"
7. In DB_Executive_Intents, this appears as: `Spawned_Project`

**Property 2: Strategic_Outcome** (Rollup)
1. In DB_Projects, click "+ Add a property"
2. Property Name: `Strategic_Outcome`
3. Property Type: **Rollup**
4. Relation: `Source_Intent`
5. Property: `Success_Criteria`
6. Calculate: "Show original"

---

## 1.3 DB_Nodes (Enhancements)

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
4. Target: DB_Executive_Intents
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

## 1.4 DB_Areas (No Changes Needed)
Your existing DB_Areas stays as-is. We'll just add relations to it from new databases.

---

# PART 2: CREATE NEW DATABASES

## 2.1 DB_Executive_Intents (The Command Center)

### Create Database
1. In Notion, navigate to your workspace
2. Click "+ New Page" or type `/database` → "Table - Full page"
3. Name: `DB_Executive_Intents`

### Add Properties (in order)

**Auto-created**:
- `Name` (Text) - Rename this to `Title`

**Property 1: Intent_ID**
1. Click "+ Add property"
2. Name: `Intent_ID`
3. Type: **Number** → Format: **Number with commas**
4. Click "..." on property → "Edit property" → Check "Show unique ID" (if available)
5. OR manually number as you create entries

**Property 2: Description**
1. Name: `Description`
2. Type: **Text** (will auto-expand to long text when you type)

**Property 3: Agent_Persona**
1. Name: `Agent_Persona`
2. Type: **Relation**
3. Target: DB_Agent_Registry (create this database first - see Section 2.2)
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
   - `Low` (Green) - "Auto-route OK"
   - `Medium` (Yellow) - "Auto-route with review"
   - `High` (Red) - "Manual assignment only"

**Property 6: Projected_Impact**
1. Name: `Projected_Impact`
2. Type: **Number**
3. Format: Number (1-10 scale) OR Currency (dollar value)
4. Your choice based on how you want to measure impact

**Property 7: Success_Criteria**
1. Name: `Success_Criteria`
2. Type: **Text**

**Property 8: Due_Date**
1. Name: `Due_Date`
2. Type: **Date**
3. Include time: Optional (your preference)

**Property 9: Created_Date**
1. Name: `Created_Date`
2. Type: **Created time**

**Property 10: Priority**
1. Name: `Priority`
2. Type: **Select**
3. Add Options:
   - `P0` (Red) - "Critical"
   - `P1` (Orange) - "High"
   - `P2` (Yellow) - "Normal"
   - `P3` (Green) - "Low"

**Property 11: Area**
1. Name: `Area`
2. Type: **Relation**
3. Target: DB_Areas (your existing database)
4. ✅ Enable "Show on DB_Areas" (appears as `Related_Intents`)

**Property 12: Source** (auto-created from DB_System_Inbox relation)
1. This will appear automatically when you create DB_System_Inbox
2. Or manually create:
   - Name: `Source`
   - Type: **Relation**
   - Target: DB_System_Inbox

**Property 13: Related_Actions** (auto-created from DB_Action_Pipes)
1. This appears automatically when you create DB_Action_Pipes relation
2. Shows all agent analyses for this intent

**Property 14: Spawned_Tasks** (auto-created from DB_Tasks)
1. This was created when you added Source_Intent to DB_Tasks (Section 1.1)

**Property 15: Spawned_Project** (auto-created from DB_Projects)
1. This was created when you added Source_Intent to DB_Projects (Section 1.2)

**Property 16: Related_Nodes** (auto-created from DB_Nodes)
1. This was created when you added Related_Intents to DB_Nodes (Section 1.3)

**Property 17: Execution_Record**
1. Name: `Execution_Record`
2. Type: **Relation**
3. Target: DB_Execution_Log
4. ✅ Enable "Show on DB_Execution_Log" (appears as `Intent`)

### Add Formulas

**Formula 1: Days_Since_Creation**
1. Click "+ Add property"
2. Name: `Days_Since_Creation`
3. Type: **Formula**
4. Formula:
```
dateBetween(now(), prop("Created_Date"), "days")
```

**Formula 2: Urgency_Score**
1. Name: `Urgency_Score`
2. Type: **Formula**
3. Formula:
```
if(prop("Priority") == "P0", 100, if(prop("Priority") == "P1", 75, if(prop("Priority") == "P2", 50, 25))) + prop("Days_Since_Creation")
```

**Formula 3: Status_Indicator**
1. Name: `Status_Indicator`
2. Type: **Formula**
3. Formula:
```
if(prop("Status") == "Pending_Approval", "🟡 " + prop("Status"), if(prop("Status") == "Executed", "🟢 " + prop("Status"), if(prop("Status") == "In_Analysis", "🔵 " + prop("Status"), if(prop("Status") == "Assigned", "🟠 " + prop("Status"), "⚪ " + prop("Status")))))
```

### Create Views

**View 1: All Intents** (Default Table)
- Shows everything, sorted by Created_Date (newest first)

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

**View 5: By Agent** (Gallery or Board)
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

## 2.2 DB_Agent_Registry (Agent Configurations)

### Create Database
1. Type `/database` → "Table - Full page"
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

**Property 8: Assigned_Intents** (auto-created from DB_Executive_Intents)
1. This appears when you create Agent_Persona relation in DB_Executive_Intents

### Seed Data (Create 3 Entries)

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
      "pros": ["Revenue potential: $X/mo", "Scalability factor: Xr", "Other advantage"],
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
  "revenue_projection": "Expected revenue: $X/mo by month Y"
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
   - **Output_Template**: (Same JSON structure as Entrepreneur)
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
   - **Output_Template**: (Same JSON structure)
   - **Auto_Route_Criteria**: `Risk = High` (Auditor reviews all high-risk)

---

## 2.3 DB_Action_Pipes (Agent Output Staging)

### Create Database
1. Type `/database` → "Table - Full page"
2. Name: `DB_Action_Pipes`

### Add Properties

**Auto-created**:
- `Name` (Text) - Rename to `Action_Title`

**Property 1: Action_ID**
1. Name: `Action_ID`
2. Type: **Number** → Unique ID or auto-number

**Property 2: Intent**
1. Name: `Intent`
2. Type: **Relation**
3. Target: DB_Executive_Intents
4. ✅ Enable "Show on DB_Executive_Intents" (appears as `Related_Actions`)

**Property 3: Agent**
1. Name: `Agent`
2. Type: **Relation**
3. Target: DB_Agent_Registry
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

## 2.4 DB_Execution_Log (Audit Trail)

### Create Database
1. Type `/database` → "Table - Full page"
2. Name: `DB_Execution_Log`

### Add Properties

**Auto-created**:
- `Name` (Text) - Rename to `Log_Entry_Title`

**Property 1: Log_ID**
1. Name: `Log_ID`
2. Type: **Number** (auto-increment)

**Property 2: Intent**
1. Name: `Intent`
2. Type: **Relation**
3. Target: DB_Executive_Intents
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
   - `The Entrepreneur` (if agent auto-executed)
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

## 2.5 DB_System_Inbox (Input Queue)

### Create Database
1. Type `/database` → "Table - Full page"
2. Name: `DB_System_Inbox`

### Add Properties

**Auto-created**:
- `Name` (Text) - Rename to `Input_Title`

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
3. Target: DB_Executive_Intents
4. ✅ Enable "Show on DB_Executive_Intents" (appears as `Source`)

**Property 8: Routed_to_Task**
1. Name: `Routed_to_Task`
2. Type: **Relation**
3. Target: DB_Tasks

**Property 9: Routed_to_Node**
1. Name: `Routed_to_Node`
2. Type: **Relation**
3. Target: DB_Nodes

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

# PART 3: MAKE.COM WORKFLOW SETUP

## Prerequisites

### 3.1 Get Notion API Key

1. Go to https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Name: `Executive Brain Automation`
4. Associated workspace: Select your workspace
5. Type: Internal integration
6. Capabilities (check all):
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
7. Click "Submit"
8. **Copy the "Internal Integration Token"** (starts with `secret_`)
9. **IMPORTANT**: Share databases with integration
   - Open each database in Notion
   - Click "..." → "Connections" → "Connect to" → Select "Executive Brain Automation"
   - Do this for ALL 9 databases (7 new + 2 existing: DB_Tasks, DB_Projects)

### 3.2 Get Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create Key"
5. Name: `Executive Brain Agent`
6. **Copy the API key** (starts with `sk-ant-`)
7. Add credits: You'll need to add payment method ($5 minimum)

### 3.3 Set Up Make.com Account

1. Go to https://www.make.com/
2. Sign up (free tier is fine for testing)
3. Create new scenario for each workflow

---

## 3.4 Workflow 1: Inbox Triage

### Overview
- **Trigger**: Scheduled (daily at 9 AM)
- **Purpose**: Check DB_System_Inbox for unprocessed items, classify with Claude, route to appropriate database

### Module-by-Module Setup

**Module 1: Schedule Trigger**
1. In Make.com, create new scenario
2. Click the clock icon (Schedule)
3. Schedule Settings:
   - Interval: Every day
   - Time: 9:00 AM (your timezone)
   - Start: Today
4. Click OK

**Module 2: Search Notion Database (Get Unprocessed Items)**
1. Click "+" after Schedule
2. Search for "Notion" → Select "Notion"
3. Action: "Search Objects"
4. Connection: Click "Add" → Paste your Notion Integration Token
5. Database ID:
   - Go to DB_System_Inbox in Notion
   - Copy database ID from URL: `notion.so/[workspace]/[DATABASE_ID]?v=...`
   - Paste the DATABASE_ID
6. Filter:
   - Click "Add item"
   - Property: `Status`
   - Condition: `equals`
   - Value: `Unprocessed`
7. Sorts: Leave empty (or sort by Received_Date ascending)
8. Limit: 10 (process 10 items per run)

**Module 3: Iterator (Loop Through Each Item)**
1. Click "+" after Notion Search
2. Search for "Iterator"
3. Array: Select `2. array` from Module 2 output

**Module 4: HTTP Request (Call Claude API)**
1. Click "+" after Iterator
2. Search for "HTTP" → "Make a request"
3. Settings:
   - URL: `https://api.anthropic.com/v1/messages`
   - Method: `POST`
   - Headers:
     - Add item:
       - Name: `x-api-key`
       - Value: `[Your Claude API Key]` (paste the sk-ant-... key)
     - Add item:
       - Name: `anthropic-version`
       - Value: `2023-06-01`
     - Add item:
       - Name: `content-type`
       - Value: `application/json`
   - Body:
```json
{
  "model": "claude-sonnet-4-5-20241022",
  "max_tokens": 1024,
  "messages": [{
    "role": "user",
    "content": "Triage this input from my system inbox:\n\n{{3.Content}}\n\nClassify as:\n- 'strategic' (requires decision analysis, multiple options, or high impact > $1000)\n- 'operational' (clear next action, can execute immediately)\n- 'reference' (knowledge to store for later)\n\nRespond ONLY with valid JSON (no markdown):\n{\n  \"type\": \"strategic|operational|reference\",\n  \"title\": \"...\",\n  \"agent\": \"The Entrepreneur|The Quant|The Auditor\",\n  \"risk\": \"Low|Medium|High\",\n  \"impact\": 1-10,\n  \"next_action\": \"...\" (if operational),\n  \"rationale\": \"Why this classification\"\n}"
  }]
}
```
   - Parse response: Yes
4. Click OK

**Module 5: Parse JSON**
1. Click "+" after HTTP
2. Search for "JSON" → "Parse JSON"
3. JSON string: `{{4.data.content[1].text}}`
   - This extracts Claude's response text

**Module 6: Router (Split Based on Type)**
1. Click "+" after Parse JSON
2. Search for "Router"
3. This will create multiple paths

**Path 1: Strategic (Create Intent)**
1. On Router, click "Add route"
2. Name: "Strategic"
3. Filter:
   - Label: "If Strategic"
   - Condition: `{{5.type}}` `equals (text)` `strategic`
4. Click "OK"
5. Click "+" on this path
6. Search for "Notion" → "Create a Database Item"
7. Connection: Use existing Notion connection
8. Database ID: [DB_Executive_Intents database ID]
9. Properties:
   - Title: `{{5.title}}`
   - Description: `{{3.Content}}`
   - Status: `Ready`
   - Risk_Level: `{{5.risk}}`
   - Projected_Impact: `{{5.impact}}`
   - Agent_Persona: Map `{{5.agent}}` to relation (see below)
   - Priority: Map based on Impact:
     ```
     {{if(5.impact >= 8, "P0", if(5.impact >= 6, "P1", "P2"))}}
     ```
10. Agent_Persona relation mapping:
    - Click the field
    - Search mode: "Search"
    - Search by: "Name"
    - Value: `{{5.agent}}`
11. Click "OK"
12. Add another module on this path: "Update Notion Item" (Module 2 - Inbox entry)
    - Database Item ID: `{{3.id}}`
    - Properties:
      - Status: `Triaged_to_Intent`
      - Triage_Destination: `Strategic (Intent)`
      - Routed_to_Intent: Link to newly created Intent (use output from previous module)

**Path 2: Operational (Create Task)**
1. On Router, click "Add route"
2. Name: "Operational"
3. Filter: `{{5.type}}` `equals` `operational`
4. Click "+" on this path
5. Notion → "Create a Database Item"
6. Database ID: [DB_Tasks database ID]
7. Properties:
   - Name/Title: `{{5.title}}`
   - Description: `{{5.next_action}}`
   - Status: `Next Actions` (or your default task status)
   - Auto_Generated: Unchecked
8. Add "Update Notion Item" for Inbox:
   - Status: `Triaged_to_Task`
   - Triage_Destination: `Operational (Task)`

**Path 3: Reference (Create Node)**
1. On Router, click "Add route"
2. Name: "Reference"
3. Filter: `{{5.type}}` `equals` `reference`
4. Notion → "Create a Database Item"
5. Database ID: [DB_Nodes database ID]
6. Properties:
   - Name: `{{5.title}}`
   - Node_Type: `Knowledge_Asset`
   - [Your custom properties based on DB_Nodes structure]
7. Update Inbox:
   - Status: `Triaged_to_Node`

**Module 7: Send Summary Email** (after Router merges)
1. Click "+" after all router paths merge
2. Search for "Email" → "Send an Email" (or use Gmail/Outlook module)
3. To: [Your email]
4. Subject: `Inbox Triage Complete - {{formatDate(now, "YYYY-MM-DD")}}`
5. Content:
```
Executive Brain Inbox Triage Summary

Items Processed: {{count(2.array)}}

Strategic: {{count(filter by type=strategic)}}
Operational: {{count(filter by type=operational)}}
Reference: {{count(filter by type=reference)}}

View pending intents: [Link to your DB_Executive_Intents Inbox view]
```
6. Click OK

**Save & Test**
1. Click "Save" (bottom left)
2. Name scenario: "1_Inbox_Triage"
3. Click "Run once" to test
4. Check output logs for errors

---

## 3.5 Workflow 2: Smart Router

### Overview
- **Trigger**: Scheduled (every 6 hours)
- **Purpose**: Find Intents with Status="Ready", auto-assign low/medium risk to agents, flag high risk for manual review

### Module-by-Module Setup

**Module 1: Schedule**
1. Create new scenario
2. Schedule trigger:
   - Interval: Every 6 hours
   - OR: Every day at specific times (9 AM, 3 PM, 9 PM)

**Module 2: Search Notion (Get Ready Intents)**
1. Notion → "Search Objects"
2. Database ID: [DB_Executive_Intents]
3. Filter:
   - Property: `Status`
   - Equals: `Ready`
4. Limit: 20

**Module 3: Iterator**
1. Iterator
2. Array: `{{2.array}}`

**Module 4: Router (By Risk Level)**
1. Router with 2 paths

**Path 1: Auto-Route (Low/Medium Risk)**
1. Filter: `{{3.Risk_Level}}` `is not equal to` `High`
2. Notion → "Update a Database Item"
3. Database Item ID: `{{3.id}}`
4. Properties:
   - Status: `Assigned`
   - Description: Append text:
     ```
     {{3.Description}}

     [Auto-routed by Smart Router on {{formatDate(now, "YYYY-MM-DD HH:mm")}}]
     ```

**Path 2: Manual Review (High Risk)**
1. Filter: `{{3.Risk_Level}}` `equals` `High`
2. Email → "Send an Email"
3. Subject: `🔴 High-Risk Intent Requires Manual Assignment`
4. Content:
```
A high-risk intent needs your review before assignment:

Title: {{3.Title}}
Risk Level: {{3.Risk_Level}}
Projected Impact: {{3.Projected_Impact}}
Suggested Agent: {{3.Agent_Persona}}

Review and manually assign: [Link to intent in Notion]
```

**Save & Test**
1. Save as "2_Smart_Router"
2. Test with sample "Ready" intent

---

## 3.6 Workflow 3: Agent Executor (CORE WORKFLOW)

### Overview
- **Trigger**: Notion database watch (when Status changes to "Assigned")
- **Purpose**: Fetch intent details, call Claude with agent persona, create Action Pipe entry

### Module-by-Module Setup

**Module 1: Notion Webhook Trigger**
1. Create new scenario
2. Notion → "Watch Database Items"
3. Webhook name: `Intent_Assigned_Trigger`
4. Connection: Your Notion connection
5. Database ID: [DB_Executive_Intents]
6. Filter: Watch for updates where `Status` changes to `Assigned`
7. Click "OK"
8. **IMPORTANT**: Copy the webhook URL
9. In Notion, you'll need to manually trigger this or use Notion's automation (see note below)

**NOTE**: Notion doesn't natively support webhooks for property changes. **Alternative trigger**:
- Change Module 1 to: **Schedule** (every 30 minutes)
- Add Module 2: Search for Intents where `Status = "Assigned"` AND `Created_Date` is within last 30 minutes

**Module 2: Get Intent Details**
1. Notion → "Get a Database Item"
2. Database Item ID: `{{1.id}}` (from trigger)
3. This fetches full intent record

**Module 3: Get Agent Details**
1. Notion → "Get a Database Item"
2. Database ID: [DB_Agent_Registry]
3. Database Item ID: `{{2.Agent_Persona.id}}`
   - This gets the related Agent record

**Module 4: Get Related Knowledge (Optional)**
1. Notion → "Get Database Items" (plural)
2. Database ID: [DB_Nodes]
3. Filter: Where `Related_Intents` contains `{{2.id}}`
4. This fetches any knowledge nodes linked to the intent

**Module 5: Build Context Package** (Text Aggregator)
1. Tools → "Text Aggregator"
2. Text: Build this string:
```
INTENT DETAILS:
Title: {{2.Title}}
Description: {{2.Description}}
Success Criteria: {{2.Success_Criteria}}
Projected Impact: {{2.Projected_Impact}}
Risk Level: {{2.Risk_Level}}
Due Date: {{2.Due_Date}}

RELATED CONTEXT:
{{join(4.array.Name, ", ")}}
```

**Module 6: Call Claude API (Agent Analysis)**
1. HTTP → "Make a request"
2. URL: `https://api.anthropic.com/v1/messages`
3. Method: POST
4. Headers: (same as Workflow 1)
   - x-api-key: [Claude API key]
   - anthropic-version: 2023-06-01
   - content-type: application/json
5. Body:
```json
{
  "model": "{{3.API_Model}}",
  "max_tokens": 4096,
  "system": "{{3.System_Prompt}}",
  "messages": [{
    "role": "user",
    "content": "{{5.text}}\n\nProvide 3 scenario options in this exact JSON format:\n{{3.Output_Template}}"
  }]
}
```
6. Parse response: Yes

**Module 7: Parse JSON Response**
1. JSON → "Parse JSON"
2. JSON string: `{{6.data.content[1].text}}`

**Module 8: Format Scenario Table** (Text)
1. Tools → "Set Variable"
2. Variable name: `scenario_table`
3. Value (build markdown table):
```markdown
| Option | Description | Pros | Cons | Risk (1-5) | Impact (1-10) |
|--------|-------------|------|------|------------|---------------|
| A | {{7.scenario_options[1].description}} | {{join(7.scenario_options[1].pros, ", ")}} | {{join(7.scenario_options[1].cons, ", ")}} | {{7.scenario_options[1].risk}} | {{7.scenario_options[1].impact}} |
| B | {{7.scenario_options[2].description}} | {{join(7.scenario_options[2].pros, ", ")}} | {{join(7.scenario_options[2].cons, ", ")}} | {{7.scenario_options[2].risk}} | {{7.scenario_options[2].impact}} |
| C | {{7.scenario_options[3].description}} | {{join(7.scenario_options[3].pros, ", ")}} | {{join(7.scenario_options[3].cons, ", ")}} | {{7.scenario_options[3].risk}} | {{7.scenario_options[3].impact}} |

**Recommended**: Option {{7.recommended_option}}

**Rationale**: {{7.recommendation_rationale}}
```

**Module 9: Extract Task Template**
1. Tools → "Set Variable"
2. Variable name: `task_template`
3. Value:
```
{{join(7.required_resources.tasks, "\n")}}
```
(Assumes agent included `tasks` array in required_resources)

**Module 10: Create Action Pipe Entry**
1. Notion → "Create a Database Item"
2. Database ID: [DB_Action_Pipes]
3. Properties:
   - Action_Title: `Analysis for: {{2.Title}}`
   - Intent: Relation to `{{2.id}}`
   - Agent: Relation to `{{3.id}}`
   - Scenario_Options: `{{8.scenario_table}}`
   - Recommended_Option: `Option {{7.recommended_option}}`
   - Risk_Assessment: `{{7.risk_assessment}}`
   - Required_Resources:
     ```
     Time: {{7.required_resources.time}}
     Money: {{7.required_resources.money}}
     Tools: {{join(7.required_resources.tools, ", ")}}
     People: {{join(7.required_resources.people, ", ")}}
     ```
   - Task_Generation_Template: `{{9.task_template}}`
   - Approval_Status: `Pending`

**Module 11: Update Intent Status**
1. Notion → "Update a Database Item"
2. Database Item ID: `{{2.id}}`
3. Properties:
   - Status: `Pending_Approval`

**Module 12: Send Notification**
1. Email → "Send an Email"
2. Subject: `⏳ New Analysis Ready: {{2.Title}}`
3. Content:
```
Agent {{3.Agent_Name}} has completed analysis for:

{{2.Title}}

Recommended Option: {{7.recommended_option}}

View full analysis: [Link to Action Pipe in Notion]
```

**Save & Test**
1. Save as "3_Agent_Executor"
2. Test by manually changing an Intent status to "Assigned"
3. Check Action Pipes for new entry

---

## 3.7 Workflow 4: Settlement Processor

### Overview
- **Trigger**: Manual button or status change to "Approved" in Action Pipes
- **Purpose**: Create Execution Log, generate tasks in DB_Tasks, update Intent

### Module-by-Module Setup

**Module 1: Trigger** (Manual Webhook or Watch)
- Option A: Notion → "Watch Database Items" (watch Action Pipes for Approval_Status = "Approved")
- Option B: Webhooks → "Custom Webhook" (trigger via Notion button - requires Zapier or n8n for button integration)

**Module 2: Get Action Pipe Details**
1. Notion → "Get a Database Item"
2. Database Item ID: `{{1.id}}`

**Module 3: Get Related Intent**
1. Notion → "Get a Database Item"
2. Database Item ID: `{{2.Intent.id}}`

**Module 4: Create Execution Log Entry**
1. Notion → "Create a Database Item"
2. Database ID: [DB_Execution_Log]
3. Properties:
   - Log_Entry_Title: `Executed: {{3.Title}}`
   - Intent: Relation to `{{3.id}}`
   - Action_Taken: `Option {{2.Recommended_Option}}: {{2.Scenario_Options}}` (extract approved option)
   - Decision_Date: `{{formatDate(now, "YYYY-MM-DD")}}`
   - Executor: `You` (or `{{2.Agent.Agent_Name}}`)
   - Outcome: `Pending execution - tasks generated`

**Module 5: Parse Task Template**
1. Text Parser → "Match Pattern"
2. Text: `{{2.Task_Generation_Template}}`
3. Pattern: Split by newline `\n`

**Module 6: Iterator (Create Tasks)**
1. Iterator
2. Array: `{{5.array}}`

**Module 7: Create Task in DB_Tasks**
1. Notion → "Create a Database Item"
2. Database ID: [DB_Tasks]
3. Properties:
   - Title/Name: `{{6.value}}`
   - Source_Intent: Relation to `{{3.id}}`
   - Auto_Generated: `true`
   - Status: `Next Actions` (or your default)
   - Area: `{{3.Area}}` (inherit from Intent)

**Module 8: Update Intent Status**
1. Notion → "Update a Database Item"
2. Database Item ID: `{{3.id}}`
3. Properties:
   - Status: `Executed`

**Module 9: Notification**
1. Email → "Send an Email"
2. Subject: `✅ Intent Executed: {{3.Title}}`
3. Content:
```
Settlement complete for: {{3.Title}}

Tasks created: {{count(5.array)}}
Execution logged: {{4.Log_Entry_Title}}

Next: Complete tasks in DB_Tasks
```

**Save & Test**
1. Save as "4_Settlement_Processor"
2. Test by manually approving an Action Pipe entry

---

## 3.8 Workflow 5: Daily Digest

### Overview
- **Trigger**: Daily at 8 PM
- **Purpose**: Send summary email of system activity

### Module-by-Module Setup

**Module 1: Schedule**
1. Schedule trigger
2. Every day at 8:00 PM

**Module 2-5: Query Notion (4 parallel searches)**
1. Search DB_Executive_Intents where `Created_Date` = Today
2. Search DB_Executive_Intents where `Status` = "Pending_Approval"
3. Search DB_Execution_Log where `Settlement_Date` = Today
4. Search DB_Action_Pipes where `Approval_Status` = "Pending"

**Module 6: Aggregate Data**
1. Tools → "Set Variables" (multiple)
2. Variables:
   - `new_intents_count`: `{{count(2.array)}}`
   - `pending_approval_count`: `{{count(3.array)}}`
   - `executed_today_count`: `{{count(4.array)}}`
   - `actions_ready_count`: `{{count(5.array)}}`

**Module 7: Send Digest Email**
1. Email → "Send an Email"
2. Subject: `Executive Brain Digest - {{formatDate(now, "YYYY-MM-DD")}}`
3. Content:
```
EXECUTIVE BRAIN DAILY DIGEST

📥 New Intents Created: {{6.new_intents_count}}
{{join(2.array.Title, "\n- ")}}

⏳ Pending Your Approval: {{6.pending_approval_count}}
{{join(3.array.Title, "\n- ")}}

✅ Executed Today: {{6.executed_today_count}}
{{join(4.array.Log_Entry_Title, "\n- ")}}

⚙️ In Analysis: {{6.actions_ready_count}}

---
View Dashboard: [Link to your Notion Executive Brain page]
```

**Save & Test**
1. Save as "5_Daily_Digest"
2. Run once to test

---

# PART 4: TESTING & VALIDATION

## 4.1 End-to-End Test Scenario

**Test Case**: "Should I invest $5k in VTI or Bitcoin?"

1. **Input to Inbox**:
   - Go to DB_System_Inbox
   - Create new entry:
     - Content: "I have $5k to invest. Should I put it in VTI (Vanguard Total Stock Market ETF) or Bitcoin? Want to hold for 5+ years."
     - Source: Manual Entry
     - Status: Unprocessed

2. **Wait for Triage** (or manually run Workflow 1):
   - Check DB_Executive_Intents
   - Should see new Intent:
     - Title: Something like "Invest $5k: VTI vs Bitcoin"
     - Agent: The Quant
     - Status: Ready
     - Risk: Medium

3. **Wait for Smart Router** (or manually run Workflow 2):
   - Intent Status should change to "Assigned"

4. **Wait for Agent Executor** (or manually run Workflow 3):
   - Check DB_Action_Pipes
   - Should see new entry with:
     - 3 scenario options (A, B, C)
     - Risk/impact ratings
     - Recommended option
     - Task template

5. **Manual Approval**:
   - Open Action Pipe entry
   - Review scenarios
   - Add User_Notes: "I'll go with Option A"
   - Change Approval_Status to "Approved"
   - Set Approved_Date to today

6. **Settlement** (manually run Workflow 4):
   - Check DB_Execution_Log - should have new entry
   - Check DB_Tasks - should have 3-5 new tasks with Source_Intent linked
   - Check Intent - Status should be "Executed"

7. **Validation**:
   - [ ] All tasks link back to Intent
   - [ ] Execution Log has audit trail
   - [ ] Intent shows Spawned_Tasks count
   - [ ] Original Inbox entry shows route to Intent

---

## 4.2 Common Issues & Fixes

**Issue 1: Notion relation not linking**
- Fix: Make sure you selected "Search by: Name" in Make.com Notion module
- Fix: Verify relation is bidirectional (checkbox enabled when creating)

**Issue 2: Claude API returns error**
- Check API key is valid (starts with `sk-ant-`)
- Check you have credits in Anthropic account
- Check `anthropic-version` header is exactly `2023-06-01`
- Check JSON in body is valid (use JSON validator)

**Issue 3: Workflow doesn't trigger**
- Notion Watch Database triggers are unreliable - switch to scheduled polling
- Check webhook is connected to correct database
- Verify database permissions (integration has access)

**Issue 4: Task generation creates blank tasks**
- Fix: Agent prompt needs to include task list in response
- Update Output_Template to include:
```json
"task_generation": ["Task 1", "Task 2", "Task 3"]
```

**Issue 5: Scenario table formatting broken**
- Fix: Use plain text join instead of markdown in Module 8
- OR: Use Notion's native table property (more complex)

---

# PART 5: CUSTOMIZATION & EXTENSIONS

## 5.1 Add Notion Buttons (Requires Notion Automation)

**Button 1: "Send to Agent" (in DB_Executive_Intents)**
1. Add Button property to DB_Executive_Intents
2. Button Action:
   - Edit properties:
     - Status → "Assigned"
3. This manually triggers Workflow 3

**Button 2: "Approve & Settle" (in DB_Action_Pipes)**
1. Add Button property to DB_Action_Pipes
2. Button Action:
   - Edit properties:
     - Approval_Status → "Approved"
     - Approved_Date → Today
3. This triggers Workflow 4

## 5.2 Add Slack Notifications (Replace Email)

In any workflow:
1. Replace "Send an Email" module with "Slack" → "Create a Message"
2. Channel: Your channel ID
3. Text: Same as email content

## 5.3 Add Voice Input (Mobile)

**iOS Shortcut**:
1. Create Shortcut:
   - Dictate Text
   - Get Contents of URL:
     - URL: `https://api.notion.com/v1/pages`
     - Method: POST
     - Headers: Authorization: `Bearer [Notion Token]`
     - Body:
```json
{
  "parent": {"database_id": "[DB_System_Inbox ID]"},
  "properties": {
    "Input_Title": {"title": [{"text": {"content": "Voice Note"}}]},
    "Content": {"rich_text": [{"text": {"content": "[Dictated Text]"}}]},
    "Source": {"select": {"name": "Voice Note"}},
    "Status": {"select": {"name": "Unprocessed"}}
  }
}
```
2. Add to home screen
3. Speak → Auto-creates Inbox entry

---

# PART 6: MAINTENANCE & MONITORING

## 6.1 Weekly Review Checklist

- [ ] Check Make.com scenario execution logs for errors
- [ ] Review Pending Approval view - any stale items?
- [ ] Review Executed intents - add Outcomes and Lessons_Learned
- [ ] Check Agent performance - are recommendations good?
- [ ] Refine System_Prompts in DB_Agent_Registry if needed

## 6.2 Monthly Metrics

Track in Notion (create DB_System_Metrics):
- Total Intents created
- Average time from Intent → Execution
- Agent accuracy (Actual vs Projected)
- API costs (Anthropic + Make.com usage)

## 6.3 Cost Monitoring

**Anthropic API**:
- Claude Sonnet: ~$3 per 1M input tokens, $15 per 1M output
- Estimate: 10 intents/week × 4k tokens each = ~$2-5/month

**Make.com**:
- Free tier: 1,000 operations/month
- Estimate usage:
  - Workflow 1: 10 ops/day × 30 = 300/month
  - Workflow 3: 5 ops/week × 4 = 20/month
  - Others: ~100/month
  - Total: ~400-500 ops/month (within free tier)

---

# SUMMARY

You now have:

## ✅ 9 Notion Databases
1. DB_Executive_Intents (strategic command center)
2. DB_Agent_Registry (3 AI personas)
3. DB_Action_Pipes (scenario analysis staging)
4. DB_Execution_Log (audit trail)
5. DB_System_Inbox (input queue)
6. DB_Tasks (enhanced with Intent tracking)
7. DB_Projects (enhanced with Intent tracking)
8. DB_Nodes (enhanced as hybrid entity/knowledge)
9. DB_Areas (unchanged)

## ✅ 5 Make.com Workflows
1. Inbox Triage (daily)
2. Smart Router (6-hour cycle)
3. Agent Executor (triggered)
4. Settlement Processor (manual)
5. Daily Digest (evening)

## ✅ Complete Flow
Input → Triage → Intent → Agent Analysis → Approval → Task Generation → Execution → Audit Log

## Next Steps
1. Build databases in order (Part 1 → Part 2)
2. Get API keys (Part 3.1-3.2)
3. Build workflows one at a time (Part 3.4-3.8)
4. Test with sample data (Part 4)
5. Customize as needed (Part 5)

---

**Questions?** If you need clarification on any specific step, ask and I'll provide more detail or alternative approaches.
