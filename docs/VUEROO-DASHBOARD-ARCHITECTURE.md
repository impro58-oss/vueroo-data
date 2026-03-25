# VUEROO.COM Dashboard Architecture Documentation
## Last Updated: 2026-03-25

---

## 📁 DIRECTORY STRUCTURE

### Root Level Dashboards (GitHub Pages Source)
```
~/.openclaw/workspace/
├── crypto-dashboard/           # CryptoVue - Bitcoin/cryptocurrency intelligence
│   ├── index.html             # Main dashboard (DEPLOYED to vueroo.com/crypto)
│   ├── data-loader.js         # Dynamic data fetching logic
│   └── process-crypto-data.js # Data processing utilities
│
├── medtech-intelligence/       # NeuroVue - Medical device intelligence
│   └── dashboard/
│       ├── index.html         # Main dashboard (DEPLOYED to vueroo.com/medtech)
│       ├── data-loader.js     # Dynamic data fetching logic
│       └── data/              # JSON data files
│           ├── data.json                 # Epidemiology data
│           ├── revenue-data.json         # Company financials
│           └── product-portfolio-data.json # Product portfolio
│
└── vueroo/                     # DEPLOYMENT FOLDER (GitHub Pages serves from here)
    ├── crypto-dashboard/        # COPIED FROM crypto-dashboard/
    ├── medtech-intelligence/  # COPIED FROM medtech-intelligence/
    └── huggingface-dashboard/ # Additional integrations
```

### Source Data Locations
```
~/.openclaw/workspace/
├── data/
│   └── crypto/
│       ├── crypto_latest.json          # ALWAYS has latest scan (March 25, 08:00)
│       ├── crypto_history.json         # Historical aggregated data
│       └── huggingface_data.json       # ML model outputs
│
└── skills/tradingview-claw-v2/         # Raw scan outputs
    └── top_50_analysis_YYYYMMDD_HHMMSS.json  # Individual scan files
```

---

## 🔄 DATA FLOW ARCHITECTURE

### CryptoVue Data Flow
```
1. TradingView Scanner runs (every 4 hours via cron)
   ↓
2. Saves to: skills/tradingview-claw-v2/top_50_analysis_YYYYMMDD_HHMMSS.json
   ↓
3. Also updates: data/crypto/crypto_latest.json (always latest)
   ↓
4. GitHub push triggers GitHub Pages rebuild
   ↓
5. Browser loads vueroo.com/crypto/index.html
   ↓
6. data-loader.js fetches: raw.githubusercontent.com/.../crypto_latest.json
   ↓
7. Dashboard renders live data
```

### NeuroVue Data Flow
```
1. Data extracted from PDFs/Excel files
   ↓
2. Saved to: medtech-intelligence/dashboard/data/*.json
   ↓
3. GitHub push → GitHub Pages
   ↓
4. Browser loads vueroo.com/medtech/
   ↓
5. data-loader.js fetches JSON from GitHub raw
   ↓
6. Dashboard renders
```

---

## 🔧 KEY FILES REFERENCE

### CryptoVue (vueroo.com/crypto)

| File | Purpose | Location |
|------|---------|----------|
| **index.html** | Main dashboard UI | crypto-dashboard/index.html → vueroo/crypto-dashboard/index.html |
| **data-loader.js** | Fetches crypto_latest.json from GitHub | Both locations synced |
| **crypto_latest.json** | ALWAYS latest scan data | data/crypto/crypto_latest.json |

### NeuroVue (vueroo.com/medtech)

| File | Purpose | Location |
|------|---------|----------|
| **index.html** | Main dashboard UI | medtech-intelligence/dashboard/index.html → vueroo/medtech-intelligence/dashboard/index.html |
| **data-loader.js** | Fetches epidemiology/revenue/portfolio data | medtech-intelligence/dashboard/data-loader.js |
| **data.json** | Epidemiology data | medtech-intelligence/dashboard/data/data.json |
| **revenue-data.json** | Company financials | medtech-intelligence/dashboard/data/revenue-data.json |

---

## 🚨 COMMON ISSUES & FIXES

### Issue: Dashboard Shows Stale Data (Old Date)

**Symptoms:** "Last Scan: March 19, 2026" instead of current date

**Root Causes:**
1. `index.html` has hardcoded embedded data (not using data-loader.js)
2. `data-loader.js` can't find the latest scan file
3. GitHub Pages cache delay

**Fix Steps:**
```bash
# 1. Verify crypto_latest.json exists and is current
cat data/crypto/crypto_latest.json | jq '.scan_timestamp'

# 2. Check data-loader.js loads crypto_latest.json
# Should contain: https://raw.githubusercontent.com/impro58-oss/rooquest1/master/data/crypto/crypto_latest.json

# 3. Rebuild index.html to use data-loader.js
# - Remove embedded 'const coins = [...]' data
# - Add: <script src="data-loader.js"></script>
# - Initialize with: await CryptoDataLoader.loadLatestScan()

# 4. Sync to vueroo/ folder
cp crypto-dashboard/index.html vueroo/crypto-dashboard/index.html
cp crypto-dashboard/data-loader.js vueroo/crypto-dashboard/data-loader.js

# 5. Commit and push
git add -A
git commit -m "fix: Update to latest data"
git push origin master

# 6. Wait 2-3 minutes for GitHub Pages, then hard refresh browser
```

### Issue: Data Not Loading (Blank Dashboard)

**Check:**
1. Open browser DevTools (F12)
2. Check Console for CORS errors
3. Check Network tab for failed requests

**Common Fix:**
```javascript
// In data-loader.js, ensure GitHub raw URL is correct:
const GITHUB_RAW_URL = 'https://raw.githubusercontent.com/impro58-oss/rooquest1/master/';

// For crypto:
const latestJsonUrl = GITHUB_RAW_URL + 'data/crypto/crypto_latest.json';

// For medtech:
const dataUrl = GITHUB_RAW_URL + 'medtech-intelligence/dashboard/data/data.json';
```

---

## 📊 DATA FORMATS

### Crypto Scan Data Format (crypto_latest.json)
```json
{
  "scan_timestamp": "2026-03-25T08:00:31.059939",
  "scan_date": "2026-03-25",
  "total_symbols": 48,
  "signals_found": 1,
  "results": [
    {
      "symbol": "BTCUSDT",
      "price": 70938.13,
      "signal": "hold",
      "confidence": 0.0,
      "csrsi_state": "neutral",
      "rtom_bias": "bullish",
      "compression": true
    }
  ]
}
```

### MedTech Epidemiology Format (data.json)
```json
{
  "metadata": {
    "version": "2.0",
    "lastUpdated": "2026-03-20"
  },
  "global": {
    "2024": {
      "annualStrokes": {"value": 12200000, "unit": "cases/year"}
    }
  },
  "regions": {
    "united_states": {
      "name": "United States",
      "flag": "🇺🇸",
      "2024": {
        "annualStrokes": {"value": 795000}
      }
    }
  }
}
```

---

## 🚀 QUICK REFERENCE COMMANDS

### Update CryptoVue with Latest Data
```powershell
cd C:\Users\impro\.openclaw\workspace

# 1. Ensure crypto_latest.json exists
test data/crypto/crypto_latest.json

# 2. Copy to deployment folder
cp data/crypto/crypto_latest.json vueroo/crypto-dashboard/

# 3. Commit and push
git add data/crypto/crypto_latest.json vueroo/crypto-dashboard/
git commit -m "data: Update crypto scan to $(date +%Y-%m-%d)"
git push origin master
```

### Force Refresh GitHub Pages
```powershell
# Make any small change to trigger rebuild
echo "# $(date)" >> vueroo/README.md
git add vueroo/README.md
git commit -m "chore: Trigger GitHub Pages rebuild"
git push
```

### Check GitHub Pages Status
```powershell
# View commit log for gh-pages branch
git log origin/gh-pages --oneline -5

# Check if latest commit is deployed
curl -s https://api.github.com/repos/impro58-oss/rooquest1/pages | jq '.html_url, .source.branch'
```

---

## 📝 DEPLOYMENT CHECKLIST

When making changes:

- [ ] Edit source file in `crypto-dashboard/` or `medtech-intelligence/`
- [ ] Copy changes to `vueroo/` folder
- [ ] Test locally (open HTML file in browser)
- [ ] Check browser console for errors
- [ ] Commit with descriptive message
- [ ] Push to origin master
- [ ] Wait 2-3 minutes for GitHub Pages
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Verify date/time in bottom-left corner

---

## 🔗 IMPORTANT URLS

| Resource | URL |
|----------|-----|
| **Live CryptoVue** | https://www.vueroo.com/crypto/index.html |
| **Live NeuroVue** | https://www.vueroo.com/medtech-intelligence/dashboard/index.html |
| **GitHub Repo** | https://github.com/impro58-oss/rooquest1 |
| **Raw Data** | https://raw.githubusercontent.com/impro58-oss/rooquest1/master/data/crypto/crypto_latest.json |
| **GitHub Pages Settings** | https://github.com/impro58-oss/rooquest1/settings/pages |

---

## 📞 TROUBLESHOOTING CONTACT

If dashboards break:
1. Check this documentation first
2. Verify GitHub Pages is building (no errors in Actions)
3. Check browser console for specific errors
4. Compare working backup files (index-static-backup.html)
5. Revert to last known good commit if needed

---

*Documentation created: 2026-03-25*
*Last crypto scan: March 25, 2026 08:00 UTC*
*GitHub commit: 6859c4e*