from datetime import datetime
R = ("staff", "manager", "owner")
def create_request(requester, requester_role, date):
    role = requester_role.strip().lower()
    if role not in R: return "INVALID_ROLE"
    try:
        if len(date) != 8: raise ValueError
        datetime.strptime(date, "%m-%d-%y")
    except ValueError: return "INVALID_DATE"
    return {"requester": requester, "requester_role": role, "date": date,
            "status": "APPROVED" if role == "owner" else "PENDING"}
def act(request, action, user, role, has_manager):
    if action not in ("approve", "reject"): return "UNKNOWN_ACTION"
    role = role.strip().lower()
    if role not in R: return "INVALID_ROLE"
    rr = request["requester_role"].strip().lower()
    ok = (rr == "staff" and (role == "manager" or (role == "owner" and not has_manager))) or \
         (rr == "manager" and role == "owner")
    if not ok or user == request["requester"]: return "NOT_ALLOWED"
    if request["status"] != "PENDING": return "INVALID_STATE"
    request["status"] = "APPROVED" if action == "approve" else "REJECTED"
    return request["status"]
