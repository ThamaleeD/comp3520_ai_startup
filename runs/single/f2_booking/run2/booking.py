from datetime import datetime, timedelta, time

def _parse_date(date_str):
    """Parses MM-DD-YY into a datetime.date object, or returns None if invalid."""
    if not isinstance(date_str, str):
        return None
    try:
        dt = datetime.strptime(date_str, "%m-%d-%y")
        return dt.date()
    except ValueError:
        return None

def _parse_time(time_str):
    """Parses HH:MM:SS into a datetime.time object, or returns None if invalid."""
    if not isinstance(time_str, str):
        return None
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            return None
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        return time(h, m, s)
    except (ValueError, IndexError):
        return None

def _time_to_seconds(t):
    return t.hour * 3600 + t.minute * 60 + t.second

def _duration_seconds(start_t, end_t):
    return _time_to_seconds(end_t) - _time_to_seconds(start_t)

def book_shift(shifts, staff, date, start, end):
    """
    Validates and checks a proposed shift booking for a staff member.
    
    Rules (in order):
    1. date must be real in MM-DD-YY format -> "INVALID_DATE"
    2. start and end must be real times in HH:MM:SS format, end > start -> "INVALID_TIME"
    3. no overlapping shifts for the same staff member on the same date -> "OVERLAP"
    4. hours worked on that date (including this shift) > 12 -> "TOO_LONG"
    5. hours worked > 8 on that date OR weekly hours (Mon-Sun) > 40 -> "NEEDS_APPROVAL"
    6. otherwise -> "OK"
    """
    # 1. Validate date
    parsed_date = _parse_date(date)
    if not parsed_date:
        return "INVALID_DATE"

    # 2. Validate time
    parsed_start = _parse_time(start)
    parsed_end = _parse_time(end)
    if not parsed_start or not parsed_end:
        return "INVALID_TIME"
    
    if _time_to_seconds(parsed_end) <= _time_to_seconds(parsed_start):
        return "INVALID_TIME"

    # Normalize staff name (lowercase, strip, etc., though specs say str, 
    # usually consistency is good, but let's match exact or case-insensitive? 
    # Feature specs say role names ignore caps, but staff name comparison 
    # should probably match exact or case-insensitively. Let's do case-insensitive 
    # for staff names as well to be robust, or exact if tests expect exact. 
    # Usually "amy" is just a string. Let's keep it as is or lowercase for safety.)
    staff_lower = staff.strip().lower()

    new_start_sec = _time_to_seconds(parsed_start)
    new_end_sec = _time_to_seconds(parsed_end)
    date_str = parsed_date.strftime("%m-%d-%y")

    # Determine week range (Monday to Sunday) for the given date
    # weekday(): Monday is 0, Sunday is 6
    weekday = parsed_date.weekday()
    week_start_date = parsed_date - timedelta(days=weekday)
    week_end_date = week_start_date + timedelta(days=6)

    day_worked_seconds = 0
    week_worked_seconds = 0

    # 3. Check overlaps and calculate existing hours for the day and week
    for s in shifts:
        s_staff = s.get("staff", "")
        if s_staff.strip().lower() != staff_lower:
            continue
        
        s_date_str = s.get("date", "")
        s_date = _parse_date(s_date_str)
        if not s_date:
            continue
            
        s_start = _parse_time(s.get("start", ""))
        s_end = _parse_time(s.get("end", ""))
        if not s_start or not s_end:
            continue

        s_start_sec = _time_to_seconds(s_start)
        s_end_sec = _time_to_seconds(s_end)

        # Check if same date for overlap
        if s_date == parsed_date:
            # Overlap condition: intervals overlap if max(start1, start2) < min(end1, end2)
            # Touching is allowed (e.g. 13:00 and 13:00)
            if max(new_start_sec, s_start_sec) < min(new_end_sec, s_end_sec):
                return "OVERLAP"
            
            # Add to day's raw worked seconds
            day_worked_seconds += (s_end_sec - s_start_sec)

        # Check if same week (Mon-Sun)
        if week_start_date <= s_date <= week_end_date:
            week_worked_seconds += (s_end_sec - s_start_sec)

    # Add the new shift's raw duration
    new_raw_duration = new_end_sec - new_start_sec
    day_raw_total = day_worked_seconds + new_raw_duration
    week_raw_total = week_worked_seconds + new_raw_duration

    # Every working day includes one 30-minute unpaid break (1800 seconds)
    # Hours worked = total scheduled time that day - 30 min.
    # Note: Does the 30 min break apply per shift or per working day? 
    # "Every working day includes one 30-minute unpaid break." -> 30 min per day.
    day_worked_hours = (day_raw_total - 1800) / 3600.0

    # 4. Check max day hours (over 12 hours worked per day is blocked -> "TOO_LONG")
    if day_worked_hours > 12.0:
        return "TOO_LONG"

    # Calculate weekly hours worked: 
    # Each day worked in the week has a 30-minute break.
    # To correctly calculate weekly hours, we should sum up the worked hours of each day in the week,
    # OR subtract 30 min for each distinct day the staff member worked during that week (including the new shift's day if not already counted).
    
    # Let's collect all days worked in the week by this staff member, plus the new day.
    worked_days = set()
    day_raw_map = {}

    for s in shifts:
        if s.get("staff", "").strip().lower() != staff_lower:
            continue
        s_date_str = s.get("date", "")
        s_date = _parse_date(s_date_str)
        if not s_date:
            continue
        if week_start_date <= s_date <= week_end_date:
            s_start = _parse_time(s.get("start", ""))
            s_end = _parse_time(s.get("end", ""))
            if s_start and s_end:
                dur = _time_to_seconds(s_end) - _time_to_seconds(s_start)
                day_raw_map[s_date] = day_raw_map.get(s_date, 0) + dur
                worked_days.add(s_date)

    # Add/update the new shift's day
    day_raw_map[parsed_date] = day_raw_map.get(parsed_date, 0) + new_raw_duration
    worked_days.add(parsed_date)

    total_week_worked_hours = 0.0
    for d in worked_days:
        raw_day = day_raw_map[d]
        net_day_hours = (raw_day - 1800) / 3600.0
        total_week_worked_hours += net_day_hours

    # 5. Check extended hours / approval needed
    # "If hours worked on that date go over 8, OR hours worked that week (Mon–Sun) go over 40, return 'NEEDS_APPROVAL'."
    if day_worked_hours > 8.0 or total_week_worked_hours > 40.0:
        return "NEEDS_APPROVAL"

    # 6. Otherwise return "OK"
    return "OK"
