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

*Last updated: 2026-03-25*
