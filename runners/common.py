"""Shared code for both AI runners.

Handles: reading the spec, calling Gemini, pulling the code out of the
answer, and counting time and tokens.
"""
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = ROOT / "specs" / "specs.md"

# Which file name each feature's code is saved as.
# The hidden tests import from these exact names.
FEATURES = {
    1: "signup",
    2: "booking",
    3: "holiday_requests",
    4: "roles",
    5: "pay",
}

# Model to test. Change with:  set GEMINI_MODEL=some-model-name
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")

# Seconds to wait between AI calls, so we stay under the free-tier limit.
WAIT_SECONDS = float(os.environ.get("WAIT_SECONDS", "13"))

# Same settings for every call, so runs are comparable.
TEMPERATURE = 1.0


def feature_spec(n):
    """Return the intro (rules for every feature) + the spec for feature n."""
    text = SPEC_FILE.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^## Feature ", text)
    intro = parts[0]
    for p in parts[1:]:
        if p.startswith(f"{n}:"):
            return intro + "## Feature " + p.strip().rstrip("-").strip()
    raise ValueError(f"Feature {n} not found in specs.md")


def extract_code(answer):
    """Pull the Python code out of the AI's answer.

    If there are ```python blocks, use the last one (the final version).
    If there are none, use the whole answer.
    """
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", answer, re.DOTALL)
    return blocks[-1].strip() + "\n" if blocks else answer.strip() + "\n"


class AI:
    """Calls Gemini and keeps a running count of calls, tokens and time."""

    def __init__(self, fake=False):
        self.fake = fake
        self.calls = 0
        self.prompt_tokens = 0
        self.output_tokens = 0
        self.model_version = "fake" if fake else MODEL
        if not fake:
            from google import genai
            key = os.environ.get("GEMINI_API_KEY")
            if not key:
                raise SystemExit("GEMINI_API_KEY is not set. See README.")
            self.client = genai.Client(api_key=key)

    def ask(self, system, prompt):
        """Send one message to the AI and return its text answer."""
        self.calls += 1
        if self.fake:
            return fake_answer(prompt)

        from google.genai import types, errors
        config = types.GenerateContentConfig(system_instruction=system,
                                             temperature=TEMPERATURE)
        for attempt in range(6):
            try:
                time.sleep(WAIT_SECONDS)
                r = self.client.models.generate_content(
                    model=MODEL, contents=prompt, config=config)
                break
            except (errors.ClientError, errors.ServerError) as e:
                # 429 = too many requests, 5xx = server busy: wait and retry
                if getattr(e, "code", None) in (429, 500, 503) and attempt < 5:
                    wait = 30 * (attempt + 1)
                    print(f"    busy ({e.code}), waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        u = r.usage_metadata
        if u:
            self.prompt_tokens += u.prompt_token_count or 0
            self.output_tokens += (u.candidates_token_count or 0) + (u.thoughts_token_count or 0)
        self.model_version = r.model_version or MODEL
        return r.text or ""


def fake_answer(prompt):
    """Offline mode for testing the pipeline: returns the reference code."""
    for n, module in FEATURES.items():
        if f"## Feature {n}:" in prompt:
            code = (ROOT / "reference" / f"{module}.py").read_text(encoding="utf-8")
            return f"Here you go:\n```python\n{code}```"
    return "Notes: looks fine."
