"""Shared grading machinery. Graders look only at chart state (initial vs final) and the submission,
never at the transcript, so a correct outcome reached by any valid path gets full credit."""

from collections import Counter
from dataclasses import asdict, dataclass, field

PATIENT_COLLECTIONS = ("conditions", "medications", "allergies", "observations", "notes", "orders")

# Equivalent ways of writing the same schedule.
FREQ_EQUIV = {"every 12 hours": "twice daily", "every 8 hours": "three times daily", "every 24 hours": "once daily"}


@dataclass
class Check:
    name: str
    passed: bool
    critical: bool = True
    detail: str = ""


@dataclass
class GradeResult:
    passed: bool
    score: float
    checks: list = field(default_factory=list)

    def failed_checks(self, critical_only=True):
        return [c.name for c in self.checks if not c.passed and (c.critical or not critical_only)]

    def to_dict(self):
        return {"passed": self.passed, "score": round(self.score, 4), "checks": [asdict(c) for c in self.checks],
                "failed_critical": self.failed_checks()}


@dataclass
class GradingContext:
    initial: dict
    final: dict
    submission: dict | None
    stop_reason: str  # submitted | end_turn | turn_limit | token_limit | ...


def finalize(checks, score=None):
    critical = [c for c in checks if c.critical]
    passed = all(c.passed for c in critical)
    if score is None:
        score = sum(c.passed for c in critical) / len(critical)
    return GradeResult(passed=passed, score=1.0 if passed else min(score, 0.99), checks=checks)


# ---- state helpers ----------------------------------------------------------------------------

def norm_freq(freq):
    return FREQ_EQUIV.get(freq, freq)


def med_key(m):
    return (m["name"], round(float(m["dose_value"]), 4), m["dose_unit"], norm_freq(m["frequency"]))


def fmt_key(k):
    return f"{k[0]} {k[1]:g} {k[2]} {k[3]}"


def active_meds(state, pid):
    return [m for m in state["medications"] if m["patient_id"] == pid and m["status"] == "active"]


def new_records(ctx, collection, pid=None):
    before = {r["id"] for r in ctx.initial[collection]}
    return [r for r in ctx.final[collection] if r["id"] not in before and (pid is None or r["patient_id"] == pid)]


def formulary(state):
    return {d["id"]: d for d in state["formulary"]}


def patient_slice(state, pid):
    out = {"patient": next(p for p in state["patients"] if p["id"] == pid)}
    for c in PATIENT_COLLECTIONS:
        out[c] = sorted((r for r in state[c] if r["patient_id"] == pid), key=lambda r: r["id"])
    return out


def changed_patients(ctx):
    pids = [p["id"] for p in ctx.final["patients"]]
    return [pid for pid in pids if patient_slice(ctx.initial, pid) != patient_slice(ctx.final, pid)]


def multiset_jaccard(a: Counter, b: Counter):
    union = sum((a | b).values())
    return 1.0 if union == 0 else sum((a & b).values()) / union


# ---- reusable checks --------------------------------------------------------------------------

def completed_check(ctx):
    ok = ctx.stop_reason in ("submitted", "end_turn")
    return Check("completed", ok, detail=f"stop_reason={ctx.stop_reason}")


def untouched_check(ctx, allowed):
    others = [pid for pid in changed_patients(ctx) if pid not in allowed]
    return Check("no_changes_to_other_patients", not others,
                 detail="changed: " + ", ".join(others) if others else "only the intended patient(s) changed")


def submitted_check(ctx):
    return Check("called_submit", ctx.submission is not None, critical=False)
