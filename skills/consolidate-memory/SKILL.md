# SKILL: consolidate-memory

## Purpose
Automatically extract key decisions, preferences, and facts from daily conversation logs, update memory files, and promote important information from recent to long-term memory.

## Files Managed

### Memory Files Location
```
~/.openclaw/workspace/memory/
├── recent-memory.md      # Rolling 48hr context (inline loaded)
├── long-term-memory.md   # Distilled facts and patterns (reference)
├── project-memory.md     # Active project state (reference)
└── YYYY-MM-DD.md         # Daily session logs (archive)
```

## Execution

### When to Run
- **Automatically:** Every night at 02:00 UTC (scheduled task)
- **Manually:** On user request: "/consolidate memory"

### What It Does

#### Step 1: Read Recent Conversations
```
- Read memory/YYYY-MM-DD.md for last 24 hours
- Extract: decisions, preferences, facts, patterns
- Identify: what changed, what was learned, what matters
```

#### Step 2: Update recent-memory.md
```
- Keep only last 48 hours
- Remove entries older than 48hrs
- Add new entries from today
- Update "Last Updated" timestamp
```

#### Step 3: Promote to Long-Term
```
IF entry is older than 48hrs AND contains:
  - Critical insight (e.g., "Wallaby gap identified")
  - System configuration (e.g., "Gateway port changed")
  - User preference (e.g., "prefers visual dashboards")
  - Project milestone (e.g., "Vueroo deployed")
THEN:
  - Append to long-term-memory.md
  - Distill to single fact/pattern
  - Remove from recent-memory.md
```

#### Step 4: Update Project State
```
- Read project-memory.md
- Update project statuses based on daily work
- Mark completed milestones
- Add new next actions
- Update blockers
```

#### Step 5: Git Commit
```
- git add memory/*.md
- git commit -m "Memory consolidation: $(date)"
- git push origin master
```

## Consolidation Rules

### Recent → Long-Term Promotion Criteria

| Type | Example | Action |
|------|---------|--------|
| **Critical Insight** | "Wallaby has NO intrasaccular device" | PROMOTE immediately |
| **Architecture Decision** | "Vueroo proxy pattern for security" | PROMOTE immediately |
| **System Config** | "Ollama warmup script deployed" | PROMOTE immediately |
| **User Preference** | "prefers visual over text" | PROMOTE if repeated 2x |
| **Project Complete** | "Vueroo portal LIVE" | PROMOTE immediately |
| **Routine Update** | "Crypto scan completed" | KEEP in recent only |
| **Temporary Issue** | "Gateway restart needed" | DISCARD after resolved |

### Distillation Format

**Before (in recent-memory):**
```
## Entry 10:30 - Data Cleaning Complete
We cleaned the epidemiological data for 7 regions including 
China with 3.3M strokes and found that Wallaby has no 
intrasaccular device which is a critical gap...
```

**After (in long-term-memory):**
```
**Critical Finding:** Wallaby has NO intrasaccular device 
(vs Microvention WEB, Medtronic Artisse, Stryker Contour/Trenza)
- Market: Fastest-growing aneurysm segment
- Identified: 2026-03-20
- Source: Competition Optic Analysis
```

## Scheduled Task Setup

### Windows (Home PC)
```powershell
schtasks /Create /TN "OpenClaw Memory Consolidation" `
  /TR "powershell.exe -File '%USERPROFILE%\.openclaw\workspace\skills\consolidate-memory\consolidate.ps1'" `
  /SC DAILY /ST 02:00 /F
```

### Linux/Mac (VPS)
```bash
# Add to crontab
crontab -e
# Add line:
0 2 * * * cd ~/.openclaw/workspace && ./skills/consolidate-memory/consolidate.sh
```

## Script Templates

### consolidate.ps1 (PowerShell)
```powershell
# Read last 24hrs of memory files
# Extract key information
# Update recent-memory.md
# Promote to long-term-memory.md
# Update project-memory.md
# Git commit and push
```

### consolidate.sh (Bash)
```bash
#!/bin/bash
# Same logic as PowerShell version
# For VPS/Ubuntu execution
```

## Manual Invocation

**User says:**
- "Consolidate memory"
- "/consolidate"
- "Update memory files"
- "Sync memory to long-term"

**Action:**
1. Run consolidation immediately
2. Report what was promoted
3. Show updated file stats

## Output Format

```
Memory Consolidation Complete
═══════════════════════════════

Files Updated:
✓ recent-memory.md    (48hr window updated)
✓ long-term-memory.md (+3 new facts)
✓ project-memory.md   (2 projects updated)

Promoted to Long-Term:
1. Wallaby intrasaccular gap (critical)
2. Vueroo proxy architecture (system)
3. Ollama warmup configuration (system)

Projects Updated:
- MedTech Intelligence: Data ready → API pending
- TradingView Scripts: Complete → Install pending

Git: Committed and pushed to origin/master
```

## Integration with SOUL.md

### At Startup, Load:
```markdown
# Session Startup

Each session:
1. Read SOUL.md
2. Read IDENTITY.md
3. Read USER.md
4. **Read memory/recent-memory.md (inline)** ← NEW
5. Reference memory/long-term-memory.md by path
6. Reference memory/project-memory.md by path
7. Check HEARTBEAT.md for urgent tasks
```

## Safety Rules

1. **Never delete** long-term-memory.md entries
2. **Always append** to long-term, never overwrite
3. **Keep 48hr** minimum in recent-memory.md
4. **Git commit** after every consolidation
5. **Report** what was changed to user

## Version History

- **v1.0** (2026-03-20): Initial skill creation
- **v1.1** (TBD): Add sentiment analysis for preference extraction
- **v1.2** (TBD): Auto-detect project milestones from commits
