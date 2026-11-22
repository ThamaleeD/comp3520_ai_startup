### PM

Here are the requirements and edge cases for the `can(role, action)` feature, prepared for development:

### Requirements

1. **Role Normalization:** 
   - The developer must normalize the input `role` string by converting it to lowercase and stripping any leading or trailing whitespace before evaluation (e.g., `"MANAGER"`, `"Manager"`, and `" manager "` must all be evaluated as `"manager"`).

2. **Action Validation:** 
   - The developer must check if the provided `action` is one of the recognized actions listed in the feature spec.

3. **Permission Matrix Enforcement:**
   - **`view_schedule`**: Allowed for `staff`, `manager`, `owner`.
   - **`book_own_shift`**: Allowed for `staff`, `manager`, `owner`.
   - **`request_holiday`**: Allowed for `staff`, `manager`. Denied for `owner`.
   - **`approve_staff_holiday`**: Allowed for `manager`, `owner`. Denied for `staff`.
   - **`approve_manager_holiday`**: Allowed for `owner` only. Denied for `staff`, `manager`.
   - **`edit_any_shift`**: Allowed for `manager`, `owner`. Denied for `staff`.
   - **`view_pay_reports`**: Allowed for `manager`, `owner`. Denied for `staff`.
   - **`manage_staff`**: Allowed for `owner` only. Denied for `staff`, `manager`.
   - **`delete_business`**: Allowed for `owner` only. Denied for `staff`, `manager`.

4. **Return Value:**
   - The function must strictly return a boolean (`True` or `False`).

---

### Edge Cases

1. **Unknown Role:** 
   - If an unrecognized role is passed (e.g., `"admin"`, `""`, `None`, 123), the function must return `False` rather than throwing an error.

2. **Unknown Action:** 
   - If an unrecognized action is passed (e.g., `"delete_schedule"`, `""`, `None`, 456), the function must return `False` rather than throwing an error.

3. **Case Sensitivity in Actions:** 
   - Verify how action strings are handled. Unless specified otherwise, actions should match exact snake_case strings (e.g., `"view_schedule"`), but developers should ensure uppercase actions like `"VIEW_SCHEDULE"` or typo-ridden actions return `False`.

4. **Type Safety / Malformed Inputs:** 
   - The function must safely handle non-string inputs for `role` and `action` (such as integers, booleans, or `None`) without crashing.

### Architect

As the software architect, here is the design for the `roles.py` module, detailing the functions, helper structures, data flow, and the exact order of execution checks.

---

### Module Architecture: `roles.py`

#### 1. Constants & Data Structures
To implement the permission matrix cleanly, define a lookup dictionary mapping each recognized action to the set (or list) of roles permitted to perform it.

```python
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
```

---

#### 2. Helper Functions

*   **`_normalize_role(role)`**
    *   **Purpose:** Safely normalize the input role string.
    *   **Logic:**
        1. Check if `role` is an instance of `str`. If not (e.g., `None`, `int`, `bool`), immediately return `None` (or an invalid sentinel string).
        2. Convert the string to lowercase using `.lower()`.
        3. Strip leading and trailing whitespace using `.strip()`.
        4. Return the cleaned string.

*   **`_validate_action(action)`**
    *   **Purpose:** Ensure the action is a valid, recognized string matching exact snake_case format.
    *   **Logic:**
        1. Check if `action` is an instance of `str`. If not, return `False`.
        2. Check if the string exists as a key in the `PERMISSIONS` dictionary.
        3. Return `True` if valid, otherwise `False`.

---

#### 3. Main Function Flow: `can(role, action) -> bool`

The function must execute checks in a strict, fail-safe order to prevent type errors and handle edge cases gracefully.

**Exact Order of Execution:**

1.  **Input Type & Role Normalization Check:**
    *   Call `_normalize_role(role)`. 
    *   *Check:* If the normalized role is not in `VALID_ROLES`, return `False` immediately. (This natively handles `None`, empty strings, integers, and unknown roles like `"admin"` without throwing exceptions).

2.  **Action Validation Check:**
    *   Call `_validate_action(action)`.
    *   *Check:* If it returns `False`, return `False` immediately. (This handles non-string actions, `None`, and typos like `"view-schedule"` or `"VIEW_SCHEDULE"`).

3.  **Permission Evaluation:**
    *   Retrieve the set of allowed roles for the given `action` from the `PERMISSIONS` dictionary.
    *   Check if the normalized `role` is present in that allowed set.

4.  **Return:**
    *   Return the resulting boolean (`True` if authorized, `False` otherwise).

### Developer

```python
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
```

### Tester

```python
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
```
