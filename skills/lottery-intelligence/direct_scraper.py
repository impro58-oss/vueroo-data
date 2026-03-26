"""
LotteryVue — Archive Page Direct Scraper
Extracts numbers directly from archive list pages without visiting individual draws.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional

# Configuration
BASE_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace\\skills\\lottery-intelligence")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.irishlottery.com"


class DirectArchiveScraper:
    """Scraper that extracts directly from archive pages."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.irish_data = []
        self.euromillions_data = []
    
    def fetch_archive_page(self, year: int, game: str) -> Optional[BeautifulSoup]:
        """Fetch archive page for a year."""
        try:
            if game == 'irish':
                url = f"{BASE_URL}/archive?year={year}"
            else:
                url = f"{BASE_URL}/euromillions-archive?year={year}"
            
            print(f"Fetching {url}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {year}: {e}")
            return None
    
    def parse_irish_archive(self, soup: BeautifulSoup, year: int) -> List[Dict]:
        """Parse Irish Lotto archive page."""
        draws = []
        
        try:
            # Find all result entries - they're in divs or lis with result info
            # Each result shows: Date, then 6 numbers, then bonus
            
            # Look for the result containers
            results = soup.find_all(['div', 'li', 'tr'], class_=re.compile('result|draw', re.I))
            
            print(f"Found {len(results)} potential result containers")
            
            # Alternative: look for date links followed by numbers
            date_links = soup.find_all('a', href=re.compile(r'/results/irish-lotto-result-'))
            
            for link in date_links:
                try:
                    # Get date from URL
                    url = link.get('href', '')
                    date_match = re.search(r'result-(\d{2})-(\d{2})-(\d{4})', url)
                    if not date_match:
                        continue
                    
                    day, month, year_str = date_match.groups()
                    date_str = f"{year_str}-{month}-{day}"
                    
                    # Find numbers in the parent container
                    parent = link.find_parent(['div', 'li', 'tr'])
                    if not parent:
                        continue
                    
                    # Look for number elements
                    nums = []
                    bonus = None
                    
                    # Try different selectors
                    num_elems = parent.find_all('li', class_=re.compile(r'ball', re.I))
                    if not num_elems:
                        num_elems = parent.find_all(['span', 'div'], class_=re.compile(r'ball|number', re.I))
                    
                    for i, elem in enumerate(num_elems[:7]):
                        text = elem.get_text().strip()
                        if text.isdigit():
                            if i < 6:
                                nums.append(int(text))
                            else:
                                bonus = int(text)
                    
                    if len(nums) == 6:
                        draws.append({
                            'date': date_str,
                            'game': 'Irish Lotto',
                            'numbers': nums,
                            'bonus': bonus,
                            'url': f"{BASE_URL}{url}" if not url.startswith('http') else url
                        })
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Parse error for Irish {year}: {e}")
        
        return draws
    
    def parse_euromillions_archive(self, soup: BeautifulSoup, year: int) -> List[Dict]:
        """Parse EuroMillions archive page."""
        draws = []
        
        try:
            date_links = soup.find_all('a', href=re.compile(r'/results/euromillions-result-'))
            
            for link in date_links:
                try:
                    url = link.get('href', '')
                    date_match = re.search(r'result-(\d{2})-(\d{2})-(\d{4})', url)
                    if not date_match:
                        continue
                    
                    day, month, year_str = date_match.groups()
                    date_str = f"{year_str}-{month}-{day}"
                    
                    parent = link.find_parent(['div', 'li', 'tr'])
                    if not parent:
                        continue
                    
                    nums = []
                    lucky_stars = []
                    
                    num_elems = parent.find_all('li', class_=re.compile(r'ball', re.I))
                    if not num_elems:
                        num_elems = parent.find_all(['span', 'div'], class_=re.compile(r'ball|number', re.I))
                    
                    for i, elem in enumerate(num_elems[:7]):
                        text = elem.get_text().strip()
                        if text.isdigit():
                            if i < 5:
                                nums.append(int(text))
                            else:
                                lucky_stars.append(int(text))
                    
                    if len(nums) == 5:
                        draws.append({
                            'date': date_str,
                            'game': 'EuroMillions',
                            'numbers': nums,
                            'lucky_stars': lucky_stars[:2],
                            'url': f"{BASE_URL}{url}" if not url.startswith('http') else url
                        })
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Parse error for EuroMillions {year}: {e}")
        
        return draws
    
    def run_scrape(self):
        """Run complete scrape."""
        print("="*60)
        print("LOTTERYVUE DIRECT ARCHIVE SCRAPER")
        print("="*60)
        
        # Irish Lotto: 1988-2026
        print("\nPHASE 1: Irish Lotto")
        print("-"*60)
        
        for year in range(2026, 1987, -1):
            soup = self.fetch_archive_page(year, 'irish')
            if soup:
                draws = self.parse_irish_archive(soup, year)
                self.irish_data.extend(draws)
                print(f"Year {year}: {len(draws)} draws extracted")
            time.sleep(1)
        
        print(f"\nTotal Irish Lotto draws: {len(self.irish_data)}")
        
        # EuroMillions: 2004-2026
        print("\nPHASE 2: EuroMillions")
        print("-"*60)
        
        for year in range(2026, 2003, -1):
            soup = self.fetch_archive_page(year, 'euromillions')
            if soup:
                draws = self.parse_euromillions_archive(soup, year)
                self.euromillions_data.extend(draws)
                print(f"Year {year}: {len(draws)} draws extracted")
            time.sleep(1)
        
        print(f"\nTotal EuroMillions draws: {len(self.euromillions_data)}")
        
        # Save
        self.save_databases()
    
    def save_databases(self):
        """Save to JSON files."""
        # Irish Lotto
        irish_db = {
            'metadata': {
                'game': 'Irish Lotto',
                'format': '6/47 + Bonus',
                'draw_days': ['Wednesday', 'Saturday'],
                'total_draws': len(self.irish_data),
                'scraped_at': datetime.now().isoformat()
            },
            'draws': sorted(self.irish_data, key=lambda x: x['date'], reverse=True)
        }
        
        with open(DATA_DIR / 'irish_lotto_db.json', 'w') as f:
            json.dump(irish_db, f, indent=2)
        
        # EuroMillions
        euro_db = {
            'metadata': {
                'game': 'EuroMillions',
                'format': '5/50 + 2/12 Lucky Stars',
                'draw_days': ['Tuesday', 'Friday'],
                'total_draws': len(self.euromillions_data),
                'scraped_at': datetime.now().isoformat()
            },
            'draws': sorted(self.euromillions_data, key=lambda x: x['date'], reverse=True)
        }
        
        with open(DATA_DIR / 'euromillions_db.json', 'w') as f:
            json.dump(euro_db, f, indent=2)
        
        print(f"\nDatabases saved to {DATA_DIR}")
        print(f"  - irish_lotto_db.json ({len(self.irish_data)} draws)")
        print(f"  - euromillions_db.json ({len(self.euromillions_data)} draws)")


if __name__ == '__main__':
    scraper = DirectArchiveScraper()
    scraper.run_scrape()
