"""Runs one trial, by a model or by a scripted policy, through the same tool dispatch, logging and grading.

Using one code path for both is the point: when the reference solution passes 10/10 through this file,
it shows the environment, the dispatch and the grader all work, so a model failure can't be blamed on them.
"""

import json
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

from env.store import EHR, hash_state
from env.tools import TOOLS, ToolError, call_tool
from tasks.common import GradingContext

SYSTEM_PROMPT_TEMPLATE = (Path(__file__).parent / "system_prompt.md").read_text().strip()
INVALID_STOPS = {"env_error", "infra_error"}


def system_prompt(ehr):
    return SYSTEM_PROMPT_TEMPLATE.format(today=ehr.today)


# ---- tool dispatch ----------------------------------------------------------------------------

@dataclass
class ToolOutcome:
    content: str
    is_error: bool
    status: str        # ok | validation_error | env_error
    latency_ms: float
    traceback: str | None = None


def execute(ehr, name, args):
    t0 = time.perf_counter()
    try:
        result = call_tool(ehr, name, args)
        content, is_error, status, tb = json.dumps(result, ensure_ascii=False), False, "ok", None
    except ToolError as e:
        content, is_error, status, tb = f"Error: {e}", True, "validation_error", None
    except Exception:  # noqa: BLE001  any other exception is our bug, never the model's
        content, is_error, status, tb = f"Internal error in tool {name}.", True, "env_error", traceback.format_exc()
    return ToolOutcome(content, is_error, status, round((time.perf_counter() - t0) * 1000, 2), tb)


# ---- logging ----------------------------------------------------------------------------------

class TrajectoryLog:
    def __init__(self, path: Path | None):
        self.path = path
        self.events = []
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("")

    def write(self, event_type, **data):
        event = {"type": event_type, "t": round(time.time(), 3), **data}
        self.events.append(event)
        if self.path:
            with self.path.open("a") as f:
                f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")


# ---- grading + result -------------------------------------------------------------------------

def finish_trial(task, ehr, initial, start_hash, stop_reason, log, meta, stats):
    valid = stop_reason not in INVALID_STOPS
    ctx = GradingContext(initial=initial, final=ehr.state, submission=ehr.submission, stop_reason=stop_reason)
    grade = task.grade(ctx)
    log.write("grade", **grade.to_dict())
    end_hash = ehr.state_hash()
    log.write("end", stop_reason=stop_reason, valid=valid, end_hash=end_hash, write_log=ehr.write_log,
              submission=ehr.submission)
    return {
        **meta,
        "start_hash": start_hash, "end_hash": end_hash, "stop_reason": stop_reason, "valid": valid,
        "passed": grade.passed if valid else None, "score": grade.score if valid else None,
        "failed_critical": grade.failed_checks(), "failed_diagnostic": grade.failed_checks(critical_only=False),
        "submission": ehr.submission, "writes": len(ehr.write_log), **stats,
        "trajectory": str(log.path) if log.path else None,
    }


# ---- scripted policy (reference solutions and grader controls) -------------------------------

def run_scripted(task, calls, *, policy="reference", trial=0, traj_path=None, run_id=None):
    ehr = EHR(task.fixture)
    initial, start_hash = ehr.snapshot(), ehr.state_hash()
    log = TrajectoryLog(traj_path)
    meta = {"run_id": run_id, "task": task.id, "policy": policy, "model": None, "trial": trial, "attempt": 1}
    log.write("meta", **meta, start_hash=start_hash, prompt=task.prompt)
    status_counts, stop_reason = {"ok": 0, "validation_error": 0, "env_error": 0}, "end_turn"
    t0 = time.time()
    for name, args in calls:
        out = execute(ehr, name, args)
        status_counts[out.status] += 1
        log.write("tool_call", name=name, input=args, status=out.status, result=out.content,
                  latency_ms=out.latency_ms, traceback=out.traceback)
        if out.status == "env_error":
            stop_reason = "env_error"
            break
        if name == "submit" and not out.is_error:
            stop_reason = "submitted"
            break
    stats = {"turns": len(calls), "tool_calls": sum(status_counts.values()), "tool_status": status_counts,
             "usage": None, "wall_s": round(time.time() - t0, 2)}
    return finish_trial(task, ehr, initial, start_hash, stop_reason, log, meta, stats)


def initial_hash(fixture=None):
    return hash_state((EHR(fixture) if fixture else EHR()).state)


def tools_for_api():
    tools = json.loads(json.dumps(TOOLS))
    tools[-1]["cache_control"] = {"type": "ephemeral"}  # cache the whole tool block across turns
    return tools
