def pay_summary(role, hours, rate, salary, holidays,
                month_pay, month_days_worked):

    # Normalize and validate role
    if not isinstance(role, str):
        raise ValueError("Invalid role")

    role = role.strip().lower()

    if role not in {"staff", "manager", "owner"}:
        raise ValueError("Invalid role")

    # Validate hours for Monday through Friday
    if not isinstance(hours, (list, tuple)) or len(hours) != 5:
        raise ValueError("Hours must contain five values")

    for daily_hours in hours:
        if (
            not isinstance(daily_hours, (int, float))
            or isinstance(daily_hours, bool)
            or not 0 <= daily_hours <= 24
        ):
            raise ValueError("Invalid working hours")

    # Holiday days must have zero working hours
    for day in holidays:
        if day in range(5) and hours[day] != 0:
            raise ValueError("Cannot work on a stat holiday")

    # Salary-based employees
    if role in {"manager", "owner"}:
        if salary <= 0:
            raise ValueError("Salary must be positive")

        return {
            "regular_hours": 0,
            "overtime_hours": 0,
            "double_time_hours": 0,
            "stat_days": 0,
            "stat_pay": 0,
            "total_pay": round(salary / 52, 2),
        }

    # Hourly staff
    if rate <= 0:
        raise ValueError("Hourly rate must be positive")

    eligible_hours = 0
    double_time_hours = 0

    for daily_hours in hours:
        eligible_hours += min(daily_hours, 12)
        double_time_hours += max(daily_hours - 12, 0)

    regular_hours = min(eligible_hours, 40)
    overtime_hours = max(eligible_hours - 40, 0)

    # Stat holiday pay
    stat_days = len(holidays)

    if month_days_worked == 0:
        stat_pay = 0
    else:
        stat_pay = stat_days * month_pay / month_days_worked

    # Total weekly earnings
    total_pay = (
        regular_hours * rate
        + overtime_hours * rate * 1.5
        + double_time_hours * rate * 2
        + stat_pay
    )

    return {
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "double_time_hours": double_time_hours,
        "stat_days": stat_days,
        "stat_pay": round(stat_pay, 2),
        "total_pay": round(total_pay, 2),
    }
