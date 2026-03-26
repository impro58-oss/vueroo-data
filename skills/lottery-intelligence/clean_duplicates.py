import json
from pathlib import Path

DATA_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence/data")

print("="*60)
print("LOTTERY DATABASE DEDUPLICATION")
print("="*60)
print()

# Clean Irish Lotto
print("Cleaning Irish Lotto database...")
with open(DATA_DIR / 'irish_lotto_db.json', 'r') as f:
    data = json.load(f)

draws = data['draws']
print(f"  Before: {len(draws)} draws")

# Remove duplicates based on date + numbers
seen = {}
unique_draws = []

for draw in draws:
    key = (draw['date'], tuple(sorted(draw['numbers'])))
    if key not in seen:
        seen[key] = True
        unique_draws.append(draw)

print(f"  After: {len(unique_draws)} draws")
print(f"  Removed: {len(draws) - len(unique_draws)} duplicates")

# Update and save
data['draws'] = unique_draws
data['metadata']['total_draws'] = len(unique_draws)

with open(DATA_DIR / 'irish_lotto_db.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"  Saved: irish_lotto_db.json")
print()

# Clean EuroMillions
print("Cleaning EuroMillions database...")
with open(DATA_DIR / 'euromillions_db.json', 'r') as f:
    data = json.load(f)

draws = data['draws']
print(f"  Before: {len(draws)} draws")

seen = {}
unique_draws = []

for draw in draws:
    key = (draw['date'], tuple(sorted(draw['numbers'])), tuple(sorted(draw.get('lucky_stars', []))))
    if key not in seen:
        seen[key] = True
        unique_draws.append(draw)

print(f"  After: {len(unique_draws)} draws")
print(f"  Removed: {len(draws) - len(unique_draws)} duplicates")

data['draws'] = unique_draws
data['metadata']['total_draws'] = len(unique_draws)

with open(DATA_DIR / 'euromillions_db.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"  Saved: euromillions_db.json")
print()

print("="*60)
print("CLEANUP COMPLETE")
print("="*60)
