# EMM Development Progress

**Last updated:** 2026-03-03
**Railway URL:** https://web-production-3d888.up.railway.app
**Project path:** `/mnt/external/executive-mind-matrix/`

---

## Current Status: DEPLOYED — PIPELINE FUNCTIONAL, FIXES PENDING DEPLOY

### What Works (verified via diagnostic endpoints)
- `/health` returns green, poller_active: true
- Strategic path: inbox → Executive Intent creation, agent assignment, area detection, task spawning, dialectic → **fully working**
- 3 strategic intents processed (Spring Rush Week 2026, etc.)
- 10 Notion databases connected and mapping correctly

### Bugs Fixed This Session (commit a71593f — needs push/redeploy)
1. `notion_poller.py`: Was reading `Content` field only — users type in `Input_Title`. Added title fallback so classification gets actual text.
2. `notion_poller.py`: Operational task `Status` used wrong Notion type (`select` → `status`)
3. `notion_poller.py`: Wrong relation property name `"Related Intents"` → `"DB_System_Inbox"`
4. `notion_poller.py`: Added `Auto Generated` checkbox for operational tasks
5. `notion_poller.py`: Added `_stamp_inbox_id()` — `Inbox_ID` field was never populated
6. `task_spawner.py`: `"Project"` → `"Projects"` (singular/plural mismatch broke task-project linking)
7. `task_spawner.py`: `"Description"` → `"Context"` (property doesn't exist in DB_Projects)

### Next Steps (in priority order)
1. **PUSH commit a71593f** → Railway auto-deploys → verify operational + reference paths
2. **Test all 3 paths**: Drop operational intent (e.g., "Book dentist appointment"), reference intent (e.g., "Note: React hooks documentation"), strategic intent (e.g., "Should I hire a sales lead?")
3. **Notion views**: Add Inbox_ID + Status + Triage_Destination as visible columns in System Inbox view
4. Session continuity CLAUDE.md update (done this session)

### Known Remaining Issues
- Hardcoded agent UUIDs in `workflow_integration.py` lines 248-253 (currently working because IDs happen to be correct, but brittle)
- `suggest_related_nodes()` in knowledge_linker.py is a stub (minor)
- Command center UUID hardcoded at `command_center.py:25` (low risk if not called)
- Model: claude-3-haiku (upgrade to sonnet pending)

### Property Name Reference (actual Notion names)
Key ones that caused bugs — use these exactly:
- DB_Tasks: `"Status"` = type `status` (NOT select), `"Source Intent"`, `"Auto Generated"`, `"Projects"`, `"DB_System_Inbox"`
- DB_Projects: `"Context"` (not Description), `"Source Intent"`, `"Tasks"`
- DB_System_Inbox: `"Input_Title"` (title), `"Content"` (rich_text), `"Inbox_ID"` (number)
- DB_Executive_Intents: `"Name"`, `"Intent ID"` (with space), `"Agent_Persona"` (relation)
