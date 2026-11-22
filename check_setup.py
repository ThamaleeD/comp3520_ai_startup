"""Check your setup before the real run.

    python check_setup.py

1. Checks your API key is set
2. Lists the Gemini models your key can use
3. Sends one tiny test message
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "runners"))
from common import MODEL  # noqa: E402

key = os.environ.get("GEMINI_API_KEY")
if not key:
    sys.exit("GEMINI_API_KEY is not set. Run:  set GEMINI_API_KEY=your_key_here")
print("API key found.")

from google import genai  # noqa: E402
client = genai.Client(api_key=key)

print("\nModels you can use for text:")
for m in client.models.list():
    actions = getattr(m, "supported_actions", None) or []
    if "generateContent" in actions and "gemini" in m.name:
        print("  ", m.name.replace("models/", ""))

print(f"\nTesting model: {MODEL}")
r = client.models.generate_content(model=MODEL, contents="Reply with just: OK")
print("Answer:", (r.text or "").strip())
print("Model version:", r.model_version)
print("\nAll good. Next: python run_experiment.py")
