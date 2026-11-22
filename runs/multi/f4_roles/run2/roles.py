"""
ShiftWise: Feature 4 - Roles
COMP 3520 Assignment 4. Team: Thamalee Dasanayake, Akshana Leninrajah
"""

VALID_ROLES = {"staff", "manager", "owner"}

PERMISSION_MATRIX = {
    "staff": {
        "view_schedule",
        "book_own_shift",
        "request_holiday"
    },
    "manager": {
        "view_schedule",
        "book_own_shift",
        "request_holiday",
        "approve_staff_holiday",
        "edit_any_shift",
        "view_pay_reports"
    },
    "owner": {
        "view_schedule",
        "book_own_shift",
        "approve_staff_holiday",
        "approve_manager_holiday",
        "edit_any_shift",
        "view_pay_reports",
        "manage_staff",
        "delete_business"
    }
}


def _normalize_role(role):
    """
    Handles type safety and normalization for the role string.
    1. Check if role is an instance of str. If not, return None.
    2. Convert the string to lowercase.
    3. Strip leading and trailing whitespace.
    4. Return the cleaned string.
    """
    if not isinstance(role, str):
        return None
    return role.lower().strip()


def can(role, action) -> bool:
    """
    Determines if a given role is permitted to perform a specific action.
    """
    # 1. Type & Null Check for Role + Normalization
    normalized_role = _normalize_role(role)
    if normalized_role is None:
        return False

    # 2. Role Existence Check
    if normalized_role not in VALID_ROLES:
        return False

    # 3. Type Check for Action
    if not isinstance(action, str):
        return False

    # 4. Action Existence & Permission Evaluation
    allowed_actions = PERMISSION_MATRIX.get(normalized_role, set())
    return action in allowed_actions
