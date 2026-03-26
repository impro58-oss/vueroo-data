import requests
from bs4 import BeautifulSoup
import re

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = "https://www.irishlottery.com/euromillions-archive?year=2026"
r = requests.get(url, headers=HEADERS, timeout=30)
soup = BeautifulSoup(r.text, 'html.parser')

# Save HTML for inspection
with open('test_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify()[:5000])

print("Saved first 5000 chars of HTML to test_page.html")

# Find result links
links = soup.find_all('a', href=re.compile(r'euromillions-result'))
print(f"\nFound {len(links)} result links")

if links:
    print("\nFirst link:")
    print(links[0])
    print("\nParent:")
    print(links[0].parent)
    print("\nParent's parent:")
    print(links[0].parent.parent if links[0].parent else "None")

# Look for number patterns
import re
text = soup.get_text()
numbers = re.findall(r'\d{1,2}', text)
print(f"\nSample numbers in text: {numbers[:30]}")
