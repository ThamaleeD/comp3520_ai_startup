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
