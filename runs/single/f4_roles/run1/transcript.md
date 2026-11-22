### Developer

```python
"""
ShiftWise Feature 4: Roles
COMP 3520 Assignment 4
Team: Thamalee Dasanayake, Akshana Leninrajah
"""

# Define the permissions matrix for each role
_PERMISSIONS = {
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
    """Determine if a given role is authorized to perform an action.

    Role names and actions are case-insensitive and ignore extra whitespace.
    Returns False if the role or action is unknown.
    """
    if not isinstance(role, str) or not isinstance(action, str):
        return False

    # Normalize role and action: strip whitespace and convert to lowercase
    normalized_role = " ".join(role.strip().lower().split())
    normalized_action = " ".join(action.strip().lower().split())

    # Check if role exists and if the action is in its permitted set
    role_permissions = _PERMISSIONS.get(normalized_role)
    if role_permissions is None:
        return False

    return normalized_action in role_permissions
```
