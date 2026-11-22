### PM

Here is the clear, numbered list of requirements and edge cases for developers building the `signup` function based on the feature spec.

### General App Rule
1. **Role Case-Insensitivity & Whitespace:** Role inputs must be normalized to ignore leading/trailing spaces and capitalization (e.g., `" MANAGER "`, `"Manager"`, and `"manager"` are all treated identically).

---

### Validation Sequence (Check in Strict Order, Return First Error)

#### 1. Normalization & Sanitization
2. **Email Pre-processing:** Strip all leading and trailing whitespace from the email string, and convert the entire email string to lowercase before performing any checks.

#### 2. Email Structure Validation (Rule 2)
3. **At-Sign Check:** The email must contain **exactly one** `@` symbol. If it has zero, two, or more, return `"INVALID_EMAIL"`.
4. **Non-Empty Local Part:** There must be at least one character before the `@` symbol. If empty, return `"INVALID_EMAIL"`.
5. **Domain Format Check:** The part after the `@` must contain at least one `.` character. 
6. **Domain Dot Placement:** The `.` in the domain part cannot be the very first character or the very last character of the domain (e.g., `@.example.com` or `@example.` are invalid). If invalid, return `"INVALID_EMAIL"`.

#### 3. Role Validation (Rule 3)
7. **Allowed Roles:** The `role` argument (after normalization) must be strictly equal to `"staff"`, `"manager"`, or `"owner"`. If it is anything else, return `"INVALID_ROLE"`.

#### 4. Prefix Matching for Staff and Manager (Rule 4)
8. **Staff Prefix:** If the role is `"staff"`, the email local part (before `@`) must start with the exact string `"staff_"`. If not, return `"WRONG_PREFIX"`.
9. **Manager Prefix:** If the role is `"manager"`, the email local part (before `@`) must start with the exact string `"manager_"`. If not, return `"WRONG_PREFIX"`.
10. **Owner Exemption:** Owners are exempt from the prefix rule. Any valid email structure is accepted regarding prefixes.

#### 5. Naming Format Validation for Staff and Manager (Rule 5)
11. **Format Enforcement:** For `"staff"` and `"manager"`, the portion of the local part *following* the prefix (`staff_` or `manager_`) must strictly match **one** of three allowed formats:
    * **Format A (`<name>`):** Consists strictly of alphabetical letters only (no numbers, no special characters, no dots). Example: `staff_mia`.
    * **Format B (`<name>.<surname>`):** Consists of alphabetical letters, followed by a single dot `.`, followed by alphabetical letters. Example: `staff_amy.chen`.
    * **Format C (`<name><empID>`):** Consists of alphabetical letters immediately followed by digits only (no dots, no special characters). Example: `staff_amy1042`.
12. **Invalid Naming Fallback:** If the local part following the prefix does not match any of the three formats above (e.g., contains underscores like `staff_mia_2`, or illegal symbols), return `"INVALID_NAME"`.

#### 6. Password Strength Validation (Rule 6)
13. **Minimum Length:** The password must be at least 8 characters long.
14. **Required Numbers:** The password must contain at least 1 numeric digit (`0-9`).
15. **Required Uppercase Letter:** The password must contain at least 1 uppercase alphabetical letter (`A-Z`).
16. **Required Special Character:** The password must contain at least 1 special character, defined as *anything* that is not a letter, not a number, and not a space (e.g., `!`, `@`, `#`, `$`, `%`, etc.).
17. **Weak Password Fallback:** If the password fails any of the length, number, uppercase, or special character conditions, return `"WEAK_PASSWORD"`.

#### 7. Email Uniqueness / Duplicate Check (Rule 7)
18. **Global Uniqueness Across Lists:** Search all three lists within the `existing_emails` dictionary (`"staff"`, `"manager"`, and `"owner"`). If the normalized email already exists in **any** of these lists, return `"EMAIL_TAKEN"`.

#### 8. Success State (Rule 8)
19. **Successful Sign-up:** If the email passes all validation rules and checks without triggering any errors, return `"OK"`.

### Architect

As the software architect, here is the structural design and execution flow for the `signup` feature in `signup.py`. 

---

### Module Architecture: `signup.py`

#### 1. Helper Functions
To keep the main `signup` function clean and maintainable, the logic is broken down into focused helper functions:

*   `_normalize_role(role: str) -> str`
    *   Strips whitespace and converts the role to lowercase.
*   `_validate_email_structure(email: str) -> bool`
    *   Checks for exactly one `@`.
    *   Splits into local and domain parts, ensuring neither is empty.
    *   Validates that the domain contains a `.` that is neither the first nor the last character of the domain.
*   `_validate_role(role: str) -> bool`
    *   Checks if the normalized role is in `{"staff", "manager", "owner"}`.
*   `_validate_prefix(local_part: str, role: str) -> bool`
    *   If role is `"staff"`, checks `local_part.startswith("staff_")`.
    *   If role is `"manager"`, checks `local_part.startswith("manager_")`.
    *   Returns `True` for `"owner"`.
*   `_validate_name_format(local_part: str, role: str) -> bool`
    *   Bypasses for `"owner"`.
    *   Strips the respective prefix (`staff_` or `manager_`) to get the remainder.
    *   Evaluates the remainder against the three regex patterns:
        *   Format A: Entirely alphabetic (`^[a-zA-Z]+$`)
        *   Format B: Alphabetic, single dot, alphabetic (`^[a-zA-Z]+\.[a-zA-Z]+$`)
        *   Format C: Alphabetic followed by digits (`^[a-zA-Z]+\d+$`)
*   `_validate_password(password: str) -> bool`
    *   Checks length $\ge 8$.
    *   Checks presence of $\ge 1$ digit (`any(c.isdigit() for c in password)`).
    *   Checks presence of $\ge 1$ uppercase letter (`any(c.isupper() for c in password)`).
    *   Checks presence of $\ge 1$ special character (`any(not c.isalnum() and not c.isspace() for c in password)`).
*   `_is_email_taken(email: str, existing_emails: dict) -> bool`
    *   Flattens or iterates through all lists in `existing_emails.values()` to check if the normalized email is present.

---

### Data Flow & Execution Sequence

The `signup(email, password, role, existing_emails)` function executes checks strictly in the order specified by the PM requirements. As soon as a condition fails, it immediately halts and returns the corresponding error string.

```python
def signup(email: str, password: str, role: str, existing_emails: dict) -> str:
    # Step 1: Normalization & Sanitization
    normalized_email = email.strip().lower()
    normalized_role = _normalize_role(role)

    # Step 2: Email Structure Validation
    if not _validate_email_structure(normalized_email):
        return "INVALID_EMAIL"

    # Step 3: Role Validation
    if not _validate_role(normalized_role):
        return "INVALID_ROLE"

    # Extract local part for prefix and naming checks
    local_part, _ = normalized_email.split("@", 1)

    # Step 4: Prefix Matching for Staff and Manager
    if not _validate_prefix(local_part, normalized_role):
        return "WRONG_PREFIX"

    # Step 5: Naming Format Validation for Staff and Manager
    if not _validate_name_format(local_part, normalized_role):
        return "INVALID_NAME"

    # Step 6: Password Strength Validation
    if not _validate_password(password):
        return "WEAK_PASSWORD"

    # Step 7: Email Uniqueness / Duplicate Check
    if _is_email_taken(normalized_email, existing_emails):
        return "EMAIL_TAKEN"

    # Step 8: Success State
    return "OK"
```

### Developer

```python
import re

def _normalize_role(role: str) -> str:
    """Strips whitespace and converts the role to lowercase."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def _validate_email_structure(email: str) -> bool:
    """
    Checks for exactly one '@'.
    Splits into local and domain parts, ensuring neither is empty.
    Validates that the domain contains a '.' that is neither the first nor the last character.
    """
    if not isinstance(email, str):
        return False
    
    if email.count("@") != 1:
        return False
    
    local_part, domain_part = email.split("@", 1)
    
    if not local_part or not domain_part:
        return False
        
    if "." not in domain_part:
        return False
        
    if domain_part.startswith(".") or domain_part.endswith("."):
        return False
        
    return True

def _validate_role(role: str) -> bool:
    """Checks if the normalized role is in {"staff", "manager", "owner"}."""
    return role in {"staff", "manager", "owner"}

def _validate_prefix(local_part: str, role: str) -> bool:
    """
    If role is 'staff', checks local_part.startswith('staff_').
    If role is 'manager', checks local_part.startswith('manager_').
    Returns True for 'owner'.
    """
    if role == "staff":
        return local_part.startswith("staff_")
    elif role == "manager":
        return local_part.startswith("manager_")
    elif role == "owner":
        return True
    return False

def _validate_name_format(local_part: str, role: str) -> bool:
    """
    Bypasses for 'owner'.
    Strips the respective prefix ('staff_' or 'manager_') to get the remainder.
    Evaluates the remainder against the three allowed formats:
        - Format A: Entirely alphabetic ([a-zA-Z]+)
        - Format B: Alphabetic, single dot, alphabetic ([a-zA-Z]+\.[a-zA-Z]+)
        - Format C: Alphabetic followed by digits ([a-zA-Z]+\d+)
    """
    if role == "owner":
        return True
    
    prefix = f"{role}_"
    if not local_part.startswith(prefix):
        return False
        
    remainder = local_part[len(prefix):]
    
    # Format A: <name> (letters only)
    pattern_a = re.compile(r"^[a-zA-Z]+$")
    # Format B: <name>.<surname> (letters, single dot, letters)
    pattern_b = re.compile(r"^[a-zA-Z]+\.[a-zA-Z]+$")
    # Format C: <name><empID> (letters followed by digits)
    pattern_c = re.compile(r"^[a-zA-Z]+\d+$")
    
    return bool(pattern_a.match(remainder) or pattern_b.match(remainder) or pattern_c.match(remainder))

def _validate_password(password: str) -> bool:
    """
    Checks length >= 8.
    Checks presence of >= 1 digit.
    Checks presence of >= 1 uppercase letter.
    Checks presence of >= 1 special character (not alnum, not space).
    """
    if not isinstance(password, str):
        return False
        
    if len(password) < 8:
        return False
        
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_special = any(not c.isalnum() and not c.isspace() for c in password)
    
    return has_digit and has_upper and has_special

def _is_email_taken(email: str, existing_emails: dict) -> bool:
    """Searches all lists in existing_emails to check if the normalized email is present."""
    if not isinstance(existing_emails, dict):
        return False
        
    for role_list in existing_emails.values():
        if isinstance(role_list, list):
            # Normalize emails in existing lists just in case
            normalized_list = [str(e).strip().lower() for e in role_list]
            if email in normalized_list:
                return True
    return False

def signup(email: str, password: str, role: str, existing_emails: dict) -> str:
    """
    Validates a user sign-up request based on structural, role, prefix, naming, 
    password strength, and uniqueness rules, returning the first encountered error or 'OK'.
    """
    # Step 1: Normalization & Sanitization
    normalized_email = email.strip().lower() if isinstance(email, str) else ""
    normalized_role = _normalize_role(role)

    # Step 2: Email Structure Validation
    if not _validate_email_structure(normalized_email):
        return "INVALID_EMAIL"

    # Step 3: Role Validation
    if not _validate_role(normalized_role):
        return "INVALID_ROLE"

    # Extract local part for prefix and naming checks
    local_part, _ = normalized_email.split("@", 1)

    # Step 4: Prefix Matching for Staff and Manager
    if not _validate_prefix(local_part, normalized_role):
        return "WRONG_PREFIX"

    # Step 5: Naming Format Validation for Staff and Manager
    if not _validate_name_format(local_part, normalized_role):
        return "INVALID_NAME"

    # Step 6: Password Strength Validation
    if not _validate_password(password):
        return "WEAK_PASSWORD"

    # Step 7: Email Uniqueness / Duplicate Check
    if _is_email_taken(normalized_email, existing_emails):
        return "EMAIL_TAKEN"

    # Step 8: Success State
    return "OK"
```

### Tester

```python
import re

def _normalize_role(role: str) -> str:
    """Strips whitespace and converts the role to lowercase."""
    if not isinstance(role, str):
        return ""
    return role.strip().lower()

def _validate_email_structure(email: str) -> bool:
    """
    Checks for exactly one '@'.
    Splits into local and domain parts, ensuring neither is empty.
    Validates that the domain contains a '.' that is neither the first nor the last character.
    """
    if not isinstance(email, str):
        return False
    
    if email.count("@") != 1:
        return False
    
    local_part, domain_part = email.split("@", 1)
    
    if not local_part or not domain_part:
        return False
        
    if "." not in domain_part:
        return False
        
    if domain_part.startswith(".") or domain_part.endswith("."):
        return False
        
    return True

def _validate_role(role: str) -> bool:
    """Checks if the normalized role is in {"staff", "manager", "owner"}."""
    return role in {"staff", "manager", "owner"}

def _validate_prefix(local_part: str, role: str) -> bool:
    """
    If role is 'staff', checks local_part.startswith('staff_').
    If role is 'manager', checks local_part.startswith('manager_').
    Returns True for 'owner'.
    """
    if role == "staff":
        return local_part.startswith("staff_")
    elif role == "manager":
        return local_part.startswith("manager_")
    elif role == "owner":
        return True
    return False

def _validate_name_format(local_part: str, role: str) -> bool:
    """
    Bypasses for 'owner'.
    Strips the respective prefix ('staff_' or 'manager_') to get the remainder.
    Evaluates the remainder against the three allowed formats:
        - Format A: Entirely alphabetic ([a-zA-Z]+)
        - Format B: Alphabetic, single dot, alphabetic ([a-zA-Z]+\.[a-zA-Z]+)
        - Format C: Alphabetic followed by digits ([a-zA-Z]+\d+)
    """
    if role == "owner":
        return True
    
    prefix = f"{role}_"
    if not local_part.startswith(prefix):
        return False
        
    remainder = local_part[len(prefix):]
    
    # Format A: <name> (letters only)
    pattern_a = re.compile(r"^[a-zA-Z]+$")
    # Format B: <name>.<surname> (letters, single dot, letters)
    pattern_b = re.compile(r"^[a-zA-Z]+\.[a-zA-Z]+$")
    # Format C: <name><empID> (letters followed by digits)
    pattern_c = re.compile(r"^[a-zA-Z]+\d+$")
    
    return bool(pattern_a.match(remainder) or pattern_b.match(remainder) or pattern_c.match(remainder))

def _validate_password(password: str) -> bool:
    """
    Checks length >= 8.
    Checks presence of >= 1 digit.
    Checks presence of >= 1 uppercase letter.
    Checks presence of >= 1 special character (not alnum, not space).
    """
    if not isinstance(password, str):
        return False
        
    if len(password) < 8:
        return False
        
    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_special = any(not c.isalnum() and not c.isspace() for c in password)
    
    return has_digit and has_upper and has_special

def _is_email_taken(email: str, existing_emails: dict) -> bool:
    """Searches all lists in existing_emails to check if the normalized email is present."""
    if not isinstance(existing_emails, dict):
        return False
        
    for role_list in existing_emails.values():
        if isinstance(role_list, list):
            # Normalize emails in existing lists just in case
            normalized_list = [str(e).strip().lower() for e in role_list]
            if email in normalized_list:
                return True
    return False

def signup(email: str, password: str, role: str, existing_emails: dict) -> str:
    """
    Validates a user sign-up request based on structural, role, prefix, naming, 
    password strength, and uniqueness rules, returning the first encountered error or 'OK'.
    """
    # Step 1: Normalization & Sanitization
    normalized_email = email.strip().lower() if isinstance(email, str) else ""
    normalized_role = _normalize_role(role)

    # Rule 1 & 3: Role validation must precede email check or follow email structure check?
    # Let's check spec order:
    # 1. Ignore spaces at the start/end of the email, and ignore capital letters everywhere.
    # 2. Email must have exactly one '@', something before it, and a '.' in the part after it (not first or last character of that part). Else "INVALID_EMAIL".
    # 3. role must be staff, manager or owner. Else "INVALID_ROLE".
    # 4. For staff and manager, the email must start with staff_ or manager_ to match the role. Else "WRONG_PREFIX".
    # 5. For staff and manager, the rest of the part before @ must match one of the 3 formats above. Else "INVALID_NAME".
    # 6. Password must be 8+ characters, with at least 1 number, 1 capital letter and 1 special character... Else "WEAK_PASSWORD".
    # 7. If the email is already in any of the three lists, return "EMAIL_TAKEN".
    # 8. Otherwise return "OK".

    # Step 2: Email Structure Validation
    if not _validate_email_structure(normalized_email):
        return "INVALID_EMAIL"

    # Step 3: Role Validation (Must be checked BEFORE prefix/name checks as per spec order)
    if not _validate_role(normalized_role):
        return "INVALID_ROLE"

    # Extract local part for prefix and naming checks
    local_part, _ = normalized_email.split("@", 1)

    # Step 4: Prefix Matching for Staff and Manager
    if not _validate_prefix(local_part, normalized_role):
        return "WRONG_PREFIX"

    # Step 5: Naming Format Validation for Staff and Manager
    if not _validate_name_format(local_part, normalized_role):
        return "INVALID_NAME"

    # Step 6: Password Strength Validation
    if not _validate_password(password):
        return "WEAK_PASSWORD"

    # Step 7: Email Uniqueness / Duplicate Check
    if _is_email_taken(normalized_email, existing_emails):
        return "EMAIL_TAKEN"

    # Step 8: Success State
    return "OK"
```
