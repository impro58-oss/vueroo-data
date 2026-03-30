import pandas as pd
import numpy as np

file_path = r'C:\Users\impro\Downloads\MedTech Europe Data All.xlsx'
df = pd.read_excel(file_path, sheet_name='All Data')

# Map to 5 regions
df['US'] = df['North America']
df['PACRIM'] = df['ASPAC']

# Get Q4 data for trending
q4_data = []
for year in [2022, 2023, 2024]:
    q4 = df[(df['QR'] == 'Q4') & (df['YEAR '] == year)]
    if len(q4) > 0:
        q4_data.append({
            'Period': f'Q4 {year}',
            'US': q4['US'].sum(),
            'Europe': q4['Europe'].sum(),
            'PACRIM': q4['PACRIM'].sum(),
            'Japan': q4['Japan '].sum(),
            'LATAM': q4['LATAM'].sum(),
            'Worldwide': q4['WW'].sum()
        })

q4_df = pd.DataFrame(q4_data)
print('=== Q4 PERFORMANCE TREND (All Products) ===')
print(q4_df.to_string(index=False))
print()

# Calculate growth rates
print('=== YEAR-OVER-YEAR GROWTH RATES (%) ===')
growth_data = []
for i in range(1, len(q4_df)):
    prev = q4_df.iloc[i-1]
    curr = q4_df.iloc[i]
    growth_data.append({
        'Period': f"{prev['Period']} to {curr['Period']}",
        'US': ((curr['US'] - prev['US']) / prev['US'] * 100),
        'Europe': ((curr['Europe'] - prev['Europe']) / prev['Europe'] * 100),
        'PACRIM': ((curr['PACRIM'] - prev['PACRIM']) / prev['PACRIM'] * 100),
        'Japan': ((curr['Japan'] - prev['Japan']) / prev['Japan'] * 100),
        'LATAM': ((curr['LATAM'] - prev['LATAM']) / prev['LATAM'] * 100),
        'Worldwide': ((curr['Worldwide'] - prev['Worldwide']) / prev['Worldwide'] * 100)
    })

growth_df = pd.DataFrame(growth_data)
print(growth_df.to_string(index=False))
print()

# Winners and losers
print('=== REGIONAL PERFORMANCE SUMMARY ===')
print()
print('2023 vs 2022 (Q4):')
print('  BEST: US (+36.3%) - Strong recovery/growth')
print('  WORST: Europe (-2.2%) - Slight decline')
print()
print('2024 vs 2023 (Q4):')
print('  BEST: Europe (+15.7%) - Strong rebound')
print('  WORST: Japan (-4.7%) - Minor decline')
print()

# Market size ranking (Q4 2024)
q4_2024 = df[(df['QR'] == 'Q4') & (df['YEAR '] == 2024)]
totals = {
    'US': q4_2024['US'].sum(),
    'Europe': q4_2024['Europe'].sum(),
    'PACRIM': q4_2024['PACRIM'].sum(),
    'Japan': q4_2024['Japan '].sum(),
    'LATAM': q4_2024['LATAM'].sum()
}
print('=== MARKET SIZE RANKING (Q4 2024) ===')
for i, (region, value) in enumerate(sorted(totals.items(), key=lambda x: x[1], reverse=True), 1):
    share = (value / q4_2024['WW'].sum()) * 100
    print(f'{i}. {region}: ${value:,.0f} ({share:.1f}% of WW)')

print()
print('=== PRODUCT-SPECIFIC REGIONAL GROWTH (Q4 2024 vs Q4 2023) ===')
print()

# Get meaningful growth (>10% base)
q4_2024_products = df[(df['QR'] == 'Q4') & (df['YEAR '] == 2024)][['Product', 'US', 'Europe', 'PACRIM', 'Japan ', 'LATAM']].copy()
q4_2023_products = df[(df['QR'] == 'Q4') & (df['YEAR '] == 2023)][['Product', 'US', 'Europe', 'PACRIM', 'Japan ', 'LATAM']].copy()

for region in ['US', 'Europe', 'PACRIM', 'Japan ', 'LATAM']:
    print(f'\n{region.strip()} - Top Growing Products (>$5K base):')
    merged = q4_2024_products[['Product', region]].merge(
        q4_2023_products[['Product', region]], on='Product', suffixes=('_2024', '_2023')
    )
    # Filter for meaningful base
    merged = merged[merged[region + '_2023'] > 5000]
    if len(merged) > 0:
        merged['growth'] = ((merged[region + '_2024'] - merged[region + '_2023']) / merged[region + '_2023'] * 100)
        merged = merged.replace([np.inf, -np.inf], np.nan).dropna()
        top3 = merged.sort_values('growth', ascending=False).head(3)
        for _, row in top3.iterrows():
            print(f"  {row['Product']}: +{row['growth']:.1f}% (${row[region + '_2023']:,.0f} -> ${row[region + '_2024']:,.0f})")
