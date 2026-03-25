# NeuroVue Dashboard Cheatsheet
## Version: 2.0 - Dynamic Data Loading

---

## 🔧 Fix Log

### Fix #1: CORS Issue on Local File Access
**Date:** 2026-03-25
**Problem:** Loading spinner stuck when opening `file://` — browser blocks fetch() on file protocol
**Solution:** Deploy to GitHub Pages / web server — CORS only blocks file://, not http/https
**Test URL:** https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/index.html

---

### Fix #2: Embedded Global Heatmap
**Date:** 2026-03-25  
**Git Commit:** `b13d9c4`  
**Problem:** Heatmap only accessible via external link, not embedded  
**Solution:** Added iframe embedding `global-heatmap-v3b.html` in dashboard hero section  
**Files Modified:** `index.html`

**Code Added:**
```html
<!-- Global Heatmap Iframe -->
<div class="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden mb-8">
    <div class="p-6 border-b border-slate-800">
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-lg font-semibold text-white">Global Neurovascular Heat Map</h3>
            </div>
            <a href="global-heatmap-v3b.html" target="_blank">Full Screen</a>
        </div>
    </div>
    <div class="relative" style="height: 600px;">
        <iframe src="global-heatmap-v3b.html" class="w-full h-full border-0"
            title="Global Neurovascular Heat Map" loading="lazy" allowfullscreen>
        </iframe>
    </div>
</div>
```

---

## 📁 File Structure

```
medtech-intelligence/dashboard/
├── index.html              ← Main dashboard (dynamic)
├── index-dynamic.html      ← Identical copy (backup)
├── data-loader.js          ← NEW: Dynamic data loading with GitHub fallback
├── global-heatmap-v3b.html ← Interactive D3 map
├── revenue-v2.html         ← Revenue dashboard (dynamic)
├── portfolio-dashboard.html
├── data/
│   ├── data.json           ← Epidemiology data
│   ├── product-portfolio-data.json
│   └── revenue-data.json   ← Company financials
└── CHEATSHEET.md           ← This file
```

---

## 🔗 Data Loader Pattern

**GitHub Raw URL Base:**
```javascript
const GITHUB_RAW_URL = 'https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/';
```

**Fallback Chain:**
1. Try local `./data/{filename}`
2. On fail → fetch from GitHub raw
3. On fail → use embedded fallback data

**Files Loaded:**
- `data.json` → Epidemiology (regional stroke data)
- `product-portfolio-data.json` → Product categories
- `revenue-data.json` → Company financials

---

## 🛠️ Common Tasks

### Test Locally (CORS-free)
```bash
cd medtech-intelligence/dashboard
python -m http.server 8000
# Open: http://localhost:8000
```

### Push to GitHub
```bash
cd medtech-intelligence/dashboard
git add .
git commit -m "NeuroVue v2.0: Dynamic data + embedded heatmap"
git push
```

### View Live

**✅ DEPLOYED TO VERCEL**
- **Commit:** `2e62f07` in `vueroo-portal` repo
- **Live URL:** `https://www.vueroo.com/medtech/`
- **Status:** Deployed at 2026-03-25 14:57 UTC

### Deployment Details
| Repo | Branch | Commit | Files Added |
|------|--------|--------|-------------|
| `impro58-oss/vueroo-portal` | main | `2e62f07` | 31 files, 374KB |
| `impro58-oss/rooquest1` | master | `abcfc61` | Submodule update |

**Vercel Build:** Auto-deployed from `vueroo-portal:main`

---

## 📝 Data Structure Notes

**Epidemiology JSON (data.json):**
```javascript
{
  regions: {
    china: {
      name: "China",
      flag: "🇨🇳",
      population: 1412000000,
      "2024": {
        annualStrokes: { value: 3300000 },
        strokeDeaths: { value: 1500000 },
        prevalence: { value: 17800000 },
        treatmentAccess: { ivTpa: 25, mt: 8 }
      },
      "2030": {
        projectedStrokes: { value: 4200000 }
      }
    }
  }
}
```

**Revenue JSON (revenue-data.json):**
```javascript
{
  companies: [
    {
      name: "Stryker",
      ticker: "SYK",
      headquarters: "USA",
      market_cap: 85000000000,
      annual_revenue: 20500000000,
      neurovascular_revenue: 1450000000,
      neurovascular_growth: 9.1
    }
  ]
}
```

---

## 🐛 Known Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Loading spinner forever | CORS on file:// | Use web server or GitHub |
| Map not interactive | iframe sandbox | `allowfullscreen` attribute |
| Data shows "--" | JSON parse error | Check console for CORS errors |
| Heatmap 404 | File path wrong | Verify `src="global-heatmap-v3b.html"` |

---

## 🔄 Version History

| Version | Date | Changes | Commit |
|---------|------|---------|--------|
| 1.0 | 2026-03-XX | Static HTML with embedded data | - |
| 2.0 | 2026-03-25 | Dynamic JSON loading + GitHub fallback + embedded heatmap | `b13d9c4` |

---

## 📚 References

- CryptoVue data-loader pattern: `~/.openclaw/workspace/crypto-dashboard/data-loader.js`
- NeuroVue Architecture: `~/.openclaw/workspace/docs/vueroo-portal-architecture.md`

---

## 📝 CHEATSHEET Update Log

| Date | Version | Change | Commit |
|------|---------|--------|--------|
| 2026-03-25 | 1.0 | Initial cheatsheet created | - |
| 2026-03-25 | 1.1 | Added Vercel deployment details + live URL | `2e62f07` |

---

*Last Updated: 2026-03-25 14:58 UTC by Lumina*
*Dashboard Live: https://www.vueroo.com/medtech/*
