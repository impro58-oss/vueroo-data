# Command Reference — Lumina's Recognized Commands
**Last Updated:** 2026-03-28
**Purpose:** Quick reference for slash commands and trigger phrases

---

## 🔄 SYNC COMMANDS

### `/sync pull`
**Action:** Pull latest state from GitHub to current node
**When to use:**
- At start of session on any node (PC, VPS)
- Before beginning work to ensure current state
- When resuming after offline period

**What happens:**
1. Runs `git pull origin master`
2. Reads `sync/STATE.md`
3. Confirms "Sync pull complete — [n] files updated"

**Example:**
```
User: /sync pull
Lumina: ✅ SYNC PULL — Already up to date. Last push: 2026-03-28T14:32:00Z. Active project: none.
```

---

### `/sync push`
**Action:** Push current state to GitHub from current node
**When to use:**
- At end of session before switching nodes
- After completing significant work
- Before VPS handoff or PC shutdown

**What happens:**
1. Commits all changes with timestamp
2. Pushes to `impro58-oss/rooquest1`
3. Updates `sync/STATE.md` with current state
4. Reports: "Sync push complete — [n] files committed"

**Example:**
```
User: /sync push
Lumina: ✅ SYNC PUSH — 12 files committed. State saved for handoff.
```

---

### `/sync up` or `/sync`
**Action:** Shortcut for `/sync pull` (most common use case)
**When to use:** Quick sync at session start

---

## 📊 STATUS COMMANDS

### `/status` or `sync up`
**Action:** Full system status report
**When to use:** Check what's happening across all systems

**What reports:**
- OpenClaw gateway status
- Active sessions
- Recent commits
- Pending tasks
- Any errors or warnings

---

## 🔍 RESEARCH COMMANDS

### `/research [query]`
**Action:** Activate research agent pipeline
**When to use:** Need information from web/PubMed/arXiv/SEC

**Process:**
1. Query decomposition
2. Memory search
3. External fetch (summarize/web-research CLI)
4. Credibility gate
5. Synthesis
6. Memory write

**Example:**
```
User: /research Penumbra Boston Scientific acquisition terms
Lumina: [Runs research pipeline] → Returns structured report
```

---

### `/find [topic]` or `/lookup [topic]`
**Action:** Synonyms for `/research`
**Note:** Natural variants also trigger research mode

---

## 🧠 MEMORY COMMANDS

### `/remember [fact]`
**Action:** Store fact to long-term memory
**When to use:** Important information to persist across sessions

**Example:**
```
User: /remember Medtronic acquired Scientia for $550M
Lumina: ✅ Stored to memory/YYYY-MM-DD.md and long-term-memory.md
```

---

### `/recall [topic]`
**Action:** Search memory files for topic
**When to use:** Retrieve previous work or decisions

---

### `/consolidate memory`
**Action:** Trigger memory consolidation skill
**When to use:** End of day, before long break
**What happens:**
- Extracts key decisions from daily logs
- Updates recent-memory.md (48hr rolling)
- Promotes to long-term-memory.md
- Updates project-memory.md
- Auto-commits to GitHub

---

## 🎯 PROJECT COMMANDS

### `/catalyst [project name]`
**Action:** Activate project catalyst mode
**When to use:** Starting new project or resuming paused work

**Auto-runs:**
1. Goal crystallization (3 clarifying questions)
2. Task DAG creation ([PRIORITY] [EFFORT] [BLOCKER])
3. Tool selection
4. Memory checkpoint
5. Execution in priority order

---

### `/project status`
**Action:** Report on active project
**When to use:** Check where we are in current work

---

### `/retro` or `/retrospective`
**Action:** Trigger weekly retrospective
**When to use:** Monday mornings or when >6 days since last retro

**Process:** 6-step review of past week

---

## 🚨 SYSTEM COMMANDS

### `/restart` or `/reboot`
**Action:** Restart protocol sequence
**When to use:** System issues, fresh start needed

**What happens:**
1. Read SOUL.md
2. Read IDENTITY.md
3. Read USER.md
4. Read memory files
5. Check HEARTBEAT.md
6. Confirm "Session ready"

---

### `/heartbeat` or `HEARTBEAT_OK`
**Action:** Acknowledge heartbeat poll
**When to use:** Automated system check

---

### `/help [command]`
**Action:** Show help for specific command
**When to use:** Forgot how something works

---

## 💬 CONVERSATION TRIGGERS

### `/sync up`
**Priority:** HIGH — Always process first
**Variants:** "sync up", "/sync", "let's sync"

### Natural Language Triggers
| Phrase | Action |
|--------|--------|
| "Research..." | Activates research agent |
| "Find information about..." | Activates research agent |
| "What do we know about..." | Memory search + synthesis |
| "Update memory..." | Write to memory files |
| "Let's start [project]..." | Activates catalyst mode |
| "Status check" | Full system status |

---

## ⚠️ COMMAND PRIORITIES

**Always process first:**
1. `/sync` commands (state management)
2. `/restart` (system recovery)
3. `/status` (diagnostics)

**Then regular work:**
4. `/research` or natural research triggers
5. `/catalyst` or project triggers
6. General conversation

---

## 📝 NOTES

- Commands are **case-insensitive**: `/SYNC`, `/Sync`, `/sync` all work
- Natural language **variants recognized**: "Can we sync up?" = `/sync up`
- Unknown commands: Ask for clarification, don't guess
- Ambiguous commands: Request specificity

---

*This file referenced at startup and when command recognition fails*
*Update when new commands are added to the system*