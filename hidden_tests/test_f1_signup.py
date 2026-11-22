"""Hidden tests for Feature 1: Sign-up.

Expected results were set by the team from specs/specs.md.
The AI under test never sees this file.
"""
import pytest
from signup import signup

EXISTING = {
    "staff": ["staff_amy@example.com", "staff_raj@example.com"],
    "manager": ["manager_lee@example.com"],
    "owner": ["owner@example.com"],
}

GOOD_PW = "Secret123!"

# (test id, email, password, role, expected)
CASES = [
    # --- valid sign-ups ---
    ("ok_staff",            "staff_mia@example.com",        GOOD_PW,       "staff",   "OK"),
    ("ok_manager",          "manager_kim@example.com",      GOOD_PW,       "manager", "OK"),
    ("ok_owner_no_prefix",  "boss@example.com",             GOOD_PW,       "owner",   "OK"),
    ("ok_surname",          "staff_amy.chen@example.com",   GOOD_PW,       "staff",   "OK"),
    ("ok_emp_id",           "staff_amy1042@example.com",    GOOD_PW,       "staff",   "OK"),
    ("ok_spaces_trimmed",   "  staff_mia@example.com  ",    GOOD_PW,       "staff",   "OK"),
    ("ok_role_caps",        "staff_mia@example.com",        GOOD_PW,       "STAFF",   "OK"),
    ("ok_email_caps",       "STAFF_MIA@EXAMPLE.COM",        GOOD_PW,       "staff",   "OK"),
    # --- email format ---
    ("email_no_at",         "staff_miaexample.com",         GOOD_PW,       "staff",   "INVALID_EMAIL"),
    ("email_two_at",        "staff_mia@@example.com",       GOOD_PW,       "staff",   "INVALID_EMAIL"),
    ("email_no_dot",        "staff_mia@examplecom",         GOOD_PW,       "staff",   "INVALID_EMAIL"),
    ("email_dot_first",     "staff_mia@.com",               GOOD_PW,       "staff",   "INVALID_EMAIL"),
    ("email_dot_last",      "staff_mia@example.",           GOOD_PW,       "staff",   "INVALID_EMAIL"),
    ("email_nothing_before","@example.com",                 GOOD_PW,       "owner",   "INVALID_EMAIL"),
    # --- role ---
    ("role_unknown",        "staff_mia@example.com",        GOOD_PW,       "intern",  "INVALID_ROLE"),
    # --- prefix ---
    ("prefix_missing",      "mia@example.com",              GOOD_PW,       "staff",   "WRONG_PREFIX"),
    ("prefix_wrong_role",   "staff_lee@example.com",        GOOD_PW,       "manager", "WRONG_PREFIX"),
    ("prefix_mgr_as_staff", "manager_kim@example.com",      GOOD_PW,       "staff",   "WRONG_PREFIX"),
    # --- name format ---
    ("name_underscore_num", "staff_mia_2@example.com",      GOOD_PW,       "staff",   "INVALID_NAME"),
    ("name_empty",          "staff_@example.com",           GOOD_PW,       "staff",   "INVALID_NAME"),
    ("name_surname_and_id", "staff_amy.chen1042@example.com", GOOD_PW,     "staff",   "INVALID_NAME"),
    # --- password ---
    ("pw_too_short",        "staff_mia@example.com",        "Se1!",        "staff",   "WEAK_PASSWORD"),
    ("pw_no_number",        "staff_mia@example.com",        "Secret!!!",   "staff",   "WEAK_PASSWORD"),
    ("pw_no_capital",       "staff_mia@example.com",        "secret123!",  "staff",   "WEAK_PASSWORD"),
    ("pw_no_special",       "staff_mia@example.com",        "Secret123",   "staff",   "WEAK_PASSWORD"),
    ("pw_space_not_special","staff_mia@example.com",        "Secret 123",  "staff",   "WEAK_PASSWORD"),
    # --- already taken ---
    ("taken_same",          "staff_amy@example.com",        GOOD_PW,       "staff",   "EMAIL_TAKEN"),
    ("taken_caps",          "STAFF_AMY@example.com",        GOOD_PW,       "staff",   "EMAIL_TAKEN"),
    ("taken_manager_list",  "manager_lee@example.com",      GOOD_PW,       "manager", "EMAIL_TAKEN"),
    ("taken_owner_list",    "owner@example.com",            GOOD_PW,       "owner",   "EMAIL_TAKEN"),
    # --- check order (first error wins) ---
    ("order_email_before_pw",   "staff_miaexample.com",     "weak",        "staff",   "INVALID_EMAIL"),
    ("order_role_before_prefix","mia@example.com",          GOOD_PW,       "intern",  "INVALID_ROLE"),
    ("order_prefix_before_pw",  "mia@example.com",          "weak",        "staff",   "WRONG_PREFIX"),
    ("order_pw_before_taken",   "staff_amy@example.com",    "weak",        "staff",   "WEAK_PASSWORD"),
]


@pytest.mark.parametrize("email,password,role,expected",
                         [c[1:] for c in CASES], ids=[c[0] for c in CASES])
def test_signup(email, password, role, expected):
    assert signup(email, password, role, EXISTING) == expected
