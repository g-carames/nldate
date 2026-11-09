# nldate

A deterministic English date parser using only the Python standard library.

```python
from datetime import date
from nldate import parse

parse("1 year and 2 months after yesterday", today=date(2025, 11, 10))
# datetime.date(2027, 1, 9)
```

`parse(expression, today=None)` returns a `datetime.date`, using the local
current date when `today` is omitted. Supported expressions include:

- `today`, `tomorrow`, `yesterday`
- `in 3 days`, `5 days ago`, `in 1 year, 2 months, and 3 days`
- `next Tuesday`, `last Friday`
- `December 1st, 2025`, `Dec 1 2025`, `2025-12-01`
- `1 December 2025`, `1st Dec, 2025`
- `2025/12/04`, `2025/12/4`, `12/04/2025`, `12-04-2025`
- `5 days before December 1st, 2025`, `1 month after next Tuesday`
- Nested expressions such as `1 day after 2 days before tomorrow`

Capitalization and repeated whitespace are ignored. Offsets accept nonnegative
integer quantities in days, weeks, months, and years, separated by spaces,
commas, or `and`. Years and months are combined and applied first, clamping the
day to the destination month's last day; weeks and days are applied afterward.
For example, one month after January 31, 2025 is February 28, 2025. Next/last
weekdays strictly exclude the reference day.

Numeric dates require a four-digit year and use year/month/day when the year
comes first, or month/day/year when it comes last. Month and day may each have
one or two digits. Use the same separator (`/` or `-`) throughout a date;
day/month/year numeric dates and two-digit years are unsupported.

Unrecognized, empty, invalid, and out-of-range expressions raise `ValueError`.
Supported years are 1–9999. Spelled-out numbers, fractional offsets, times,
time zones, and other languages are unsupported.
