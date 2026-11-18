# ShiftWise: Spec Change Log

COMP 3520 Assignment 4. Team: Thamalee Dasanayake, Akshana Leninrajah

How the feature specs were developed before any experiment was run.

- **First draft:** written with AI help (Claude), as a starting point.
- **Review:** Thamalee Dasanayake reviewed every rule and made the changes below. Claude only rewrote her changes into spec format.
- **Final rules:** decided by Thamalee, not the AI. These are the answer key for the hidden tests.

Date of review: Nov 18, 2026

---

## Changes made by Thamalee

| # | Feature | First draft (AI) | Changed to | Reason | Changed by |
|---|---|---|---|---|---|
| 1 | App | Name "ShiftSwap" | Name "ShiftWise" | Shift swaps were removed, so the old name no longer fit | Thamalee (AI suggested the name, Thamalee chose it) |
| 2 | Setting | Small business | Any company that runs shift work, with a set team structure (example: construction) | Long shifts, like construction's 12-hr shifts, need to be supported | Thamalee |
| 3 | All | Role names not covered outside Feature 4 | Role names ignore capitals and spaces in every feature (`MANAGER` = `manager`) | Users type roles differently; the system should treat them as the same word | Thamalee |
| 4 | All | No pay types | Staff = hourly; manager and owner = salary | Matches how corporate roles are paid | Thamalee |
| 5 | 1 Sign-up | One list of existing emails | Three lists: staff, manager, owner | Accounts are grouped by role | Thamalee |
| 6 | 1 Sign-up | Any valid email | Staff and manager emails must start with `staff_` / `manager_`, matching the role picked | Role is clear from the email | Thamalee |
| 7 | 1 Sign-up | No name rule | Format `<role>_<name>`; if the name is taken, add a surname (`staff_amy.chen`) or employee ID (`staff_amy1042`) | Better identification when names repeat | Thamalee |
| 8 | 1 Sign-up | Password: 8+ chars, 1 number, 1 capital | Also needs 1 special character | Stronger password policy | Thamalee |
| 9 | 2 Booking | Day as a number 0–6, whole hours | Date in `MM-DD-YY`, time in `HH:MM:SS` | Real date and time formats | Thamalee |
| 10 | 2 Booking | Max 12 hrs per shift | 30-min break per day; normal shift up to 12 hrs worked; hours over 12 allowed (paid double time) | Supports long-shift industries, e.g. construction | Thamalee |
| 11 | 2 Booking | Overlap rule unclear | Each staff member has their own schedule. Different staff can overlap; one person can't double-book themselves | Several staff often work the same hours | Thamalee |
| 12 | 3 | Shift swaps (manager approval) | Removed. Replaced with holiday requests | With a set team structure, swaps aren't needed | Thamalee |
| 13 | 3 Holidays | — | Staff holidays approved by a manager; manager holidays approved by the owner | Follows the reporting structure | Thamalee |
| 14 | 3 Holidays | Owner couldn't approve staff holidays | Owner approves staff holidays only if there's no manager | Staff fall under managers; owner is the backup | Thamalee |
| 15 | 4 Roles | Swap permissions | Holiday permissions: `request_holiday`, `approve_staff_holiday`, `approve_manager_holiday` | Matches the new Feature 3 | Thamalee |
| 16 | 5 Pay | Work week Mon–Sun (7 days) | Mon–Fri (5 days) | Corporate work week | Thamalee |
| 17 | 5 Pay | Overtime over 40 hrs/week | Kept: over 40 hrs/week = overtime (1.5×) | — | Thamalee (kept from the first draft) |
| 18 | 5 Pay | No daily limit | Over 12 hrs in a day = double time (2×), for that day only | Daily double-time rule | Thamalee |
| 19 | 5 Pay | Holiday hours paid 1.5× | Holidays get stat pay = average day's pay over the last month | Stat pay rule | Thamalee |
| 20 | 5 Pay | Everyone paid by the hour | Managers and owners get salary ÷ 52 per week, no overtime | Salaried roles | Thamalee |

---

## Details added by the AI (Thamalee to confirm)

These weren't in Thamalee's changes. Claude added them to make the rules complete enough to test. They only count once Thamalee confirms them.

| # | Feature | Detail | Status |
|---|---|---|---|
| A | 1 Sign-up | Owners have no email prefix rule | To confirm |
| B | 2 Booking | The 30-min break is unpaid and taken off the day's total (8.5 hrs scheduled = 8 hrs worked) | To confirm |
| C | 2 Booking | One break per day, even with 2 short shifts | To confirm |
| D | 2 Booking | No overnight shifts | To confirm |
| E | 3 Holidays | Owner holidays are approved automatically | To confirm |
| F | 3 Holidays | Nobody can approve their own request | To confirm |
| G | 5 Pay | Double-time hours don't count toward the 40 | To confirm |
| H | 5 Pay | Hours on a holiday must be 0 | To confirm |
| I | 2 Booking | Daily safety limit of 16 hrs worked (else `TOO_LONG`) | To confirm |
| J | 2 Booking | Weekly booking limit raised from 40 to 60 hrs, so overtime over 40 can happen | To confirm |

---

## Resolved issue

| Issue | Decision |
|---|---|
| Booking limits clashed with overtime and double-time pay (an 8 hr/day and 40 hr/week booking cap meant OT and double time could never happen) | Team chose to support 12-hr shifts (construction used as an example). Booking limits raised (see I and J), so OT and double time can now happen. |

---

## How to use this in the paper

- **Methodology:** Thamalee made 20 changes to the specs before testing, so the expected results come from human judgement, not the AI. This meets the assignment's rule not to let AI judge its own output.
- **Threats to validity:** the first draft came from an AI, which may have shaped the structure of the features.
- **AI-use disclosure:** Claude drafted the first version of the specs and wrote Thamalee's changes into spec format. Thamalee decided every rule.
