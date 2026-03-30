import pandas as pd
import numpy as np

file_path = r'C:\Users\impro\Downloads\MedTech Europe Data All.xlsx'
df = pd.read_excel(file_path, sheet_name='All Data')

# Map regions
df['US'] = df['North America']
df['PACRIM'] = df['ASPAC']

# Filter for thrombectomy products
thrombectomy = df[df['Product'].isin(['Aspiration Catheters', 'Stent Retrievers'])].copy()

print('=== THROMBECTOMY MARKET OVERVIEW ===')
print('Products: Aspiration Catheters, Stent Retrievers')
print()

# Quarterly totals by region
quarterly = thrombectomy.groupby(['YEAR ', 'QR']).agg({
    'US': 'sum',
    'Europe': 'sum',
    'PACRIM': 'sum',
    'Japan ': 'sum',
    'LATAM': 'sum',
    'WW': 'sum'
}).reset_index()

# Sort chronologically
order = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
quarterly['sort_key'] = quarterly['YEAR '] * 10 + quarterly['QR'].map(order)
quarterly = quarterly.sort_values('sort_key')

print('=== QUARTERLY THROMBECTOMY PERFORMANCE BY REGION ===')
print(quarterly[['YEAR ', 'QR', 'US', 'Europe', 'PACRIM', 'Japan ', 'LATAM', 'WW']].to_string(index=False))
print()

# Calculate growth rates for each region
print('=== YEAR-OVER-YEAR GROWTH (Q4 vs Q4) ===')
q4_only = quarterly[quarterly['QR'] == 'Q4'].copy()

for region in ['US', 'Europe', 'PACRIM', 'Japan ', 'LATAM', 'WW']:
    q4_only[f'{region}_growth'] = q4_only[region].pct_change() * 100

print(q4_only[['YEAR ', 'US', 'US_growth', 'Europe', 'Europe_growth', 'PACRIM', 'PACRIM_growth', 
               'Japan ', 'Japan _growth', 'LATAM', 'LATAM_growth', 'WW', 'WW_growth']].to_string(index=False))
print()

# Product breakdown for Q4 periods
print('=== PRODUCT BREAKDOWN BY REGION ===')
for year in [2022, 2023, 2024]:
    print(f'\nQ4 {year}:')
    q4_data = thrombectomy[(thrombectomy['QR'] == 'Q4') & (thrombectomy['YEAR '] == year)]
    
    aspiration = q4_data[q4_data['Product'] == 'Aspiration Catheters']
    stent = q4_data[q4_data['Product'] == 'Stent Retrievers']
    
    if len(aspiration) > 0 and len(stent) > 0:
        print(f'  Aspiration Catheters WW: ${aspiration["WW"].sum():,.0f}')
        print(f'  Stent Retrievers WW: ${stent["WW"].sum():,.0f}')
        print(f'  Total Thrombectomy WW: ${q4_data["WW"].sum():,.0f}')
        
        print(f'  Regional split:')
        print(f'    US: ${q4_data["US"].sum():,.0f}')
        print(f'    Europe: ${q4_data["Europe"].sum():,.0f}')
        print(f'    PACRIM: ${q4_data["PACRIM"].sum():,.0f}')
        print(f'    Japan: ${q4_data["Japan "].sum():,.0f}')
        print(f'    LATAM: ${q4_data["LATAM"].sum():,.0f}')

print()
print('=== MARKET SHARE EVOLUTION (Thrombectomy) ===')
for year in [2022, 2023, 2024]:
    q4_data = thrombectomy[(thrombectomy['QR'] == 'Q4') & (thrombectomy['YEAR '] == year)]
    if len(q4_data) > 0:
        total = q4_data['WW'].sum()
        print(f'\nQ4 {year} (Total: ${total:,.0f}):')
        print(f'  US: {(q4_data["US"].sum()/total)*100:.1f}%')
        print(f'  Europe: {(q4_data["Europe"].sum()/total)*100:.1f}%')
        print(f'  PACRIM: {(q4_data["PACRIM"].sum()/total)*100:.1f}%')
        print(f'  Japan: {(q4_data["Japan "].sum()/total)*100:.1f}%')
        print(f'  LATAM: {(q4_data["LATAM"].sum()/total)*100:.1f}%')

print()
print('=== ASPRATION vs STENT RETRIEVER TRENDS ===')
for product in ['Aspiration Catheters', 'Stent Retrievers']:
    print(f'\n{product}:')
    prod_data = thrombectomy[thrombectomy['Product'] == product]
    q4_prod = prod_data[prod_data['QR'] == 'Q4'].groupby('YEAR ')['WW'].sum()
    for year in q4_prod.index:
        print(f'  Q4 {year}: ${q4_prod[year]:,.0f}')
