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
