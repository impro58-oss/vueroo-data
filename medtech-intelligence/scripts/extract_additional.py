import pdfplumber
import json
import os
from pathlib import Path

# Configuration
BASE_DIR = Path("C:/Users/impro/Documents/MedTech Intell/Journals + Cites")
OUTPUT_DIR = Path("C:/Users/impro/.openclaw/workspace/medtech-intelligence/extracted-data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(pdf_path, max_pages=15):
    """Extract text from PDF"""
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

# Extract key documents
key_docs = {
    "mt_glass_global": BASE_DIR / "AIS/REF_asif-2023-MT-global-access-for-stroke-(mt-glass)-a-...",
    "global_stroke_2024": BASE_DIR / "AIS/REF_Kim-2024-Global-Stroke-Statistics-2023-Svailability...",
    "eu_burden_appendix": BASE_DIR / "AIS/REF_Burden_of_Stroke_in_Europe_Report_SAFE_Appendix.pdf",
    "eu_burden_main": BASE_DIR / "AIS/REF_Burden-Of-Stroke-In-Europe-SAFE.pdf",
    "epidemiology": BASE_DIR / "1- Epidemiology of stroke/1941874415588319.pdf",
    "rennert_lvo": BASE_DIR / "LVO/Rennert et al., 2019.pdf",
    "meyer_mevo": BASE_DIR / "MeVO - DMeVO/meyer-et-al-aspiration-versus-stent-retriever-...",
    "china_projections": BASE_DIR / "2- China/pu-et-al-2023-projected-global-trends-in-IS.pdf"
}

results = {}

print("Extracting additional documents...")
for name, path in key_docs.items():
    if path.exists():
        print(f"Processing: {name}")
        text = extract_text_from_pdf(path, max_pages=15)
        results[name] = {
            "path": str(path),
            "text_sample": text[:8000] if text else "No text extracted"
        }
    else:
        # Try alternative paths
        alt_paths = [
            path.parent / path.name.replace("...", ""),
            path.parent / (path.stem + ".pdf")
        ]
        found = False
        for alt in alt_paths:
            if alt.exists():
                print(f"Found via alt path: {name}")
                text = extract_text_from_pdf(alt, max_pages=15)
                results[name] = {
                    "path": str(alt),
                    "text_sample": text[:8000] if text else "No text extracted"
                }
                found = True
                break
        if not found:
            print(f"Not found: {name}")
            results[name] = {"error": "File not found"}

# Save
output_file = OUTPUT_DIR / "additional_extractions.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nExtraction complete. Data saved to: {output_file}")
