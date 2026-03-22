import pandas as pd
import numpy as np
import json
from pathlib import Path

INPUT_DIR = Path("C:/Users/impro/Documents/MedTech Intell/Market Intel")
OUTPUT_DIR = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/dashboard/data")

# Extract Portfolio Analysis file
print("=== Extracting Portfolio Analysis ===")
try:
    portfolio_file = INPUT_DIR / "Devices" / "2024-6-4 portfolio analysis - AWr.xlsx"
    xls = pd.ExcelFile(portfolio_file)
    print(f"Sheets: {xls.sheet_names}")
    
    portfolio_data = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(portfolio_file, sheet_name=sheet)
        df_clean = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        records = df_clean.to_dict('records')
        portfolio_data[sheet] = records
        print(f"  {sheet}: {len(records)} rows")
        if records:
            print(f"    Columns: {list(records[0].keys())[:8]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Extracting ROOT Product List ===")
try:
    root_file = INPUT_DIR / "Devices" / "ROOT - STANDARD LIST FOR MODELING- 2 APR 2025.xlsx"
    xls = pd.ExcelFile(root_file)
    print(f"Sheets: {xls.sheet_names}")
    
    root_data = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(root_file, sheet_name=sheet)
        df_clean = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        records = df_clean.to_dict('records')
        root_data[sheet] = records
        print(f"  {sheet}: {len(records)} rows")
        if records:
            print(f"    Columns: {list(records[0].keys())[:8]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Extracting Upstream Marketing ===")
try:
    upstream_file = INPUT_DIR / "Devices" / "Upstream Marketing Ideas & Trends.xlsx"
    xls = pd.ExcelFile(upstream_file)
    print(f"Sheets: {xls.sheet_names}")
    
    upstream_data = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(upstream_file, sheet_name=sheet)
        df_clean = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        records = df_clean.to_dict('records')
        upstream_data[sheet] = records
        print(f"  {sheet}: {len(records)} rows")
        if records:
            print(f"    Columns: {list(records[0].keys())[:8]}")
except Exception as e:
    print(f"Error: {e}")

# Save combined data
combined_data = {
    "portfolio_analysis": portfolio_data,
    "root_products": root_data,
    "upstream_marketing": upstream_data
}

output_file = OUTPUT_DIR / "product-portfolio-data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, indent=2, ensure_ascii=False, default=str)

print(f"\n=== Saved to: {output_file} ===")
