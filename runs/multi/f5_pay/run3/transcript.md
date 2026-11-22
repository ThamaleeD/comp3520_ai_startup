### PM

Here is the clear, numbered list of requirements and edge cases for developers implementing the `pay_summary` feature.

### Input Sanitization & General Requirements
1. **Role Normalization:** The `role` input must be case-insensitive and ignore leading/trailing whitespace (e.g., `"MANAGER"`, `"Manager"`, `" manager "` all evaluate to `"manager"`). Valid roles are `"staff"`, `"manager"`, and `"owner"`.
2. **Hours Validation:** The `hours` parameter must be a list containing exactly 5 numerical items representing Monday through Friday.
3. **Daily Hour Limits:** Individual daily hours cannot be negative and cannot exceed 24.
4. **Rounding:** All monetary values (`stat_pay`, `total_pay`) must be rounded strictly to 2 decimal places.

---

### Staff (Hourly) Requirements
5. **Holiday Hours Constraint:** Hours worked on any day designated as a stat holiday (`holidays` set containing the day index 0–4) must be strictly `0`.
6. **Stat Pay Calculation:** 
   - Stat pay per holiday is calculated as `month_pay / month_days_worked`.
   - If `month_days_worked` is `0`, stat pay defaults to `0`.
   - Total stat pay is the sum of stat pay for all holidays in the `holidays` set.
7. **Double Time Rules:** 
   - Hours exceeding 12 within a single day are paid at $2 \times \text{rate}$.
   - Only the hours *above* 12 on that specific day are classified as double-time hours.
   - Double-time hours do *not* count toward the weekly 40-hour regular threshold.
8. **Overtime Rules:**
   - Regular hours are capped at a maximum of 12 per day (excluding double time).
   - Sum these daily capped hours for the week.
   - The first 40 hours are classified as regular pay (paid at $1 \times \text{rate}$).
   - Any accumulated weekly hours over 40 are classified as overtime (paid at $1.5 \times \text{rate}$).
9. **Staff Total Pay Formula:** 
   $$\text{total\_pay} = (\text{regular\_hours} \times \text{rate}) + (\text{overtime\_hours} \times 1.5 \times \text{rate}) + (\text{double\_time\_hours} \times 2 \times \text{rate}) + \text{stat\_pay}$$

---

### Manager and Owner (Salary) Requirements
10. **Salary Pay Formula:** For both managers and owners, `total_pay` is calculated strictly as `salary / 52` (rounded to 2 decimal places).
11. **Zero-Hour Rule:** For salaried roles, all hour-related return fields (`regular_hours`, `overtime_hours`, `double_time_hours`, `stat_days`, `stat_pay`) must be explicitly set to `0` (or `0.0` where applicable). Overtime, double time, and stat pay do not apply.

---

### Error Handling (`ValueError` Triggers)
The function must raise a `ValueError` under any of the following conditions:
12. **Unknown Role:** The role string does not match `"staff"`, `"manager"`, or `"owner"` (after normalization).
13. **Invalid Hours Length:** The `hours` list does not contain exactly 5 items.
14. **Out-of-Bounds Daily Hours:** Any value in `hours` is less than 0 or greater than 24.
15. **Holiday Hours Violation:** Any hours are logged on a day specified in the `holidays` set (hours on holiday must be 0).
16. **Invalid Staff Rate:** The role is `"staff"` and `rate` is less than or equal to `0`.
17. **Invalid Salary:** The role is `"manager"` or `"owner"` and `salary` is less than or equal to `0`.

---

### Return Format Requirements
18. The function must return a dictionary with the exact keys and types specified below:
    ```python
    {
        "regular_hours": float/int,
        "overtime_hours": float/int,
        "double_time_hours": float/int,
        "stat_days": int,        # Count of holidays in the week
        "stat_pay": float,       # Total calculated stat pay rounded to 2 decimals
        "total_pay": float       # Total calculated pay rounded to 2 decimals
    }
    ```

---

### Edge Cases to Test
19. **Zero Hours Worked (Staff):** Staff member works 0 hours all week.
20. **Exact 40 Hours:** Staff member works `[8, 8, 8, 8, 8]` (Standard 40 hours, 0 OT, 0 Double).
21. **Overtime Threshold Crossing:** Staff member works `[10, 10, 10, 10, 5]` (Total 45 hours $\rightarrow$ 40 regular, 5 OT).
22. **Double Time Trigger:** Staff member works `[14, 8, 8, 8, 8]` (Mon has 2 hours $> 12 \rightarrow$ 2 double time; remaining days sum to 38 cap $\rightarrow$ 40 regular, 4 OT, 2 Double).
23. **Stat Holiday with Zero Month Work:** Staff has a holiday, but `month_days_worked = 0` (Stat pay evaluates to 0 safely without division by zero errors).
24. **Case Insensitivity:** Passing role as `"MANAGER"`, `" owner "`, or `"StAfF"`.

### Architect

# Architecture & Execution Plan: `pay.py`

## 1. Module Structure & Helper Functions

To keep the codebase modular, clean, and testable, the `pay_summary` function will rely on three internal helper functions inside `pay.py`:

*   `_normalize_role(role: str) -> str`
    *   Strips leading/trailing whitespace and converts the string to lowercase. Validates if it matches `"staff"`, `"manager"`, or `"owner"`. Raises `ValueError` otherwise.
*   `_validate_inputs(norm_role, hours, rate, salary, holidays)`
    *   Executes strict checks sequentially to ensure all boundaries (list length, hour limits, holiday constraints, rate/salary limits) are respected. Raises `ValueError` on failure.
*   `_calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked) -> dict`
    *   Performs the granular math for hourly staff (daily double-time, weekly regular vs. overtime capping, and stat holiday calculations).
*   `_calculate_salary_pay(salary) -> dict`
    *   Computes the weekly pay for salaried workers (`salary / 52`) and zeroes out all hour-related fields.

---

## 2. Exact Order of Validation Checks (Fail-Fast Architecture)

When `pay_summary` is invoked, checks must occur in the exact order below to satisfy test expectation sequences:

1.  **Role Normalization & Validation:** Validate the `role` string. If invalid, raise `ValueError`.
2.  **Hours Length Validation:** Check that `hours` is iterable and contains *exactly* 5 items. If not, raise `ValueError`.
3.  **Daily Hours Boundary Validation:** Iterate through `hours` (indices 0 to 4). If any value is `< 0` or `> 24`, raise `ValueError`.
4.  **Holiday Hour Constraints:** Check if any day index in `holidays` has a corresponding hour value $> 0$. If so, raise `ValueError`.
5.  **Role-Specific Financial Validation:**
    *   If role is `"staff"` and `rate <= 0`, raise `ValueError`.
    *   If role is `"manager"` or `"owner"` and `salary <= 0`, raise `ValueError`.

---

## 3. Data Flow & Calculation Logic

### Branch A: Salaried Roles (`manager`, `owner`)
1. Inputs bypass hour-accrual math.
2. `total_pay = round(salary / 52, 2)`
3. Return dictionary populates all hour metrics (`regular_hours`, `overtime_hours`, `double_time_hours`, `stat_days`, `stat_pay`) explicitly with `0` or `0.0`.

### Branch B: Hourly Role (`staff`)
1. **Stat Pay Processing:**
   * `stat_days = len(holidays)`
   * If `month_days_worked == 0` or `month_pay == 0`: `stat_pay_per_day = 0.0`
   * Else: `stat_pay_per_day = month_pay / month_days_worked`
   * `stat_pay = round(stat_pay_per_day * stat_days, 2)`
2. **Daily Hour Breakdown (Mon–Fri / Indices 0–4):**
   * Initialize counters: `regular_accumulated = 0`, `double_time_hours = 0`.
   * For each day `d` with hours `h`:
     * If `d` is in `holidays`, `h` is guaranteed to be `0` (validated earlier).
     * If `h > 12`:
       * `double_time_hours += (h - 12)`
       * `regular_accumulated += 12`
     * Else:
       * `regular_accumulated += h`
3. **Weekly Overtime Split:**
   * `regular_hours = min(40, regular_accumulated)`
   * `overtime_hours = max(0, regular_accumulated - 40)`
4. **Total Compensation Calculation:**
   * $\text{raw\_total} = (\text{regular\_hours} \times \text{rate}) + (\text{overtime\_hours} \times 1.5 \times \text{rate}) + (\text{double\_time\_hours} \times 2 \times \text{rate}) + \text{stat\_pay}$
   * `total_pay = round(raw_total, 2)`
5. Return the finalized dictionary mapping all keys to their computed numerical types.

### Developer

```python
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
    if not month_days_worked or month_days_worked <= 0 or not month_pay or month_pay <= 0:
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
```

### Tester

```python
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
```
