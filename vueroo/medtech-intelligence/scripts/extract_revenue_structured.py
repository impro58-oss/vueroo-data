import pandas as pd
import numpy as np
import json
from pathlib import Path

# Input/Output paths
INPUT_DIR = Path("C:/Users/impro/Documents/MedTech Intell/Market Intel/Revnew")
OUTPUT_DIR = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/dashboard/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_revenue_data(filepath, file_key):
    """Extract revenue data from Excel files"""
    try:
        xls = pd.ExcelFile(filepath)
        data = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            df_clean = df.replace({np.nan: None, np.inf: None, -np.inf: None})
            records = df_clean.to_dict('records')
            data[sheet_name] = records
        
        return {"sheets": data, "filename": filepath.name}
    except Exception as e:
        return {"error": str(e), "filename": filepath.name}

# Process all revenue files
revenue_files = [
    ("GLOBAL MARKET - MedTech Europe 2024 - 21 MAR 2025.xlsx", "medtech_europe_2024"),
    ("GLOBAL MARKET - MKT SHARE - KEY COMPANIES - 28 MAR 2025.xlsx", "market_share_companies"),
    ("GLOBAL MARKET - REVENUE - KEY COMPANIES - 10 APR 2025.xlsx", "revenue_companies_apr"),
    ("GLOBAL MARKET - REVENUE - KEY COMPANIES - 26 Aug 2025.xlsx", "revenue_companies_aug")
]

revenue_data = {}

for filename, key in revenue_files:
    filepath = INPUT_DIR / filename
    if filepath.exists():
        print(f"Processing: {filename}")
        revenue_data[key] = extract_revenue_data(filepath, key)
    else:
        print(f"Not found: {filename}")
        revenue_data[key] = {"error": "File not found"}

# Save raw data
output_file = OUTPUT_DIR / "revenue-data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(revenue_data, f, indent=2, ensure_ascii=False, default=str)

print(f"\nRaw revenue data saved to: {output_file}")

# Now create a structured/cleaned version
print("\n=== Creating structured revenue dataset ===")

structured_records = []

# Company mapping
company_names = {
    'MDT NV': 'Medtronic',
    'MDT': 'Medtronic',
    'SYK NV': 'Stryker',
    'SYK': 'Stryker',
    'MicroVention': 'MicroVention',
    'MV': 'MicroVention',
    'Penumbra': 'Penumbra',
    'PEN': 'Penumbra',
    'JNJ': 'Johnson & Johnson',
    'ACDS': 'Acandis',
    'BALT': 'Balt',
    'ZOOM': 'Zoom'
}

# Parse Jie's sheet
if "revenue_companies_aug" in revenue_data and "sheets" in revenue_data["revenue_companies_aug"]:
    sheets = revenue_data["revenue_companies_aug"]["sheets"]
    
    if "Jie's" in sheets:
        jie_sheet = sheets["Jie's"]
        print(f"Processing Jie's sheet ({len(jie_sheet)} rows)")
        
        for row in jie_sheet[2:]:
            company_code = row.get('Unnamed: 1')
            if not company_code or company_code == 'Tab.3 Key Companies':
                continue
            
            company_name = company_names.get(company_code, company_code)
            highlight = row.get('Unnamed: 2')
            
            year_cols = {
                2016: 'Unnamed: 5', 2017: 'Unnamed: 6', 2018: 'Unnamed: 7', 2019: 'Unnamed: 8',
                2020: 'Unnamed: 9', 2021: 'Unnamed: 10', 2022: 'Unnamed: 11',
                2023: 'Unnamed: 13', 2024: 'Unnamed: 15', 2025: 'Unnamed: 17',
                2026: 'Unnamed: 18', 2027: 'Unnamed: 19', 2028: 'Unnamed: 20',
                2029: 'Unnamed: 21', 2030: 'Unnamed: 22'
            }
            
            for year, col in year_cols.items():
                revenue = row.get(col)
                if revenue and isinstance(revenue, (int, float)) and revenue > 0:
                    structured_records.append({
                        "company": company_name,
                        "companyCode": company_code,
                        "year": year,
                        "revenue": float(revenue),
                        "revenueFormatted": f"${revenue/1000000:.1f}M" if revenue > 1000000 else f"${revenue/1000:.1f}K",
                        "highlight": highlight,
                        "type": "company_revenue",
                        "source": "Jie's Analysis"
                    })
        
        print(f"  Extracted {len([r for r in structured_records if r['type'] == 'company_revenue'])} company revenue records")

# Save structured data
structured_file = OUTPUT_DIR / "revenue-structured.json"
with open(structured_file, 'w', encoding='utf-8') as f:
    json.dump({
        "metadata": {
            "totalRecords": len(structured_records),
            "companies": len(set(r["company"] for r in structured_records if r.get("company"))),
            "yearRange": {
                "min": min(r["year"] for r in structured_records if r.get("year")),
                "max": max(r["year"] for r in structured_records if r.get("year"))
            }
        },
        "records": structured_records
    }, f, indent=2, ensure_ascii=False)

print(f"\nStructured data saved to: {structured_file}")
print(f"Total records: {len(structured_records)}")

# Print sample
print("\nSample records:")
for r in structured_records[:5]:
    print(f"  {r}")
