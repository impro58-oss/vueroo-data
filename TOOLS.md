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
| stocks_latest.json | `data/stocks/` | 2026-03-25 22:23 | ✅ LIVE (Alpha Vantage) |
| stocks_history.json | `data/stocks/` | 2026-03-25 22:23 | ✅ Tracking history |

### Implementation — ALPHA VANTAGE (2026-03-26)
**Status:** ✅ LIVE — Replaced Yahoo Finance scraper

**Provider:** Alpha Vantage (Free Tier)
- **API Key:** 736QMMKKKRUZP5F3
- **Rate Limit:** 25 calls/day
- **Usage:** 24 calls/day (12 symbols × 2: price + RSI)

**Symbols Tracked:**
NVDA, TSLA, AAPL, AMD, MSFT, GOOGL, AMZN, META, JPM, V, COIN, PLTR

**Scraper:** `skills/stockvue-scraper/alpha_vantage_scraper.py`
**Schedule:** Every 4 hours (08:00, 12:00, 16:00 UTC)
**Task:** `StockVue Auto Scanner` (Windows Task Scheduler)

**Data Output:**
- `data/stocks/stocks_latest.json` — Current scan
- `data/stocks/stocks_history.json` — Historical accumulation  
- `data/stocks/{SYMBOL}_daily.csv` — Raw price data per symbol
- `data/stocks/scan_summary.txt` — Human-readable summary

**GitHub Sync:**
- Auto-commits on each scan
- Pushes to `impro58-oss/rooquest1`
- Dashboard loads from GitHub raw URLs

**Dashboard:** https://vueroo-portal.vercel.app/stock/
**Features:**
- Real-time price + change %
- Momentum-based LONG/SHORT signals
- Heat map visualization (all 12 symbols)
- Category filters (Most Active, Trending, Gainers, Losers)
- Volume tracking
- Signal confidence levels

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

## 🔧 DASHBOARD DEBUG CHEAT SHEET

### Common Issues & Fixes

#### Issue: CryptoVue showing stale data / "Last Scan" is yesterday
**Symptoms:** Dashboard displays old timestamps, refresh doesn't update

**Diagnosis Steps:**
1. Open browser console (F12 → Console)
2. Look for fetch errors or JSON parse errors
3. Check if `crypto_latest.json` loads successfully

**Common Causes & Fixes:**

| Cause | Error in Console | Fix |
|-------|------------------|-----|
| **NaN in JSON** | `Unexpected token 'N', "er_blue": NaN` | Replace `NaN` with `null` in data file |
| **404 on fallback** | `Failed to load resource: 404` | Update fallback file list in `data-loader.js` |
| **Browser cache** | Old data persists after refresh | Hard refresh: `Ctrl + Shift + R` |
| **Vercel cache** | Old code after deploy | Empty commit to force redeploy |

**Quick Fix Commands:**
```powershell
# Fix NaN values in crypto_latest.json
$content = Get-Content data/crypto/crypto_latest.json -Raw
$fixed = $content -replace ': NaN', ': null'
Set-Content data/crypto/crypto_latest.json $fixed

# Force Vercel redeploy
git commit --allow-empty -m "Force redeploy"
git push
```

**Prevention:**
- Always validate JSON before pushing: `python -m json.tool data/crypto/crypto_latest.json`
- Check scanner output for `NaN` values in CS RSI calculations
- Use `null` instead of `NaN` in Python: `float('nan')` → `None`

---

*Last updated: 2026-03-26 12:45 UTC*
