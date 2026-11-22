### Developer

```python
import re

def signup(email, password, role, existing_emails):
    """
    Validates and registers a new user for ShiftWise based on strict role, email,
    naming convention, and password criteria.
    """
    # 1. Normalize email and role
    if email is None:
        return "INVALID_EMAIL"
    
    email = email.strip().lower()
    
    if role is None:
        return "INVALID_ROLE"
    
    role = role.strip().lower()

    # 2. Email structural validation
    # Must have exactly one '@'
    if email.count('@') != 1:
        return "INVALID_EMAIL"
    
    local_part, domain_part = email.split('@')
    
    # Something before '@' and a '.' in the part after it (not first or last char)
    if not local_part or not domain_part:
        return "INVALID_EMAIL"
    
    if '.' not in domain_part or domain_part.startswith('.') or domain_part.endswith('.'):
        return "INVALID_EMAIL"

    # 3. Role validation
    valid_roles = {"staff", "manager", "owner"}
    if role not in valid_roles:
        return "INVALID_ROLE"

    # 4 & 5. Prefix and naming format validation for staff and manager
    if role in {"staff", "manager"}:
        expected_prefix = f"{role}_"
        if not local_part.startswith(expected_prefix):
            return "WRONG_PREFIX"
        
        # Rest of the part before '@'
        remainder = local_part[len(expected_prefix):]
        
        # Check formats:
        # Format 1: <name> (letters only)
        # Format 2: <name>.<surname> (letters only, separated by one dot)
        # Format 3: <name><empID> (letters followed by digits)
        
        # Regular expressions for the three formats:
        # 1. ^[a-zA-Z]+$
        # 2. ^[a-zA-Z]+\.[a-zA-Z]+$
        # 3. ^[a-zA-Z]+[0-9]+$
        
        match_format_1 = re.fullmatch(r"^[a-z]+$", remainder)
        match_format_2 = re.fullmatch(r"^[a-z]+\.[a-z]+$", remainder)
        match_format_3 = re.fullmatch(r"^[a-z]+[0-9]+$", remainder)
        
        if not (match_format_1 or match_format_2 or match_format_3):
            return "INVALID_NAME"

    # 6. Password validation
    # 8+ characters, at least 1 number, 1 capital letter, 1 special character
    if password is None or len(password) < 8:
        return "WEAK_PASSWORD"
    
    has_number = any(c.isdigit() for c in password)
    has_capital = any(c.isupper() for c in password)
    # Special character: anything that isn't a letter, number, or space
    has_special = any(not c.isalnum() and not c.isspace() for c in password)
    
    if not (has_number and has_capital and has_special):
        return "WEAK_PASSWORD"

    # 7. Check if email is already in ANY of the three lists (case-insensitive)
    all_existing_emails = set()
    if existing_emails:
        for r_list in existing_emails.values():
            if r_list:
                for e in r_list:
                    if e:
                        all_existing_emails.add(e.strip().lower())
                        
    if email in all_existing_emails:
        return "EMAIL_TAKEN"

    # 8. All checks passed
    return "OK"
```
