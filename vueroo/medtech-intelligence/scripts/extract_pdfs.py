import pdfplumber
import json
import os
from pathlib import Path

# Configuration
BASE_DIR = Path("C:/Users/impro/Documents/MedTech Intell/Journals + Cites")
OUTPUT_DIR = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/extracted-data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(pdf_path, max_pages=10):
    """Extract text from first N pages of PDF"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages[:max_pages]):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i+1} ---\n" + page_text
            return text
    except Exception as e:
        return f"Error: {str(e)}"

def extract_key_metrics(text):
    """Extract stroke-related metrics from text"""
    import re
    
    metrics = {
        "incidence": [],
        "prevalence": [],
        "mortality": [],
        "projections": [],
        "treatment_access": [],
        "countries": []
    }
    
    # Look for patterns
    patterns = {
        "incidence": r'(\d+[.,]?\d*)\s*(million|thousand)?\s*(new\s+)?(stroke|ischemic|hemorrhagic)',
        "prevalence": r'(\d+[.,]?\d*)\s*(million|thousand)?\s*(people\s+)?(living\s+with|survivors)',
        "mortality": r'(\d+[.,]?\d*)\s*(million|thousand)?\s*(deaths|mortality)',
        "year": r'20(2[0-9]|3[0-9])'
    }
    
    return metrics

# Key documents to process
key_docs = {
    "global_stroke_2025": BASE_DIR / "World Stroke/feigin-et-al-2025-world-stroke-organization-gl...",
    "china_2019": BASE_DIR / "2- China/REF_2022 Zhao - China Stroke Statistics 2019.pdf",
    "china_report": BASE_DIR / "2- China/s40779-023-00463-x (China Stroke Report).pdf",
    "eu_burden": BASE_DIR / "2- EU/REF_Wafa - Burden of Stroke - Europe - 2017 - 2047.pdf",
    "eu_plan": BASE_DIR / "2- EU/EU Stroke Plan 2018-2030.pdf",
    "mt_glass": BASE_DIR / "AIS/REF_asif-2023-MT-global-access-for-stroke-(mt-glass)-a-...",
    "germany": BASE_DIR / "2- Ger/s42466-023-00297-x.pdf",
    "japan": BASE_DIR / "2- Japan/fneur-14-1090136.pdf"
}

results = {}

print("Extracting data from key documents...")
for name, path in key_docs.items():
    if path.exists():
        print(f"Processing: {name}")
        text = extract_text_from_pdf(path, max_pages=15)
        results[name] = {
            "path": str(path),
            "text_sample": text[:5000] if text else "No text extracted"
        }
    else:
        print(f"Not found: {name}")
        results[name] = {"error": "File not found"}

# Save extracted data
output_file = OUTPUT_DIR / "extracted_text_samples.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nExtraction complete. Data saved to: {output_file}")
