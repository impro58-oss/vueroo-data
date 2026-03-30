import pandas as pd
import json

# Load the Excel data
file_path = r'C:\Users\impro\Downloads\MedTech Europe Data All.xlsx'
df = pd.read_excel(file_path, sheet_name='All Data')

# Define country columns
country_columns = [
    'North America', 'France', 'Germany', 'Italy', 'The Netherlands', 'Spain', 'UK', 
    'Russia', 'Austria', 'Belgium', 'Portugal', 'Ireland', 'Switzerland', 'Israel', 
    'Nordics', 'Poland', 'South Africa', 'Turkey', 'Saudi Arabia', 'Rest of MEA',
    'Argentina', 'Brazil', 'Chile', 'Colombia', 'Mexico', 'Costa Rica', 'Peru', 'Ecuador',
    'ANZ', 'China', 'Hong Kong', 'India', 'Indonesia', 'Japan ', 'Malaysia', 
    'Singapore', 'South Korea', 'Taiwan', 'Thailand', 'Vietnam'
]

# Melt the dataframe to get country-wise data
dashboard_data = []

for _, row in df.iterrows():
    year = int(row['YEAR '])
    quarter = row['QR']
    product = row['Product']
    
    for country in country_columns:
        if country in row.index and pd.notna(row[country]) and row[country] > 0:
            # Clean country names
            clean_country = country.strip()
            if clean_country == 'North America':
                clean_country = 'United States'
            elif clean_country == 'Japan ':
                clean_country = 'Japan'
            
            dashboard_data.append({
                'Year': year,
                'Quarter': quarter,
                'Product': product,
                'Country': clean_country,
                'Cases': float(row[country])
            })

# Convert to JSON for embedding
data_json = json.dumps(dashboard_data)

print(f"Total records: {len(dashboard_data)}")
print(f"Unique countries: {len(set(d['Country'] for d in dashboard_data))}")
print(f"Unique products: {len(set(d['Product'] for d in dashboard_data))}")

# Save embedded data script
embedded_js = f"""
// Embedded MedTech Data - Generated automatically
window.embeddedData = {data_json};
"""

with open(r'C:\Users\impro\.openclaw\workspace\medtech-control-intelligence\dashboard\data.js', 'w') as f:
    f.write(embedded_js)

print("\nData file created: dashboard/data.js")

# Also create a summary
summary = {}
for d in dashboard_data:
    key = f"{d['Year']}-{d['Quarter']}"
    if key not in summary:
        summary[key] = 0
    summary[key] += d['Cases']

print("\nCase volume by period:")
for period in sorted(summary.keys()):
    print(f"  {period}: {int(summary[period]):,} cases")
