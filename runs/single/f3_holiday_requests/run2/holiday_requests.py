from datetime import datetime

VALID_ROLES = {"staff", "manager", "owner"}
VALID_ACTIONS = {"approve", "reject"}

def _normalize_role(role: str) -> str:
    """Normalize role string by stripping whitespace and converting to lowercase."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def _validate_date(date_str: str) -> bool:
    """Validate MM-DD-YY date format and ensure it's a real calendar date."""
    if not isinstance(date_str, str):
        return False
    try:
        # Ensures exact MM-DD-YY format and valid date values
        datetime.strptime(date_str, "%m-%d-%y")
        return True
    except ValueError:
        return False

def create_request(requester: str, requester_role: str, date: str) -> dict | str:
    """
    Creates a holiday request for a staff member, manager, or owner.
    """
    normalized_role = _normalize_role(requester_role)
    
    # 1. Unknown role -> "INVALID_ROLE"
    if normalized_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    # 2. Bad date -> "INVALID_DATE"
    if not _validate_date(date):
        return "INVALID_DATE"
    
    # 3 & 4. Determine status based on role
    status = "APPROVED" if normalized_role == "owner" else "PENDING"
    
    return {
        "requester": requester,
        "requester_role": normalized_role,
        "date": date,
        "status": status
    }

def act(request: dict, action: str, user: str, role: str, has_manager: bool) -> str:
    """
    Approves or rejects a pending holiday request based on permissions.
    """
    # 1. Unknown action -> "UNKNOWN_ACTION"
    if not isinstance(action, str) or action.strip().lower() not in VALID_ACTIONS:
        return "UNKNOWN_ACTION"
    
    normalized_action = action.strip().lower()
    
    # 2. Unknown role -> "INVALID_ROLE"
    normalized_actor_role = _normalize_role(role)
    if normalized_actor_role not in VALID_ROLES:
        return "INVALID_ROLE"
    
    requester = request.get("requester")
    requester_role = _normalize_role(request.get("requester_role", ""))
    
    # 3. Permission checks
    # - Nobody can approve or reject their own request
    if user == requester:
        return "NOT_ALLOWED"
        
    allowed_to_act = False
    
    if requester_role == "staff":
        if has_manager:
            # A staff request is approved/rejected by a manager if has_manager is True
            if normalized_actor_role == "manager":
                allowed_to_act = True
        else:
            # If has_manager is False, the owner approves it instead
            if normalized_actor_role == "owner":
                allowed_to_act = True
    elif requester_role == "manager":
        # A manager request can only be approved/rejected by an owner
        if normalized_actor_role == "owner":
            allowed_to_act = True
            
    if not allowed_to_act:
        return "NOT_ALLOWED"
        
    # 4. The request must be PENDING. Else -> "INVALID_STATE"
    if request.get("status") != "PENDING":
        return "INVALID_STATE"
        
    # 5. On success, update request["status"] to "APPROVED" or "REJECTED" and return it.
    new_status = "APPROVED" if normalized_action == "approve" else "REJECTED"
    request["status"] = new_status
    
    return new_status
