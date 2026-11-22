"""
ShiftWise: Feature 4 - Roles module.
COMP 3520 Assignment 4. Team: Thamalee Dasanayake, Akshana Leninrajah
"""

# Define the permissions mapping for each role
PERMISSIONS = {
    "staff": {
        "view_schedule": True,
        "book_own_shift": True,
        "request_holiday": True,
        "approve_staff_holiday": False,
        "approve_manager_holiday": False,
        "edit_any_shift": False,
        "view_pay_reports": False,
        "manage_staff": False,
        "delete_business": False,
    },
    "manager": {
        "view_schedule": True,
        "book_own_shift": True,
        "request_holiday": True,
        "approve_staff_holiday": True,
        "approve_manager_holiday": False,
        "edit_any_shift": True,
        "view_pay_reports": True,
        "manage_staff": False,
        "delete_business": False,
    },
    "owner": {
        "view_schedule": True,
        "book_own_shift": True,
        "request_holiday": False,
        "approve_staff_holiday": True,
        "approve_manager_holiday": True,
        "edit_any_shift": True,
        "view_pay_reports": True,
        "manage_staff": True,
        "delete_business": True,
    },
}


def can(role: str, action: str) -> bool:
    """Determine if a given role is allowed to perform a specific action.

    Role names ignore capital letters and extra spaces (e.g., "MANAGER", "Manager",
    " manager " all mean "manager"). Unknown roles or unknown actions return False.
    """
    if not isinstance(role, str) or not isinstance(action, str):
        return False

    # Normalize the role: strip whitespace and convert to lowercase
    normalized_role = role.strip().lower()

    # Check if the role and action are valid
    if normalized_role not in PERMISSIONS:
        return False

    if action not in PERMISSIONS[normalized_role]:
        return False

    return PERMISSIONS[normalized_role][action]
