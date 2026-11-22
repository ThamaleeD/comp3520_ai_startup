from datetime import datetime


def normalize_role(role):
    return role.strip().lower()


def valid_date(date):
    try:
        datetime.strptime(date, "%m-%d-%y")
        return True
    except (ValueError, TypeError):
        return False


def create_request(requester, requester_role, date):
    role = normalize_role(requester_role)

    if role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"

    if not valid_date(date):
        return "INVALID_DATE"

    status = "APPROVED" if role == "owner" else "PENDING"

    return {
        "requester": requester,
        "requester_role": role,
        "date": date,
        "status": status,
    }


def act(request, action, user, role, has_manager):
    if action not in {"approve", "reject"}:
        return "UNKNOWN_ACTION"

    role = normalize_role(role)

    if role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"

    requester_role = normalize_role(request["requester_role"])

    if user == request["requester"]:
        return "NOT_ALLOWED"

    allowed = False

    if requester_role == "staff":
        if has_manager:
            allowed = role == "manager"
        else:
            allowed = role == "owner"
    elif requester_role == "manager":
        allowed = role == "owner"

    if not allowed:
        return "NOT_ALLOWED"

    if request["status"] != "PENDING":
        return "INVALID_STATE"

    request["status"] = "APPROVED" if action == "approve" else "REJECTED"

    return request["status"]
