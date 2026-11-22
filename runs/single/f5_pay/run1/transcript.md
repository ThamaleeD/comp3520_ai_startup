### Developer

```python
def pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked):
    """
    Calculates the pay summary for a staff member, manager, or owner given their role,
    hours worked, pay rate/salary, holidays, and recent work history for stat pay.
    """
    # Normalize role
    if not isinstance(role, str):
        raise ValueError("Role must be a string.")
    cleaned_role = role.strip().lower()

    if cleaned_role not in {"staff", "manager", "owner"}:
        raise ValueError(f"Unknown role: {role}")

    # Validate hours structure and values
    if not isinstance(hours, (list, tuple)) or len(hours) != 5:
        raise ValueError("Hours must be a list or tuple of 5 items.")

    for i, h in enumerate(hours):
        if not isinstance(h, (int, float)) or h < 0 or h > 24:
            raise ValueError(f"Invalid hours on day {i}: {h}")

    # Validate holidays
    if holidays is None:
        holidays = set()
    else:
        holidays = set(holidays)

    # Check hours on holiday days
    for day in holidays:
        if day < 0 or day > 4:
            continue
        if hours[day] > 0:
            raise ValueError(f"Hours on holiday day {day} must be 0.")

    # Process based on role
    if cleaned_role in {"manager", "owner"}:
        if salary is None or not isinstance(salary, (int, float)) or salary <= 0:
            raise ValueError("Salary must be greater than 0 for manager and owner.")
        
        total_pay = round(salary / 52, 2)
        return {
            "regular_hours": 0,
            "overtime_hours": 0,
            "double_time_hours": 0,
            "stat_days": 0,
            "stat_pay": 0.0,
            "total_pay": total_pay
        }

    # Staff (hourly) rules
    if rate is None or not isinstance(rate, (int, float)) or rate <= 0:
        raise ValueError("Rate must be greater than 0 for staff.")

    regular_hours = 0.0
    overtime_hours = 0.0
    double_time_hours = 0.0
    stat_days = len([d for d in holidays if 0 <= d <= 4])

    # Calculate stat pay
    if stat_days > 0:
        if month_days_worked and month_days_worked > 0:
            avg_day_pay = month_pay / month_days_worked
            stat_pay = round(stat_days * avg_day_pay, 2)
        else:
            stat_pay = 0.0
    else:
        stat_pay = 0.0

    # Calculate hours per day
    accumulated_regular = 0.0

    for day_idx, h in enumerate(hours):
        if day_idx in holidays:
            continue  # Holiday hours must be 0 anyway

        # Rule 1: Double time for hours over 12 in a single day
        day_regular_or_ot = h
        day_double = 0.0
        if h > 12:
            day_double = h - 12
            day_regular_or_ot = 12

        double_time_hours += day_double

        # Rule 2 & 3: Accumulate towards weekly 40 regular hours limit
        if accumulated_regular < 40:
            space_left = 40 - accumulated_regular
            if day_regular_or_ot <= space_left:
                regular_hours += day_regular_or_ot
                accumulated_regular += day_regular_or_ot
            else:
                regular_hours += space_left
                accumulated_regular += space_left
                overtime_hours += (day_regular_or_ot - space_left)
        else:
            overtime_hours += day_regular_or_ot

    # Rule 5: total_pay = regular*rate + overtime*1.5*rate + double*2*rate + stat_pay
    raw_total = (
        regular_hours * rate +
        overtime_hours * 1.5 * rate +
        double_time_hours * 2.0 * rate +
        stat_pay
    )
    total_pay = round(raw_total, 2)

    return {
        "regular_hours": regular_hours if isinstance(regular_hours, int) else round(regular_hours, 2) if regular_hours % 1 != 0 else int(regular_hours),
        "overtime_hours": overtime_hours if isinstance(overtime_hours, int) else round(overtime_hours, 2) if overtime_hours % 1 != 0 else int(overtime_hours),
        "double_time_hours": double_time_hours if isinstance(double_time_hours, int) else round(double_time_hours, 2) if double_time_hours % 1 != 0 else int(double_time_hours),
        "stat_days": stat_days,
        "stat_pay": stat_pay,
        "total_pay": total_pay
    }
```
