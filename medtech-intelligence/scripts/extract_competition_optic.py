#!/usr/bin/env python3
"""
Extract company and product data from Competition Optic mind map HTML
"""

from bs4 import BeautifulSoup
import json
import re
from pathlib import Path

def extract_from_competition_optic():
    input_file = Path("C:/Users/impro/Downloads/Competition Optic - rw-v01.html")
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        return None
    
    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract all text
    text = soup.get_text()
    
    # Look for company patterns
    companies_found = {}
    
    # Major competitors to look for
    target_companies = [
        'Medtronic', 'Stryker', 'Penumbra', 'MicroVention', 'Terumo',
        'Cerenovus', 'Johnson', 'Balt', 'Phenox', 'Wallaby',
        'J\u0026J', 'JNJ', 'Johnson \u0026 Johnson',
        'Target', 'Axium', 'Pipeline', 'Solitaire', 'Trevo',
        'Axium Prime', 'Axium MicroFX', 'Galaxy', 'Embotrap',
        'pCONUS', 'pEGASUS', 'Avenir', 'FRED', 'LVIS', 'Scepter',
        'ACE', 'Lightning', '3D Revascularization', 'Smart Coil',
        'Neuroform', 'Enterprise', 'Leo', 'Optima', 'Eclipse'
    ]
    
    for company in target_companies:
        if company.lower() in text.lower():
            # Find context around the company name
            pattern = re.compile(r'.{0,50}' + re.escape(company) + r'.{0,100}', re.IGNORECASE)
            matches = pattern.findall(text)
            companies_found[company] = {
                'mentions': len(matches),
                'context': matches[:3]  # First 3 contexts
            }
    
    # Extract URLs
    urls = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text_content = link.get_text(strip=True)
        if href.startswith('http') and len(text_content) < 100:
            urls.append({
                'url': href,
                'text': text_content
            })
    
    # Extract product names (capitalized words that might be products)
    product_patterns = re.findall(r'\b[A-Z][a-zA-Z]+\s+(?:Coil|Stent|Catheter|Balloon|Diverter|Retriever|Pump|Device)\b', text)
    products = list(set(product_patterns))
    
    # Create output
    output = {
        'source_file': str(input_file),
        'companies_mentioned': companies_found,
        'urls_found': urls[:50],  # Limit to first 50
        'potential_products': products[:100],
        'total_text_length': len(text)
    }
    
    # Save to JSON
    output_path = Path(__file__).parent.parent / 'dashboard' / 'data' / 'competition-optic-extracted.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Extraction complete!")
    print(f"Found {len(companies_found)} companies")
    print(f"Found {len(urls)} URLs")
    print(f"Found {len(products)} potential products")
    print(f"Saved to: {output_path}")
    
    return output

if __name__ == '__main__':
    extract_from_competition_optic()
