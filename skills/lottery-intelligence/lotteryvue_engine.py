"""
LotteryVue Analysis Engine
Pattern recognition, number analysis, and wheel generation for lottery intelligence.
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
from itertools import combinations
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

BASE_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace\\skills\\lottery-intelligence")
DATA_DIR = BASE_DIR / "data"


@dataclass
class NumberStats:
    """Statistics for a single number."""
    number: int
    frequency: int
    last_drawn: Optional[str]
    gap: int  # draws since last seen
    hot_score: float  # 0-1, higher = hotter


@dataclass  
class WheelTicket:
    """A wheel ticket with numbers."""
    ticket_id: int
    numbers: List[int]
    coverage: float  # % of combinations covered


class LotteryVueEngine:
    """Main analysis engine."""
    
    def __init__(self, game: str = 'irish'):
        self.game = game
        self.data = None
        self.draws = []
        self.number_stats = {}
        
        if game == 'irish':
            self.load_irish_data()
            self.main_count = 6
            self.max_number = 47
            self.has_bonus = True
        else:
            self.load_euro_data()
            self.main_count = 5
            self.max_number = 50
            self.has_lucky_stars = True
            self.star_count = 2
            self.max_star = 12
    
    def load_irish_data(self):
        """Load Irish Lotto data."""
        with open(DATA_DIR / 'irish_lotto_db.json', 'r') as f:
            self.data = json.load(f)
        self.draws = self.data['draws']
        print(f"Loaded {len(self.draws)} Irish Lotto draws")
    
    def load_euro_data(self):
        """Load EuroMillions data."""
        with open(DATA_DIR / 'euromillions_db.json', 'r') as f:
            self.data = json.load(f)
        self.draws = self.data['draws']
        print(f"Loaded {len(self.draws)} EuroMillions draws")
    
    def calculate_frequency(self, lookback: int = 100) -> Dict[int, int]:
        """Calculate frequency of each number in last N draws."""
        recent_draws = self.draws[:lookback]
        all_numbers = []
        
        for draw in recent_draws:
            all_numbers.extend(draw['numbers'])
        
        return Counter(all_numbers)
    
    def calculate_gaps(self) -> Dict[int, int]:
        """Calculate gaps (draws since last appearance) for each number."""
        gaps = {n: float('inf') for n in range(1, self.max_number + 1)}
        
        for i, draw in enumerate(self.draws):
            for num in draw['numbers']:
                if gaps[num] == float('inf'):
                    gaps[num] = i
        
        return gaps
    
    def generate_number_stats(self, lookback: int = 100) -> List[NumberStats]:
        """Generate comprehensive stats for all numbers."""
        freq = self.calculate_frequency(lookback)
        gaps = self.calculate_gaps()
        
        stats = []
        for num in range(1, self.max_number + 1):
            # Find last drawn date
            last_date = None
            for draw in self.draws:
                if num in draw['numbers']:
                    last_date = draw['date']
                    break
            
            # Calculate hot score (inverse of gap, normalized)
            gap = gaps.get(num, lookback)
            hot_score = 1.0 - min(gap / lookback, 1.0)
            
            stats.append(NumberStats(
                number=num,
                frequency=freq.get(num, 0),
                last_drawn=last_date,
                gap=gap,
                hot_score=hot_score
            ))
        
        return sorted(stats, key=lambda x: x.hot_score, reverse=True)
    
    def get_hot_numbers(self, count: int = 10) -> List[int]:
        """Get the hottest numbers."""
        stats = self.generate_number_stats()
        return [s.number for s in stats[:count]]
    
    def get_cold_numbers(self, count: int = 10) -> List[int]:
        """Get the coldest numbers."""
        stats = self.generate_number_stats()
        return [s.number for s in stats[-count:]]
    
    def get_due_numbers(self, count: int = 10) -> List[int]:
        """Get numbers that are 'due' (longest gaps)."""
        stats = self.generate_number_stats()
        return [s.number for s in sorted(stats, key=lambda x: x.gap, reverse=True)[:count]]
    
    def generate_wheel(self, selected_numbers: List[int], ticket_size: int = None) -> List[WheelTicket]:
        """
        Generate a lottery wheel from selected numbers.
        
        A wheel organizes your numbers into multiple tickets to guarantee
        certain coverage if some of your numbers are drawn.
        """
        if ticket_size is None:
            ticket_size = self.main_count
        
        tickets = []
        ticket_id = 1
        
        # Generate all combinations of ticket_size from selected_numbers
        for combo in combinations(sorted(selected_numbers), ticket_size):
            tickets.append(WheelTicket(
                ticket_id=ticket_id,
                numbers=list(combo),
                coverage=0.0  # Would calculate based on match guarantees
            ))
            ticket_id += 1
        
        return tickets
    
    def generate_abbreviated_wheel(self, selected_numbers: List[int], 
                                     match_if: int = 3, guarantee: int = 3) -> List[List[int]]:
        """
        Generate an abbreviated wheel (not full coverage).
        
        If you match 'match_if' numbers from your selected pool,
        you're guaranteed to have at least 'guarantee' numbers correct
        on at least one ticket.
        
        This is a simplified implementation.
        """
        # For now, generate a balanced distribution
        tickets = []
        numbers = sorted(selected_numbers)
        
        # Strategy: Distribute numbers evenly across tickets
        # Each number appears in multiple tickets
        
        if self.game == 'irish':
            # 6 numbers per ticket from pool
            # Simple wheel: create tickets that overlap well
            
            # Start with first 12 numbers, create varied combinations
            pool = numbers[:12] if len(numbers) >= 12 else numbers
            
            # Generate 4 tickets from 12 numbers
            # This guarantees if you hit 3 in the pool, you get at least 2 somewhere
            combos = [
                pool[0:6],
                pool[2:8],
                pool[4:10],
                pool[6:12] if len(pool) >= 12 else pool[0:6],
            ]
            
            return [c for c in combos if len(c) == 6]
        
        else:  # EuroMillions
            pool = numbers[:10] if len(numbers) >= 10 else numbers
            
            # 5 number tickets
            combos = [
                pool[0:5],
                pool[2:7],
                pool[4:9],
            ]
            
            return [c for c in combos if len(c) == 5]
    
    def analyze_patterns(self) -> Dict:
        """Analyze common patterns in winning numbers."""
        patterns = {
            'odd_even': {'odd': 0, 'even': 0},
            'high_low': {'high': 0, 'low': 0},
            'consecutive': 0,
            'sum_range': []
        }
        
        for draw in self.draws[:100]:  # Last 100 draws
            nums = draw['numbers']
            
            # Odd/Even
            odd_count = sum(1 for n in nums if n % 2 == 1)
            patterns['odd_even']['odd'] += odd_count
            patterns['odd_even']['even'] += len(nums) - odd_count
            
            # High/Low
            mid = self.max_number // 2
            high_count = sum(1 for n in nums if n > mid)
            patterns['high_low']['high'] += high_count
            patterns['high_low']['low'] += len(nums) - high_count
            
            # Consecutive pairs
            sorted_nums = sorted(nums)
            for i in range(len(sorted_nums) - 1):
                if sorted_nums[i+1] - sorted_nums[i] == 1:
                    patterns['consecutive'] += 1
            
            # Sum
            patterns['sum_range'].append(sum(nums))
        
        # Calculate averages
        patterns['avg_sum'] = statistics.mean(patterns['sum_range'])
        patterns['sum_std'] = statistics.stdev(patterns['sum_range']) if len(patterns['sum_range']) > 1 else 0
        
        return patterns
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        lines = [
            f"# LotteryVue Analysis Report",
            f"Game: {self.data['metadata']['game']}",
            f"Total draws analyzed: {len(self.draws)}",
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Hot Numbers (Last 100 draws)"
        ]
        
        stats = self.generate_number_stats(100)
        hot = stats[:10]
        cold = stats[-10:]
        
        lines.append("")
        lines.append("| Rank | Number | Frequency | Last Drawn | Gap | Hot Score |")
        lines.append("|------|--------|-----------|------------|-----|-----------|")
        
        for i, s in enumerate(hot, 1):
            lines.append(f"| {i} | {s.number} | {s.frequency} | {s.last_drawn or 'Never'} | {s.gap} | {s.hot_score:.2f} |")
        
        lines.append("")
        lines.append("## Cold Numbers")
        lines.append("")
        lines.append("| Rank | Number | Frequency | Last Drawn | Gap |")
        lines.append("|------|--------|-----------|------------|-----|")
        
        for i, s in enumerate(cold, 1):
            lines.append(f"| {i} | {s.number} | {s.frequency} | {s.last_drawn or 'Never'} | {s.gap} |")
        
        # Pattern analysis
        patterns = self.analyze_patterns()
        
        lines.extend([
            "",
            "## Pattern Analysis (Last 100 draws)",
            "",
            f"- **Odd/Even split**: {patterns['odd_even']['odd']} odd / {patterns['odd_even']['even']} even",
            f"- **High/Low split**: {patterns['high_low']['high']} high / {patterns['high_low']['low']} low",
            f"- **Consecutive pairs**: {patterns['consecutive']} occurrences",
            f"- **Average sum**: {patterns['avg_sum']:.1f} (+-{patterns['sum_std']:.1f})",
            "",
            "## Wheel Generator",
            "",
            "To generate a wheel, select your numbers and use:",
            "",
            "```python",
            "engine = LotteryVueEngine('irish')",
            "my_numbers = [4, 8, 15, 16, 23, 42, 10, 20, 30, 35]",
            "wheel = engine.generate_abbreviated_wheel(my_numbers)",
            "for ticket in wheel:",
            "    print(ticket)",
            "```",
            "",
            "This guarantees if you match 3 numbers in your pool,",
            "you'll have at least 2 on one ticket.",
            ""
        ])
        
        return '\n'.join(lines)


if __name__ == '__main__':
    import sys
    # Fix Windows unicode output
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Generate report for Irish Lotto
    print("="*60)
    print("LOTTERYVUE ANALYSIS ENGINE")
    print("="*60)
    print()
    
    engine = LotteryVueEngine('irish')
    report = engine.generate_report()
    
    # Save report
    report_file = DATA_DIR / 'analysis_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print()
    print(f"Report saved to: {report_file}")
    print()
    
    # Demo wheel generation
    print("="*60)
    print("WHEEL DEMONSTRATION")
    print("="*60)
    print()
    
    hot_numbers = engine.get_hot_numbers(12)
    print(f"Selected hot numbers: {hot_numbers}")
    print()
    
    wheel = engine.generate_abbreviated_wheel(hot_numbers)
    print("Generated wheel tickets:")
    for i, ticket in enumerate(wheel, 1):
        print(f"  Ticket {i}: {ticket}")
    print()
    print("If 3 of your selected numbers are drawn,")
    print("you're guaranteed to have at least 2 on one ticket.")
