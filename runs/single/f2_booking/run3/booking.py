from datetime import datetime, timedelta

def _parse_date(date_str):
    """Parses MM-DD-YY date string. Returns datetime.date or None."""
    if not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str, "%m-%d-%y").date()
    except ValueError:
        return None

def _parse_time(time_str):
    """Parses HH:MM:SS time string. Returns datetime.time or None."""
    if not isinstance(time_str, str):
        return None
    try:
        return datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        return None

def _time_to_seconds(t):
    """Converts datetime.time to total seconds from midnight."""
    return t.hour * 3600 + t.minute * 60 + t.second

def _shift_duration_seconds(start_t, end_t):
    """Calculates duration of shift in seconds, assuming end > start."""
    return _time_to_seconds(end_t) - _time_to_seconds(start_t)

def _get_worked_hours_for_shift(start_t, end_t):
    """Calculates worked hours for a shift (duration minus 30 minutes / 1800 seconds)."""
    duration_sec = _shift_duration_seconds(start_t, end_t)
    worked_sec = duration_sec - 1805 if duration_sec < 0 else duration_sec - 1800
    # Let's be precise: 30 minutes = 1800 seconds
    return (duration_sec - 1800) / 3600.0

def book_shift(shifts, staff, date, start, end):
    """
    Validates and checks a shift booking against rules:
    1. Valid date (MM-DD-YY)
    2. Valid time (HH:MM:SS, end > start)
    3. No overlapping shifts for the same staff member on the same date
    4. Max 12 hours worked per day (including 30 min unpaid break rule -> total duration <= 12.5 hrs)
    5. Needs approval if daily hours > 8 or weekly hours (Mon-Sun) > 40
    6. Otherwise OK
    """
    # 1. Check date validity
    d_obj = _parse_date(date)
    if d_obj is None:
        return "INVALID_DATE"

    # 2. Check time validity
    s_obj = _parse_time(start)
    e_obj = _parse_time(end)
    if s_obj is None or e_obj is None:
        return "INVALID_TIME"
    
    start_sec = _time_to_seconds(s_obj)
    end_sec = _time_to_seconds(e_obj)
    if end_sec <= start_sec:
        return "INVALID_TIME"

    # Normalize staff name / identifier if needed (or treat as exact match depending on spec, 
    # but the prompt says role names ignore casing. For staff names, standard matching applies).
    staff_lower = staff.strip().lower()

    # Filter existing shifts for this specific staff member
    staff_shifts = []
    for sh in shifts:
        if sh.get("staff", "").strip().lower() == staff_lower:
            staff_shifts.append(sh)

    # 3. Check overlaps
    # Different staff members can overlap, but only a staff member's own shifts can't overlap.
    # Touching is fine (one ends at 13:00:00, next starts at 13:00:00).
    for sh in staff_shifts:
        if sh.get("date") == date:
            existing_s = _parse_time(sh.get("start"))
            existing_e = _parse_time(sh.get("end"))
            if existing_s and existing_e:
                ex_start_sec = _time_to_seconds(existing_s)
                ex_end_sec = _time_to_seconds(existing_e)
                
                # Check for overlap: not (new_end <= ex_start or new_start >= ex_end)
                # Touching means new_end == ex_start or new_start == ex_end, which is allowed.
                if not (end_sec <= ex_start_sec or start_sec >= ex_end_sec):
                    return "OVERLAP"

    # Calculate hours worked for the new shift
    new_shift_duration_hours = (end_sec - start_sec) / 3600.0
    new_shift_worked_hours = new_shift_duration_hours - 0.5  # minus 30 min break

    # Calculate total worked hours for that date (existing + new)
    date_worked_hours = new_shift_worked_hours
    for sh in staff_shifts:
        if sh.get("date") == date:
            ex_s = _parse_time(sh.get("start"))
            ex_e = _parse_time(sh.get("end"))
            if ex_s and ex_e:
                dur = (_time_to_seconds(ex_e) - _time_to_seconds(ex_s)) / 3600.0
                date_worked_hours += (dur - 0.5)

    # 4. Max 12 hours worked per day
    if date_worked_hours > 12.0:
        return "TOO_LONG"

    # Calculate weekly hours (Mon–Sun)
    # Find Monday and Sunday of the week for the target date
    # weekday(): Monday is 0, Sunday is 6
    day_of_week = d_obj.weekday()
    monday = d_obj - timedelta(days=day_of_week)
    sunday = monday + timedelta(days=6)

    weekly_worked_hours = 0.0
    
    # We need to sum up all worked hours for this staff member in that Mon-Sun week,
    # including the new shift we are trying to book.
    # First, collect all shifts in that week (including the new one if its date falls in range).
    # Wait, a shift's date must fall between monday and sunday inclusive.
    all_staff_shifts_this_week = list(staff_shifts)
    # Add temporary new shift representation for calculation
    all_staff_shifts_this_week.append({"date": date, "start": start, "end": end})

    for sh in all_staff_shifts_this_week:
        sh_d = _parse_date(sh.get("date"))
        if sh_d and monday <= sh_d <= sunday:
            sh_s = _parse_time(sh.get("start"))
            sh_e = _parse_time(sh.get("end"))
            if sh_s and sh_e:
                dur = (_time_to_seconds(sh_e) - _time_to_seconds(sh_s)) / 3600.0
                weekly_worked_hours += (dur - 0.5)

    # 5. If hours worked on that date go over 8, OR hours worked that week go over 40, return "NEEDS_APPROVAL"
    if date_worked_hours > 8.0 or weekly_worked_hours > 40.0:
        return "NEEDS_APPROVAL"

    # 6. Otherwise return "OK"
    return "OK"
