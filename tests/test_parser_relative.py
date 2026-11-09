from datetime import date, timedelta

import pytest

from nldate import parse


@pytest.mark.parametrize(
    ("expression", "offset"),
    [
        ("the day after tomorrow", 2),
        ("day after tomorrow", 2),
        ("the day before yesterday", -2),
        ("day before yesterday", -2),
        ("the day after yesterday", 0),
        ("the day before tomorrow", 0),
        ("day after yesterday", 0),
        ("day before tomorrow", 0),
        ("two days from now", 2),
        ("two days ago", -2),
        ("  THE DAY\tAFTER\nTOMORROW ", 2),
    ],
)
@pytest.mark.parametrize(
    ("reference", "two_days_before", "two_days_after"),
    [
        (date(2025, 11, 10), date(2025, 11, 8), date(2025, 11, 12)),
        (date(2025, 1, 31), date(2025, 1, 29), date(2025, 2, 2)),
        (date(2025, 3, 1), date(2025, 2, 27), date(2025, 3, 3)),
        (date(2024, 2, 28), date(2024, 2, 26), date(2024, 3, 1)),
        (date(2025, 12, 31), date(2025, 12, 29), date(2026, 1, 2)),
        (date(2026, 1, 1), date(2025, 12, 30), date(2026, 1, 3)),
    ],
)
def test_conversational_dates(
    expression: str,
    offset: int,
    reference: date,
    two_days_before: date,
    two_days_after: date,
) -> None:
    expected = {-2: two_days_before, 0: reference, 2: two_days_after}[offset]
    assert parse(expression, today=reference) == expected


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("two days after the day after tomorrow", date(2025, 11, 14)),
        ("the day before two days from now", date(2025, 11, 11)),
        ("the day after the day before yesterday", date(2025, 11, 9)),
        ("the day after December 31, 2025", date(2026, 1, 1)),
    ],
)
def test_conversational_dates_in_longer_expressions(
    expression: str, expected: date
) -> None:
    assert parse(expression, today=date(2025, 11, 10)) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "the day after tomorrow garbage",
        "the day before",
        "the day after",
        "the day",
        "the days after tomorrow",
        "the the day after tomorrow",
        "someday after tomorrow",
        "the day after tomorrow ago",
        "the two days ago",
        "two days from now garbage",
        "two days ago tomorrow",
    ],
)
def test_reject_malformed_conversational_dates(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, today=date(2025, 11, 10))


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("a day ago", date(2025, 11, 9)),
        ("a week ago", date(2025, 11, 3)),
        ("a month ago", date(2025, 10, 10)),
        ("a year ago", date(2024, 11, 10)),
        ("one week ago", date(2025, 11, 3)),
        ("1 week ago", date(2025, 11, 3)),
        ("a week from now", date(2025, 11, 17)),
        ("in a week", date(2025, 11, 17)),
        ("a month from today", date(2025, 12, 10)),
        ("two weeks ago", date(2025, 10, 27)),
        ("three days from now", date(2025, 11, 13)),
        ("  A WEEK\tFROM\nTODAY ", date(2025, 11, 17)),
        ("a week and two days ago", date(2025, 11, 1)),
        ("in a year, two months, and three days", date(2027, 1, 13)),
        ("one day after a week before tomorrow", date(2025, 11, 5)),
        ("a day after two weeks from now", date(2025, 11, 25)),
        ("a week before next Tuesday", date(2025, 11, 4)),
        ("a day after Dec. 1, 2025", date(2025, 12, 2)),
        ("two days before 2025/12/04", date(2025, 12, 2)),
    ],
)
def test_relative_forms(expression: str, expected: date) -> None:
    assert parse(expression, today=date(2025, 11, 10)) == expected


@pytest.mark.parametrize(
    ("count", "word"),
    list(
        enumerate(
            [
                "zero",
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
                "ten",
                "eleven",
                "twelve",
                "thirteen",
                "fourteen",
                "fifteen",
                "sixteen",
                "seventeen",
                "eighteen",
                "nineteen",
                "twenty",
            ]
        )
    ),
)
@pytest.mark.parametrize("unit", ["days", "weeks", "months", "years"])
@pytest.mark.parametrize("form", ["in {}", "{} ago", "{} from now", "{} from today"])
def test_written_quantities(count: int, word: str, unit: str, form: str) -> None:
    reference = date(2050, 6, 15)
    assert parse(form.format(f"{word} {unit}"), reference) == parse(
        form.format(f"{count} {unit}"), reference
    )
    if unit == "days":
        direction = -1 if form == "{} ago" else 1
        assert parse(form.format(f"{word} {unit}"), reference) == reference + timedelta(
            days=count * direction
        )


@pytest.mark.parametrize(
    ("expression", "reference", "expected"),
    [
        ("in a month", date(2024, 1, 31), date(2024, 2, 29)),
        ("a month from today", date(2025, 1, 31), date(2025, 2, 28)),
        ("a month ago", date(2024, 3, 31), date(2024, 2, 29)),
        ("one month ago", date(2025, 3, 31), date(2025, 2, 28)),
        ("a year from now", date(2024, 2, 29), date(2025, 2, 28)),
        ("a year ago", date(2024, 2, 29), date(2023, 2, 28)),
        ("four years from today", date(2024, 2, 29), date(2028, 2, 29)),
        ("a month and a day from now", date(2025, 1, 31), date(2025, 3, 1)),
        ("a year and a month ago", date(2024, 2, 29), date(2023, 1, 29)),
        ("a week ago", date(2025, 1, 3), date(2024, 12, 27)),
    ],
)
def test_calendar_boundaries(expression: str, reference: date, expected: date) -> None:
    assert parse(expression, reference) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "an hour ago",
        "in an hour",
        "a minute from now",
        "one second ago",
        "in a weeks",
        "an day ago",
        "a ago",
        "a week",
        "week ago",
        "one two weeks ago",
        "twenty one days ago",
        "half a week ago",
        "a couple weeks ago",
        "in minus one day",
        "in -one day",
        "a week from yesterday",
        "a week from",
        "from now",
        "in a week ago",
        "a week ago from now",
        "a week from now garbage",
        "a week and ago",
        "a week, from today",
        "a week and and a day ago",
        "one dayand two days ago",
        "one daytwo weeks ago",
        "in a month and an hour",
        "one weekday ago",
    ],
)
def test_reject_invalid_relative_forms(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, date(2025, 1, 1))


@pytest.mark.parametrize(
    ("expression", "reference"),
    [
        ("a day ago", date.min),
        ("a week from now", date.max),
        ("in twenty years", date.max),
        ("a month ago", date.min),
        ("the day before yesterday", date.min),
        ("the day after tomorrow", date.max),
    ],
)
def test_relative_range_errors(expression: str, reference: date) -> None:
    with pytest.raises(ValueError):
        parse(expression, reference)
