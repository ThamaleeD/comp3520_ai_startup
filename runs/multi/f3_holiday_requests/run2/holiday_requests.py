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
