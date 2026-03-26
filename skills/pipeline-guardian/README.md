# Pipeline Guardian — Data Pipeline Monitor

**Version:** 1.0  
**Purpose:** Automated monitoring for all Vueroo data silos  
**Created:** 2026-03-26

---

## Overview

Pipeline Guardian is a continuous monitoring system that:
- Checks data freshness every hour
- Validates JSON schemas haven't drifted
- Alerts when data goes stale (>6h old)
- Auto-documents changes and issues
- Sends status reports to designated channels

## Monitored Silos

| Silo | Data URL | Freshness Threshold | Last Check |
|------|----------|---------------------|------------|
| CryptoVue | `crypto/crypto_latest.json` | 6 hours | -- |
| StockVue | `stocks/stocks_latest.json` | 6 hours | -- |
| NeuroVue | `medtech-intelligence/*` | 24 hours | -- |
| CycleVue | `cyclevue/cycle-data.json` | 24 hours | -- |

## Checks Performed

1. **Freshness Check** — Is `scan_timestamp` within threshold?
2. **Schema Validation** — Does JSON match expected structure?
3. **Completeness Check** — Are required fields present and non-null?
4. **GitHub Sync** — Is local data synced with remote?

## Alert Triggers

- Data stale >6h (warning)
- Schema mismatch (critical)
- Failed fetch (critical)
- Missing required fields (error)

## Output

- `logs/guardian/YYYY-MM-DD.log` — Daily logs
- `alerts/pending/` — Unresolved issues
- Status dashboard at `/admin/pipeline-status`

---

## Quick Commands

```bash
# Run manual check
python guardian.py --check-all

# Validate specific silo
python guardian.py --silo cryptovue

# Generate status report
python guardian.py --report
```

---

*Part of the Vueroo Intelligence Platform*
