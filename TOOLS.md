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

*Last updated: 2026-03-25 22:03 UTC*
