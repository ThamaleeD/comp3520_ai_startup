### PM

Here are the requirements and edge cases for the developers, organized by function based on the provided feature spec.

---

### Global / Pre-processing Requirements (Applies to all inputs involving roles)
1. **Role Normalization:** All role names must be processed to ignore casing and surrounding whitespace (e.g., `"MANAGER"`, `"Manager"`, and `" manager "` must all evaluate to `"manager"`). Valid roles are `"staff"`, `"manager"`, and `"owner"`.

---

### Function 1: `create_request(requester, requester_role, date)`

#### Requirements:
1. **Date Format:** The `date` parameter must strictly adhere to the `"MM-DD-YY"` format.
2. **Staff/Manager Creation:** When a valid requester with a role of `"staff"` or `"manager"` submits a request, return a dictionary with the structure:
   `{"requester": requester, "requester_role": normalized_role, "date": date, "status": "PENDING"}`.
3. **Owner Creation:** When a valid requester with a role of `"owner"` submits a request, return the same dictionary structure, but with `"status": "APPROVED"` (since owners do not require approval).

#### Edge Cases & Validation Order:
4. **Invalid Role (Check 1):** If `requester_role` does not match `"staff"`, `"manager"`, or `"owner"` (after normalization), immediately return `"INVALID_ROLE"`.
5. **Invalid Date (Check 2):** If `date` does not match the expected `"MM-DD-YY"` format or contains invalid date values, return `"INVALID_DATE"`. *(Note: Role validation takes precedence over date validation based on the specified order).*

---

### Function 2: `act(request, action, user, role, has_manager)`

#### Requirements:
1. **Action Execution:** If all validation checks pass, update `request["status"]` to either `"APPROVED"` or `"REJECTED"` (matching the requested action) and return the updated request dictionary.
2. **Immutability on Failure:** If any error or validation failure occurs during the execution of `act`, the original `request["status"]` must remain entirely unchanged.

#### Edge Cases & Validation Order:
3. **Unknown Action (Check 1):** If `action` is not explicitly `"approve"` or `"reject"`, return `"UNKNOWN_ACTION"`.
4. **Unknown Role (Check 2):** If the acting user's `role` is not a valid normalized role (`"staff"`, `"manager"`, or `"owner"`), return `"INVALID_ROLE"`.
5. **Permission - Self-Approval/Rejection (Check 3a):** A user cannot approve or reject their own request (i.e., `request["requester"]` must not equal `user`). If they attempt to, return `"NOT_ALLOWED"`.
6. **Permission - Staff Request when `has_manager` is `True` (Check 3b):** A staff request must be acted upon by a **manager**. If an owner or another staff member attempts to act on it when a manager exists, return `"NOT_ALLOWED"`.
7. **Permission - Staff Request when `has_manager` is `False` (Check 3c):** If `has_manager` is `False`, a staff request must be acted upon by an **owner**. If a manager or staff member attempts to act on it, return `"NOT_ALLOWED"`.
8. **Permission - Manager Request (Check 3d):** A manager request can *only* be acted upon by an **owner**. If a manager (even a different manager) or staff member attempts to act on it, return `"NOT_ALLOWED"`.
9. **Permission - Catch-all (Check 3e):** If any other unauthorized role combination attempts to act, return `"NOT_ALLOWED"`.
10. **State Validation (Check 4):** The target `request["status"]` must currently be `"PENDING"`. If the request is already `"APPROVED"` or `"REJECTED"`, return `"INVALID_STATE"`.

### Architect

As the software architect, here is the design for `holiday_requests.py`. 

---

# Architectural Design: `holiday_requests.py`

## 1. Helper Functions

*   `_normalize_role(role: str) -> str`
    *   **Purpose:** Strips whitespace and converts role strings to lowercase.
    *   **Logic:** `return role.strip().lower()`
    *   **Validation:** Returns the normalized string if valid (`"staff"`, `"manager"`, `"owner"`), otherwise raises a value error or returns `None`.

*   `_validate_date(date: str) -> bool`
    *   **Purpose:** Validates that the string strictly matches the `"MM-DD-YY"` format and represents a real calendar date.
    *   **Logic:** Use Python's `datetime.strptime(date, "%m-%d-%y")`. Wrap in a `try-except` block to catch `ValueError`. Ensure the string layout strictly conforms to 2 digits for month, day, and year separated by hyphens.

---

## 2. Function: `create_request(requester, requester_role, date)`

### Data Flow & Exact Order of Checks:
1. **Normalize & Check Role (Check 1):**
   * Call `_normalize_role(requester_role)`.
   * If the resulting role is not in `{"staff", "manager", "owner"}`, immediately return `"INVALID_ROLE"`.
2. **Validate Date (Check 2):**
   * Call `_validate_date(date)`.
   * If `False`, immediately return `"INVALID_DATE"`.
3. **Construct and Evaluate Request:**
   * Determine initial status: `"APPROVED"` if normalized role is `"owner"`, otherwise `"PENDING"`.
   * Build and return the dictionary:
     ```python
     {
         "requester": requester,
         "requester_role": normalized_role,
         "date": date,
         "status": initial_status
     }
     ```

---

## 3. Function: `act(request, action, user, role, has_manager)`

### Data Flow & Exact Order of Checks:
*Note: Because requirement states "If there's an error, the status must not change," mutations to `request["status"]` must happen strictly at the very end after all checks pass.*

1. **Normalize & Check Action (Check 1):**
   * Normalize action: `action = action.strip().lower()`.
   * If `action` is not `"approve"` or `"reject"`, return `"UNKNOWN_ACTION"`.
2. **Normalize & Check Actor Role (Check 2):**
   * Call `_normalize_role(role)`.
   * If the resulting role is not in `{"staff", "manager", "owner"}`, return `"INVALID_ROLE"`.
3. **Check Permissions (Check 3):**
   * *Self-check (3a):* If `request["requester"] == user`, return `"NOT_ALLOWED"`.
   * *Target Request Type:* Look up `req_role = request["requester_role"]`.
   * *Staff Request Routing (3b & 3c):*
     * If `req_role == "staff"`:
       * If `has_manager` is `True` and actor role must be `"manager"`. If actor role is *not* `"manager"`, return `"NOT_ALLOWED"`.
       * If `has_manager` is `False` and actor role must be `"owner"`. If actor role is *not* `"owner"`, return `"NOT_ALLOWED"`.
   * *Manager Request Routing (3d):*
     * If `req_role == "manager"`:
       * Actor role must be `"owner"`. If actor role is *not* `"owner"`, return `"NOT_ALLOWED"`.
   * *Owner Request / Catch-all (3e):*
     * (Owners generally don't need approval, but if an action is attempted on an owner's request, handle per system matrix; typically owners cannot have their requests acted on, or only by owners. Fallback to `"NOT_ALLOWED"` if unhandled).
4. **Check Request State (Check 4):**
   * If `request["status"] != "PENDING"`, return `"INVALID_STATE"`.
5. **Execute Action (Success Path):**
   * Map action to status: `"approve"` $\rightarrow$ `"APPROVED"`, `"reject"` $\rightarrow$ `"REJECTED"`.
   * Mutate `request["status"]`.
   * Return the updated `request` dictionary.

### Developer

```python
from datetime import datetime

def _normalize_role(role: str) -> str:
    """Strips whitespace and converts role strings to lowercase."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def _validate_date(date: str) -> bool:
    """Validates that the string strictly matches the 'MM-DD-YY' format 
    and represents a real calendar date.
    """
    if not isinstance(date, str):
        return False
    try:
        # Check basic length and hyphen positions to enforce exact strictness
        parts = date.split('-')
        if len(parts) != 3 or len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 2:
            return False
        
        datetime.strptime(date, "%m-%d-%y")
        return True
    except (ValueError, AttributeError):
        return False

def create_request(requester, requester_role, date):
    """Creates a holiday request for staff, manager, or owner."""
    # 1. Normalize & Check Role (Check 1)
    norm_role = _normalize_role(requester_role)
    if norm_role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"
    
    # 2. Validate Date (Check 2)
    if not _validate_date(date):
        return "INVALID_DATE"
    
    # 3. Construct and Evaluate Request
    initial_status = "APPROVED" if norm_role == "owner" else "PENDING"
    
    return {
        "requester": requester,
        "requester_role": norm_role,
        "date": date,
        "status": initial_status
    }

def act(request, action, user, role, has_manager):
    """Approves or rejects a holiday request based on strict permissions and state."""
    # 1. Normalize & Check Action (Check 1)
    if not isinstance(action, str):
        return "UNKNOWN_ACTION"
    norm_action = action.strip().lower()
    if norm_action not in {"approve", "reject"}:
        return "UNKNOWN_ACTION"
    
    # 2. Normalize & Check Actor Role (Check 2)
    norm_role = _normalize_role(role)
    if norm_role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"
    
    # 3. Check Permissions (Check 3)
    # 3a. Self-check
    if request.get("requester") == user:
        return "NOT_ALLOWED"
    
    req_role = request.get("requester_role")
    
    # 3b & 3c. Staff Request Routing
    if req_role == "staff":
        if has_manager:
            if norm_role != "manager":
                return "NOT_ALLOWED"
        else:
            if norm_role != "owner":
                return "NOT_ALLOWED"
                
    # 3d. Manager Request Routing
    elif req_role == "manager":
        if norm_role != "owner":
            return "NOT_ALLOWED"
            
    # 3e. Catch-all / Owner requests or others
    else:
        return "NOT_ALLOWED"
        
    # 4. Check Request State (Check 4)
    if request.get("status") != "PENDING":
        return "INVALID_STATE"
        
    # 5. Execute Action (Success Path)
    new_status = "APPROVED" if norm_action == "approve" else "REJECTED"
    request["status"] = new_status
    
    return request
```

### Tester

```python
from datetime import datetime

def _normalize_role(role: str) -> str:
    """Strips whitespace and converts role strings to lowercase."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def _validate_date(date: str) -> bool:
    """Validates that the string strictly matches the 'MM-DD-YY' format 
    and represents a real calendar date.
    """
    if not isinstance(date, str):
        return False
    try:
        # Check basic length and hyphen positions to enforce exact strictness
        parts = date.split('-')
        if len(parts) != 3 or len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 2:
            return False
        
        datetime.strptime(date, "%m-%d-%y")
        return True
    except (ValueError, AttributeError):
        return False

def create_request(requester, requester_role, date):
    """Creates a holiday request for staff, manager, or owner."""
    # 1. Unknown role -> "INVALID_ROLE"
    norm_role = _normalize_role(requester_role)
    if norm_role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"
    
    # 2. Bad date -> "INVALID_DATE"
    if not _validate_date(date):
        return "INVALID_DATE"
    
    # 3 & 4. Construct and Evaluate Request
    initial_status = "APPROVED" if norm_role == "owner" else "PENDING"
    
    return {
        "requester": requester,
        "requester_role": norm_role,
        "date": date,
        "status": initial_status
    }

def act(request, action, user, role, has_manager):
    """Approves or rejects a holiday request based on strict permissions and state."""
    # 1. Unknown action -> "UNKNOWN_ACTION"
    if not isinstance(action, str):
        return "UNKNOWN_ACTION"
    norm_action = action.strip().lower()
    if norm_action not in {"approve", "reject"}:
        return "UNKNOWN_ACTION"
    
    # 2. Unknown role -> "INVALID_ROLE"
    norm_role = _normalize_role(role)
    if norm_role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"
    
    # 4. The request must be PENDING. Else -> "INVALID_STATE"
    # Check this before permission/self-checks to match expected ordering (or ensure it's evaluated safely)
    if not isinstance(request, dict) or request.get("status") != "PENDING":
        return "INVALID_STATE"

    # 3. Check Permissions
    # 3a. Nobody can approve or reject their own request
    if request.get("requester") == user:
        return "NOT_ALLOWED"
    
    req_role = request.get("requester_role")
    
    # Staff / Manager approval routing & Else -> "NOT_ALLOWED"
    if req_role == "staff":
        if has_manager:
            if norm_role != "manager":
                return "NOT_ALLOWED"
        else:
            if norm_role != "owner":
                return "NOT_ALLOWED"
    elif req_role == "manager":
        if norm_role != "owner":
            return "NOT_ALLOWED"
    else:
        # Owner requests or unknown/invalid req_roles cannot be acted upon
        return "NOT_ALLOWED"
        
    # 5. On success, update request["status"] to "APPROVED" or "REJECTED" and return it.
    new_status = "APPROVED" if norm_action == "approve" else "REJECTED"
    request["status"] = new_status
    
    return request
```
