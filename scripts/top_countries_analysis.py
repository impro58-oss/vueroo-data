import pandas as pd

file_path = r'C:\Users\impro\Downloads\MedTech Europe Data All.xlsx'
df = pd.read_excel(file_path, sheet_name='All Data')

# Get Q4 2024 data
q4_2024 = df[(df['QR'] == 'Q4') & (df['YEAR '] == 2024)]

# Sum all products by country
countries = ['France', 'Germany', 'Italy', 'The Netherlands', 'Spain', 'UK', 
             'Russia', 'Austria', 'Belgium', 'Portugal', 'Ireland', 'Switzerland', 
             'Israel', 'Nordics', 'Poland', 'South Africa', 'Turkey', 'Saudi Arabia',
             'Argentina', 'Brazil', 'Chile', 'Colombia', 'Mexico', 'Peru', 'Ecuador',
             'ANZ', 'China', 'Hong Kong', 'India', 'Indonesia', 'Japan ', 
             'Malaysia', 'Singapore', 'South Korea', 'Taiwan', 'Thailand', 'Vietnam',
             'North America']

# Calculate country totals
print('=== TOP 20 COUNTRIES BY CASE VOLUME (Q4 2024) ===')
print()

country_totals = {}
for country in countries:
    if country in q4_2024.columns:
        total = q4_2024[country].sum()
        if total > 0 and not pd.isna(total):
            country_totals[country] = total

# Sort and display top 20
sorted_countries = sorted(country_totals.items(), key=lambda x: x[1], reverse=True)

print('Rank | Country | Q4 2024 Cases | % of Global')
print('-----|---------|---------------|------------')
for i, (country, cases) in enumerate(sorted_countries[:20], 1):
    pct = (cases / q4_2024['WW'].sum()) * 100
    print(f'{i:4} | {country:15} | {cases:13,.0f} | {pct:8.1f}%')

print()
print('=== REGIONAL LEADERS ===')
print()

# Europe top 5
europe_countries = ['France', 'Germany', 'Italy', 'Spain', 'UK', 'Russia', 'Austria', 
                   'Belgium', 'Portugal', 'Ireland', 'Switzerland', 'Nordics', 'Poland']
europe_totals = {c: country_totals[c] for c in europe_countries if c in country_totals}
europe_sorted = sorted(europe_totals.items(), key=lambda x: x[1], reverse=True)

print('Europe Top 5:')
for i, (country, cases) in enumerate(europe_sorted[:5], 1):
    print(f'  {i}. {country}: {cases:,.0f} cases')

# ASPAC top 5
aspac_countries = ['China', 'Japan ', 'South Korea', 'India', 'ANZ', 'Taiwan', 'Singapore',
                  'Malaysia', 'Thailand', 'Vietnam', 'Indonesia', 'Hong Kong']
aspac_totals = {c: country_totals[c] for c in aspac_countries if c in country_totals}
aspac_sorted = sorted(aspac_totals.items(), key=lambda x: x[1], reverse=True)

print('\\nASPAC Top 5:')
for i, (country, cases) in enumerate(aspac_sorted[:5], 1):
    print(f'  {i}. {country}: {cases:,.0f} cases')

# LATAM top 5
latam_countries = ['Brazil', 'Mexico', 'Argentina', 'Colombia', 'Chile', 'Peru']
latam_totals = {c: country_totals[c] for c in latam_countries if c in country_totals}
latam_sorted = sorted(latam_totals.items(), key=lambda x: x[1], reverse=True)

print('\\nLATAM Top 5:')
for i, (country, cases) in enumerate(latam_sorted[:5], 1):
    print(f'  {i}. {country}: {cases:,.0f} cases')

# MEA
mea_countries = ['Turkey', 'Saudi Arabia', 'South Africa', 'Israel']
mea_totals = {c: country_totals[c] for c in mea_countries if c in country_totals}
mea_sorted = sorted(mea_totals.items(), key=lambda x: x[1], reverse=True)

print('\\nMEA Top Countries:')
for i, (country, cases) in enumerate(mea_sorted[:5], 1):
    print(f'  {i}. {country}: {cases:,.0f} cases')

print()
print('=== PRODUCT-LEVEL COUNTRY LEADERS ===')
print()

# For top products, which country leads?
top_products = ['Coils', 'MicroCatheters', 'Guidewires', 'Guide Catheters']

for product in top_products:
    prod_data = q4_2024[q4_2024['Product'] == product]
    if len(prod_data) > 0:
        print(f'{product}:')
        # Find top country for this product
        country_cases = {}
        for country in countries:
            if country in prod_data.columns:
                val = prod_data[country].sum()
                if val > 0 and not pd.isna(val):
                    country_cases[country] = val
        
        top_3 = sorted(country_cases.items(), key=lambda x: x[1], reverse=True)[:3]
        for rank, (country, cases) in enumerate(top_3, 1):
            print(f'  #{rank} {country}: {cases:,.0f} cases')
        print()
