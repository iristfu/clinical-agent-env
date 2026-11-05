# Clinical agent environment

A small mock EHR for a primary care practice, four clinical tasks inside it, state-based graders with tested controls, reference solutions, and a harness that runs a model against the tasks and attributes every failure.

All patient data is synthetic.

## Setup

Python 3.10 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your ANTHROPIC_API_KEY
python -m pytest -q           # 66 tests, no API calls
python -m harness.models      # confirm claude-opus-5 is available to your key
```

## Running

One entry point, `harness/run.py`, takes a task and a model and writes results, trajectories and a report to `runs/<run_id>/`.

```bash
# Prove the environment and graders before spending tokens
python -m harness.run --task all --policy reference --trials 10 --run-name reference
python -m harness.run --task all --policy controls --run-name controls

# Pilot, then calibrate task difficulty (see "Workflow")
python -m harness.run --task all --model claude-opus-5 --trials 3 --run-name pilot1

# Final runs, after committing and tagging the frozen tasks
python -m harness.run --task all --model claude-opus-5 --trials 10 --run-name final

# Attribute failures, then confirm each label by hand
python -m harness.triage runs/<run_id>
python -m harness.triage runs/<run_id> --review
python -m harness.report runs/<run_id>
```

From Python

```python
from harness.run import run_task
results = run_task("strep_allergy", "claude-opus-5", trials=1)
```

Useful flags are `--effort` (omit for the model default, which is high on Opus 5), `--concurrency`, `--task <id>` and `--start-index` for topping up a run. Opus 5 rejects non-default temperature, so the harness never sets it.

## Layout

```
env/
  fixtures/build_panel.py   the 30-patient panel, every trap hand-authored here
  fixtures/panel.json       generated from build_panel.py, the starting state of every trial
  store.py                  in-memory state, reset, state hashing
  tools.py                  17 tools; invalid requests raise ToolError, anything else is an env bug
tasks/<task_id>/
  prompt.md                 the exact prompt the model sees
  rubric.md                 expected answer, clinical rationale, traps, difficulty knobs
  task.py                   the grader
  reference.py              reference solution and grader controls
harness/
  run.py                    entry point
  agent_loop.py             Messages API tool-use loop
  trial.py                  shared dispatch, logging and grading for model and scripted runs
  report.py                 pass rates with Wilson intervals, failure breakdown, cost
  triage.py                 LLM first-pass failure labels plus human review
tests/                      environment, graders, harness
runs/                       one folder per run (config.json, results.jsonl, trajectories/, report.md, triage.jsonl)
WRITEUP.md
```

## Tasks

| Task | Shape | The deciding fact |
|---|---|---|
| strep_allergy | Single patient, safety | Penicillin anaphylaxis recorded only inside a 2019 ED note |
| apixaban_dose | Rule application | Current weight (128.3 lb) exists only in the 9/24 visit note |
| panel_a1c | Panel-wide coverage | 30 patients with mixed coding, a note-only diagnosis, a pending order, a death |
| med_rec_discharge | Multi-change reconciliation | A phone note after discharge supersedes two discharge changes |

## How a trial can end

| stop_reason | Meaning | Counted in pass rate |
|---|---|---|
| submitted | Model called submit | yes |
| end_turn | Model stopped calling tools without submitting | yes (graded on chart state) |
| turn_limit, token_limit, refusal | Model didn't finish | yes, as a failure |
| env_error | A tool raised an unexpected exception | no, trial is invalid and the traceback is logged |
| infra_error | API failed after retries | no, retried twice automatically, then marked invalid |

## Workflow

1. Run the reference and controls. Both must be clean before any model run means anything.
2. Pilot with 3 trials per task. Read every trajectory.
3. If a task passes 3 of 3, turn a difficulty knob up (each rubric lists them). If it fails 3 of 3, first look for an ambiguous prompt, a confusing tool response or a grader that rejected a valid answer. Only make the task easier once you're sure the model is failing on the clinical reasoning.
4. Rebuild the fixture if you changed it (`python -m env.fixtures.build_panel`), update the rubric and tests, run `pytest`.
5. Commit and tag (`git tag frozen-v1`). The run config records the commit and warns if task files are dirty.
6. Run 10 fresh trials per task. Triage, review, report, write up.
