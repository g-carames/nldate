from datetime import date

import pytest

from nldate import parse

REFERENCE_DATE = date(2025, 11, 10)


def test_today():
    assert parse("today", REFERENCE_DATE) == REFERENCE_DATE


def test_tomorrow():
    assert parse("tomorrow", REFERENCE_DATE) == date(2025, 11, 11)


def test_yesterday():
    assert parse("yesterday", REFERENCE_DATE) == date(2025, 11, 9)


def test_in_three_days():
    assert parse("in 3 days", REFERENCE_DATE) == date(2025, 11, 13)


def test_five_days_ago():
    assert parse("5 days ago", REFERENCE_DATE) == date(2025, 11, 5)


def test_next_tuesday():
    assert parse("next Tuesday", REFERENCE_DATE) == date(2025, 11, 11)


def test_last_friday():
    assert parse("last Friday", REFERENCE_DATE) == date(2025, 11, 7)


def test_absolute_date():
    assert parse("December 1st, 2025", REFERENCE_DATE) == date(2025, 12, 1)


def test_days_before_date():
    assert parse("5 days before December 1st, 2025", REFERENCE_DATE) == date(
        2025, 11, 26
    )


def test_invalid_input():
    with pytest.raises(ValueError):
        parse("hello world", REFERENCE_DATE)


def test_empty_input():
    with pytest.raises(ValueError):
        parse("", REFERENCE_DATE)
