# Executive Mind Matrix - Database Property Map

**Auto-generated property reference**

*Use this to check existing properties before creating new ones*

## Action Pipes

**19 properties + 1 pending**

| Property Name | Type | Notes |
|---------------|------|-------|
| AI_Raw_Output | `rich_text` |  |
| Action_ID | `number` | Sequential counter |
| Action_Title | `title` |  |
| Agent | `relation` |  |
| Analysis_Date | `created_time` | Temporal tracking |
| Approval_Status | `select` | Workflow status |
| Approved_Date | `date` | Temporal tracking |
| Auditor_Recommendation | `select` | Agent recommendation |
| Consensus | `checkbox` |  |
| Diff_Logged | `checkbox` | **PENDING — add manually.** Prevents poller re-processing approved actions every 2 min |
| Entrepreneur_Recommendation | `select` | Agent recommendation |
| Final_Decision | `select` |  |
| Intent | `relation` |  |
| Recommended_Option | `select` |  |
| Required_Resources | `rich_text` |  |
| Risk_Assessment | `rich_text` |  |
| Scenario_Options | `rich_text` |  |
| Synthesis_Summary | `rich_text` |  |
| Task_Generation_Template | `rich_text` |  |
| User_Notes | `rich_text` |  |

## Agent Registry

**10 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| API_Model | `select` |  |
| Active | `checkbox` |  |
| Agent_Name | `title` |  |
| Assigned Intents | `relation` |  |
| Auto_Route_Criteria | `rich_text` |  |
| Focus_Area | `rich_text` |  |
| Generated_Actions | `relation` |  |
| Output_Template | `rich_text` |  |
| Risk_Tolerance | `select` |  |
| System_Prompt | `rich_text` |  |

## Areas

**7 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| Name | `title` |  |
| Nodes | `relation` |  |
| Projects | `relation` |  |
| Related Intents | `relation` |  |
| Status | `select` | Workflow status |
| Tasks | `relation` |  |
| Vision | `rich_text` |  |

## Execution Log

**10 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| Action_Taken | `rich_text` |  |
| Actual_vs_Projected | `rich_text` |  |
| Decision_Date | `date` | Temporal tracking |
| Executor | `select` |  |
| Intent | `relation` |  |
| Lessons_Learned | `rich_text` |  |
| Log_Entry_Title | `title` |  |
| Log_ID | `number` |  |
| Outcome | `rich_text` |  |
| Settlement_Date | `created_time` | Temporal tracking |

## Executive Intents

**23 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| Age | `formula` |  |
| Agent_Persona | `relation` |  |
| Area | `relation` |  |
| Conflict_Level | `select` |  |
| Created_Date | `date` | Temporal tracking |
| Created_Time | `created_time` |  |
| Decision_Made | `rich_text` |  |
| Description | `rich_text` |  |
| Due_Date | `date` | Temporal tracking |
| Execution Record | `relation` |  |
| Intent ID | `number` |  |
| Name | `title` |  |
| Priority | `select` |  |
| Projected_Impact | `number` |  |
| Related_Actions | `relation` |  |
| Related_Nodes | `relation` |  |
| Risk_Level | `select` |  |
| Source | `relation` |  |
| Spawned Project | `relation` |  |
| Status | `select` | Workflow status |
| Success_Criteria | `rich_text` |  |
| Urgency Score | `formula` |  |
| ✅ Spawned tasks | `relation` |  |

## Nodes

**15 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| Areas | `relation` |  |
| Content | `rich_text` |  |
| Date added | `date` | Temporal tracking |
| Entity_Relationship | `select` |  |
| Knowledge_Tags | `multi_select` |  |
| Name | `title` |  |
| Node_Type | `select` |  |
| Projects | `relation` |  |
| Related_Intents | `relation` |  |
| Tags | `multi_select` |  |
| Tasks | `relation` |  |
| Text | `rich_text` |  |
| Topic | `multi_select` |  |
| Type | `select` |  |
| URL | `url` |  |

## Projects

**13 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| % Accomplished | `rollup` |  |
| Area | `relation` |  |
| Context | `rich_text` |  |
| Generate plan | `checkbox` |  |
| Name | `title` |  |
| Nodes | `relation` |  |
| Progress | `formula` |  |
| Source Intent | `relation` |  |
| Status | `select` | Workflow status |
| Strategic Outcome | `rollup` |  |
| Tasks | `relation` |  |
| Text | `rich_text` |  |
| Timeline | `date` |  |

## System Inbox

**10 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| Content | `rich_text` |  |
| Inbox_ID | `number` |  |
| Input_Title | `title` |  |
| Received_Date | `created_time` | Temporal tracking |
| Routed_to_Intent | `relation` |  |
| Routed_to_Node | `relation` |  |
| Routed_to_Task | `relation` |  |
| Source | `select` |  |
| Status | `select` | Workflow status |
| Triage_Destination | `select` |  |

## Tasks

**14 properties**

| Property Name | Type | Notes |
|---------------|------|-------|
| Agent Context | `rollup` |  |
| Area | `relation` |  |
| Auto Generated | `checkbox` |  |
| Date | `date` | Temporal tracking |
| Done | `checkbox` |  |
| Energy | `select` |  |
| Name | `title` |  |
| Nodes | `relation` |  |
| Priority | `select` |  |
| Projects | `relation` |  |
| Related notes | `relation` |  |
| Source Intent | `relation` |  |
| Status | `status` | Workflow status |
| Time Estimate | `number` |  |

## Training Data

**8 properties + 1 pending**

| Property Name | Type | Notes |
|---------------|------|-------|
| Acceptance_Rate | `number` | Stored as 0–100; code normalises to 0–1 |
| Agent_Name | `select` | **PENDING — add manually.** Required for per-agent analytics and fine-tuning export filtering |
| Final_Plan | `rich_text` | Human-approved output (assistant turn in fine-tuning JSONL) |
| Intent_ID | `rich_text` | Notion page ID of source Executive Intent |
| Modifications | `rich_text` | Human-readable list of changes |
| Modifications_Count | `number` |  |
| Original_Plan | `rich_text` | Raw AI output at time of dialectic analysis |
| Timestamp | `date` |  |
| Title | `title` |  |

