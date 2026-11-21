import copy

import pytest

from manual.roles import can
from manual.holidays import create_request, act
from manual.signup import signup
from manual.booking import book_shift
from manual.pay import pay_summary


EXISTING = {
    "staff": ["staff_amy@example.com", "staff_raj@example.com"],
    "manager": ["manager_lee@example.com"],
    "owner": ["owner@example.com"],
}


# Feature 1: Sign-up

@pytest.mark.parametrize("email,role,password,expected", [
    ("staff_mia@example.com", "staff", "Secret123!", "OK"),
    ("staff_miaexample.com", "staff", "Secret123!", "INVALID_EMAIL"),
    ("mia@example.com", "staff", "Secret123!", "WRONG_PREFIX"),
    ("staff_lee@example.com", "manager", "Secret123!", "WRONG_PREFIX"),
    ("staff_mia_2@example.com", "staff", "Secret123!", "INVALID_NAME"),
    ("staff_mia@example.com", "staff", "secret", "WEAK_PASSWORD"),
    ("staff_mia@example.com", "staff", "Secret123", "WEAK_PASSWORD"),
    ("STAFF_AMY@example.com", "staff", "Secret123!", "EMAIL_TAKEN"),
    ("staff_amy.chen@example.com", "staff", "Secret123!", "OK"),
    ("staff_amy1042@example.com", "staff", "Secret123!", "OK"),
    ("owner@example.com", "owner", "Secret123!", "EMAIL_TAKEN"),
    ("owner_new@example.com", " OWNER ", "Secret123!", "OK"),
    ("staff_mia@example.com", "unknown", "Secret123!", "INVALID_ROLE"),
    ("staff_mia@example.com", "staff", "Secret123!", "OK"),
])
def test_signup(email, role, password, expected):
    assert signup(email, password, role, EXISTING) == expected


def test_signup_error_priority():
    assert signup("invalid", "weak", "unknown", EXISTING) == "INVALID_EMAIL"
    assert signup("staff_amy@example.com", "weak", "staff", EXISTING) == "WEAK_PASSWORD"


# Feature 2: Shift booking

def shift(staff, date, start, end):
    return {"staff": staff, "date": date, "start": start, "end": end}


@pytest.mark.parametrize("existing,staff,date,start,end,expected", [
    ([], "amy", "11-16-26", "09:00:00", "17:30:00", "OK"),
    ([], "amy", "11-16-26", "07:00:00", "19:30:00", "OK"),
    ([], "amy", "11-16-26", "06:00:00", "23:00:00", "TOO_LONG"),
    ([], "amy", "2026-11-16", "09:00:00", "17:00:00", "INVALID_DATE"),
    ([], "amy", "02-30-26", "09:00:00", "17:00:00", "INVALID_DATE"),
    ([], "amy", "11-16-26", "17:00:00", "09:00:00", "INVALID_TIME"),
    ([], "amy", "11-16-26", "25:00:00", "26:00:00", "INVALID_TIME"),
    ([shift("amy", "11-16-26", "09:00:00", "13:00:00")],
     "amy", "11-16-26", "12:00:00", "16:00:00", "OVERLAP"),
    ([shift("amy", "11-16-26", "09:00:00", "13:00:00")],
     "amy", "11-16-26", "13:00:00", "17:30:00", "OK"),
    ([shift("amy", "11-16-26", "09:00:00", "17:30:00")],
     "raj", "11-16-26", "09:00:00", "17:30:00", "OK"),
])
def test_booking(existing, staff, date, start, end, expected):
    before = copy.deepcopy(existing)
    assert book_shift(existing, staff, date, start, end) == expected
    assert existing == before


def test_booking_exact_weekly_limit():
    existing = [
        shift("amy", f"11-{day}-26", "07:00:00", "19:30:00")
        for day in range(16, 20)
    ]
    assert book_shift(existing, "amy", "11-20-26",
                      "07:00:00", "19:30:00") == "OK"


def test_booking_exceeds_weekly_limit():
    existing = [
        shift("amy", f"11-{day}-26", "07:00:00", "19:30:00")
        for day in range(16, 21)
    ]
    assert book_shift(existing, "amy", "11-21-26",
                      "07:00:00", "08:00:00") == "OVER_HOURS"


# Feature 3: Holiday requests

@pytest.mark.parametrize("role,expected", [
    ("staff", "PENDING"),
    ("manager", "PENDING"),
    ("owner", "APPROVED"),
    (" OWNER ", "APPROVED"),
])
def test_create_holiday(role, expected):
    request = create_request("amy", role, "11-16-26")
    assert request["status"] == expected
    assert request["requester_role"] == role.strip().lower()
    assert request["date"] == "11-16-26"


def test_create_holiday_errors():
    assert create_request("amy", "unknown", "11-16-26") == "INVALID_ROLE"
    assert create_request("amy", "staff", "02-30-26") == "INVALID_DATE"


@pytest.mark.parametrize("requester,requester_role,user,role,has_manager,action,expected", [
    ("amy", "staff", "lee", "manager", True, "approve", "APPROVED"),
    ("amy", "staff", "lee", "manager", True, "reject", "REJECTED"),
    ("amy", "staff", "raj", "staff", True, "approve", "NOT_ALLOWED"),
    ("lee", "manager", "lee", "manager", True, "approve", "NOT_ALLOWED"),
    ("lee", "manager", "boss", "owner", True, "approve", "APPROVED"),
    ("lee", "manager", "kim", "MANAGER", True, "approve", "NOT_ALLOWED"),
    ("amy", "staff", "boss", "owner", False, "approve", "APPROVED"),
    ("amy", "staff", "boss", "owner", True, "approve", "NOT_ALLOWED"),
    ("amy", "staff", "amy", "manager", True, "approve", "NOT_ALLOWED"),
])
def test_holiday_actions(requester, requester_role, user, role,
                         has_manager, action, expected):
    request = create_request(requester, requester_role, "11-16-26")
    result = act(request, action, user, role, has_manager)
    assert result == expected
    assert request["status"] == (
        expected if expected in {"APPROVED", "REJECTED"} else "PENDING"
    )


def test_holiday_invalid_state():
    request = create_request("amy", "staff", "11-16-26")
    request["status"] = "APPROVED"
    assert act(request, "reject", "lee", "manager", True) == "INVALID_STATE"
    assert request["status"] == "APPROVED"


def test_holiday_error_order():
    request = create_request("amy", "staff", "11-16-26")
    assert act(request, "cancel", "lee", "invalid", True) == "UNKNOWN_ACTION"
    assert act(request, "approve", "lee", "invalid", True) == "INVALID_ROLE"
    assert request["status"] == "PENDING"


# Feature 4: Roles

PERMISSIONS = {
    "view_schedule": (True, True, True),
    "book_own_shift": (True, True, True),
    "request_holiday": (True, True, False),
    "approve_staff_holiday": (False, True, True),
    "approve_manager_holiday": (False, False, True),
    "edit_any_shift": (False, True, True),
    "view_pay_reports": (False, True, True),
    "manage_staff": (False, False, True),
    "delete_business": (False, False, True),
}


@pytest.mark.parametrize("action,permissions", PERMISSIONS.items())
def test_role_matrix(action, permissions):
    for role, expected in zip(("staff", "manager", "owner"), permissions):
        assert can(role, action) is expected


def test_role_normalization_and_unknowns():
    assert can(" MANAGER ", "edit_any_shift") is True
    assert can("invalid", "view_schedule") is False
    assert can("staff", "unknown_action") is False


# Feature 5: Pay summary

@pytest.mark.parametrize("hours,holidays,month_pay,days,expected", [
    ([8, 8, 8, 8, 8], set(), 0, 0,
     (40, 0, 0, 0, 0, 800)),
    ([10, 10, 10, 10, 5], set(), 0, 0,
     (40, 5, 0, 0, 0, 950)),
    ([14, 8, 8, 8, 8], set(), 0, 0,
     (40, 4, 2, 0, 0, 1000)),
    ([0, 8, 8, 8, 8], {0}, 3200, 20,
     (32, 0, 0, 1, 160, 800)),
])
def test_staff_pay(hours, holidays, month_pay, days, expected):
    result = pay_summary("staff", hours, 20, 0,
                         holidays, month_pay, days)
    keys = (
        "regular_hours", "overtime_hours", "double_time_hours",
        "stat_days", "stat_pay", "total_pay"
    )
    for key, value in zip(keys, expected):
        assert result[key] == pytest.approx(value)


@pytest.mark.parametrize("role,salary,expected", [
    ("manager", 78000, 1500),
    ("MANAGER", 78000, 1500),
    ("owner", 104000, 2000),
])
def test_salary_pay(role, salary, expected):
    result = pay_summary(role, [0] * 5, 0, salary, set(), 0, 0)
    assert result["total_pay"] == expected
    for key in ("regular_hours", "overtime_hours",
                "double_time_hours", "stat_days", "stat_pay"):
        assert result[key] == 0


@pytest.mark.parametrize("role,hours,rate,salary,holidays", [
    ("unknown", [8] * 5, 20, 0, set()),
    ("staff", [8] * 4, 20, 0, set()),
    ("staff", [-1, 8, 8, 8, 8], 20, 0, set()),
    ("staff", [25, 8, 8, 8, 8], 20, 0, set()),
    ("staff", [8] * 5, 20, 0, {0}),
    ("staff", [8] * 5, 0, 0, set()),
    ("manager", [0] * 5, 0, 0, set()),
    ("owner", [0] * 5, 0, -1, set()),
])
def test_pay_validation(role, hours, rate, salary, holidays):
    with pytest.raises(ValueError):
        pay_summary(role, hours, rate, salary, holidays, 0, 0)
