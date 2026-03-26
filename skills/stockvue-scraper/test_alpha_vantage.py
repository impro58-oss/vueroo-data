"""
Quick test for Alpha Vantage API key and connection.
Run this to verify your key works.
"""
import os
import sys
from pathlib import Path
import requests

# Get API key
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY') or Path.home().joinpath('.openclaw/.config/alphavantage/api_key').read_text().strip()

if not API_KEY:
    print("ERROR: ALPHA_VANTAGE_API_KEY not set")
    print("Set it as environment variable or in ~/.openclaw/.config/alphavantage/api_key")
    sys.exit(1)

print(f"Testing Alpha Vantage API...")
print(f"API Key: {API_KEY[:4]}...{API_KEY[-4:]}")
print("")

# Test 1: Simple price quote
print("Test 1: Getting IBM daily prices...")
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey={API_KEY}"

response = requests.get(url, timeout=30)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    if 'Time Series (Daily)' in data:
        dates = list(data['Time Series (Daily)'].keys())[:3]
        print(f"[SUCCESS] Got {len(data['Time Series (Daily)'])} days of data")
        print(f"Latest dates: {dates}")
        
        latest = data['Time Series (Daily)'][dates[0]]
        print(f"Latest price: ${latest['4. close']}")
        print("")
        print("API is working! You can now run the scanner.")
        sys.exit(0)
    elif 'Note' in data:
        print(f"⚠️ Rate limit: {data['Note']}")
        print("Wait a minute and try again")
        sys.exit(1)
    elif 'Error Message' in data:
        print(f"❌ API Error: {data['Error Message']}")
        sys.exit(1)
    else:
        print(f"❌ Unexpected response: {data}")
        sys.exit(1)
else:
    print(f"❌ HTTP Error: {response.status_code}")
    sys.exit(1)
