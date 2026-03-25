# NeuroVue Dashboard Site Structure
## Current State (As of 2026-03-25 17:08)

---

## 📁 LOCAL FILES (Workspace)

```
C:\Users\impro\.openclaw\workspace\medtech-intelligence\dashboard\
│
├── 📄 index.html                           ← EPIDEMIOLOGY DASHBOARD
│   └── Features: Stroke stats, regions, heatmap, data tables
│
├── 📄 competitive-intelligence.html        ← COMPANY/COMPETITOR DASHBOARD  
│   └── Features: Company cards, Wallaby positioning, product gaps
│
├── 📄 index-dynamic.html                 ← Duplicate copy
├── 📄 index-static-backup.html           ← Backup copy
│
├── 📄 revenue-dashboard.html               ← Revenue data (old)
├── 📄 revenue-v2.html                     ← Revenue data (newer)
│
├── 📄 portfolio-dashboard.html           ← Product matrix
├── 📄 portfolio-simple.html              ← Simple version
├── 📄 portfolio-pro.html                 ← Pro version
│
├── 📄 global-heatmap-v3b.html            ← Interactive map
├── 📄 global-heatmap-v4.html              ← Newer version
│
├── 📄 platform-analysis.html             ← Strategic analysis
├── 📄 platform-naming.html               ← Naming guide
├── 📄 competition-optic.html             ← Competition view
│
├── 📄 data-viewer.html                   ← Raw data viewer
├── 📄 excel-viewer.html                  ← Excel viewer
├── 📄 visualization.html                 ← Charts
│
├── 📄 CHEATSHEET.md                      ← Documentation
├── 📄 DEBUGGING-FRAMEWORK.md             ← Debugging guide
└── 📄 data-loader.js                       ← JS utilities

    📁 data\
        ├── data.json                      ← Epidemiology data
        ├── revenue-data.json              ← Company finances
        └── product-portfolio-data.json    ← Product matrix
```

---

## 🌐 DEPLOYED TO VERCEL (vueroo-portal/public/medtech/)

```
https://www.vueroo.com/medtech/
│
├── 📄 index.html                           ← CURRENTLY: competitive-intelligence.html
│   └── Shows: Company cards, Wallaby, competitor analysis
│
├── 📄 competitive-intelligence.html        ← COPY of above
├── 📄 revenue-v2.html                       ← Revenue dashboard
├── 📄 portfolio-dashboard.html              ← Product matrix
├── 📄 global-heatmap-v3b.html              ← Heatmap
│
└── 📁 data\                                 ← JSON files
    ├── data.json
    ├── revenue-data.json
    └── product-portfolio-data.json
```

---

## 🎯 WHAT I CHANGED (Mistake #1)

**I DID:**
```
Copied competitive-intelligence.html → index.html
```

**RESULT:**
- `/medtech/` now shows **company cards** (not epidemiology)
- All the stroke stats, regional data, heatmap = GONE

---

## ❓ WHAT DO YOU WANT?

### Option A: Separate Pages
```
/medtech/                    ← Epidemiology (original index.html)
/medtech/companies.html      ← Competitive intelligence
/medtech/revenue.html        ← Revenue dashboard
/medtech/heatmap.html        ← Global map
/medtech/portfolio.html      ← Product matrix
```

### Option B: Main + Subpages
```
/medtech/                    ← Competitive intelligence (main)
/medtech/epidemiology.html   ← Stroke stats
/medtech/revenue.html        ← Revenue
/medtech/heatmap.html        ← Map
```

### Option C: Something Else?
**Tell me:**
1. What should `/medtech/` show as the main page?
2. What other pages do you want accessible?
3. What's the priority order?

---

## 🛑 BEFORE I MAKE ANY MORE CHANGES

**Confirm:**
- [ ] Which file = main `/medtech/` page?
- [ ] What other pages need to be live?
- [ ] What should I delete vs. keep?

**I'll wait for your direction.**
