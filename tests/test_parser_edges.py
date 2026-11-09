from datetime import date

import pytest

from nldate import parse


@pytest.mark.parametrize(
    ("expression", "reference", "expected"),
    [
        ("  NeXt \t TUESDAY\n", date(2025, 11, 11), date(2025, 11, 18)),
        ("last Tuesday", date(2025, 11, 11), date(2025, 11, 4)),
        (" DECEMBER  1st , 2025 ", date(2025, 1, 1), date(2025, 12, 1)),
        ("Feb 29th, 2024", date(2025, 1, 1), date(2024, 2, 29)),
        ("2024-02-29", date(2025, 1, 1), date(2024, 2, 29)),
        ("in 1 month", date(2024, 1, 31), date(2024, 2, 29)),
        ("1 month ago", date(2025, 3, 31), date(2025, 2, 28)),
        ("in 1 year", date(2024, 2, 29), date(2025, 2, 28)),
        ("in 1 year and 1 month", date(2024, 2, 29), date(2025, 3, 29)),
        ("in 1 month and 1 day", date(2025, 1, 31), date(2025, 3, 1)),
        ("in 2 weeks", date(2025, 12, 25), date(2026, 1, 8)),
        ("1 year and 2 months after yesterday", date(2025, 11, 10), date(2027, 1, 9)),
        ("1 week, 2 days ago", date(2025, 11, 10), date(2025, 11, 1)),
        ("in 1 year, 2 months, and 3 days", date(2025, 1, 1), date(2026, 3, 4)),
        ("in 0 days", date(2025, 1, 1), date(2025, 1, 1)),
        ("1 day after 2 days before tomorrow", date(2025, 1, 1), date(2025, 1, 1)),
    ],
)
def test_calendar_expressions(expression: str, reference: date, expected: date) -> None:
    assert parse(expression, reference) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "   ",
        "February 29, 2025",
        "April 31st, 2025",
        "December 0, 2025",
        "in -1 day",
        "in 1.5 days",
        "in 3 days garbage",
        "in 1 day and",
        "in 1 day,",
        "in 1 day and and 2 days",
        "next someday",
        "1 day before",
        "in days",
        "in 100000000000000000000 years",
        "9999-12-32",
    ],
)
def test_invalid_expressions(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, date(2025, 1, 1))


@pytest.mark.parametrize(
    ("expression", "reference"),
    [
        ("yesterday", date.min),
        ("tomorrow", date.max),
        ("in 1 month", date.max),
        ("1 year ago", date.min),
    ],
)
def test_range_errors(expression: str, reference: date) -> None:
    with pytest.raises(ValueError):
        parse(expression, reference)


def test_default_reference() -> None:
    before = date.today()
    result = parse("today")
    assert before <= result <= date.today()
