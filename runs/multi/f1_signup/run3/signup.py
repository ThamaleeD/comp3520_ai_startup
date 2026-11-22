"""
ShiftWise: Feature 1 - Sign-up
COMP 3520 Assignment 4. Team: Thamalee Dasanayake, Akshana Leninrajah
"""

def _sanitize_inputs(email: str, role: str) -> tuple[str, str]:
    """Strips whitespace and lowercases email; lowercases and strips/collapses role."""
    clean_email = email.strip().lower() if isinstance(email, str) else ""
    clean_role = role.strip().lower() if isinstance(role, str) else ""
    return clean_email, clean_role


def _validate_email_structure(email: str) -> bool:
    """Validates @ count, local part presence, and dot placement in domain part."""
    if not isinstance(email, str):
        return False
        
    if email.count("@") != 1:
        return False
    
    local_part, domain_part = email.split("@", 1)
    
    if not local_part:
        return False
        
    if "." not in domain_part:
        return False
        
    if domain_part.startswith(".") or domain_part.endswith("."):
        return False
        
    return True


def _validate_role(role: str) -> bool:
    """Checks if role is in {"staff", "manager", "owner"}."""
    return role in {"staff", "manager", "owner"}


def _validate_prefix(local_part: str, role: str) -> bool:
    """Validates role-prefix matching for staff and manager."""
    if role == "staff":
        return local_part.startswith("staff_")
    elif role == "manager":
        return local_part.startswith("manager_")
    elif role == "owner":
        return True
    return False


def _validate_name_pattern(local_part: str, role: str) -> bool:
    """Validates the three approved name formats for staff and manager."""
    if role == "owner":
        return True
        
    prefix = f"{role}_"
    if not local_part.startswith(prefix):
        return False
        
    remainder = local_part[len(prefix):]
    if not remainder:
        return False
        
    # Format 1: <name> (Letters only)
    if remainder.isalpha():
        return True
        
    # Format 2: <name>.<surname> (Letters separated by a single dot)
    if "." in remainder:
        parts = remainder.split(".")
        if len(parts) == 2 and parts[0].isalpha() and parts[1].isalpha():
            return True
        return False
        
    # Format 3: <name><empID> (Letters immediately followed by digits only)
    # Find the boundary where letters end and digits begin
    first_digit_idx = -1
    for i, char in enumerate(remainder):
        if char.isdigit():
            first_digit_idx = i
            break
            
    if first_digit_idx != -1:
        # Format rule: <name> must be letters only, <empID> must be digits only
        # This means the boundary must be exact (no trailing non-digits after digits)
        name_part = remainder[:first_digit_idx]
        id_part = remainder[first_digit_idx:]
        if name_part.isalpha() and id_part.isdigit():
            return True
            
    return False


def _validate_password(password: str) -> bool:
    """Checks length >= 8, at least one digit, uppercase letter, and special character."""
    if not isinstance(password, str) or len(password) < 8:
        return False
        
    has_digit = any(char.isdigit() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_special = any(not char.isalnum() and not char.isspace() for char in password)
    
    return has_digit and has_upper and has_special


def _check_duplicate_email(email: str, existing_emails: dict) -> bool:
    """Checks if email already exists in any of the role lists."""
    if not isinstance(existing_emails, dict):
        return False
        
    for role_key, emails in existing_emails.items():
        if isinstance(emails, list):
            for existing in emails:
                if isinstance(existing, str) and existing.strip().lower() == email:
                    return True
    return False


def signup(email, password, role, existing_emails) -> str:
    """
    Validates and processes a user sign-up according to ShiftWise feature specs.
    
    Order of checks according to spec:
    1. Ignore spaces at start/end of email, ignore capital letters everywhere.
    2. Email must have exactly one @, something before it, and a . in the part after it. Else "INVALID_EMAIL".
    3. Role must be staff, manager, or owner. Else "INVALID_ROLE".
    4. For staff and manager, email must start with staff_ or manager_ to match role. Else "WRONG_PREFIX".
    5. For staff and manager, rest of part before @ must match one of the 3 formats. Else "INVALID_NAME".
    6. Password must be 8+ chars, with at least 1 number, 1 capital, 1 special char. Else "WEAK_PASSWORD".
    7. If email is already in any of the three lists, return "EMAIL_TAKEN".
    8. Otherwise return "OK".
    """
    # 0. Global Preprocessing
    clean_email, clean_role = _sanitize_inputs(email, role)

    # Step 1 (Spec rule 2): Email Format Validation
    if not _validate_email_structure(clean_email):
        return "INVALID_EMAIL"

    # Step 2 (Spec rule 3): Role Validation
    if not _validate_role(clean_role):
        return "INVALID_ROLE"

    # Extract local part for subsequent checks
    local_part, _ = clean_email.split("@", 1)

    # Step 3 (Spec rule 4): Prefix Validation (Staff & Manager only)
    if not _validate_prefix(local_part, clean_role):
        return "WRONG_PREFIX"

    # Step 4 (Spec rule 5): Name/Identifier Pattern Validation (Staff & Manager only)
    if not _validate_name_pattern(local_part, clean_role):
        return "INVALID_NAME"

    # Step 5 (Spec rule 6): Password Strength Validation
    if not _validate_password(password):
        return "WEAK_PASSWORD"

    # Step 6 (Spec rule 7): Duplicate Email Check
    if _check_duplicate_email(clean_email, existing_emails):
        return "EMAIL_TAKEN"

    # Step 7 (Spec rule 8): Success Condition
    return "OK"
