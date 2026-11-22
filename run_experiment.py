"""Run the AI conditions and save every output.

    python run_experiment.py            # real run with Gemini
    python run_experiment.py --fake     # offline test, no API calls

For each condition (single, multi), each feature (1-5) and each run (1-3):
  - asks the AI to build the feature
  - saves the code to runs/<condition>/f<N>_<module>/run<K>/<module>.py
  - saves the full AI conversation next to it (transcript.md)
  - adds a row to results/raw_runs.csv

Safe to stop and restart: runs that already finished are skipped.
"""
import argparse
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "runners"))
from common import AI, FEATURES, ROOT, extract_code, feature_spec  # noqa: E402
import single_ai  # noqa: E402
import multi_agent  # noqa: E402

CONDITIONS = {"single": single_ai, "multi": multi_agent}
RUNS = 3
CSV_FILE = ROOT / "results" / "raw_runs.csv"
FIELDS = ["condition", "feature", "module", "run", "model", "seconds",
          "ai_calls", "prompt_tokens", "output_tokens", "finished_at"]


def already_done():
    if not CSV_FILE.exists():
        return set()
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return {(r["condition"], r["feature"], r["run"]) for r in csv.DictReader(f)}


def save_row(row):
    new = not CSV_FILE.exists()
    CSV_FILE.parent.mkdir(exist_ok=True)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fake", action="store_true", help="offline test mode")
    p.add_argument("--only", choices=list(CONDITIONS), help="run one condition")
    args = p.parse_args()

    done = already_done()
    todo = [(c, n, k) for c in CONDITIONS if not args.only or c == args.only
            for n in FEATURES for k in range(1, RUNS + 1)
            if (c, str(n), str(k)) not in done]
    print(f"{len(todo)} runs to do.")

    for i, (cond, n, k) in enumerate(todo, 1):
        module = FEATURES[n]
        print(f"[{i}/{len(todo)}] {cond}  feature {n} ({module})  run {k}")
        ai = AI(fake=args.fake)
        start = time.time()
        answer, transcript = CONDITIONS[cond].build(ai, feature_spec(n), module)
        seconds = round(time.time() - start, 1)

        out = ROOT / "runs" / cond / f"f{n}_{module}" / f"run{k}"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{module}.py").write_text(extract_code(answer), encoding="utf-8")
        (out / "transcript.md").write_text(transcript, encoding="utf-8")

        save_row({"condition": cond, "feature": n, "module": module, "run": k,
                  "model": ai.model_version, "seconds": seconds,
                  "ai_calls": ai.calls, "prompt_tokens": ai.prompt_tokens,
                  "output_tokens": ai.output_tokens,
                  "finished_at": datetime.now().isoformat(timespec="seconds")})

    print("Done. Next: python score.py")


if __name__ == "__main__":
    main()
