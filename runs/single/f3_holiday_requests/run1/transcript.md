### Developer

```python
from datetime import datetime

VALID_ROLES = {"staff", "manager", "owner"}
VALID_ACTIONS = {"approve", "reject"}

def _normalize_role(role: str) -> str:
    """Normalizes role names by ignoring case and extra spaces."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def _normalize_action(action: str) -> str:
    """Normalizes action names."""
    if not isinstance(action, str):
        return ""
    return action.strip().lower()

def _is_valid_date(date_str: str) -> bool:
    """Validates date format 'MM-DD-YY'."""
    if not isinstance(date_str, str):
        return False
    try:
        # Check if it strictly matches MM-DD-YY and is a real calendar date
        datetime.strptime(date_str, "%m-%d-%y")
        return True
    except ValueError:
        return False

def create_request(requester: str, requester_role: str, date: str) -> dict | str:
    """
    Creates a holiday request dict or returns an error string.
    """
    role = _normalize_role(requester_role)
    
    # 1. Unknown role
    if role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    # 2. Bad date
    if not _is_valid_date(date):
        return "INVALID_DATE"
    
    # 3. Staff or manager
    if role in {"staff", "manager"}:
        return {
            "requester": requester,
            "requester_role": role,
            "date": date,
            "status": "PENDING"
        }
    
    # 4. Owner (automatic approval)
    if role == "owner":
        return {
            "requester": requester,
            "requester_role": role,
            "date": date,
            "status": "APPROVED"
        }
        
    return "INVALID_ROLE"

def act(request: dict, action: str, user: str, role: str, has_manager: bool) -> str | dict:
    """
    Approves or rejects a holiday request based on permissions and state rules.
    On success, updates and returns the request dict.
    On failure, returns an error string without mutating the request.
    """
    norm_action = _normalize_action(action)
    norm_role = _normalize_role(role)
    
    # 1. Unknown action
    if norm_action not in VALID_ACTIONS:
        return "UNKNOWN_ACTION"
    
    # 2. Unknown role
    if norm_role not in VALID_ROLES:
        return "INVALID_ROLE"
        
    # 3. Permission checks
    requester = request.get("requester")
    req_role = request.get("requester_role")
    
    # Cannot approve/reject own request
    if user == requester:
        return "NOT_ALLOWED"
        
    if req_role == "staff":
        if has_manager:
            # Must be a manager
            if norm_role != "manager":
                return "NOT_ALLOWED"
        else:
            # No manager, must be an owner
            if norm_role != "owner":
                return "NOT_ALLOWED"
    elif req_role == "manager":
        # Can only be approved/rejected by an owner
        if norm_role != "owner":
            return "NOT_ALLOWED"
    else:
        # Owners or unknown roles shouldn't typically have requests to approve, 
        # but if so, not allowed by default rules.
        return "NOT_ALLOWED"

    # 4. The request must be PENDING
    if request.get("status") != "PENDING":
        return "INVALID_STATE"
        
    # 5. On success, update status and return request
    new_status = "APPROVED" if norm_action == "approve" else "REJECTED"
    request["status"] = new_status
    
    return request
```
