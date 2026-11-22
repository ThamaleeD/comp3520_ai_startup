### PM

Here are the requirements and edge cases for developers implementing the `pay_summary` feature based on the ShiftWise product spec.

### General & Role Requirements
1. **Role Normalization:** The `role` argument must be case-insensitive and ignore leading/trailing whitespace (e.g., `"MANAGER"`, `"Manager"`, `" manager "` all evaluate to `"manager"`). Valid roles are `"staff"`, `"manager"`, and `"owner"`.
2. **Rounding:** All monetary outputs (`stat_pay`, `total_pay`) must be rounded to 2 decimal places.

---

### Staff (Hourly) Requirements
3. **Daily Hour Validation:** `hours` must be a list of exactly 5 numbers representing Monday through Friday.
4. **Double Time Rules:** 
   - Any hours exceeding 12 hours within a single calendar day are paid at $2 \times \text{rate}$.
   - Only the hours *above* 12 on that specific day qualify for double time.
   - Double-time hours do **not** contribute to the weekly 40-hour threshold for overtime.
5. **Overtime Rules:**
   - Calculate each day's eligible regular hours (capping daily hours counted toward this at a maximum of 12 per day, even if double time is triggered).
   - The first 40 cumulative regular hours across the week are paid at standard `rate`.
   - Any regular hours exceeding 40 for the week are paid at overtime rate ($1.5 \times \text{rate}$).
6. **Statutory Holiday Rules:**
   - `holidays` is a set of day integers where `0 = Monday` through `4 = Friday`.
   - On a holiday, the employee is paid a flat `stat_pay` instead of hourly wages.
   - `stat_pay` per holiday = `month_pay / month_days_worked`.
   - If `month_days_worked` is `0`, `stat_pay` for that holiday is `0`.
   - Hours worked on a holiday must be `0` (any non-zero hours on a holiday day must trigger an error).
7. **Staff Total Pay Calculation:** 
   $$\text{total\_pay} = (\text{regular} \times \text{rate}) + (\text{overtime} \times 1.5 \times \text{rate}) + (\text{double} \times 2 \times \text{rate}) + \text{stat\_pay}$$

---

### Manager and Owner (Salary) Requirements
8. **Salary Pay Calculation:** 
   - `total_pay = salary / 52`, rounded to 2 decimals.
9. **Zero-Hour Rule for Salaried Roles:** All hour tracking fields in the return dictionary (`regular_hours`, `overtime_hours`, `double_time_hours`, `stat_days`, `stat_pay`) must be explicitly set to `0` or `0.0`.

---

### Error Handling (`ValueError` Triggers)
The function must raise a `ValueError` under any of the following conditions:
10. **Invalid Role:** The `role` string does not match `"staff"`, `"manager"`, or `"owner"` (after normalization).
11. **Invalid Hours Length:** The `hours` list does not contain exactly 5 items.
12. **Out-of-Range Hours:** Any value in the `hours` list is negative (`< 0`) or greater than 24 (`> 24`).
13. **Working on a Holiday:** Any hours are logged on a day designated as a stat holiday within the `holidays` set (hours on a holiday must be strictly `0`).
14. **Invalid Staff Rate:** The `rate` for a staff member is `0` or less (`<= 0`).
15. **Invalid Salary:** The `salary` for a manager or owner is `0` or less (`<= 0`).

---

### Return Dictionary Schema
The function must return a dictionary matching this exact structure:
```python
{
    "regular_hours": float,      # Total regular hours (capped at 40 max for staff, 0 for salary)
    "overtime_hours": float,     # Total weekly overtime hours (> 40 regular hours, 0 for salary)
    "double_time_hours": float,  # Total daily hours exceeding 12 hours (0 for salary)
    "stat_days": int,            # Total number of applicable stat holidays (0 for salary)
    "stat_pay": float,           # Total monetary compensation for stat holidays (0.0 for salary)
    "total_pay": float           # Final calculated pay rounded to 2 decimal places
}
```

### Architect

As the software architect, I have designed the data flow, validation sequence, and helper functions for the `pay_summary` feature in `pay.py`. 

### Architectural Overview

To maintain clean separation of concerns and ensure strict validation ordering, the module is structured around a main entry function and three specialized validation/calculation helpers.

---

### Function Design & Data Flow

#### 1. `_normalize_role(role)`
* **Purpose:** Normalizes the input role string.
* **Logic:** Strips leading/trailing whitespace and converts the string to lowercase.
* **Checks:** Raises `ValueError` if the resulting string is not one of `{"staff", "manager", "owner"}`.

#### 2. `_validate_inputs(role, hours, rate, salary, holidays)`
* **Purpose:** Centralized validation gatekeeper ensuring all domain rules and data constraints are met *before* any financial math occurs.
* **Exact Order of Checks:**
  1. **Role Check:** Validate and normalize `role` via `_normalize_role`.
  2. **Hours Length Check:** Ensure `hours` is a list/iterable of exactly 5 elements. Raises `ValueError` otherwise.
  3. **Hours Value Check:** Iterate through `hours`. Ensure each value is a number between `0` and `24` (inclusive). Raises `ValueError` otherwise.
  4. **Holiday Work Check:** Iterate through `holidays`. If any index in `holidays` corresponds to a non-zero hour in the `hours` list, raise `ValueError` (working on a holiday is forbidden).
  5. **Role-Specific Pay Parameter Check:**
     * If normalized role is `"staff"`: Check that `rate > 0`. If not, raise `ValueError`.
     * If normalized role is `"manager"` or `"owner"`: Check that `salary > 0`. If not, raise `ValueError`.

#### 3. `_calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)`
* **Purpose:** Executes hourly, overtime, double-time, and statutory holiday calculations for staff members.
* **Algorithm Steps:**
  1. **Stat Pay Calculation:**
     * Count the number of stat days (`stat_days = len(holidays)`).
     * Calculate daily stat pay: If `month_days_worked > 0`, `daily_stat = month_pay / month_days_worked`, else `0.0`.
     * `stat_pay = stat_days * daily_stat`.
  2. **Daily Hour Breakdown (Loop Mon–Fri / Index 0 to 4):**
     * If the day is in `holidays`, hours must be 0 (guaranteed by validation), skip hour accumulation.
     * For non-holiday days:
       * **Double Time:** If hours $> 12$, `double_time += (hours - 12)` and daily regular hours contribution = `12`. Else, daily regular hours contribution = `hours`.
  3. **Weekly Overtime Breakdown:**
     * Sum up all daily regular hours contributions across the week.
     * **Regular vs Overtime split:**
       * If total regular hours $\le 40$: `regular_hours = total_regular`, `overtime_hours = 0`.
       * If total regular hours $> 40$: `regular_hours = 40`, `overtime_hours = total_regular - 40`.
  4. **Total Pay Formula:**
     * `raw_total = (regular_hours * rate) + (overtime_hours * 1.5 * rate) + (double_time_hours * 2 * rate) + stat_pay`
     * Round `stat_pay` and `raw_total` to 2 decimal places.
  5. Return schema dictionary with computed metrics.

#### 4. `_calculate_salary_pay(salary)`
* **Purpose:** Computes compensation for salaried roles (`manager`, `owner`).
* **Algorithm Steps:**
  * `total_pay = round(salary / 52, 2)`
  * Return schema dictionary with all hour and stat tracking fields explicitly set to `0` or `0.0`, and `total_pay`.

---

### Main Function: `pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked)`

1. **Call `_validate_inputs(role, hours, rate, salary, holidays)`**. (Aborts execution and raises `ValueError` if any rule fails).
2. **Branching logic based on normalized role:**
   * If `"staff"`: Return `_calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)`.
   * If `"manager"` or `"owner"`: Return `_calculate_salary_pay(salary)`.

### Developer

```python
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

    # Stat pay calculation
    if month_days_worked and month_days_worked > 0:
        daily_stat = month_pay / month_days_worked
    else:
        daily_stat = 0.0
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

def pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked):
    """
    Computes the pay summary for staff, managers, or owners based on hours worked,
    rates/salaries, and statutory holidays.
    """
    norm_role = _validate_inputs(role, hours, rate, salary, holidays)

    if norm_role == "staff":
        return _calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)
    else:
        return _calculate_salary_pay(salary)
```

### Tester

```python
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
```
