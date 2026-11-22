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
