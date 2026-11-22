"""Score every version of every feature with the hidden tests.

    python score.py

Scores:
  - runs/single/...   (condition B)
  - runs/multi/...    (condition C)
  - human_led/manual/ (human-led, AI-assisted: Akshana's code)

For each one it records:
  - tests passed / total          (correctness)
  - ruff warnings                 (code quality: style and bugs)
  - average cyclomatic complexity (code quality: how tangled the code is)
  - lines of code

Writes results/scores.csv. The hidden tests are never changed.
"""
import csv
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "runners"))
from common import FEATURES  # noqa: E402

TESTS = ROOT / "hidden_tests"
OUT = ROOT / "results" / "scores.csv"
FIELDS = ["condition", "feature", "module", "run", "passed", "total",
          "pass_rate", "imports_ok", "ruff_warnings", "avg_complexity", "loc"]


def run_tests(code_dir, n, module):
    """Run the hidden tests for feature n against the code in code_dir."""
    test_file = next(TESTS.glob(f"test_f{n}_*.py"))
    with tempfile.TemporaryDirectory() as tmp:
        xml = Path(tmp) / "r.xml"
        env = {**os.environ, "PYTHONPATH": str(code_dir)}
        try:
            subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-q", "--tb=no",
                 "-p", "no:cacheprovider", f"--junitxml={xml}"],
                cwd=tmp, env=env, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:   # code got stuck (e.g. endless loop)
            return 0, total_tests(n), False
        if not xml.exists():
            return 0, total_tests(n), False
        suite = ET.parse(xml).getroot()
        suite = suite if suite.tag == "testsuite" else suite.find("testsuite")
        total = int(suite.get("tests", 0))
        bad = int(suite.get("failures", 0)) + int(suite.get("errors", 0)) + int(suite.get("skipped", 0))
        # If the code didn't even import, pytest reports 1 collection error
        if total <= 1 and int(suite.get("errors", 0)) >= 1:
            return 0, total_tests(n), False
        return total - bad, total, True


_TOTALS = {}


def total_tests(n):
    """How many tests feature n has (counted once from the test file)."""
    if n not in _TOTALS:
        test_file = next(TESTS.glob(f"test_f{n}_*.py"))
        r = subprocess.run([sys.executable, "-m", "pytest", str(test_file),
                            "--collect-only", "-q", "-p", "no:cacheprovider"],
                           env={**os.environ, "PYTHONPATH": str(ROOT / "reference")},
                           capture_output=True, text=True)
        m = re.search(r"(\d+) tests? collected", r.stdout)
        _TOTALS[n] = int(m.group(1)) if m else 0
    return _TOTALS[n]


def quality(file):
    """Ruff warnings, average complexity and lines of code for one file."""
    r = subprocess.run([sys.executable, "-m", "ruff", "check", str(file),
                        "--output-format=json", "--isolated"],
                       capture_output=True, text=True)
    try:
        warnings = len(json.loads(r.stdout or "[]"))
    except json.JSONDecodeError:
        warnings = ""
    r = subprocess.run([sys.executable, "-m", "radon", "cc", str(file), "-j"],
                       capture_output=True, text=True)
    try:
        blocks = next(iter(json.loads(r.stdout).values()))
        scores = [b["complexity"] for b in blocks if isinstance(b, dict)]
        cc = round(sum(scores) / len(scores), 2) if scores else 0
    except (json.JSONDecodeError, StopIteration, TypeError):
        cc = ""
    loc = sum(1 for line in file.read_text(encoding="utf-8").splitlines()
              if line.strip() and not line.strip().startswith("#"))
    return warnings, cc, loc


def targets():
    """Every (condition, feature, run, folder) we need to score."""
    for cond in ("single", "multi"):
        for n, module in FEATURES.items():
            base = ROOT / "runs" / cond / f"f{n}_{module}"
            for run_dir in sorted(base.glob("run*")):
                yield cond, n, module, run_dir.name.replace("run", ""), run_dir
    # Human-led, AI-assisted code (Akshana). Her holiday file is called
    # holidays.py, so it is copied as holiday_requests.py for the tests.
    human = ROOT / "human_led" / "manual"
    names = {"holiday_requests": "holidays"}
    for n, module in FEATURES.items():
        src = human / f"{names.get(module, module)}.py"
        if src.exists():
            tmp = Path(tempfile.mkdtemp())
            shutil.copy(src, tmp / f"{module}.py")
            yield "human_led", n, module, "1", tmp


def main():
    rows = []
    for cond, n, module, run, folder in targets():
        file = folder / f"{module}.py"
        passed, total, ok = run_tests(folder, n, module)
        warnings, cc, loc = quality(file)
        rows.append({"condition": cond, "feature": n, "module": module,
                     "run": run, "passed": passed, "total": total,
                     "pass_rate": round(passed / total, 3) if total else 0,
                     "imports_ok": ok, "ruff_warnings": warnings,
                     "avg_complexity": cc, "loc": loc})
        print(f"{cond:6} f{n} run{run}: {passed}/{total} passed, "
              f"{warnings} ruff warnings, complexity {cc}, {loc} lines")

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
