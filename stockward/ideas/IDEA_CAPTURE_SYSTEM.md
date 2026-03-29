# Idea Capture & Synthesis System
## The "Shower Thoughts" Pipeline
**Created:** March 29, 2026  
**Purpose:** Capture random ideas, evaluate systematically, synthesize into opportunities  
**Tagline:** "No idea lost. No bad idea pursued."

---

## 🎯 THE PROBLEM YOU IDENTIFIED

**Current State:**
- 💭 Random idea pops into head (shower, walk, 3 AM)
- 💬 Splurge it to me in Telegram
- ❓ ...then what? No structure. No evaluation. No synthesis.
- 🗑️ Ideas lost in chat history, forgotten, or inconsistently acted on

**Desired State:**
- 💭 Idea captured instantly (fast, low friction)
- 🏷️ Tagged and triaged (categorized, scored)
- 🔗 Synthesized (connected to other ideas, patterns detected)
- ⚖️ Evaluated (pursue / park / pass decision)
- 📊 Tracked (active pipeline, clear next steps)

---

## 📁 FILE STRUCTURE — The Idea Pipeline

```
stockward/ideas/
├── capture/                    # RAW IDEAS (fast dump)
│   ├── 2026-03-29-ai-documentation.md
│   ├── 2026-03-29-crypto-whale-tracker.md
│   └── TEMPLATE-raw.md         # Quick capture format
│
├── triage/                     # EVALUATED IDEAS (scored)
│   ├── SCORED-ai-documentation.md
│   ├── SCORED-crypto-whale-tracker.md
│   └── TEMPLATE-scored.md      # Evaluation framework
│
├── synthesis/                  # CONNECTED IDEAS (patterns)
│   ├── pattern-healthcare-ai.md
│   ├── pattern-smart-money-intel.md
│   └── TEMPLATE-synthesis.md   # Pattern detection
│
├── pipeline/                   # ACTIVE IDEAS (being worked)
│   ├── ACTIVE-ai-finance-manager/
│   ├── ACTIVE-[idea-name]/
│   └── INDEX.md                # What's being pursued
│
├── archive/                    # PARKED/PASSED IDEAS
│   ├── PARKED-2026/
│   ├── PASSED-2026/
│   └── INDEX.md                # Why we parked/passed
│
└── INDEX.md                    # Master idea catalog
```

---

## 🔄 THE PIPELINE — 5 Stages

### Stage 1: CAPTURE (Fast, Low Friction)

**Trigger:** You have an idea  
**Action:** Splurge it to me in Telegram (or voice note, or text)  
**My Response:**
1. Acknowledge receipt
2. Ask 3 clarifying questions (30 seconds)
3. Write to `capture/YYYY-MM-DD-[idea-name].md`
4. Tag with #raw-idea

**Capture Template (I fill this):**
```markdown
# Idea: [Name]
**Date:** YYYY-MM-DD HH:MM UTC  
**Source:** Telegram message from Roo  
**Raw Input:** "[Your exact words]"

## Clarifying Questions
1. [Q1] → [Your answer]
2. [Q2] → [Your answer]
3. [Q3] → [Your answer]

## Initial Framing
**Problem:** [What pain point does this solve?]  
**Solution:** [What's the core idea?]  
**Market:** [Who would pay for this?]  
**Differentiation:** [Why you, why now?]

## Tags
#raw-idea #[sector] #[type] #[status-new]

## Next Step
Triage evaluation (Stage 2)

---
*Captured by: Lumina*  
*Time: [timestamp]*
```

**Time:** 5 minutes  
**Goal:** Idea exists in system, not lost in chat

---

### Stage 2: TRIAGE (Score & Categorize)

**Trigger:** 24-48 hours after capture (cooling-off period)  
**Action:** I evaluate against scoring framework  
**My Output:** `triage/SCORED-[idea-name].md`

**Scoring Framework (FINTENDANT-derived):**

| Criteria | Weight | Score (1-5) | Notes |
|----------|--------|-------------|-------|
| **Market Size** | 20% | | $TAM, growth rate |
| **Problem Severity** | 20% | | How painful is the pain? |
| **Solution Feasibility** | 15% | | Can we actually build this? |
| **Competitive Advantage** | 15% | | Moat, differentiation |
| **Timing** | 15% | | Why now? Market readiness |
| **Fit to Skills** | 10% | | Can Roo + Lumina execute? |
| **Capital Efficiency** | 5% | | Can we bootstrap/prove? |

**Composite Score:** [Weighted total / 25]  
**Confidence:** [High/Medium/Low] — [Reasoning]

**Decision Gate:**
- **≥ 20/25:** → Pursue (move to pipeline/)
- **15-19/25:** → Park (move to synthesis/, monitor)
- **< 15/25:** → Pass (move to archive/PASSED/)

**Time:** 20-30 minutes  
**Goal:** Objective scoring, kill bad ideas fast

---

### Stage 3: SYNTHESIS (Connect & Combine)

**Trigger:** Multiple ideas in same sector, or pattern detected  
**Action:** Look for connections, combinations, emergent themes  
**My Output:** `synthesis/pattern-[theme].md`

**Pattern Types:**
1. **Convergence:** Two ideas that become one stronger idea
2. **Stack:** Ideas that build on each other (infrastructure → application)
3. **Wave:** Multiple ideas pointing to same macro trend
4. **Gap:** What's NOT being addressed (anti-pattern)

**Synthesis Template:**
```markdown
# Pattern: [Theme Name]
**Date:** YYYY-MM-DD  
**Pattern Type:** [Convergence/Stack/Wave/Gap]

## Contributing Ideas
1. [Idea A] — [Score] — [Link to capture]
2. [Idea B] — [Score] — [Link to capture]
3. [Idea C] — [Score] — [Link to capture]

## The Synthesis
**What we noticed:** [Pattern description]  
**The opportunity:** [Elevated/connected idea]  
**Why it's stronger:** [1+1=3 logic]

## Validation Questions
- [ ] Does this still solve a real problem?
- [ ] Is the market bigger than the sum of parts?
- [ ] Can we execute on the combined idea?
- [ ] What's the new competition landscape?

## Recommendation
[Pursue / Research more / Park]

## If Pursued
**New Project Name:** [Combined name]  
**Move to:** pipeline/[new-name]/  
**Priority:** [1-5]
```

**Time:** 30-60 minutes (when patterns emerge)  
**Goal:** Elevate individual ideas into stronger combined opportunities

---

### Stage 4: PIPELINE (Active Pursuit)

**Trigger:** Idea scored ≥ 20/25 OR synthesis validates combined idea  
**Action:** Move to active project status  
**Location:** `pipeline/[idea-name]/`

**Pipeline Structure:**
```
pipeline/[idea-name]/
├── README.md              # Project charter
├── business-model.md      # How we make money
├── market-analysis.md     # TAM, competition, trends
├── execution-plan.md      # Roadmap, milestones
├── validation-log.md      # Customer interviews, tests
├── decisions.md           # Key decisions with rationale
└── status.md              # Current state, blockers
```

**Status Tracking:**
- **Phase 0:** Idea validation (talk to customers)
- **Phase 1:** MVP scoping (define minimum viable)
- **Phase 2:** Build (execute)
- **Phase 3:** Launch (go to market)
- **Phase 4:** Scale (grow)

**Time:** Ongoing (weeks to months)  
**Goal:** Structured execution on validated ideas

---

### Stage 5: ARCHIVE (Learn & Move On)

**Trigger:** Idea parked or passed  
**Action:** Move to archive with reasoning  
**Location:** `archive/PARKED-YYYY/` or `archive/PASSED-YYYY/`

**Why Archive Matters:**
- **Learning:** Why did we pass? (avoid same mistake)
- **Timing:** Market not ready → revisit in 6-12 months
- **Connections:** Today's passed idea may inform tomorrow's

**Archive Entry:**
```markdown
# [Idea Name]
**Date Archived:** YYYY-MM-DD  
**Decision:** [Parked / Passed]  
**Score:** [X/25]  
**Reason:** [Why we didn't pursue]

## If Parked
**Revisit Trigger:** [What would make us revisit?]  
**Next Review Date:** YYYY-MM-DD

## If Passed
**Lessons:** [What we learned]  
**Related Ideas:** [Connections to other ideas]
```

---

## 🎯 COMMAND INTERFACE

### Quick Commands (Telegram)

| Command | Action |
|---------|--------|
| **"Idea: [description]"** | Triggers immediate capture (Stage 1) |
| **"/idea [description]"** | Explicit idea capture command |
| **"Triage my ideas"** | Run evaluation on all #raw-idea files |
| **"Synthesize patterns"** | Look for connections in recent ideas |
| **"What's in the pipeline?"** | Show ACTIVE projects |
| **"Show me parked ideas"** | Review archive for revisit |
| **"Idea status"** | Summary: capture/triage/pipeline counts |

### Natural Triggers
- "What if we..." → Capture
- "I just thought of..." → Capture
- "This might be crazy but..." → Capture
- "Remember that idea about..." → Retrieve + update

---

## 📊 DASHBOARD — Idea Health Metrics

**Weekly Summary (Auto-generated):**
```
IDEA PIPELINE STATUS — Week of [date]

Capture:      3 new ideas this week
Triage:       2 awaiting evaluation
Synthesis:    1 pattern detected (Healthcare AI)
Pipeline:     1 active (FINTENDANT)
Archive:      1 parked, 0 passed

Top Scored Idea: [Name] — 22/25 — Healthcare AI documentation
Pattern Alert: 3 ideas converging on AI + Clinical workflow

Recommended Action: Pursue Healthcare AI doc validation
```

---

## 💡 USAGE EXAMPLES

### Example 1: Healthcare AI Documentation (Real)

**Day 1, 09:28 — Capture:**
```
Roo: "Idea: AI voice recognition for NHS ward round documentation. 
Junior doctor spends 2.5h after shift reconstructing from memory."

Lumina: Captures to `capture/2026-03-28-nhs-ai-doc.md`
Asks clarifying questions → fills template
Tags: #raw-idea #healthcare #ai #nhs #workflow
```

**Day 2 — Triage:**
```
Lumina: Evaluates → Score: 21/25 (Market: 4, Problem: 5, Feasibility: 4, 
Timing: 4, Fit: 4)
Decision: PURSUE
Moves to `pipeline/healthcare-ai-doc/`
Creates: README.md, business-model.md, market-analysis.md
```

**Day 3 — Synthesis:**
```
Lumina: Notices this connects to:
- Consulting intelligence (McKinsey AI healthcare reports)
- Smart money (3 VCs invested in clinical AI)
- Pattern: "AI + Administrative burden"

Elevates: Part of "AI Administrative Automation" theme
```

### Example 2: Random Crypto Thought

**Day 1, 14:15 — Capture:**
```
Roo: "Idea: What if we tracked VC wallets like crypto whales? 
Follow the smart money in real-time?"

Lumina: Captures to `capture/2026-03-29-vc-whale-tracker.md`
```

**Day 2 — Triage:**
```
Lumina: Evaluates → Score: 19/25 (Market: 3, Problem: 4, Feasibility: 3, 
Competition: 3, Timing: 3, Fit: 3)
Decision: PARK (close, but data access issues)
Moves to `archive/PARKED-2026/`
```

**Day 5 — Synthesis:**
```
Lumina: Realizes this is SAME as consulting intelligence framework!
Elevates: Part of "Smart Money Intelligence Layer" 
Combined with consulting research → stronger together
```

---

## 🚀 IMMEDIATE SETUP

**Today:**
1. ✅ Create directory structure
2. ✅ Create templates
3. ✅ Write this framework document

**This Week:**
4. [ ] Retroactively capture 5 recent ideas from chat history
5. [ ] Triage them (score all 5)
6. [ ] Look for synthesis patterns
7. [ ] Populate pipeline/ with active ideas

**Ongoing:**
8. [ ] Every idea → capture in 5 minutes
9. [ ] Every 48h → triage new captures
10. [ ] Weekly → synthesis review
11. [ ] Monthly → pipeline status review

---

## 🎯 SUCCESS METRICS

**Monthly:**
- [ ] 10+ ideas captured
- [ ] 100% of ideas triaged within 48h
- [ ] 2+ patterns synthesized
- [ ] 0 ideas lost in chat history

**Quarterly:**
- [ ] 3+ ideas moved to pipeline
- [ ] 1+ idea launched or validated
- [ ] Archive: lessons documented
- [ ] Synthesis accuracy: Did patterns predict?

---

*System Version: 1.0*  
*Created: 2026-03-29*  
*Owner: Roo + Lumina*  
*Mission: No idea lost. No bad idea pursued. Good ideas elevated.*