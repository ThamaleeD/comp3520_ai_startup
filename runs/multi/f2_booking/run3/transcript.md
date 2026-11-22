### PM

Here is the numbered list of requirements and edge cases for developers building the `book_shift` feature based on the spec:

### Input & General Rules
1. **Immutability:** The function must not modify the input `shifts` list under any circumstances (even if the result is `"OK"`).
2. **Staff Name Handling:** Staff names in the `shifts` list and the `staff` argument should be treated consistently (ensure proper matching for overlap and weekly hour calculations).

### Validation & Error Ordering (Strict Priority)
Developers must check rules in the exact order specified below, returning the first matching error string.

3. **Rule 1: Date Format & Validity (`"INVALID_DATE"`)**
   - The `date` parameter must strictly follow the `"MM-DD-YY"` format.
   - It must represent a real, valid calendar date (e.g., rejecting invalid months like `"13-01-26"` or invalid days like `"02-30-26"`).
   - Incorrect separators (e.g., `"11/16/26"` or `"2026-11-16"`) must trigger `"INVALID_DATE"`.

4. **Rule 2: Time Format & Logic (`"INVALID_TIME"`)**
   - The `start` and `end` parameters must strictly follow the `"HH:MM:SS"` format on a 24-hour clock.
   - They must represent valid times (hours 00–23, minutes 00–59, seconds 00–59).
   - **No Overnight Shifts:** The `end` time must be strictly after the `start` time on the same calendar day. Equal start and end times, or an end time earlier than the start time, must return `"INVALID_TIME"`.

5. **Rule 3: Schedule Overlap (`"OVERLAP"`)**
   - Check existing shifts in the `shifts` list for the same staff member on the same `date`.
   - Different staff members can have overlapping shifts on the same date without triggering an overlap.
   - **Touching Shifts:** Shifts that touch consecutively are allowed (e.g., Shift A ends at 13:00:00, Shift B starts at 13:00:00).
   - Any actual overlap in time between a staff member's existing shift and the new proposed shift must return `"OVERLAP"`.

6. **Rule 4: Maximum Daily Limit (`"TOO_LONG"`)**
   - Calculate total scheduled time for the day (including the new shift) and subtract a mandatory 30-minute unpaid break.
   - If the resulting daily work hours exceed 12 hours (e.g., 13 hours worked), return `"TOO_LONG"`. Exactly 12 hours is permitted to pass this check and move to rule 5.

7. **Rule 5: Approval Thresholds (`"NEEDS_APPROVAL"`)**
   - **Daily Extended Hours:** If hours worked on that single day exceed 8 hours and are up to (or equal to) 12 hours, return `"NEEDS_APPROVAL"`.
   - **Weekly Extended Hours:** A week runs Monday to Sunday. Sum the total work hours (each shift minus its 30-minute break) for the staff member across the entire Monday–Sunday week containing the target date, including the new shift. If the total weekly hours exceed 40 hours, return `"NEEDS_APPROVAL"`.

8. **Rule 6: Standard Shift (`"OK"`)**
   - If all previous rules pass, and daily hours do not exceed 8 and weekly hours do not exceed 40, return `"OK"`.

### Edge Cases to Handle
9. **Break Deduction Mechanics:** Ensure the 30-minute break is subtracted per working day, not per individual shift if a worker has multiple shifts in a single day (verify how multi-shift days accumulate hours and breaks).
10. **Leap Years:** Ensure date validation correctly handles leap years (e.g., Feb 29 on valid leap years).
11. **Boundary Times:** Test exact hour boundaries (e.g., shifts totaling exactly 8 hours vs. 8 hours and 1 minute, and weekly totals hitting exactly 40 hours vs. 40.5 hours).
12. **Empty Shifts List:** Ensure the function behaves correctly when `shifts` is empty (`[]`).

### Architect

# Architecture Design: `booking.py`

This document outlines the architecture, data flow, helper functions, and exact execution order for the `book_shift` feature in `booking.py`.

---

## 1. Helper Functions & Utilities

To keep the main `book_shift` function clean and maintainable, the module will rely on several focused helper functions:

- **`parse_date(date_str: str) -> datetime.date | None`**
  - Validates that `date_str` strictly matches `MM-DD-YY` format and is a valid calendar date (leveraging Python's `datetime.strptime` and handling leap years). Returns a `datetime.date` object or `None` if invalid.

- **`parse_time(time_str: str) -> datetime.time | None`**
  - Validates that `time_str` strictly matches `HH:MM:SS` format and represents a valid time (00:00:00 to 23:59:59). Returns a `datetime.time` object or `None` if invalid.

- **`calculate_shift_duration_minutes(start: datetime.time, end: datetime.time) -> int`**
  - Converts start and end times into total seconds/minutes elapsed. Assumes `end > start` (validation handled separately).

- **`get_week_bounds(target_date: datetime.date) -> tuple[datetime.date, datetime.date]`**
  - Given any date, calculates the Monday and Sunday of that same calendar week (Monday–Sunday definition).

---

## 2. Data Flow & Core Logic

When `book_shift(shifts, staff, date, start, end)` is invoked, the execution flows strictly through the following sequential validation pipeline. 

### Step-by-Step Validation Order

1. **Rule 1: Date Format & Validity**
   - Call `parse_date(date)`. 
   - If it returns `None`, immediately return `"INVALID_DATE"`.

2. **Rule 2: Time Format & Logic**
   - Call `parse_time(start)` and `parse_time(end)`.
   - If either returns `None`, return `"INVALID_TIME"`.
   - Check if `end <= start` (using `datetime.time` comparison). If true, return `"INVALID_TIME"` (enforces no overnight shifts and prevents zero/negative duration).

3. **Rule 3: Schedule Overlap**
   - Filter the input `shifts` list for entries where `shift["staff"]` matches the target `staff` (case-sensitive or normalized based on team convention, though names are typically matching strings) and `shift["date"] == date`.
   - For each existing shift of this staff member on this date, parse its start and time strings.
   - Check for time intersection with the new proposed shift `[start, end]`. 
     - *Overlap condition:* Existing shift start < New shift end **AND** Existing shift end > New shift start.
     - *Touching:* If an existing shift ends exactly when the new one starts (or vice versa), this is permitted.
   - If any actual overlap is detected, return `"OVERLAP"`.

4. **Rule 4: Maximum Daily Limit (`TOO_LONG`)**
   - Gather all shifts for this staff member on this `date` (including the new proposed shift).
   - Calculate total raw scheduled minutes across all shifts on this day.
   - **Break Deduction Rule:** Subtract a single 30-minute unpaid break for the day (applied once per calendar day regardless of how many shifts the staff member works that day).
   - Convert total working minutes to hours.
   - If daily work hours **exceed 12 hours** (i.e., `> 12.0`), return `"TOO_LONG"`. (Exactly 12.0 hours passes this check).

5. **Rule 5: Approval Thresholds (`NEEDS_APPROVAL`)**
   - **Check Daily Extended Hours:** If the calculated daily work hours (from Step 4) are **greater than 8 hours** and **less than or equal to 12 hours**, return `"NEEDS_APPROVAL"`.
   - **Check Weekly Extended Hours:** 
     - Determine the Monday–Sunday date range for the target `date` using `get_week_bounds`.
     - Filter all shifts in `shifts` belonging to this staff member that fall within this Monday–Sunday date range, plus include the new proposed shift.
     - Group these shifts by date. For *each unique working day* in this week, calculate that day's total shift duration minus a single 30-minute break.
     - Sum these daily net work hours across the entire week.
     - If the total weekly hours **exceed 40 hours** (i.e., `> 40.0`), return `"NEEDS_APPROVAL"`.

6. **Rule 6: Standard Shift (`OK`)**
   - If all checks pass and hours are within normal limits ($\le 8$ hours/day and $\le 40$ hours/week), return `"OK"`.
   - Ensure the input `shifts` list remains completely unmodified.

### Developer

```python
from datetime import datetime, date, time, timedelta

def parse_date(date_str: str) -> date | None:
    """
    Validates that date_str strictly matches MM-DD-YY format and is a valid calendar date.
    Returns a datetime.date object or None if invalid.
    """
    if not isinstance(date_str, str):
        return None
    try:
        dt = datetime.strptime(date_str, "%m-%d-%y")
        return dt.date()
    except ValueError:
        return None

def parse_time(time_str: str) -> time | None:
    """
    Validates that time_str strictly matches HH:MM:SS format and represents a valid time.
    Returns a datetime.time object or None if invalid.
    """
    if not isinstance(time_str, str):
        return None
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S")
        return dt.time()
    except ValueError:
        return None

def time_to_minutes(t: time) -> int:
    """Converts a datetime.time object to total minutes since midnight."""
    return t.hour * 60 + t.minute + t.seconds / 60.0

def get_week_bounds(target_date: date) -> tuple[date, date]:
    """
    Given any date, calculates the Monday and Sunday of that same calendar week (Monday–Sunday definition).
    """
    # weekday(): Monday is 0, Sunday is 6
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def book_shift(shifts: list[dict], staff: str, date: str, start: str, end: str) -> str:
    """
    Books a shift for a staff member after validating format, overlap, daily limits, 
    and weekly approval thresholds.
    """
    # 1. Rule 1: Date Format & Validity
    parsed_date = parse_date(date)
    if parsed_date is None:
        return "INVALID_DATE"

    # 2. Rule 2: Time Format & Logic
    parsed_start = parse_time(start)
    parsed_end = parse_time(end)
    if parsed_start is None or parsed_end is None:
        return "INVALID_TIME"
    
    # Enforce no overnight shifts and strict end > start
    if parsed_end <= parsed_start:
        return "INVALID_TIME"

    # Normalize staff name for comparison
    target_staff = staff.strip().lower()

    # 3. Rule 3: Schedule Overlap
    # Filter existing shifts for the same staff member on the same date
    staff_day_shifts = []
    for s in shifts:
        if s.get("staff", "").strip().lower() == target_staff and s.get("date") == date:
            s_start = parse_time(s.get("start", ""))
            s_end = parse_time(s.get("end", ""))
            if s_start and s_end:
                staff_day_shifts.append((s_start, s_end))

    # Check for overlap with proposed shift [parsed_start, parsed_end]
    # Overlap condition: Existing shift start < New end AND Existing shift end > New start
    for existing_start, existing_end in staff_day_shifts:
        if existing_start < parsed_end and existing_end > parsed_start:
            return "OVERLAP"

    # 4. Rule 4 & 5 Calculations: Daily and Weekly Hours
    # Collect all shifts for this staff member on this date, plus the new one
    all_day_shifts = list(staff_day_shifts)
    all_day_shifts.append((parsed_start, parsed_end))

    # Calculate total raw scheduled minutes for the day
    total_day_raw_minutes = sum(
        (time_to_minutes(e) - time_to_minutes(st)) for st, e in all_day_shifts
    )
    
    # Break Deduction Rule: 30-minute unpaid break once per calendar day
    daily_work_hours = (total_day_raw_minutes - 30) / 60.0

    # Rule 4: Maximum Daily Limit (strict > 12 hours is TOO_LONG)
    if daily_work_hours > 12.0:
        return "TOO_LONG"

    # Rule 5: Approval Thresholds
    # Daily Extended Hours: > 8 and <= 12 hours
    if daily_work_hours > 8.0:
        return "NEEDS_APPROVAL"

    # Weekly Extended Hours: Monday to Sunday total > 40 hours
    week_start, week_end = get_week_bounds(parsed_date)
    
    # Map all shifts for the staff member in the shifts list, grouped by date
    # First, aggregate staff shifts across the week by date string
    week_shifts_by_date = {}
    
    for s in shifts:
        if s.get("staff", "").strip().lower() == target_staff:
            s_date_str = s.get("date")
            s_date_obj = parse_date(s_date_str)
            if s_date_obj and week_start <= s_date_obj <= week_end:
                s_start = parse_time(s.get("start", ""))
                s_end = parse_time(s.get("end", ""))
                if s_start and s_end:
                    if s_date_str not in week_shifts_by_date:
                        week_shifts_by_date[s_date_str] = []
                    week_shifts_by_date[s_date_str].append((s_start, s_end))

    # Add/update the new proposed shift in the week's collection
    if date not in week_shifts_by_date:
        week_shifts_by_date[date] = []
    # If the new shift wasn't in the input list (which it shouldn't be), add it.
    # Note: staff_day_shifts didn't include the new shift initially, but all_day_shifts does.
    week_shifts_by_date[date] = all_day_shifts

    # Calculate total weekly hours (sum of net daily hours across unique working days)
    total_weekly_hours = 0.0
    for d_str, d_shifts in week_shifts_by_date.items():
        day_raw = sum((time_to_minutes(e) - time_to_minutes(st)) for st, e in d_shifts)
        day_net = (day_raw - 30) / 60.0
        total_weekly_hours += day_net

    if total_weekly_hours > 40.0:
        return "NEEDS_APPROVAL"

    # 6. Rule 6: Standard Shift
    return "OK"
```

### Tester

```python
from datetime import datetime, date, time, timedelta

def parse_date(date_str: str) -> date | None:
    """
    Validates that date_str strictly matches MM-DD-YY format and is a valid calendar date.
    Returns a datetime.date object or None if invalid.
    """
    if not isinstance(date_str, str):
        return None
    try:
        dt = datetime.strptime(date_str, "%m-%d-%y")
        return dt.date()
    except ValueError:
        return None

def parse_time(time_str: str) -> time | None:
    """
    Validates that time_str strictly matches HH:MM:SS format and represents a valid time.
    Returns a datetime.time object or None if invalid.
    """
    if not isinstance(time_str, str):
        return None
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S")
        return dt.time()
    except ValueError:
        return None

def time_to_minutes(t: time) -> float:
    """Converts a datetime.time object to total minutes since midnight."""
    return t.hour * 60 + t.minute + t.second / 60.0

def get_week_bounds(target_date: date) -> tuple[date, date]:
    """
    Given any date, calculates the Monday and Sunday of that same calendar week (Monday–Sunday definition).
    """
    # weekday(): Monday is 0, Sunday is 6
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def book_shift(shifts: list[dict], staff: str, date: str, start: str, end: str) -> str:
    """
    Books a shift for a staff member after validating format, overlap, daily limits, 
    and weekly approval thresholds.
    """
    # 1. Rule 1: Date Format & Validity
    parsed_date = parse_date(date)
    if parsed_date is None:
        return "INVALID_DATE"

    # 2. Rule 2: Time Format & Logic
    parsed_start = parse_time(start)
    parsed_end = parse_time(end)
    if parsed_start is None or parsed_end is None:
        return "INVALID_TIME"
    
    # Enforce no overnight shifts and strict end > start
    if parsed_end <= parsed_start:
        return "INVALID_TIME"

    # Normalize staff name for comparison (roles and staff names ignore case/extra spaces per spec rules)
    target_staff = staff.strip().lower()

    # 3. Rule 3: Schedule Overlap
    # Filter existing shifts for the same staff member on the same date
    staff_day_shifts = []
    for s in shifts:
        if s.get("staff", "").strip().lower() == target_staff and s.get("date") == date:
            s_start = parse_time(s.get("start", ""))
            s_end = parse_time(s.get("end", ""))
            if s_start and s_end:
                staff_day_shifts.append((s_start, s_end))

    # Check for overlap with proposed shift [parsed_start, parsed_end]
    # Overlap condition: Existing shift start < New end AND Existing shift end > New start
    for existing_start, existing_end in staff_day_shifts:
        if existing_start < parsed_end and existing_end > parsed_start:
            return "OVERLAP"

    # 4. Rule 4 & 5 Calculations: Daily and Weekly Hours
    # Collect all shifts for this staff member on this date, plus the new one
    all_day_shifts = list(staff_day_shifts)
    all_day_shifts.append((parsed_start, parsed_end))

    # Calculate total raw scheduled minutes for the day
    total_day_raw_minutes = sum(
        (time_to_minutes(e) - time_to_minutes(st)) for st, e in all_day_shifts
    )
    
    # Break Deduction Rule: 30-minute unpaid break once per calendar day
    daily_work_hours = (total_day_raw_minutes - 30) / 60.0

    # Rule 4: Maximum Daily Limit (strict > 12 hours is TOO_LONG)
    if daily_work_hours > 12.0:
        return "TOO_LONG"

    # Rule 5: Approval Thresholds
    # Daily Extended Hours: > 8 and <= 12 hours
    if daily_work_hours > 8.0:
        return "NEEDS_APPROVAL"

    # Weekly Extended Hours: Monday to Sunday total > 40 hours
    week_start, week_end = get_week_bounds(parsed_date)
    
    # Map all shifts for the staff member in the shifts list, grouped by date
    week_shifts_by_date = {}
    
    for s in shifts:
        if s.get("staff", "").strip().lower() == target_staff:
            s_date_str = s.get("date")
            s_date_obj = parse_date(s_date_str)
            if s_date_obj and week_start <= s_date_obj <= week_end:
                s_start = parse_time(s.get("start", ""))
                s_end = parse_time(s.get("end", ""))
                if s_start and s_end:
                    if s_date_str not in week_shifts_by_date:
                        week_shifts_by_date[s_date_str] = []
                    week_shifts_by_date[s_date_str].append((s_start, s_end))

    # Add/update the new proposed shift in the week's collection
    week_shifts_by_date[date] = all_day_shifts

    # Calculate total weekly hours (sum of net daily hours across unique working days)
    total_weekly_hours = 0.0
    for d_str, d_shifts in week_shifts_by_date.items():
        day_raw = sum((time_to_minutes(e) - time_to_minutes(st)) for st, e in d_shifts)
        day_net = (day_raw - 30) / 60.0
        total_weekly_hours += day_net

    if total_weekly_hours > 40.0:
        return "NEEDS_APPROVAL"

    # 6. Rule 6: Standard Shift
    return "OK"
```
