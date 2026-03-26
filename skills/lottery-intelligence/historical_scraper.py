"""
Historical Lottery Data Scraper
Extracts complete draw data from 2020-2026 for Irish Lotto and EuroMillions
Includes: numbers, jackpot amounts, winner counts
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
DATA_DIR.mkdir(exist_ok=True)

# Headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def scrape_irish_lotto():
    """Scrape Irish Lotto data from 2020-2026"""
    print("="*60)
    print("SCRAPING IRISH LOTTO (2020-2026)")
    print("="*60)
    
    all_draws = []
    years = list(range(2026, 2019, -1))  # 2026 down to 2020
    
    for year in years:
        url = f"https://www.irishlottery.com/irish-lotto-archive?year={year}"
        print(f"\nFetching {year}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find draw links
            draw_links = []
            
            # Look for result links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'irish-lotto-result' in href and '/results/' in href:
                    full_url = href if href.startswith('http') else f"https://www.irishlottery.com{href}"
                    draw_links.append(full_url)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in draw_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            print(f"  Found {len(unique_links)} draws")
            
            # Extract draw data from archive page first (quick)
            year_draws = extract_draws_from_archive(soup, year)
            print(f"  Extracted {len(year_draws)} from archive")
            
            # Now visit each result page for jackpot details
            print(f"  Fetching jackpot details...")
            for i, draw in enumerate(year_draws):
                try:
                    if draw.get('url'):
                        jackpot_info = scrape_result_page(draw['url'], 'irish')
                        draw.update(jackpot_info)
                        
                        if (i + 1) % 10 == 0:
                            print(f"    Processed {i+1}/{len(year_draws)}...")
                        
                        time.sleep(0.3)  # Rate limiting
                except Exception as e:
                    print(f"    Error on draw {draw.get('date')}: {e}")
                    continue
            
            all_draws.extend(year_draws)
            print(f"  Total so far: {len(all_draws)} draws")
            
        except Exception as e:
            print(f"  Error fetching year {year}: {e}")
            continue
    
    # Sort by date
    all_draws.sort(key=lambda x: x['date'], reverse=True)
    
    # Save
    output = {
        "metadata": {
            "game": "Irish Lotto",
            "format": "6/47 + Bonus",
            "draw_days": ["Wednesday", "Saturday"],
            "total_draws": len(all_draws),
            "date_range": f"{all_draws[-1]['date']} to {all_draws[0]['date']}" if all_draws else "N/A",
            "scraped_at": datetime.now().isoformat()
        },
        "draws": all_draws
    }
    
    output_file = DATA_DIR / 'irish_lotto_historical.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(all_draws)} draws to irish_lotto_historical.json")
    return all_draws

def scrape_euromillions():
    """Scrape EuroMillions data from 2020-2026"""
    print("\n" + "="*60)
    print("SCRAPING EUROMILLIONS (2020-2026)")
    print("="*60)
    
    all_draws = []
    years = list(range(2026, 2019, -1))
    
    for year in years:
        url = f"https://www.irishlottery.com/euromillions-archive?year={year}"
        print(f"\nFetching {year}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract draws from archive
            year_draws = extract_euro_draws_from_archive(soup, year)
            print(f"  Extracted {len(year_draws)} from archive")
            
            # Fetch jackpot details
            print(f"  Fetching jackpot details...")
            for i, draw in enumerate(year_draws):
                try:
                    if draw.get('url'):
                        jackpot_info = scrape_result_page(draw['url'], 'euro')
                        draw.update(jackpot_info)
                        
                        if (i + 1) % 10 == 0:
                            print(f"    Processed {i+1}/{len(year_draws)}...")
                        
                        time.sleep(0.3)
                except Exception as e:
                    print(f"    Error on draw {draw.get('date')}: {e}")
                    continue
            
            all_draws.extend(year_draws)
            print(f"  Total so far: {len(all_draws)} draws")
            
        except Exception as e:
            print(f"  Error fetching year {year}: {e}")
            continue
    
    # Sort by date
    all_draws.sort(key=lambda x: x['date'], reverse=True)
    
    # Save
    output = {
        "metadata": {
            "game": "EuroMillions",
            "format": "5/50 + 2/12 Lucky Stars",
            "draw_days": ["Tuesday", "Friday"],
            "total_draws": len(all_draws),
            "date_range": f"{all_draws[-1]['date']} to {all_draws[0]['date']}" if all_draws else "N/A",
            "scraped_at": datetime.now().isoformat()
        },
        "draws": all_draws
    }
    
    output_file = DATA_DIR / 'euromillions_historical.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(all_draws)} draws to euromillions_historical.json")
    return all_draws

def extract_draws_from_archive(soup, year):
    """Extract Irish Lotto draws from archive page"""
    draws = []
    
    # Try to find draw entries
    # Look for list items or table rows containing date and numbers
    
    # Method 1: Look for links with dates
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'irish-lotto-result' in href:
            # Extract date from URL
            date_match = re.search(r'-(\d{2})-(\d{2})-(\d{4})', href)
            if date_match:
                day, month, year_str = date_match.groups()
                date_str = f"{year_str}-{month}-{day}"
                
                # Try to find numbers near this link
                parent = link.find_parent(['li', 'tr', 'div'])
                if parent:
                    numbers = extract_numbers_from_element(parent)
                    if len(numbers) >= 6:
                        draws.append({
                            "date": date_str,
                            "game": "Irish Lotto",
                            "numbers": numbers[:6],
                            "bonus": numbers[6] if len(numbers) > 6 else None,
                            "url": href if href.startswith('http') else f"https://www.irishlottery.com{href}"
                        })
    
    return draws

def extract_euro_draws_from_archive(soup, year):
    """Extract EuroMillions draws from archive page"""
    draws = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'euromillions-result' in href:
            date_match = re.search(r'-(\d{2})-(\d{2})-(\d{4})', href)
            if date_match:
                day, month, year_str = date_match.groups()
                date_str = f"{year_str}-{month}-{day}"
                
                parent = link.find_parent(['li', 'tr', 'div'])
                if parent:
                    numbers = extract_numbers_from_element(parent)
                    if len(numbers) >= 5:
                        draws.append({
                            "date": date_str,
                            "game": "EuroMillions",
                            "numbers": numbers[:5],
                            "lucky_stars": numbers[5:7] if len(numbers) > 5 else [],
                            "url": href if href.startswith('http') else f"https://www.irishlottery.com{href}"
                        })
    
    return draws

def extract_numbers_from_element(element):
    """Extract numbers from HTML element"""
    numbers = []
    
    # Look for number balls or list items
    for num_elem in element.find_all(['span', 'li', 'div', 'td']):
        text = num_elem.get_text().strip()
        # Try to extract numbers
        if text.isdigit():
            num = int(text)
            if 1 <= num <= 50:  # Reasonable lottery number range
                numbers.append(num)
    
    return numbers

def scrape_result_page(url, game_type):
    """Scrape individual result page for jackpot and winner info"""
    info = {
        "jackpot_amount": None,
        "jackpot_winners": 0,
        "total_winners": 0,
        "machine": None,
        "ball_set": None
    }
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for jackpot info in various formats
        text = soup.get_text()
        
        # Extract jackpot amount (look for € or Euro symbol followed by numbers)
        jackpot_match = re.search(r'[€\£\$]([\d,]+(?:\.\d{2})?)\s*(Million|Thousand)?', text, re.IGNORECASE)
        if jackpot_match:
            amount = jackpot_match.group(1).replace(',', '')
            unit = jackpot_match.group(2) or ''
            info["jackpot_amount"] = f"€{amount} {unit}".strip()
        
        # Extract winner counts
        winner_match = re.search(r'(\d+)\s+Jackpot\s+Winner', text, re.IGNORECASE)
        if winner_match:
            info["jackpot_winners"] = int(winner_match.group(1))
        
        # Look for total winners
        total_match = re.search(r'Total\s+Winners[:\s]+([\d,]+)', text, re.IGNORECASE)
        if total_match:
            info["total_winners"] = int(total_match.group(1).replace(',', ''))
        
        # Machine and ball set (often in draw details)
        machine_match = re.search(r'Machine[:\s]+(\w+)', text, re.IGNORECASE)
        if machine_match:
            info["machine"] = machine_match.group(1)
        
        ballset_match = re.search(r'Ball\s+Set[:\s]+(\w+)', text, re.IGNORECASE)
        if ballset_match:
            info["ball_set"] = ballset_match.group(1)
            
    except Exception as e:
        print(f"    Warning: Could not scrape result page {url}: {e}")
    
    return info

if __name__ == '__main__':
    print("="*60)
    print("LOTTERYVUE HISTORICAL DATA SCRAPER")
    print("="*60)
    print("\nThis will scrape Irish Lotto and EuroMillions data")
    print("from 2020-2026 including jackpot information.")
    print("\nEstimated time: 15-30 minutes")
    print("="*60)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    # Scrape both games
    irish_data = scrape_irish_lotto()
    euro_data = scrape_euromillions()
    
    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)
    print(f"\nIrish Lotto: {len(irish_data)} draws")
    print(f"EuroMillions: {len(euro_data)} draws")
    print(f"\nFiles saved to:")
    print(f"  - {DATA_DIR / 'irish_lotto_historical.json'}")
    print(f"  - {DATA_DIR / 'euromillions_historical.json'}")
