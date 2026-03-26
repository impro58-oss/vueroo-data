"""
LotteryVue Historical Data Scraper
Scrapes 2020-2026 for both Irish Lotto and EuroMillions
Based on working simple_scraper approach
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import time
import re

BASE_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.irishlottery.com"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_page(url):
    """Fetch page with retry"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"  Error: {e}")
        return None

def parse_irish_archive(soup, year):
    """Parse Irish Lotto archive page"""
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
                            if j <= 6:
                                numbers.append(int(num_text))
                            else:
                                bonus = int(num_text)
                
                if len(numbers) == 6:
                    draws.append({
                        'date': date_str,
                        'game': 'Irish Lotto',
                        'numbers': numbers,
                        'bonus': bonus,
                        'url': f"{BASE_URL}{href}"
                    })
                
                i += 7
                continue
        
        i += 1
    
    return draws

def parse_euro_archive(soup, year):
    """Parse EuroMillions archive page"""
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
                lucky_stars = []
                
                for j in range(1, 8):
                    if i + j < len(all_lis):
                        num_text = all_lis[i + j].get_text().strip()
                        if num_text.isdigit():
                            num = int(num_text)
                            if j <= 5 and len(numbers) < 5:
                                numbers.append(num)
                            elif len(lucky_stars) < 2:
                                lucky_stars.append(num)
                
                if len(numbers) == 5:
                    draws.append({
                        'date': date_str,
                        'game': 'EuroMillions',
                        'numbers': numbers,
                        'lucky_stars': lucky_stars,
                        'url': f"{BASE_URL}{href}"
                    })
                
                i += 7
                continue
        
        i += 1
    
    return draws

def scrape_years(game_type, years):
    """Scrape multiple years for a game"""
    all_draws = []
    
    for year in years:
        if game_type == 'irish':
            url = f"{BASE_URL}/irish-lotto-archive?year={year}"
        else:
            url = f"{BASE_URL}/euromillions-archive?year={year}"
        
        print(f"\nFetching {year}...")
        soup = fetch_page(url)
        
        if soup:
            if game_type == 'irish':
                draws = parse_irish_archive(soup, year)
            else:
                draws = parse_euro_archive(soup, year)
            
            print(f"  Found {len(draws)} draws")
            all_draws.extend(draws)
        else:
            print(f"  Failed")
        
        time.sleep(1)
    
    return all_draws

def save_data(draws, game_type):
    """Save to JSON"""
    if not draws:
        print(f"No data to save for {game_type}")
        return None
    
    draws.sort(key=lambda x: x['date'], reverse=True)
    
    if game_type == 'irish':
        metadata = {
            "game": "Irish Lotto",
            "format": "6/47 + Bonus",
            "draw_days": ["Wednesday", "Saturday"],
            "total_draws": len(draws),
            "date_range": f"{draws[-1]['date']} to {draws[0]['date']}",
            "scraped_at": datetime.now().isoformat()
        }
        filename = 'irish_lotto_historical.json'
    else:
        metadata = {
            "game": "EuroMillions",
            "format": "5/50 + 2/12 Lucky Stars",
            "draw_days": ["Tuesday", "Friday"],
            "total_draws": len(draws),
            "date_range": f"{draws[-1]['date']} to {draws[0]['date']}",
            "scraped_at": datetime.now().isoformat()
        }
        filename = 'euromillions_historical.json'
    
    output = {"metadata": metadata, "draws": draws}
    
    output_path = DATA_DIR / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n  Saved {len(draws)} draws to {filename}")
    return output_path

if __name__ == '__main__':
    print("="*60)
    print("LOTTERYVUE HISTORICAL SCRAPER - Phase 1")
    print("="*60)
    print("Scraping numbers for 2020-2026")
    print("Jackpot details will be Phase 2")
    print("="*60)
    
    years = list(range(2026, 2019, -1))
    
    # Irish Lotto
    print("\n" + "-"*60)
    print("IRISH LOTTO")
    print("-"*60)
    irish_draws = scrape_years('irish', years)
    save_data(irish_draws, 'irish')
    
    # EuroMillions
    print("\n" + "-"*60)
    print("EUROMILLIONS")
    print("-"*60)
    euro_draws = scrape_years('euro', years)
    save_data(euro_draws, 'euro')
    
    print("\n" + "="*60)
    print("PHASE 1 COMPLETE")
    print("="*60)
    print(f"Irish Lotto: {len(irish_draws)} draws")
    print(f"EuroMillions: {len(euro_draws)} draws")
    
    # Summary
    total_draws = len(irish_draws) + len(euro_draws)
    print(f"\nTotal: {total_draws} draws collected")
    print(f"Estimated time saved: {total_draws * 0.5 / 60:.1f} minutes (vs individual page scraping)")
