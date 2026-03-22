import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
import numpy as np

# Paths
INPUT_DIR = Path("C:/Users/impro/Documents/MedTech Intell/Market Intel/Epidemiological")
OUTPUT_DIR = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/dashboard/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_date_from_filename(filename):
    """Extract date from filename"""
    # Look for patterns like 20250211, 2024, 18_6_24, etc.
    patterns = [
        r'(\d{4})(\d{2})(\d{2})',  # 20250211
        r'(\d{4})',               # 2024
        r'(\d{1,2})[_-](\d{1,2})[_-](\d{2,4})',  # 18_6_24
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                # Full date
                year = groups[0] if len(groups[0]) == 4 else '20' + groups[0]
                month = groups[1].zfill(2)
                day = groups[2].zfill(2) if len(groups[2]) <= 2 else groups[2][-2:].zfill(2)
                return {'year': int(year), 'month': int(month), 'day': int(day), 'full': f"{year}-{month}-{day}"}
            elif len(groups) == 1:
                # Just year
                year = groups[0]
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                return {'year': int(year), 'month': None, 'day': None, 'full': year}
    
    return {'year': None, 'month': None, 'day': None, 'full': None}

def infer_region_from_filename(filename):
    """Infer region from filename"""
    filename_lower = filename.lower()
    
    region_map = {
        'china': 'china',
        'cn': 'china',
        'eu': 'eu',
        'europe': 'eu',
        'germany': 'germany',
        'de': 'germany',
        'japan': 'japan',
        'jp': 'japan',
        'usa': 'usa',
        'us': 'usa',
        'india': 'india',
        'in': 'india',
        'brazil': 'brazil',
        'br': 'brazil',
        'africa': 'africa',
        'global': 'global',
        'world': 'global',
        'asia': 'seasia',
        'asah': 'asah',
        'aneurysm': 'aneurysm'
    }
    
    for key, region in region_map.items():
        if key in filename_lower:
            return region
    
    return 'unspecified'

def clean_dataframe(df):
    """Clean dataframe: remove empty rows/columns, standardize headers"""
    # Remove completely empty rows and columns
    df = df.dropna(how='all').dropna(axis=1, how='all')
    
    # Clean column names
    df.columns = [str(col).strip().replace('\n', ' ').replace('  ', ' ') for col in df.columns]
    
    # Convert numeric-looking strings to numbers
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    return df

def identify_date_columns(df):
    """Identify columns that contain dates or years"""
    date_cols = []
    
    for col in df.columns:
        col_str = str(col).lower()
        
        # Check column name
        if any(keyword in col_str for keyword in ['year', 'date', 'month', 'period', 'time']):
            date_cols.append(col)
            continue
        
        # Check if column contains years (1900-2050)
        try:
            numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(numeric_vals) > 0:
                year_vals = numeric_vals[(numeric_vals >= 1990) & (numeric_vals <= 2050)]
                if len(year_vals) / len(numeric_vals) > 0.5:  # More than 50% are years
                    date_cols.append(col)
        except:
            pass
    
    return date_cols

def extract_metric_type(filename, sheet_name, column_names):
    """Identify what type of metric this data represents"""
    text = f"{filename} {sheet_name} {' '.join(column_names)}".lower()
    
    metrics = {
        'incidence': ['incidence', 'new cases', 'annual', 'occurrence'],
        'prevalence': ['prevalence', 'living', 'survivors', 'existing'],
        'mortality': ['mortality', 'death', 'fatality', 'mortality'],
        'daly': ['daly', 'disability', 'burden', 'adjusted'],
        'treatment': ['treatment', 'therapy', 'thrombolysis', 'thrombectomy', 'mt', 'ivt'],
        'risk_factors': ['risk', 'hypertension', 'diabetes', 'smoking', 'factor'],
        'cost': ['cost', 'expenditure', 'economic', 'burden', 'price'],
        'hospital': ['hospital', 'admission', 'discharge', 'stay'],
        'outcomes': ['outcome', 'mrs', 'modified rankin', 'disability', 'recovery']
    }
    
    detected_metrics = []
    for metric_type, keywords in metrics.items():
        if any(keyword in text for keyword in keywords):
            detected_metrics.append(metric_type)
    
    return detected_metrics[0] if detected_metrics else 'general'

def process_excel_file(filepath):
    """Comprehensive Excel extraction"""
    results = {
        'filename': filepath.name,
        'file_date': parse_date_from_filename(filepath.name),
        'inferred_region': infer_region_from_filename(filepath.name),
        'sheets': {}
    }
    
    try:
        # Read all sheets
        xls = pd.ExcelFile(filepath)
        
        for sheet_name in xls.sheet_names:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                df = clean_dataframe(df)
                
                if df.empty:
                    continue
                
                # Identify date columns
                date_cols = identify_date_columns(df)
                
                # Detect metric type
                metric_type = extract_metric_type(filepath.name, sheet_name, df.columns.tolist())
                
                # Convert to records with metadata
                records = []
                for idx, row in df.iterrows():
                    record = {
                        '_row_index': idx,
                        '_source_file': filepath.name,
                        '_sheet_name': sheet_name,
                        '_extraction_date': datetime.now().isoformat(),
                        '_metric_type': metric_type
                    }
                    
                    # Add all cell values
                    for col in df.columns:
                        val = row[col]
                        # Handle NaN
                        if pd.isna(val):
                            record[str(col)] = None
                        else:
                            record[str(col)] = val
                    
                    records.append(record)
                
                results['sheets'][sheet_name] = {
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'columns': df.columns.tolist(),
                    'date_columns': date_cols,
                    'metric_type': metric_type,
                    'data': records
                }
                
            except Exception as e:
                results['sheets'][sheet_name] = {'error': str(e)}
    
    except Exception as e:
        results['error'] = str(e)
    
    return results

def create_time_series_database(all_extractions):
    """Create a time-series database from all extractions"""
    time_series = {}
    
    for extraction in all_extractions:
        region = extraction['inferred_region']
        file_date = extraction['file_date']
        
        if region not in time_series:
            time_series[region] = {}
        
        for sheet_name, sheet_data in extraction.get('sheets', {}).items():
            if 'data' not in sheet_data:
                continue
            
            metric_type = sheet_data.get('metric_type', 'general')
            
            if metric_type not in time_series[region]:
                time_series[region][metric_type] = []
            
            for record in sheet_data['data']:
                # Enrich record with file date
                enriched = {
                    **record,
                    '_file_year': file_date['year'],
                    '_file_month': file_date['month'],
                    '_file_date_full': file_date['full'],
                    '_region': region
                }
                time_series[region][metric_type].append(enriched)
    
    return time_series

def main():
    print("=" * 80)
    print("COMPREHENSIVE EXCEL EXTRACTION")
    print("=" * 80)
    
    # Find all Excel files
    excel_files = list(INPUT_DIR.glob("*.xlsx")) + list(INPUT_DIR.glob("*.xls"))
    
    print(f"\nFound {len(excel_files)} Excel files:")
    for f in excel_files:
        print(f"  - {f.name}")
    
    # Process each file
    all_extractions = []
    
    for filepath in excel_files:
        print(f"\n{'='*60}")
        print(f"Processing: {filepath.name}")
        print(f"File date: {parse_date_from_filename(filepath.name)}")
        print(f"Inferred region: {infer_region_from_filename(filepath.name)}")
        
        extraction = process_excel_file(filepath)
        all_extractions.append(extraction)
        
        print(f"Sheets found: {list(extraction.get('sheets', {}).keys())}")
        for sheet_name, sheet_data in extraction.get('sheets', {}).items():
            if 'error' not in sheet_data:
                print(f"  - {sheet_name}: {sheet_data['row_count']} rows, {sheet_data['column_count']} cols")
                print(f"    Metric type: {sheet_data.get('metric_type', 'unknown')}")
                print(f"    Date columns: {sheet_data.get('date_columns', [])}")
    
    # Create time-series database
    print(f"\n{'='*60}")
    print("Creating time-series database...")
    time_series = create_time_series_database(all_extractions)
    
    # Create master dataset
    master_dataset = {
        'metadata': {
            'version': '2.0',
            'lastUpdated': datetime.now().isoformat(),
            'extractionDate': datetime.now().strftime('%Y-%m-%d'),
            'filesProcessed': len(excel_files),
            'regions': list(time_series.keys()),
            'totalRecords': sum(len(records) for region in time_series.values() 
                             for records in region.values())
        },
        'rawExtractions': all_extractions,
        'timeSeriesByRegion': time_series,
        'dataQuality': {
            'dateCoverage': {},
            'regionCoverage': {},
            'metricCoverage': {}
        }
    }
    
    # Calculate coverage stats
    for region, metrics in time_series.items():
        years = set()
        metric_counts = {}
        
        for metric_type, records in metrics.items():
            metric_counts[metric_type] = len(records)
            for record in records:
                if record.get('_file_year'):
                    years.add(record['_file_year'])
        
        master_dataset['dataQuality']['regionCoverage'][region] = {
            'yearsAvailable': sorted(list(years)),
            'metricTypes': list(metrics.keys()),
            'totalRecords': sum(metric_counts.values())
        }
        master_dataset['dataQuality']['dateCoverage'][region] = sorted(list(years))
        master_dataset['dataQuality']['metricCoverage'][region] = metric_counts
    
    # Save files
    print(f"\n{'='*60}")
    print("Saving datasets...")
    
    # Master dataset
    master_file = OUTPUT_DIR / "master-dataset-v2.json"
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_dataset, f, indent=2, ensure_ascii=False, default=str)
    print(f"✓ Master dataset: {master_file}")
    
    # Time series only (for dashboard)
    ts_file = OUTPUT_DIR / "time-series-data.json"
    with open(ts_file, 'w', encoding='utf-8') as f:
        json.dump(time_series, f, indent=2, ensure_ascii=False, default=str)
    print(f"✓ Time series: {ts_file}")
    
    # Summary report
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed: {len(excel_files)}")
    print(f"Regions identified: {list(time_series.keys())}")
    print(f"\nRecords by region:")
    for region, metrics in time_series.items():
        total = sum(len(records) for records in metrics.values())
        print(f"  {region}: {total} records")
        for metric_type, records in metrics.items():
            print(f"    - {metric_type}: {len(records)}")
    
    print(f"\n{'='*60}")
    print("Ready for analysis!")
    print(f"Use 'time-series-data.json' for dashboard")
    print(f"Use 'master-dataset-v2.json' for full access")

if __name__ == "__main__":
    main()
