"""Condition C: a multi-agent AI team.

Four agents, each with its own role, pass work down a pipeline:

    PM  ->  Architect  ->  Developer  ->  Tester
  (needs)    (design)       (code)      (review + fix)

Inspired by Paperclip-style "AI companies". Same model as condition B;
only the roles and the hand-offs are different.
"""

ROLES = {
    "pm": (
        "You are the product manager at a startup. You turn a feature spec "
        "into a clear numbered list of requirements and edge cases for the "
        "developers. Do not write code."
    ),
    "architect": (
        "You are the software architect at a startup. You design how a "
        "feature should be built: functions, helper functions, data flow, "
        "and the exact order of checks. Do not write the full code."
    ),
    "developer": (
        "You are a software developer at a startup. Write clean, correct "
        "Python 3 code. Use only the standard library."
    ),
    "tester": (
        "You are the QA tester at a startup. You review code against the "
        "spec, find bugs and missed edge cases, and fix them."
    ),
}


def build(ai, spec, module):
    """Run the 4-agent pipeline. Returns (final answer, transcript)."""
    pm = ai.ask(ROLES["pm"],
        f"Feature spec:\n\n{spec}\n\n"
        "List every requirement and edge case the developer must handle.")

    design = ai.ask(ROLES["architect"],
        f"Feature spec:\n\n{spec}\n\nPM requirements:\n\n{pm}\n\n"
        f"Design the module `{module}.py`.")

    code = ai.ask(ROLES["developer"],
        f"Feature spec:\n\n{spec}\n\nPM requirements:\n\n{pm}\n\n"
        f"Architect design:\n\n{design}\n\n"
        f"Write the module `{module}.py`. "
        "Return the complete module in one ```python code block.")

    final = ai.ask(ROLES["tester"],
        f"Feature spec:\n\n{spec}\n\nDeveloper's code:\n\n{code}\n\n"
        "Check the code against every rule in the spec. Fix any bugs. "
        "Return the complete final module in one ```python code block, "
        "even if nothing needed fixing.")

    transcript = (f"### PM\n\n{pm}\n\n### Architect\n\n{design}\n\n"
                  f"### Developer\n\n{code}\n\n### Tester\n\n{final}\n")
    return final, transcript
