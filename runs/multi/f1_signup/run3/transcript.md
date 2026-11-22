### PM

Here are the requirements and edge cases for the **`signup`** function based on the feature spec. Developers must implement these checks in the exact order specified.

### Global Preprocessing Rules
1. **Email Sanitization:** Strip leading and trailing whitespace from the email string and convert the entire email to lowercase before performing any checks.
2. **Role Sanitization:** Ignore capital letters and extra spaces for the `role` parameter (e.g., `"MANAGER"`, `"Manager"`, `" manager "` all evaluate to `"manager"`).

---

### Numbered Requirements & Edge Cases

#### Step 1: Email Format Validation
1. **At-Symbol Check:** The email must contain **exactly one** `@` character. If it has zero or multiple `@` symbols, return `"INVALID_EMAIL"`.
2. **Local Part Check:** There must be at least one character before the `@` symbol. If empty, return `"INVALID_EMAIL"`.
3. **Domain Part Check (Dot Rule):** The part after the `@` must contain at least one `.` character. Furthermore, the `.` cannot be the very first character or the very last character of that domain part. If this rule is violated, return `"INVALID_EMAIL"`.

#### Step 2: Role Validation
4. **Valid Roles:** The sanitized `role` must be strictly equal to `"staff"`, `"manager"`, or `"owner"`. If it is anything else, return `"INVALID_ROLE"`.

#### Step 3: Prefix Validation (Staff & Manager only)
5. **Role-Prefix Matching:** 
   - If the role is `"staff"`, the local part (before `@`) must start with the exact string `"staff_"`.
   - If the role is `"manager"`, the local part must start with the exact string `"manager_"`.
   - If the prefix does not match the role, return `"WRONG_PREFIX"`.
   - *Edge Case:* Owners do **not** require a specific prefix; any valid email format is acceptable for owners.

#### Step 4: Name/Identifier Pattern Validation (Staff & Manager only)
6. **Valid Name Formats:** For staff and manager roles, the remaining characters of the local part (everything *after* the `"staff_"` or `"manager_"` prefix) must match **one** of the three approved formats:
   - **Format 1 (`<name>`):** Letters only (e.g., `staff_mia`).
   - **Format 2 (`<name>.<surname>`):** Letters only, separated by a single dot (e.g., `staff_amy.chen`).
   - **Format 3 (`<name><empID>`):** Letters immediately followed by digits only (e.g., `staff_amy1042`).
   - If the remaining string violates all three formats (e.g., contains underscores, hyphens, or misplaced symbols like `staff_mia_2`), return `"INVALID_NAME"`.

#### Step 5: Password Strength Validation
7. **Minimum Length:** The password must be at least 8 characters long.
8. **Required Character Classes:** The password must contain at least:
   - One numeric digit (`0-9`)
   - One uppercase letter (`A-Z`)
   - One special character (any character that is **not** a letter, number, or space—such as `!`, `@`, `#`, `$`, `%`).
9. **Password Error Output:** If the password fails any of the length or character criteria, return `"WEAK_PASSWORD"`.

#### Step 6: Duplicate Email Check
10. **Global Uniqueness:** Check the provided `existing_emails` dictionary (which contains lists for `"staff"`, `"manager"`, and `"owner"`). If the sanitized email already exists in **any** of the three lists (regardless of which role category it is currently filed under), return `"EMAIL_TAKEN"`.

#### Step 7: Success Condition
11. **Successful Sign-up:** If all validations pass without triggering any of the above error returns, return `"OK"`.

### Architect

As the software architect, here is the structural blueprint, helper functions, and exact execution flow for the `signup` feature in `signup.py`.

---

### Module Architecture: `signup.py`

#### 1. Helper Functions

To keep the main `signup` function clean and modular, we define targeted helper functions:

*   **`_sanitize_inputs(email, role)`**
    *   *Input:* `email` (str), `role` (str)
    *   *Logic:* Strips whitespace and lowercases `email`. Lowercases and strips/collapses internal spaces for `role`.
    *   *Output:* Tuple `(clean_email, clean_role)`

*   **`_validate_email_structure(email)`**
    *   *Input:* `email` (sanitized str)
    *   *Logic:* 
        1. Count occurrences of `@`. Must be exactly 1. Split into `local_part` and `domain_part`.
        2. Verify `local_part` is non-empty.
        3. Verify `domain_part` contains at least one `.`, and that the `.` is neither index `0` nor the final index of `domain_part`.
    *   *Output:* Boolean `True` if valid, `False` otherwise.

*   **`_validate_role(role)`**
    *   *Input:* `role` (sanitized str)
    *   *Logic:* Checks if `role` is in `{"staff", "manager", "owner"}`.
    *   *Output:* Boolean `True` if valid, `False` otherwise.

*   **`_validate_prefix(local_part, role)`**
    *   *Input:* `local_part` (str), `role` (str)
    *   *Logic:* 
        *   If role is `"staff"`, checks `local_part.startswith("staff_")`.
        *   If role is `"manager"`, checks `local_part.startswith("manager_")`.
        *   If role is `"owner"`, returns `True` (owners bypass prefix rules).
    *   *Output:* Boolean.

*   **`_validate_name_pattern(local_part, role)`**
    *   *Input:* `local_part` (str), `role` (str)
    *   *Logic:* 
        *   If role is `"owner"`, returns `True` (bypasses name pattern rule).
        *   Extracts the remainder string after stripping the respective prefix (`"staff_"` or `"manager_"`).
        *   Evaluates the remainder against the 3 regex or character-class rules:
            1. `<name>`: All characters are alphabetic (`isalpha()`).
            2. `<name>.<surname>`: Split by `.`. Exactly two parts, both parts are entirely alphabetic.
            3. `<name><empID>`: Find the transition from letters to digits. The prefix part must be purely alphabetic, and the suffix part must be purely numeric (`isdigit()`).
    *   *Output:* Boolean.

*   **`_validate_password(password)`**
    *   *Input:* `password` (str)
    *   *Logic:* Checks length $\ge 8$, and scans for at least one `[0-9]`, one `[A-Z]`, and one special character (not alphanumeric and not a space).
    *   *Output:* Boolean.

*   **`_check_duplicate_email(email, existing_emails)`**
    *   *Input:* `email` (sanitized str), `existing_emails` (dict of lists)
    *   *Logic:* Flattens or iterates through all lists inside `existing_emails` (`"staff"`, `"manager"`, `"owner"`) to check if `email` is present.
    *   *Output:* Boolean (`True` if taken, `False` if unique).

---

#### 2. Main Function Flow: `signup(email, password, role, existing_emails)`

The main function executes the validation checks strictly in the sequence defined by the PM requirements. Returning early on the first failure.

```python
def signup(email, password, role, existing_emails) -> str:
    # 0. Global Preprocessing
    clean_email, clean_role = _sanitize_inputs(email, role)

    # Step 1: Email Format Validation
    if not _validate_email_structure(clean_email):
        return "INVALID_EMAIL"

    # Step 2: Role Validation
    if not _validate_role(clean_role):
        return "INVALID_ROLE"

    # Extract local part for subsequent checks
    local_part, _ = clean_email.split("@", 1)

    # Step 3: Prefix Validation (Staff & Manager only)
    if not _validate_prefix(local_part, clean_role):
        return "WRONG_PREFIX"

    # Step 4: Name/Identifier Pattern Validation (Staff & Manager only)
    if not _validate_name_pattern(local_part, clean_role):
        return "INVALID_NAME"

    # Step 5: Password Strength Validation
    if not _validate_password(password):
        return "WEAK_PASSWORD"

    # Step 6: Duplicate Email Check
    if _check_duplicate_email(clean_email, existing_emails):
        return "EMAIL_TAKEN"

    # Step 7: Success Condition
    return "OK"
```

### Developer

```python
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
    """
    # 0. Global Preprocessing
    clean_email, clean_role = _sanitize_inputs(email, role)

    # Step 1: Email Format Validation
    if not _validate_email_structure(clean_email):
        return "INVALID_EMAIL"

    # Step 2: Role Validation
    if not _validate_role(clean_role):
        return "INVALID_ROLE"

    # Extract local part for subsequent checks
    local_part, _ = clean_email.split("@", 1)

    # Step 3: Prefix Validation (Staff & Manager only)
    if not _validate_prefix(local_part, clean_role):
        return "WRONG_PREFIX"

    # Step 4: Name/Identifier Pattern Validation (Staff & Manager only)
    if not _validate_name_pattern(local_part, clean_role):
        return "INVALID_NAME"

    # Step 5: Password Strength Validation
    if not _validate_password(password):
        return "WEAK_PASSWORD"

    # Step 6: Duplicate Email Check
    if _check_duplicate_email(clean_email, existing_emails):
        return "EMAIL_TAKEN"

    # Step 7: Success Condition
    return "OK"
```

### Tester

```python
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
```
