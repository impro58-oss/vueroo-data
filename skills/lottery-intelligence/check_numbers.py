import json
from pathlib import Path

DATA_DIR = Path("C:/Users/impro/.openclaw/workspace/skills/lottery-intelligence/data")

# Load Irish Lotto data
with open(DATA_DIR / 'irish_lotto_db.json', 'r') as f:
    data = json.load(f)

draws = data['draws']

# Numbers to check
check_numbers = {1, 2, 12, 14, 18, 29}

print("Searching Irish Lotto database...")
print(f"Looking for exact match: {sorted(check_numbers)}")
print(f"Total draws in database: {len(draws)}")
print()

# Check for exact match
exact_matches = []
partial_matches = []  # 3+ numbers matching

for draw in draws:
    draw_numbers = set(draw['numbers'])
    
    # Check exact match
    if draw_numbers == check_numbers:
        exact_matches.append(draw)
    
    # Check partial matches (3+ numbers)
    matches = len(draw_numbers & check_numbers)
    if matches >= 3:
        partial_matches.append({
            'date': draw['date'],
            'numbers': draw['numbers'],
            'bonus': draw.get('bonus'),
            'matches': matches,
            'matching_numbers': sorted(draw_numbers & check_numbers)
        })

print("="*60)
print("RESULTS")
print("="*60)
print()

if exact_matches:
    print(f"EXACT MATCH FOUND!")
    for match in exact_matches:
        print(f"   Date: {match['date']}")
        print(f"   Numbers: {match['numbers']}")
        print(f"   Bonus: {match.get('bonus')}")
else:
    print(f"No exact match found")
    print(f"   The combination {sorted(check_numbers)} has NEVER been drawn")
    print()

print(f"PARTIAL MATCHES (3+ numbers):")
print(f"   Found {len(partial_matches)} draws with 3+ matching numbers")
print()

# Show best partial matches
if partial_matches:
    # Sort by match count
    partial_matches.sort(key=lambda x: x['matches'], reverse=True)
    
    print("   Top matches:")
    for i, match in enumerate(partial_matches[:10], 1):
        print(f"   {i}. {match['date']}: {match['matches']} numbers matched - {match['matching_numbers']}")
        print(f"      Draw: {match['numbers']} (Bonus: {match['bonus']})")
    
    # Count by number of matches
    match_counts = {}
    for m in partial_matches:
        match_counts[m['matches']] = match_counts.get(m['matches'], 0) + 1
    
    print()
    print("   Summary:")
    for count in sorted(match_counts.keys(), reverse=True):
        print(f"      {count} numbers matched: {match_counts[count]} draws")

print()
print("="*60)
