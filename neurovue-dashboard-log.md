# NeuroVue Dashboard - Developer Log & Troubleshooting Guide

**Project:** NeuroVue Intelligence - Neurovascular Market Intelligence Platform  
**URL:** https://www.vueroo.com/medtech  
**Created:** March 25, 2026  
**Last Updated:** March 25, 2026

---

## 📁 Project Structure

```
vueroo-portal/
└── public/medtech/
    ├── index.html                    # Main NeuroVue dashboard
    ├── global-heatmap-v3b.html       # Geographic stroke visualization
    ├── competitive-intelligence.html # Standalone CI analysis
    ├── competition-optic.html        # Competition analysis
    ├── platform-analysis.html      # Platform metrics
    ├── platform-naming.html          # Product naming strategy
    ├── due-diligence-template.html   # Due diligence framework
    └── data/                       # ❌ NO LONGER USED - all data from GitHub

rooquest1/                         # Data repository (GitHub)
└── medtech-intelligence/
    └── dashboard/
        └── data/
            ├── data.json             # Epidemiology data
            ├── revenue-historical.json   # Company revenue
            ├── competitor-intelligence.json  # CI data
            └── portfolio-matrix.json       # Portfolio coverage
```

---

## 🏗️ Architecture Principles

### Single Source of Truth
**CRITICAL:** All JSON data loads from `rooquest1` GitHub repo ONLY.

```javascript
const DATA_BASE = 'https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data';
```

**NEVER:**
- ❌ Embed static data in HTML
- ❌ Store JSON files in vueroo-portal repo
- ❌ Use relative paths (`./data/file.json`)
- ❌ Assume data exists without null checks

**ALWAYS:**
- ✅ Fetch from GitHub raw URLs
- ✅ Use absolute paths (`/medtech/page.html`)
- ✅ Validate data before accessing properties
- ✅ Handle individual fetch failures gracefully

---

## 🐛 Error Log & Fixes

### Error #1: "Cannot set properties of null (setting 'innerHTML')"
**Symptoms:** Page crashes, blank screen, console shows null error
**Cause:** JavaScript trying to access DOM elements that don't exist
**Fix:**
```javascript
// WRONG - direct access
element.innerHTML = content;

// RIGHT - null check
var element = document.getElementById('id');
if (element) element.innerHTML = content;
```

### Error #2: "Failed to load data: Revenue data not found" (404)
**Symptoms:** Loading spinner forever, "Failed to Load Data" message
**Cause:** JSON file missing or wrong path
**Fix:**
1. Check file exists in `rooquest1/medtech-intelligence/dashboard/data/`
2. Use GitHub raw URL, not local path
3. Add cache-busting: `?t=` + Date.now()
4. Verify GitHub repo is public

### Error #3: Portfolio Matrix shows no data
**Symptoms:** Empty table, no coverage chart
**Cause:** JSON structure mismatch between data and code
**Fix:**
```javascript
// Check actual JSON structure
// GitHub format: { products: [...], strength: "high" }
// Old format: [...] (just array)

// RIGHT - access nested structure
if (companyData && companyData.products && companyData.products.length > 0)
```

### Error #4: Research Hub links 404
**Symptoms:** Clicking cards shows 404 error
**Cause:** Relative paths break in production
**Fix:**
```html
<!-- WRONG - relative -->
<a href="page.html">

<!-- RIGHT - absolute -->
<a href="/medtech/page.html">
```

### Error #5: "Uncaught SyntaxError: Invalid or unexpected token"
**Symptoms:** Page completely blank, nothing loads
**Cause:** JavaScript syntax error (misplaced quote, missing bracket)
**Fix:**
```javascript
// WRONG - misplaced quote
html += '<tr class="...' + rowClass + '"'>';

// RIGHT
html += '<tr class="...' + rowClass + '">';
```

### Error #6: Charts not rendering (Chart.js)
**Symptoms:** Canvas elements empty
**Cause:** Canvas context not found or Chart.js not loaded
**Fix:**
```javascript
var ctx = document.getElementById('chartId');
if (!ctx) return;  // Exit if canvas doesn't exist

// Destroy existing chart before creating new one
if (existingChart) existingChart.destroy();

// Then create new chart
new Chart(ctx, { ... });
```

### Error #7: Data loads but sections don't update
**Symptoms:** Dashboard shows "--" for all metrics
**Cause:** `renderDashboard()` called before data loads
**Fix:**
```javascript
// Load data FIRST, then render
NeuroVueDataLoader.loadNeuroVueData().then(function(data) {
    appData = data;
    renderDashboard();  // Call AFTER data loads
    document.getElementById('loading-overlay').style.display = 'none';
});
```

---

## 🔧 Troubleshooting Checklist

### When Page Won't Load:
1. [ ] Check browser console (F12) for errors
2. [ ] Verify all 4 JSON files load in Network tab
3. [ ] Check GitHub raw URLs are accessible (not 404)
4. [ ] Hard refresh (Ctrl+Shift+R) to clear cache
5. [ ] Check for JavaScript syntax errors

### When Data Doesn't Display:
1. [ ] Verify JSON structure matches expected format
2. [ ] Check `appData` is populated: `console.log(appData)`
3. [ ] Check data path: `appData.revenue.companies`
4. [ ] Ensure null checks before accessing nested properties
5. [ ] Verify DOM elements exist before updating

### When Links Don't Work:
1. [ ] Use absolute paths: `/medtech/page.html`
2. [ ] Verify file exists in GitHub repo
3. [ ] Check file was committed and pushed
4. [ ] Wait for Vercel deployment (30-60 seconds)

---

## 🚀 Quick Commands

### Deploy to Production:
```bash
cd ~/.openclaw/workspace/vueroo-portal
git add public/medtech/
git commit -m "Description of changes"
git push
```

### Check GitHub Data Files:
```bash
# Epidemiology
curl https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/data.json

# Revenue
curl https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/revenue-historical.json

# Portfolio Matrix
curl https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/portfolio-matrix.json

# Competitors
curl https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/competitor-intelligence.json
```

### Verify Page Loads:
```bash
# Main dashboard
curl -I https://www.vueroo.com/medtech/index.html

# Global heatmap
curl -I https://www.vueroo.com/medtech/global-heatmap-v3b.html
```

---

## 📊 Data Structure Reference

### Epidemiology (data.json)
```javascript
{
  "global": {
    "2024": {
      "annualStrokes": { "value": 12200000, ... },
      "strokeDeaths": { "value": 6500000, ... }
    }
  },
  "regions": {
    "asia": {
      "name": "Asia Pacific",
      "2024": { ... }
    }
  }
}
```

### Revenue (revenue-historical.json)
```javascript
{
  "companies": [
    {
      "id": "stryker",
      "name": "Stryker",
      "neurovascularRevenue": 1450000000,
      "historicalRevenue": { "2024": 1450, ... },
      "projectedRevenue": { "2030": 2450, ... }
    }
  ]
}
```

### Portfolio Matrix (portfolio-matrix.json)
```javascript
{
  "categories": [
    {
      "id": "coils",
      "name": "Coils",
      "medtronic": { "products": [...], "strength": "high" },
      "stryker": { "products": [...], "strength": "high" },
      // ... all 10 companies
    }
  ]
}
```

### Competitors (competitor-intelligence.json)
```javascript
{
  "companies": [
    {
      "id": "stryker",
      "name": "Stryker",
      "threatLevel": "high",
      "strengths": [...],
      "weaknesses": [...]
    }
  ]
}
```

---

## 🔗 Navigation Pattern

### Linking from Standalone Pages to Dashboard Sections:

```javascript
// From global-heatmap.html:
<a href="/medtech/index.html" 
   onclick="sessionStorage.setItem('navigateToRevenue', 'true');">
   Go to Revenue
</a>

// In index.html initialization:
document.addEventListener('DOMContentLoaded', function() {
    // Check for navigation request
    if (sessionStorage.getItem('navigateToRevenue') === 'true') {
        sessionStorage.removeItem('navigateToRevenue');
        showSection('revenue');
    }
    
    // Then load data
    NeuroVueDataLoader.loadNeuroVueData()...
});
```

---

## 🎨 Style Guide

### Colors:
- Primary: `#3B82F6` (blue-500)
- Success: `#10B981` (emerald-500)
- Warning: `#F59E0B` (amber-500)
- Danger: `#EF4444` (red-500)
- Background: `#0f172a` (slate-900)
- Card: `#1e293b` (slate-800)

### Icons (Font Awesome):
- Navigation: `fa-globe`, `fa-chart-pie`, `fa-chess`
- Companies: `fa-building`, `fa-hospital`
- Actions: `fa-arrow-right`, `fa-download`, `fa-sync`
- Status: `fa-check-circle`, `fa-minus`, `fa-exclamation-triangle`

---

## 📝 Commit Message Format

```
Fix [component] - [brief description]

Changes:
- [Specific change 1]
- [Specific change 2]

Fixes: [error description or issue]
```

Examples:
```
Fix Portfolio Matrix - update HTML headers to match GitHub JSON structure

Changes:
- Updated table headers from 6 to 10 companies
- Fixed getCoverageCounts() to check products array
- Updated colspan values for empty states

Fixes: Matrix showing no data, coverage chart empty
```

---

## 🔄 Rebuild from Scratch

### If Starting Over:

1. **Create GitHub Repos:**
   - `vueroo-portal` (private) - HTML/JS/CSS
   - `rooquest1` (public) - JSON data files

2. **Deploy Vercel:**
   - Connect `vueroo-portal` repo
   - Set output directory to `public/`
   - Enable auto-deploy on push

3. **Upload Data:**
   - Create `medtech-intelligence/dashboard/data/`
   - Add 4 JSON files (epidemiology, revenue, competitors, portfolio)
   - Verify raw URLs work

4. **Build Dashboard:**
   - Copy `index.html` structure
   - Implement `NeuroVueDataLoader`
   - Create section containers
   - Add render functions

5. **Test:**
   - Verify all 4 JSON files load
   - Check each section renders
   - Test navigation between sections
   - Verify charts display

6. **Add Standalone Pages:**
   - Create `global-heatmap-v3b.html`
   - Add navigation links back to dashboard
   - Deploy and test links

---

## 📚 External Resources

- **Tailwind CSS:** https://tailwindcss.com/docs
- **Chart.js:** https://www.chartjs.org/docs/
- **Font Awesome:** https://fontawesome.com/icons
- **Vercel Docs:** https://vercel.com/docs
- **GitHub Raw URLs:** https://raw.githubusercontent.com/

---

## ⚡ Performance Tips

1. **Cache Busting:** Always add `?t=` + Date.now() to fetch URLs
2. **Lazy Loading:** Load charts only when section is visible
3. **Debouncing:** Debounce filter inputs (300ms)
4. **Chart Destruction:** Always destroy old charts before creating new ones
5. **CDN Resources:** Use jsDelivr for Chart.js, Tailwind CDN for dev

---

## 🔐 Security Notes

- Never expose API keys in client-side code
- Keep `rooquest1` public for raw URL access
- Keep `vueroo-portal` private
- Don't commit sensitive data to either repo
- Use environment variables for any secrets (server-side only)

---

## 🆘 Emergency Contacts

If completely stuck:
1. Check this README first
2. Review `memory/2026-03-25.md` for session context
3. Check `MEMORY.md` for architecture decisions
4. Review git commit history: `git log --oneline -20`

---

**Remember:** The key to this system is GitHub-hosted JSON + client-side rendering. No backend needed, no database to manage. Just HTML, JavaScript, and well-structured data files.

*Last commit: d4995d6*  
*Files: index.html, global-heatmap-v3b.html, 4 JSON data files*  
*Status: LIVE and working* 🚀
