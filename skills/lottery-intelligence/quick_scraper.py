"""
Working Historical Lottery Scraper
Uses correct URLs based on testing
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
import re

BASE_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence")
DATA_DIR = BASE_DIR / "data"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def scrape_euromillions():
    """Scrape EuroMillions 2020-2026"""
    print("Scraping EuroMillions...")
    all_draws = []
    
    for year in range(2026, 2019, -1):
        url = f"https://www.irishlottery.com/euromillions-archive?year={year}"
        print(f"  {year}...", end=" ")
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Parse using working method
            draws = []
            all_lis = soup.find_all('li')
            
            i = 0
            while i < len(all_lis):
                li = all_lis[i]
                link = li.find('a', href=re.compile(r'/results/euromillions-result-'))
                
                if link:
                    href = link.get('href', '')
                    date_match = re.search(r'result-(\d{2})-(\d{2})-(\d{4})', href)
                    
                    if date_match:
                        day, month, year_str = date_match.groups()
                        date_str = f"{year_str}-{month}-{day}"
                        
                        numbers = []
                        for j in range(1, 8):
                            if i + j < len(all_lis):
                                num_text = all_lis[i + j].get_text().strip()
                                if num_text.isdigit():
                                    numbers.append(int(num_text))
                        
                        if len(numbers) >= 5:
                            draws.append({
                                'date': date_str,
                                'numbers': numbers[:5],
                                'lucky_stars': numbers[5:7] if len(numbers) > 5 else []
                            })
                        
                        i += 7
                        continue
                
                i += 1
            
            # Remove duplicates
            seen = set()
            unique = []
            for d in draws:
                key = d['date']
                if key not in seen:
                    seen.add(key)
                    unique.append(d)
            
            print(f"{len(unique)} draws")
            all_draws.extend(unique)
            
        except Exception as e:
            print(f"ERROR: {e}")
        
        time.sleep(1)
    
    # Save
    all_draws.sort(key=lambda x: x['date'], reverse=True)
    with open(DATA_DIR / 'euromillions_historical.json', 'w') as f:
        json.dump({
            'metadata': {'game': 'EuroMillions', 'total_draws': len(all_draws), 'years': '2020-2026'},
            'draws': all_draws
        }, f, indent=2)
    
    print(f"Saved {len(all_draws)} EuroMillions draws")
    return all_draws

if __name__ == '__main__':
    print("="*60)
    print("LOTTERY SCRAPER - Phase 1")
    print("="*60)
    
    # EuroMillions first (known working)
    euro = scrape_euromillions()
    
    print(f"\nTotal: {len(euro)} EuroMillions draws")
    print("Done!")
