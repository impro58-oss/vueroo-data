import json
from pathlib import Path

DATA_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence/data")

# Load clean EuroMillions data
with open(DATA_DIR / 'euromillions_historical.json', 'r') as f:
    data = json.load(f)

draws = data['draws']

# Remove duplicates
seen = {}
unique = []
for d in draws:
    key = (d['date'], tuple(d['numbers']), tuple(d.get('lucky_stars', [])))
    if key not in seen:
        seen[key] = True
        unique.append(d)

print(f"Total unique draws: {len(unique)}")
print(f"Date range: {unique[-1]['date']} to {unique[0]['date']}")
print()

# Check for jackpot winners
winners = [d for d in unique if d.get('jackpot_winners', 0) > 0]
no_winner_info = [d for d in unique if 'jackpot_winners' not in d or d.get('jackpot_winners', 0) == 0]

print(f"Draws WITH jackpot winners: {len(winners)}")
print(f"Draws WITHOUT winner data: {len(no_winner_info)}")
print()

if winners:
    print("Jackpot wins:")
    for w in winners:
        print(f"  {w['date']}: {w['jackpot_winners']} winner(s) - {w.get('jackpot_amount', 'N/A')}")
else:
    print("No jackpot winner data found in the scraped data.")
    print("\nSample draw data:")
    for d in unique[:3]:
        print(f"  {d['date']}: {d['numbers']} + {d.get('lucky_stars', [])}")
        print(f"    Available fields: {list(d.keys())}")

# Check prize breakdown info
with_prizes = [d for d in unique if d.get('prize_breakdown')]
print(f"\nDraws with full prize breakdown: {len(with_prizes)}")

if with_prizes:
    print("\nSample prize breakdown:")
    for d in with_prizes[:2]:
        print(f"  {d['date']}:")
        for prize in d['prize_breakdown'][:3]:
            print(f"    {prize}")
