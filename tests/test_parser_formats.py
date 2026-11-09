import calendar
from datetime import date

import pytest

from nldate import parse


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("Dec. 1, 2025", date(2025, 12, 1)),
        ("Dec 1, 2025", date(2025, 12, 1)),
        ("Jan. 15, 2026", date(2026, 1, 15)),
        ("Sept. 5, 2025", date(2025, 9, 5)),
        ("Sept 5 2025", date(2025, 9, 5)),
        ("December 1, 2025", date(2025, 12, 1)),
        ("December 1st, 2025", date(2025, 12, 1)),
        ("1 December 2025", date(2025, 12, 1)),
        ("  dEc.\t1ST ,\n2025  ", date(2025, 12, 1)),
        ("1st DEC.,2025.", date(2025, 12, 1)),
        ("December 1 2025.", date(2025, 12, 1)),
        ("1 day after Dec. 1, 2025", date(2025, 12, 2)),
        ("1 month before 5 Sept. 2025", date(2025, 8, 5)),
    ],
)
def test_named_date_variations(expression: str, expected: date) -> None:
    assert parse(expression, today=date(2030, 1, 1)) == expected


@pytest.mark.parametrize(
    ("month_number", "month"),
    list(enumerate(calendar.month_abbr[1:], start=1)),
)
@pytest.mark.parametrize("period", ["", "."])
@pytest.mark.parametrize("day_first", [False, True])
def test_all_month_abbreviations(
    month_number: int, month: str, period: str, day_first: bool
) -> None:
    expression = (
        f"15 {month}{period} 2025" if day_first else f"{month}{period} 15, 2025"
    )
    assert parse(expression) == date(2025, month_number, 15)


@pytest.mark.parametrize(
    "expression",
    [
        "2025/12/04",
        "2025-12-04",
        "12/04/2025",
        "12-04-2025",
        "2025/12/4",
        "2025-12-4",
        "12/4/2025",
        "12-4-2025",
    ],
)
def test_numeric_formats(expression: str) -> None:
    assert parse(expression) == date(2025, 12, 4)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2025/1/2", date(2025, 1, 2)),
        ("2025-1-2", date(2025, 1, 2)),
        ("1/2/2025", date(2025, 1, 2)),
        ("1-2-2025", date(2025, 1, 2)),
        ("2024/02/29", date(2024, 2, 29)),
        ("02-29-2024", date(2024, 2, 29)),
        ("0001/1/1", date.min),
        ("12/31/9999", date.max),
        ("  2025/12/04  ", date(2025, 12, 4)),
        ("1 day after 2025/12/04", date(2025, 12, 5)),
        ("1 month before 12-04-2025", date(2025, 11, 4)),
        ("4 December 2025", date(2025, 12, 4)),
        ("4th Dec, 2025", date(2025, 12, 4)),
        ("  4TH  DECEMBER  2025 ", date(2025, 12, 4)),
        ("29 Feb 2024", date(2024, 2, 29)),
        ("1 day after 4 December 2025", date(2025, 12, 5)),
    ],
)
def test_additional_formats(expression: str, expected: date) -> None:
    assert parse(expression, today=date(2030, 1, 1)) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "2025/02/29",
        "2025-02-29",
        "02/29/2025",
        "02-29-2025",
        "2025/04/31",
        "04-31-2025",
        "2025/00/04",
        "2025/13/04",
        "00/04/2025",
        "13-04-2025",
        "2025/12/00",
        "12/32/2025",
        "0000/12/04",
        "12-04-0000",
        "10000/12/04",
        "12/04/10000",
        "2025/12-04",
        "12-04/2025",
        "25/12/04",
        "12/04/25",
        "2025/012/04",
        "2025/12/004",
        "2025/12/04 garbage",
        "garbage 12/04/2025",
        "29 February 2025",
        "31 Apr 2025",
        "0 December 2025",
        "4 Unknown 2025",
        "Feb. 29, 2025",
        "31 Apr. 2025",
        "Dec.. 1, 2025",
        "De.c 1, 2025",
        "Dec. 1, 2025 garbage",
    ],
)
def test_invalid_formats(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression)
