# Human-led, AI-assisted condition

Code written by Akshana Leninrajah, working as a software engineer: she read the spec, used an AI assistant as a helper, reviewed and changed its output, and wrote her own tests.

- `manual/`: her five feature files, scored by `score.py` with the hidden tests
- `test_manual.py`: her own 68 tests (run with `python -m pytest human_led/test_manual.py` from inside `human_led/`)

Note: `booking.py` was built from an earlier draft of the spec (16-hour daily and 60-hour weekly limits with `OVER_HOURS`), not the final `specs/specs.md`. Her own tests follow that earlier draft, so they pass, but 8 hidden booking tests fail. We report this as is.
