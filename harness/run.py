"""Single entry point: takes a task and a model (or a scripted policy) and hands back results.

Command line
  python -m harness.run --task strep_allergy --model claude-opus-5 --trials 10
  python -m harness.run --task all --model claude-opus-5 --trials 10 --run-name final
  python -m harness.run --task all --policy reference --trials 10     # reference solutions, same harness
  python -m harness.run --task all --policy controls                  # grader controls

In code
  from harness.run import run_task
  results = run_task("strep_allergy", "claude-opus-5", trials=1)
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from env.store import DEFAULT_FIXTURE
from env.tools import TOOLS
from harness.trial import initial_hash, run_scripted
from tasks import load_task, task_ids

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"
DEFAULT_MODEL = "claude-opus-5"


def load_dotenv():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def make_client():
    import anthropic
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. Put it in .env (see .env.example) or export it.")
    return anthropic.Anthropic(max_retries=8, timeout=900)


def _git_info():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                         stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--", "env", "tasks", "harness"],
                                             cwd=ROOT, text=True).strip())
        return {"commit": commit, "dirty": dirty}
    except Exception:  # noqa: BLE001
        return {"commit": None, "dirty": None}


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()[:12]


class ResultSink:
    def __init__(self, run_dir):
        self.path = run_dir / "results.jsonl" if run_dir else None
        self.lock = threading.Lock()

    def add(self, result):
        if self.path:
            with self.lock, self.path.open("a") as f:
                f.write(json.dumps(result, ensure_ascii=False, default=str) + "\n")


def _print_result(r):
    if r["policy"].startswith("control:"):
        verdict = "OK " if r["control_ok"] else "BAD"
        print(f"  [{r['task']:<18} {r['policy']:<44}] {verdict} passed={r['passed']} "
              f"failed={sorted(r['failed_critical'])}")
        return
    status = "INVALID" if not r["valid"] else ("PASS" if r["passed"] else "FAIL")
    extra = f" failed={r['failed_critical']}" if r["valid"] and not r["passed"] else ""
    print(f"  [{r['task']:<18} trial {r['trial']:02d}] {status:<7} score={r['score'] if r['score'] is not None else '-'} "
          f"turns={r['turns']} stop={r['stop_reason']}{extra}", flush=True)


def run_task(task_id, model=DEFAULT_MODEL, *, policy="model", trials=1, run_dir=None, client=None, effort=None,
             concurrency=4, max_tokens=32000, show_thinking=True, infra_retries=2, start_index=0, sink=None,
             verbose=True):
    task = load_task(task_id)
    run_dir = Path(run_dir) if run_dir else None
    run_id = run_dir.name if run_dir else None
    sink = sink or ResultSink(run_dir)

    def traj(name):
        return run_dir / "trajectories" / task_id / f"{name}.jsonl" if run_dir else None

    results = []

    def record(r):
        results.append(r)
        sink.add(r)
        if verbose:
            _print_result(r)

    if policy == "reference":
        for i in range(start_index, start_index + trials):
            r = run_scripted(task, task.reference, policy="reference", trial=i, traj_path=traj(f"reference_{i:02d}"),
                             run_id=run_id)
            record(r)
        return results

    if policy == "controls":
        for c in task.controls:
            r = run_scripted(task, c.calls, policy=f"control:{c.name}", traj_path=traj(f"control_{c.name}"),
                             run_id=run_id)
            r["control_expect_pass"] = c.expect_pass
            r["control_expect_failed"] = sorted(c.expect_failed)
            r["control_ok"] = (r["passed"] is True) if c.expect_pass else (
                r["passed"] is False and set(r["failed_critical"]) == set(c.expect_failed))
            record(r)
        return results

    if policy != "model":
        raise ValueError(f"Unknown policy {policy!r}")
    from harness.agent_loop import run_model_trial
    client = client or make_client()

    def one(i):
        for attempt in range(1, infra_retries + 2):
            name = f"trial_{i:02d}" + (f"_attempt{attempt}" if attempt > 1 else "")
            r = run_model_trial(task, model, client, trial=i, attempt=attempt, traj_path=traj(name), run_id=run_id,
                                effort=effort, max_tokens=max_tokens, show_thinking=show_thinking)
            if r["stop_reason"] != "infra_error" or attempt == infra_retries + 1:
                return r
            if verbose:
                print(f"  [{task_id} trial {i:02d}] infra error, retrying ({r.get('error')})", flush=True)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(one, i) for i in range(start_index, start_index + trials)]
        for fut in as_completed(futures):
            r = fut.result()
            record(r)
    return sorted(results, key=lambda r: r["trial"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", default="all", help=f"task id or 'all'. Tasks: {', '.join(task_ids())}")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--policy", default="model", choices=["model", "reference", "controls"])
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--start-index", type=int, default=0, help="first trial index, for topping up a run")
    ap.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max"],
                    help="omit to use the model default (high for Opus 5)")
    ap.add_argument("--max-tokens", type=int, default=32000)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--no-thinking-display", action="store_true", help="don't request summarized thinking")
    ap.add_argument("--run-name", default=None)
    ap.add_argument("--run-dir", default=None, help="append to an existing run directory")
    args = ap.parse_args(argv)

    tasks = task_ids() if args.task == "all" else [args.task]
    label = args.run_name or (args.policy if args.policy != "model" else args.model)
    run_dir = Path(args.run_dir) if args.run_dir else RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}_{label}"
    run_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "run_id": run_dir.name, "created": datetime.now().isoformat(timespec="seconds"),
        "policy": args.policy, "model": args.model if args.policy == "model" else None, "tasks": tasks,
        "trials": args.trials, "effort": args.effort or "model default", "max_tokens": args.max_tokens,
        "thinking_display": not args.no_thinking_display, "git": _git_info(),
        "fixture": str(DEFAULT_FIXTURE.relative_to(ROOT)), "initial_state_hash": initial_hash(),
        "tool_schema_hash": _sha(json.dumps(TOOLS, sort_keys=True)),
        "prompt_hashes": {t: _sha(load_task(t).prompt) for t in tasks},
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    if config["git"]["dirty"]:
        print("Note: env/, tasks/ or harness/ has uncommitted changes. Commit and tag before final runs.")

    client = make_client() if args.policy == "model" else None
    sink = ResultSink(run_dir)
    print(f"Run {run_dir.name}  policy={args.policy}  model={config['model']}  tasks={tasks}")
    try:
        for t in tasks:
            run_task(t, args.model, policy=args.policy, trials=args.trials, run_dir=run_dir, client=client,
                     effort=args.effort, concurrency=args.concurrency, max_tokens=args.max_tokens,
                     show_thinking=not args.no_thinking_display, start_index=args.start_index, sink=sink)
    finally:
        from harness.report import build_report
        if (run_dir / "results.jsonl").exists():
            report = build_report(run_dir)
            print("\n" + report)
            print(f"Saved to {run_dir}")


if __name__ == "__main__":
    main()
