def _normalize_role(role: str) -> str:
    """Normalizes and validates the role string."""
    if not isinstance(role, str):
        raise ValueError("Role must be a string.")
    norm = role.strip().lower()
    if norm not in ("staff", "manager", "owner"):
        raise ValueError(f"Unknown role: {role}")
    return norm


def _validate_inputs(norm_role: str, hours: list, rate: float, salary: float, holidays: set):
    """Executes strict checks in the required order."""
    # 2. Hours Length Validation
    if not isinstance(hours, (list, tuple)) or len(hours) != 5:
        raise ValueError("Hours must be a list of exactly 5 items.")

    # 3. Daily Hours Boundary Validation
    for h in hours:
        if not isinstance(h, (int, float)):
            raise ValueError("Hour values must be numbers.")
        if h < 0 or h > 24:
            raise ValueError("Daily hours cannot be negative or exceed 24.")

    # 4. Holiday Hour Constraints
    if holidays is not None:
        for day in holidays:
            if not isinstance(day, int) or day < 0 or day > 4:
                raise ValueError("Holiday day index must be between 0 and 4.")
            if hours[day] > 0:
                raise ValueError(f"Hours on holiday day {day} must be 0.")

    # 5. Role-Specific Financial Validation
    if norm_role == "staff":
        if rate is None or rate <= 0:
            raise ValueError("Staff rate must be greater than 0.")
    else:  # manager or owner
        if salary is None or salary <= 0:
            raise ValueError("Salary must be greater than 0.")


def _calculate_staff_pay(hours: list, rate: float, holidays: set, month_pay: float, month_days_worked: int) -> dict:
    """Performs granular math for hourly staff."""
    holidays = holidays or set()
    
    # 1. Stat Pay Processing
    stat_days = len(holidays)
    # Bug fix: A staff member could have month_days_worked > 0 with month_pay == 0. 
    # However, if month_pay <= 0, stat pay per day should be 0.0. 
    # Checking month_days_worked <= 0 or month_pay < 0 correctly handles zero or positive earnings.
    if not month_days_worked or month_days_worked <= 0 or month_pay is None or month_pay < 0:
        stat_pay_per_day = 0.0
    else:
        stat_pay_per_day = month_pay / month_days_worked
    stat_pay = round(stat_pay_per_day * stat_days, 2)

    # 2. Daily Hour Breakdown
    regular_accumulated = 0.0
    double_time_hours = 0.0

    for d, h in enumerate(hours):
        if d in holidays:
            continue
        if h > 12:
            double_time_hours += (h - 12)
            regular_accumulated += 12.0
        else:
            regular_accumulated += float(h)

    # 3. Weekly Overtime Split
    regular_hours = min(40.0, regular_accumulated)
    overtime_hours = max(0.0, regular_accumulated - 40.0)

    # Ensure integer representations if they are whole numbers, matching common expectations,
    # though floats are also acceptable. We will keep them as floats or ints depending on value.
    if regular_hours.is_integer():
        regular_hours = int(regular_hours)
    if overtime_hours.is_integer():
        overtime_hours = int(overtime_hours)
    if double_time_hours.is_integer():
        double_time_hours = int(double_time_hours)

    # 4. Total Compensation Calculation
    raw_total = (
        (float(regular_hours) * rate) +
        (float(overtime_hours) * 1.5 * rate) +
        (float(double_time_hours) * 2.0 * rate) +
        stat_pay
    )
    total_pay = round(raw_total, 2)

    return {
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "double_time_hours": double_time_hours,
        "stat_days": stat_days,
        "stat_pay": stat_pay,
        "total_pay": total_pay
    }


def _calculate_salary_pay(salary: float) -> dict:
    """Computes weekly pay for salaried workers."""
    total_pay = round(salary / 52.0, 2)
    return {
        "regular_hours": 0,
        "overtime_hours": 0,
        "double_time_hours": 0,
        "stat_days": 0,
        "stat_pay": 0.0,
        "total_pay": total_pay
    }


def pay_summary(role, hours, rate=0.0, salary=0.0, holidays=None, month_pay=0.0, month_days_worked=0) -> dict:
    """
    Calculates the pay summary for staff, manager, or owner roles given hours worked,
    rates, salaries, and holiday information.
    """
    norm_role = _normalize_role(role)
    _validate_inputs(norm_role, hours, rate, salary, holidays)

    if norm_role == "staff":
        return _calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)
    else:
        return _calculate_salary_pay(salary)
