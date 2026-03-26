# LotteryVue Analysis Report
Game: Irish Lotto
Total draws analyzed: 2028
Report generated: 2026-03-26 20:47:21

## Hot Numbers (Last 100 draws)

| Rank | Number | Frequency | Last Drawn | Gap | Hot Score |
|------|--------|-----------|------------|-----|-----------|
| 1 | 4 | 39 | 2026-03-25 | 0 | 1.00 |
| 2 | 6 | 39 | 2026-03-25 | 0 | 1.00 |
| 3 | 8 | 39 | 2026-03-25 | 0 | 1.00 |
| 4 | 19 | 39 | 2026-03-25 | 0 | 1.00 |
| 5 | 22 | 39 | 2026-03-25 | 0 | 1.00 |
| 6 | 27 | 39 | 2026-03-25 | 0 | 1.00 |
| 7 | 1 | 39 | 2026-03-21 | 39 | 0.61 |
| 8 | 5 | 39 | 2026-03-21 | 39 | 0.61 |
| 9 | 15 | 39 | 2026-03-21 | 39 | 0.61 |
| 10 | 17 | 39 | 2026-03-21 | 39 | 0.61 |

## Cold Numbers

| Rank | Number | Frequency | Last Drawn | Gap |
|------|--------|-----------|------------|-----|
| 1 | 34 | 0 | 2026-03-07 | 195 |
| 2 | 35 | 0 | 2026-02-21 | 351 |
| 3 | 36 | 0 | 2026-02-04 | 546 |
| 4 | 37 | 0 | 2026-03-14 | 117 |
| 5 | 38 | 0 | 2026-02-28 | 273 |
| 6 | 40 | 0 | 2026-03-11 | 156 |
| 7 | 41 | 0 | 2026-03-11 | 156 |
| 8 | 42 | 0 | 2026-03-14 | 117 |
| 9 | 43 | 0 | 2026-03-07 | 195 |
| 10 | 44 | 0 | 2026-02-21 | 351 |

## Pattern Analysis (Last 100 draws)

- **Odd/Even split**: 356 odd / 244 even
- **High/Low split**: 166 high / 434 low
- **Consecutive pairs**: 22 occurrences
- **Average sum**: 118.4 (+-43.4)

## Wheel Generator

To generate a wheel, select your numbers and use:

```python
engine = LotteryVueEngine('irish')
my_numbers = [4, 8, 15, 16, 23, 42, 10, 20, 30, 35]
wheel = engine.generate_abbreviated_wheel(my_numbers)
for ticket in wheel:
    print(ticket)
```

This guarantees if you match 3 numbers in your pool,
you'll have at least 2 on one ticket.
