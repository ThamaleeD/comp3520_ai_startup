from datetime import datetime, timedelta, date, time

def parse_date(date_str: str) -> date | None:
    """
    Attempts to parse date_str using format "%m-%d-%y" strictly.
    Returns a datetime.date object if valid, or None if parsing fails or values are out of bounds.
    """
    if not isinstance(date_str, str):
        return None
    
    # Ensure strict MM-DD-YY format with 2-digit year (length 8: e.g., "11-16-26")
    parts = date_str.split('-')
    if len(parts) != 3 or len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 2:
        return None

    try:
        dt = datetime.strptime(date_str, "%m-%d-%y")
        return dt.date()
    except ValueError:
        return None

def parse_time(time_str: str) -> time | None:
    """
    Attempts to parse time_str using format "%H:%M:%S".
    Returns a datetime.time object if valid, or None otherwise.
    """
    if not isinstance(time_str, str):
        return None
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S")
        return dt.time()
    except ValueError:
        return None

def calculate_shift_duration_hours(start_time: time, end_time: time) -> float:
    """
    Converts start_time and end_time into elapsed seconds since midnight.
    Computes raw duration, subtracts 1800 seconds (the 30-minute unpaid break), 
    and returns the net duration in hours.
    """
    start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
    raw_seconds = end_seconds - start_seconds
    net_seconds = max(0, raw_seconds - 1800)  # Subtract 30 minutes unpaid break, guard against negative
    return net_seconds / 3600.0

def get_week_bounds(target_date: date) -> tuple[date, date]:
    """
    Determines the Monday and Sunday boundaries of the week containing target_date 
    (since a week runs Monday–Sunday). weekday() returns 0 for Monday, 6 for Sunday.
    """
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def book_shift(shifts: list[dict], staff: str, date: str, start: str, end: str) -> str:
    """
    Books a shift for a staff member after validating dates, times, overlaps, 
    daily maximum hours, and approval requirements.
    """
    if not isinstance(staff, str):
        return "INVALID_DATE"
    
    normalized_staff = staff.strip().lower()

    # 1. Date Validation
    parsed_date = parse_date(date)
    if parsed_date is None:
        return "INVALID_DATE"

    # 2. Time Validation
    parsed_start = parse_time(start)
    parsed_end = parse_time(end)
    if parsed_start is None or parsed_end is None:
        return "INVALID_TIME"
    
    if parsed_end <= parsed_start:
        return "INVALID_TIME"

    # 3. Overlap Validation
    # Filter existing shifts for the same staff and date (case-insensitive staff matching)
    staff_day_shifts = []
    for s in shifts:
        s_staff = s.get("staff")
        if isinstance(s_staff, str) and s_staff.strip().lower() == normalized_staff and s.get("date") == date:
            s_start = parse_time(s.get("start", ""))
            s_end = parse_time(s.get("end", ""))
            if s_start and s_end:
                staff_day_shifts.append((s_start, s_end))

    # Check for intersection: new_start < existing_end and new_end > existing_start
    for s_start, s_end in staff_day_shifts:
        if parsed_start < s_end and parsed_end > s_start:
            return "OVERLAP"

    # 4. Maximum Daily Hours Validation
    current_day_raw_seconds = (parsed_end.hour * 3600 + parsed_end.minute * 60 + parsed_end.second) - \
                              (parsed_start.hour * 3600 + parsed_start.minute * 60 + parsed_start.second)
    
    for s_start, s_end in staff_day_shifts:
        s_raw = (s_end.hour * 3600 + s_end.minute * 60 + s_end.second) - \
                (s_start.hour * 3600 + s_start.minute * 60 + s_start.second)
        current_day_raw_seconds += s_raw
    
    total_daily_hours = (max(0, current_day_raw_seconds - 1800)) / 3600.0

    if total_daily_hours > 12.0:
        return "TOO_LONG"

    # 5. Approval Required Validation
    daily_needs_approval = total_daily_hours > 8.0

    # Calculate weekly hours (Monday–Sunday)
    week_start, week_end = get_week_bounds(parsed_date)
    
    week_shifts_by_date: dict[str, list[tuple[time, time]]] = {}
    
    # Include existing shifts in the week
    for s in shifts:
        s_staff = s.get("staff")
        if isinstance(s_staff, str) and s_staff.strip().lower() == normalized_staff:
            s_date_str = s.get("date")
            s_parsed_date = parse_date(s_date_str)
            if s_parsed_date and week_start <= s_parsed_date <= week_end:
                s_start = parse_time(s.get("start", ""))
                s_end = parse_time(s.get("end", ""))
                if s_start and s_end:
                    week_shifts_by_date.setdefault(s_date_str, []).append((s_start, s_end))
                    
    # Add/update the new shift in the week collection
    week_shifts_by_date.setdefault(date, []).append((parsed_start, parsed_end))
    
    total_weekly_hours = 0.0
    for d_str, day_shifts_list in week_shifts_by_date.items():
        day_raw_seconds = 0
        for st, et in day_shifts_list:
            day_raw_seconds += (et.hour * 3600 + et.minute * 60 + et.second) - \
                               (st.hour * 3600 + st.minute * 60 + st.second)
        # Each working day includes one 30-minute unpaid break
        day_net_hours = (max(0, day_raw_seconds - 1800)) / 3600.0
        total_weekly_hours += day_net_hours

    weekly_needs_approval = total_weekly_hours > 40.0

    if daily_needs_approval or weekly_needs_approval:
        return "NEEDS_APPROVAL"

    # 6. Success State
    return "OK"
