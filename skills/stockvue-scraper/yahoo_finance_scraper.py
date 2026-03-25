"""
yahoo_finance_scraper.py — Scrape stock data from Yahoo Finance markets pages
Stores data for StockVue dashboard, runs every 3 hours
"""
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import time
import re

# Config
DATA_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace\\data\\stocks")
GITHUB_REPO = "impro58-oss/rooquest1"

# Yahoo Finance URLs
YAHOO_URLS = {
    'most_active': 'https://finance.yahoo.com/markets/stocks/most-active/',
    'trending': 'https://finance.yahoo.com/markets/stocks/trending/',
    'losers': 'https://finance.yahoo.com/markets/stocks/losers/',
    'gainers_52w': 'https://finance.yahoo.com/markets/stocks/52-week-gainers/'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def parse_price(price_str):
    """Parse price string to float."""
    if not price_str or price_str == 'N/A':
        return None
    # Remove $, commas, and other symbols
    cleaned = re.sub(r'[^\d.\-]', '', str(price_str))
    try:
        return float(cleaned) if cleaned else None
    except:
        return None


def parse_percentage(pct_str):
    """Parse percentage string to float."""
    if not pct_str or pct_str == 'N/A':
        return None
    # Remove %, +, commas
    cleaned = re.sub(r'[^\d.\-]', '', str(pct_str))
    try:
        return float(cleaned) if cleaned else None
    except:
        return None


def parse_volume(vol_str):
    """Parse volume string (handles K, M, B)."""
    if not vol_str or vol_str == 'N/A':
        return None
    vol_str = str(vol_str).upper().replace(',', '')
    multipliers = {'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}
    
    for suffix, multiplier in multipliers.items():
        if suffix in vol_str:
            try:
                return float(vol_str.replace(suffix, '')) * multiplier
            except:
                return None
    
    try:
        return float(vol_str)
    except:
        return None


def scrape_yahoo_page(url, category_name):
    """Scrape a single Yahoo Finance page."""
    print(f"Scraping {category_name}...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        stocks = []
        
        # Yahoo Finance tables have specific structure
        # Try multiple selectors for robustness
        rows = soup.select('table tbody tr') or soup.select('[data-test="quote-table-row"]') or soup.select('.yf-1dbt8wv tbody tr')
        
        if not rows:
            # Try alternative selectors
            rows = soup.find_all('tr', {'class': lambda x: x and ('row' in x.lower() if x else False)})
        
        print(f"  Found {len(rows)} rows")
        
        for row in rows[:25]:  # Top 25 from each category
            try:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 5:
                    continue
                
                # Extract symbol and name
                symbol_elem = cells[0].select_one('a') or cells[0]
                symbol = symbol_elem.text.strip() if symbol_elem else None
                
                # Skip if no symbol
                if not symbol or len(symbol) > 10 or not symbol.isalpha():
                    continue
                
                name_elem = cells[1] if len(cells) > 1 else None
                name = name_elem.text.strip() if name_elem else symbol
                
                # Extract price
                price_elem = cells[2] if len(cells) > 2 else None
                price = parse_price(price_elem.text if price_elem else None)
                
                # Extract change and percent
                change_elem = cells[3] if len(cells) > 3 else None
                change_text = change_elem.text if change_elem else ''
                
                # Try to separate change and percent
                change_match = re.search(r'([\d.,]+)', change_text)
                change = parse_price(change_match.group(1) if change_match else None)
                
                pct_match = re.search(r'\(([\d\.,]+)%\)', change_text)
                change_percent = parse_percentage(pct_match.group(1) if pct_match else None)
                
                # Extract volume
                vol_elem = cells[4] if len(cells) > 4 else None
                volume = parse_volume(vol_elem.text if vol_elem else None)
                
                # Extract avg volume (if available)
                avg_vol = None
                if len(cells) > 5:
                    avg_vol = parse_volume(cells[5].text)
                
                # Determine trend from category
                trend = 'neutral'
                if category_name == 'gainers_52w':
                    trend = 'bullish'
                elif category_name == 'losers':
                    trend = 'bearish'
                elif category_name == 'most_active':
                    trend = 'active'
                
                stock = {
                    'symbol': symbol,
                    'name': name[:50],  # Truncate long names
                    'price': price,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': volume,
                    'avg_volume': avg_vol,
                    'market_cap': None,  # Will calculate if possible
                    'pe_ratio': None,
                    'category': category_name,
                    'trend': trend,
                    'timestamp': datetime.now().isoformat()
                }
                
                stocks.append(stock)
                
            except Exception as e:
                print(f"    Error parsing row: {e}")
                continue
        
        return stocks
        
    except Exception as e:
        print(f"  ERROR scraping {category_name}: {e}")
        return []


def calculate_signals(stocks):
    """Calculate trading signals for stocks."""
    for stock in stocks:
        # Signal logic
        signal = 'hold'
        confidence = 0.0
        reasons = []
        
        change_pct = stock.get('change_percent') or 0
        volume = stock.get('volume') or 0
        avg_vol = stock.get('avg_volume') or volume
        
        # Volume spike detection
        vol_spike = False
        if volume and avg_vol and avg_vol > 0:
            vol_ratio = volume / avg_vol
            if vol_ratio > 2.0:
                vol_spike = True
                reasons.append(f'Volume spike {vol_ratio:.1f}x avg')
        
        # Signal determination
        if stock['category'] == 'gainers_52w':
            if change_pct > 10:
                signal = 'long'
                confidence = min(abs(change_pct) / 20, 0.9)
                reasons.append('Strong 52-week momentum')
            elif change_pct > 5:
                signal = 'long'
                confidence = min(abs(change_percent) / 20, 0.7)
                reasons.append('52-week uptrend')
        
        elif stock['category'] == 'losers':
            if change_pct < -10:
                signal = 'short'
                confidence = min(abs(change_pct) / 20, 0.9)
                reasons.append('Strong breakdown')
            elif change_pct < -5:
                signal = 'short'
                confidence = min(abs(change_pct) / 20, 0.7)
                reasons.append('Downward momentum')
        
        elif stock['category'] == 'most_active':
            if vol_spike and change_pct > 2:
                signal = 'long'
                confidence = 0.6
                reasons.append('High activity + positive')
            elif vol_spike and change_pct < -2:
                signal = 'short'
                confidence = 0.6
                reasons.append('High activity + negative')
        
        elif stock['category'] == 'trending':
            if change_pct > 3:
                signal = 'long'
                confidence = 0.55
                reasons.append('Trending up')
            elif change_pct < -3:
                signal = 'short'
                confidence = 0.55
                reasons.append('Trending down')
        
        stock['signal'] = signal
        stock['confidence'] = round(confidence, 2)
        stock['confidence_label'] = 'high' if confidence >= 0.7 else 'medium' if confidence >= 0.5 else 'low'
        stock['reasons'] = reasons
        stock['setup_type'] = 'momentum'
    
    return stocks


def save_scan_results(results, timestamp=None):
    """Save scan results to JSON files."""
    if timestamp is None:
        timestamp = datetime.now()
    
    data_dir = ensure_data_dir()
    
    # Prepare data structure
    scan_data = {
        "scan_timestamp": timestamp.isoformat(),
        "scan_date": timestamp.strftime("%Y-%m-%d"),
        "scan_time": timestamp.strftime("%H:%M:%S"),
        "total_stocks": len(results),
        "signals_found": len([r for r in results if r.get('signal') in ['long', 'short'] and r.get('confidence', 0) >= 0.5]),
        "long_opportunities": len([r for r in results if r.get('signal') == 'long']),
        "short_opportunities": len([r for r in results if r.get('signal') == 'short']),
        "categories_scanned": list(set(r.get('category') for r in results)),
        "results": results
    }
    
    # 1. Save to stocks_latest.json (for dashboard)
    latest_file = data_dir / "stocks_latest.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, indent=2, default=str)
    
    # 2. Append to stocks_history.json (for trends)
    history_file = data_dir / "stocks_history.json"
    history_data = []
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    history_data.append(scan_data)
    
    # Keep last 500 scans (manage file size)
    if len(history_data) > 500:
        history_data = history_data[-500:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, default=str)
    
    # 3. Save dated archive
    month_dir = data_dir / timestamp.strftime("%Y-%m")
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


def run_stock_scan():
    """Main function to run stock scan."""
    print("=" * 60)
    print("STOCKVUE — Yahoo Finance Market Scanner")
    print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    all_stocks = []
    
    # Scrape each category
    for category, url in YAHOO_URLS.items():
        stocks = scrape_yahoo_page(url, category)
        all_stocks.extend(stocks)
        time.sleep(1)  # Be nice to Yahoo
    
    print(f"\nTotal stocks collected: {len(all_stocks)}")
    
    # Calculate signals
    all_stocks = calculate_signals(all_stocks)
    
    # Save results
    result = save_scan_results(all_stocks)
    
    # Summary
    scan_data = result['scan_data']
    print("\n" + "=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)
    print(f"Total Stocks: {scan_data['total_stocks']}")
    print(f"Signals Found: {scan_data['signals_found']}")
    print(f"  - Long: {scan_data['long_opportunities']}")
    print(f"  - Short: {scan_data['short_opportunities']}")
    print(f"\nFiles saved:")
    print(f"  - {result['latest_file']}")
    print(f"  - {result['history_file']}")
    print(f"  - {result['dated_file']}")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    run_stock_scan()
