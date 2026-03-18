# Agent Report Template - gstack Workflow Integration
## Version 2.0 - With Workflow Stages

---

## Workflow Stages (gstack Model)

### Stage 1: PLAN
**Before starting work, define:**
- What problem are we solving?
- What does success look like?
- What are the constraints?
- What could go wrong?

### Stage 2: EXECUTE
**Do the work:**
- Follow the plan
- Document progress
- Handle edge cases
- Stay focused on goal

### Stage 3: REVIEW
**Quality check before completion:**
- Does this solve the original problem?
- Are there bugs or issues?
- Is documentation complete?
- Would this pass a peer review?

### Stage 4: DOCUMENT
**Save for future reference:**
- Write to memory file
- Update Notion databases
- Log key decisions
- Archive artifacts

---

## Entry HH:MM - [AGENT NAME] Task Complete

**Agent:** [agent-name]
**Task:** [brief description]
**Status:** [completed/partial/failed]
**Runtime:** [duration]

### Stage 1: PLAN
**Problem:** [What we needed to solve]
**Success Criteria:** [How we know it's done]
**Constraints:** [Time, resources, limitations]
**Risks:** [What could go wrong]

### Stage 2: EXECUTE
**What was done:**
- [Step 1]
- [Step 2]
- [Step 3]

**Progress notes:**
- [Any deviations from plan]
- [Discoveries made]
- [Adjustments needed]

### Stage 3: REVIEW
**Quality Check:**
- ✅ Solves original problem: [Yes/No - why]
- ✅ No critical bugs: [Yes/No - list if any]
- ✅ Documentation complete: [Yes/No]
- ✅ Peer review ready: [Yes/No]

**Issues found:**
- [List any bugs or concerns]
- [Severity: Critical/Medium/Low]

### Stage 4: DOCUMENT
**Key Findings:**
- [bullet 1]
- [bullet 2]
- [bullet 3]

**Data/Files Created:**
- [file path 1]
- [file path 2]

**Notion Updates:**
- Database: [name]
- Entries: [count]

**Recommendations:**
- [Action item 1]
- [Action item 2]

**Confidence Level:**
[High/Medium/Low] - [reasoning]

**Next Steps:**
[What should happen next]

---

## Agent Status Tracking

**Active Agents:**
- neurovascular-upstream-director: [status]
- stockward-bd-director: [status]
- opportunity-scout: [status]
- [future agents listed here]

**Last Check-in:** [timestamp]
**Pending Tasks:** [count]
**Completed Today:** [count]

---

## Daily Brief Compilation

**Time:** 6:30 AM daily
**Compiled by:** Lumina
**Includes:**
- All agent activity from previous 24h
- Key findings summary
- Recommended actions
- Escalation items (if any)

### Daily Brief Template

```markdown
# Daily Agent Activity Brief - [DATE]

## Summary
[X] agents active, [Y] tasks completed, [Z] findings requiring review

## Agent Reports

### 1. [Agent Name]
**Task:** [what they did]
**Key Finding:** [most important result]
**Recommendation:** [what Lumina suggests]
**Action Required:** [yes/no - what]

### 2. [Next Agent]
...

## Priority Actions
1. [Highest priority item]
2. [Second priority]
3. [Third priority]

## Escalations
- [None / list items needing immediate attention]

## System Health
- All agents: [operational/degraded/offline]
- Scheduled tasks: [running/on time/delayed]
- Data sync: [current/stale]

---
Compiled by Lumina at [TIME]
```

---

## Control Gates

**NO autonomous actions without approval:**
- No external outreach
- No financial transactions
- No commitments or contracts
- No database deletions

**Lumina reviews all agent outputs before presenting to Roo**

---

## Escalation Triggers

**Immediate alert to Roo:**
- High-confidence opportunity (>80%)
- Critical error or failure
- Time-sensitive finding
- Unexpected result

**Batch in daily brief:**
- Routine analysis complete
- Background research
- Data updates
- Monitoring reports

---

## Agent Registry

| Agent Name | Role | Status | Last Active | Output Location |
|------------|------|--------|-------------|-----------------|
| neurovascular-upstream-director | MedTech Strategy | Active | 2026-03-15 14:46 | memory/YYYY-MM-DD.md |
| stockward-bd-director | Business Development | Active | 2026-03-15 16:42 | memory/YYYY-MM-DD.md |
| opportunity-scout | Opportunity Research | Active | 2026-03-15 18:11 | memory/YYYY-MM-DD.md |
| [pending] | LUXBRIDGE Research | Pending | - | - |

---

## gstack Integration Notes

**What we adopted from gstack:**
1. **Plan stage** - Pressure-test before building
2. **Review stage** - Quality gates before completion
3. **Document stage** - Automatic documentation

**What we kept from original:**
- Agent registry
- Control gates
- Escalation triggers
- Daily brief format

**Improvement estimate:**
- +40% efficiency (clear stages)
- +30% quality (review gates)
- +25% consistency (standardized outputs)

---

*Template Version: 2.0*
*Last Updated: 2026-03-17*
*Based on: gstack workflow model + original AGENTS.md*