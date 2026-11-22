"""
ShiftWise: Roles Feature (roles.py)
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

# QA Fix: Actions should also be verified against a known set of actions 
# to ensure unknown actions correctly return False per the spec rule:
# "Unknown role or unknown action -> False."
VALID_ACTIONS = {
    "view_schedule",
    "book_own_shift",
    "request_holiday",
    "approve_staff_holiday",
    "approve_manager_holiday",
    "edit_any_shift",
    "view_pay_reports",
    "manage_staff",
    "delete_business"
}


def _normalize_role(role) -> str | None:
    """
    Safely clean and normalize the role input.
    Returns a cleaned string or None if invalid.
    """
    if not isinstance(role, str):
        return None
    # Normalize by converting to lowercase and stripping whitespace
    cleaned = " ".join(role.lower().split())
    if cleaned in VALID_ROLES:
        return cleaned
    return None


def _normalize_action(action) -> str | None:
    """
    Safely validate and normalize the action input.
    Returns a cleaned action string or None if invalid.
    """
    if not isinstance(action, str):
        return None
    # Normalize by converting to lowercase and stripping whitespace
    cleaned = " ".join(action.lower().split())
    # QA Fix: Ensure the action is a recognized action in the system
    if cleaned in VALID_ACTIONS:
        return cleaned
    return None


def can(role, action) -> bool:
    """
    Determines if a given role has permission to perform a specific action.
    Returns strictly True or False.
    """
    # 1. Type & Input Safety Check (Role)
    normalized_role = _normalize_role(role)
    if normalized_role is None:
        return False

    # 2. Type & Input Safety Check (Action)
    normalized_action = _normalize_action(action)
    if normalized_action is None:
        return False

    # 3. Permission Lookup & Return
    return normalized_action in PERMISSION_MATRIX[normalized_role]
