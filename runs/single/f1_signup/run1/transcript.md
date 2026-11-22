### Developer

```python
import re

def signup(email: str, password: str, role: str, existing_emails: dict) -> str:
    """
    Validates and registers a user for ShiftWise.
    
    Checks rules in order and returns the first error code or "OK".
    """
    # 1. Normalize email and role
    if not isinstance(email, str) or not isinstance(role, str) or not isinstance(password, str):
        return "INVALID_EMAIL"
    
    email = email.strip().lower()
    role = role.strip().lower()
    
    # 2. Email format validation
    # Exactly one '@'
    if email.count('@') != 1:
        return "INVALID_EMAIL"
    
    local_part, domain_part = email.split('@')
    
    # Something before '@' and a '.' in domain part (not first or last character)
    if not local_part:
        return "INVALID_EMAIL"
    
    if '.' not in domain_part or domain_part.startswith('.') or domain_part.endswith('.'):
        return "INVALID_EMAIL"
        
    # 3. Role validation
    if role not in ("staff", "manager", "owner"):
        return "INVALID_ROLE"
        
    # 4. Prefix validation for staff and manager
    if role in ("staff", "manager"):
        required_prefix = f"{role}_"
        if not local_part.startswith(required_prefix):
            return "WRONG_PREFIX"
            
        # 5. Name format validation for staff and manager
        # Format possibilities for local_part (after removing prefix):
        # - <name> (letters only)
        # - <name>.<surname> (letters only, separated by one dot)
        # - <name><empID> (letters only followed by digits only)
        rest = local_part[len(required_prefix):]
        if not rest:
            return "INVALID_NAME"
            
        # Check format 1: <name> (pure letters)
        if rest.isalpha():
            pass
        # Check format 2: <name>.<surname> (letters.letters)
        elif '.' in rest:
            parts = rest.split('.')
            if len(parts) == 2 and parts[0].isalpha() and parts[1].isalpha():
                pass
            else:
                return "INVALID_NAME"
        # Check format 3: <name><empID> (letters followed by digits)
        else:
            # Find where letters end and digits begin
            # Search for the transition from alpha to digit
            match = re.fullmatch(r"([a-z]+)(\d+)", rest)
            if not match:
                return "INVALID_NAME"
                
    # 6. Password validation
    # 8+ characters, at least 1 number, 1 capital letter, 1 special character
    if len(password) < 8:
        return "WEAK_PASSWORD"
        
    has_number = any(c.isdigit() for c in password)
    has_capital = any(c.isupper() for c in password)
    # Special character: anything that isn't a letter, number, or space
    has_special = any(not c.isalnum() and not c.isspace() for c in password)
    
    if not (has_number and has_capital and has_special):
        return "WEAK_PASSWORD"
        
    # 7. Check if email is already taken in any of the three lists
    # Flatten all existing emails, normalize them just in case
    all_existing = []
    for r_list in existing_emails.values():
        if isinstance(r_list, list):
            all_existing.extend([e.strip().lower() for e in r_list if isinstance(e, str)])
            
    if email in all_existing:
        return "EMAIL_TAKEN"
        
    # 8. All checks passed
    return "OK"
```
