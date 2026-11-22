"""Pay summary feature implementation for ShiftWise."""


def _normalize_role(role: str) -> str:
    """Normalizes the role string by stripping whitespace and lowercasing."""
    if not isinstance(role, str):
        raise ValueError("Role must be a string.")
    normalized = role.strip().lower()
    if normalized not in {"staff", "manager", "owner"}:
        raise ValueError(f"Unknown role: {role}")
    return normalized


def _validate_inputs(role: str, hours: list, rate: float, salary: float, holidays: set) -> None:
    """Validates all input parameters according to specifications."""
    # 1. Validate hours length
    if not isinstance(hours, (list, tuple)) or len(hours) != 5:
        raise ValueError("Hours must be a sequence of exactly 5 items.")

    # 2. Validate hours boundaries
    for h in hours:
        if not isinstance(h, (int, float)) or h < 0 or h > 24:
            raise ValueError("Hours must be between 0 and 24 inclusive.")

    # 3. Validate role-specific pay parameters
    if role == "staff":
        if not isinstance(rate, (int, float)) or rate <= 0:
            raise ValueError("Staff rate must be greater than 0.")
    else:  # manager or owner
        if not isinstance(salary, (int, float)) or salary <= 0:
            raise ValueError("Salary must be greater than 0.")

    # 4. Validate holiday-hour constraints
    if holidays is not None:
        for day in holidays:
            if not isinstance(day, int) or day < 0 or day >= 5:
                raise ValueError("Holiday day index must be between 0 and 4.")
            if hours[day] != 0:
                raise ValueError("Hours on a holiday day must be 0.")


def _calculate_staff_pay(hours: list, rate: float, holidays: set, month_pay: float, month_days_worked: int) -> dict:
    """Calculates payroll figures for hourly staff."""
    holidays = holidays or set()
    stat_days = len(holidays)

    # Calculate stat pay
    if month_days_worked and month_days_worked > 0:
        daily_stat_pay = month_pay / month_days_worked
    else:
        daily_stat_pay = 0.0
    stat_pay = round(stat_days * daily_stat_pay, 2)

    total_pool_hours = 0.0
    double_time_hours = 0.0

    for i, h in enumerate(hours):
        if i in holidays:
            continue
        # Double-time: hours over 12 in a single day
        dt_day = max(0.0, h - 12.0)
        # Regular pool contribution: min(12, h)
        reg_pool_day = min(12.0, h)

        double_time_hours += dt_day
        total_pool_hours += reg_pool_day

    # Weekly overtime calculation (first 40 hours regular, rest overtime)
    regular_hours = min(40.0, total_pool_hours)
    overtime_hours = max(0.0, total_pool_hours - 40.0)

    # Total pay formula
    total_pay = (regular_hours * rate) + (overtime_hours * 1.5 * rate) + (double_time_hours * 2.0 * rate) + stat_pay
    total_pay = round(total_pay, 2)

    return {
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "double_time_hours": double_time_hours,
        "stat_days": stat_days,
        "stat_pay": stat_pay,
        "total_pay": total_pay,
    }


def pay_summary(role, hours, rate=0.0, salary=0.0, holidays=None, month_pay=0.0, month_days_worked=0) -> dict:
    """Computes the pay summary for staff, managers, or owners based on hours, rates, salaries, and holidays."""
    normalized_role = _normalize_role(role)
    _validate_inputs(normalized_role, hours, rate, salary, holidays)

    if normalized_role in {"manager", "owner"}:
        total_pay = round(salary / 52.0, 2)
        return {
            "regular_hours": 0.0,
            "overtime_hours": 0.0,
            "double_time_hours": 0.0,
            "stat_days": 0,
            "stat_pay": 0.0,
            "total_pay": total_pay,
        }
    else:
        return _calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)
