"""
Historical Lottery Data Scraper - Working Version
Uses the actual irishlottery.com structure
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from pathlib import Path
import re

BASE_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence")
DATA_DIR = BASE_DIR / "data"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def fetch_archive_page(url):
    """Fetch and parse archive page"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_irish_draws_from_archive(soup, year):
    """Extract Irish Lotto draws from archive page HTML"""
    draws = []
    
    # Find all result links - the working scraper found these patterns
    links = soup.find_all('a', href=re.compile(r'/results/irish-lotto-result-\d{2}-\d{2}-\d{4}'))
    
    for link in links:
        href = link.get('href')
        if not href:
            continue
            
        # Extract date from URL
        date_match = re.search(r'-(\d{2})-(\d{2})-(\d{4})', href)
        if not date_match:
            continue
            
        day, month, year_str = date_match.groups()
        date_str = f"{year_str}-{month}-{day}"
        
        # Get full URL
        full_url = href if href.startswith('http') else f"https://www.irishlottery.com{href}"
        
        # Try to find numbers near the link
        parent = link.find_parent(['li', 'div', 'tr'])
        numbers = []
        bonus = None
        
        if parent:
            # Look for number spans or list items
            for elem in parent.find_all(['span', 'li', 'div']):
                text = elem.get_text().strip()
                if text.isdigit():
                    num = int(text)
                    if 1 <= num <= 47 and num not in numbers:
                        numbers.append(num)
        
        if len(numbers) >= 6:
            draws.append({
                "date": date_str,
                "game": "Irish Lotto",
                "numbers": sorted(numbers[:6]),
                "bonus": numbers[6] if len(numbers) > 6 else None,
                "url": full_url
            })
    
    # Remove duplicates
    seen = {}
    unique = []
    for d in draws:
        key = d['date']
        if key not in seen:
            seen[key] = True
            unique.append(d)
    
    return unique

def extract_euro_draws_from_archive(soup, year):
    """Extract EuroMillions draws from archive page"""
    draws = []
    
    links = soup.find_all('a', href=re.compile(r'/results/euromillions-result-\d{2}-\d{2}-\d{4}'))
    
    for link in links:
        href = link.get('href')
        if not href:
            continue
            
        date_match = re.search(r'-(\d{2})-(\d{2})-(\d{4})', href)
        if not date_match:
            continue
            
        day, month, year_str = date_match.groups()
        date_str = f"{year_str}-{month}-{day}"
        
        full_url = href if href.startswith('http') else f"https://www.irishlottery.com{href}"
        
        parent = link.find_parent(['li', 'div', 'tr'])
        numbers = []
        
        if parent:
            for elem in parent.find_all(['span', 'li', 'div']):
                text = elem.get_text().strip()
                if text.isdigit():
                    num = int(text)
                    if 1 <= num <= 50 and num not in numbers:
                        numbers.append(num)
        
        if len(numbers) >= 5:
            draws.append({
                "date": date_str,
                "game": "EuroMillions",
                "numbers": sorted(numbers[:5]),
                "lucky_stars": sorted(numbers[5:7]) if len(numbers) > 5 else [],
                "url": full_url
            })
    
    seen = {}
    unique = []
    for d in draws:
        key = d['date']
        if key not in seen:
            seen[key] = True
            unique.append(d)
    
    return unique

def scrape_result_details(draw, game_type):
    """Scrape individual result page for jackpot and prize info"""
    url = draw.get('url')
    if not url:
        return draw
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract jackpot info from page text
        text = soup.get_text()
        
        # Jackpot amount - look for patterns like "Jackpot: €X" or "€X Million"
        jackpot_patterns = [
            r'Jackpot[:\s]+([€£$][\d,]+(?:\.\d+)?\s*(?:Million|Thousand)?)',
            r'([€£$][\d,]+(?:\.\d+)?)\s*(Million|m)?',
            r'Winning\s+Jackpot[:\s]+([\d,]+)',
        ]
        
        for pattern in jackpot_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                draw['jackpot_amount'] = match.group(1)
                break
        
        # Winner counts
        winner_match = re.search(r'(\d+)\s+Jackpot\s+Winner', text, re.IGNORECASE)
        if winner_match:
            draw['jackpot_winners'] = int(winner_match.group(1))
        
        # Total winners in all categories
        total_match = re.search(r'Total\s+Winners[:\s]+([\d,]+)', text, re.IGNORECASE)
        if total_match:
            draw['total_winners'] = int(total_match.group(1).replace(',', ''))
        
        # Prize breakdown table (if available)
        prize_table = soup.find('table', {'class': re.compile(r'prize|winner', re.I)})
        if prize_table:
            prizes = []
            for row in prize_table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    prizes.append({
                        'category': cells[0].get_text().strip(),
                        'winners': cells[1].get_text().strip(),
                        'prize': cells[2].get_text().strip()
                    })
            if prizes:
                draw['prize_breakdown'] = prizes
        
        time.sleep(0.5)  # Rate limiting
        
    except Exception as e:
        print(f"  Error scraping {url}: {e}")
    
    return draw

def scrape_game(game_type, years):
    """Scrape a lottery game for multiple years"""
    print(f"\n{'='*60}")
    print(f"SCRAPING {game_type.upper()} ({years[0]}-{years[-1]})")
    print(f"{'='*60}")
    
    all_draws = []
    base_url = "https://www.irishlottery.com"
    
    for year in years:
        if game_type == 'irish':
            url = f"{base_url}/irish-lotto-archive?year={year}"
        else:
            url = f"{base_url}/euromillions-archive?year={year}"
        
        print(f"\nFetching {year}...")
        soup = fetch_archive_page(url)
        
        if not soup:
            print(f"  Failed to load page")
            continue
        
        # Extract draws from archive
        if game_type == 'irish':
            year_draws = extract_irish_draws_from_archive(soup, year)
        else:
            year_draws = extract_euro_draws_from_archive(soup, year)
        
        print(f"  Found {len(year_draws)} draws in archive")
        
        if year_draws:
            print(f"  Fetching jackpot details for {len(year_draws)} draws...")
            
            for i, draw in enumerate(year_draws):
                if (i + 1) % 5 == 0:
                    print(f"    Processed {i+1}/{len(year_draws)}...")
                
                draw = scrape_result_details(draw, game_type)
                all_draws.append(draw)
        
        print(f"  Running total: {len(all_draws)} draws")
        time.sleep(1)  # Be nice to server
    
    # Sort by date
    all_draws.sort(key=lambda x: x['date'], reverse=True)
    
    return all_draws

def save_data(draws, game_type):
    """Save data to JSON file"""
    if game_type == 'irish':
        metadata = {
            "game": "Irish Lotto",
            "format": "6/47 + Bonus",
            "draw_days": ["Wednesday", "Saturday"],
            "total_draws": len(draws),
            "date_range": f"{draws[-1]['date']} to {draws[0]['date']}" if draws else "N/A",
            "scraped_at": datetime.now().isoformat()
        }
        filename = 'irish_lotto_historical.json'
    else:
        metadata = {
            "game": "EuroMillions",
            "format": "5/50 + 2/12 Lucky Stars",
            "draw_days": ["Tuesday", "Friday"],
            "total_draws": len(draws),
            "date_range": f"{draws[-1]['date']} to {draws[0]['date']}" if draws else "N/A",
            "scraped_at": datetime.now().isoformat()
        }
        filename = 'euromillions_historical.json'
    
    output = {"metadata": metadata, "draws": draws}
    
    output_path = DATA_DIR / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(draws)} draws to {filename}")
    return output_path

if __name__ == '__main__':
    print("="*60)
    print("LOTTERYVUE HISTORICAL DATA SCRAPER")
    print("="*60)
    print("Scraping 2020-2026 with jackpot details")
    print("="*60)
    
    years = list(range(2026, 2019, -1))  # 2026, 2025, 2024, 2023, 2022, 2021, 2020
    
    # Scrape Irish Lotto
    irish_draws = scrape_game('irish', years)
    save_data(irish_draws, 'irish')
    
    # Scrape EuroMillions
    euro_draws = scrape_game('euro', years)
    save_data(euro_draws, 'euro')
    
    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)
    print(f"Irish Lotto: {len(irish_draws)} draws")
    print(f"EuroMillions: {len(euro_draws)} draws")
    print(f"\nFiles saved to {DATA_DIR}")
