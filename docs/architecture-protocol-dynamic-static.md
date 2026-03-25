# Architecture Protocol - Dynamic vs Static
**Version:** 1.0  
**Created:** 2026-03-24  
**Authority:** Non-negotiable

---

## 🚨 THE RULE

| If the system has... | Then the frontend must be... | Never... |
|---------------------|------------------------------|----------|
| Database | Dynamic | Static fallback without explicit TEST marker |
| JSON API | Dynamic | Hardcoded data |
| Auto-updating scans | Dynamic | Manual copy-paste |
| Live data pipeline | Dynamic | Snapshot pretending to be live |

**If you see JSON files, database connections, or scheduled data pipelines → DYNAMIC ONLY**

---

## ✅ DYNAMIC DATA PATTERN (Required)

```javascript
// RIGHT: Fetch from source of truth
async function loadData() {
    const data = await fetch('/api/latest-scan'); // or GitHub, or local JSON
    render(data);
}
```

```javascript
// WRONG: Embedded static data
const data = [
    {symbol: "BTC", price: 69931.01, ...}, // Hardcoded = LIE
    {symbol: "ETH", price: 2165.67, ...}
];
```

---

## 🏷️ TEST DATA MARKER (Required if Static)

If static data is absolutely necessary (prototyping, demo, offline fallback):

```html
<!-- REQUIRED BANNER -->
<div style="background: #EF4444; color: white; padding: 12px; text-align: center; font-weight: bold;"
     ⚠️ TEST DATA — NOT LIVE — Last updated: March 19, 2026
</div>
```

**Rules:**
- Red background mandatory
- "TEST DATA" in caps
- Date stamp required
- Cannot be hidden in comments
- Must be visible above fold

---

## 🔍 DETECTION CHECKLIST

Before delivering any dashboard/report/UI:

- [ ] Search file for hardcoded arrays (`const data = [`)
- [ ] Check if fetch/axios/API calls exist
- [ ] Verify `data-loader.js` or equivalent is imported
- [ ] Confirm no "sample" or "dummy" data in production code
- [ ] Look for `JSON.parse` or `response.json()` calls
- [ ] Check if last-updated timestamp is dynamic

**If ANY static data found without TEST marker → REJECT delivery**

---

## 💥 ARCHITECTURE SMELLS

These indicate wrong architecture:

| Smell | Meaning | Fix |
|-------|---------|-----|
| "Last Updated: March 19" when it's March 24 | Static data pretending to be live | Wire to actual data source |
| `const coins = [...]` in HTML | Hardcoded snapshot | Move to fetch + render |
| Loading "instantly" with no spinner | Pre-baked data | Add async loading states |
| Sidebar shows dates without API call | Static fallback | Dynamic discovery |

---

## 🛠️ CORRECT PATTERN: CryptoVue

**Data Layer:**
- Python script runs every 4 hours
- Outputs: `top_50_analysis_YYYYMMDD_HHMMSS.json`
- Latest scan auto-discovered by `data-loader.js`

**Frontend:**
```html
<script src="data-loader.js"></script>
<script>
    async function init() {
        showLoadingState();
        const data = await CryptoDataLoader.loadLatestScan();
        render(data);
        showLiveIndicator();
    }
</script>
```

**States:**
1. Loading (skeleton screens)
2. Live data (green indicator, timestamp)
3. Error (retry button, fallback message)

**Never:** Static embedded array

---

## 📋 INCIDENT LOG

**2026-03-24: Static CryptoVue Shipped**
- **Mistake:** `index.html` had hardcoded `const coins = [...]` array
- **Impact:** User saw March 19 data on March 24
- **Root Cause:** I built a "demo" version and forgot to wire the dynamic loader
- **Fix:** Refactored to use `data-loader.js` with async loading
- **Prevention:** This protocol document

---

## ✅ ACCEPTANCE CRITERIA

For any data-driven UI to be considered "done":

1. **Source of truth is external** (API, JSON file, database)
2. **Loading states exist** (not instant fake data)
3. **Timestamp is dynamic** (shows actual last update)
4. **Refresh capability** (manual reload button)
5. **Status indicator** (loading → live → error)
6. **No hardcoded arrays** in production code

**Sign-off required:** Architect confirms dynamic data pipeline is operational.

---

## 🔒 ENFORCEMENT

If building a system with:
- Scheduled jobs (cron, every 4 hours)
- JSON outputs (scans, analysis)
- Database persistence
- API endpoints

**Then:** Dynamic loading is non-optional. Static is a bug, not a feature.

**Test data must scream TEST DATA.**

---

*Protocol created after delivering static dashboard when dynamic was specified.*