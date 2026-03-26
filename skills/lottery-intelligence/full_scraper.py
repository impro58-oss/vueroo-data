"""
LotteryVue — Full Historical Data Scraper
Scrapes all Irish Lotto and EuroMillions draws from irishlottery.com
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional, Tuple
import sys

# Configuration
BASE_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace\\skills\\lottery-intelligence")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.irishlottery.com"
LOG_FILE = DATA_DIR / "scrape_log.txt"

class LotteryScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.irish_data = []
        self.euromillions_data = []
        self.errors = []
        self.start_time = datetime.now()
        
        # Statistics
        self.stats = {
            'irish_draws_found': 0,
            'euro_draws_found': 0,
            'pages_fetched': 0,
            'errors': 0,
            'start_time': self.start_time.isoformat()
        }
    
    def log(self, message: str):
        """Log progress to console and file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        with open(LOG_FILE, 'a') as f:
            f.write(log_line + '\n')
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                self.stats['pages_fetched'] += 1
                return BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                if attempt == max_retries - 1:
                    self.log(f"ERROR: Failed to fetch {url}: {e}")
                    self.stats['errors'] += 1
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    def parse_draw_result(self, soup: BeautifulSoup, game_type: str) -> Optional[Dict]:
        """Parse a single draw result page."""
        try:
            # Extract date from URL or page
            canonical = soup.find('link', rel='canonical')
            url = canonical['href'] if canonical else ''
            
            # Parse date from URL pattern like .../irish-lotto-result-25-03-2026
            date_match = re.search(r'result-(\d{2})-(\d{2})-(\d{4})', url)
            if date_match:
                day, month, year = date_match.groups()
                date_str = f"{year}-{month}-{day}"
            else:
                # Try to find date in page content
                date_elem = soup.find(text=re.compile(r'\d{1,2}(st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'))
                date_str = None
            
            if not date_str:
                return None
            
            # Find all number balls
            number_elements = soup.find_all('li', class_=lambda x: x and 'ball' in x.lower() if x else False)
            
            if game_type == 'irish':
                # Irish Lotto: 6 main + 1 bonus
                numbers = []
                bonus = None
                
                for i, elem in enumerate(number_elements[:7]):
                    num_text = elem.get_text().strip()
                    if num_text.isdigit():
                        num = int(num_text)
                        if i < 6:
                            numbers.append(num)
                        else:
                            bonus = num
                
                if len(numbers) != 6:
                    return None
                
                # Extract jackpot
                jackpot = self.extract_jackpot(soup)
                
                return {
                    'date': date_str,
                    'game': 'Irish Lotto',
                    'numbers': numbers,
                    'bonus': bonus,
                    'jackpot_eur': jackpot,
                    'url': url
                }
                
            elif game_type == 'euromillions':
                # EuroMillions: 5 main + 2 lucky stars
                numbers = []
                lucky_stars = []
                
                for i, elem in enumerate(number_elements[:7]):
                    num_text = elem.get_text().strip()
                    if num_text.isdigit():
                        num = int(num_text)
                        if i < 5:
                            numbers.append(num)
                        else:
                            lucky_stars.append(num)
                
                if len(numbers) != 5 or len(lucky_stars) != 2:
                    return None
                
                jackpot = self.extract_jackpot(soup)
                
                return {
                    'date': date_str,
                    'game': 'EuroMillions',
                    'numbers': numbers,
                    'lucky_stars': lucky_stars,
                    'jackpot_eur': jackpot,
                    'url': url
                }
                
        except Exception as e:
            self.log(f"Parse error: {e}")
            return None
    
    def extract_jackpot(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract jackpot amount from page."""
        try:
            # Look for jackpot text
            jackpot_text = soup.find(text=re.compile(r'Jackpot\s*:?\s*€', re.I))
            if jackpot_text:
                # Extract number
                match = re.search(r'€\s*([\d,.]+)\s*(Million)?', jackpot_text, re.I)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    multiplier = 1000000 if match.group(2) else 1
                    return int(float(amount_str) * multiplier)
            
            # Alternative: look for prize breakdown
            prize_elem = soup.find('td', text=re.compile(r'Jackpot'))
            if prize_elem:
                next_td = prize_elem.find_next('td')
                if next_td:
                    match = re.search(r'([\d,.]+)', next_td.get_text())
                    if match:
                        return int(match.group(1).replace(',', ''))
                        
        except Exception:
            pass
        return None
    
    def get_year_archive_url(self, year: int, game: str) -> str:
        """Build archive URL for a specific year."""
        if game == 'irish':
            return f"{BASE_URL}/archive?year={year}"
        else:
            return f"{BASE_URL}/euromillions-archive?year={year}"
    
    def scrape_year(self, year: int, game: str) -> List[Dict]:
        """Scrape all draws from a specific year."""
        self.log(f"Scraping {game} for year {year}...")
        
        url = self.get_year_archive_url(year, game)
        soup = self.fetch_page(url)
        
        if not soup:
            self.log(f"Failed to fetch {url}")
            return []
        
        draws = []
        
        # Find all draw result links
        result_links = soup.find_all('a', href=re.compile(r'/results/.*-result-\d{2}-\d{2}-\d{4}'))
        
        self.log(f"Found {len(result_links)} draw links for {year}")
        
        for link in result_links:
            try:
                draw_url = link['href']
                if not draw_url.startswith('http'):
                    draw_url = BASE_URL + draw_url
                
                # Fetch draw page
                draw_soup = self.fetch_page(draw_url)
                if not draw_soup:
                    continue
                
                # Parse result
                result = self.parse_draw_result(draw_soup, game)
                if result:
                    draws.append(result)
                    if game == 'irish':
                        self.stats['irish_draws_found'] += 1
                    else:
                        self.stats['euro_draws_found'] += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                self.log(f"Error processing draw: {e}")
                continue
        
        self.log(f"Scraped {len(draws)} draws from {year}")
        return draws
    
    def run_full_scrape(self):
        """Run complete historical scrape."""
        self.log("="*60)
        self.log("LOTTERYVUE FULL HISTORICAL SCRAPE")
        self.log("="*60)
        self.log(f"Started: {self.start_time}")
        self.log("")
        
        # Irish Lotto: 1988-2026
        self.log("PHASE 1: Irish Lotto (1988-2026)")
        self.log("-"*60)
        
        for year in range(2026, 1987, -1):  # Reverse chronological
            year_draws = self.scrape_year(year, 'irish')
            self.irish_data.extend(year_draws)
            self.save_progress()
            
            # Progress update
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.log(f"Year {year} complete. Total Irish draws: {len(self.irish_data)}")
            self.log(f"Elapsed: {elapsed/60:.1f} minutes")
            self.log("")
        
        # EuroMillions: 2004-2026
        self.log("PHASE 2: EuroMillions (2004-2026)")
        self.log("-"*60)
        
        for year in range(2026, 2003, -1):
            year_draws = self.scrape_year(year, 'euromillions')
            self.euromillions_data.extend(year_draws)
            self.save_progress()
            
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.log(f"Year {year} complete. Total Euro draws: {len(self.euromillions_data)}")
            self.log(f"Elapsed: {elapsed/60:.1f} minutes")
            self.log("")
        
        # Final save
        self.save_final_databases()
        
        # Summary
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.log("="*60)
        self.log("SCRAPING COMPLETE")
        self.log("="*60)
        self.log(f"Irish Lotto draws: {len(self.irish_data)}")
        self.log(f"EuroMillions draws: {len(self.euromillions_data)}")
        self.log(f"Total pages fetched: {self.stats['pages_fetched']}")
        self.log(f"Errors: {self.stats['errors']}")
        self.log(f"Total time: {elapsed/3600:.2f} hours")
        self.log("="*60)
    
    def save_progress(self):
        """Save intermediate progress."""
        progress = {
            'stats': self.stats,
            'irish_draws': len(self.irish_data),
            'euro_draws': len(self.euromillions_data),
            'last_save': datetime.now().isoformat()
        }
        
        with open(DATA_DIR / 'scrape_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
    
    def save_final_databases(self):
        """Save final databases."""
        # Irish Lotto
        irish_db = {
            'metadata': {
                'game': 'Irish Lotto',
                'format': '6/47 + Bonus',
                'draw_days': ['Wednesday', 'Saturday'],
                'start_date': '1988-04-16',
                'last_draw_date': self.irish_data[0]['date'] if self.irish_data else None,
                'total_draws': len(self.irish_data),
                'scraped_at': datetime.now().isoformat()
            },
            'draws': sorted(self.irish_data, key=lambda x: x['date'], reverse=True)
        }
        
        with open(DATA_DIR / 'irish_lotto_full_db.json', 'w') as f:
            json.dump(irish_db, f, indent=2)
        
        # EuroMillions
        euro_db = {
            'metadata': {
                'game': 'EuroMillions',
                'format': '5/50 + 2/12 Lucky Stars',
                'draw_days': ['Tuesday', 'Friday'],
                'start_date': '2004-02-13',
                'last_draw_date': self.euromillions_data[0]['date'] if self.euromillions_data else None,
                'total_draws': len(self.euromillions_data),
                'scraped_at': datetime.now().isoformat()
            },
            'draws': sorted(self.euromillions_data, key=lambda x: x['date'], reverse=True)
        }
        
        with open(DATA_DIR / 'euromillions_full_db.json', 'w') as f:
            json.dump(euro_db, f, indent=2)
        
        self.log(f"Databases saved to {DATA_DIR}")


if __name__ == '__main__':
    scraper = LotteryScraper()
    
    # Check for resume capability
    progress_file = DATA_DIR / 'scrape_progress.json'
    if progress_file.exists():
        with open(progress_file) as f:
            progress = json.load(f)
        print(f"Resuming from previous scrape...")
        print(f"Previously found: {progress['irish_draws']} Irish, {progress['euro_draws']} Euro draws")
    
    try:
        scraper.run_full_scrape()
    except KeyboardInterrupt:
        print("\nScrape interrupted. Progress saved.")
        scraper.save_progress()
        sys.exit(0)
