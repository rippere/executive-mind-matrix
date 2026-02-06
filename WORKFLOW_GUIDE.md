# Executive Mind Matrix - Complete Workflow Guide

**The Cohesive System You Asked For**

---

## 🎯 The Complete Journey

Your Command Center now shows **the entire decision-making lifecycle** in one place:

```
Create → Triage → Analyze → Decide → Execute → Learn
  ↓        ↓         ↓        ↓        ↓        ↓
Inbox → Intent → Dialectic → Action → Execute → Training
```

Every database is **connected and purposeful**.

---

## 📋 The 6-Step Workflow

### Step 1: **Create** (System Inbox)
**Location:** Top section of Command Center

**What You Do:**
- Add a new entry directly in the System Inbox table view
- Title: Your decision or task
- Content: Additional context
- Leave Status as "Unprocessed"

**What Happens Automatically:**
- System polls every 2 minutes
- AI classifies as Strategic/Operational/Reference
- Creates related entries in appropriate databases

**Relations Created:**
- System Inbox → Executive Intent (linked via "Source" field)

---

### Step 2: **Triage & Classify** (Executive Intents)
**Location:** 2nd section - "Active Strategic Decisions"

**What You See:**
- New strategic decisions appear here automatically
- Each intent shows:
  - 🧠 AI Classification Results (callout)
  - Risk assessment
  - Impact score
  - Recommended agent
  - AI rationale

**What You Do:**
- Review the AI's classification
- Read the automated insights
- Decide if you want deeper analysis

**Relations:**
- ← Linked back to System Inbox (source)
- → Can spawn Action Pipes
- → Can generate Training Data

---

### Step 3: **Analyze** (Dialectic)
**What:** Run multi-agent adversarial analysis

**How:**
```bash
# Copy the Intent ID from the URL or page
curl -X POST http://localhost:8000/dialectic/{INTENT_ID}
```

**What Happens:**
1. **Growth Perspective** (🚀 Entrepreneur) analyzes
2. **Risk Perspective** (🔍 Auditor) analyzes
3. **Synthesis** combines both views
4. Results added directly to Intent page with:
   - Green callout: Growth recommendation
   - Red callout: Risk recommendation
   - Blue callout: Recommended path
   - Conflict points listed
5. Intent status → "Analyzed"

**Now Your Intent Page Contains:**
- Original classification
- Multi-agent dialectic results
- Synthesis
- Recommended path
- Next steps checklist

**All in one place!**

---

### Step 4: **Decide** (Review in Command Center)
**Location:** Your Executive Intent page (click from Command Center)

**What You Have:**
- ✅ AI classification
- ✅ Growth perspective
- ✅ Risk perspective
- ✅ Synthesis
- ✅ Recommended path
- ✅ Conflict points
- ✅ Next steps checklist

**What You Do:**
- Read through all perspectives
- Make your final decision
- Check off "Make decision" in the Next Steps list

---

### Step 5: **Execute** (Action Pipes)
**Location:** 3rd section - "Action Pipes"

**Option A: Create Action Manually**
1. Go to Action Pipes view in Command Center
2. Click "New"
3. Fill in action details
4. Set Intent relation to link it back

**Option B: Create Action via API**
```bash
curl -X POST "http://localhost:8000/intent/{INTENT_ID}/create-action" \
  -H "Content-Type: application/json" \
  -d '{
    "action_title": "Implement hiring decision",
    "action_description": "Execute the strategic intent"
  }'
```

**What Happens:**
- Action Pipe created
- Automatically linked to source Intent
- Execution checklist added:
  - Define specific tasks
  - Assign resources
  - Set timeline
  - Execute
  - Document results

**Relations:**
- Action Pipes → Executive Intents (via "Intent" field)
- Action Pipes → AI_Raw_Output (for training data)

---

### Step 6: **Learn** (Training Data)
**Location:** 5th section - "Training Data"

**What Happens:**
- As you edit AI suggestions, system captures diffs
- Stores in Training Data database
- Shows:
  - What AI recommended originally
  - What you actually chose
  - Acceptance rate
  - Modifications made

**Purpose:**
- Future fine-tuning of AI models
- Understanding your decision patterns
- Improving AI accuracy over time

**Relations:**
- Training Data → Executive Intents
- Training Data → Action Pipes (AI_Raw_Output field)

---

## 🔗 How Everything Connects

### Database Relations Map:

```
System Inbox
    ↓ (Source field)
Executive Intents
    ↓ (Intent field)
Action Pipes ←→ Training Data
    ↓                    ↑
Execution Log ← (logs everything)
    ↓
Training Data
```

### Key Relation Fields:

**System Inbox:**
- `Routed_to_Intent` → Executive Intents

**Executive Intents:**
- `Source` → System Inbox (where it came from)
- `Related_Actions` → Action Pipes (what got created)
- `Execution Record` → Execution Log
- `Agent_Persona` → Agent Registry (which AI analyzed it)

**Action Pipes:**
- `Intent` → Executive Intents (source decision)
- `Agent` → Agent Registry
- `AI_Raw_Output` → Stored for training data

**Training Data:**
- Links to both Intents and Actions
- Captures diffs between AI output and human edits

---

## 🎯 Example: Complete Flow

Let's walk through a real example:

### 1. You Create an Intent
**In System Inbox view (Command Center):**
- Title: "Should I hire a senior dev or 2 junior devs?"
- Content: "Budget: $200k. Need to scale team fast. Project launching in 3 months."

### 2. Auto-Triage (2 minutes)
**System automatically:**
- Classifies as "Strategic"
- Creates Executive Intent
- Adds to "Active Decisions" view
- Links back to System Inbox

**Executive Intent page now has:**
```
🧠 AI Classification Results
🟡 Risk: Medium
⚡ Impact: 8/10
📊 Agent: The Quant
Rationale: High-impact hiring decision requiring cost-benefit analysis

📋 Next Steps
☐ Review AI classification
☐ Run dialectic analysis
☐ Make decision
☐ Create action items
```

### 3. You Run Dialectic
**Command:**
```bash
curl -X POST http://localhost:8000/dialectic/2f7c8854-2aed-8142-9f68-dda8a0e5af83
```

**Intent page updates with:**
```
🤝 Multi-Agent Dialectic Analysis

🚀 Growth Perspective: Hire 2 junior devs
Focus: Lower cost, more velocity, redundancy

🔍 Risk Perspective: Hire 1 senior dev
Focus: Quality, mentorship, lower management overhead

💡 Synthesis
Hybrid approach: Hire 1 mid-level + 1 junior...

🎯 Recommended Path
Start with senior hire for foundation...

⚔️ Conflicts
• Cost vs quality tradeoff
• Short-term velocity vs long-term stability
```

### 4. You Decide
**You review and decide:** "Let's go with 1 senior dev first"

### 5. Create Action
**Command:**
```bash
curl -X POST "http://localhost:8000/intent/2f7c88.../create-action" \
  -d '{"action_title": "Hire Senior Developer", "action_description": "Post job, interview, hire by end of Q1"}'
```

**Action Pipes view updates:**
- New action appears
- Linked to source Intent (click to see full analysis)
- Execution checklist ready

### 6. Training Data Captured
**As you execute and refine:**
- AI suggested "senior + junior"
- You chose "senior only"
- System logs this preference
- Builds training data for future fine-tuning

---

## 🎨 What Makes This Cohesive

### 1. **Automatic Cross-Linking**
Every database entry links to related entries:
- Click Intent → See source inbox item
- Click Action → See source Intent and full analysis
- Click Training Data → See what Intent it came from

### 2. **Rich Context Everywhere**
No isolated data:
- Intents show full AI classification
- Actions show execution checklists
- Everything has "why" and "what next"

### 3. **Guided Workflow**
Each page tells you what to do next:
- ✅ Checkboxes for progress
- 📋 Next steps clearly listed
- ⚡ Quick commands provided

### 4. **One Source of Truth**
Command Center shows everything:
- All databases in one view
- Create, analyze, execute - all visible
- No tab-switching or database-hopping

### 5. **Learning Loop**
System gets smarter:
- Captures your decisions
- Learns your patterns
- Improves over time

---

## ⚡ Quick Reference Commands

### Daily Operations
```bash
# Update Command Center metrics
curl -X POST http://localhost:8000/command-center/update-metrics

# Trigger immediate triage
curl -X POST http://localhost:8000/trigger-poll

# Check system health
curl http://localhost:8000/health
```

### Per-Intent Workflow
```bash
# 1. Create intent (do this in Command Center Inbox view)

# 2. Wait 2 min for auto-triage, or trigger manually:
curl -X POST http://localhost:8000/trigger-poll

# 3. Run dialectic analysis
curl -X POST http://localhost:8000/dialectic/{INTENT_ID}

# 4. Create action from intent
curl -X POST http://localhost:8000/intent/{INTENT_ID}/create-action
```

---

## 📊 Command Center Setup (If Not Done)

If you haven't added the 6 linked database views yet:

1. **System Inbox** - Create items here
2. **Executive Intents** - Strategic decisions
3. **Action Pipes** - Execution tasks
4. **Agent Registry** - Your AI agents
5. **Training Data** - Learning loop
6. **Execution Log** - History

For each: Type `/linked` → Select database → Choose view type

---

## 🎓 Best Practices

### When to Use Each Database

**System Inbox:**
- ANY new item (strategic or operational)
- Quick capture
- System will route appropriately

**Executive Intents:**
- View only (auto-populated)
- Review and analyze
- Run dialectics
- Make decisions

**Action Pipes:**
- Implementation tasks
- Create from Intents
- Track execution

**Agent Registry:**
- View only
- See available AI personas
- Understand agent capabilities

**Training Data:**
- View only (auto-populated)
- Review system learning
- Analyze decision patterns

**Execution Log:**
- View only (auto-populated)
- Historical record
- Audit trail

### Workflow Tips

1. **Start in Inbox** - Always begin here
2. **Let System Triage** - Trust the AI classification
3. **Run Dialectic for Big Decisions** - $10k+, career moves, strategic pivots
4. **Create Actions After Deciding** - Not before
5. **Review Training Data** - Monthly, to see patterns

---

## 🔮 Future Enhancements (Optional)

Once you're comfortable with the workflow:

1. **Scheduled Metrics Updates** - Auto-refresh every hour
2. **Deploy to Railway** - 24/7 operation
3. **Upgrade to Sonnet** - Better analysis quality
4. **Fine-tuning** - Use training data for custom model
5. **Dashboard Analytics** - Visualize decision patterns

---

## ✅ Checklist: Is Your System Cohesive?

- [ ] All 6 database views added to Command Center
- [ ] Created test intent in System Inbox
- [ ] Intent auto-triaged to Executive Intents
- [ ] Ran dialectic analysis on intent
- [ ] Created action from intent
- [ ] Can click through relations (Inbox → Intent → Action)
- [ ] See contextual information on every page
- [ ] Understand the complete workflow

If all checked: **Your system is fully cohesive!** 🎉

---

**Last Updated:** 2026-01-29
**Version:** 2.0 - Fully Integrated Workflow

🤖 Generated with [Claude Code](https://claude.com/claude-code)
