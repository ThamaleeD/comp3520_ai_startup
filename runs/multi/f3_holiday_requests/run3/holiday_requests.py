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
