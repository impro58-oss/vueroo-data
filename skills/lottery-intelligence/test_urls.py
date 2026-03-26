import requests
from bs4 import BeautifulSoup
import sys

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test URLs
print("Testing URLs...")

urls = [
    ("Irish", "https://www.irishlottery.com/irish-lotto-archive?year=2026"),
    ("Irish", "https://www.irishlottery.com/irish-lotto-archive"),
    ("Euro", "https://www.irishlottery.com/euromillions-archive?year=2026"),
    ("Euro", "https://www.irishlottery.com/euromillions-archive"),
]

for name, url in urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            pattern = 'irish-lotto-result' if name == 'Irish' else 'euromillions-result'
            links = soup.find_all('a', href=lambda x: x and pattern in x)
            print(f"OK: {name} - {url}")
            print(f"   Found {len(links)} result links")
        else:
            print(f"FAIL {r.status_code}: {name} - {url}")
    except Exception as e:
        print(f"ERROR: {name} - {url} - {e}")
