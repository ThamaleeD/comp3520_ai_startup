### Developer

```python
def pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked):
    """
    Calculates the pay summary for a given role (staff, manager, or owner)
    based on hours worked, rates, holidays, and history.
    """
    # Normalize role
    if not isinstance(role, str):
        raise ValueError("Invalid role type")
    normalized_role = role.strip().lower()

    if normalized_role not in {"staff", "manager", "owner"}:
        raise ValueError(f"Unknown role: {role}")

    # Validate hours
    if not isinstance(hours, (list, tuple)) or len(hours) != 5:
        raise ValueError("Hours must be a sequence of 5 numbers")
    
    for h in hours:
        if not isinstance(h, (int, float)) or h < 0 or h > 24:
            raise ValueError("Hours must be between 0 and 24 inclusive")

    # Validate holidays
    if holidays is None:
        holidays = set()
    for d in holidays:
        if not isinstance(d, int) or d < 0 or d > 4:
            raise ValueError("Holiday day numbers must be between 0 and 4")
        # Rule 7: hours on a holiday day must be 0
        if hours[d] != 0:
            raise ValueError(f"Hours on holiday day {d} must be 0")

    # Handle Manager and Owner (Salary)
    if normalized_role in {"manager", "owner"}:
        if not isinstance(salary, (int, float)) or salary <= 0:
            raise ValueError("Salary must be greater than 0 for managers and owners")
        
        total_pay = round(salary / 52.0, 2)
        return {
            "regular_hours": 0.0,
            "overtime_hours": 0.0,
            "double_time_hours": 0.0,
            "stat_days": 0,
            "stat_pay": 0.0,
            "total_pay": total_pay
        }

    # Handle Staff (Hourly)
    if not isinstance(rate, (int, float)) or rate <= 0:
        raise ValueError("Rate must be greater than 0 for staff")

    if month_days_worked is None or month_days_worked < 0:
        month_days_worked = 0
    if month_pay is None or month_pay < 0:
        month_pay = 0.0

    # Calculate stat pay
    stat_days = len(holidays)
    if month_days_worked > 0:
        stat_pay_per_day = month_pay / month_days_worked
    else:
        stat_pay_per_day = 0.0
    
    total_stat_pay = stat_days * stat_pay_per_day

    regular_hours = 0.0
    overtime_hours = 0.0
    double_time_hours = 0.0
    total_base_and_ot_hours = 0.0

    # Process each day (0 to 4)
    for day in range(5):
        if day in holidays:
            continue  # Hours are guaranteed to be 0 by validation
        
        h = hours[day]
        # Rule 1: Double time for hours over 12 in a single day
        if h > 12:
            day_regular = 12.0
            day_double = h - 12.0
        else:
            day_regular = h
            day_double = 0.0

        double_time_hours += day_double
        total_base_and_ot_hours += day_regular

    # Rule 2 & 3: First 40 hours of base (capped at 12/day) are regular. Anything over 40 is overtime.
    if total_base_and_ot_hours > 40:
        regular_hours = 40.0
        overtime_hours = total_base_and_ot_hours - 40.0
    else:
        regular_hours = total_base_and_ot_hours
        overtime_hours = 0.0

    # Rule 5: total_pay = regular*rate + overtime*1.5*rate + double*2*rate + stat_pay
    raw_total = (
        (regular_hours * rate) +
        (overtime_hours * 1.5 * rate) +
        (double_time_hours * 2.0 * rate) +
        total_stat_pay
    )

    return {
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "double_time_hours": double_time_hours,
        "stat_days": stat_days,
        "stat_pay": round(total_stat_pay, 2),
        "total_pay": round(raw_total, 2)
    }
```
