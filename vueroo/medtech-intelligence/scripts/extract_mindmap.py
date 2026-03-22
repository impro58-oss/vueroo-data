#!/usr/bin/env python3
"""
Extract company and product data from Competition Optic mind map HTML
This handles large mind map export files from Mindomo
"""

import json
import re
from pathlib import Path

def extract_from_mindmap():
    input_file = Path("C:/Users/impro/Downloads/Competition Optic - rw-v01.html")
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        return None
    
    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find all text between quotes that might be company/product names
    # Look for patterns in the mind map data
    
    results = {
        'source_file': str(input_file),
        'companies': [],
        'urls': [],
        'products': [],
        'text_snippets': []
    }
    
    # Extract URL patterns
    url_pattern = r'https?://[^\s"<>{}|\\^`\[\]]+[^\s"<>{}|\\^`\[\]\.,;!?]'
    urls = re.findall(url_pattern, content)
    results['urls'] = list(set(urls))[:100]  # Get unique URLs, limit to 100
    
    # Look for company names in text
    company_keywords = [
        'Medtronic', 'Stryker', 'Penumbra', 'MicroVention', 'Terumo',
        'Cerenovus', 'Johnson', 'Balt', 'Phenox', 'Wallaby',
        'J\u0026J', 'JNJ', 'Abbott', 'Boston Scientific', 'Integra',
        'Rapid Medical', 'Perflow', 'Siemens', 'Philips', 'GE',
        'Kaneka', 'Medico', 'Surpass', 'Streamline',
        'pCONUS', 'pEGASUS', 'Avenir', 'PICO', 'FRED', 
        'Pipeline', 'Solitaire', 'Trevo', 'Embotrap', 'Galaxy',
        'Axium', 'Target', 'LVIS', 'Scepter', 'Enterprise',
        'ACE', 'Lightning', '3D', 'Smart', 'Optima', 'Leo',
        'Coil', 'Stent', 'Catheter', 'Balloon', 'Diverter',
        'aneurysm', 'stroke', 'ischemic', 'hemorrhagic',
        'coil', 'flow diverter', 'stent retriever', 'aspiration'
    ]
    
    # Search for company/product keywords in the raw text
    found_items = set()
    text_lower = content.lower()
    
    for keyword in company_keywords:
        if keyword.lower() in text_lower:
            # Find context around the match
            pattern = re.compile(r'.{0,30}' + re.escape(keyword) + r'.{0,30}', re.IGNORECASE)
            matches = pattern.findall(content)
            found_items.add(keyword)
            results['text_snippets'].append({
                'keyword': keyword,
                'contexts': matches[:3]
            })
    
    results['companies'] = list(found_items)
    
    # Extract product-like patterns (capitalized words)
    # Look for standalone words that might be products
    product_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
    potential_products = re.findall(product_pattern, content)
    # Filter for likely medical device products
    medical_terms = [p for p in potential_products if len(p) > 2 and len(p) < 40]
    results['products'] = list(set(medical_terms))[:200]
    
    # Save results
    output_path = Path(__file__).parent.parent / 'dashboard' / 'data' / 'competition-optic-extracted.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Extraction complete!")
    print(f"Found {len(results['companies'])} keywords")
    print(f"Found {len(results['urls'])} URLs")
    print(f"Found {len(results['products'])} potential products/terms")
    print(f"Saved to: {output_path}")
    
    # Print summary
    print("\n=== COMPANIES/KEYWORDS FOUND ===")
    for company in sorted(results['companies'])[:30]:
        print(f"  - {company}")
    
    print("\n=== URLs FOUND ===")
    for url in sorted(results['urls'])[:20]:
        print(f"  - {url}")
    
    return results

if __name__ == '__main__':
    extract_from_mindmap()
