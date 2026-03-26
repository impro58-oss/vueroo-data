# STOCKVUE CHEAT SHEET — 2026-03-26

## 🚀 NEW SILO: STOCKVUE — LIVE

### Quick Links
- **Dashboard:** https://vueroo-portal.vercel.app/stock/
- **Main Portal:** https://vueroo-portal.vercel.app/dashboard (StockVue button added)
- **Data Repo:** https://github.com/impro58-oss/rooquest1/tree/master/data/stocks

### What It Does
- Tracks 12 US stocks via Alpha Vantage API
- Runs every 4 hours (08:00, 12:00, 16:00 UTC)
- Generates LONG/SHORT/HOLD signals based on momentum
- Displays heat map, category filters, volume data

### Symbols Tracked
1. NVDA — AI/GPU leader
2. TSLA — EV/Energy
3. AAPL — Consumer tech
4. AMD — Semiconductor
5. MSFT — Cloud/AI
6. GOOGL — Search/AI
7. AMZN — E-commerce/Cloud
8. META — Social/VR
9. JPM — Banking
10. V — Payments
11. COIN — Crypto proxy
12. PLTR — AI/Data

### Data Files (Local + GitHub)
```
data/stocks/
├── stocks_latest.json          ← Current scan (pushed to GitHub)
├── stocks_history.json         ← All scans accumulated
├── AMD_daily.csv               ← Raw price data per symbol
├── NVDA_daily.csv
└── scan_summary.txt            ← Human-readable summary
```

### How to Check Status
```powershell
cd ~/.openclaw/workspace/skills/stockvue-scraper
python alpha_vantage_scraper.py  # Manual run
```

### How to Force Refresh Dashboard
1. Wait 5 min after scan (GitHub cache)
2. Or add `?t=12345` to URL for cache-bust

### API Limits
- **Free Tier:** 25 calls/day
- **Usage:** 24 calls/day (12 symbols × 2: price + RSI)
- **Spare:** 1 call for testing

### Troubleshooting
| Issue | Fix |
|-------|-----|
| Dashboard shows "--" | Check GitHub has latest JSON, wait 5 min |
| "Failed to load data" | API rate limit hit, wait for next hour |
| Missing symbol data | Check `*_daily.csv` files exist |

---

## ✅ TODAY'S DEPLOYMENT SUMMARY (2026-03-26)

### StockVue — NEW
- ✅ Alpha Vantage scraper built
- ✅ 12 symbols configured
- ✅ Scheduled task running every 4h
- ✅ GitHub auto-commit working
- ✅ Dashboard deployed to Vercel
- ✅ Button added to main dashboard

### CryptoVue — EXPANDED
- ✅ Now tracking 194 coins (was 50)
- ✅ GitHub-first loading fixed
- ✅ Fallback filenames updated

### NeuroVue — POLISHED
- ✅ Product Coverage chart scale 8→12
- ✅ Bars no longer maxing out

### Infrastructure — SYNCHRONIZED
- ✅ All repos pushed to GitHub
- ✅ Vercel auto-deploy active
- ✅ Memory files updated
- ✅ TOOLS.md documented

---

## 📊 LIVE DASHBOARDS STATUS

| Dashboard | URL | Status | Last Update |
|-----------|-----|--------|-------------|
| CryptoVue | /crypto/ | ✅ LIVE | Every 4h |
| StockVue | /stock/ | ✅ LIVE | Every 4h |
| NeuroVue | /medtech/ | ✅ LIVE | Manual |

All synced. All deployed. Ready for next project.

---

*Generated: 2026-03-26 12:45 UTC*
