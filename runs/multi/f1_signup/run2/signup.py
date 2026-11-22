def _is_valid_email_structure(email: str) -> bool:
    if email.count('@') != 1:
        return False
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local_part, domain_part = parts
    
    # Local part must be non-empty
    if not local_part:
        return False
    
    # Domain must contain at least one dot, and dot cannot be first or last character
    if '.' not in domain_part:
        return False
    
    if domain_part.startswith('.') or domain_part.endswith('.'):
        return False
        
    return True


def _is_valid_name_format(local_part: str, role: str) -> bool:
    prefix = f"{role}_"
    if not local_part.startswith(prefix):
        return False
    
    remainder = local_part[len(prefix):]
    if not remainder:
        return False
    
    # Format 1: <name> (letters only)
    if remainder.isalpha():
        return True
    
    # Format 2: <name>.<surname> (separated by a single dot, both alpha)
    if '.' in remainder:
        if remainder.count('.') != 1:
            return False
        name_part, surname_part = remainder.split('.')
        if name_part.isalpha() and surname_part.isalpha():
            return True
        return False
    
    # Format 3: <name><empID> (<name> is alpha, <empID> is digits)
    # Find transition from letters to digits
    first_digit_idx = -1
    for i, char in enumerate(remainder):
        if char.isdigit():
            first_digit_idx = i
            break
            
    if first_digit_idx != -1:
        name_chunk = remainder[:first_digit_idx]
        id_chunk = remainder[first_digit_idx:]
        if name_chunk.isalpha() and id_chunk.isdigit():
            return True
            
    return False


def _is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
        
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() and not c.isspace() for c in password)
    
    return has_upper and has_digit and has_special


def signup(email: str, password: str, role: str, existing_emails: dict) -> str:
    """
    Validates sign-up credentials based on ShiftWise feature specifications.
    
    Parameters:
    - email: str
    - password: str
    - role: str ("staff", "manager", or "owner")
    - existing_emails: dict with lists of emails for each role
    
    Returns:
    - str: "OK" if all checks pass, or the specific error string.
    """
    # 1. Normalize inputs
    clean_email = email.strip().lower()
    clean_role = role.strip().lower()
    
    # 2. Check Role Validation (Moved up to satisfy the spec order:
    # "3. role must be staff, manager or owner. Else "INVALID_ROLE".")
    if clean_role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"
        
    # 3. Check Email Structure
    if not _is_valid_email_structure(clean_email):
        return "INVALID_EMAIL"
        
    # 4. Check Role-Prefix Matching (staff and manager only)
    if clean_role in {"staff", "manager"}:
        expected_prefix = f"{clean_role}_"
        if not clean_email.startswith(expected_prefix):
            return "WRONG_PREFIX"
            
    # 5. Check Name Format Validation (staff and manager only)
    if clean_role in {"staff", "manager"}:
        if not _is_valid_name_format(clean_email, clean_role):
            return "INVALID_NAME"
            
    # 6. Check Password Strength
    if not _is_strong_password(password):
        return "WEAK_PASSWORD"
        
    # 7. Check Email Uniqueness
    for email_list in existing_emails.values():
        if clean_email in [e.lower() for e in email_list]:
            return "EMAIL_TAKEN"
            
    # 8. Success State
    return "OK"
