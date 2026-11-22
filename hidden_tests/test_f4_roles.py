"""Hidden tests for Feature 4: Roles.

Expected results were set by the team from specs/specs.md.
The AI under test never sees this file.
"""
import pytest
from roles import can

# action: (staff, manager, owner)
TABLE = {
    "view_schedule":           (True,  True,  True),
    "book_own_shift":          (True,  True,  True),
    "request_holiday":         (True,  True,  False),
    "approve_staff_holiday":   (False, True,  True),
    "approve_manager_holiday": (False, False, True),
    "edit_any_shift":          (False, True,  True),
    "view_pay_reports":        (False, True,  True),
    "manage_staff":            (False, False, True),
    "delete_business":         (False, False, True),
}

FULL = [(role, action, allowed[i])
        for action, allowed in TABLE.items()
        for i, role in enumerate(["staff", "manager", "owner"])]


@pytest.mark.parametrize("role,action,expected", FULL,
                         ids=[f"{r}-{a}" for r, a, _ in FULL])
def test_permission_table(role, action, expected):
    assert can(role, action) is expected


@pytest.mark.parametrize("role", ["MANAGER", "Manager", " manager ", "mAnAgEr"])
def test_role_ignores_caps_and_spaces(role):
    assert can(role, "approve_staff_holiday") is True
    assert can(role, "delete_business") is False


@pytest.mark.parametrize("role,action", [
    ("intern", "view_schedule"),
    ("", "view_schedule"),
    ("owner", "fly_to_moon"),
    ("staff", ""),
    ("admin", "delete_business"),
])
def test_unknown_is_false(role, action):
    assert can(role, action) is False
