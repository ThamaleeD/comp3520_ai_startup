"""Hidden tests for Feature 5: Pay summary.

Expected results were set by the team from specs/specs.md.
The AI under test never sees this file.
Signature: pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked)
"""
import pytest
from pay import pay_summary

A = pytest.approx

# ---------- staff (hourly) ----------
# (test id, hours, rate, holidays, month_pay, month_days,
#  regular, overtime, double, stat_days, stat_pay, total)
STAFF_CASES = [
    ("normal_40",        [8, 8, 8, 8, 8],      20, set(), 0, 0,     40, 0, 0, 0, 0,     800.00),
    ("overtime_5",       [10, 10, 10, 10, 5],  20, set(), 0, 0,     40, 5, 0, 0, 0,     950.00),
    ("double_time_2",    [14, 8, 8, 8, 8],     20, set(), 0, 0,     40, 4, 2, 0, 0,     1000.00),
    ("all_long_days",    [13, 13, 13, 13, 13], 20, set(), 0, 0,     40, 20, 5, 0, 0,    1600.00),
    ("exactly_12",       [12, 8, 8, 8, 4],     20, set(), 0, 0,     40, 0, 0, 0, 0,     800.00),
    ("half_hour_ot",     [8.5, 8, 8, 8, 8],    20, set(), 0, 0,     40, 0.5, 0, 0, 0,   815.00),
    ("part_time",        [4, 4, 4, 0, 0],      20, set(), 0, 0,     12, 0, 0, 0, 0,     240.00),
    ("zero_hours",       [0, 0, 0, 0, 0],      20, set(), 0, 0,     0, 0, 0, 0, 0,      0.00),
    ("rounding",         [8, 8, 8, 8, 8],   17.33, set(), 0, 0,     40, 0, 0, 0, 0,     693.20),
    ("stat_mon",         [0, 8, 8, 8, 8],      20, {0}, 3200, 20,   32, 0, 0, 1, 160.00, 800.00),
    ("stat_two_days",    [0, 8, 8, 8, 0],      20, {0, 4}, 3200, 20, 24, 0, 0, 2, 320.00, 800.00),
    ("stat_no_history",  [0, 8, 8, 8, 8],      20, {0}, 0, 0,       32, 0, 0, 1, 0.00,  640.00),
    ("stat_uneven",      [0, 8, 8, 8, 8],      20, {0}, 1000, 3,    32, 0, 0, 1, 333.33, 973.33),
]


@pytest.mark.parametrize(
    "hours,rate,holidays,mpay,mdays,reg,ot,dt,sdays,spay,total",
    [c[1:] for c in STAFF_CASES], ids=[c[0] for c in STAFF_CASES])
def test_staff_pay(hours, rate, holidays, mpay, mdays, reg, ot, dt, sdays, spay, total):
    r = pay_summary("staff", hours, rate, None, holidays, mpay, mdays)
    assert r["regular_hours"] == A(reg)
    assert r["overtime_hours"] == A(ot)
    assert r["double_time_hours"] == A(dt)
    assert r["stat_days"] == sdays
    assert r["stat_pay"] == A(spay, abs=0.01)
    assert r["total_pay"] == A(total, abs=0.001)


def test_staff_role_caps():
    r = pay_summary("STAFF", [8, 8, 8, 8, 8], 20, None, set(), 0, 0)
    assert r["total_pay"] == A(800.00)


# ---------- manager / owner (salary) ----------
SALARY_CASES = [
    ("manager",       "manager", 78000,  1500.00),
    ("manager_caps",  "MANAGER", 78000,  1500.00),
    ("owner",         "owner",   104000, 2000.00),
    ("rounding",      "manager", 50000,  961.54),
]


@pytest.mark.parametrize("role,salary,total",
                         [c[1:] for c in SALARY_CASES], ids=[c[0] for c in SALARY_CASES])
def test_salary_pay(role, salary, total):
    r = pay_summary(role, [12, 12, 12, 12, 12], None, salary, set(), 0, 0)
    assert r["total_pay"] == A(total, abs=0.001)
    assert r["regular_hours"] == 0
    assert r["overtime_hours"] == 0
    assert r["double_time_hours"] == 0
    assert r["stat_pay"] == 0


# ---------- errors ----------
ERROR_CASES = [
    ("unknown_role",     "intern",  [8, 8, 8, 8, 8],       20,   None,  set()),
    ("seven_days",       "staff",   [8, 8, 8, 8, 8, 0, 0], 20,   None,  set()),
    ("four_days",        "staff",   [8, 8, 8, 8],          20,   None,  set()),
    ("negative_hours",   "staff",   [8, -1, 8, 8, 8],      20,   None,  set()),
    ("over_24",          "staff",   [25, 8, 8, 8, 8],      20,   None,  set()),
    ("hours_on_holiday", "staff",   [8, 8, 8, 8, 8],       20,   None,  {0}),
    ("rate_zero",        "staff",   [8, 8, 8, 8, 8],       0,    None,  set()),
    ("rate_negative",    "staff",   [8, 8, 8, 8, 8],       -5,   None,  set()),
    ("salary_zero",      "manager", [8, 8, 8, 8, 8],       None, 0,     set()),
    ("salary_negative",  "owner",   [8, 8, 8, 8, 8],       None, -100,  set()),
]


@pytest.mark.parametrize("role,hours,rate,salary,holidays",
                         [c[1:] for c in ERROR_CASES], ids=[c[0] for c in ERROR_CASES])
def test_errors(role, hours, rate, salary, holidays):
    with pytest.raises(ValueError):
        pay_summary(role, hours, rate, salary, holidays, 0, 0)
