# ShiftWise: Feature Specs

COMP 3520 Assignment 4. Team: Thamalee Dasanayake, Akshana Leninrajah

ShiftWise is a made-up startup app for scheduling shifts at any company that runs shift work. Example: construction, where 12-hour shifts are common.
Each feature is one Python function. The AI only sees this file. The hidden tests are kept separately.

**Applies to every feature:** role names ignore capital letters and extra spaces. `"MANAGER"`, `"Manager"`, `" manager "` all mean `"manager"`. Same for `"staff"` and `"owner"`.

**Roles and pay type:**

| role | pay type | holiday approved by |
|---|---|---|
| staff | hourly | manager (owner if there's no manager) |
| manager | salary | owner |
| owner | salary | no approval needed |

---

## Feature 1: Sign-up

`signup(email, password, role, existing_emails) -> str`

- `email`, `password`: strings
- `role`: `"staff"`, `"manager"`, or `"owner"` (the role picked at sign-up)
- `existing_emails`: dict of three lists, one per role, with emails already registered:

```python
existing_emails = {
    "staff":   ["staff_amy@example.com", "staff_raj@example.com"],
    "manager": ["manager_lee@example.com"],
    "owner":   ["owner@example.com"],
}
```

**Email naming rule:**

The part before `@` must follow one of these formats:

| format | example | when to use |
|---|---|---|
| `<role>_<name>` | `staff_mia@example.com` | normal |
| `<role>_<name>.<surname>` | `staff_amy.chen@example.com` | name already taken |
| `<role>_<name><empID>` | `staff_amy1042@example.com` | name already taken |

- `<role>` is `staff` or `manager` and must match the role picked.
- `<name>` and `<surname>` are letters only. `<empID>` is digits only.
- Owners don't need a prefix. Any valid email is fine.

**Rules (check in this order, return the first error):**

1. Ignore spaces at the start/end of the email, and ignore capital letters everywhere.
2. Email must have exactly one `@`, something before it, and a `.` in the part after it (not first or last character of that part). Else `"INVALID_EMAIL"`.
3. `role` must be `staff`, `manager` or `owner`. Else `"INVALID_ROLE"`.
4. For staff and manager, the email must start with `staff_` or `manager_` to match the role. Else `"WRONG_PREFIX"`.
5. For staff and manager, the rest of the part before `@` must match one of the 3 formats above. Else `"INVALID_NAME"`.
6. Password must be 8+ characters, with at least 1 number, 1 capital letter and 1 special character (anything that isn't a letter, number or space, like `! @ # $ %`). Else `"WEAK_PASSWORD"`.
7. If the email is already in **any** of the three lists, return `"EMAIL_TAKEN"`. (The user should then add their surname or employee ID.)
8. Otherwise return `"OK"`.

**Examples (using `existing_emails` above):**

| email | role | password | result |
|---|---|---|---|
| `"staff_mia@example.com"` | staff | `"Secret123!"` | `"OK"` |
| `"staff_miaexample.com"` | staff | `"Secret123!"` | `"INVALID_EMAIL"` |
| `"mia@example.com"` | staff | `"Secret123!"` | `"WRONG_PREFIX"` |
| `"staff_lee@example.com"` | manager | `"Secret123!"` | `"WRONG_PREFIX"` |
| `"staff_mia_2@example.com"` | staff | `"Secret123!"` | `"INVALID_NAME"` |
| `"staff_mia@example.com"` | staff | `"secret"` | `"WEAK_PASSWORD"` |
| `"staff_mia@example.com"` | staff | `"Secret123"` | `"WEAK_PASSWORD"` (no special character) |
| `"STAFF_AMY@example.com"` | staff | `"Secret123!"` | `"EMAIL_TAKEN"` |
| `"staff_amy.chen@example.com"` | staff | `"Secret123!"` | `"OK"` |
| `"staff_amy1042@example.com"` | staff | `"Secret123!"` | `"OK"` |
| `"owner@example.com"` | owner | `"Secret123!"` | `"EMAIL_TAKEN"` |

---

## Feature 2: Shift booking

`book_shift(shifts, staff, date, start, end) -> str`

- `shifts`: list of existing shifts, each a dict `{"staff": str, "date": str, "start": str, "end": str}`
- `date`: `"MM-DD-YY"` format, e.g. `"11-16-26"` (Mon, Nov 16, 2026)
- `start`, `end`: `"HH:MM:SS"` format, 24-hour clock, e.g. `"09:00:00"`, `"17:30:00"`
- A staff member's schedule = their shifts, shown by date and start/end time.

**Daily limit and break:**

- Every working day includes one 30-minute unpaid break.
- Hours worked on a day = total scheduled time that day − 30 min.
- A normal shift is up to **12 hours worked** (e.g. 07:00:00–19:30:00). Hours over 12 are allowed but paid as double time (see Feature 5).
- Hard safety limit: max **16 hours worked per day**.
- A week runs Monday to Sunday.

**Rules (check in this order, return the first error):**

1. `date` must be a real date in `MM-DD-YY` format. Else `"INVALID_DATE"`.
2. `start` and `end` must be real times in `HH:MM:SS` format, and `end` must be after `start` on the same day (no overnight shifts). Else `"INVALID_TIME"`.
3. Each staff member has their own schedule. Different staff members CAN have overlapping shifts (amy 09:00–17:30 and raj 09:00–17:30 is fine). Only a staff member's own shifts can't overlap each other on the same date. Touching is fine (one ends at 13:00:00, next starts at 13:00:00). Else `"OVERLAP"`.
4. That staff member's hours worked on that date, including this shift, can't go over 16. Else `"TOO_LONG"`.
5. That staff member's hours worked for the week (Mon–Sun), including this shift, can't go over 60. Else `"OVER_HOURS"`. (Over 40 is allowed but paid as overtime, see Feature 5.)
6. Otherwise return `"OK"`. Do not change the `shifts` list.

**Examples:**

| existing shifts | new shift | result |
|---|---|---|
| none | amy, 11-16-26, 09:00:00–17:30:00 | `"OK"` (8 hrs worked) |
| none | amy, 11-16-26, 07:00:00–19:30:00 | `"OK"` (12 hrs worked) |
| none | amy, 11-16-26, 06:00:00–23:00:00 | `"TOO_LONG"` (16.5 hrs worked) |
| none | amy, 2026-11-16, 09:00:00–17:00:00 | `"INVALID_DATE"` |
| none | amy, 11-16-26, 17:00:00–09:00:00 | `"INVALID_TIME"` |
| amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 12:00:00–16:00:00 | `"OVERLAP"` |
| amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 13:00:00–17:30:00 | `"OK"` (8 hrs worked that day) |
| amy 11-16-26 09:00:00–17:30:00 | raj, 11-16-26, 09:00:00–17:30:00 | `"OK"` (different staff) |
| amy Mon–Thu (11-16 to 11-19), 07:00:00–19:30:00 each | amy, 11-20-26, 07:00:00–19:30:00 | `"OK"` (60 hrs that week) |
| amy Mon–Fri (11-16 to 11-20), 07:00:00–19:30:00 each | amy, 11-21-26, 07:00:00–08:00:00 | `"OVER_HOURS"` (60.5 hrs) |

---

## Feature 3: Holiday requests

ShiftWise is for companies with a set team structure, so there are no shift swaps. Instead, staff and managers request holidays, and someone above them approves.

`create_request(requester, requester_role, date) -> dict or str`

- `date`: `"MM-DD-YY"` format
- Rules (in order):
  1. Unknown role → `"INVALID_ROLE"`
  2. Bad date → `"INVALID_DATE"`
  3. Staff or manager → return `{"requester": requester, "requester_role": role, "date": date, "status": "PENDING"}`
  4. Owner → same dict, but `"status": "APPROVED"` (owners don't need approval)

`act(request, action, user, role, has_manager) -> str`

- `action`: `"approve"` or `"reject"`
- `user`, `role`: the person trying to approve or reject
- `has_manager`: `True` if the business has at least one manager, else `False`

**Rules (check in this order):**

1. Unknown action → `"UNKNOWN_ACTION"`
2. Unknown role → `"INVALID_ROLE"`
3. Permission:
   - A staff request is approved/rejected by a **manager**. If `has_manager` is `False`, the **owner** approves it instead.
   - A manager request can only be approved/rejected by an **owner**
   - Nobody can approve or reject their own request
   - Else → `"NOT_ALLOWED"`
4. The request must be `PENDING`. Else → `"INVALID_STATE"`
5. On success, update `request["status"]` to `"APPROVED"` or `"REJECTED"` and return it.
6. If there's an error, the status must not change.

**Flow:**

```
staff request   --(manager approves/rejects)-->  APPROVED / REJECTED
                  (owner, only if no manager)
manager request --(owner approves/rejects)---->  APPROVED / REJECTED
owner request   --------------------------------> APPROVED (automatic)
```

**Examples:**

| request from | action by | result |
|---|---|---|
| amy (staff) | lee (manager), approve | `"APPROVED"` |
| amy (staff) | raj (staff), approve | `"NOT_ALLOWED"` |
| lee (manager) | lee (manager), approve | `"NOT_ALLOWED"` (own request) |
| lee (manager) | owner (owner), approve | `"APPROVED"` |
| lee (manager) | kim (MANAGER), approve | `"NOT_ALLOWED"` |
| amy (staff), has_manager = False | owner (owner), approve | `"APPROVED"` |
| amy (staff), has_manager = True | owner (owner), approve | `"NOT_ALLOWED"` (manager handles it) |
| amy (staff), already APPROVED | lee (manager), reject | `"INVALID_STATE"` |

---

## Feature 4: Roles

`can(role, action) -> bool`

| action | staff | manager | owner |
|---|---|---|---|
| `view_schedule` | yes | yes | yes |
| `book_own_shift` | yes | yes | yes |
| `request_holiday` | yes | yes | no |
| `approve_staff_holiday` | no | yes | yes (only used when there's no manager) |
| `approve_manager_holiday` | no | no | yes |
| `edit_any_shift` | no | yes | yes |
| `view_pay_reports` | no | yes | yes |
| `manage_staff` | no | no | yes |
| `delete_business` | no | no | yes |

**Rules:**

1. Role names ignore capital letters and spaces (`"MANAGER"` = `"manager"`).
2. Unknown role or unknown action → `False`.

---

## Feature 5: Pay summary

`pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked) -> dict`

- `role`: staff, manager or owner
- `hours`: list of 5 numbers, hours worked Mon to Fri
- `rate`: hourly pay (staff only)
- `salary`: yearly salary (manager and owner only)
- `holidays`: set of day numbers (0 = Mon to 4 = Fri) that are stat holidays this week
- `month_pay`, `month_days_worked`: what the staff member earned and how many days they worked in the last 30 days (used for stat pay)

**Staff (hourly) rules:**

1. **Double time:** hours over 12 in a single day are paid at 2× rate. Only that day's extra hours are double time.
2. **Overtime:** add up each day's hours (counting max 12 per day). The first 40 are regular. Anything over 40 for the week is overtime at 1.5× rate.
3. Double-time hours do NOT count toward the 40.
4. **Stat pay:** each holiday day is paid as stat pay instead of hours.
   - Stat pay per day = `month_pay / month_days_worked` (the average day's pay over the last month)
   - If `month_days_worked` is 0, stat pay is 0
   - Hours on a holiday day must be 0
5. `total_pay = regular×rate + overtime×1.5×rate + double×2×rate + stat_pay`, rounded to 2 decimals.

**Manager and owner (salary) rules:**

6. `total_pay = salary / 52`, rounded to 2 decimals. No overtime, double time or stat pay (it's all covered by salary). All hour fields are 0.

**Errors (raise `ValueError`):**

7. Unknown role, `hours` isn't 5 items, any hours are negative or over 24, hours on a holiday day, staff `rate` is 0 or less, or manager/owner `salary` is 0 or less.

**Return:**

```python
{"regular_hours": ..., "overtime_hours": ..., "double_time_hours": ...,
 "stat_days": ..., "stat_pay": ..., "total_pay": ...}
```

**Examples (staff, rate = 20, no holidays unless shown):**

| hours (Mon–Fri) | other | regular | OT | double | stat | total_pay |
|---|---|---|---|---|---|---|
| `[8,8,8,8,8]` | | 40 | 0 | 0 | 0 | 800.00 |
| `[10,10,10,10,5]` | | 40 | 5 | 0 | 0 | 950.00 |
| `[14,8,8,8,8]` | | 40 | 4 | 2 | 0 | 1000.00 |
| `[0,8,8,8,8]` | holiday Mon, month_pay 3200, 20 days | 32 | 0 | 0 | 160.00 | 800.00 |

**Examples (salary):**

| role | salary | total_pay |
|---|---|---|
| `"manager"` | 78000 | 1500.00 |
| `"MANAGER"` | 78000 | 1500.00 |
| `"owner"` | 104000 | 2000.00 |
