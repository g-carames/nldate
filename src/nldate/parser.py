"""Deterministic parsing of English calendar-date expressions."""

import calendar
import re
from datetime import date, timedelta

_MONTHS = {
    name.lower(): number
    for number in range(1, 13)
    for name in (calendar.month_name[number], calendar.month_abbr[number])
}
_WEEKDAYS = {name.lower(): number for number, name in enumerate(calendar.day_name)}
_OFFSET = re.compile(r"(\d+)\s+(days?|weeks?|months?|years?)")


def _offset(text: str) -> tuple[int, int]:
    """Read a complete offset, returning calendar months and elapsed days."""
    months = days = 0
    remaining = text
    while remaining:
        match = _OFFSET.match(remaining)
        if match is None:
            raise ValueError(f"Invalid offset: {text!r}")
        count = int(match[1])
        unit = match[2].rstrip("s")
        if unit == "year":
            months += count * 12
        elif unit == "month":
            months += count
        else:
            days += count * (7 if unit == "week" else 1)
        remaining = remaining[match.end() :]
        if not remaining:
            break
        separator = re.match(r"(?:,\s*(?:and\s+)?|\s+(?:and\s+)?)", remaining)
        if separator is None:
            raise ValueError(f"Invalid offset: {text!r}")
        remaining = remaining[separator.end() :]
        if not remaining:
            raise ValueError(f"Incomplete offset: {text!r}")
    if not text:
        raise ValueError("Empty offset")
    return months, days


def _shift(base: date, months: int, days: int) -> date:
    """Shift months once, clamping the day, then add elapsed days."""
    year, month_index = divmod(base.year * 12 + base.month - 1 + months, 12)
    if not 1 <= year <= 9999:
        raise ValueError("Date outside supported range (years 1–9999)")
    month = month_index + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day) + timedelta(days=days)


def _anchor(text: str, today: date) -> date:
    """Parse a named day, strict next/last weekday, or absolute date."""
    if text in {"today", "tomorrow", "yesterday"}:
        return today + timedelta(
            days={"today": 0, "tomorrow": 1, "yesterday": -1}[text]
        )
    weekday = re.fullmatch(r"(next|last) ([a-z]+)", text)
    if weekday and weekday[2] in _WEEKDAYS:
        difference = (_WEEKDAYS[weekday[2]] - today.weekday()) % 7
        if weekday[1] == "next":
            return today + timedelta(days=difference or 7)
        return today + timedelta(days=difference - 7)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return date.fromisoformat(text)
    absolute = re.fullmatch(
        r"([a-z]+) (\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*| )(\d{4})", text
    )
    if absolute and absolute[1] in _MONTHS:
        return date(int(absolute[3]), _MONTHS[absolute[1]], int(absolute[2]))
    raise ValueError(f"Unrecognized date expression: {text!r}")


def parse(s: str, today: date | None = None) -> date:
    """Parse an English date expression relative to ``today`` (default: today).

    Offsets use nonnegative integer quantities. Years/months are combined and
    applied before weeks/days, clamping to the destination month's last day.
    Next/last weekdays always exclude the reference day. Nested before/after
    expressions are evaluated from the innermost anchor outward.

    Raise ValueError for unrecognized expressions or dates outside years 1–9999.
    """
    text = " ".join(s.lower().split())
    reference = today if today is not None else date.today()
    pending: list[tuple[int, int]] = []
    try:
        while True:
            relative = re.fullmatch(r"(.+?) (before|after) (.+)", text)
            if relative:
                months, days = _offset(relative[1])
                direction = -1 if relative[2] == "before" else 1
                pending.append((months * direction, days * direction))
                text = relative[3]
                continue
            if text.startswith("in "):
                months, days = _offset(text[3:])
                result = _shift(reference, months, days)
            elif text.endswith(" ago"):
                months, days = _offset(text[:-4])
                result = _shift(reference, -months, -days)
            else:
                result = _anchor(text, reference)
            break
        for months, days in reversed(pending):
            result = _shift(result, months, days)
        return result
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"Invalid date expression: {s!r}") from exc
