"""
Cross-Silo Intelligence Engine
Finds correlations and generates signals across Vueroo data silos.
"""

import json
import os
import sys
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Configuration
BASE_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace")
DATA_DIR = BASE_DIR / "data"
GITHUB_RAW = "https://raw.githubusercontent.com/impro58-oss/rooquest1/master/data"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger('CrossSiloEngine')


class SignalStrength(Enum):
    NONE = 0
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class SiloData:
    name: str
    timestamp: datetime
    metrics: Dict[str, Any]
    signals: List[str]
    sentiment: str  # 'bullish', 'bearish', 'neutral'


@dataclass
class CrossSiloSignal:
    id: str
    timestamp: str
    strength: SignalStrength
    direction: str  # 'risk_on', 'risk_off', 'rotation'
    headline: str
    description: str
    contributing_silos: List[str]
    confidence: float
    recommended_action: str


class CrossSiloEngine:
    """Analyzes correlations across all silos."""
    
    def __init__(self):
        self.silo_data: Dict[str, SiloData] = {}
        self.historical_signals: List[CrossSiloSignal] = []
        
    def load_crypto_data(self) -> Optional[SiloData]:
        """Load and parse CryptoVue data."""
        try:
            url = f"{GITHUB_RAW}/crypto/crypto_latest.json"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            # Parse metrics
            results = data.get('results', [])
            long_count = sum(1 for r in results if r.get('signal') == 'long')
            short_count = sum(1 for r in results if r.get('signal') == 'short')
            total = len(results)
            
            # Determine sentiment
            if long_count > short_count * 2:
                sentiment = 'bullish'
            elif short_count > long_count * 2:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            # Get top signals
            signals = []
            for r in sorted(results, key=lambda x: x.get('confidence', 0), reverse=True)[:3]:
                if r.get('signal') in ['long', 'short']:
                    signals.append(f"{r['symbol']} ({r['signal'].upper()}, conf: {r.get('confidence', 0):.2f})")
            
            return SiloData(
                name='CryptoVue',
                timestamp=datetime.fromisoformat(data.get('scan_timestamp', '').replace('Z', '+00:00')),
                metrics={
                    'total_assets': total,
                    'long_signals': long_count,
                    'short_signals': short_count,
                    'signal_ratio': long_count / max(short_count, 1),
                    'avg_confidence': sum(r.get('confidence', 0) for r in results) / max(len(results), 1)
                },
                signals=signals,
                sentiment=sentiment
            )
        except Exception as e:
            logger.error(f"Failed to load CryptoVue data: {e}")
            return None
    
    def load_stock_data(self) -> Optional[SiloData]:
        """Load and parse StockVue data."""
        try:
            url = f"{GITHUB_RAW}/stocks/stocks_latest.json"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            results = data.get('results', [])
            long_count = sum(1 for r in results if r.get('signal') == 'long')
            short_count = sum(1 for r in results if r.get('signal') == 'short')
            
            # Tech momentum check
            tech_symbols = ['NVDA', 'AMD', 'PLTR', 'MSFT']
            tech_bullish = sum(1 for r in results if r.get('symbol') in tech_symbols and r.get('signal') == 'long')
            tech_bearish = sum(1 for r in results if r.get('symbol') in tech_symbols and r.get('signal') == 'short')
            
            if tech_bullish > tech_bearish * 2:
                sentiment = 'bullish'
            elif tech_bearish > tech_bullish * 2:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            signals = []
            for r in sorted(results, key=lambda x: abs(x.get('change_percent', 0)), reverse=True)[:3]:
                signals.append(f"{r['symbol']} ({r.get('change_percent', 0):+.1f}%)")
            
            return SiloData(
                name='StockVue',
                timestamp=datetime.fromisoformat(data.get('scan_timestamp', '').replace('Z', '+00:00')),
                metrics={
                    'total_stocks': len(results),
                    'long_signals': long_count,
                    'short_signals': short_count,
                    'tech_bullish': tech_bullish,
                    'tech_bearish': tech_bearish,
                    'avg_change': sum(r.get('change_percent', 0) for r in results) / max(len(results), 1)
                },
                signals=signals,
                sentiment=sentiment
            )
        except Exception as e:
            logger.error(f"Failed to load StockVue data: {e}")
            return None
    
    def load_cycle_data(self) -> Optional[SiloData]:
        """Load CycleVue position data."""
        try:
            # CycleVue is static/config-driven
            # Current position: 2026, Late Expansion (70% ECM, 38% Structural, 11% Generational)
            
            return SiloData(
                name='CycleVue',
                timestamp=datetime.now(),
                metrics={
                    'ecm_phase': 'Late',  # 70% through 8.6yr cycle
                    'structural_phase': 'Recovery',  # 38% through 18yr
                    'generational_phase': 'Early',  # 11% through 54yr
                    'composite_position': 'Late Expansion / Early Generational'
                },
                signals=[
                    'ECM Late Phase (2028 peak ahead)',
                    'Structural Recovery Phase',
                    'Early Generational Position'
                ],
                sentiment='cautious'  # Late cycle = caution
            )
        except Exception as e:
            logger.error(f"Failed to load CycleVue data: {e}")
            return None
    
    def load_all_silos(self):
        """Load data from all silos."""
        logger.info("Loading data from all silos...")
        
        self.silo_data['cryptovue'] = self.load_crypto_data()
        self.silo_data['stockvue'] = self.load_stock_data()
        self.silo_data['cyclevue'] = self.load_cycle_data()
        
        loaded = sum(1 for v in self.silo_data.values() if v is not None)
        logger.info(f"Loaded {loaded}/{len(self.silo_data)} silos")
    
    def analyze_correlations(self) -> List[CrossSiloSignal]:
        """Find cross-silo patterns and generate signals."""
        signals = []
        
        crypto = self.silo_data.get('cryptovue')
        stocks = self.silo_data.get('stockvue')
        cycles = self.silo_data.get('cyclevue')
        
        if not all([crypto, stocks, cycles]):
            logger.warning("Missing data from some silos, analysis may be incomplete")
        
        # Pattern 1: Risk-on / Risk-off Alignment
        if crypto and stocks:
            crypto_bullish = crypto.sentiment == 'bullish'
            stocks_bullish = stocks.sentiment == 'bullish'
            
            if crypto_bullish and stocks_bullish:
                signals.append(CrossSiloSignal(
                    id='risk_on_aligned',
                    timestamp=datetime.now().isoformat(),
                    strength=SignalStrength.STRONG,
                    direction='risk_on',
                    headline='🟢 Risk-On Alignment: Crypto + Stocks Bullish',
                    description=f'Both risk assets showing bullish signals. Crypto: {crypto.metrics["long_signals"]} longs. Stocks: {stocks.metrics["long_signals"]} longs. Momentum supports growth positioning.',
                    contributing_silos=['CryptoVue', 'StockVue'],
                    confidence=0.75,
                    recommended_action='Consider increasing equity/crypto exposure. Watch for late-cycle exhaustion signals.'
                ))
            elif not crypto_bullish and not stocks_bullish:
                signals.append(CrossSiloSignal(
                    id='risk_off_aligned',
                    timestamp=datetime.now().isoformat(),
                    strength=SignalStrength.STRONG,
                    direction='risk_off',
                    headline='🔴 Risk-Off Alignment: Crypto + Stocks Bearish',
                    description=f'Both risk assets showing bearish signals. Defensive positioning warranted.',
                    contributing_silos=['CryptoVue', 'StockVue'],
                    confidence=0.75,
                    recommended_action='Reduce risk exposure. Consider gold (RGLD), bonds, or cash. Watch for capitulation.'
                ))
            else:
                signals.append(CrossSiloSignal(
                    id='divergence',
                    timestamp=datetime.now().isoformat(),
                    strength=SignalStrength.MODERATE,
                    direction='rotation',
                    headline='🟡 Divergence: Crypto vs Stocks Diverged',
                    description=f'Mixed signals between asset classes. Possible rotation or decoupling.',
                    contributing_silos=['CryptoVue', 'StockVue'],
                    confidence=0.60,
                    recommended_action='Tactical positioning. Wait for clarity before major moves.'
                ))
        
        # Pattern 2: Late Cycle + Risk Asset Strength = Warning
        if cycles and crypto:
            if cycles.metrics.get('ecm_phase') == 'Late' and crypto.sentiment == 'bullish':
                signals.append(CrossSiloSignal(
                    id='late_cycle_warning',
                    timestamp=datetime.now().isoformat(),
                    strength=SignalStrength.VERY_STRONG,
                    direction='risk_off',
                    headline='⚠️ Late Cycle Warning: Bullish Momentum in End Phase',
                    description=f'ECM cycle is 70% complete (Late Phase) but crypto showing bullish signals. Classic late-cycle exuberance pattern. High probability of sharp correction ahead.',
                    contributing_silos=['CycleVue', 'CryptoVue'],
                    confidence=0.85,
                    recommended_action='TAKE PROFITS. Reduce leverage. Move to defensive positions. This setup historically precedes 20-40% corrections.'
                ))
        
        # Pattern 3: Tech Divergence
        if stocks:
            tech_bullish = stocks.metrics.get('tech_bullish', 0)
            tech_bearish = stocks.metrics.get('tech_bearish', 0)
            
            if tech_bullish > 2 and tech_bearish == 0:
                signals.append(CrossSiloSignal(
                    id='tech_momentum',
                    timestamp=datetime.now().isoformat(),
                    strength=SignalStrength.MODERATE,
                    direction='risk_on',
                    headline='📈 Tech Momentum: AI/Semiconductor Strength',
                    description=f'{tech_bullish}/4 tech stocks showing long signals. AI/semiconductor theme active.',
                    contributing_silos=['StockVue'],
                    confidence=0.70,
                    recommended_action='Overweight NVDA, AMD, PLTR. Monitor for concentration risk.'
                ))
        
        # Pattern 4: Defensive Rotation (Gold + Healthcare)
        # If we had real-time sector data, this would trigger on JNJ + RGLD strength
        
        return signals
    
    def generate_report(self) -> str:
        """Generate comprehensive cross-silo report."""
        self.load_all_silos()
        signals = self.analyze_correlations()
        
        lines = [
            "# 🧠 Cross-Silo Intelligence Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## 📊 Silo Status",
            ""
        ]
        
        for name, data in self.silo_data.items():
            if data:
                lines.append(f"### {data.name}")
                lines.append(f"- Sentiment: **{data.sentiment.upper()}**")
                lines.append(f"- Key metrics: {json.dumps(data.metrics, indent=2)}")
                lines.append(f"- Top signals: {', '.join(data.signals[:2])}")
                lines.append("")
        
        lines.extend([
            "## 🎯 Cross-Silo Signals",
            ""
        ])
        
        if not signals:
            lines.append("*No significant cross-silo patterns detected.*")
        else:
            for sig in sorted(signals, key=lambda x: x.strength.value, reverse=True):
                strength_icon = {
                    SignalStrength.VERY_STRONG: '🔥',
                    SignalStrength.STRONG: '✅',
                    SignalStrength.MODERATE: '⚡',
                    SignalStrength.WEAK: '💡',
                    SignalStrength.NONE: '⚪'
                }.get(sig.strength, '⚪')
                
                lines.append(f"### {strength_icon} {sig.headline}")
                lines.append(f"**Strength:** {sig.strength.name} | **Confidence:** {sig.confidence:.0%}")
                lines.append(f"**Contributing:** {', '.join(sig.contributing_silos)}")
                lines.append(f"**Description:** {sig.description}")
                lines.append(f"**Action:** {sig.recommended_action}")
                lines.append("")
        
        return '\n'.join(lines)


if __name__ == '__main__':
    import sys
    # Fix Windows unicode output
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    engine = CrossSiloEngine()
    report = engine.generate_report()
    print(report)
