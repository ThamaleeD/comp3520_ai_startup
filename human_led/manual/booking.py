from datetime import datetime, timedelta
import re


DATE_FORMAT = "%m-%d-%y"
TIME_FORMAT = "%H:%M:%S"
BREAK_HOURS = 0.5
MAX_DAILY_HOURS = 16
MAX_WEEKLY_HOURS = 60


def parse_date(value):
    if not isinstance(value, str):
        return None

    if not re.fullmatch(r"\d{2}-\d{2}-\d{2}", value):
        return None

    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        return None


def parse_time(value):
    if not isinstance(value, str):
        return None

    if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", value):
        return None

    try:
        return datetime.strptime(value, TIME_FORMAT).time()
    except ValueError:
        return None


def scheduled_hours(start, end):
    start_seconds = (
        start.hour * 3600 + start.minute * 60 + start.second
    )
    end_seconds = (
        end.hour * 3600 + end.minute * 60 + end.second
    )

    return (end_seconds - start_seconds) / 3600


def book_shift(shifts, staff, date, start, end):
    # Rule 1: Validate the date.
    new_date = parse_date(date)

    if new_date is None:
        return "INVALID_DATE"

    # Rule 2: Validate times and reject overnight shifts.
    new_start = parse_time(start)
    new_end = parse_time(end)

    if (
        new_start is None
        or new_end is None
        or new_end <= new_start
    ):
        return "INVALID_TIME"

    # Collect existing shifts for this employee.
    staff_shifts = [
        shift for shift in shifts
        if shift["staff"] == staff
    ]

    # Rule 3: Detect overlapping shifts on the same date.
    for shift in staff_shifts:
        shift_date = parse_date(shift["date"])

        if shift_date != new_date:
            continue

        existing_start = parse_time(shift["start"])
        existing_end = parse_time(shift["end"])

        if new_start < existing_end and new_end > existing_start:
            return "OVERLAP"

    # Combine existing shifts with the proposed shift.
    proposed_shifts = staff_shifts + [{
        "staff": staff,
        "date": date,
        "start": start,
        "end": end,
    }]

    # Calculate total scheduled hours for each working day.
    daily_scheduled = {}

    for shift in proposed_shifts:
        shift_date = parse_date(shift["date"])
        shift_start = parse_time(shift["start"])
        shift_end = parse_time(shift["end"])

        hours = scheduled_hours(shift_start, shift_end)

        daily_scheduled[shift_date] = (
            daily_scheduled.get(shift_date, 0) + hours
        )

    # Apply one unpaid break per working day.
    daily_worked = {
        day: max(0, hours - BREAK_HOURS)
        for day, hours in daily_scheduled.items()
    }

    # Rule 4: Enforce the 16-hour daily limit.
    if daily_worked[new_date] > MAX_DAILY_HOURS:
        return "TOO_LONG"

    # Rule 5: Enforce the Monday-Sunday weekly limit.
    week_start = new_date - timedelta(days=new_date.weekday())
    week_end = week_start + timedelta(days=6)

    weekly_hours = sum(
        hours
        for day, hours in daily_worked.items()
        if week_start <= day <= week_end
    )

    if weekly_hours > MAX_WEEKLY_HOURS:
        return "OVER_HOURS"

    # Rule 6: Valid shift. Do not modify the original list.
    return "OK"
