# Auto-Dialectic Feature Guide

## What is Auto-Dialectic?

Auto-Dialectic automatically triggers comprehensive multi-agent dialectic analysis for high-impact strategic intents without requiring manual intervention. This ensures critical decisions receive full adversarial analysis (Growth vs Risk perspectives) immediately upon intent creation.

## When Does It Trigger?

Auto-dialectic automatically activates when **either** of these conditions is met:

1. **High Impact:** Intent has projected impact score **≥ 8** (out of 10)
2. **High Risk:** Intent is classified with **"High"** risk level

### Examples:

**✅ Will Trigger:**
- "Should I invest $50k in crypto?" (Impact: 9, Risk: High)
- "Launch new product line next month" (Impact: 8, Risk: Medium)
- "Restructure entire company operations" (Impact: 7, Risk: High)

**❌ Won't Trigger:**
- "Update marketing copy on website" (Impact: 4, Risk: Low)
- "Schedule team meeting for Friday" (Impact: 2, Risk: Low)
- "Research new productivity tool" (Impact: 5, Risk: Medium)

## What Happens When It Triggers?

### Automatic Flow:

```
1. Intent Created → Classification Complete
   ↓
2. Initial Agent Analysis (Single Agent)
   ↓
3. AUTO-DIALECTIC CHECK
   ↓
4. IF High-Impact/High-Risk:
   ├─ Run Growth Agent (The Entrepreneur)
   ├─ Run Risk Agent (The Auditor)
   ├─ Synthesize Both Perspectives
   ├─ Create Action Pipe with Synthesis
   └─ Log to Execution Log
   ↓
5. Continue Normal Workflow
```

### What You Get:

1. **Dialectic Analysis on Intent Page:**
   - Growth perspective (revenue, scalability)
   - Risk perspective (compliance, sustainability)
   - Synthesis of both views
   - Recommended path forward
   - Key conflict points

2. **Auto-Generated Action Pipe:**
   - Title: "🤖 Auto-Generated: [Your Intent Title]"
   - Contains complete synthesis
   - Ready for approval
   - Linked to original intent

3. **Execution Log Entry:**
   - Action: "Auto-Dialectic Triggered"
   - Details: Impact score, risk level
   - Timestamp of analysis

## Configuration

### Enable/Disable Feature

**Via Environment Variable:**
```bash
# Enable (default)
ENABLE_AUTO_DIALECTIC=true

# Disable
ENABLE_AUTO_DIALECTIC=false
```

**Via Code (config/settings.py):**
```python
enable_auto_dialectic: bool = True
```

### Current Thresholds (Hardcoded):
- High Impact: `>= 8`
- High Risk: `== "High"`

## User Experience

### Before Auto-Dialectic:

```
1. Create intent in System Inbox
2. Wait for classification
3. Check Executive Intents database
4. Manually run: curl -X POST http://localhost:8000/dialectic/{intent_id}
5. Wait for dialectic to complete
6. Check results
7. Create action manually
```

**Time:** ~5-10 minutes of manual work

### After Auto-Dialectic:

```
1. Create intent in System Inbox
2. Check Executive Intents database
3. Dialectic + Action already created!
```

**Time:** ~30 seconds (fully automated)

## Monitoring

### Check if Auto-Dialectic Ran:

1. **In Notion - Executive Intent Page:**
   - Look for "🤝 Multi-Agent Dialectic Analysis" section
   - If present, auto-dialectic ran

2. **In Notion - Execution Log:**
   - Filter for "Auto-Dialectic Triggered"
   - Shows which intents got automatic analysis

3. **In Action Pipes Database:**
   - Filter for titles starting with "🤖 Auto-Generated"
   - These were created by auto-dialectic

### Prometheus Metrics:

```promql
# Total auto-dialectics triggered
auto_dialectics_triggered_total

# By trigger reason
auto_dialectics_triggered_total{trigger_reason="high_impact"}
auto_dialectics_triggered_total{trigger_reason="high_risk"}

# Success rate
sum(rate(auto_dialectics_triggered_total{status="success"}[5m]))
/
sum(rate(auto_dialectics_triggered_total[5m]))
```

### Grafana Dashboard:

Add these panels:
- **Auto-Dialectic Triggers Over Time:** `rate(auto_dialectics_triggered_total[5m])`
- **Trigger Reasons Breakdown:** `sum by (trigger_reason) (auto_dialectics_triggered_total)`
- **Success vs Failed:** `sum by (status) (auto_dialectics_triggered_total)`

## Manual Override

You can still manually trigger dialectic even if auto-dialectic ran:

```bash
curl -X POST http://localhost:8000/dialectic/{intent_id}
```

This will:
- Re-run the dialectic analysis
- Add new results to the Intent page
- Create a new Action Pipe

**Use Case:** If you want to re-analyze with updated information.

## Error Handling

### What Happens if Auto-Dialectic Fails?

**Graceful Degradation:**
1. Error is logged to application logs
2. "Auto-Dialectic Failed" entry added to Execution Log
3. **Intent creation continues normally**
4. You can manually trigger dialectic later

**The workflow never crashes due to auto-dialectic failures.**

### Common Issues:

**Issue:** Auto-dialectic not triggering
**Check:**
- Is `ENABLE_AUTO_DIALECTIC=true`?
- Does intent meet criteria (impact ≥ 8 or risk = High)?
- Check application logs for errors

**Issue:** Action Pipe not created
**Check:**
- Look for "Auto-Dialectic Failed" in Execution Log
- Check application logs for specific error
- Verify Notion API connectivity

## Performance Impact

### Additional Processing Time:
- **Normal Intent:** ~2-5 seconds
- **With Auto-Dialectic:** ~15-35 seconds

### Why the difference?
- Auto-dialectic makes 2 additional LLM API calls:
  - Growth Agent analysis (~5-10 seconds)
  - Risk Agent analysis (~5-10 seconds)
- Creates additional Notion records:
  - Action Pipe
  - Execution Log entry

### Optimization:
Processing happens **synchronously** during intent creation to ensure all data is available immediately.

Future enhancement: Could move to background task for faster response.

## Best Practices

### 1. Review Auto-Generated Actions
Even though the system is automated, **always review** the Action Pipe before approval:
- Verify the synthesis makes sense
- Check if conflict points are legitimate
- Ensure recommended path aligns with goals

### 2. Adjust Classification Accuracy
If you're getting too many/few auto-dialectics:
- Improve classification prompt accuracy
- Ensure impact scores are calibrated
- Verify risk assessments are correct

### 3. Use Execution Log for Auditing
The Execution Log provides complete audit trail:
- Which intents triggered auto-dialectic
- When they ran
- Success/failure status

### 4. Monitor Performance
Track auto-dialectic metrics:
- Are they mostly succeeding?
- What's the average trigger rate?
- Is performance acceptable?

## Troubleshooting

### Auto-Dialectic Not Running

**Symptom:** High-impact intent created but no dialectic
**Debug Steps:**
1. Check feature flag: `echo $ENABLE_AUTO_DIALECTIC`
2. Verify classification: Check intent's impact/risk scores in Notion
3. Check logs: `grep "Auto-triggering dialectic" app.log`
4. Verify agent router: Test manual dialectic endpoint

### Action Pipe Not Created

**Symptom:** Dialectic ran but no Action Pipe
**Debug Steps:**
1. Check Execution Log for "Auto-Dialectic Failed"
2. Review application logs for errors
3. Verify Notion API permissions
4. Check Action Pipes database schema

### Performance Degradation

**Symptom:** Intent creation taking too long
**Debug Steps:**
1. Check Anthropic API latency
2. Monitor LLM response times
3. Consider disabling auto-dialectic temporarily
4. Review recent changes to prompts/logic

## FAQ

### Q: Can I disable auto-dialectic for specific intents?
**A:** Not currently. It's all-or-nothing via feature flag. Future enhancement could add per-intent override.

### Q: What if I disagree with the auto-dialectic synthesis?
**A:** You can:
1. Manually re-run dialectic: `POST /dialectic/{intent_id}`
2. Ignore the auto-generated Action Pipe
3. Create your own Action Pipe manually

### Q: Does auto-dialectic use more API credits?
**A:** Yes, each auto-dialectic makes 3 LLM calls (vs 1 for normal intent):
1. Growth Agent analysis
2. Risk Agent analysis
3. Synthesis generation

Estimated additional cost: ~$0.01-0.05 per auto-dialectic (depending on content length)

### Q: Can I change the trigger thresholds?
**A:** Currently hardcoded. To change:
1. Edit `app/workflow_integration.py` line 140-142
2. Modify the condition: `classification.get("impact", 0) >= 8`
3. Redeploy application

Future enhancement: Make these configurable via settings.

### Q: Will auto-dialectic work offline?
**A:** No, it requires:
- Anthropic API access (for LLM calls)
- Notion API access (for database updates)

If either API is unavailable, auto-dialectic will fail gracefully and log the error.

## Support

For issues or questions:
1. Check application logs: `tail -f logs/app.log`
2. Review Execution Log in Notion
3. Check Prometheus metrics
4. Open issue in repository

---

**Last Updated:** February 25, 2026
**Feature Version:** P3.1.1
**Status:** Production Ready ✅
