import json
from pathlib import Path

DATA_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence/data")

# Clean EuroMillions
print("Cleaning EuroMillions data...")
with open(DATA_DIR / 'euromillions_historical.json', 'r') as f:
    data = json.load(f)

draws = data['draws']
print(f"Before: {len(draws)} draws")

# Remove duplicates
seen = {}
unique = []
for d in draws:
    key = (d['date'], tuple(d['numbers']), tuple(d.get('lucky_stars', [])))
    if key not in seen:
        seen[key] = True
        unique.append(d)

print(f"After: {len(unique)} draws")

# Update metadata
data['draws'] = unique
data['metadata']['total_draws'] = len(unique)

# Save clean version
with open(DATA_DIR / 'euromillions_clean.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Saved clean data to euromillions_clean.json")

# Show sample
print(f"\nDate range: {unique[-1]['date']} to {unique[0]['date']}")
print(f"Sample draw: {unique[0]}")
