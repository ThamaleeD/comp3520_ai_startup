def pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked):
    """Calculates the pay summary for staff, managers, or owners based on ShiftWise rules."""
    # Normalize role
    if not isinstance(role, str):
        raise ValueError("Invalid role type")
    normalized_role = role.strip().lower()

    if normalized_role not in {"staff", "manager", "owner"}:
        raise ValueError(f"Unknown role: {role}")

    # Validate hours
    if not isinstance(hours, (list, tuple)) or len(hours) != 5:
        raise ValueError("Hours must be a list or tuple of 5 items")

    for h in hours:
        if not isinstance(h, (int, float)) or h < 0 or h > 24:
            raise ValueError("Hours must be between 0 and 24 inclusive")

    # Validate holidays
    if holidays is None:
        holidays = set()
    for day in holidays:
        if day < 0 or day > 4:
            raise ValueError("Holiday day index must be between 0 and 4")
        if hours[day] != 0:
            raise ValueError("Hours on a holiday day must be 0")

    # Salary roles (manager, owner)
    if normalized_role in {"manager", "owner"}:
        if salary is None or not isinstance(salary, (int, float)) or salary <= 0:
            raise ValueError("Salary must be greater than 0 for managers and owners")
        
        total_pay = round(salary / 52, 2)
        return {
            "regular_hours": 0,
            "overtime_hours": 0,
            "double_time_hours": 0,
            "stat_days": 0,
            "stat_pay": 0.0,
            "total_pay": total_pay
        }

    # Staff (hourly) role
    if rate is None or not isinstance(rate, (int, float)) or rate <= 0:
        raise ValueError("Rate must be greater than 0 for staff")

    if month_pay is None:
        month_pay = 0.0
    if month_days_worked is None:
        month_days_worked = 0

    stat_days = len(holidays)
    if month_days_worked > 0:
        daily_stat_pay = month_pay / month_days_worked
    else:
        daily_stat_pay = 0.0
    
    total_stat_pay = stat_days * daily_stat_pay

    regular_hours = 0.0
    overtime_hours = 0.0
    double_time_hours = 0.0

    # Calculate hours per day
    for day_idx, h in enumerate(hours):
        if day_idx in holidays:
            continue
        
        # Double time: hours over 12 in a single day
        if h > 12:
            dt = h - 12
            base_h = 12
            double_time_hours += dt
        else:
            base_h = h
        
        regular_hours += base_h

    # Overtime calculation: first 40 regular hours are regular, anything over 40 is overtime
    if regular_hours > 40:
        overtime_hours = regular_hours - 40
        regular_hours = 40.0

    # Calculate total pay
    raw_total_pay = (
        regular_hours * rate +
        overtime_hours * 1.5 * rate +
        double_time_hours * 2.0 * rate +
        total_stat_pay
    )

    return {
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "double_time_hours": double_time_hours,
        "stat_days": stat_days,
        "stat_pay": round(total_stat_pay, 2),
        "total_pay": round(raw_total_pay, 2)
    }
