### PM

Here are the requirements and edge cases for the `can(role, action)` feature, prepared for the development team:

### Requirements

1. **Role and Action Normalization:**
   * The `role` parameter must be case-insensitive and ignore leading/trailing/extra whitespace (e.g., `"MANAGER"`, `"Manager"`, `" manager "` all evaluate to `"manager"`).
   * The `action` parameter must match the defined action strings (e.g., `"view_schedule"`, `"book_own_shift"`, etc.).

2. **Action Permissions by Role:**
   * **Staff Permissions:**
     * Allowed: `view_schedule`, `book_own_shift`, `request_holiday`
     * Denied: `approve_staff_holiday`, `approve_manager_holiday`, `edit_any_shift`, `view_pay_reports`, `manage_staff`, `delete_business`
   * **Manager Permissions:**
     * Allowed: `view_schedule`, `book_own_shift`, `request_holiday`, `approve_staff_holiday`, `edit_any_shift`, `view_pay_reports`
     * Denied: `approve_manager_holiday`, `manage_staff`, `delete_business`
   * **Owner Permissions:**
     * Allowed: `view_schedule`, `book_own_shift`, `approve_staff_holiday`, `approve_manager_holiday`, `edit_any_shift`, `view_pay_reports`, `manage_staff`, `delete_business`
     * Denied: `request_holiday`

3. **Return Type:**
   * The function must strictly return a boolean (`True` or `False`).

---

### Edge Cases

1. **Unknown Roles:**
   * If a role is passed that is not `staff`, `manager`, or `owner` (e.g., `"admin"`, `""`, `123`, `None`), the function must return `False`.

2. **Unknown Actions:**
   * If an action is passed that is not part of the defined feature list (e.g., `"fire_employee"`, `""`, `None`), the function must return `False`.

3. **Malformed Inputs:**
   * Handle unexpected data types gracefully (e.g., passing integers or `None` for either `role` or `action`) without throwing unhandled exceptions; return `False`.

4. **Case/Whitespace Variations in Actions:**
   * Note: The spec specifies normalization for *roles*. Developers should verify if actions require exact matching or if they should also be case-normalized for safety, adhering strictly to the snake_case action strings provided in the spec.

### Architect

# Software Architecture: `roles.py`

As the software architect, I have designed the architecture for the `can(role, action)` feature in `roles.py`. Below is the blueprint detailing the data structures, helper functions, data flow, and exact order of execution to ensure robustness against malformed inputs and edge cases.

---

## 1. Data Structures & Configuration

To cleanly map permissions without nested `if/else` statements, we will use a constant mapping dictionary at the module level.

* **`VALID_ROLES`**: A set of accepted normalized role strings (`"staff"`, `"manager"`, `"owner"`).
* **`PERMISSION_MATRIX`**: A nested dictionary mapping normalized roles to a set of allowed actions.

```python
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
```

---

## 2. Helper Functions

### `_normalize_role(role)`
* **Purpose**: Safely clean and normalize the `role` input.
* **Logic**: 
  1. Check if `role` is of type `str`. If not (e.g., `None`, `int`, `dict`), return `None`.
  2. Convert to lowercase and strip whitespace (including collapsing internal extra spaces if necessary, though standard `.strip().lower()` handles edge cases like `" manager "`).
* **Returns**: A cleaned string or `None`.

### `_normalize_action(action)`
* **Purpose**: Safely validate the `action` input.
* **Logic**:
  1. Check if `action` is of type `str`. If not, return `None`.
  2. For safety against user error (as per edge case 4), we can `.strip().lower()` the action, or match it directly against the known action strings. Let's strip and lowercase it to be resilient.
* **Returns**: A cleaned action string or `None`.

---

## 3. Data Flow and Exact Order of Checks

When `can(role, action)` is invoked, it must execute the following checks in strict sequence:

1. **Type & Input Safety Check (Role)**:
   * Call `_normalize_role(role)`. 
   * If the result is `None` or not in `VALID_ROLES`, immediately return `False`.

2. **Type & Input Safety Check (Action)**:
   * Call `_normalize_action(action)`.
   * If the result is `None`, immediately return `False`.

3. **Permission Lookup**:
   * Access `PERMISSION_MATRIX[normalized_role]`.
   * Check if `normalized_action` exists within that role's action set.

4. **Return**:
   * Return `True` if present, otherwise `False`.

---

## 4. Function Signature

```python
def can(role: str, action: str) -> bool:
    """
    Determines if a given role has permission to perform a specific action.
    """
    # Order of execution enforced here.
    ...
```

### Developer

```python
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
    return cleaned if cleaned else None


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
```

### Tester

```python
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
```
