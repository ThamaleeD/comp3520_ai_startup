### Developer

```python
import re

def signup(email: str, password: str, role: str, existing_emails: dict) -> str:
    """
    Validates and registers a user signup for ShiftWise.
    
    Rules checked in order:
    1. Normalize email (strip whitespace, lowercase).
    2. Validate email structure (exactly one '@', non-empty prefix, domain contains '.' not at start/end).
    3. Validate role ('staff', 'manager', 'owner').
    4. For staff/manager, email must start with matching prefix ('staff_' or 'manager_').
    5. For staff/manager, the part of the local-part after the prefix must match allowed formats.
    6. Password must be 8+ chars, with at least 1 digit, 1 uppercase letter, and 1 special char.
    7. Email must not already exist in any of the existing_emails lists.
    8. Return "OK" if all checks pass.
    """
    # Rule 1: Normalize email (strip start/end whitespace, lowercase everything)
    if not isinstance(email, str):
        return "INVALID_EMAIL"
    email = email.strip().lower()

    # Normalize role
    if not isinstance(role, str):
        return "INVALID_ROLE"
    role = role.strip().lower()

    # Rule 2: Email format validation
    # Exactly one '@'
    if email.count('@') != 1:
        return "INVALID_EMAIL"
    
    local_part, domain_part = email.split('@')
    
    # Something before '@'
    if not local_part:
        return "INVALID_EMAIL"
    
    # '.' in the part after '@' (not first or last character of that part)
    if not domain_part or '.' not in domain_part:
        return "INVALID_EMAIL"
    if domain_part.startswith('.') or domain_part.endswith('.'):
        return "INVALID_EMAIL"

    # Rule 3: Role validation
    valid_roles = {"staff", "manager", "owner"}
    if role not in valid_roles:
        return "INVALID_ROLE"

    # Rule 4 & 5: Prefix and naming rules for staff and manager
    if role in {"staff", "manager"}:
        prefix = role + "_"
        if not local_part.startswith(prefix):
            return "WRONG_PREFIX"
        
        # Rest of the local part after the prefix
        rest = local_part[len(prefix):]
        
        # Formats:
        # 1. <name> -> letters only
        # 2. <name>.<surname> -> letters, single dot, letters (no dots at start/end of rest, exactly one dot)
        # 3. <name><empID> -> letters followed by digits only
        
        # Let's validate using regex on `rest`
        # <name> only: ^[a-z]+$
        # <name>.<surname>: ^[a-z]+\.[a-z]+$
        # <name><empID>: ^[a-z]+[0-9]+$
        
        pattern_name = r"^[a-z]+$"
        pattern_name_surname = r"^[a-z]+\.[a-z]+$"
        pattern_name_empid = r"^[a-z]+[0-9]+$"
        
        if not (re.match(pattern_name, rest) or 
                re.match(pattern_name_surname, rest) or 
                re.match(pattern_name_empid, rest)):
            return "INVALID_NAME"

    # Rule 6: Password strength
    # 8+ characters, at least 1 number, 1 capital letter, 1 special character
    if not isinstance(password, str) or len(password) < 8:
        return "WEAK_PASSWORD"
    
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    # Special character: anything that isn't a letter, number, or space
    has_special = any(not c.isalnum() and not c.isspace() for c in password)
    
    if not (has_digit and has_upper and has_special):
        return "WEAK_PASSWORD"

    # Rule 7: Check if email is already in any of the three lists
    # existing_emails is a dict of three lists, e.g., {"staff": [...], "manager": [...], "owner": [...]}
    all_existing = set()
    if isinstance(existing_emails, dict):
        for lst in existing_emails.values():
            if isinstance(lst, list):
                for e in lst:
                    if isinstance(e, str):
                        all_existing.add(e.strip().lower())
                        
    if email in all_existing:
        return "EMAIL_TAKEN"

    # Rule 8: All checks passed
    return "OK"
```
