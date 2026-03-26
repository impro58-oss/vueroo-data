"""
Phase 2: Detailed Result Page Scraping
Gets jackpot winners, prize breakdowns, machine/ball set info
For both EuroMillions and Irish Lotto (2020-2026)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence")
DATA_DIR = BASE_DIR / "data"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def scrape_result_details(url, game_type):
    """Scrape detailed info from individual result page"""
    details = {
        'jackpot_winners': None,
        'total_winners': None,
        'total_prize_fund': None,
        'machine': None,
        'ball_set': None,
        'prize_breakdown': []
    }
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text()
        
        # Extract jackpot winners
        jackpot_patterns = [
            r'(\d+)\s+Jackpot\s+Winner',
            r'Jackpot\s+Winners?[:\s]+(\d+)',
            r'Number\s+of\s+jackpot\s+winners[:\s]+(\d+)'
        ]
        
        for pattern in jackpot_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['jackpot_winners'] = int(match.group(1))
                break
        
        # Total winners
        total_match = re.search(r'Total\s+Winners[:\s]+([\d,]+)', text, re.IGNORECASE)
        if total_match:
            details['total_winners'] = int(total_match.group(1).replace(',', ''))
        
        # Prize fund
        fund_match = re.search(r'Prize\s+Fund[:\s]+([€£$][\d,]+(?:\.\d+)?\s*(?:Million)?)', text, re.IGNORECASE)
        if fund_match:
            details['total_prize_fund'] = fund_match.group(1)
        
        # Machine and ball set
        machine_match = re.search(r'Machine[:\s]+(\w+)', text, re.IGNORECASE)
        if machine_match:
            details['machine'] = machine_match.group(1)
        
        ballset_match = re.search(r'Ball\s+Set[:\s]+(\w+)', text, re.IGNORECASE)
        if ballset_match:
            details['ball_set'] = ballset_match.group(1)
        
        # Prize breakdown table
        tables = soup.find_all('table')
        for table in tables:
            headers = [th.get_text().strip().lower() for th in table.find_all('th')]
            if 'match' in headers or 'prize' in headers or 'winners' in headers:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        prize_info = {
                            'match': cells[0].get_text().strip(),
                            'winners': cells[1].get_text().strip(),
                            'prize': cells[2].get_text().strip()
                        }
                        details['prize_breakdown'].append(prize_info)
        
        time.sleep(0.5)  # Rate limiting
        
    except Exception as e:
        print(f"    Error scraping {url}: {e}")
    
    return details

def enhance_euromillions():
    """Add detailed info to EuroMillions draws"""
    print("="*60)
    print("ENHANCING EUROMILLIONS DATA")
    print("="*60)
    
    # Load existing data
    with open(DATA_DIR / 'euromillions_historical.json', 'r') as f:
        data = json.load(f)
    
    draws = data['draws']
    
    # Remove duplicates first
    seen = {}
    unique = []
    for d in draws:
        key = (d['date'], tuple(d['numbers']), tuple(d.get('lucky_stars', [])))
        if key not in seen:
            seen[key] = True
            unique.append(d)
    
    print(f"Processing {len(unique)} unique draws...")
    print()
    
    # Enhance each draw
    for i, draw in enumerate(unique):
        if draw.get('url'):
            if (i + 1) % 10 == 0 or i == 0:
                print(f"  Processing {i+1}/{len(unique)}: {draw['date']}")
            
            details = scrape_result_details(draw['url'], 'euro')
            draw.update(details)
    
    # Save enhanced data
    data['draws'] = unique
    data['metadata']['enhanced_at'] = datetime.now().isoformat()
    data['metadata']['total_draws'] = len(unique)
    
    with open(DATA_DIR / 'euromillions_enhanced.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nEnhanced data saved to euromillions_enhanced.json")
    return unique

def scrape_irish_lotto_full():
    """Scrape Irish Lotto from 2020-2026 with details"""
    print("\n" + "="*60)
    print("SCRAPING IRISH LOTTO (2020-2026)")
    print("="*60)
    
    all_draws = []
    years = list(range(2026, 2019, -1))
    
    for year in years:
        url = f"https://www.irishlottery.com/irish-lotto-archive?year={year}"
        print(f"\nFetching {year}...", end=" ")
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Parse using li traversal method
            draws = []
            all_lis = soup.find_all('li')
            
            i = 0
            while i < len(all_lis):
                li = all_lis[i]
                link = li.find('a', href=re.compile(r'/results/irish-lotto-result-'))
                
                if link:
                    href = link.get('href', '')
                    date_match = re.search(r'result-(\d{2})-(\d{2})-(\d{4})', href)
                    
                    if date_match:
                        day, month, year_str = date_match.groups()
                        date_str = f"{year_str}-{month}-{day}"
                        
                        numbers = []
                        bonus = None
                        
                        for j in range(1, 8):
                            if i + j < len(all_lis):
                                num_text = all_lis[i + j].get_text().strip()
                                if num_text.isdigit():
                                    num = int(num_text)
                                    if j <= 6:
                                        numbers.append(num)
                                    else:
                                        bonus = num
                        
                        if len(numbers) == 6:
                            full_url = href if href.startswith('http') else f"https://www.irishlottery.com{href}"
                            draws.append({
                                'date': date_str,
                                'game': 'Irish Lotto',
                                'numbers': numbers,
                                'bonus': bonus,
                                'url': full_url
                            })
                        
                        i += 7
                        continue
                
                i += 1
            
            print(f"{len(draws)} draws")
            
            # Enhance with details
            print(f"  Fetching details for {len(draws)} draws...")
            for j, draw in enumerate(draws):
                if (j + 1) % 10 == 0:
                    print(f"    {j+1}/{len(draws)}")
                
                details = scrape_result_details(draw['url'], 'irish')
                draw.update(details)
            
            all_draws.extend(draws)
            
        except Exception as e:
            print(f"ERROR: {e}")
        
        time.sleep(1)
    
    # Remove duplicates
    seen = {}
    unique = []
    for d in all_draws:
        key = d['date']
        if key not in seen:
            seen[key] = True
            unique.append(d)
    
    unique.sort(key=lambda x: x['date'], reverse=True)
    
    # Save
    output = {
        'metadata': {
            'game': 'Irish Lotto',
            'format': '6/47 + Bonus',
            'draw_days': ['Wednesday', 'Saturday'],
            'total_draws': len(unique),
            'date_range': f"{unique[-1]['date']} to {unique[0]['date']}" if unique else 'N/A',
            'scraped_at': datetime.now().isoformat()
        },
        'draws': unique
    }
    
    with open(DATA_DIR / 'irish_lotto_enhanced.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved {len(unique)} Irish Lotto draws to irish_lotto_enhanced.json")
    return unique

if __name__ == '__main__':
    print("="*60)
    print("LOTTERYVUE PHASE 2 SCRAPER")
    print("="*60)
    print("Scraping detailed winner info for both games")
    print("2020-2026 coverage")
    print("="*60)
    print()
    
    # EuroMillions first
    euro_draws = enhance_euromillions()
    
    # Irish Lotto
    irish_draws = scrape_irish_lotto_full()
    
    print("\n" + "="*60)
    print("PHASE 2 COMPLETE")
    print("="*60)
    print(f"EuroMillions: {len(euro_draws)} draws with full details")
    print(f"Irish Lotto: {len(irish_draws)} draws with full details")
    print()
    print("Files created:")
    print("  - euromillions_enhanced.json")
    print("  - irish_lotto_enhanced.json")
    print()
    print("Ready for pattern analysis!")
