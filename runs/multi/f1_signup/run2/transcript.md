### PM

Here are the clear requirements and edge cases for developers implementing the `signup(email, password, role, existing_emails)` feature, based on the ShiftWise product spec.

### Global Assumptions
1. **Role Sanitization:** The `role` argument must be case-insensitive and ignore leading/trailing spaces (e.g., `" MANAGER "` evaluates to `"manager"`).

---

### Requirements (Strict Execution Order)

The function must evaluate validation checks sequentially and return the **first** matching error string, or `"OK"` if all checks pass.

1. **Email Normalization:**
   * Automatically strip leading and trailing whitespace from the email.
   * Convert the entire email to lowercase before performing any checks.

2. **Check 1: Email Structure (`"INVALID_EMAIL"`)**
   * Must contain exactly one `@` symbol.
   * Must have a non-empty local part (before `@`).
   * The domain part (after `@`) must contain at least one `.` character.
   * The `.` in the domain part cannot be the very first or the very last character of the domain.

3. **Check 2: Role Validation (`"INVALID_ROLE"`)**
   * The sanitized `role` must equal `"staff"`, `"manager"`, or `"owner"`.

4. **Check 3: Role-Prefix Matching (`"WRONG_PREFIX"`)**
   * *Applies to staff and manager roles only.*
   * The local part of the email must strictly start with `staff_` (if role is staff) or `manager_` (if role is manager). 
   * (Owners are exempt from prefix rules).

5. **Check 4: Name Format Validation (`"INVALID_NAME"`)**
   * *Applies to staff and manager roles only.*
   * Following the prefix (`staff_` or `manager_`), the remainder of the local part must match one of three valid formats:
     * **Format 1 (`<role>_<name>`):** `<name>` consists exclusively of alphabetical characters (letters only).
     * **Format 2 (`<role>_<name>.<surname>`):** `<name>` and `<surname>` consist exclusively of alphabetical characters, separated by a single dot `.`
     * **Format 3 (`<role>_<name><empID>`):** `<name>` consists exclusively of alphabetical characters, immediately followed by `<empID>` which consists exclusively of digits.
   * (Owners are exempt from these specific naming rules).

6. **Check 5: Password Strength (`"WEAK_PASSWORD"`)**
   * Password length must be 8 or more characters.
   * Must contain at least one numeric digit (`0-9`).
   * Must contain at least one uppercase alphabetical letter (`A-Z`).
   * Must contain at least one special character (any character that is **not** a letter, a number, or a space, such as `!`, `@`, `#`, `$`, `%`, etc.).

7. **Check 6: Email Uniqueness (`"EMAIL_TAKEN"`)**
   * Check the normalized email against every list inside the `existing_emails` dictionary (across all three keys: `"staff"`, `"manager"`, and `"owner"`).
   * If the email exists in **any** of the lists, reject it.

8. **Success State (`"OK"`)**
   * If all validation checks pass successfully, return `"OK"`.

---

### Edge Cases to Handle

1. **Case-Insensitive Input:** 
   * Email inputs with mixed casing (e.g., `"STAFF_Mia@Example.com"`) must be successfully normalized, validated against prefixes/lists, and processed.
2. **Whitespace Padding:** 
   * Inputs with accidental padding (e.g., `"  staff_mia@example.com  "`) must be cleaned prior to parsing.
3. **Owner Emails:** 
   * An owner's email does not require a `staff_` or `manager_` prefix, and does not need to follow Formats 1, 2, or 3. Any structurally valid email (Check 1) is acceptable as long as it passes password rules and is not already taken.
4. **Incorrect Role-Prefix Mapping:** 
   * A staff member attempting to sign up with a `manager_` prefix (or vice versa) must trigger `"WRONG_PREFIX"`.
5. **Missing Special Characters in Passwords:** 
   * Passwords containing letters and numbers (e.g., `"Secret123"`) must trigger `"WEAK_PASSWORD"` due to the missing special character requirement.
6. **Cross-Role Email Duplication:** 
   * If an email is listed under `"manager"` in `existing_emails`, attempting to sign up as a `"staff"` member with that same email must still trigger `"EMAIL_TAKEN"`.
7. **Malformed Domain Dots:** 
   * Emails with a dot as the first or last character of the domain (e.g., `staff_mia@.com` or `staff_mia@example.com.`) must trigger `"INVALID_EMAIL"`.
8. **Invalid Characters in Name/ID Segments:** 
   * Staff/manager emails containing symbols or numbers in forbidden spots (e.g., `staff_mia_2@example.com` or `staff_mia!.chen@example.com`) must trigger `"INVALID_NAME"`.

### Architect

Here is the architectural design for the `signup.py` module, outlining the required functions, data flow, helper utilities, and the strict execution order of checks.

---

### Architecture Overview (`signup.py`)

#### 1. Helper Functions (Modular Validation Utilities)

To keep the main function clean and maintainable, the module will utilize targeted helper functions:

*   **`normalize_inputs(email, role)`**:
    *   Strips leading/trailing whitespace and converts `email` to lowercase.
    *   Strips leading/trailing whitespace and converts `role` to lowercase.
*   **`is_valid_email_structure(email) -> bool`**:
    *   Splits the email by `@`. Ensures there is exactly 1 split (yielding 2 parts: local and domain).
    *   Ensures the local part is non-empty.
    *   Checks the domain part for a `.` character using `.find()` or `.count()`.
    *   Ensures the `.` is neither the first index (`index 0`) nor the last index (`index len(domain) - 1`).
*   **`is_valid_name_format(local_part, role) -> bool`**:
    *   *Pre-condition:* Assumes `role` is either `"staff"` or `"manager"`.
    *   Strips the expected prefix (`staff_` or `manager_`). If it doesn't match, returns `False`.
    *   Parses the remainder against the 3 regex or character-group patterns:
        *   **Format 1 (`<name>`):** Entire remainder is `.isalpha()`.
        *   **Format 2 (`<name>.<surname>`):** Splits by `.`. Exactly one dot resulting in two parts, both of which are `.isalpha()`.
        *   **Format 3 (`<name><empID>`):** Finds the transition from letters to digits. The prefix chunk must be `.isalpha()` and the suffix chunk must be `.isdigit()` (and non-empty).
*   **`is_strong_password(password) -> bool`**:
    *   Checks `len(password) >= 8`.
    *   Iterates or checks using regex/character sets for:
        *   At least one uppercase character (`any(c.isupper() for c in password)`).
        *   At least one numeric digit (`any(c.isdigit() for c in password)`).
        *   At least one special character (`any(not c.isalnum() and not c.isspace() for c in password)`).

---

#### 2. Main Function Data Flow & Execution Order

`signup(email, password, role, existing_emails) -> str`

The function executes sequentially, immediately returning the corresponding error string upon failure.

```
[Start signup()]
       │
       ▼
 1. Normalize inputs (email.strip().lower(), role.strip().lower())
       │
       ▼
 2. Check Email Structure ──(Fails)──> Return "INVALID_EMAIL"
       │ (Passes)
       ▼
 3. Check Role Validation ──(Fails)──> Return "INVALID_ROLE"
       │ (Passes)
       ▼
 4. Check Role-Prefix ──────(Fails)──> Return "WRONG_PREFIX"
    (If role is staff/manager)
       │ (Passes or role is owner)
       ▼
 5. Check Name Format ──────(Fails)──> Return "INVALID_NAME"
    (If role is staff/manager)
       │ (Passes or role is owner)
       ▼
 6. Check Password Strength ─(Fails)──> Return "WEAK_PASSWORD"
       │ (Passes)
       ▼
 7. Check Email Uniqueness ──(Fails)──> Return "EMAIL_TAKEN"
    (Search across all lists in existing_emails values)
       │ (Passes)
       ▼
 8. Return "OK"
```

---

### Detailed Step-by-Step Logic Implementation Blueprint

1.  **Normalization:**
    ```python
    clean_email = email.strip().lower()
    clean_role = role.strip().lower()
    ```
2.  **Check 1 (`"INVALID_EMAIL"`):**
    *   Verify `@` count == 1.
    *   Verify split parts `local, domain = clean_email.split('@')`.
    *   Verify `domain` contains `.` and does not start/end with `.`.
3.  **Check 2 (`"INVALID_ROLE"`):**
    *   Verify `clean_role in {"staff", "manager", "owner"}`.
4.  **Check 3 (`"WRONG_PREFIX"`):**
    *   If `clean_role == "staff"` and not `clean_email.startswith("staff_")`: return `"WRONG_PREFIX"`
    *   If `clean_role == "manager"` and not `clean_email.startswith("manager_")`: return `"WRONG_PREFIX"`
5.  **Check 4 (`"INVALID_NAME"`):**
    *   If `clean_role in {"staff", "manager"}`, slice off the prefix (`staff_` or `manager_`).
    *   Validate remainder against Format 1, Format 2, or Format 3 rules. If all fail, return `"INVALID_NAME"`.
6.  **Check 5 (`"WEAK_PASSWORD"`):**
    *   Run length, uppercase, digit, and special character assertions. If any fail, return `"WEAK_PASSWORD"`.
7.  **Check 6 (`"EMAIL_TAKEN"`):**
    *   Flatten or iterate through all lists in `existing_emails.values()`.
    *   If `clean_email` exists in any of those lists, return `"EMAIL_TAKEN"`.
8.  **Success:**
    *   Return `"OK"`.

### Developer

```python
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
    
    # 2. Check Email Structure
    if not _is_valid_email_structure(clean_email):
        return "INVALID_EMAIL"
        
    # 3. Check Role Validation
    if clean_role not in {"staff", "manager", "owner"}:
        return "INVALID_ROLE"
        
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
```

### Tester

```python
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
```
