### PM

Here is the clear, numbered list of requirements and edge cases for developers building the **Holiday requests** feature for ShiftWise, based strictly on the provided feature spec.

---

### Global Normalization Requirement
1. **Role Normalization:** All role inputs (`requester_role`, `role`, etc.) must be case-insensitive and ignore leading/trailing whitespace (e.g., `"MANAGER"`, `"Manager"`, and `" manager "` must all be treated identically as `"manager"`).

---

### Function 1: `create_request(requester, requester_role, date)`

#### Requirements
2. **Date Format:** The `date` parameter must strictly adhere to the `"MM-DD-YY"` format.
3. **Role Validation (Rule 1):** If the normalized `requester_role` is not recognized (i.e., not staff, manager, or owner), return the string `"INVALID_ROLE"`.
4. **Date Validation (Rule 2):** If the `date` is invalid or does not match the `"MM-DD-YY"` format, return the string `"INVALID_DATE"`.
5. **Staff/Manager Request Creation (Rule 3):** If the role is staff or manager, return a dictionary with the structure:
   `{"requester": requester, "requester_role": normalized_role, "date": date, "status": "PENDING"}`.
6. **Owner Request Creation (Rule 4):** If the role is owner, return a dictionary with the structure:
   `{"requester": requester, "requester_role": normalized_role, "date": date, "status": "APPROVED"}` (owners require no approval).

#### Edge Cases
7. **Invalid Role Strings:** Pass strings like `"admin"`, `""`, or `None` as the role to ensure it returns `"INVALID_ROLE"`.
8. **Malformed Dates:** Pass dates with invalid months, days, years, or wrong separators (e.g., `"YYYY-MM-DD"`, `"13-01-23"`, `"12-32-23"`) to ensure it returns `"INVALID_DATE"`.

---

### Function 2: `act(request, action, user, role, has_manager)`

#### Requirements
9. **Action Validation (Rule 1):** If the `action` is not `"approve"` or `"reject"` (case sensitivity rules apply if applicable, but strictly expect these strings), return the string `"UNKNOWN_ACTION"`.
10. **Actor Role Validation (Rule 2):** If the actor's `role` is an unknown role, return the string `"INVALID_ROLE"`.
11. **Permission Check - Staff Requests (Rule 3):**
    * If `has_manager` is `True`, staff requests can **only** be approved/rejected by a `manager`.
    * If `has_manager` is `False`, staff requests can **only** be approved/rejected by an `owner`.
12. **Permission Check - Manager Requests (Rule 3):** Manager requests can **only** be approved/rejected by an `owner`.
13. **Self-Approval Prohibition (Rule 3):** No user can approve or reject their own request (compare `request["requester"]` with `user`), regardless of their role or permissions.
14. **General Permission Failure (Rule 3):** If any permission condition in Rule 3 fails, return the string `"NOT_ALLOWED"`.
15. **State Validation (Rule 4):** The target request's `status` must be `"PENDING"`. If it is already `"APPROVED"` or `"REJECTED"`, return the string `"INVALID_STATE"`.
16. **State Mutation & Success (Rule 5):** On successful authorization and state validation, update `request["status"]` to either `"APPROVED"` or `"REJECTED"` (matching the input action converted to uppercase/past tense context) and return the updated `request` dictionary.
17. **Atomicity/Immutability on Error (Rule 6):** If any error or failure condition occurs during execution, the original `request["status"]` must remain entirely unchanged.

#### Edge Cases
18. **Unknown Actions:** Pass actions like `"maybe"`, `""`, or `"APPROVE"` (if case-sensitive, though verify exact behavior) to trigger `"UNKNOWN_ACTION"`.
19. **Staff Request with `has_manager=True` acted on by Owner:** Must return `"NOT_ALLOWED"`.
20. **Staff Request with `has_manager=False` acted on by Manager:** Must return `"NOT_ALLOWED"` (since a manager cannot act on staff if there is no manager role utilized/allowed, or per rule: owner approves it instead).
21. **Manager Request acted on by a Manager:** Must return `"NOT_ALLOWED"`.
22. **Staff/Manager acting on their own request:** Must return `"NOT_ALLOWED"`, even if they technically hold the correct administrative role (e.g., a manager trying to approve their own request).
23. **Acting on an already approved/rejected request:** Must return `"INVALID_STATE"`, and the status must not be overwritten.
24. **Role casing in Actor Role:** Pass actor roles with mixed casing and spaces (e.g., `" MANAGER "`) and verify permissions still evaluate correctly.

### Architect

Here is the architectural and logic design for **ShiftWise Feature 3: Holiday requests** (`holiday_requests.py`).

---

### 1. Helper Functions & Data Flow

#### A. Normalization & Validation Helpers
* **`_normalize_role(role)`**:
  * Input: `role` (string or `None`)
  * Logic: If `role` is not a string, return `None`. Otherwise, `role.strip().lower()`.
  * Valid roles set: `{"staff", "manager", "owner"}`.
* **`_validate_date(date_str)`**:
  * Input: `date_str` (string)
  * Logic: Check if the string matches the exact format `"MM-DD-YY"` using Python's `datetime.strptime(date_str, "%m-%d-%y")`. 
  * Returns: `True` if valid, `False` if `ValueError` or `TypeError` is raised. Also ensures strict component boundaries (e.g., rejecting month 13 or day 32).

---

### 2. Core Functions & Exact Order of Checks

#### Function 1: `create_request(requester, requester_role, date)`

**Order of execution and checks:**
1. **Normalize Role:** Call `_normalize_role(requester_role)`. If the resulting role is not in `{"staff", "manager", "owner"}`, immediately return `"INVALID_ROLE"`.
2. **Validate Date:** Call `_validate_date(date)`. If `False`, immediately return `"INVALID_DATE"`.
3. **Branching on Role:**
   * If normalized role is `"staff"` or `"manager"`: 
     Return dict: `{"requester": requester, "requester_role": normalized_role, "date": date, "status": "PENDING"}`
   * If normalized role is `"owner"`: 
     Return dict: `{"requester": requester, "requester_role": normalized_role, "date": date, "status": "APPROVED"}`

---

#### Function 2: `act(request, action, user, role, has_manager)`

**Order of execution and checks (Atomicity Maintained):**
*Note: Because of Rule 6 (mutations must not happen on error), no changes to `request` should be written until all checks pass.*

1. **Normalize Action & Role:** 
   * Normalize input `action` (e.g., lowercased and stripped).
   * Normalize actor `role` using `_normalize_role(role)`.
2. **Check 1: Unknown Action**
   * If normalized `action` is not in `{"approve", "reject"}`, return `"UNKNOWN_ACTION"`.
3. **Check 2: Unknown Actor Role**
   * If normalized actor role is not in `{"staff", "manager", "owner"}`, return `"INVALID_ROLE"`.
4. **Check 3: Self-Approval Prohibition**
   * If `request["requester"] == user`, return `"NOT_ALLOWED"`. *(Checked before permissions to ensure priority)*.
5. **Check 4: Permissions (Rule 3)**
   * Retrieve request's target role: `target_role = request["requester_role"]`.
   * **If `target_role == "staff"`:**
     * If `has_manager` is `True`: Actor role must be `"manager"`.
     * If `has_manager` is `False`: Actor role must be `"owner"`.
     * If condition fails, return `"NOT_ALLOWED"`.
   * **If `target_role == "manager"`:**
     * Actor role must be `"owner"`. If not, return `"NOT_ALLOWED"`.
   * **If `target_role == "owner"`:**
     * (Owners don't need approval, but if someone tries to act on it, fallback or handle per general rules. Usually, owner requests are pre-approved, but standard permission logic applies: only an owner could theoretically act, though it's already approved. For safety, restrict to `"owner"` or evaluate as `"NOT_ALLOWED"` if not applicable).
6. **Check 5: State Validation (Rule 4)**
   * If `request["status"] != "PENDING"`, return `"INVALID_STATE"`.
7. **Check 6: Mutation & Success (Rule 5)**
   * Map action to target status: 
     * `"approve"` $\rightarrow$ `"APPROVED"`
     * `"reject"` $\rightarrow$ `"REJECTED"`
   * Mutate `request["status"] = target_status`.
   * Return the updated `request` dictionary.

### Developer

```python
from datetime import datetime

VALID_ROLES = {"staff", "manager", "owner"}
VALID_ACTIONS = {"approve", "reject"}

def _normalize_role(role):
    """Normalize role by stripping whitespace and converting to lowercase."""
    if not isinstance(role, str):
        return None
    return role.strip().lower()

def _validate_date(date_str):
    """Validate date string is strictly in MM-DD-YY format with valid calendar days/months."""
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%m-%d-%y")
        return True
    except (ValueError, TypeError):
        return False

def create_request(requester, requester_role, date):
    """
    Creates a holiday request for staff, manager, or owner.
    
    Rules:
    1. Unknown role -> "INVALID_ROLE"
    2. Bad date -> "INVALID_DATE"
    3. Staff or manager -> PENDING status
    4. Owner -> APPROVED status
    """
    norm_role = _normalize_role(requester_role)
    if norm_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    if not _validate_date(date):
        return "INVALID_DATE"
    
    if norm_role in {"staff", "manager"}:
        return {
            "requester": requester,
            "requester_role": norm_role,
            "date": date,
            "status": "PENDING"
        }
    else:  # owner
        return {
            "requester": requester,
            "requester_role": norm_role,
            "date": date,
            "status": "APPROVED"
        }

def act(request, action, user, role, has_manager):
    """
    Approves or rejects a pending holiday request based on permissions and business rules.
    Ensures atomicity (no state mutation occurs on error).
    """
    # 1. Normalize action and actor role
    norm_action = action.strip().lower() if isinstance(action, str) else ""
    norm_actor_role = _normalize_role(role)
    
    # Check 1: Unknown Action
    if norm_action not in VALID_ACTIONS:
        return "UNKNOWN_ACTION"
    
    # Check 2: Unknown Actor Role
    if norm_actor_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    # Check 3: Self-Approval Prohibition
    if request.get("requester") == user:
        return "NOT_ALLOWED"
    
    # Check 4: Permissions (Rule 3)
    target_role = request.get("requester_role")
    
    if target_role == "staff":
        if has_manager:
            if norm_actor_role != "manager":
                return "NOT_ALLOWED"
        else:
            if norm_actor_role != "owner":
                return "NOT_ALLOWED"
    elif target_role == "manager":
        if norm_actor_role != "owner":
            return "NOT_ALLOWED"
    else:
        # Owner requests or any unexpected target roles are not allowed to be acted upon
        return "NOT_ALLOWED"
        
    # Check 5: State Validation (Rule 4)
    if request.get("status") != "PENDING":
        return "INVALID_STATE"
    
    # Check 6: Mutation & Success (Rule 5)
    target_status = "APPROVED" if norm_action == "approve" else "REJECTED"
    request["status"] = target_status
    
    return request
```

### Tester

```python
from datetime import datetime
import copy

VALID_ROLES = {"staff", "manager", "owner"}
VALID_ACTIONS = {"approve", "reject"}

def _normalize_role(role):
    """Normalize role by stripping whitespace and converting to lowercase."""
    if not isinstance(role, str):
        return None
    return role.strip().lower()

def _validate_date(date_str):
    """Validate date string is strictly in MM-DD-YY format with valid calendar days/months."""
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%m-%d-%y")
        return True
    except (ValueError, TypeError):
        return False

def create_request(requester, requester_role, date):
    """
    Creates a holiday request for staff, manager, or owner.
    
    Rules:
    1. Unknown role -> "INVALID_ROLE"
    2. Bad date -> "INVALID_DATE"
    3. Staff or manager -> PENDING status
    4. Owner -> APPROVED status
    """
    norm_role = _normalize_role(requester_role)
    if norm_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    if not _validate_date(date):
        return "INVALID_DATE"
    
    if norm_role in {"staff", "manager"}:
        return {
            "requester": requester,
            "requester_role": norm_role,
            "date": date,
            "status": "PENDING"
        }
    else:  # owner
        return {
            "requester": requester,
            "requester_role": norm_role,
            "date": date,
            "status": "APPROVED"
        }

def act(request, action, user, role, has_manager):
    """
    Approves or rejects a pending holiday request based on permissions and business rules.
    Ensures atomicity (no state mutation occurs on error).
    """
    # 1. Normalize action and actor role
    norm_action = action.strip().lower() if isinstance(action, str) else ""
    norm_actor_role = _normalize_role(role)
    
    # Check 1: Unknown Action
    if norm_action not in VALID_ACTIONS:
        return "UNKNOWN_ACTION"
    
    # Check 2: Unknown Actor Role
    if norm_actor_role not in VALID_ROLES:
        return "INVALID_ROLE"
        
    # Check 3: State Validation (Rule 4 check needs to happen before permission/self checks)
    # Spec says:
    # 1. Unknown action -> "UNKNOWN_ACTION"
    # 2. Unknown role -> "INVALID_ROLE"
    # 3. Permission
    # 4. The request must be PENDING. Else -> "INVALID_STATE"
    if not isinstance(request, dict) or request.get("status") != "PENDING":
        return "INVALID_STATE"
    
    # Check 4: Self-Approval Prohibition
    if request.get("requester") == user:
        return "NOT_ALLOWED"
    
    # Check 5: Permissions (Rule 3)
    target_role = request.get("requester_role")
    
    if target_role == "staff":
        if has_manager:
            if norm_actor_role != "manager":
                return "NOT_ALLOWED"
        else:
            if norm_actor_role != "owner":
                return "NOT_ALLOWED"
    elif target_role == "manager":
        if norm_actor_role != "owner":
            return "NOT_ALLOWED"
    else:
        # Owner requests or any unexpected target roles are not allowed to be acted upon
        return "NOT_ALLOWED"
    
    # Check 6: Mutation & Success (Rule 5)
    target_status = "APPROVED" if norm_action == "approve" else "REJECTED"
    request["status"] = target_status
    
    return request
```
