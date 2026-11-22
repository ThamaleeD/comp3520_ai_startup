"""Hidden tests for Feature 3: Holiday requests.

Expected results were set by the team from specs/specs.md.
The AI under test never sees this file.
"""
import pytest
from holiday_requests import create_request, act


def pending(requester, role):
    return {"requester": requester, "requester_role": role,
            "date": "12-24-26", "status": "PENDING"}


# ---------- create_request ----------

def test_create_staff_pending():
    r = create_request("amy", "staff", "12-24-26")
    assert r["status"] == "PENDING"
    assert r["requester"] == "amy"
    assert r["date"] == "12-24-26"


def test_create_manager_pending():
    assert create_request("lee", "manager", "12-24-26")["status"] == "PENDING"


def test_create_owner_auto_approved():
    assert create_request("boss", "owner", "12-24-26")["status"] == "APPROVED"


def test_create_role_caps():
    assert create_request("lee", "MANAGER", "12-24-26")["status"] == "PENDING"


def test_create_invalid_role():
    assert create_request("amy", "intern", "12-24-26") == "INVALID_ROLE"


def test_create_invalid_date():
    assert create_request("amy", "staff", "2026-12-24") == "INVALID_DATE"


def test_create_order_role_before_date():
    assert create_request("amy", "intern", "2026-12-24") == "INVALID_ROLE"


# ---------- act ----------
# (test id, request role, requester, action, user, user role, has_manager, expected)
ACT_CASES = [
    ("mgr_approves_staff",        "staff",   "amy", "approve", "lee",  "manager", True,  "APPROVED"),
    ("mgr_rejects_staff",         "staff",   "amy", "reject",  "lee",  "manager", True,  "REJECTED"),
    ("staff_approves_staff",      "staff",   "amy", "approve", "raj",  "staff",   True,  "NOT_ALLOWED"),
    ("owner_staff_has_mgr",       "staff",   "amy", "approve", "boss", "owner",   True,  "NOT_ALLOWED"),
    ("owner_staff_no_mgr",        "staff",   "amy", "approve", "boss", "owner",   False, "APPROVED"),
    ("owner_rejects_staff_no_mgr","staff",   "amy", "reject",  "boss", "owner",   False, "REJECTED"),
    ("owner_approves_mgr",        "manager", "lee", "approve", "boss", "owner",   True,  "APPROVED"),
    ("owner_rejects_mgr",         "manager", "lee", "reject",  "boss", "owner",   True,  "REJECTED"),
    ("other_mgr_approves_mgr",    "manager", "lee", "approve", "kim",  "manager", True,  "NOT_ALLOWED"),
    ("mgr_approves_own",          "manager", "lee", "approve", "lee",  "manager", True,  "NOT_ALLOWED"),
    ("staff_approves_mgr",        "manager", "lee", "approve", "amy",  "staff",   True,  "NOT_ALLOWED"),
    ("role_caps_manager",         "staff",   "amy", "approve", "lee",  "MANAGER", True,  "APPROVED"),
    ("unknown_action",            "staff",   "amy", "cancel",  "lee",  "manager", True,  "UNKNOWN_ACTION"),
    ("unknown_role",              "staff",   "amy", "approve", "lee",  "boss",    True,  "INVALID_ROLE"),
    ("order_action_before_role",  "staff",   "amy", "cancel",  "lee",  "boss",    True,  "UNKNOWN_ACTION"),
]


@pytest.mark.parametrize("req_role,requester,action,user,role,has_manager,expected",
                         [c[1:] for c in ACT_CASES], ids=[c[0] for c in ACT_CASES])
def test_act(req_role, requester, action, user, role, has_manager, expected):
    req = pending(requester, req_role)
    result = act(req, action, user, role, has_manager)
    assert result == expected
    if expected in ("APPROVED", "REJECTED"):
        assert req["status"] == expected
    else:
        assert req["status"] == "PENDING"   # errors must not change status


def test_act_already_approved():
    req = pending("amy", "staff")
    req["status"] = "APPROVED"
    assert act(req, "reject", "lee", "manager", True) == "INVALID_STATE"
    assert req["status"] == "APPROVED"


def test_act_already_rejected():
    req = pending("amy", "staff")
    req["status"] = "REJECTED"
    assert act(req, "approve", "lee", "manager", True) == "INVALID_STATE"
    assert req["status"] == "REJECTED"


def test_act_permission_before_state():
    req = pending("amy", "staff")
    req["status"] = "APPROVED"
    assert act(req, "reject", "raj", "staff", True) == "NOT_ALLOWED"


def test_full_flow_create_then_approve():
    req = create_request("amy", "staff", "12-24-26")
    assert act(req, "approve", "lee", "manager", True) == "APPROVED"
    assert act(req, "approve", "lee", "manager", True) == "INVALID_STATE"
