# ShiftWise: Feature 5 Pay Summary Module
# COMP 3520 Assignment 4

def _normalize_role(role):
    """Normalizes the input role string and validates it."""
    if not isinstance(role, str):
        raise ValueError("Role must be a string.")
    normalized = role.strip().lower()
    if normalized not in {"staff", "manager", "owner"}:
        raise ValueError(f"Unknown role: {role}")
    return normalized

def _validate_inputs(role, hours, rate, salary, holidays):
    """Centralized validation gatekeeper ensuring all domain rules and data constraints are met."""
    # 1. Role Check
    norm_role = _normalize_role(role)

    # 2. Hours Length Check
    if not isinstance(hours, (list, tuple)) or len(hours) != 5:
        raise ValueError("Hours must be a list/tuple of exactly 5 items.")

    # 3. Hours Value Check
    for h in hours:
        if not isinstance(h, (int, float)):
            raise ValueError("Hour values must be numbers.")
        if h < 0 or h > 24:
            raise ValueError(f"Hours out of range (0-24): {h}")

    # 4. Holiday Work Check
    if not isinstance(holidays, (set, list, tuple)):
        raise ValueError("Holidays must be a set, list, or tuple.")
    
    holidays_set = set(holidays)
    for day_idx in holidays_set:
        if not isinstance(day_idx, int) or day_idx < 0 or day_idx > 4:
            raise ValueError(f"Invalid holiday day index: {day_idx}")
        if hours[day_idx] != 0:
            raise ValueError(f"Cannot work on a holiday (Day {day_idx} has {hours[day_idx]} hours).")

    # 5. Role-Specific Pay Parameter Check
    if norm_role == "staff":
        if not isinstance(rate, (int, float)) or rate <= 0:
            raise ValueError(f"Invalid staff rate: {rate}")
    else:  # manager or owner
        if not isinstance(salary, (int, float)) or salary <= 0:
            raise ValueError(f"Invalid salary: {salary}")

    return norm_role

def _calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked):
    """Executes hourly, overtime, double-time, and statutory holiday calculations for staff members."""
    holidays_set = set(holidays)
    stat_days = len(holidays_set)

    # Stat pay calculation (Note: calculated per day and then summed, or calculated directly)
    # Spec: "Stat pay per day = month_pay / month_days_worked"
    # "each holiday day is paid as stat pay instead of hours."
    if month_days_worked and month_days_worked > 0:
        daily_stat = month_pay / month_days_worked
    else:
        daily_stat = 0.0
    
    # Bug fix: Stat pay for each day should be rounded individually or total rounded at the end?
    # To maintain maximum precision and match standard financial calculations, we calculate total stat pay 
    # as stat_days * daily_stat and round at the end, or round daily_stat. Let's round daily_stat to 2 decimals 
    # or keep precision. Spec doesn't specify intermediate rounding, but standard is `round(stat_days * daily_stat, 2)`.
    stat_pay = round(stat_days * daily_stat, 2)

    regular_contributions = []
    double_time_hours = 0.0

    for day_idx, h in enumerate(hours):
        if day_idx in holidays_set:
            continue  # Hours on holiday are guaranteed 0 by validation
        
        if h > 12:
            double_time_hours += (h - 12)
            regular_contributions.append(12.0)
        else:
            regular_contributions.append(float(h))

    total_regular_pool = sum(regular_contributions)

    if total_regular_pool <= 40:
        regular_hours = total_regular_pool
        overtime_hours = 0.0
    else:
        regular_hours = 40.0
        overtime_hours = total_regular_pool - 40.0

    raw_total = (regular_hours * rate) + \
                (overtime_hours * 1.5 * rate) + \
                (double_time_hours * 2.0 * rate) + \
                stat_pay

    return {
        "regular_hours": float(regular_hours),
        "overtime_hours": float(overtime_hours),
        "double_time_hours": float(double_time_hours),
        "stat_days": int(stat_days),
        "stat_pay": float(stat_pay),
        "total_pay": round(raw_total, 2)
    }

def _calculate_salary_pay(salary):
    """Computes compensation for salaried roles (manager, owner)."""
    total_pay = round(salary / 52, 2)
    return {
        "regular_hours": 0.0,
        "overtime_hours": 0.0,
        "double_time_hours": 0.0,
        "stat_days": 0,
        "stat_pay": 0.0,
        "total_pay": total_pay
    }

def pay_summary(role, hours, rate=None, salary=None, holidays=None, month_pay=0.0, month_days_worked=0):
    """
    Computes the pay summary for staff, managers, or owners based on hours worked,
    rates/salaries, and statutory holidays.
    """
    if holidays is None:
        holidays = set()
        
    norm_role = _validate_inputs(role, hours, rate, salary, holidays)

    if norm_role == "staff":
        return _calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)
    else:
        return _calculate_salary_pay(salary)
