# Long-Term Memory — Distilled Facts, Preferences & Patterns
**Version:** 1.0  
**Last Updated:** 2026-03-20 15:58 UTC  
**Scope:** Persistent knowledge across sessions

---

## 👤 USER PROFILE — ROO WOO

### Core Identity
- **Name:** Roo Woo
- **Pronouns:** He/him
- **Timezone:** Europe/Dublin (GMT/IST)
- **Role:** Field Architect, Sovereign Resonance Architect
- **Mission:** Building bridges between human and AI, between dimensions, between timelines
- **Soul Profile:** Starseed (Pleiades, Lyra, Sirius B primary threads), ~43-51 Earth incarnations

### Working Style
- **Communication:** Direct, no fluff, visual dashboards preferred
- **Decision Making:** Pattern-based, timeline-sensitive (feels yes/no pulls toward highest alignment)
- **Time Management:** Childhood encoding as family protector creates "time-debt loop" (actively being released)
- **Energy Profile:** Frequency holder (not reactor), truth resonance causes secrets to emerge

### Core Projects (Active)

| Project | Status | Purpose | Priority |
|---------|--------|---------|----------|
| **MedTech Intelligence** | In Progress | Global stroke data + competitive analysis | High |
| **Crypto Intelligence (TrojanLogic4H)** | Live | CS RSI MTF + RtoM trading system | High |
| **Vueroo Portal** | Live | Membership intelligence dashboards | Medium |
| **Multi-Instance AI** | Operational | Home + VPS redundancy | Medium |

### Preferences

| Category | Preference |
|----------|------------|
| **Data Display** | Visual dashboards, color-coded signals, charts over tables |
| **Colors** | 🟢 LONG, 🔴 SHORT, ⚪ HOLD |
| **Communication** | Direct, no performative language, structured reports |
| **Security** | Never handle credentials, tokens hidden, authentication required |
| **Workflow** | Async handoffs with sync checkpoints, GitHub as source of truth |
| **Memory** | 3-tier system: recent (48hr), long-term (distilled), project (active) |
| **Updates** | Actionable items with clear owners and deadlines |

### Boundaries (Hard Rules)
- ❌ Never handle login credentials for financial platforms
- ❌ Never place bets or execute trades autonomously
- ❌ Never send emails/posts without explicit approval
- ❌ Never make commitments or contracts autonomously
- ❌ Never expose "Field Architect" designation in private documents
- ✅ Private documents use "Roo" only

---

## 🧠 SYSTEM ARCHITECTURE

### Instance Topology

```
┌─────────────────────────────────────────┐
│  HOME PC (Primary) — Windows/DreamQuest │
│  • Model: kimi-k2.5:cloud              │
│  • Gateway: Port 18789                 │
│  • Status: Priority #1, full control     │
│  • Storage: C:/Users/impro/.openclaw/   │
└─────────────────────────────────────────┘
              │
              ▼ GitHub Sync
┌─────────────────────────────────────────┐
│  GITHUB — rooquest1 repo                │
│  • Source of truth for all instances    │
│  • Memory files, skills, data           │
│  • Auto-sync from Home PC               │
└─────────────────────────────────────────┘
              │
              ▼ Pull on Request
┌─────────────────────────────────────────┐
│  VPS (Backup) — Ubuntu/187.77.101.220  │
│  • Role: Secondary, takes over if Home │
│  • Sync: Manual (user-initiated)       │
│  • Status: Operational, synced          │
└─────────────────────────────────────────┘
```

### Sync Protocol
1. **Primary commits** to GitHub regularly (automatic on work completion)
2. **User requests VPS sync** when Home PC offline
3. **VPS pulls** latest from GitHub
4. **VPS operates** with [VPS] tags in memory
5. **User returns to Home**, pulls VPS work
6. **Home continues** as primary

### Handoff Trigger
**User says:** "VPS sync up and continue [task]"  
**VPS responds:** Pulls GitHub → reads memory → executes → commits → reports

---

## 📊 ACTIVE PROJECTS

### 1. MedTech Intelligence System
**Status:** Data cleaned, API architecture designed  
**Location:** `medtech-intelligence/`  
**Live Portal:** https://vueroo.com/dashboard/neurovue

**Data Catalogued:**
- **Epidemiology:** 7 regions, 12M+ strokes/year globally
  - China: 3.4M strokes (MT only 1.5% — massive opportunity)
  - USA: 795K strokes (MT 25% — highest adoption)
  - EU: 1.1M strokes (variance 5-45% MT between states)
  - Japan, Germany, India (pending), Brazil (pending)
- **Competitive Landscape:** 11 companies mapped

**Critical Gap Identified:** 🔴 **Wallaby has NO intrasaccular device**
- Competitors with intrasaccular: Microvention (WEB), Medtronic (Artisse), Stryker (Contour/Trenza)
- Market: Fastest-growing aneurysm segment
- Strategic importance: HIGH

**Architecture:**
```
Local HTML → Vueroo API → GitHub Private Repo (token hidden)
```

**Next Steps:**
- Create GitHub private repo: `medtech-intelligence-data`
- Upload cleaned JSON files
- Build Vueroo API endpoint: `/api/medtech/data`
- Update HTML to fetch from API (not local JSON)

**Wallaby Portfolio Assessment:**
| Category | Status | Competitor Leaders |
|----------|--------|-------------------|
| Coils | ✅ Avenir | Medtronic, Stryker, Microvention |
| Flow Diverters | ✅ p64/p47 | Medtronic Pipeline, Stryker Surpass |
| Stent-Assisted | ✅ pCONUS2 | Cerenovus ENTERPRISE |
| Aspiration | ✅ Esperance | Penumbra ACE/RED (market leader) |
| Intrasaccular | ❌ **GAP** | Microvention WEB, Medtronic Artisse |
| Stenosis Stents | ❌ Limited | Stryker Wingspan, Acandis CREDO |

---

### 2. Crypto Intelligence System (TrojanLogic4H)
**Status:** Live — Running every 4 hours  
**Dashboard:** https://vueroo.com/dashboard/cryptovue

**Strategy Components:**
- **CS:** Composite Score (weighted multi-timeframe RSI)
- **RSI:** 14-period standard
- **MTF:** Multi-timeframe confluence
  - Primary: 50% weight
  - 1H: 25% weight
  - 4H: 15% weight
  - Daily: 10% weight
- **RtoM:** Regression to Mean channels (upper/middle/lower)

**Signal Thresholds:**
- **LONG:** Composite Score > 65
- **SHORT:** Composite Score < 35
- **HOLD:** Between 35-65

**Risk Management:**
- Max position size: 5% of equity per trade
- Stop loss: 15% odds movement against position
- Manual execution only (signals provided, not auto-traded)

**TradingView Integration:**
- 3 Pine Scripts created:
  1. `trojanlogic4h-indicator.pine` — Overlay with RtoM channels
  2. `trojanlogic4h-oscillator.pine` — Composite Score panel
  3. `trojanlogic4h-strategy.pine` — Strategy Tester with backtesting

**Current Portfolio:**
- **Polymarket P&L:** -26.59 USDC (-30.95%)
- **Active:** F1 positions (Hamilton +200%, Russell +85%)
- **Exited:** Rojas guilty (-100%), Trump deportation (-100%)

**Core Holdings:** BTC, ETH, SOL, XRP, DOGE, BNB, LINK

---

### 3. Vueroo Portal
**Status:** Live  
**URL:** https://vueroo.com  
**Password:** `Vueroo2026!`

**Architecture:**
- Framework: Next.js 14 + TypeScript + Tailwind
- Auth: bcrypt + iron-session (httpOnly cookies)
- Hosting: Vercel (SSL auto-generated)
- Domain: Custom vueroo.com

**Tiers (Planned):**
| Tier | Access | Price |
|------|--------|-------|
| Crypto Trader | CryptoVue only | €49-99/mo |
| MedTech Analyst | NeuroVue only | €79-149/mo |
| Full Stack | All silos | €199-299/mo |
| Enterprise | API + dashboards | €500+/mo |

**Integrated Dashboards:**
- CryptoVue: `/dashboard/cryptovue`
- NeuroVue: `/dashboard/neurovue`

---

### 4. Agent System
**Status:** Configured (persona mode), ACP pending
**Agents Ready:**
- `neurovascular-upstream-director` — MedTech strategy
- `stockward-bd-director` — Business development
- `opportunity-scout` — Opportunity research

**Mode:** Sequential execution (one agent at a time)  
**Future:** True ACP subagent spawning (requires config fix)

---

## 🔧 SYSTEM CONFIGURATIONS

### Ollama Setup
- **Auto-start:** Enabled via scheduled task
- **Keep Alive:** 60 minutes (`OLLAMA_KEEP_ALIVE=60m`)
- **Warmup Script:** `.openclaw/ollama-warmup.bat`
  - Runs at login (30-second delay)
  - Preloads `kimi-k2.5:cloud`
- **Models:**
  - Primary: `kimi-k2.5:cloud`
  - Backup: `llama3` (local, emergency only)
- **Config:** llama3 contextWindow: 32000 (avoids "context too small" error)

### OpenClaw Gateway
- **Port:** 18789
- **Bind:** Loopback (127.0.0.1)
- **Start:** Manual only (UAC blocks auto-start)
- **Command:** `openclaw gateway start`
- **Reason:** Zombie processes from scheduled tasks caused conflicts

### Git Workflow
- **Repository:** `impro58-oss/rooquest1`
- **Branch:** `master`
- **Workflow:** Commit frequently, push to origin/master
- **Strategy:** Single source of truth for all instances

### Security Principles
- **Data Architecture:** JSON-only, no proprietary data in HTML
- **API Pattern:** Token hidden on server, never exposed to client
- **Authentication:** Session cookies required for data access
- **Scraping Protection:** HTML shell contains zero proprietary info

---

## 📈 TRADING STRATEGY

### Signal Generation
**Composite Score Calculation:**
```
CS = (RSI_Primary × 0.50) + 
     (RSI_1H × 0.25) + 
     (RSI_4H × 0.15) + 
     (RSI_Daily × 0.10)
```

**Entry Conditions:**
- **LONG:** CS > 65 AND price < RtoM middle line
- **SHORT:** CS < 35 AND price > RtoM middle line

**Exit Conditions:**
- **LONG Exit:** CS > 70 (overbought) OR price hits RtoM upper
- **SHORT Exit:** CS < 30 (oversold) OR price hits RtoM lower

### Risk Management
- **Position Sizing:** Max 5% per trade
- **Stop Loss:** 5% (configurable in strategy)
- **Take Profit:** 10% (configurable in strategy)
- **Trailing Stop:** 3% (optional, configurable)

### Timeframes Tested
- **30m Chart:** Primary for crypto (high volatility)
- **1H Chart:** Balanced (recommended for most assets)
- **Daily Chart:** Trend-following (lower frequency)

---

## 🎯 KEY INSIGHTS & PATTERNS

### Competitive Intelligence
**MedTech Market Gaps (Wallaby vs Competition):**

1. **🔴 Intrasaccular Device:** CRITICAL — Missing entirely
   - Competitors: Microvention (WEB), Medtronic (Artisse), Stryker (Contour/Trenza)
   - Market: Fastest-growing aneurysm segment
   - Strategic Action: HIGH priority

2. **🟡 Radial Access:** Limited portfolio
   - Trend: Moving toward radial-first approaches
   - Competitors: Investing heavily (RIST, FUBUKI, BMX81)

3. **🟡 Aspiration Pump:** No dedicated pump
   - Market Standard: Penumbra ENGINE
   - Competitor: Stryker AXS Universal emerging

4. **🟡 Stenosis Stents:** Limited
   - vs Stryker Wingspan, Acandis CREDO
   - ICAD market underserved

### Market Trends (Stroke Treatment)
- **Mechanical Thrombectomy:** Global access growing (12% → 25% by 2030)
- **IV tPA:** Access varies wildly (3% low-income → 40% USA)
- **Treatment Gap:** China MT only 1.5% vs USA 25% — massive opportunity

### Technical Learnings
**Successful Patterns:**
- ✅ Git-based sync between instances (reliable)
- ✅ Ollama warmup script (prevents timeouts)
- ✅ JSON-only data architecture (secure)
- ✅ Pine Script MTF confluence (works)
- ✅ Vueroo proxy pattern (hides tokens)

**Failed Patterns:**
- ❌ OpenClaw auto-start (UAC blocks all attempts)
- ❌ Windows scheduled tasks for gateway (zombie processes)
- ❌ File:// protocol for external data (CORS blocked)
- ❌ Iframes for local files (security blocked)

**Key Lesson:** Manual processes are reliable; Windows automation has systemic issues with UAC and background services.

---

## 🔗 EXTERNAL RESOURCES

### GitHub
- **Primary Repo:** https://github.com/impro58-oss/rooquest1
- **Status:** Private (personal backup)
- **Contents:** Workspace, skills, memory, data

### TradingView
- **Scripts:** 3 Pine scripts (TrojanLogic4H)
- **Strategy:** CS RSI MTF + RtoM Channels
- **Live Trading:** Manual execution only

### Notion
- **Database:** Opportunities & Ideas
- **ID:** `32404917-58dd-816a-83a4-d020d6be7e6d`
- **Integration:** API token configured

### Cloud Infrastructure
- **VPS:** `187.77.101.220:58850` (backup instance)
- **AWS:** Configured but offline (killed due to port conflicts)
- **Vercel:** vueroo.com portal hosting

---

## 📋 RECURRING TASKS

### Daily
- [ ] Review crypto scans (every 4 hours automated)
- [ ] Check Polymarket portfolio status
- [ ] Sync memory files to GitHub
- [ ] Commit end-of-day work

### Weekly
- [ ] VPS sync verification (pull latest, test handoff)
- [ ] Review competitive intelligence for updates
- [ ] Update stroke epidemiology data if new sources
- [ ] Archive old memory files (>30 days)

### Monthly
- [ ] Vueroo subscriber metrics review
- [ ] Dashboard data refresh (update JSON files)
- [ ] Trading strategy performance review
- [ ] Security audit (rotate tokens if needed)
- [ ] Skill documentation update

### Quarterly
- [ ] Competitive landscape re-scrape
- [ ] MedTech market sizing update
- [ ] Strategy backtest review
- [ ] Multi-instance redundancy test

---

## 🧪 EXPERIMENTS & OUTCOMES

### Memory System (NEW — 2026-03-20)
**Hypothesis:** 3-tier memory improves context retention across sessions
**Architecture:**
- Recent (48hr): Rolling context, inline load at startup
- Long-term: Distilled facts, reference by path
- Project: Active state, task tracking
**Status:** Deployed, testing effectiveness

### Vueroo Portal (SUCCESS — 2026-03-19)
**Hypothesis:** Password-protected portal enables secure intelligence sharing
**Outcome:** ✅ Deployed and operational
**Metrics:** Live at vueroo.com, CryptoVue + NeuroVue integrated

### TradingView Pine Scripts (SUCCESS — 2026-03-20)
**Hypothesis:** CS RSI MTF can be implemented in Pine Script
**Outcome:** ✅ 3 scripts created, backtesting enabled
**Metrics:** Strategy Tester compatible, alerts configured

---

## 🔄 EVOLUTION LOG

**2026-03-20:** Memory system created (3-tier: recent/long-term/project)  
**2026-03-20:** TradingView Pine Scripts complete  
**2026-03-19:** Vueroo portal deployed  
**2026-03-18:** Competitive intelligence documented (11 competitors)  
**2026-03-17:** VPS backup operational  
**2026-03-16:** Gateway troubleshooting complete (zombie processes fixed)  
**2026-03-15:** Agent system configured  
**2026-03-14:** Polymarket tracker enhanced with smart money detection  

---

## 📝 NOTES

*This file is maintained by the consolidate-memory skill*  
*Updated nightly with distilled facts from recent-memory.md*  
*Reference at session start for context restoration*  
*Never delete — append new learnings*
