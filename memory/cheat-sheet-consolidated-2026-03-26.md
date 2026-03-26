# CONSOLIDATED CHEAT SHEET — 2026-03-26

## SYSTEM STATUS: ✅ OPERATIONAL

### Live Dashboards (4 Silos)

| Silo | URL | Status | Data Age |
|------|-----|--------|----------|
| **CryptoVue** | /dashboard/cryptovue | ✅ LIVE | Every 4h |
| **NeuroVue** | /dashboard/neurovue | ✅ LIVE | Manual |
| **StockVue** | /stock/ | ✅ LIVE | Every 4h |
| **CycleVue** | /dashboard/cyclevue | ✅ LIVE | Static (1924-2124) |

---

## COMMON ISSUES & FIXES

### Dashboard Shows "--" or No Data
**Cause:** GitHub cache (5 min) or JSON not yet pushed  
**Fix:** 
1. Check `rooquest1` repo has latest data
2. Wait 5 minutes for cache
3. Hard refresh (Ctrl+F5)

### 404 Errors on New Pages
**Cause:** Next.js routing vs static files  
**Fix:** Use `/dashboard/silo` not `/silo/` for new pages

### API Rate Limits Hit
**Crypto:** CoinGecko free = 30 calls/min (we use far less)  
**Stocks:** Alpha Vantage = 25 calls/day (we use 24)  
**Fix:** Reduce symbols if limits hit

### Vercel Deployment Fails
**Check:** Git status should be clean  
**Trigger:** Push empty commit if needed

---

## ARCHITECTURE PATTERNS

### Data Flow
```
Local Scan → JSON → GitHub → Vercel → Dashboard
```

### File Structure
```
rooquest1/          (data repo)
  data/
    crypto/
    stocks/
    polymarket/
    
vueroo-portal/      (dashboard repo)
  app/
    dashboard/
      cryptovue/
      neurovue/
      cyclevue/
  public/
    crypto/
    stock/
    cyclevue/
```

### Critical Rule
**NEVER use local paths in dashboard code**  
**ALWAYS use GitHub raw URLs for data**

---

## REPOSITORY STATES

| Repo | Commit | Last Push |
|------|--------|-----------|
| rooquest1 | 628e61d | 2026-03-26 17:16 |
| vueroo-portal | 94910c6 | 2026-03-26 17:07 |

---

## NEXT TASK READY

**Status:** ✅ System backed up  
**Memory:** ✅ Consolidated  
**Cheat Sheets:** ✅ Combined into this file  

**Ready for:** Next autonomous build

---

*Consolidated: 2026-03-26 17:16 UTC*
