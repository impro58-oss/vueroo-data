import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

# Paths
INPUT_DIR = Path("C:/Users/impro/Documents/MedTech Intell/Market Intel/Epidemiological")
OUTPUT_DIR = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/dashboard/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("EXCEL DIAGNOSTIC - Checking file structure")
print("=" * 80)

excel_files = list(INPUT_DIR.glob("*.xlsx")) + list(INPUT_DIR.glob("*.xls"))

for filepath in excel_files:
    print(f"\n{'='*60}")
    print(f"File: {filepath.name}")
    print(f"{'='*60}")
    
    try:
        xls = pd.ExcelFile(filepath)
        print(f"Sheets found: {xls.sheet_names}")
        
        for sheet in xls.sheet_names[:3]:  # Check first 3 sheets
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(filepath, sheet_name=sheet)
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)[:10]}")  # First 10 columns
            if not df.empty:
                print(f"First few rows:")
                print(df.head(3).to_string())
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("Now extracting comprehensively...")
print("=" * 80)

def parse_date_from_filename(filename):
    patterns = [
        r'(\d{4})(\d{2})(\d{2})',
        r'(\d{4})',
        r'(\d{1,2})[_-](\d{1,2})[_-](\d{2,4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                year = groups[0] if len(groups[0]) == 4 else '20' + groups[0]
                month = groups[1].zfill(2)
                day = groups[2].zfill(2) if len(groups[2]) <= 2 else groups[2][-2:].zfill(2)
                return {'year': int(year), 'month': int(month), 'day': int(day), 'full': f"{year}-{month}-{day}"}
            elif len(groups) == 1:
                year = groups[0]
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                return {'year': int(year), 'month': None, 'day': None, 'full': year}
    return {'year': None, 'month': None, 'day': None, 'full': None}

def clean_dataframe(df):
    df = df.dropna(how='all').dropna(axis=1, how='all')
    df.columns = [str(col).strip().replace('\n', ' ').replace('  ', ' ') for col in df.columns]
    return df

def infer_region(filename):
    filename_lower = filename.lower()
    if 'eu' in filename_lower or 'europe' in filename_lower:
        return 'eu'
    elif 'china' in filename_lower or 'cn' in filename_lower:
        return 'china'
    elif 'germany' in filename_lower:
        return 'germany'
    elif 'japan' in filename_lower:
        return 'japan'
    elif 'usa' in filename_lower or 'us' in filename_lower:
        return 'usa'
    elif 'global' in filename_lower or 'world' in filename_lower:
        return 'global'
    elif 'asah' in filename_lower:
        return 'asah'
    elif 'aneurysm' in filename_lower:
        return 'aneurysm'
    return 'unspecified'

# Comprehensive extraction
all_data = {
    'metadata': {
        'extractionDate': datetime.now().isoformat(),
        'filesProcessed': len(excel_files),
        'totalRecords': 0
    },
    'datasets': {}
}

for filepath in excel_files:
    file_key = filepath.stem
    file_date = parse_date_from_filename(filepath.name)
    region = infer_region(filepath.name)
    
    print(f"\nProcessing: {filepath.name}")
    print(f"  Date: {file_date}")
    print(f"  Region: {region}")
    
    try:
        xls = pd.ExcelFile(filepath)
        file_data = {
            'filename': filepath.name,
            'fileDate': file_date,
            'region': region,
            'sheets': {}
        }
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            df = clean_dataframe(df)
            
            if df.empty:
                continue
            
            # Convert to clean records
            records = []
            for idx, row in df.iterrows():
                record = {'_rowIndex': idx}
                for col in df.columns:
                    val = row[col]
                    if pd.isna(val):
                        record[str(col)] = None
                    else:
                        # Try to convert to appropriate type
                        try:
                            if isinstance(val, (int, float)):
                                record[str(col)] = val
                            else:
                                record[str(col)] = str(val)
                        except:
                            record[str(col)] = str(val)
                record['_fileDate'] = file_date['full']
                record['_fileYear'] = file_date['year']
                record['_region'] = region
                records.append(record)
            
            file_data['sheets'][sheet_name] = {
                'shape': {'rows': len(df), 'cols': len(df.columns)},
                'columns': list(df.columns),
                'data': records
            }
            all_data['metadata']['totalRecords'] += len(records)
            print(f"  Sheet '{sheet_name}': {len(records)} records")
        
        all_data['datasets'][file_key] = file_data
        
    except Exception as e:
        print(f"  ERROR: {e}")
        all_data['datasets'][file_key] = {'error': str(e)}

# Create time-series view
time_series = {}
for file_key, file_data in all_data['datasets'].items():
    if 'error' in file_data:
        continue
    
    region = file_data.get('region', 'unspecified')
    if region not in time_series:
        time_series[region] = []
    
    for sheet_name, sheet_data in file_data.get('sheets', {}).items():
        for record in sheet_data.get('data', []):
            enriched = {
                **record,
                '_sourceFile': file_data['filename'],
                '_sheetName': sheet_name
            }
            time_series[region].append(enriched)

all_data['timeSeries'] = time_series

# Summary
print(f"\n{'='*60}")
print("EXTRACTION COMPLETE")
print(f"{'='*60}")
print(f"Files: {all_data['metadata']['filesProcessed']}")
print(f"Total records: {all_data['metadata']['totalRecords']}")
print(f"Regions: {list(time_series.keys())}")

for region, records in time_series.items():
    print(f"  {region}: {len(records)} records")

# Save
output_file = OUTPUT_DIR / "comprehensive-extraction.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)

print(f"\nSaved to: {output_file}")
print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
