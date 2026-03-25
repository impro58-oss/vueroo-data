"""
yahoo_finance_scraper_v2.py — Robust Yahoo Finance scraper using Playwright
Handles JavaScript-rendered content and anti-bot protection
"""
import asyncio
from playwright.async_api import async_playwright
import json
import re
from datetime import datetime
from pathlib import Path

# Config
DATA_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace\\data\\stocks")

YAHOO_URLS = {
    'most_active': 'https://finance.yahoo.com/markets/stocks/most-active/',
    'trending': 'https://finance.yahoo.com/markets/stocks/trending/',
    'losers': 'https://finance.yahoo.com/markets/stocks/losers/',
    'gainers_52w': 'https://finance.yahoo.com/markets/stocks/52-week-gainers/'
}


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def parse_value(value_str):
    """Parse numeric values from strings."""
    if not value_str or value_str in ['N/A', '-', '']:
        return None
    
    # Remove $, %, commas, + signs
    cleaned = re.sub(r'[$,%+\s]', '', str(value_str))
    
    # Handle K, M, B, T
    multipliers = {'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}
    for suffix, mult in multipliers.items():
        if suffix in cleaned.upper():
            try:
                num = float(cleaned.upper().replace(suffix, ''))
                return num * mult
            except:
                return None
    
    try:
        return float(cleaned)
    except:
        return None


async def scrape_yahoo_page(page, url, category_name):
    """Scrape a Yahoo Finance page using Playwright."""
    print(f"Scraping {category_name}...")
    
    try:
        # Navigate with timeout
        await page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Wait for table to load (multiple selectors)
        selectors = [
            'table tbody tr',
            '[data-test="quote-table-row"]',
            '.yf-1dbt8wv tbody tr',
            '[data-field="regularMarketPrice"]',
            '.yf-1dbt8wv'  # Container for the table
        ]
        
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                break
            except:
                continue
        
        # Additional wait for JavaScript to render
        await asyncio.sleep(3)
        
        stocks = []
        
        # Try to extract data from the page
        # Method 1: Direct table extraction
        rows = await page.query_selector_all('table tbody tr')
        
        if not rows:
            # Method 2: Try alternative selectors
            rows = await page.query_selector_all('[data-test="quote-table-row"]')
        
        if not rows:
            # Method 3: Look for data in script tags (JSON)
            scripts = await page.query_selector_all('script')
            for script in scripts:
                text = await script.text_content()
                if 'root.App.main' in text:
                    # Extract JSON data from script
                    match = re.search(r'root\.App\.main\s*=\s*(\{.+?\});', text, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            # Parse the JSON structure
                            if isinstance(data, dict):
                                # Look for quotes/stocks in the data
                                stocks_data = extract_stocks_from_json(data, category_name)
                                if stocks_data:
                                    stocks.extend(stocks_data)
                        except:
                            pass
        
        if rows and not stocks:
            # Extract from table rows
            for row in rows[:25]:  # Top 25
                try:
                    cells = await row.query_selector_all('td')
                    if len(cells) < 5:
                        continue
                    
                    # Extract data from cells
                    symbol_elem = await cells[0].query_selector('a')
                    symbol = await symbol_elem.text_content() if symbol_elem else await cells[0].text_content()
                    symbol = symbol.strip() if symbol else None
                    
                    if not symbol or len(symbol) > 10:
                        continue
                    
                    name = await cells[1].text_content() if len(cells) > 1 else symbol
                    name = name.strip()[:50] if name else symbol
                    
                    price_text = await cells[2].text_content() if len(cells) > 2 else None
                    price = parse_value(price_text)
                    
                    change_text = await cells[3].text_content() if len(cells) > 3 else None
                    change = parse_value(change_text)
                    
                    # Try to extract percent from change text
                    change_percent = None
                    if change_text and '%' in change_text:
                        change_percent = parse_value(change_text.split('%')[0])
                    
                    vol_text = await cells[4].text_content() if len(cells) > 4 else None
                    volume = parse_value(vol_text)
                    
                    stock = {
                        'symbol': symbol,
                        'name': name,
                        'price': price,
                        'change': change,
                        'change_percent': change_percent,
                        'volume': volume,
                        'category': category_name,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    stocks.append(stock)
                    
                except Exception as e:
                    print(f"  Error parsing row: {e}")
                    continue
        
        print(f"  Found {len(stocks)} stocks")
        return stocks
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return []


def extract_stocks_from_json(data, category):
    """Extract stock data from Yahoo's JSON structure."""
    stocks = []
    try:
        # Navigate through Yahoo's nested JSON structure
        # This is a simplified version - actual structure may vary
        context = data.get('context', {})
        dispatcher = context.get('dispatcher', {})
        stores = dispatcher.get('stores', {})
        
        # Look for quote data in stores
        for store_name, store_data in stores.items():
            if 'quote' in store_name.lower() or 'price' in store_name.lower():
                quotes = store_data if isinstance(store_data, list) else [store_data]
                for quote in quotes:
                    if isinstance(quote, dict):
                        symbol = quote.get('symbol') or quote.get('ticker')
                        if symbol:
                            stock = {
                                'symbol': symbol,
                                'name': quote.get('shortName', quote.get('longName', symbol)),
                                'price': quote.get('regularMarketPrice', quote.get('price')),
                                'change': quote.get('regularMarketChange', quote.get('change')),
                                'change_percent': quote.get('regularMarketChangePercent', quote.get('changePercent')),
                                'volume': quote.get('regularMarketVolume', quote.get('volume')),
                                'category': category,
                                'timestamp': datetime.now().isoformat()
                            }
                            stocks.append(stock)
    except Exception as e:
        print(f"  JSON extraction error: {e}")
    
    return stocks


def calculate_signals(stocks):
    """Calculate trading signals."""
    for stock in stocks:
        signal = 'hold'
        confidence = 0.0
        reasons = []
        
        change_pct = stock.get('change_percent') or 0
        volume = stock.get('volume') or 0
        
        # Signal logic based on category and momentum
        if stock['category'] == 'gainers_52w':
            if change_pct and change_pct > 10:
                signal = 'long'
                confidence = min(abs(change_pct) / 30, 0.9)
                reasons.append('Strong 52W momentum')
            elif change_pct and change_pct > 5:
                signal = 'long'
                confidence = min(abs(change_pct) / 30, 0.7)
                reasons.append('52W uptrend')
        
        elif stock['category'] == 'losers':
            if change_pct and change_pct < -10:
                signal = 'short'
                confidence = min(abs(change_pct) / 30, 0.9)
                reasons.append('Strong breakdown')
            elif change_pct and change_pct < -5:
                signal = 'short'
                confidence = min(abs(change_pct) / 30, 0.7)
                reasons.append('Downward momentum')
        
        elif stock['category'] == 'most_active':
            if volume and volume > 1e7:  # 10M+ volume
                if change_pct and change_pct > 2:
                    signal = 'long'
                    confidence = 0.6
                    reasons.append('High volume + positive')
                elif change_pct and change_pct < -2:
                    signal = 'short'
                    confidence = 0.6
                    reasons.append('High volume + negative')
        
        elif stock['category'] == 'trending':
            if change_pct and change_pct > 3:
                signal = 'long'
                confidence = 0.55
                reasons.append('Trending up')
            elif change_pct and change_pct < -3:
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
    """Save scan results."""
    if timestamp is None:
        timestamp = datetime.now()
    
    data_dir = ensure_data_dir()
    
    scan_data = {
        "scan_timestamp": timestamp.isoformat(),
        "scan_date": timestamp.strftime("%Y-%m-%d"),
        "scan_time": timestamp.strftime("%H:%M:%S"),
        "total_stocks": len(results),
        "signals_found": len([r for r in results if r.get('signal') in ['long', 'short']]),
        "long_opportunities": len([r for r in results if r.get('signal') == 'long']),
        "short_opportunities": len([r for r in results if r.get('signal') == 'short']),
        "categories_scanned": list(set(r.get('category') for r in results)),
        "results": results
    }
    
    # Save latest
    latest_file = data_dir / "stocks_latest.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, indent=2, default=str)
    
    # Append to history
    history_file = data_dir / "stocks_history.json"
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


async def run_stock_scan():
    """Main scan function."""
    print("=" * 60)
    print("STOCKVUE — Yahoo Finance Market Scanner (Playwright)")
    print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    all_stocks = []
    
    async with async_playwright() as p:
        # Launch browser with stealth options
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True
        )
        
        page = await context.new_page()
        
        # Scrape each category
        for category, url in YAHOO_URLS.items():
            stocks = await scrape_yahoo_page(page, url, category)
            all_stocks.extend(stocks)
            await asyncio.sleep(2)  # Rate limiting
        
        await browser.close()
    
    print(f"\nTotal stocks collected: {len(all_stocks)}")
    
    if all_stocks:
        all_stocks = calculate_signals(all_stocks)
        result = save_scan_results(all_stocks)
        scan_data = result['scan_data']
        
        print("=" * 60)
        print("SCAN COMPLETE")
        print("=" * 60)
        print(f"Total Stocks: {scan_data['total_stocks']}")
        print(f"Signals Found: {scan_data['signals_found']}")
        print(f"  - Long: {scan_data['long_opportunities']}")
        print(f"  - Short: {scan_data['short_opportunities']}")
    else:
        print("WARNING: No stocks collected - may need manual intervention")
    
    return len(all_stocks)


if __name__ == "__main__":
    count = asyncio.run(run_stock_scan())
    exit(0 if count > 0 else 1)
