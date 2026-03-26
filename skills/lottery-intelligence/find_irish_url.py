import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# More URL patterns to test
urls = [
    "https://www.irishlottery.com/irish-lotto-results",
    "https://www.irishlottery.com/results/irish-lotto",
    "https://www.irishlottery.com/lotto/irish-lotto-results",
    "https://www.irishlottery.com/lotto-results",
    "https://www.irishlottery.com/archive/irish-lotto",
]

print("Finding Irish Lotto archive URL...")

for url in urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            print(f"OK: {url}")
            # Look for archive links
            soup = BeautifulSoup(r.text, 'html.parser')
            archive_links = soup.find_all('a', href=lambda x: x and 'archive' in x.lower())
            print(f"   Archive links: {len(archive_links)}")
            for link in archive_links[:3]:
                print(f"     - {link.get('href')}")
        else:
            print(f"{r.status_code}: {url}")
    except Exception as e:
        print(f"ERROR: {url} - {e}")
