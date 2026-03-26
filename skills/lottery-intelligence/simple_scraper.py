"""
LotteryVue — Simple Archive Parser
Parses numbers directly from archive page HTML structure.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace\\skills\\lottery-intelligence")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.irishlottery.com"


def parse_irish_archive_page(soup: BeautifulSoup, year: int) -> List[Dict]:
    """Parse Irish Lotto archive page - numbers are visible directly on page."""
    draws = []
    
    # Find all result rows - each has a date link followed by numbers
    # Structure: Link to result, then 6 numbers + bonus as list items
    
    # Get all list items that contain numbers
    all_lis = soup.find_all('li')
    
    i = 0
    while i < len(all_lis):
        li = all_lis[i]
        
        # Check if this li contains a date link
        link = li.find('a', href=re.compile(r'/results/irish-lotto-result-'))
        if link:
            # Extract date from URL
            href = link.get('href', '')
            date_match = re.search(r'result-(\d{2})-(\d{2})-(\d{4})', href)
            if date_match:
                day, month, year_str = date_match.groups()
                date_str = f"{year_str}-{month}-{day}"
                
                # Next 7 lis should be the numbers (6 main + bonus)
                numbers = []
                bonus = None
                
                for j in range(1, 8):
                    if i + j < len(all_lis):
                        num_text = all_lis[i + j].get_text().strip()
                        if num_text.isdigit():
                            if j <= 6:
                                numbers.append(int(num_text))
                            else:
                                bonus = int(num_text)
                
                if len(numbers) == 6:
                    draws.append({
                        'date': date_str,
                        'game': 'Irish Lotto',
                        'numbers': numbers,
                        'bonus': bonus
                    })
                    
                # Skip past the numbers we just processed
                i += 7
                continue
        
        i += 1
    
    return draws


def parse_euromillions_archive_page(soup: BeautifulSoup, year: int) -> List[Dict]:
    """Parse EuroMillions archive page."""
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
                
                # Next 7 lis: 5 main numbers + 2 lucky stars
                numbers = []
                lucky_stars = []
                
                for j in range(1, 8):
                    if i + j < len(all_lis):
                        num_text = all_lis[i + j].get_text().strip()
                        if num_text.isdigit():
                            if j <= 5:
                                numbers.append(int(num_text))
                            else:
                                lucky_stars.append(int(num_text))
                
                if len(numbers) == 5:
                    draws.append({
                        'date': date_str,
                        'game': 'EuroMillions',
                        'numbers': numbers,
                        'lucky_stars': lucky_stars[:2]
                    })
                    
                i += 7
                continue
        
        i += 1
    
    return draws


def scrape_year(year: int, game: str) -> List[Dict]:
    """Scrape a single year."""
    try:
        if game == 'irish':
            url = f"{BASE_URL}/archive?year={year}"
            parse_func = parse_irish_archive_page
        else:
            url = f"{BASE_URL}/euromillions-archive?year={year}"
            parse_func = parse_euromillions_archive_page
        
        print(f"Fetching {url}...")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        draws = parse_func(soup, year)
        
        print(f"  Extracted {len(draws)} draws")
        return draws
        
    except Exception as e:
        print(f"  Error: {e}")
        return []


def main():
    """Run full scrape."""
    print("="*60)
    print("LOTTERYVUE ARCHIVE SCRAPER")
    print("="*60)
    
    irish_data = []
    euro_data = []
    
    # Irish Lotto: 1988-2026
    print("\nPHASE 1: Irish Lotto (1988-2026)")
    print("-"*60)
    
    for year in range(2026, 1987, -1):
        draws = scrape_year(year, 'irish')
        irish_data.extend(draws)
        time.sleep(0.5)  # Rate limiting
    
    print(f"\nTotal Irish Lotto draws: {len(irish_data)}")
    
    # EuroMillions: 2004-2026
    print("\nPHASE 2: EuroMillions (2004-2026)")
    print("-"*60)
    
    for year in range(2026, 2003, -1):
        draws = scrape_year(year, 'euromillions')
        euro_data.extend(draws)
        time.sleep(0.5)
    
    print(f"\nTotal EuroMillions draws: {len(euro_data)}")
    
    # Save databases
    print("\n" + "="*60)
    print("SAVING DATABASES")
    print("="*60)
    
    # Irish Lotto
    irish_db = {
        'metadata': {
            'game': 'Irish Lotto',
            'format': '6/47 + Bonus',
            'draw_days': ['Wednesday', 'Saturday'],
            'first_draw': '1988-04-16',
            'total_draws': len(irish_data),
            'scraped_at': datetime.now().isoformat()
        },
        'draws': sorted(irish_data, key=lambda x: x['date'], reverse=True)
    }
    
    with open(DATA_DIR / 'irish_lotto_complete.json', 'w') as f:
        json.dump(irish_db, f, indent=2)
    
    # EuroMillions
    euro_db = {
        'metadata': {
            'game': 'EuroMillions',
            'format': '5/50 + 2/12 Lucky Stars',
            'draw_days': ['Tuesday', 'Friday'],
            'first_draw': '2004-02-13',
            'total_draws': len(euro_data),
            'scraped_at': datetime.now().isoformat()
        },
        'draws': sorted(euro_data, key=lambda x: x['date'], reverse=True)
    }
    
    with open(DATA_DIR / 'euromillions_complete.json', 'w') as f:
        json.dump(euro_db, f, indent=2)
    
    print(f"\n✓ irish_lotto_complete.json: {len(irish_data)} draws")
    print(f"✓ euromillions_complete.json: {len(euro_data)} draws")
    print(f"\nFiles saved to: {DATA_DIR}")


if __name__ == '__main__':
    main()
