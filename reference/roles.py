P = {"staff": {"view_schedule", "book_own_shift", "request_holiday"},
     "manager": {"view_schedule", "book_own_shift", "request_holiday", "approve_staff_holiday", "edit_any_shift", "view_pay_reports"},
     "owner": {"view_schedule", "book_own_shift", "approve_staff_holiday", "approve_manager_holiday", "edit_any_shift", "view_pay_reports", "manage_staff", "delete_business"}}
def can(role, action):
    return action in P.get(role.strip().lower(), set())
