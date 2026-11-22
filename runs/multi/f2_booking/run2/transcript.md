### PM

Here are the requirements and edge cases for developers implementing the `book_shift(shifts, staff, date, start, end)` feature. 

### Core Rules & Calculation Logic
1. **Unpaid Break Rule:** Every working day includes exactly one 30-minute unpaid break. Hours worked on any given day equal the total scheduled time minus 30 minutes.
2. **Work Week Definition:** A work week runs strictly from Monday to Sunday.
3. **Immutability:** The function must **not** modify the input `shifts` list under any circumstance.
4. **Validation Order:** Validation checks must execute strictly in the numerical order specified below. The function must return the result of the *first* rule that triggers.

---

### Numbered Requirements and Edge Cases

#### 1. Date Format & Validity Validation (`"INVALID_DATE"`)
1.1. The `date` parameter must strictly match the `MM-DD-YY` format (e.g., `"11-16-26"`).
1.2. **Edge Case:** Reject alternative formats like `YYYY-MM-DD` (e.g., `"2026-11-16"`), `DD-MM-YY`, or slashes (`"11/16/26"`).
1.3. **Edge Case:** Reject calendar dates that do not exist (e.g., `"02-30-26"`, `"13-01-26"`).
1.4. **Edge Case:** Handle leap years correctly if applicable to the provided two-digit year.

#### 2. Time Format & Range Validation (`"INVALID_TIME"`)
2.1. The `start` and `end` parameters must strictly match the `HH:MM:SS` 24-hour clock format (e.g., `"09:00:00"`).
2.2. **Edge Case:** Reject invalid time values (e.g., hours `>= 24`, minutes/seconds `>= 60`).
2.3. **Edge Case:** The `end` time must be strictly chronologically *after* the `start` time on the same day. 
2.4. **Edge Case:** Overnight shifts (where `end` is on the following calendar day, or `end <= start`) are forbidden and must trigger `"INVALID_TIME"`.
2.5. **Edge Case:** Zero-duration shifts (`start` equals `end`) must be rejected as invalid.

#### 3. Schedule Overlap Check (`"OVERLAP"`)
3.1. Different staff members are permitted to have overlapping shifts on the same date.
3.2. A single staff member's shifts **cannot** overlap with their own existing shifts on the same date.
3.3. **Edge Case (Touching Shifts):** Back-to-back shifts where one shift's end time equals the next shift's start time (e.g., shift 1 ends at `13:00:00`, shift 2 starts at `13:00:00`) are **valid** and must not trigger an overlap.
3.4. **Edge Case:** Partial overlaps, complete containment of one shift inside another, and duplicate identical shifts for the same staff member must trigger `"OVERLAP"`.

#### 4. Maximum Daily Limit Check (`"TOO_LONG"`)
4.1. Calculate the total hours worked by the staff member on the target date, inclusive of the proposed new shift (minus the 30-minute daily break).
4.2. If the total hours worked on that single day exceed **12 hours**, return `"TOO_LONG"`.
4.3. **Edge Case:** Exactly 12 hours worked is allowed (subject to approval rules); 12 hours + 1 second (or greater) triggers `"TOO_LONG"`.

#### 5. Management Approval Requirement (`"NEEDS_APPROVAL"`)
5.1. Calculate the daily hours worked (inclusive of the new shift). If daily hours worked exceed **8 hours**, return `"NEEDS_APPROVAL"`.
5.2. Calculate the cumulative weekly hours worked (Monday through Sunday of the target date's week, inclusive of the new shift). If weekly hours worked exceed **40 hours**, return `"NEEDS_APPROVAL"`.
5.3. **Edge Case:** A shift that keeps daily hours $\le 8$ and weekly hours $\le 40$ does not trigger this rule (proceeds to `"OK"`).

#### 6. Success State (`"OK"`)
6.1. If all validation checks, overlap checks, and hour threshold checks pass without triggering any preceding rule, return `"OK"`.
6.2. Ensure the original `shifts` argument remains completely unaltered.

### Architect

Here is the architectural design for `booking.py`, detailing the functions, helper functions, data flow, and exact execution order.

---

### Module Architecture: `booking.py`

#### 1. Helper Functions

*   `_parse_date(date_str)`
    *   **Purpose:** Validates the `MM-DD-YY` format and calendar validity (including leap years for 2-digit years assuming 20YY).
    *   **Returns:** A Python `datetime.date` object if valid, or `None` if invalid.
*   `_parse_time(time_str)`
    *   **Purpose:** Validates the `HH:MM:SS` 24-hour format and checks boundaries (`0 <= hour < 24`, `0 <= minute < 60`, `0 <= second < 60`).
    *   **Returns:** A Python `datetime.time` object if valid, or `None` if invalid.
*   `_calculate_duration_hours(start_time, end_time)`
    *   **Purpose:** Computes the raw duration between two `datetime.time` objects in hours (subtracting the mandatory 30-minute / 0.5-hour break if the day has worked time).
    *   **Returns:** Float representing hours worked. *(Note: The spec states "Every working day includes one 30-minute unpaid break." Daily total time minus 0.5 hours).*
*   `_get_week_range(target_date)`
    *   **Purpose:** Determines the Monday-to-Sunday date boundaries for a given `datetime.date`.
    *   **Returns:** Tuple of `(monday_date, sunday_date)`.

---

### Data Flow & Execution Order (`book_shift`)

The main function `book_shift(shifts, staff, date, start, end)` must execute checks strictly in the following sequential order. The first rule to trigger halts execution and returns the corresponding string.

1.  **Date Validation (Rule 1)**
    *   Call `_parse_date(date)`.
    *   *Check:* If it returns `None`, immediately return `"INVALID_DATE"`.
    *   *Store:* Parsed `datetime.date` object (`target_date`).

2.  **Time Validation & Chronology (Rule 2)**
    *   Call `_parse_time(start)` and `_parse_time(end)`.
    *   *Check:* If either returns `None`, immediately return `"INVALID_TIME"`.
    *   *Check:* If `end <= start` (ensuring chronological order and preventing zero-duration or overnight shifts), return `"INVALID_TIME"`.
    *   *Store:* Parsed `datetime.time` objects (`start_t`, `end_t`).

3.  **Schedule Overlap Check (Rule 3)**
    *   Filter the input `shifts` list for entries where:
        *   `shift["staff"] == staff` (case-sensitive or normalized depending on system conventions, assume exact match per data contract unless specified, but match the specific staff member).
        *   `shift["date"] == date` (matching the string date).
    *   For each existing shift of that staff member on that date, parse its start and time.
    *   *Check:* Do the time ranges overlap? 
        *   Overlap condition: `max(existing_start, new_start) < min(existing_end, new_end)`.
        *   *(Note: Touching boundaries where `existing_end == new_start` or `new_end == existing_start` naturally evaluates to `False` in strict inequality, allowing back-to-back shifts).*
    *   *Check:* If any overlap is detected, return `"OVERLAP"`.

4.  **Maximum Daily Limit Check (Rule 4)**
    *   Retrieve all shifts for this staff member on `date` (including the proposed new shift).
    *   Calculate the total gross duration of all shifts combined for that day, then subtract 0.5 hours (30-minute unpaid break) to get total daily hours worked.
    *   *Check:* If total daily hours worked > 12.0, return `"TOO_LONG"`.

5.  **Management Approval Check (Rule 5)**
    *   **Daily Check:** *Check:* If total daily hours worked > 8.0, return `"NEEDS_APPROVAL"`.
    *   **Weekly Check:** 
        *   Determine the Monday–Sunday week range using `_get_week_range(target_date)`.
        *   Sum up all hours worked across all days within this Monday–Sunday window for the staff member (including the new shift, subtracting the 30-minute break for *each* unique working day that has shifts).
        *   *Check:* If total weekly hours worked > 40.0, return `"NEEDS_APPROVAL"`.

6.  **Success State (Rule 6)**
    *   If all checks pass cleanly, return `"OK"`. 
    *   *Architectural Guarantee:* Ensure no append or mutation operations are performed on the input `shifts` list.

### Developer

```python
from datetime import datetime, date, time, timedelta

def _parse_date(date_str):
    """
    Validates MM-DD-YY format and calendar validity (including leap years assuming 20YY).
    Returns a datetime.date object if valid, or None if invalid.
    """
    if not isinstance(date_str, str):
        return None
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return None
        month_str, day_str, year_str = parts
        if len(month_str) != 2 or len(day_str) != 2 or len(year_str) != 2:
            return None
        
        month = int(month_str)
        day = int(day_str)
        year = int(year_str) + 2000
        
        return date(year, month, day)
    except (ValueError, TypeError):
        return None

def _parse_time(time_str):
    """
    Validates HH:MM:SS 24-hour format and checks boundaries.
    Returns a datetime.time object if valid, or None if invalid.
    """
    if not isinstance(time_str, str):
        return None
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            return None
        h_str, m_str, s_str = parts
        if len(h_str) != 2 or len(m_str) != 2 or len(s_str) != 2:
            return None
        
        hour = int(h_str)
        minute = int(m_str)
        second = int(s_str)
        
        if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
            return None
            
        return time(hour, minute, second)
    except (ValueError, TypeError):
        return None

def _time_to_seconds(t):
    """Converts a datetime.time object to total seconds from midnight."""
    return t.hour * 3600 + t.minute * 60 + t.second

def _calculate_shift_duration_hours(start_time, end_time):
    """Computes the raw duration between two time objects in hours."""
    s_sec = _time_to_seconds(start_time)
    e_sec = _time_to_seconds(end_time)
    return (e_sec - s_sec) / 3600.0

def _get_week_range(target_date):
    """Determines the Monday-to-Sunday date boundaries for a given datetime.date."""
    # weekday(): Monday is 0, Sunday is 6
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def book_shift(shifts, staff, date_str, start, end):
    """
    Books a shift for a staff member, checking date, time, overlaps, 
    daily maximums, and approval thresholds.
    """
    # 1. Date Validation (Rule 1)
    target_date = _parse_date(date_str)
    if target_date is None:
        return "INVALID_DATE"

    # 2. Time Validation & Chronology (Rule 2)
    start_t = _parse_time(start)
    end_t = _parse_time(end)
    if start_t is None or end_t is None:
        return "INVALID_TIME"
    
    if end_t <= start_t:
        return "INVALID_TIME"

    # 3. Schedule Overlap Check (Rule 3)
    # Filter shifts for this staff member on this date
    # (staff matching can be exact or normalized, but let's check exact match or handle string)
    staff_lower = staff.strip().lower() if isinstance(staff, str) else staff
    
    staff_day_shifts = []
    for s in shifts:
        s_staff = s.get("staff")
        if s_staff is not None and isinstance(s_staff, str):
            s_staff_norm = s_staff.strip().lower()
        else:
            s_staff_norm = s_staff
            
        if s_staff_norm == staff_lower and s.get("date") == date_str:
            s_start = _parse_time(s.get("start"))
            s_end = _parse_time(s.get("end"))
            if s_start and s_end:
                staff_day_shifts.append((s_start, s_end))

    new_start_sec = _time_to_seconds(start_t)
    new_end_sec = _time_to_seconds(end_t)

    for ex_start, ex_end in staff_day_shifts:
        ex_start_sec = _time_to_seconds(ex_start)
        ex_end_sec = _time_to_seconds(ex_end)
        
        # Overlap condition: max(existing_start, new_start) < min(existing_end, new_end)
        if max(ex_start_sec, new_start_sec) < min(ex_end_sec, new_end_sec):
            return "OVERLAP"

    # 4. Maximum Daily Limit Check (Rule 4)
    # Calculate daily gross hours including new shift, then subtract 0.5 hours for unpaid break
    total_daily_gross = (new_end_sec - new_start_sec) / 3600.0
    for ex_start, ex_end in staff_day_shifts:
        total_daily_gross += _calculate_shift_duration_hours(ex_start, ex_end)
    
    daily_worked_hours = total_daily_gross - 0.5

    if daily_worked_hours > 12.0:
        return "TOO_LONG"

    # 5. Management Approval Requirement (Rule 5)
    # Daily Check: > 8 hours worked
    if daily_worked_hours > 8.0:
        return "NEEDS_APPROVAL"

    # Weekly Check: Monday through Sunday
    monday, sunday = _get_week_range(target_date)
    
    # Collect all shifts in this week for the staff member
    # We need to group shifts by date to apply the 30-min break per working day
    week_shifts_by_date = {}
    
    # Add existing shifts
    for s in shifts:
        s_staff = s.get("staff")
        if s_staff is not None and isinstance(s_staff, str):
            s_staff_norm = s_staff.strip().lower()
        else:
            s_staff_norm = s_staff
            
        if s_staff_norm == staff_lower:
            s_date_str = s.get("date")
            d_obj = _parse_date(s_date_str)
            if d_obj and monday <= d_obj <= sunday:
                s_start = _parse_time(s.get("start"))
                s_end = _parse_time(s.get("end"))
                if s_start and s_end:
                    if s_date_str not in week_shifts_by_date:
                        week_shifts_by_date[s_date_str] = []
                    week_shifts_by_date[s_date_str].append((s_start, s_end))

    # Add the new shift to the week's collection
    if date_str not in week_shifts_by_date:
        week_shifts_by_date[date_str] = []
    week_shifts_by_date[date_str].append((start_t, end_t))

    # Calculate total weekly hours (sum of worked hours per working day)
    total_weekly_worked = 0.0
    for d_str, day_shift_list in week_shifts_by_date.items():
        day_gross = sum(_calculate_shift_duration_hours(ds, de) for ds, de in day_shift_list)
        day_worked = day_gross - 0.5
        total_weekly_worked += day_worked

    if total_weekly_worked > 40.0:
        return "NEEDS_APPROVAL"

    # 6. Success State (Rule 6)
    return "OK"
```

### Tester

```python
from datetime import datetime, date, time, timedelta

def _parse_date(date_str):
    """
    Validates MM-DD-YY format and calendar validity (including leap years assuming 20YY).
    Returns a datetime.date object if valid, or None if invalid.
    """
    if not isinstance(date_str, str):
        return None
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return None
        month_str, day_str, year_str = parts
        if len(month_str) != 2 or len(day_str) != 2 or len(year_str) != 2:
            return None
        
        month = int(month_str)
        day = int(day_str)
        year = int(year_str) + 2000
        
        return date(year, month, day)
    except (ValueError, TypeError):
        return None

def _parse_time(time_str):
    """
    Validates HH:MM:SS 24-hour format and checks boundaries.
    Returns a datetime.time object if valid, or None if invalid.
    """
    if not isinstance(time_str, str):
        return None
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            return None
        h_str, m_str, s_str = parts
        if len(h_str) != 2 or len(m_str) != 2 or len(s_str) != 2:
            return None
        
        hour = int(h_str)
        minute = int(m_str)
        second = int(s_str)
        
        if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
            return None
            
        return time(hour, minute, second)
    except (ValueError, TypeError):
        return None

def _time_to_seconds(t):
    """Converts a datetime.time object to total seconds from midnight."""
    return t.hour * 3600 + t.minute * 60 + t.second

def _calculate_shift_duration_hours(start_time, end_time):
    """Computes the raw duration between two time objects in hours."""
    s_sec = _time_to_seconds(start_time)
    e_sec = _time_to_seconds(end_time)
    return (e_sec - s_sec) / 3600.0

def _get_week_range(target_date):
    """Determines the Monday-to-Sunday date boundaries for a given datetime.date."""
    # weekday(): Monday is 0, Sunday is 6
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def book_shift(shifts, staff, date_str, start, end):
    """
    Books a shift for a staff member, checking date, time, overlaps, 
    daily maximums, and approval thresholds.
    """
    # 1. Date Validation (Rule 1)
    target_date = _parse_date(date_str)
    if target_date is None:
        return "INVALID_DATE"

    # 2. Time Validation & Chronology (Rule 2)
    start_t = _parse_time(start)
    end_t = _parse_time(end)
    if start_t is None or end_t is None:
        return "INVALID_TIME"
    
    if end_t <= start_t:
        return "INVALID_TIME"

    # 3. Schedule Overlap Check (Rule 3)
    # Filter shifts for this staff member on this date
    # Role / staff names ignore capital letters and extra spaces according to spec:
    # "Applies to every feature: role names ignore capital letters and extra spaces."
    # (Applying the same normalization to staff member names to be safe and robust)
    staff_lower = staff.strip().lower() if isinstance(staff, str) else staff
    
    staff_day_shifts = []
    for s in shifts:
        s_staff = s.get("staff")
        if s_staff is not None and isinstance(s_staff, str):
            s_staff_norm = s_staff.strip().lower()
        else:
            s_staff_norm = s_staff
            
        if s_staff_norm == staff_lower and s.get("date") == date_str:
            s_start = _parse_time(s.get("start"))
            s_end = _parse_time(s.get("end"))
            if s_start and s_end:
                staff_day_shifts.append((s_start, s_end))

    new_start_sec = _time_to_seconds(start_t)
    new_end_sec = _time_to_seconds(end_t)

    for ex_start, ex_end in staff_day_shifts:
        ex_start_sec = _time_to_seconds(ex_start)
        ex_end_sec = _time_to_seconds(ex_end)
        
        # Overlap condition: touching is fine (one ends at 13:00:00, next starts at 13:00:00).
        # Standard strict overlap condition: max(existing_start, new_start) < min(existing_end, new_end)
        # E.g., [9:00 - 13:00] and [13:00 - 17:30] -> max(9:00, 13:00) < min(13:00, 17:30) -> 13:00 < 13:00 is False (no overlap). Correct.
        if max(ex_start_sec, new_start_sec) < min(ex_end_sec, new_end_sec):
            return "OVERLAP"

    # 4. Maximum Daily Limit Check (Rule 4)
    # Calculate daily gross hours including new shift, then subtract 0.5 hours for unpaid break
    total_daily_gross = (new_end_sec - new_start_sec) / 3600.0
    for ex_start, ex_end in staff_day_shifts:
        total_daily_gross += _calculate_shift_duration_hours(ex_start, ex_end)
    
    daily_worked_hours = total_daily_gross - 0.5

    if daily_worked_hours > 12.0:
        return "TOO_LONG"

    # 5. Management Approval Requirement (Rule 5)
    # Daily Check: > 8 hours worked
    if daily_worked_hours > 8.0:
        return "NEEDS_APPROVAL"

    # Weekly Check: Monday through Sunday
    monday, sunday = _get_week_range(target_date)
    
    # Collect all shifts in this week for the staff member
    # We need to group shifts by date to apply the 30-min break per working day
    week_shifts_by_date = {}
    
    # Add existing shifts
    for s in shifts:
        s_staff = s.get("staff")
        if s_staff is not None and isinstance(s_staff, str):
            s_staff_norm = s_staff.strip().lower()
        else:
            s_staff_norm = s_staff
            
        if s_staff_norm == staff_lower:
            s_date_str = s.get("date")
            d_obj = _parse_date(s_date_str)
            if d_obj and monday <= d_obj <= sunday:
                s_start = _parse_time(s.get("start"))
                s_end = _parse_time(s.get("end"))
                if s_start and s_end:
                    if s_date_str not in week_shifts_by_date:
                        week_shifts_by_date[s_date_str] = []
                    week_shifts_by_date[s_date_str].append((s_start, s_end))

    # Add the new shift to the week's collection
    if date_str not in week_shifts_by_date:
        week_shifts_by_date[date_str] = []
    week_shifts_by_date[date_str].append((start_t, end_t))

    # Calculate total weekly hours (sum of worked hours per working day)
    total_weekly_worked = 0.0
    for d_str, day_shift_list in week_shifts_by_date.items():
        day_gross = sum(_calculate_shift_duration_hours(ds, de) for ds, de in day_shift_list)
        day_worked = day_gross - 0.5
        total_weekly_worked += day_worked

    if total_weekly_worked > 40.0:
        return "NEEDS_APPROVAL"

    # 6. Success State (Rule 6)
    return "OK"
```
