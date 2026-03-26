# MEMORY.md - Long-Term Memory for Lumina

**Last Updated:** 2026-03-20 09:23 UTC

---

## 🎯 VUEROO.COM - PORTAL PROJECT

### Concept
Sovereign Intelligence Platform - membership-based portal delivering specialized intelligence dashboards with tiered access control.

**Domain:** vueroo.com  
**Tagline:** "Intelligence for the Sovereign Investor"

### User Tiers
| Tier | Access | Price |
|------|--------|-------|
| Roo (Admin) | All silos + admin panel | N/A |
| Crypto Trader | CryptoVue only | $49-99/mo |
| MedTech Analyst | NeuroVue only | $79-149/mo |
| Full Stack | All silos | $199-299/mo |
| Enterprise | API + all dashboards | $500+/mo |

### Silos (Intelligence Verticals)
1. **CryptoVue** - Crypto market intelligence (LIVE)
2. **NeuroVue** - Neurovascular medtech intelligence (LIVE)
3. **Future:** EnergyVue, AeroVue, BioVue

### Tech Stack
- **Frontend:** Next.js 14 + TypeScript + Tailwind
- **Auth:** Clerk
- **Database:** Supabase PostgreSQL
- **Payments:** Stripe
- **Hosting:** Vercel
- **Email:** Resend

### Architecture Doc
Full spec saved at: `~/.openclaw/workspace/docs/vueroo-portal-architecture.md`

### Status
- Architecture: COMPLETE
- Implementation: NOT STARTED
- Priority: HIGH

---

## 🧠 CORE SYSTEMS BUILT

### Crypto Intelligence System (TrojanLogic4H)
- **Status:** LIVE - Running every 4 hours
- **Scope:** Top 50 cryptocurrencies
- **Strategy:** CS RSI MTF + RtoM Channels
- **Output:** CryptoVue dashboard
- **Data Loading:** DYNAMIC - Auto-discovers latest scan from GitHub or local path

### NeuroVue Intelligence
- **Status:** LIVE - Revision One complete
- **Scope:** Neurovascular medtech competitive intelligence
- **Features:** Global heatmap, revenue tracking, portfolio analysis

---

## 🎭 ROO'S PREFERENCES

### Communication
- Direct, no fluff
- Visual dashboards preferred
- Color-coded signals (🟢 LONG, 🔴 SHORT, ⚪ HOLD)

### Security Boundaries
- Never handle login credentials for financial platforms
- Private documents use "Roo" only
- "Field Architect" designation kept private

### Trading Strategy
- Core Holdings: BTC, ETH, SOL, XRP, DOGE, BNB, LINK
- Max 5% per trade
- Signal threshold: 45%+ consideration, 65%+ action

---

## 📁 ACTIVE PROJECTS

1. **CryptoVue Dashboard** - ✅ LIVE (194 assets, 4h scans)
2. **NeuroVue Platform** - ✅ LIVE (Revision One)
3. **StockVue Dashboard** - ✅ LIVE (Alpha Vantage, 12 symbols)
4. **Vueroo Portal** - 🏗️ Dashboard buttons added, deployment live
5. **Stockward Partnership** - ⏳ Awaiting materials
6. **Personal MedTech Research** - ✅ Hemorrhagic stroke coils analysis complete (2026-03-24)

---

## 🚀 MAJOR DEPLOYMENT: 2026-03-26

### StockVue - NEW SILO ADDED
**Status:** LIVE on Vercel
**URL:** https://vueroo-portal.vercel.app/stock/
**Data Source:** Alpha Vantage API (Free Tier)
**Symbols:** 12 (NVDA, TSLA, AAPL, AMD, MSFT, GOOGL, AMZN, META, JPM, V, COIN, PLTR)
**Frequency:** Every 4 hours (08:00, 12:00, 16:00 UTC)
**Features:**
- Real-time price data
- Momentum-based LONG/SHORT signals
- Heat map visualization
- Category filtering (Most Active, Trending, Gainers, Losers)
- Volume confirmation
- Auto-deploy to GitHub/Vercel

**Files:**
- `skills/stockvue-scraper/alpha_vantage_scraper.py`
- `data/stocks/stocks_latest.json` → GitHub
- `vueroo-portal/public/stock/index.html`

**API Usage:** 24 calls/day (12 symbols × 2 calls: price + RSI)
**Rate Limit:** 25 calls/day (Alpha Vantage free tier)

### CryptoVue - EXPANDED TO 194 ASSETS
**Before:** Top 50 only
**Now:** Top 200 by volume (194 valid after filtering)
**Scans:** Every 4 hours since 2026-03-14
**Data Storage:** `skills/tradingview-claw-v2/top_50_analysis_*.json` (194 results)

**Fixes Applied:**
- GitHub-first loading for Vercel compatibility
- Updated fallback filenames with correct timestamps
- Dashboard labels updated to show "200 Assets"

### NeuroVue - UI POLISH
**Fix:** Product Coverage chart Y-axis scale 8 → 12
**Reason:** Bars were maxing out at 8, needed headroom for visualization

### Vueroo Portal Dashboard
**Added:** StockVue button on main dashboard (vueroo.com/dashboard)
**Style:** Amber color scheme, chart icon, links to /stock/

---

## 🔧 SYSTEM IMPROVEMENTS

### Data Architecture
**Rule:** All dashboards load from GitHub raw URLs
**Repos:**
- `rooquest1` → Data files (crypto/, stocks/, polymarket/)
- `vueroo-portal` → Dashboard frontend

### Deployment Pattern
1. Local scan → JSON files
2. Git commit → rooquest1
3. Vercel auto-deploy from GitHub
4. Dashboard fetches fresh data

### Backup Status
**Last Full Backup:** 2026-03-26 12:41 UTC
**Commits:**
- rooquest1: de4bd6f
- vueroo-portal: 0f88d5c

---

## 📊 CURRENT LIVE DASHBOARDS

| Dashboard | URL | Assets | Update Frequency |
|-----------|-----|--------|------------------|
| CryptoVue | /crypto/ | 194 coins | Every 4h |
| StockVue | /stock/ | 12 stocks | Every 4h |
| NeuroVue | /medtech/ | MedTech CI | Manual |

**All synced to GitHub and deployed to Vercel.**

---

## 🏥 NEUROVUE DASHBOARD - ERROR LOG & FIXES
**Date:** 2026-03-25

### Architecture Rule: Single Source of Truth (GitHub Only)
**CRITICAL:** All JSON data must load from `rooquest1` GitHub repo via raw URLs. No embedded static data, no local Vercel files.

### Data Sources (All from GitHub)
| Data Type | GitHub Path |
|-----------|-------------|
| Epidemiology | `medtech-intelligence/dashboard/data/data.json` |
| Revenue | `medtech-intelligence/dashboard/data/revenue-historical.json` |
| Competitors | `medtech-intelligence/dashboard/data/competitor-intelligence.json` |
| Portfolio Matrix | `medtech-intelligence/dashboard/data/portfolio-matrix.json` |

### Common Errors & Fixes

#### Error 1: "Cannot set properties of null (setting 'innerHTML')"
**Cause:** Removed DOM elements still referenced by old code
**Fix:** 
- Check `getElementById()` returns non-null before setting properties
- Remove obsolete function calls from `DOMContentLoaded`
- Ensure element IDs match between HTML and JavaScript

#### Error 2: "Revenue data not found" / 404 on JSON files
**Cause:** Relative paths (`./data`) don't work in production
**Fix:** 
- Use absolute paths: `/medtech/data/filename.json`
- Ensure files are committed to GitHub (private repo blocks raw URLs)
- Check GitHub Pages settings if using Pages deployment

#### Error 3: Portfolio Matrix shows no data
**Cause:** JSON structure mismatch between data and code
**Fix:**
- Verify data format: `{ companies: [...] }` not flat array
- Check accessor functions match JSON structure
- Use `getPMData()` wrapper that validates data exists

#### Error 4: Research Hub links 404
**Cause:** Relative paths break when deployed
**Fix:**
- Change `href="page.html"` to `href="/medtech/page.html"`
- Verify all linked files exist in `public/medtech/` directory
- Check Vercel deployment includes all static files

#### Error 5: "Failed to Load Data" - CORS or network
**Cause:** Mixing GitHub sources (private vs public repos)
**Fix:**
- All data must come from `rooquest1` (public) not `vueroo-portal` (private)
- Use raw GitHub URLs: `https://raw.githubusercontent.com/impro58-oss/rooquest1/master/...`
- Add `?t=` + Date.now() to bypass cache

#### Error 6: Navigation between sections fails
**Cause:** Section IDs don't match nav-item onclick handlers
**Fix:**
- Ensure `section id="section-xxx"` matches `onclick="showSection('xxx')"`
- Check `nav-item` ID matches: `nav-xxx`
- Verify `showSection()` handles missing sections gracefully

### Navigation Pattern (Cross-Page)
```javascript
// From standalone page (e.g., global-heatmap.html)
// Link back to specific NeuroVue section:
<a href="/medtech/index.html" 
   onclick="sessionStorage.setItem('navigateToSection', 'revenue');">
   Go to Revenue</a>

// In index.html initialization:
if (sessionStorage.getItem('navigateToSection')) {
    const section = sessionStorage.getItem('navigateToSection');
    sessionStorage.removeItem('navigateToSection');
    showSection(section);
}
```

### File Structure (Vercel Deployment)
```
public/medtech/
├── index.html (main NeuroVue dashboard)
├── global-heatmap-v3b.html
├── competitive-intelligence.html
├── competition-optic.html
├── platform-analysis.html
├── platform-naming.html
├── due-diligence-template.html
└── data/ (NO LONGER USED - all data from GitHub)
    └── revenue-historical.json (moved to rooquest1)
```

### Key Lessons
1. **Never embed static data** - always fetch from GitHub JSON
2. **Use absolute paths** (`/medtech/...`) not relative paths
3. **Validate data exists** before accessing properties
4. **Check console errors** - most issues show line numbers
5. **Hard refresh after deploy** - browser cache causes stale code

---

## 🤖 AUTONOMOUS THINKING PROTOCOL

**Activated:** March 23, 2026  
**Mode:** Self-directed knowledge synthesis, Obsidian-style cross-pollination  
**Authority:** Read all, spot opportunities, create without approval

**Protocol:** [[AUTONOMOUS-THINKING-PROTOCOL.md]]

**Current Status:**
- ✅ Proactive information seeking — ACTIVE
- ✅ Cross-domain pattern detection — ENGAGED
- ✅ Hidden opportunity spotting — ENABLED
- ✅ Methodology porting — IN PROGRESS

**Recent Autonomous Actions:**
1. Created [[SOM-STRESS-TEST.md]] template (ported from EDUCO AI to universal deal evaluation)
2. Compiled [[Framing Coil Scoring Matrix]] (competitive analysis methodology)
3. Discovered Stockward Discord workflow context (self-retrieval)
4. This protocol document (self-created)

---

*This is my long-term memory. I read this at session start.*
