### Developer

```python
"""
ShiftWise Feature 4: Roles
COMP 3520 Assignment 4
Team: Thamalee Dasanayake, Akshana Leninrajah
"""

# Define the permissions matrix for each role
PERMISSIONS = {
    "staff": {
        "view_schedule",
        "book_own_shift",
        "request_holiday",
    },
    "manager": {
        "view_schedule",
        "book_own_shift",
        "request_holiday",
        "approve_staff_holiday",
        "edit_any_shift",
        "view_pay_reports",
    },
    "owner": {
        "view_schedule",
        "book_own_shift",
        "approve_staff_holiday",
        "approve_manager_holiday",
        "edit_any_shift",
        "view_pay_reports",
        "manage_staff",
        "delete_business",
    },
}


def can(role: str, action: str) -> bool:
    """Check if a given role is permitted to perform a specific action.

    Role names and actions are case-insensitive and ignore extra whitespace.
    Returns False if the role or action is unknown.
    """
    if not isinstance(role, str) or not isinstance(action, str):
        return False

    # Normalize role: strip whitespace and convert to lowercase
    normalized_role = role.strip().lower()

    # Normalize action: strip whitespace and convert to lowercase
    normalized_action = action.strip().lower()

    # Check if the role exists in our permissions table
    if normalized_role not in PERMISSIONS:
        return False

    # Check if the action is allowed for this role
    return normalized_action in PERMISSIONS[normalized_role]
```
