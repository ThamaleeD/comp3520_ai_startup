### PM

Here are the requirements and edge cases for the `pay_summary` function, organized for development.

### 1. General & Normalization Requirements
1. **Role Normalization:** The `role` argument must be case-insensitive and ignore leading/trailing whitespace (e.g., `"MANAGER"`, `"Manager"`, and `" manager "` all evaluate to `"manager"`). Valid roles are `"staff"`, `"manager"`, and `"owner"`.
2. **Rounding:** All monetary outputs (`stat_pay`, `total_pay`) must be rounded to exactly 2 decimal places.

---

### 2. Staff (Hourly) Calculation Requirements
3. **Daily Hour Validation & Double Time:** 
   - For each day (Monday through Friday), hours worked over 12 in a single day are classified as double-time hours. 
   - Only the excess hours over 12 for that specific day qualify for double-time ($2\times \text{rate}$).
   - The remaining hours for that day (up to 12) contribute to the weekly calculation.
4. **Weekly Overtime:**
   - Sum up each day's eligible hours (capped at a maximum of 12 hours counted per day, excluding any double-time portions).
   - The first 40 hours of this sum are paid at the regular rate ($1\times \text{rate}$).
   - Any hours exceeding 40 for the week are classified as overtime and paid at $1.5\times \text{rate}$.
5. **Exclusion Rule:** Double-time hours do **not** count toward the 40-hour weekly threshold for overtime calculation.
6. **Statutory Holiday Pay:**
   - If a day is listed in `holidays`, that day is treated as a statutory holiday.
   - Stat pay per holiday = `month_pay / month_days_worked` (average daily pay over the last 30 days).
   - If `month_days_worked` is `0`, stat pay for that holiday is `0`.
7. **Staff Total Pay Formula:**
   $$\text{total\_pay} = (\text{regular\_hours} \times \text{rate}) + (\text{overtime\_hours} \times 1.5 \times \text{rate}) + (\text{double\_time\_hours} \times 2 \times \text{rate}) + \text{stat\_pay}$$

---

### 3. Manager and Owner (Salary) Calculation Requirements
8. **Salary Pay Structure:** For managers and owners, `total_pay` is calculated strictly as $\text{salary} / 52$, rounded to 2 decimal places.
9. **Salary Hour Fields:** For managers and owners, all hour-related return fields (`regular_hours`, `overtime_hours`, `double_time_hours`, `stat_days`, `stat_pay`) must be `0` (or `0.0`). They are not eligible for overtime, double time, or stat pay.

---

### 4. Error Handling (`ValueError` Triggers)
The function must raise a `ValueError` under any of the following conditions:
10. **Unknown Role:** The `role` argument does not match `"staff"`, `"manager"`, or `"owner"` (after normalization).
11. **Invalid Hours Length:** The `hours` list does not contain exactly 5 items (representing Mon–Fri).
12. **Out of Bounds Hours:** Any value in the `hours` list is negative ($< 0$) or greater than 24 ($> 24$).
13. **Holiday Hours Violation:** Any day designated as a holiday in the `holidays` set has a non-zero hour value in the `hours` list (hours on a holiday must strictly be `0`).
14. **Invalid Staff Rate:** If the `role` is `"staff"` and `rate` is less than or equal to 0 ($\le 0$).
15. **Invalid Salary:** If the `role` is `"manager"` or `"owner"` and `salary` is less than or equal to 0 ($\le 0$).

---

### 5. Return Format Requirements
16. The function must return a dictionary with the exact following keys:
    ```python
    {
        "regular_hours": float/int,
        "overtime_hours": float/int,
        "double_time_hours": float/int,
        "stat_days": int,
        "stat_pay": float,
        "total_pay": float
    }
    ```

---

### 6. Edge Cases to Test
17. **Zero Hours Worked (Staff):** All 5 days are `0`, resulting in 0 pay unless stat holidays are present.
18. **Exact 40 Hours (Staff):** `[8, 8, 8, 8, 8]` yields 40 regular hours, 0 OT, 0 double time.
19. **Mixed Overtime & Double Time (Staff):** A day with $\ge 12$ hours (e.g., `[14, 8, 8, 8, 8]`) correctly splits into daily regular/capped hours and 2 double-time hours, while properly pooling remaining weekly hours toward overtime.
20. **Multiple Holidays:** Multiple days present in the `holidays` set (with corresponding `hours` strictly equal to `0` on those days).
21. **Zero Month Days Worked:** `month_days_worked = 0` alongside a holiday should result in `0` stat pay for that day without causing a division-by-zero error.
22. **Case and Spacing Variations:** Passing `" MANAGER "` or `"owner"` with trailing spaces correctly routes to the appropriate calculation logic.

### Architect

As the software architect, here is the structural and logical design for the `pay.py` module implementing the `pay_summary` feature.

---

# Architectural Design: `pay.py`

## 1. Data Flow & Execution Order

The function must follow a strict validation-first approach before computing any payroll figures. 

```
[Input: pay_summary()] 
   │
   ├─► Step 1: Normalize & Validate Role
   ├─► Step 2: Validate Hours Length & Bounds
   ├─► Step 3: Validate Role-Specific Pay Parameters (rate vs salary)
   ├─► Step 4: Validate Holiday-Hour Constraints
   │
   ├─► Step 5: Branch Execution
   │     ├─► Case A [Manager / Owner]: Compute Salary, Zero-out hours
   │     └─► Case B [Staff]: Compute Daily/Weekly Hours, Stat Pay, and Gross Pay
   │
   └─► Step 6: Construct and Return Structured Dictionary
```

---

## 2. Helper Functions & Responsibilities

To keep the main `pay_summary` clean and maintainable, the module will utilize private helper functions:

1. **`_normalize_role(role)`**
   * *Purpose:* Strips whitespace and converts the role string to lowercase.
   * *Validation:* Raises `ValueError` if the result is not in `{"staff", "manager", "owner"}`.

2. **`_validate_inputs(role, hours, rate, salary, holidays)`**
   * *Purpose:* Aggregates all precondition checks to fail fast.
   * *Checks:*
     * `hours` length == 5.
     * All items in `hours` are numbers between $0$ and $24$ inclusive.
     * If role is `"staff"`, `rate > 0`.
     * If role is `"manager"` or `"owner"`, `salary > 0`.
     * For every day index $i$ in `holidays`, `hours[i] == 0` (Raises `ValueError` if a holiday has non-zero hours).

3. **`_calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)`**
   * *Purpose:* Executes the complex hourly, overtime, double-time, and stat pay logic.
   * *Logic Flow:*
     * **Stat Pay Calculation:** 
       * Count number of holidays: `stat_days = len(holidays)`.
       * Daily average stat pay = `(month_pay / month_days_worked)` if `month_days_worked > 0` else `0.0`.
       * Total `stat_pay = stat_days * daily_stat_pay`.
     * **Daily Processing Loop (Mon–Fri, indices 0–4):**
       * For each day, if day is in `holidays`, hours are guaranteed to be `0` (skipped in accumulation).
       * Otherwise, compute `double_time_day = max(0, day_hours - 12)`.
       * Compute `regular_pool_day = min(12, day_hours)`.
     * **Weekly Overtime Allocation:**
       * Sum up all `regular_pool_day` values to get `total_pool_hours`.
       * `regular_hours = min(40, total_pool_hours)`
       * `overtime_hours = max(0, total_pool_hours - 40)`
       * Sum up all `double_time_day` values to get `double_time_hours`.
     * **Financial Calculation:**
       * `gross = (regular_hours * rate) + (overtime_hours * 1.5 * rate) + (double_time_hours * 2 * rate) + stat_pay`
       * Round `stat_pay` and `total_pay` to 2 decimal places.

---

## 3. Exact Order of Validation Checks (Raising `ValueError`)

The implementation must check and raise errors in this exact conceptual sequence:

1. **Role validation:** If `role` is not a valid string or normalizes to an unknown role $\rightarrow$ `ValueError`.
2. **Hours structure validation:** If `len(hours) != 5` $\rightarrow$ `ValueError`.
3. **Hours boundary validation:** If any hour $< 0$ or $> 24$ $\rightarrow$ `ValueError`.
4. **Pay parameter validation:** 
   * If role is `"staff"` and `rate <= 0` $\rightarrow$ `ValueError`.
   * If role is in `{"manager", "owner"}` and `salary <= 0` $\rightarrow$ `ValueError`.
5. **Holiday-hour conflict validation:** If any day index present in `holidays` has `hours[index] != 0` $\rightarrow$ `ValueError`.

---

## 4. Return Dictionary Structure

Regardless of the role, the function will always return a dictionary matching this exact schema:

```python
{
    "regular_hours": 0,       # int or float
    "overtime_hours": 0,      # int or float
    "double_time_hours": 0,   # int or float
    "stat_days": 0,           # int
    "stat_pay": 0.0,          # float (rounded to 2 decimal places)
    "total_pay": 0.0          # float (rounded to 2 decimal places)
}
```
For salaried staff (`manager`/`owner`), the hour metrics and `stat_pay` will explicitly be `0` (or `0.0` where floats are expected), and `total_pay` will be `round(salary / 52, 2)`.

### Developer

```python
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
            "regular_hours": 0,
            "overtime_hours": 0,
            "double_time_hours": 0,
            "stat_days": 0,
            "stat_pay": 0.0,
            "total_pay": total_pay,
        }
    else:
        return _calculate_staff_pay(hours, rate, holidays, month_pay, month_days_worked)
```

### Tester

```python
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
```
