"""
Alpha Vantage Scraper for StockVue
Optimized for 25 calls/day free tier
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import time

# Config
# API key from TOOLS.md
API_KEY = '736QMMKKKRUZP5F3'
BASE_URL = "https://www.alphavantage.co/query"
DATA_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace\\data\\stocks")

# Stock symbols to track (prioritized list - 12 symbols for 24 calls/day with RSI)
# 25 calls/day = 12 symbols x 2 calls (price + RSI) = 24 calls, 1 spare
# Updated 2026-03-26: Balanced portfolio - Tech, Healthcare, Energy, Materials, Broad Market
DEFAULT_SYMBOLS = [
    # Tech/Growth - AI & Semiconductors
    'NVDA',  # AI/GPU leader
    'TSLA',  # EV/Energy
    'AAPL',  # Consumer tech
    'AMD',   # Semiconductor
    # Cloud/Big Tech
    'MSFT',  # Cloud/AI
    'AMZN',  # E-commerce/Cloud
    'META',  # Social/VR/Metaverse
    'PLTR',  # AI/Data analytics
    # Defensive/Sectors
    'JNJ',   # Healthcare/pharma dividend
    'SLB',   # Energy/oilfield services
    'RGLD',  # Gold royalty - recession hedge
    'VUAG',  # S&P 500 ETF - broad exposure
]


def ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def av_request(function: str, **params) -> Optional[Dict]:
    """Make Alpha Vantage API request with rate limiting."""
    url = f"{BASE_URL}?function={function}"
    for key, value in params.items():
        url += f"&{key}={value}"
    url += f"&apikey={API_KEY}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            print(f"API Error: {data['Error Message']}")
            return None
        if 'Note' in data:
            print(f"API Note: {data['Note']}")  # Usually rate limit warning
            return None
            
        return data
    except Exception as e:
        print(f"Request failed: {e}")
        return None


def get_daily_prices(symbol: str, outputsize: str = 'compact') -> Optional[pd.DataFrame]:
    """Get daily OHLCV data. Counts as 1 API call."""
    data = av_request('TIME_SERIES_DAILY', symbol=symbol, outputsize=outputsize)
    
    if not data or 'Time Series (Daily)' not in data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
    df = df.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume'
    })
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    # Add metadata
    df['symbol'] = symbol
    
    return df


def get_rsi(symbol: str, interval: str = 'daily', time_period: int = 14) -> Optional[pd.DataFrame]:
    """Get RSI technical indicator. Counts as 1 API call."""
    data = av_request('RSI', symbol=symbol, interval=interval, time_period=time_period, series_type='close')
    
    if not data or 'Technical Analysis: RSI' not in data:
        return None
    
    df = pd.DataFrame.from_dict(data['Technical Analysis: RSI'], orient='index')
    df = df.rename(columns={'RSI': 'rsi'})
    df['rsi'] = pd.to_numeric(df['rsi'])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df['symbol'] = symbol
    
    return df


def get_macd(symbol: str, interval: str = 'daily') -> Optional[pd.DataFrame]:
    """Get MACD technical indicator. Counts as 1 API call."""
    data = av_request('MACD', symbol=symbol, interval=interval, series_type='close')
    
    if not data or 'Technical Analysis: MACD' not in data:
        return None
    
    df = pd.DataFrame.from_dict(data['Technical Analysis: MACD'], orient='index')
    df = df.rename(columns={
        'MACD': 'macd',
        'MACD_Signal': 'macd_signal',
        'MACD_Hist': 'macd_hist'
    })
    for col in ['macd', 'macd_signal', 'macd_hist']:
        df[col] = pd.to_numeric(df[col])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df['symbol'] = symbol
    
    return df


def get_sma(symbol: str, time_period: int = 20) -> Optional[pd.DataFrame]:
    """Get SMA technical indicator. Counts as 1 API call."""
    data = av_request('SMA', symbol=symbol, interval='daily', time_period=time_period, series_type='close')
    
    if not data or 'Technical Analysis: SMA' not in data:
        return None
    
    df = pd.DataFrame.from_dict(data['Technical Analysis: SMA'], orient='index')
    df = df.rename(columns={'SMA': f'sma_{time_period}'})
    df[f'sma_{time_period}'] = pd.to_numeric(df[f'sma_{time_period}'])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df['symbol'] = symbol
    
    return df


def calculate_cs_rsi_mtf(df: pd.DataFrame, rsi_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate CS RSI MTF (Cumulative Strength RSI Multi-Timeframe).
    Your custom strategy adapted for Alpha Vantage data.
    """
    df = df.copy()
    
    # Merge RSI data
    if rsi_data is not None and not rsi_data.empty:
        df = df.join(rsi_data[['rsi']], how='left')
    
    # Calculate additional RSI periods if we have enough data
    if 'rsi' in df.columns:
        # RSI states
        df['rsi_bullish'] = df['rsi'] > 50
        df['rsi_overbought'] = df['rsi'] > 70
        df['rsi_oversold'] = df['rsi'] < 30
        
        # RSI slope (momentum)
        df['rsi_slope'] = df['rsi'].diff(3)  # 3-day slope
        df['rsi_acceleration'] = df['rsi_slope'].diff(1)
    
    return df


def calculate_signals(df: pd.DataFrame) -> Dict:
    """Generate trading signals from technical data."""
    if df is None or df.empty:
        return None
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    signal = 'hold'
    confidence = 0.0
    reasons = []
    
    # Price action
    price_change = ((latest['close'] - prev['close']) / prev['close'] * 100) if prev['close'] != 0 else 0
    
    # Price momentum signals (always available)
    if price_change > 2:
        signal = 'long'
        confidence = 0.55
        reasons.append(f'Strong positive momentum (+{price_change:.1f}%)')
    elif price_change > 0.5:
        signal = 'long'
        confidence = 0.45
        reasons.append(f'Positive momentum (+{price_change:.1f}%)')
    elif price_change < -2:
        signal = 'short'
        confidence = 0.55
        reasons.append(f'Strong negative momentum ({price_change:.1f}%)')
    elif price_change < -0.5:
        signal = 'short'
        confidence = 0.45
        reasons.append(f'Negative momentum ({price_change:.1f}%)')
    
    # Volume spike
    avg_volume = df['volume'].tail(20).mean()
    if latest['volume'] > avg_volume * 1.5:
        if signal == 'hold':
            signal = 'long'
            confidence = 0.4
        reasons.append(f'Volume spike ({latest["volume"]/1e6:.1f}M vs avg {avg_volume/1e6:.1f}M)')
    
    # RSI-based signals (if available)
    rsi = latest.get('rsi')
    if pd.notna(rsi) and not pd.isna(rsi):
        if rsi < 30:
            signal = 'long'
            confidence = max(confidence, 0.7)
            reasons.append(f'RSI oversold ({rsi:.1f})')
        elif rsi > 70:
            signal = 'short'
            confidence = max(confidence, 0.7)
            reasons.append(f'RSI overbought ({rsi:.1f})')
        elif rsi > 50 and latest.get('rsi_slope', 0) > 0:
            if signal == 'hold':
                signal = 'long'
                confidence = max(confidence, 0.55)
            reasons.append(f'RSI bullish momentum ({rsi:.1f})')
        elif rsi < 50 and latest.get('rsi_slope', 0) < 0:
            if signal == 'hold':
                signal = 'short'
                confidence = max(confidence, 0.55)
            reasons.append(f'RSI bearish momentum ({rsi:.1f})')
    
    # MACD signals
    macd = latest.get('macd')
    macd_signal = latest.get('macd_signal')
    if pd.notna(macd) and pd.notna(macd_signal):
        if macd > macd_signal and prev.get('macd', 0) <= prev.get('macd_signal', 0):
            if signal != 'long':
                signal = 'long'
                confidence = max(confidence, 0.65)
            reasons.append('MACD bullish crossover')
        elif macd < macd_signal and prev.get('macd', 0) >= prev.get('macd_signal', 0):
            if signal != 'short':
                signal = 'short'
                confidence = max(confidence, 0.65)
            reasons.append('MACD bearish crossover')
    
    # Volume confirmation
    avg_volume = df['volume'].tail(20).mean()
    if latest['volume'] > avg_volume * 1.5:
        confidence = min(confidence + 0.1, 0.95)
        reasons.append(f'High volume ({latest["volume"]/1e6:.1f}M vs avg {avg_volume/1e6:.1f}M)')
    
    # Build result
    result = {
        'symbol': latest['symbol'],
        'price': round(latest['close'], 2),
        'change_percent': round(price_change, 2),
        'volume': int(latest['volume']),
        'rsi': round(rsi, 2) if pd.notna(rsi) else None,
        'macd': round(macd, 4) if pd.notna(macd) else None,
        'signal': signal,
        'confidence': round(confidence, 2),
        'confidence_label': 'high' if confidence >= 0.7 else 'medium' if confidence >= 0.5 else 'low',
        'reasons': reasons,
        'timestamp': datetime.now().isoformat(),
        'data_date': str(df.index[-1].date())
    }
    
    return result


def scan_symbol(symbol: str, use_technicals: bool = True) -> Optional[Dict]:
    """
    Scan a single symbol. 
    1 call for prices + (optional) 1-2 calls for technicals.
    """
    print(f"Scanning {symbol}...")
    
    # Get price data (1 call)
    df = get_daily_prices(symbol)
    if df is None or df.empty:
        print(f"  No data for {symbol}")
        return None
    
    # Get technicals (optional, 1-2 more calls)
    if use_technicals:
        rsi_data = get_rsi(symbol)
        if rsi_data is not None:
            df = calculate_cs_rsi_mtf(df, rsi_data)
        
        # We can add more technicals here if we have call budget
        # macd_data = get_macd(symbol)  # +1 call
    
    # Calculate signals
    result = calculate_signals(df)
    
    # Save raw data for analysis
    ensure_data_dir()
    symbol_file = DATA_DIR / f"{symbol}_daily.csv"
    df.to_csv(symbol_file)
    
    return result


def scan_symbols(symbols: List[str], max_calls: int = 25) -> List[Dict]:
    """
    Scan multiple symbols respecting API call limits.
    
    Strategy:
    - With 25 calls, we can scan 12-25 symbols
    - 1 call per symbol for prices only
    - 2 calls per symbol for prices + RSI
    - 3 calls per symbol for prices + RSI + MACD
    """
    results = []
    calls_used = 0
    
    # Determine technical depth based on symbol count
    if len(symbols) <= 12:
        use_technicals = True  # 2 calls per symbol
        calls_per_symbol = 2
    elif len(symbols) <= 25:
        use_technicals = False  # 1 call per symbol (prices only)
        calls_per_symbol = 1
    else:
        symbols = symbols[:25]  # Cap at 25
        use_technicals = False
        calls_per_symbol = 1
    
    print(f"Scanning {len(symbols)} symbols ({calls_per_symbol} call(s) per symbol)")
    print(f"Expected API calls: {len(symbols) * calls_per_symbol}")
    print("")
    
    for symbol in symbols:
        if calls_used >= max_calls:
            print(f"API call limit reached ({max_calls}). Stopping.")
            break
        
        result = scan_symbol(symbol, use_technicals=use_technicals)
        if result:
            results.append(result)
            calls_used += calls_per_symbol
        
        # Rate limiting (5 calls per minute max for free tier)
        time.sleep(12)  # 12 seconds between calls
    
    return results


def save_scan_results(results: List[Dict], metadata: Dict = None):
    """Save scan results to JSON files."""
    ensure_data_dir()
    
    timestamp = datetime.now()
    
    scan_data = {
        "scan_timestamp": timestamp.isoformat(),
        "scan_date": timestamp.strftime("%Y-%m-%d"),
        "scan_time": timestamp.strftime("%H:%M:%S"),
        "api": "Alpha Vantage",
        "api_calls_used": metadata.get('calls_used', len(results)) if metadata else len(results),
        "total_stocks": len(results),
        "signals_found": len([r for r in results if r.get('signal') in ['long', 'short']]),
        "long_opportunities": len([r for r in results if r.get('signal') == 'long']),
        "short_opportunities": len([r for r in results if r.get('signal') == 'short']),
        "categories_scanned": ['alpha_vantage_universe'],
        "results": results
    }
    
    # Save latest
    latest_file = DATA_DIR / "stocks_latest.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, indent=2, default=str)
    
    # Append to history
    history_file = DATA_DIR / "stocks_history.json"
    history_data = []
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    history_data.append(scan_data)
    if len(history_data) > 500:
        history_data = history_data[-500:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, default=str)
    
    # Save dated
    month_dir = DATA_DIR / timestamp.strftime("%Y-%m")
    month_dir.mkdir(exist_ok=True)
    dated_file = month_dir / timestamp.strftime("%Y-%m-%d_%H%M%S.json")
    with open(dated_file, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, indent=2, default=str)
    
    return {
        "latest_file": str(latest_file),
        "history_file": str(history_file),
        "dated_file": str(dated_file),
        "scan_data": scan_data
    }


def run_stock_scan(symbols: List[str] = None, max_calls: int = 25):
    """Main scan function."""
    print("=" * 60)
    print("STOCKVUE — Alpha Vantage Scanner")
    print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    print("")
    
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    
    print(f"Symbols to scan: {len(symbols)}")
    print(f"Max API calls: {max_calls}")
    print("")
    
    # Run scan
    results = scan_symbols(symbols, max_calls=max_calls)
    
    if results:
        # Save results
        metadata = {'calls_used': len(results) * (2 if len(symbols) <= 12 else 1)}
        saved = save_scan_results(results, metadata)
        scan_data = saved['scan_data']
        
        print("")
        print("=" * 60)
        print("SCAN COMPLETE")
        print("=" * 60)
        print(f"Total Stocks: {scan_data['total_stocks']}")
        print(f"Signals Found: {scan_data['signals_found']}")
        print(f"  - Long: {scan_data['long_opportunities']}")
        print(f"  - Short: {scan_data['short_opportunities']}")
        print(f"API Calls Used: {scan_data['api_calls_used']}")
        print(f"Files saved:")
        print(f"  - {saved['latest_file']}")
        print(f"  - {saved['history_file']}")
        print(f"  - {saved['dated_file']}")
        
        # Print signals
        if scan_data['signals_found'] > 0:
            print("")
            print("SIGNALS:")
            for r in results:
                if r['signal'] in ['long', 'short']:
                    emoji = "🟢" if r['signal'] == 'long' else "🔴"
                    print(f"  {emoji} {r['symbol']}: {r['signal'].upper()} (conf: {r['confidence']}, RSI: {r['rsi']})")
                    print(f"     Reasons: {', '.join(r['reasons'])}")
        
        return len(results)
    else:
        print("WARNING: No data collected")
        return 0


if __name__ == "__main__":
    count = run_stock_scan()
    exit(0 if count > 0 else 1)
