import json

with open('dashboard/data/revenue-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check Jie's sheet structure
jie_sheet = data['revenue_companies_aug']['sheets']["Jie's"]
print('=== Jie Sheet - First 5 rows ===')
for i, row in enumerate(jie_sheet[:5]):
    print(f'{i}: {row}')

print()
print('=== Row 2 (index 2) - Header row? ===')
print(jie_sheet[2])

print()
print('=== Row 3 - First data row? ===')
print(jie_sheet[3])

# Check 2024_Revenue sheet
print()
print('=== 2024_Revenue Sheet - First 10 rows ===')
rev_sheet = data['medtech_europe_2024']['sheets']['2024_Revenue']
for i, row in enumerate(rev_sheet[:10]):
    print(f'{i}: {row}')

# Check MDT sheet
print()
print('=== MDT Sheet - First 10 rows ===')
mdt_sheet = data['revenue_companies_aug']['sheets']['MDT']
for i, row in enumerate(mdt_sheet[:10]):
    print(f'{i}: {row}')
