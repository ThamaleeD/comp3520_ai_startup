import re


def signup(email, password, role, existing_emails):
    # Rule 1: Normalize email
    email = email.strip().lower()

    # Rule 2: Validate email structure
    if email.count("@") != 1:
        return "INVALID_EMAIL"

    local_part, domain = email.split("@")

    if (
        not local_part
        or "." not in domain
        or domain.startswith(".")
        or domain.endswith(".")
    ):
        return "INVALID_EMAIL"

    # Rule 3: Validate role
    role = role.strip().lower()

    if role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"

    # Rules 4 and 5: Validate staff/manager naming format
    if role in {"staff", "manager"}:
        prefix = f"{role}_"

        if not local_part.startswith(prefix):
            return "WRONG_PREFIX"

        name_part = local_part[len(prefix):]

        valid_name = r"[a-z]+(?:\.[a-z]+|[0-9]+)?"

        if not re.fullmatch(valid_name, name_part):
            return "INVALID_NAME"

    # Rule 6: Validate password
    has_number = any(char.isdigit() for char in password)
    has_uppercase = any(char.isupper() for char in password)
    has_special = any(
        not char.isalnum() and not char.isspace()
        for char in password
    )

    if (
        len(password) < 8
        or not has_number
        or not has_uppercase
        or not has_special
    ):
        return "WEAK_PASSWORD"

    # Rule 7: Check duplicate emails across all roles
    for registered_emails in existing_emails.values():
        for registered_email in registered_emails:
            if email == registered_email.strip().lower():
                return "EMAIL_TAKEN"

    # Rule 8: All checks passed
    return "OK"
