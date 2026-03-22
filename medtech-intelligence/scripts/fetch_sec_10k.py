import requests
import json
from pathlib import Path
from datetime import datetime

# SEC EDGAR API - Free public access
# https://www.sec.gov/edgar/sec-api-documentation

class SEC10KFetcher:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'MedTech Intelligence Research (your-email@example.com)'  # Required by SEC
        }
        
        # Major MedTech companies and their CIK numbers
        self.companies = {
            'MDT': {'name': 'Medtronic plc', 'cik': '0001613103'},
            'SYK': {'name': 'Stryker Corp', 'cik': '0000310764'},
            'JNJ': {'name': 'Johnson & Johnson', 'cik': '0000200406'},
            'ABT': {'name': 'Abbott Laboratories', 'cik': '0000001800'},
            'BAX': {'name': 'Baxter International', 'cik': '0000015667'},
            'BSX': {'name': 'Boston Scientific', 'cik': '0000885725'},
            'PEN': {'name': 'Penumbra Inc', 'cik': '0001168683'},
            'EW': {'name': 'Edwards Lifesciences', 'cik': '0001096325'},
            'ZBH': {'name': 'Zimmer Biomet', 'cik': '0001136869'},
            'GMED': {'name': 'Globus Medical', 'cik': '0001455631'}
        }
    
    def get_company_filings(self, cik):
        """Get recent filings for a company"""
        url = f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&output=json"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code} for CIK {cik}")
                return None
        except Exception as e:
            print(f"Error fetching {cik}: {e}")
            return None
    
    def get_submissions(self, cik):
        """Get submissions using newer SEC API"""
        # CIK must be 10 digits with leading zeros
        cik_padded = cik.zfill(10)
        url = f"{self.base_url}/submissions/CIK{cik_padded}.json"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code} for {url}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def fetch_all(self):
        """Fetch 10-K data for all tracked companies"""
        results = {}
        
        print("Fetching 10-K data from SEC EDGAR...")
        print("=" * 60)
        
        for ticker, info in self.companies.items():
            print(f"\nFetching {ticker} ({info['name']})...")
            
            data = self.get_submissions(info['cik'])
            
            if data:
                # Extract recent 10-K filings
                recent = data.get('filings', {}).get('recent', {})
                forms = recent.get('form', [])
                dates = recent.get('filingDate', [])
                accession = recent.get('accessionNumber', [])
                
                # Find 10-K filings
                ten_ks = []
                for i, form in enumerate(forms):
                    if form == '10-K':
                        ten_ks.append({
                            'form': form,
                            'date': dates[i] if i < len(dates) else None,
                            'accession': accession[i] if i < len(accession) else None
                        })
                
                results[ticker] = {
                    'name': info['name'],
                    'cik': info['cik'],
                    'recent_10k': ten_ks[:3],  # Last 3 10-Ks
                    'all_filings': len(forms)
                }
                
                print(f"  [OK] Found {len(ten_ks)} 10-K filings")
                for k in ten_ks[:2]:
                    print(f"    - {k['date']}: {k['accession']}")
            else:
                print(f"  [FAIL] Failed to fetch")
                results[ticker] = {'error': 'Failed to fetch'}
        
        return results

def main():
    fetcher = SEC10KFetcher()
    data = fetcher.fetch_all()
    
    # Save results
    output_dir = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/dashboard/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "sec-10k-data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'companies': data
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Data saved to: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Download actual 10-K filings using accession numbers")
    print(f"2. Extract revenue segments (neurovascular, etc.)")
    print(f"3. Parse XBRL data for structured financials")

if __name__ == '__main__':
    main()
