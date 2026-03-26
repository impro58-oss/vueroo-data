# TradingAgents Integration Plan
## Phase 1: StockVue + Alpha Vantage → Phase 2: Multi-Agent Trading

**Date:** 2026-03-26  
**Status:** Awaiting Alpha Vantage API Key

---

## 🎯 INTEGRATION OVERVIEW

**Goal:** Combine TradingAgents' multi-agent architecture with your existing dashboards

**Architecture:**
```
Alpha Vantage Data
        ↓
StockVue Scanner (FIXED) ─→ TradingAgents Analysis ─→ Your Dashboards
        ↓                        ↓                        ↓
   Price/Vol Data          Multi-agent signals      CryptoVue/NeuroVue
   Technicals             (Bull/Bear debate)       Unified Portal
```

---

## PHASE 1: FIX STOCKVUE (Immediate — You Get API Key)

### Step 1.1: Create Alpha Vantage Scraper
**File:** `skills/stockvue-scraper/alpha_vantage_scraper.py`

```python
# Core functions needed:
- get_daily_prices(symbol)           # Time Series Daily
- get_technical_indicators(symbol)    # RSI, MACD, SMA, etc.
- get_sector_performance()           # Sector performance
- get_market_movers()                # Gainers/Losers (if available)
- scan_all_symbols(symbols_list)     # Batch scanning
```

**API Endpoints:**
| Endpoint | Function | Rate Limit |
|----------|----------|------------|
| `TIME_SERIES_DAILY` | OHLCV data | 25/day free |
| `RSI` / `MACD` | Technicals | 25/day free |
| `SECTOR` | Sector performance | 500/day |

### Step 1.2: Update Signal Generation
Replace Yahoo-based logic with Alpha Vantage:
- Pull real price data
- Calculate CS RSI MTF properly
- Generate actual signals (not empty)

### Step 1.3: Test & Validate
- Run single symbol test (AAPL)
- Compare with manual Yahoo check
- Verify signal accuracy

**Deliverable:** Working StockVue with real data

---

## PHASE 2: TRADINGAGENTS INTEGRATION (Next Week)

### Step 2.1: Install TradingAgents
```bash
cd ~/.openclaw/workspace
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
pip install .
```

### Step 2.2: Create Bridge Script
**File:** `scripts/tradingagents-bridge.py`

**Function:** Connect TradingAgents to your data pipeline

```python
# Pseudo-code:
from tradingagents.graph.trading_graph import TradingAgentsGraph

class TradingAgentsBridge:
    def __init__(self, config):
        self.ta = TradingAgentsGraph(config=config)
    
    def analyze_symbol(self, symbol, date):
        """Run TradingAgents analysis on a symbol"""
        _, decision = self.ta.propagate(symbol, date)
        return decision
    
    def analyze_portfolio(self, symbols):
        """Batch analyze portfolio"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.analyze_symbol(symbol, today)
        return results
```

### Step 2.3: Create Custom Config
**File:** `config/tradingagents-config.yaml`

Customize for your needs:
```yaml
llm_provider: "openai"  # or anthropic, google
deep_think_llm: "gpt-4o"  # for complex reasoning
quick_think_llm: "gpt-4o-mini"  # for quick tasks
max_debate_rounds: 2  # Bull vs Bear debates

# Add your existing signals as context
include_technical_signals: true
signal_weight: 0.3  # Your CS RSI MTF weight
llm_weight: 0.7     # TradingAgents weight

# Risk management
max_position_size: 0.05  # 5% max (your rule)
stop_loss_pct: 0.05      # 5% stop loss
```

### Step 2.4: Integrate with CryptoVue
**New File:** `skills/tradingagents-crypto/crypto_analyzer.py`

Use TradingAgents architecture for crypto:
```
CryptoVue Data → CryptoAnalyst Agents → TradingDecision
     ↓                    ↓                  ↓
  Prices          Bull/Bear debate      Position sizing
  On-chain        Sentiment analysis    Risk check
  News            Technical synthesis   Final signal
```

---

## PHASE 3: UNIFIED DASHBOARD (Week 3-4)

### Step 3.1: Multi-Agent Signal Display
**Update:** CryptoVue + StockVue dashboards

| Symbol | Price | Your Signal | TA Signal | Consensus | Confidence |
|--------|-------|-------------|-----------|-------------|------------|
| AAPL | $180.25 | 🟢 LONG | 🟢 BULLISH | 🟢 STRONG LONG | 82% |
| NVDA | $850.00 | ⚪ HOLD | 🔴 BEARISH | ⚪ NEUTRAL | 45% |
| BTC | $67,500 | 🟢 LONG | 🟢 BULLISH | 🟢 STRONG LONG | 78% |

### Step 3.2: Agent Debate Viewer
**New Feature:** See why TradingAgents made a decision

Display:
- Bullish researcher arguments
- Bearish researcher counter-arguments
- Risk team assessment
- Final PM decision

### Step 3.3: Vueroo Portal Integration
**Location:** `vueroo-portal` (when built)

Add "Intelligence Layer":
```
Tier Access:
├── Basic: Raw signals (your current)
├── Pro: + TradingAgents analysis
├── Enterprise: + Custom agent config
└── API: Direct TradingAgents access
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Alpha Vantage (You do this)
- [ ] Sign up at alphavantage.co
- [ ] Get free API key
- [ ] Send me the key (securely)
- [ ] I'll build the scraper (1 day)

### Phase 2: TradingAgents (I do this)
- [ ] Clone & install TradingAgents
- [ ] Create bridge script
- [ ] Test with 5 symbols
- [ ] Integrate signal weights
- [ ] Update dashboards

### Phase 3: Unification (We do together)
- [ ] Multi-agent signal display
- [ ] Debate viewer
- [ ] Portal integration
- [ ] Documentation

---

## 🔐 API KEY SECURITY

**Where to store:**
1. **Local:** `.env` file (never commit)
2. **GitHub Secrets:** For CI/CD (future)
3. **OpenClaw Config:** `~/.openclaw/.config/alphavantage/api_key`

**Script access:**
```python
import os
from pathlib import Path

def get_alpha_vantage_key():
    # Priority order
    return (
        os.getenv('ALPHA_VANTAGE_API_KEY') or
        Path.home() / '.openclaw/.config/alphavantage/api_key'.read_text().strip() or
        None
    )
```

---

## 💰 COSTS

| Service | Cost | Limit | Notes |
|---------|------|-------|-------|
| Alpha Vantage Free | $0 | 25 calls/day | Enough for daily scans |
| Alpha Vantage Premium | $49/mo | 75 calls/min | Real-time scans |
| OpenAI API | Pay per use | - | TradingAgents reasoning |
| **Total Phase 1** | **$0** | - | Free tier sufficient |
| **Total Phase 2+** | **~$50-100/mo** | - | If you scale |

---

## 🚀 ALTERNATIVE: START EVEN SIMPLER

If TradingAgents feels heavy, we can:

**Option A: Alpha Vantage Only**
- Fix StockVue with Alpha Vantage
- Keep your CS RSI MTF strategy
- Add TradingAgents later

**Option B: Hybrid Approach**
- Use TradingAgents for 5-10 high-conviction symbols
- Keep your scanners for broad market
- Compare performance over 30 days

**Option C: Full Integration**
- Everything in the plan above
- Full multi-agent pipeline
- Most powerful but takes longer

---

## ⏱️ TIMELINE

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 1-2 days | Working StockVue with Alpha Vantage |
| Phase 2 | 3-5 days | TradingAgents integration working |
| Phase 3 | 1-2 weeks | Unified dashboard with multi-agent signals |

**Start:** As soon as you send API key  
**Done:** ~2 weeks

---

## 📞 NEXT STEPS

1. **Sign up:** https://www.alphavantage.co/support/#api-key
2. **Get key:** Free tier, instant activation
3. **Send key:** Securely (I'll tell you how)
4. **I'll build:** Alpha Vantage scraper first
5. **We test:** Verify data quality
6. **Then:** TradingAgents integration

---

**Ready when you are!** 🚀

Once you have the API key, I can have StockVue pulling real data within hours.
