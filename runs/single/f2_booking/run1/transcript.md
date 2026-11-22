### Developer

```python
from datetime import datetime, timedelta

def _parse_date(date_str):
    """Parses MM-DD-YY into a datetime.date object. Returns None if invalid."""
    if not isinstance(date_str, str):
        return None
    try:
        # strict check: must match MM-DD-YY exactly
        return datetime.strptime(date_str, "%m-%d-%y").date()
    except ValueError:
        return None

def _parse_time(time_str):
    """Parses HH:MM:SS into a datetime.time object. Returns None if invalid."""
    if not isinstance(time_str, str):
        return None
    try:
        return datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        return None

def _time_to_seconds(t):
    return t.hour * 3600 + t.minute * 60 + t.second

def _calculate_shift_work_seconds(start_time, end_time):
    """Calculates work seconds for a shift, subtracting 30-min unpaid break."""
    start_sec = _time_to_seconds(start_time)
    end_sec = _time_to_seconds(end_time)
    total_duration = end_sec - start_sec
    # subtract 30 minutes (1800 seconds)
    work_duration = total_duration - 1800
    return max(0, work_duration)

def _times_overlap(s1, e1, s2, e2):
    """Checks if two time ranges overlap. Touching at endpoints is allowed."""
    start1 = _time_to_seconds(s1)
    end1 = _time_to_seconds(e1)
    start2 = _time_to_seconds(s2)
    end2 = _time_to_seconds(e2)
    
    # Overlap occurs if one starts before the other ends, and ends after the other starts.
    # Touching (end1 == start2 or end2 == start1) is not an overlap.
    return not (end1 <= start2 or end2 <= start1)

def book_shift(shifts, staff, date, start, end):
    """
    Validates and checks a proposed shift booking against existing shifts and policy rules.
    
    Rules checked in order:
    1. date must be a real date in MM-DD-YY format -> "INVALID_DATE"
    2. start and end must be real times in HH:MM:SS format, end > start -> "INVALID_TIME"
    3. no overlapping shifts for the same staff member on the same date -> "OVERLAP"
    4. hours worked on that date including this shift <= 12 hours -> "TOO_LONG"
    5. hours worked on that date > 8 hours OR weekly hours (Mon-Sun) > 40 -> "NEEDS_APPROVAL"
    6. otherwise -> "OK"
    """
    # 1. Validate date
    d_obj = _parse_date(date)
    if d_obj is None:
        return "INVALID_DATE"
    
    # 2. Validate time
    s_obj = _parse_time(start)
    e_obj = _parse_time(end)
    if s_obj is None or e_obj is None:
        return "INVALID_TIME"
    
    if _time_to_seconds(e_obj) <= _time_to_seconds(s_obj):
        return "INVALID_TIME"
    
    # 3. Check overlaps for the same staff member on the same date
    staff_lower = staff.strip().lower()
    date_str = d_obj.strftime("%m-%d-%y")
    
    for shift in shifts:
        if shift.get("staff", "").strip().lower() == staff_lower:
            if shift.get("date") == date_str:
                existing_s = _parse_time(shift.get("start"))
                existing_e = _parse_time(shift.get("end"))
                if existing_s and existing_e:
                    if _times_overlap(s_obj, e_obj, existing_s, existing_e):
                        return "OVERLAP"

    # Calculate hours for the current proposed shift
    new_shift_work_secs = _calculate_shift_work_seconds(s_obj, e_obj)
    new_shift_work_hours = new_shift_work_secs / 3600.0

    # 4 & 5 Preparation: Gather all shifts for this staff member to calculate daily and weekly totals
    staff_shifts = []
    for shift in shifts:
        if shift.get("staff", "").strip().lower() == staff_lower:
            s_date = _parse_date(shift.get("date"))
            s_start = _parse_time(shift.get("start"))
            s_end = _parse_time(shift.get("end"))
            if s_date and s_start and s_end:
                staff_shifts.append({
                    "date_obj": s_date,
                    "start": s_start,
                    "end": s_end,
                    "work_seconds": _calculate_shift_work_seconds(s_start, s_end)
                })

    # Calculate daily work hours for this date (including the new shift)
    daily_work_secs = new_shift_work_secs
    for shift in staff_shifts:
        if shift["date_obj"] == d_obj:
            daily_work_secs += shift["work_seconds"]
            
    daily_work_hours = daily_work_secs / 3600.0

    # 4. Check if daily work hours exceed 12
    if daily_work_hours > 12.0:
        return "TOO_LONG"

    # 5. Check weekly work hours (Monday to Sunday)
    # Determine the Monday of the week for the given date
    # weekday(): Monday is 0, Sunday is 6
    monday_date = d_obj - timedelta(days=d_obj.weekday())
    sunday_date = monday_date + timedelta(days=6)

    weekly_work_secs = new_shift_work_secs
    for shift in staff_shifts:
        if monday_date <= shift["date_obj"] <= sunday_date:
            weekly_work_secs += shift["work_seconds"]
            
    weekly_work_hours = weekly_work_secs / 3600.0

    # If daily work hours go over 8, OR weekly work hours go over 40
    if daily_work_hours > 8.0 or weekly_work_hours > 40.0:
        return "NEEDS_APPROVAL"

    # 6. Otherwise OK
    return "OK"
```
