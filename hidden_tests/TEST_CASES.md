# ShiftWise: Hidden Test Cases (for review)

Team: Thamalee Dasanayake, Akshana Leninrajah

Every row is one test. Check that the **Expected** column matches what you'd want from the spec. If any are wrong, tell me the test name.


## Feature 1: Sign-up (34 tests)

Password `Secret123!` is the good password unless shown.

| Test | Email | Password | Role | Expected |
|---|---|---|---|---|
| ok_staff | `staff_mia@example.com` | `Secret123!` | staff | **OK** |
| ok_manager | `manager_kim@example.com` | `Secret123!` | manager | **OK** |
| ok_owner_no_prefix | `boss@example.com` | `Secret123!` | owner | **OK** |
| ok_surname | `staff_amy.chen@example.com` | `Secret123!` | staff | **OK** |
| ok_emp_id | `staff_amy1042@example.com` | `Secret123!` | staff | **OK** |
| ok_spaces_trimmed | `  staff_mia@example.com  ` | `Secret123!` | staff | **OK** |
| ok_role_caps | `staff_mia@example.com` | `Secret123!` | STAFF | **OK** |
| ok_email_caps | `STAFF_MIA@EXAMPLE.COM` | `Secret123!` | staff | **OK** |
| email_no_at | `staff_miaexample.com` | `Secret123!` | staff | **INVALID_EMAIL** |
| email_two_at | `staff_mia@@example.com` | `Secret123!` | staff | **INVALID_EMAIL** |
| email_no_dot | `staff_mia@examplecom` | `Secret123!` | staff | **INVALID_EMAIL** |
| email_dot_first | `staff_mia@.com` | `Secret123!` | staff | **INVALID_EMAIL** |
| email_dot_last | `staff_mia@example.` | `Secret123!` | staff | **INVALID_EMAIL** |
| email_nothing_before | `@example.com` | `Secret123!` | owner | **INVALID_EMAIL** |
| role_unknown | `staff_mia@example.com` | `Secret123!` | intern | **INVALID_ROLE** |
| prefix_missing | `mia@example.com` | `Secret123!` | staff | **WRONG_PREFIX** |
| prefix_wrong_role | `staff_lee@example.com` | `Secret123!` | manager | **WRONG_PREFIX** |
| prefix_mgr_as_staff | `manager_kim@example.com` | `Secret123!` | staff | **WRONG_PREFIX** |
| name_underscore_num | `staff_mia_2@example.com` | `Secret123!` | staff | **INVALID_NAME** |
| name_empty | `staff_@example.com` | `Secret123!` | staff | **INVALID_NAME** |
| name_surname_and_id | `staff_amy.chen1042@example.com` | `Secret123!` | staff | **INVALID_NAME** |
| pw_too_short | `staff_mia@example.com` | `Se1!` | staff | **WEAK_PASSWORD** |
| pw_no_number | `staff_mia@example.com` | `Secret!!!` | staff | **WEAK_PASSWORD** |
| pw_no_capital | `staff_mia@example.com` | `secret123!` | staff | **WEAK_PASSWORD** |
| pw_no_special | `staff_mia@example.com` | `Secret123` | staff | **WEAK_PASSWORD** |
| pw_space_not_special | `staff_mia@example.com` | `Secret 123` | staff | **WEAK_PASSWORD** |
| taken_same | `staff_amy@example.com` | `Secret123!` | staff | **EMAIL_TAKEN** |
| taken_caps | `STAFF_AMY@example.com` | `Secret123!` | staff | **EMAIL_TAKEN** |
| taken_manager_list | `manager_lee@example.com` | `Secret123!` | manager | **EMAIL_TAKEN** |
| taken_owner_list | `owner@example.com` | `Secret123!` | owner | **EMAIL_TAKEN** |
| order_email_before_pw | `staff_miaexample.com` | `weak` | staff | **INVALID_EMAIL** |
| order_role_before_prefix | `mia@example.com` | `Secret123!` | intern | **INVALID_ROLE** |
| order_prefix_before_pw | `mia@example.com` | `weak` | staff | **WRONG_PREFIX** |
| order_pw_before_taken | `staff_amy@example.com` | `weak` | staff | **WEAK_PASSWORD** |

## Feature 2: Shift booking (29 tests)

Week = Mon 11-16-26 to Sun 11-22-26. A "full day" = 09:00:00–17:30:00 (8 hrs worked).

| Test | Existing shifts | New shift | Expected |
|---|---|---|---|
| ok_8_hrs | none | amy, 11-16-26, 09:00:00–17:30:00 | **OK** |
| ok_short_shift | none | amy, 11-16-26, 09:00:00–13:00:00 | **OK** |
| approval_8_5_hrs | none | amy, 11-16-26, 09:00:00–18:00:00 | **NEEDS_APPROVAL** |
| approval_12_hrs | none | amy, 11-16-26, 07:00:00–19:30:00 | **NEEDS_APPROVAL** |
| too_long_12_5_hrs | none | amy, 11-16-26, 06:30:00–19:30:00 | **TOO_LONG** |
| too_long_13_hrs | none | amy, 11-16-26, 06:00:00–19:30:00 | **TOO_LONG** |
| date_iso_format | none | amy, 2026-11-16, 09:00:00–17:00:00 | **INVALID_DATE** |
| date_not_real | none | amy, 02-30-26, 09:00:00–17:00:00 | **INVALID_DATE** |
| date_month_13 | none | amy, 13-01-26, 09:00:00–17:00:00 | **INVALID_DATE** |
| time_end_before | none | amy, 11-16-26, 17:00:00–09:00:00 | **INVALID_TIME** |
| time_end_equal | none | amy, 11-16-26, 09:00:00–09:00:00 | **INVALID_TIME** |
| time_hour_25 | none | amy, 11-16-26, 09:00:00–25:00:00 | **INVALID_TIME** |
| time_no_seconds | none | amy, 11-16-26, 09:00–17:00 | **INVALID_TIME** |
| overlap_same_staff | amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 12:00:00–16:00:00 | **OVERLAP** |
| overlap_inside | amy 11-16-26 09:00:00–17:00:00 | amy, 11-16-26, 10:00:00–11:00:00 | **OVERLAP** |
| touching_ok | amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 13:00:00–17:30:00 | **OK** |
| other_staff_ok | amy 11-16-26 09:00:00–17:30:00 | raj, 11-16-26, 09:00:00–17:30:00 | **OK** |
| other_date_ok | amy 11-17-26 09:00:00–17:30:00 | amy, 11-16-26, 09:00:00–17:30:00 | **OK** |
| two_shifts_8_hrs | amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 14:00:00–18:30:00 | **OK** |
| two_shifts_over_8 | amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 14:00:00–19:00:00 | **NEEDS_APPROVAL** |
| two_shifts_over_12 | amy 11-16-26 06:00:00–12:00:00 | amy, 11-16-26, 12:00:00–19:00:00 | **TOO_LONG** |
| week_40_ok | amy full days 11-16-26 to 11-19-26 | amy, 11-20-26, 09:00:00–17:30:00 | **OK** |
| week_over_40_sat | amy full days 11-16-26 to 11-20-26 | amy, 11-21-26, 09:00:00–10:00:00 | **NEEDS_APPROVAL** |
| week_over_40_sun | amy full days 11-16-26 to 11-20-26 | amy, 11-22-26, 09:00:00–10:00:00 | **NEEDS_APPROVAL** |
| last_week_not_counted | amy full days 11-09-26 to 11-13-26 | amy, 11-16-26, 09:00:00–17:30:00 | **OK** |
| other_staff_week_not_counted | raj full days 11-16-26 to 11-20-26 | amy, 11-21-26, 09:00:00–17:30:00 | **OK** |
| order_date_before_time | none | amy, 2026-11-16, 17:00:00–09:00:00 | **INVALID_DATE** |
| order_overlap_before_too_long | amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 06:00:00–19:30:00 | **OVERLAP** |
| does_not_change_shifts_list | amy 11-16-26 09:00:00–13:00:00 | amy, 11-16-26, 13:00:00–17:30:00 | **shifts list unchanged** |

## Feature 3: Holiday requests (26 tests)

**create_request**

| Test | Input | Expected |
|---|---|---|
| create_staff_pending | amy, staff, 12-24-26 | **PENDING** |
| create_manager_pending | lee, manager, 12-24-26 | **PENDING** |
| create_owner_auto_approved | boss, owner, 12-24-26 | **APPROVED** |
| create_role_caps | lee, MANAGER, 12-24-26 | **PENDING** |
| create_invalid_role | amy, intern, 12-24-26 | **INVALID_ROLE** |
| create_invalid_date | amy, staff, 2026-12-24 | **INVALID_DATE** |
| create_order_role_before_date | amy, intern, 2026-12-24 | **INVALID_ROLE** |

**act** (request starts as PENDING unless shown; on any error, status must not change)

| Test | Request from | Action by | Has manager? | Expected |
|---|---|---|---|---|
| mgr_approves_staff | amy (staff) | lee (manager), approve | yes | **APPROVED** |
| mgr_rejects_staff | amy (staff) | lee (manager), reject | yes | **REJECTED** |
| staff_approves_staff | amy (staff) | raj (staff), approve | yes | **NOT_ALLOWED** |
| owner_staff_has_mgr | amy (staff) | boss (owner), approve | yes | **NOT_ALLOWED** |
| owner_staff_no_mgr | amy (staff) | boss (owner), approve | no | **APPROVED** |
| owner_rejects_staff_no_mgr | amy (staff) | boss (owner), reject | no | **REJECTED** |
| owner_approves_mgr | lee (manager) | boss (owner), approve | yes | **APPROVED** |
| owner_rejects_mgr | lee (manager) | boss (owner), reject | yes | **REJECTED** |
| other_mgr_approves_mgr | lee (manager) | kim (manager), approve | yes | **NOT_ALLOWED** |
| mgr_approves_own | lee (manager) | lee (manager), approve | yes | **NOT_ALLOWED** |
| staff_approves_mgr | lee (manager) | amy (staff), approve | yes | **NOT_ALLOWED** |
| role_caps_manager | amy (staff) | lee (MANAGER), approve | yes | **APPROVED** |
| unknown_action | amy (staff) | lee (manager), cancel | yes | **UNKNOWN_ACTION** |
| unknown_role | amy (staff) | lee (boss), approve | yes | **INVALID_ROLE** |
| order_action_before_role | amy (staff) | lee (boss), cancel | yes | **UNKNOWN_ACTION** |
| act_already_approved | amy (staff), already APPROVED | lee (manager), reject | yes | **INVALID_STATE** |
| act_already_rejected | amy (staff), already REJECTED | lee (manager), approve | yes | **INVALID_STATE** |
| act_permission_before_state | amy (staff), already APPROVED | raj (staff), reject | yes | **NOT_ALLOWED** |
| full_flow_create_then_approve | amy (staff), new request | lee (manager), approve twice | yes | **APPROVED, then INVALID_STATE** |

## Feature 4: Roles (36 tests)

- **27 tests:** every cell of the permissions table in the spec (9 actions × 3 roles)
- **4 tests:** `MANAGER`, `Manager`, ` manager `, `mAnAgEr` all act as manager
- **5 tests:** unknown role or action returns False (`intern`, empty role, `admin`, `fly_to_moon`, empty action)

## Feature 5: Pay summary (28 tests)

**Staff (hourly)**

| Test | Hours Mon–Fri | Rate | Holidays; last month | Reg | OT | Double | Stat days | Stat pay | Total |
|---|---|---|---|---|---|---|---|---|---|
| normal_40 | [8, 8, 8, 8, 8] | 20 | none | 40 | 0 | 0 | 0 | 0 | **800.00** |
| overtime_5 | [10, 10, 10, 10, 5] | 20 | none | 40 | 5 | 0 | 0 | 0 | **950.00** |
| double_time_2 | [14, 8, 8, 8, 8] | 20 | none | 40 | 4 | 2 | 0 | 0 | **1000.00** |
| all_long_days | [13, 13, 13, 13, 13] | 20 | none | 40 | 20 | 5 | 0 | 0 | **1600.00** |
| exactly_12 | [12, 8, 8, 8, 4] | 20 | none | 40 | 0 | 0 | 0 | 0 | **800.00** |
| half_hour_ot | [8.5, 8, 8, 8, 8] | 20 | none | 40 | 0.5 | 0 | 0 | 0 | **815.00** |
| part_time | [4, 4, 4, 0, 0] | 20 | none | 12 | 0 | 0 | 0 | 0 | **240.00** |
| zero_hours | [0, 0, 0, 0, 0] | 20 | none | 0 | 0 | 0 | 0 | 0 | **0.00** |
| rounding | [8, 8, 8, 8, 8] | 17.33 | none | 40 | 0 | 0 | 0 | 0 | **693.20** |
| stat_mon | [0, 8, 8, 8, 8] | 20 | Mon; $3200 over 20 days | 32 | 0 | 0 | 1 | 160.0 | **800.00** |
| stat_two_days | [0, 8, 8, 8, 0] | 20 | Mon, Fri; $3200 over 20 days | 24 | 0 | 0 | 2 | 320.0 | **800.00** |
| stat_no_history | [0, 8, 8, 8, 8] | 20 | Mon; $0 over 0 days | 32 | 0 | 0 | 1 | 0.0 | **640.00** |
| stat_uneven | [0, 8, 8, 8, 8] | 20 | Mon; $1000 over 3 days | 32 | 0 | 0 | 1 | 333.33 | **973.33** |
| staff_role_caps | [8, 8, 8, 8, 8], role `STAFF` | 20 | none | 40 | 0 | 0 | 0 | 0 | **800.00** |

**Manager / owner (salary)** (all hour fields and stat pay must be 0)

| Test | Role | Yearly salary | Weekly total |
|---|---|---|---|
| manager | manager | 78000 | **1500.00** |
| manager_caps | MANAGER | 78000 | **1500.00** |
| owner | owner | 104000 | **2000.00** |
| rounding | manager | 50000 | **961.54** |

**Errors** (all must raise `ValueError`)

| Test | What's wrong |
|---|---|
| unknown_role | role `intern` |
| seven_days | 7 days of hours |
| four_days | 4 days of hours |
| negative_hours | -1 hours on Tue |
| over_24 | 25 hours on Mon |
| hours_on_holiday | 8 hours on a holiday (Mon) |
| rate_zero | staff rate 0 |
| rate_negative | staff rate -5 |
| salary_zero | manager salary 0 |
| salary_negative | owner salary -100 |

---

**Total: 153 tests.**
