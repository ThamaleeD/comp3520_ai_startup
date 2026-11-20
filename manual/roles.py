def can(role, action) -> bool:
    """
    Check whether a user role has permission
    to perform a specific action.
    """

    # Normalize the role
    role = role.strip().lower()

    # Define permissions for each role
    permissions = {
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

    # Unknown roles return False
    if role not in permissions:
        return False

    # Check whether the action is permitted
    return action in permissions[role]