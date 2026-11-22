"""Hidden tests for Feature 2: Shift booking.

Expected results were set by the team from specs/specs.md.
The AI under test never sees this file.
Week of Mon 11-16-26 to Sun 11-22-26.
"""
import copy
import pytest
from booking import book_shift


def s(staff, date, start, end):
    return {"staff": staff, "date": date, "start": start, "end": end}


def full_days(staff, dates, start="09:00:00", end="17:30:00"):
    return [s(staff, d, start, end) for d in dates]


MON_THU = ["11-16-26", "11-17-26", "11-18-26", "11-19-26"]
MON_FRI = MON_THU + ["11-20-26"]
LAST_WEEK = ["11-09-26", "11-10-26", "11-11-26", "11-12-26", "11-13-26"]

# (test id, existing shifts, (staff, date, start, end), expected)
CASES = [
    # --- normal day ---
    ("ok_8_hrs",            [], ("amy", "11-16-26", "09:00:00", "17:30:00"), "OK"),
    ("ok_short_shift",      [], ("amy", "11-16-26", "09:00:00", "13:00:00"), "OK"),
    # --- extended day ---
    ("approval_8_5_hrs",    [], ("amy", "11-16-26", "09:00:00", "18:00:00"), "NEEDS_APPROVAL"),
    ("approval_12_hrs",     [], ("amy", "11-16-26", "07:00:00", "19:30:00"), "NEEDS_APPROVAL"),
    ("too_long_12_5_hrs",   [], ("amy", "11-16-26", "06:30:00", "19:30:00"), "TOO_LONG"),
    ("too_long_13_hrs",     [], ("amy", "11-16-26", "06:00:00", "19:30:00"), "TOO_LONG"),
    # --- date format ---
    ("date_iso_format",     [], ("amy", "2026-11-16", "09:00:00", "17:00:00"), "INVALID_DATE"),
    ("date_not_real",       [], ("amy", "02-30-26", "09:00:00", "17:00:00"), "INVALID_DATE"),
    ("date_month_13",       [], ("amy", "13-01-26", "09:00:00", "17:00:00"), "INVALID_DATE"),
    # --- time format ---
    ("time_end_before",     [], ("amy", "11-16-26", "17:00:00", "09:00:00"), "INVALID_TIME"),
    ("time_end_equal",      [], ("amy", "11-16-26", "09:00:00", "09:00:00"), "INVALID_TIME"),
    ("time_hour_25",        [], ("amy", "11-16-26", "09:00:00", "25:00:00"), "INVALID_TIME"),
    ("time_no_seconds",     [], ("amy", "11-16-26", "09:00", "17:00"), "INVALID_TIME"),
    # --- overlap ---
    ("overlap_same_staff",  [s("amy", "11-16-26", "09:00:00", "13:00:00")],
                            ("amy", "11-16-26", "12:00:00", "16:00:00"), "OVERLAP"),
    ("overlap_inside",      [s("amy", "11-16-26", "09:00:00", "17:00:00")],
                            ("amy", "11-16-26", "10:00:00", "11:00:00"), "OVERLAP"),
    ("touching_ok",         [s("amy", "11-16-26", "09:00:00", "13:00:00")],
                            ("amy", "11-16-26", "13:00:00", "17:30:00"), "OK"),
    ("other_staff_ok",      [s("amy", "11-16-26", "09:00:00", "17:30:00")],
                            ("raj", "11-16-26", "09:00:00", "17:30:00"), "OK"),
    ("other_date_ok",       [s("amy", "11-17-26", "09:00:00", "17:30:00")],
                            ("amy", "11-16-26", "09:00:00", "17:30:00"), "OK"),
    # --- one break per day, across shifts ---
    ("two_shifts_8_hrs",    [s("amy", "11-16-26", "09:00:00", "13:00:00")],
                            ("amy", "11-16-26", "14:00:00", "18:30:00"), "OK"),
    ("two_shifts_over_8",   [s("amy", "11-16-26", "09:00:00", "13:00:00")],
                            ("amy", "11-16-26", "14:00:00", "19:00:00"), "NEEDS_APPROVAL"),
    ("two_shifts_over_12",  [s("amy", "11-16-26", "06:00:00", "12:00:00")],
                            ("amy", "11-16-26", "12:00:00", "19:00:00"), "TOO_LONG"),
    # --- weekly ---
    ("week_40_ok",          full_days("amy", MON_THU),
                            ("amy", "11-20-26", "09:00:00", "17:30:00"), "OK"),
    ("week_over_40_sat",    full_days("amy", MON_FRI),
                            ("amy", "11-21-26", "09:00:00", "10:00:00"), "NEEDS_APPROVAL"),
    ("week_over_40_sun",    full_days("amy", MON_FRI),
                            ("amy", "11-22-26", "09:00:00", "10:00:00"), "NEEDS_APPROVAL"),
    ("last_week_not_counted", full_days("amy", LAST_WEEK),
                            ("amy", "11-16-26", "09:00:00", "17:30:00"), "OK"),
    ("other_staff_week_not_counted", full_days("raj", MON_FRI),
                            ("amy", "11-21-26", "09:00:00", "17:30:00"), "OK"),
    # --- check order ---
    ("order_date_before_time", [], ("amy", "2026-11-16", "17:00:00", "09:00:00"), "INVALID_DATE"),
    ("order_overlap_before_too_long", [s("amy", "11-16-26", "09:00:00", "13:00:00")],
                            ("amy", "11-16-26", "06:00:00", "19:30:00"), "OVERLAP"),
]


@pytest.mark.parametrize("existing,new,expected",
                         [c[1:] for c in CASES], ids=[c[0] for c in CASES])
def test_book_shift(existing, new, expected):
    assert book_shift(existing, *new) == expected


def test_does_not_change_shifts_list():
    existing = [s("amy", "11-16-26", "09:00:00", "13:00:00")]
    before = copy.deepcopy(existing)
    book_shift(existing, "amy", "11-16-26", "13:00:00", "17:30:00")
    assert existing == before
