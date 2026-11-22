### PM

Here are the requirements and edge cases for the developers, broken down by function according to the feature specification.

---

### Global / Pre-processing Requirements (Applies to all functions)
1. **Role Normalization:** All role inputs (e.g., `requester_role`, `role`) must be case-insensitive and ignore leading/trailing whitespace (e.g., `"MANAGER"`, `"Manager"`, and `" manager "` all evaluate to `"manager"`). Valid roles are restricted to `"staff"`, `"manager"`, and `"owner"`.

---

### Function 1: `create_request(requester, requester_role, date)`

#### Requirements:
2. **Date Format:** The `date` parameter must strictly follow the `"MM-DD-YY"` format.
3. **Role Validation (Rule 1):** If the normalized `requester_role` is not one of the valid roles (`staff`, `manager`, `owner`), return the exact string `"INVALID_ROLE"`.
4. **Date Validation (Rule 2):** If the `date` is invalid or does not match the `"MM-DD-YY"` format, return the exact string `"INVALID_DATE"`.
5. **Staff/Manager Request Creation (Rule 3):** If the requester is a `"staff"` or `"manager"`, return a dictionary containing:
   - `"requester"`: the provided requester identifier
   - `"requester_role"`: the normalized role
   - `"date"`: the provided date
   - `"status"`: `"PENDING"`
6. **Owner Request Creation (Rule 4):** If the requester is an `"owner"`, return the same dictionary structure as above, but with `"status": "APPROVED"` (since owners do not require approval).

#### Edge Cases:
7. `requester_role` contains mixed casing or padded spaces (e.g., `"  sTaFf  "`).
8. `date` strings with incorrect separators (e.g., `"MM/DD/YY"`, `"MM-DD-YYYY"`).
9. Empty string passed as `requester_role` or `date`.

---

### Function 2: `act(request, action, user, role, has_manager)`

#### Requirements:
10. **Action Validation (Rule 1):** If the `action` is not recognized (i.e., not `"approve"` or `"reject"`, case-sensitive or insensitive depending on spec implementation, but safely checking exact values), return the exact string `"UNKNOWN_ACTION"`.
11. **Role Validation (Rule 2):** If the actor's `role` (after normalization) is not a valid role (`staff`, `manager`, `owner`), return the exact string `"INVALID_ROLE"`.
12. **Permission Validation (Rule 3 - Staff Requests):** 
    - If `request["requester_role"] == "staff"` and `has_manager == True`, only a normalized `manager` can act on it.
    - If `request["requester_role"] == "staff"` and `has_manager == False`, only an `owner` can act on it.
13. **Permission Validation (Rule 3 - Manager Requests):**
    - If `request["requester_role"] == "manager"`, only an `owner` can act on it. (Managers cannot approve manager requests, even if `has_manager` is true).
14. **Permission Validation (Rule 3 - Self-Approval Block):**
    - No user (`user`) is permitted to approve or reject their own holiday request, regardless of their role. Return `"NOT_ALLOWED"` if `request["requester"] == user`.
15. **General Permission Failure:** If any actor does not meet the strict permission criteria above, return the exact string `"NOT_ALLOWED"`.
16. **State Validation (Rule 4):** The target `request["status"]` must be strictly `"PENDING"`. If the request is already `"APPROVED"` or `"REJECTED"`, return the exact string `"INVALID_STATE"`.
17. **State Mutation & Success Return (Rule 5):** On successful authorization and state check:
    - Update `request["status"]` to `"APPROVED"` if `action == "approve"`.
    - Update `request["status"]` to `"REJECTED"` if `action == "reject"`.
    - Return the modified `request` dictionary.
18. **Atomicity / Immutability on Error (Rule 6):** If any validation check fails at any step during execution, the original `request["status"]` must remain entirely unchanged.

#### Edge Cases:
19. A manager tries to approve a staff request when `has_manager = False` (should fail with `"NOT_ALLOWED"` because only the owner can approve it in this scenario).
20. An owner tries to approve a staff request when `has_manager = True` (should fail with `"NOT_ALLOWED"` because the manager must handle it).
21. A manager tries to approve another manager's request (should fail with `"NOT_ALLOWED"` as only owners can approve managers).
22. A user tries to approve their own request using a variation of their name/identifier, or matching identifier strings.
23. Attempting to act on a request whose status is already `"APPROVED"` or `"REJECTED"` (must return `"INVALID_STATE"`, even if the user attempting it has the correct permissions).

### Architect

As the software architect, here is the design for the `holiday_requests.py` module, detailing the helper functions, data flow, and exact validation sequence required to build the feature robustly.

---

### Helper Functions & Utilities

1. **`normalize_role(role: str) -> str`**
   - **Purpose:** Handles case-insensitivity and whitespace stripping for any role string.
   - **Logic:** Converts to lowercase and strips leading/trailing whitespace. If the resulting string is not in `{"staff", "manager", "owner"}`, returns `None` or raises an invalid flag.

2. **`validate_date(date_str: str) -> bool`**
   - **Purpose:** Strict format checking for `"MM-DD-YY"`.
   - **Logic:** 
     - Check length and presence of exactly two hyphens separating three numeric chunks.
     - Ensure each chunk consists of valid digits representing month (01-12), day (01-31), and a 2-digit year.
     - (Optional safety check: can use `datetime.strptime(date_str, "%m-%d-%y")` to catch calendar anomalies like Feb 30).

---

### Function 1: `create_request(requester, requester_role, date)`

**Exact Order of Execution & Data Flow:**

1. **Normalize Role:**
   - Pass `requester_role` to `normalize_role()`. 
   - *Check 1:* If normalization yields an invalid role, immediately return `"INVALID_ROLE"`.

2. **Validate Date:**
   - Pass `date` to `validate_date()`.
   - *Check 2:* If `False`, immediately return `"INVALID_DATE"`.

3. **Determine Initial Status & Construct Dictionary:**
   - *Check 3 (Owner vs Staff/Manager):*
     - If the normalized role is `"owner"`, set `"status": "APPROVED"`.
     - Otherwise (role is `"staff"` or `"manager"`), set `"status": "PENDING"`.
   - Return the constructed dictionary:
     ```python
     {
         "requester": requester,
         "requester_role": normalized_role,
         "date": date,
         "status": status
     }
     ```

---

### Function 2: `act(request, action, user, role, has_manager)`

**Exact Order of Execution & Data Flow (Strictly adhering to precedence and immutability):**

1. **Action Validation (Rule 1):**
   - *Check 1:* If `action` is not strictly equal to `"approve"` or `"reject"`, return `"UNKNOWN_ACTION"`.

2. **Role Validation (Rule 2):**
   - Normalize the actor's input `role` using `normalize_role()`.
   - *Check 2:* If the normalized role is invalid (`None`), return `"INVALID_ROLE"`.

3. **Self-Approval Check (Rule 3 subset):**
   - *Check 3:* If `request["requester"] == user`, return `"NOT_ALLOWED"`. *(Must happen before structural permission checks to prevent self-approval regardless of role)*.

4. **Permission Validation (Rule 3):**
   - Get `target_role = request["requester_role"]`.
   - *Check 4 (Staff requests):* 
     - If `target_role == "staff"`:
       - If `has_manager == True` and actor role is **not** `"manager"`, return `"NOT_ALLOWED"`.
       - If `has_manager == False` and actor role is **not** `"owner"`, return `"NOT_ALLOWED"`.
   - *Check 5 (Manager requests):*
     - If `target_role == "manager"`:
       - If actor role is **not** `"owner"`, return `"NOT_ALLOWED"`.
   - *Check 6 (Owner requests / Fallback safety):*
     - If `target_role == "owner"` (though owners auto-approve, if someone tries to act on it), no role can act on it → return `"NOT_ALLOWED"`.

5. **State Validation (Rule 4):**
   - *Check 7:* Inspect `request["status"]`. If it is anything other than `"PENDING"` (e.g., `"APPROVED"` or `"REJECTED"`), return `"INVALID_STATE"`. *(Note: This check occurs after permissions so unauthorized users get `"NOT_ALLOWED"` rather than state errors, aligning with standard security practices).*

6. **State Mutation & Success Return (Rule 5 & 6):**
   - *Atomicity:* Because all validation checks evaluate *before* any mutation occurs, the request dictionary remains completely immutable if any error code is returned.
   - If all checks pass:
     - If `action == "approve"`, set `request["status"] = "APPROVED"`.
     - If `action == "reject"`, set `request["status"] = "REJECTED"`.
   - Return the updated `request` dictionary.

### Developer

```python
from datetime import datetime

VALID_ROLES = {"staff", "manager", "owner"}

def normalize_role(role: str) -> str:
    """Normalizes role by converting to lowercase and stripping whitespace."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def validate_date(date_str: str) -> bool:
    """Validates date strictly follows 'MM-DD-YY' format and is a valid calendar date."""
    if not isinstance(date_str, str):
        return False
    try:
        # datetime.strptime will check format and calendar validity (e.g., month 1-12, day 1-31)
        # %m-%d-%y strictly matches 2-digit month, 2-digit day, 2-digit year separated by hyphens.
        # Note: %y parses 2-digit years. We also want to ensure it strictly had 2 hyphens.
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        if len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 2:
            return False
        datetime.strptime(date_str, "%m-%d-%y")
        return True
    except ValueError:
        return False

def create_request(requester, requester_role, date):
    """
    Creates a holiday request dictionary or returns an error string if invalid.
    """
    norm_role = normalize_role(requester_role)
    if norm_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    if not validate_date(date):
        return "INVALID_DATE"
    
    status = "APPROVED" if norm_role == "owner" else "PENDING"
    
    return {
        "requester": requester,
        "requester_role": norm_role,
        "date": date,
        "status": status
    }

def act(request, action, user, role, has_manager):
    """
    Approves or rejects a holiday request based on permissions and state rules.
    """
    # 1. Action Validation
    if action not in ("approve", "reject"):
        return "UNKNOWN_ACTION"
    
    # 2. Role Validation
    norm_role = normalize_role(role)
    if norm_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    # 3. Self-Approval Check
    if request.get("requester") == user:
        return "NOT_ALLOWED"
    
    # 4. Permission Validation
    target_role = request.get("requester_role")
    
    if target_role == "staff":
        if has_manager:
            if norm_role != "manager":
                return "NOT_ALLOWED"
        else:
            if norm_role != "owner":
                return "NOT_ALLOWED"
    elif target_role == "manager":
        if norm_role != "owner":
            return "NOT_ALLOWED"
    else:
        # Owner requests or unknown target roles cannot be acted upon
        return "NOT_ALLOWED"
    
    # 5. State Validation
    if request.get("status") != "PENDING":
        return "INVALID_STATE"
    
    # 6. State Mutation & Success Return
    if action == "approve":
        request["status"] = "APPROVED"
    elif action == "reject":
        request["status"] = "REJECTED"
        
    return request
```

### Tester

```python
from datetime import datetime

VALID_ROLES = {"staff", "manager", "owner"}

def normalize_role(role: str) -> str:
    """Normalizes role by converting to lowercase and stripping whitespace."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def validate_date(date_str: str) -> bool:
    """Validates date strictly follows 'MM-DD-YY' format and is a valid calendar date."""
    if not isinstance(date_str, str):
        return False
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        if len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 2:
            return False
        datetime.strptime(date_str, "%m-%d-%y")
        return True
    except ValueError:
        return False

def create_request(requester, requester_role, date):
    """
    Creates a holiday request dictionary or returns an error string if invalid.
    """
    norm_role = normalize_role(requester_role)
    if norm_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    if not validate_date(date):
        return "INVALID_DATE"
    
    status = "APPROVED" if norm_role == "owner" else "PENDING"
    
    return {
        "requester": requester,
        "requester_role": norm_role,
        "date": date,
        "status": status
    }

def act(request, action, user, role, has_manager):
    """
    Approves or rejects a holiday request based on permissions and state rules.
    """
    # 1. Action Validation (Check before role, as per standard evaluation ordering or to catch unknown actions first)
    if action not in ("approve", "reject"):
        return "UNKNOWN_ACTION"
    
    # 2. Role Validation
    norm_role = normalize_role(role)
    if norm_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    # 3. Permission & Self-Approval Validation
    # Rules state:
    # - Unknown action -> "UNKNOWN_ACTION" (Checked)
    # - Unknown role -> "INVALID_ROLE" (Checked)
    # - Permission:
    #   - A staff request is approved/rejected by a manager. If has_manager is False, the owner approves it instead.
    #   - A manager request can only be approved/rejected by an owner
    #   - Nobody can approve or reject their own request
    #   - Else -> "NOT_ALLOWED"
    # - The request must be PENDING. Else -> "INVALID_STATE"
    # Note: Checking request state *before* permission or vice versa? 
    # Let's verify standard error precedence. If an unauthorized user tries to act on an already APPROVED request, 
    # checking permissions first usually takes precedence (i.e., unauthorized users shouldn't know or affect state validation).
    # But let's check self-approval and permissions:
    if request.get("requester") == user:
        return "NOT_ALLOWED"
    
    target_role = request.get("requester_role")
    
    if target_role == "staff":
        if has_manager:
            if norm_role != "manager":
                return "NOT_ALLOWED"
        else:
            if norm_role != "owner":
                return "NOT_ALLOWED"
    elif target_role == "manager":
        if norm_role != "owner":
            return "NOT_ALLOWED"
    else:
        # Owner requests or unknown target roles cannot be acted upon
        return "NOT_ALLOWED"
    
    # 4. State Validation (Must be PENDING)
    if request.get("status") != "PENDING":
        return "INVALID_STATE"
    
    # 5. State Mutation & Success Return
    if action == "approve":
        request["status"] = "APPROVED"
    elif action == "reject":
        request["status"] = "REJECTED"
        
    return request
```
