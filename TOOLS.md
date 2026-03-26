# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## NeuroVue Data Sources — KNOWLEDGE BASE

### Primary Data Files (Source of Truth)

| File | Location | Purpose |
|------|----------|---------|
| **epidemiology-comprehensive.json** | `medtech-intelligence/dashboard/data/` | **NEW** Combined stroke data (summary + detailed) |
| **revenue-summary.json** | `medtech-intelligence/dashboard/data/` | Company revenue, growth rates, market cap |
| **competitor-intelligence.json** | `medtech-intelligence/dashboard/data/` | Competitor profiles, products, gaps |
| **portfolio-matrix.json** | `medtech-intelligence/dashboard/data/` | Product portfolio coverage matrix |
| **product-portfolio-data.json** | `medtech-intelligence/dashboard/data/` | Detailed product listings by category |

### Epidemiology Data — COMBINED FORMAT

**Structure:**
```json
{
  "global": {
    "summary": {          // Quick stats for dashboard hero
      "2024": { annualStrokes, strokeDeaths, prevalence, treatmentAccess },
      "2030": { projectedStrokes }
    },
    "detailed": {       // Deep dive data
      "dalyLost": 143000000,
      "treatmentTechnologies": { stentRetrievers, aspiration, combined },
      "riskFactors": { hypertension, diabetes, af, obesity }
    }
  },
  "regions": {
    "china": {
      "flag": "🇨🇳",
      "population2024": 1412000000,
      "summary": { "2024": {...}, "2030": {...} },
      "detailed": {        // Rich data where available
        "2020Data": { treatment: { ivTpa, mechanicalThrombectomy }, economicBurden },
        "keyInsights": [...]
      }
    },
    "india": { "status": "pending_extraction" }  // Marker for gaps
  }
}
```

**Display Strategy:**
| View | Data Source | Use |
|------|-------------|-----|
| **Summary** | `global.summary` + `regions.*.summary` | Dashboard hero, quick stats |
| **Detailed** | `global.detailed` + `regions.*.detailed` | Deep dive, treatment outcomes, economics |
| **Pending regions** | `status: "pending_extraction"` | Flagged as "Data extraction in progress" |

**Used by:**
- `index.html` Epidemiology section — Summary/Detailed toggle
- `global-heatmap-v3b.html` — Global stroke burden visualization

### GitHub Repository
- **Repo:** `impro58-oss/rooquest1`
- **Branch:** `master`
- **Data URL:** `https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/`

### Revenue Data Flow

```
revenue-summary.json
    ├── neurovascularRevenue: number (in millions USD)
    ├── annualRevenue: number (total company)
    ├── revenueGrowth: number (%)
    ├── neurovascularGrowth: number (%)
    ├── marketCap: number
    └── ticker: string
```

**Used by:**
- `revenue-v2.html` — Revenue Analysis dashboard
- `competitive-intelligence.html` — CI cards (via shared loader)
- `index.html` — Overview metrics

### Data Loading Pattern

All dashboards use `NeuroVueDataLoader`:
```javascript
const appData = await NeuroVueDataLoader.loadNeuroVueData();
// Access: appData.revenue.companies
// Access: appData.competitors
// Access: appData.portfolio
```

### Data Accuracy Rules

| Rule | Action |
|------|--------|
| **Verified data exists** | Use exact value from revenue-summary.json |
| **No verified data** | Use **0.1** as marker (indicates gap) |
| **Never estimate** | Ask user for source or leave empty |
| **Always cite source** | Document where numbers came from |

### Cache Considerations
- GitHub raw files cache for ~5 minutes
- After pushing updates, wait 5 min before refresh
- Or add `?t=${Date.now()}` for cache-busting (dev only)

---

## SESSION LOG — 2026-03-25 (Evening Session)

### NeuroVue Dashboard Updates

**1. Wallaby Phenox Styling**
- Color changed to `#39FF14` (fluorescent green)
- Applied to: Portfolio Matrix header + cells, CI cards, Research Hub
- Empty product indicator: Changed from ❌ to ○ (neutral circle)
- Commit: `c288410`

**2. NeuroRevenue Field Added**
- Source: `revenue-summary.json`
- Values (in $M):
  - Medtronic: 1380, Stryker: 1450, J&J: 680, Microvention: 520
  - Penumbra: 380, Balt: 180, Phenox: 95, Rapid: 35, Acandis: 45, Imperative: 65
- Displayed in CI cards with $ icon

**3. Product Portfolio Manager**
- Created: `product-portfolio-manager.html`
- Features: Load JSON, edit cells, add/delete rows, export
- Added to Research Hub with pink styling
- Font sizes increased (header 24px, body 15px)
- JSON loading: Better error handling + debug logging

**4. Epidemiology Data Consolidation**
- **NEW FILE**: `epidemiology-comprehensive.json`
- Combines `data.json` (summary) + `stroke-intelligence.json` (detailed)
- Structure: `global.summary` + `global.detailed` + `regions[].summary` + `regions[].detailed`
- Pending regions: India, Brazil, Africa, SE Asia (marked as "pending_extraction")
- Dashboard: Summary/Detailed view toggle

### Key Principles Reinforced
- **0.1** = marker for unverified data (not estimates)
- **Never estimate financial data** — use verified sources only
- **Source files** for NeuroVue:
  - `epidemiology-comprehensive.json` — Stroke data
  - `revenue-summary.json` — Company revenue
  - `competitor-intelligence.json` — Competitor profiles
  - `portfolio-matrix.json` — Product coverage

### Git Sync Status
- **rooquest1** (data): ✅ Synced
- **vueroo-portal** (dashboard): ✅ Synced
- **Commit**: `31ca869` — "Sync: Backup all changes..."

---

## 📊 STOCKVUE DATA COLLECTION — YAHOO FINANCE STATUS

**Current Status:** ⚠️ NOT COLLECTING DATA

### What Happened
- **Last successful scan:** None (scraper running but returning 0 results)
- **Issue:** Yahoo Finance blocking Playwright scraper (JavaScript-rendered anti-bot protection)
- **Scraper:** `yahoo_finance_scraper_v2.py` using Playwright with stealth
- **Schedule:** Every 3 hours via `StockVue Auto Scanner` task

### Current Data Files
| File | Location | Last Update | Status |
|------|----------|-------------|--------|
| stocks_latest.json | `data/stocks/` | 2026-03-25 22:23 | Empty (0 stocks) |
| stocks_history.json | `data/stocks/` | 2026-03-25 22:23 | Empty |

### Root Cause
Yahoo Finance has implemented aggressive anti-scraping:
- JavaScript challenges requiring browser fingerprinting
- Rate limiting and IP blocking
- Dynamic content that doesn't render in headless mode
- Cloudflare protection on some endpoints

### Solution Options
1. **Alpha Vantage API** — Free tier 25 calls/day, paid plans available
2. **Polygon.io** — $49/mo for 1000 calls/min, institutional quality
3. **Finnhub** — Free tier 60 calls/min, good for US stocks
4. **Yahoo Finance API** — Unofficial endpoints (yfinance library) — may break
5. **Manual data import** — Import from broker exports (TD/IBKR/etc)

### Recommended Fix
**Option: Alpha Vantage + Finnhub combo**
- Alpha Vantage: Core price data, technical indicators
- Finnhub: Real-time news, sentiment
- Cost: Free tier sufficient for daily scans
- Reliability: API-based, won't break like scraping

### Immediate Action Required
Choose one:
- [ ] **Sign up for Alpha Vantage** (free API key) — I'll update scraper
- [ ] **Sign up for Polygon.io** ($49/mo) — Higher quality data
- [ ] **Pause StockVue** until you decide — Stop wasting compute cycles

---

## 🔄 AUTO-BACKUP IMPLEMENTATION — COMPLETE

### ✅ Daily Memory Backup
**Script:** `scripts/daily-memory-backup.ps1`  
**Schedule:** Daily at 23:00  
**What it does:**
- Creates zip archive in `C:\Users\impro\OneDrive\OpenClaw\backups`
- Commits memory files to GitHub
- Cleans up archives older than 30 days
- Writes status to `memory/backup-status.json`

**Status:** ✅ ACTIVE (created 2026-03-26)

### ✅ Workspace Auto-Commit
**Script:** `scripts/auto-commit-workspace.ps1`  
**Schedule:** Every 2 hours (recommend setting up)  
**What it does:**
- Stages changes in `data/`, `memory/`, `scripts/`, `skills/`
- Commits with timestamp
- Pushes to `impro58-oss/rooquest1`

**To activate:** Run `setup-auto-commit-task.ps1`

---

*Last updated: 2026-03-26 06:58 UTC*
