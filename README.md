# ShiftWise: Single AI vs Multi-Agent AI Development

COMP 3520 Assignment 4 (Research). Team: Thamalee Dasanayake, Akshana Leninrajah.

Paper: see the PDF submitted with this repo.

**Research question:** How does a role-based multi-agent AI workflow compare with a single AI assistant and with human-led, AI-assisted development, in terms of correctness, code quality, time and cost, when building small software features?

We built 5 features of a made-up shift-scheduling app (ShiftWise) three ways:

- **Human-led, AI-assisted:** a team member works as a software engineer, using AI as a helper (`human_led/`)
- **Single AI:** one prompt, one AI call
- **Multi-agent:** PM → Architect → Developer → Tester, four AI calls

The two automated ways ran 3 times per feature (30 runs). Every version was scored with 153 hidden tests written before any AI ran.

## Results summary

| | Human-led | Single AI | Multi-agent |
|---|---|---|---|
| Hidden tests passed | 145/153 (94.8%) | 439/459 (95.6%) | 413/459 (90.0%) |
| Mean Ruff warnings | 0.4 | 1.1 | 1.7 |
| Mean cyclomatic complexity | 10.2 | 15.5 | 6.2 |
| Mean tokens per run | – | 2,090 | 12,826 |
| Median time per run | not recorded | 16.5 s | 65.0 s |

Model: `gemini-3.5-flash-lite` (Google Gemini API, free tier), temperature 1.0. Full results are in `results/`.

## Repository layout

| Path | What it is |
|---|---|
| `specs/specs.md` | Feature spec given to the AI |
| `specs/spec_changes.md` | Record of every human change to the spec |
| `hidden_tests/` | 153 pytest tests (the AI never sees these); `TEST_CASES.md` lists them in plain tables |
| `reference/` | Reference implementation, used only to check the tests have no mistakes (written with Claude) |
| `runners/common.py` | Shared code: reads the spec, calls Gemini, extracts code, counts tokens |
| `runners/single_ai.py` | Single-AI condition |
| `runners/multi_agent.py` | Multi-agent condition |
| `check_setup.py` | Checks your API key and model |
| `run_experiment.py` | Runs all 30 runs and saves code, transcripts and `results/raw_runs.csv` |
| `score.py` | Runs hidden tests, Ruff and Radon on every run and saves `results/scores.csv` |
| `runs/` | Every AI-generated file and the full agent conversation (`transcript.md`) |
| `human_led/` | Human-led, AI-assisted code and Akshana's own tests |
| `results/` | Raw results: `raw_runs.csv` (time, tokens) and `scores.csv` (tests, quality) |

## How to reproduce

Requires Python 3.10+ and a free Gemini API key from https://aistudio.google.com.

```bash
pip install -r requirements.txt
```

Set your key and model (PowerShell):

```powershell
$env:GEMINI_API_KEY="your_key_here"
$env:GEMINI_MODEL="gemini-3.5-flash-lite"
```

(macOS/Linux: `export GEMINI_API_KEY=your_key_here` and `export GEMINI_MODEL=gemini-3.5-flash-lite`)

Then:

```bash
python check_setup.py      # 1. check key and model
python run_experiment.py   # 2. run all 30 AI runs (about 30 min)
python score.py            # 3. score every run
```

To test the pipeline offline without any API calls: `python run_experiment.py --fake`.

To re-score our saved runs without calling the AI, just run `python score.py`.

`run_experiment.py` skips runs already in `results/raw_runs.csv`. To start fresh, delete `runs/` and `results/` first. AI output changes between runs, so new runs will not match ours exactly.

## AI use

- **Claude (Anthropic):** helped plan the study, drafted the first spec (then reviewed and changed by the team), wrote the hidden test code (expected results checked by the team), the reference implementation, and these scripts.
- **Gemini (Google):** the model being tested. It wrote all code in `runs/`.
- **ChatGPT (OpenAI):** used by Akshana as a helper in the human-led condition.

Never commit your API key. It is read from an environment variable only.
