import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

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
            # Clean data - replace NaN with None for JSON
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

# Save consolidated data
output_file = OUTPUT_DIR / "revenue-data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(revenue_data, f, indent=2, ensure_ascii=False, default=str)

print(f"\nRevenue data saved to: {output_file}")

# Also create a parsed/structured version for visualization
print("\nCreating structured revenue dataset...")

structured_data = {
    "companies": [],
    "products": [],
    "disease_segments": [],
    "revenue_by_year": [],
    "market_share": []
}

# Parse MedTech Europe 2024 file (likely has overall market data)
if "medtech_europe_2024" in revenue_data and "sheets" in revenue_data["medtech_europe_2024"]:
    sheets = revenue_data["medtech_europe_2024"]["sheets"]
    for sheet_name, records in sheets.items():
        print(f"  Sheet: {sheet_name} ({len(records)} rows)")
        # Look for company names and revenue data
        for record in records[:5]:  # Preview first 5 rows
            print(f"    {record}")

# Parse Revenue by Companies files
for key in ["revenue_companies_apr", "revenue_companies_aug"]:
    if key in revenue_data and "sheets" in revenue_data[key]:
        sheets = revenue_data[key]["sheets"]
        for sheet_name, records in sheets.items():
            print(f"\n  {key} - Sheet: {sheet_name} ({len(records)} rows)")
            for record in records[:3]:
                print(f"    {record}")

# Parse Market Share file
if "market_share_companies" in revenue_data and "sheets" in revenue_data["market_share_companies"]:
    sheets = revenue_data["market_share_companies"]["sheets"]
    for sheet_name, records in sheets.items():
        print(f"\n  Market Share - Sheet: {sheet_name} ({len(records)} rows)")
        for record in records[:3]:
            print(f"    {record}")

print("\n✓ Extraction complete!")
