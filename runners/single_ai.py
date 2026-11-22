"""Condition B: one AI, one prompt.

The AI gets the spec and writes the code in a single call.
"""

SYSTEM = (
    "You are a software developer at a startup. "
    "Write clean, correct Python 3 code. Use only the standard library."
)


def build(ai, spec, module):
    """Ask the AI once. Returns (code, transcript)."""
    prompt = (
        f"Write the Python module `{module}.py` for this feature.\n\n"
        f"{spec}\n\n"
        "Return the complete module in one ```python code block."
    )
    answer = ai.ask(SYSTEM, prompt)
    transcript = f"### Developer\n\n{answer}\n"
    return answer, transcript
