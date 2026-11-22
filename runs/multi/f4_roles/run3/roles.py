"""
ShiftWise: Feature 4 - Roles
Module: roles.py
"""

PERMISSIONS = {
    "view_schedule": {"staff", "manager", "owner"},
    "book_own_shift": {"staff", "manager", "owner"},
    "request_holiday": {"staff", "manager"},
    "approve_staff_holiday": {"manager", "owner"},
    "approve_manager_holiday": {"owner"},
    "edit_any_shift": {"manager", "owner"},
    "view_pay_reports": {"manager", "owner"},
    "manage_staff": {"owner"},
    "delete_business": {"owner"},
}

VALID_ROLES = {"staff", "manager", "owner"}


def _normalize_role(role):
    """
    Safely normalize the input role string.
    Returns the lowercased, stripped string if it's a string, else None.
    """
    if not isinstance(role, str):
        return None
    return role.lower().strip()


def _validate_action(action):
    """
    Ensure the action is a valid, recognized string matching exact snake_case format.
    Returns True if valid, otherwise False.
    """
    if not isinstance(action, str):
        return False
    return action in PERMISSIONS


def can(role, action) -> bool:
    """
    Determine if a given role is allowed to perform a specific action.
    Returns a strict boolean (True or False).
    """
    # 1. Input Type & Role Normalization Check
    normalized_role = _normalize_role(role)
    if normalized_role not in VALID_ROLES:
        return False

    # 2. Action Validation Check
    if not _validate_action(action):
        return False

    # 3. Permission Evaluation & 4. Return
    allowed_roles = PERMISSIONS[action]
    return normalized_role in allowed_roles
