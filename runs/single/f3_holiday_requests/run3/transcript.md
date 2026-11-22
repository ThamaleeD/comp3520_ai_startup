### Developer

```python
from datetime import datetime

VALID_ROLES = {"staff", "manager", "owner"}
VALID_ACTIONS = {"approve", "reject"}

def _normalize_role(role: str) -> str:
    """Normalizes a role string by lowercasing and stripping whitespace."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def _validate_date(date_str: str) -> bool:
    """Validates if the date string is strictly in MM-DD-YY format and represents a real calendar date."""
    if not isinstance(date_str, str):
        return False
    try:
        # datetime.strptime will catch invalid dates like month 13, day 32, or non-dates
        datetime.strptime(date_str, "%m-%d-%y")
        return True
    except ValueError:
        return False

def create_request(requester: str, requester_role: str, date: str) -> dict | str:
    """
    Creates a holiday request dict or returns an error string.
    """
    normalized_role = _normalize_role(requester_role)
    
    # Rule 1: Unknown role
    if normalized_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    # Rule 2: Bad date
    if not _validate_date(date):
        return "INVALID_DATE"
    
    # Rule 3 & 4: Status determination
    status = "APPROVED" if normalized_role == "owner" else "PENDING"
    
    return {
        "requester": requester,
        "requester_role": normalized_role,
        "date": date,
        "status": status
    }

def act(request: dict, action: str, user: str, role: str, has_manager: bool) -> str | dict:
    """
    Approves or rejects a pending holiday request based on permissions and business rules.
    """
    # Normalize action and role
    normalized_action = action.strip().lower() if isinstance(action, str) else ""
    normalized_role = _normalize_role(role)
    
    # Rule 1: Unknown action
    if normalized_action not in VALID_ACTIONS:
        return "UNKNOWN_ACTION"
    
    # Rule 2: Unknown role
    if normalized_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    # Rule 3: Permission checks
    requester = request.get("requester")
    requester_role = _normalize_role(request.get("requester_role", ""))
    
    # Check if user is trying to approve/reject their own request
    is_own_request = (user == requester)
    
    allowed = False
    if is_own_request:
        allowed = False
    elif requester_role == "staff":
        if has_manager:
            # Managed by a manager
            if normalized_role == "manager":
                allowed = True
        else:
            # Managed by an owner (no manager exists)
            if normalized_role == "owner":
                allowed = True
    elif requester_role == "manager":
        # Managed only by an owner
        if normalized_role == "owner":
            allowed = True
            
    if not allowed:
        return "NOT_ALLOWED"
        
    # Rule 4: The request must be PENDING
    if request.get("status") != "PENDING":
        return "INVALID_STATE"
        
    # Rule 5 & 6: On success, update status and return the request dict
    new_status = "APPROVED" if normalized_action == "approve" else "REJECTED"
    request["status"] = new_status
    
    return request
```
