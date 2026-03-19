# CryptoVue Intelligence Dashboard

**Real-time crypto market analysis with TrojanLogic4H strategy**

Built with ❤️ using 6+ days of scan data (30+ data points)

---

## 🚀 Quick Start

1. Open `index.html` in your browser:
```
file:///C:/Users/impro/.openclaw/workspace/crypto-dashboard/index.html
```

2. Or view live data:
```
# Process latest scans
node process-crypto-data.js

# Then open index.html
```

---

## 📊 Features

### Market Pulse Dashboard
- **Live Stats**: Long/Short signals, High confidence setups, Compression alerts
- **Top Opportunities**: Highest confidence trades with entry zones
- **Recent Signals**: Latest signal changes from 50 tracked coins

### Heat Map
- Visual grid of all 50 cryptocurrencies
- Color-coded by confidence level
- Filter by: Long/Short/Futures/Compression

### Trend Analysis
- Signal distribution charts
- Confidence trends over time
- Historical analysis

### Trading Opportunities
- Complete list of FUTURES-ready setups
- Entry zones, stop losses, take profits
- Risk management parameters

### Portfolio Tracker
- Core holdings: BTC, ETH, SOL, XRP, DOGE, BNB, LINK
- Signal status for each position
- Compression alerts

### Signal History
- 6 days of historical data
- Per-coin trend analysis
- Signal change detection

---

## 🛠️ Data Pipeline

```
TrojanLogic4H Scanner (every 4h)
    ↓
JSON files in skills/tradingview-claw-v2/
    ↓
process-crypto-data.js (aggregator)
    ↓
crypto-data.json (consolidated)
    ↓
Dashboard visualization
```

### Files

| File | Purpose |
|------|---------|
| `index.html` | Main dashboard |
| `data-loader.js` | Data processing utilities |
| `process-crypto-data.js` | Aggregates all scan files |
| `sample-data.json` | Demo data structure |
| `crypto-data.json` | **Generated** - Latest consolidated data |

---

## 📈 Data Sources

- **Strategy**: CS RSI MTF (13/64) + RtoM Channels (200-day)
- **Scans**: Every 4 hours
- **Coins**: Top 50 by volume
- **History**: 6 days (26 scans)
- **Data Points**: 1,300+ individual readings

---

## 🔄 Backup to GitHub

### Manual backup:
```bash
cd ~/.openclaw/workspace/crypto-dashboard
./backup.sh "Your commit message"
```

### Auto-update data:
```bash
node process-crypto-data.js
```

---

## 🎨 Design System

Same as NeuroVue Intelligence:
- **Background**: slate-950 (#0f172a)
- **Cards**: slate-900 (#1e293b)
- **Borders**: slate-800 (#1e293b)
- **Primary**: blue-500 (#3b82f6)
- **Success**: emerald-500 (#10b981)
- **Warning**: amber-500 (#f59e0b)
- **Danger**: red-500 (#ef4444)

---

## 📊 Metrics

Latest Scan (2026-03-19 12:00):
- Total Coins: 50
- Long Signals: 0
- Short Signals: 6
- Futures Ready: 0
- Compression: 20
- Historical Coins: 89

---

## 🚀 Roadmap

- [ ] Real-time price updates via WebSocket
- [ ] Chart.js integration for trend visualization
- [ ] Email alerts for signal changes
- [ ] Mobile app companion
- [ ] AI-powered pattern recognition

---

**Built by Lumina | Data from TrojanLogic4H | March 2026**
