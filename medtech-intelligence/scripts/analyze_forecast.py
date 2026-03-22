import json

with open('dashboard/data/revenue-structured.json', 'r') as f:
    data = json.load(f)

print('=== Revenue Data Analysis ===')
print(f'Total records: {len(data["records"])}')

# Check year distribution
years = {}
for r in data['records']:
    y = r['year']
    years[y] = years.get(y, 0) + 1

print('\n=== Records by Year ===')
for y in sorted(years.keys()):
    print(f'{y}: {years[y]} records')

# Check if 2025-2030 data exists
future_years = [y for y in years.keys() if y > 2024]
print(f'\nFuture years (2025+): {future_years}')

# Sample data
print('\n=== Sample: Medtronic Revenue Timeline ===')
mdt_data = [r for r in data['records'] if r['company'] == 'Medtronic']
for r in sorted(mdt_data, key=lambda x: x['year']):
    print(f"{r['year']}: {r['revenueFormatted']} - {r['highlight'][:50] if r['highlight'] else 'No notes'}")

print('\n=== Data Source Check ===')
print(f"All records source: {list(set(r['source'] for r in data['records']))}")

print('\n=== Is this forecasted data? ===')
# Check if 2025-2030 values look calculated vs reported
recent = [r for r in data['records'] if r['year'] in [2024, 2025, 2026, 2030]]
for r in recent[:8]:
    print(f"{r['company']} {r['year']}: {r['revenueFormatted']}")
