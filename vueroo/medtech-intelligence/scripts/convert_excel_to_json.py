import pandas as pd
import numpy as np
import json
from pathlib import Path

# Input/Output paths
INPUT_DIR = Path("C:/Users/impro/Documents/MedTech Intell/Market Intel/Epidemiological")
OUTPUT_DIR = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/dashboard/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def process_excel_file(filepath):
    """Extract data from Excel files"""
    try:
        # Read all sheets
        xls = pd.ExcelFile(filepath)
        data = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            # Convert to records, handling NaN values properly for JSON
            df_clean = df.replace({np.nan: None, np.inf: None, -np.inf: None})
            records = df_clean.to_dict('records')
            data[sheet_name] = records
        
        return data
    except Exception as e:
        return {"error": str(e)}

# Process files
files = [
    ("DM_Aneurysm_GL_A_20250211.xlsx", "aneurysm"),
    ("Epidemiological model aSAH__updated_18_6_24.xlsx", "asah_model"),
    ("Epidemiology of stroke and EVT in EU_April2023.xlsx", "eu_evt")
]

epidemiological_data = {}

for filename, key in files:
    filepath = INPUT_DIR / filename
    if filepath.exists():
        print(f"Processing: {filename}")
        epidemiological_data[key] = process_excel_file(filepath)
    else:
        print(f"Not found: {filename}")
        epidemiological_data[key] = {"error": "File not found"}

# Save consolidated data
output_file = OUTPUT_DIR / "epidemiological-data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(epidemiological_data, f, indent=2, ensure_ascii=False, default=str)

print(f"\nData saved to: {output_file}")

# Also create a master data file that merges with stroke intelligence
print("\nCreating master data file...")

# Load existing stroke intelligence
try:
    with open(OUTPUT_DIR / "stroke-intelligence.json", 'r', encoding='utf-8') as f:
        stroke_intel = json.load(f)
except:
    stroke_intel = {"regions": {}}

# Merge new epidemiological data
master_data = {
    "version": "1.1",
    "lastUpdated": "2026-03-18",
    "global": stroke_intel.get("global", {}),
    "regions": stroke_intel.get("regions", {}),
    "epidemiologicalModels": epidemiological_data,
    "sources": [
        "Tu et al. 2023 - China Stroke Surveillance",
        "Ungerer et al. 2024 - German Stroke Care",
        "Wada et al. 2023 - Japan Stroke Data Bank",
        "SAFE 2017 - Burden of Stroke in Europe",
        "AHA 2024 - US Stroke Statistics",
        "Epidemiological Excel Models"
    ]
}

master_file = OUTPUT_DIR / "master-data.json"
with open(master_file, 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=2, ensure_ascii=False)

print(f"Master data saved to: {master_file}")
