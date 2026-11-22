import re
def signup(email, password, role, existing_emails):
    email = email.strip().lower()
    if email.count("@") != 1: return "INVALID_EMAIL"
    local, domain = email.split("@")
    if not local or "." not in domain or domain[0] == "." or domain[-1] == ".": return "INVALID_EMAIL"
    role = role.strip().lower()
    if role not in ("staff", "manager", "owner"): return "INVALID_ROLE"
    if role != "owner":
        if not local.startswith(role + "_"): return "WRONG_PREFIX"
        name = local[len(role) + 1:]
        if not re.fullmatch(r"[a-z]+|[a-z]+\.[a-z]+|[a-z]+[0-9]+", name): return "INVALID_NAME"
    if (len(password) < 8 or not any(c.isdigit() for c in password) or not any(c.isupper() for c in password)
            or not any(not c.isalnum() and not c.isspace() for c in password)): return "WEAK_PASSWORD"
    if any(email == e.strip().lower() for lst in existing_emails.values() for e in lst): return "EMAIL_TAKEN"
    return "OK"
