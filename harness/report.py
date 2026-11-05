"""Summarize a run: pass rates with Wilson intervals, failure breakdown, triage labels, tool use, cost.

  python -m harness.report runs/<run_id>
"""

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

BAND = (0.2, 0.7)

# USD per million tokens (input, output). Cache reads and writes are billed as multiples of input.
# Estimates only; check https://platform.claude.com/docs/en/about-claude/pricing before quoting.
PRICES = {"claude-opus-5": (5.0, 25.0, 0.10), "claude-opus-5-5": (4.0, 20.0, 0.05),
          "claude-sonnet-5-5": (2.0, 10.0, 0.05)}
CACHE_WRITE_MULT = 1.25


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def latest_attempts(results):
    """Keep one result per (task, policy, trial): the last attempt."""
    keep = {}
    for r in results:
        keep[(r["task"], r["policy"], r["trial"])] = r
    return list(keep.values())


def triage_labels(run_dir):
    labels = {}
    for t in load_jsonl(Path(run_dir) / "triage.jsonl"):
        final = t.get("human_label") or t.get("llm_category")
        labels[(t["task"], t["trial"], t["kind"])] = {"label": final, "confirmed": bool(t.get("human_label"))}
    return labels


def cost(model, usage):
    if model not in PRICES or not usage:
        return None
    pin, pout, cache_read_mult = PRICES[model]
    return (usage["input_tokens"] * pin + usage["output_tokens"] * pout
            + usage["cache_read_input_tokens"] * pin * cache_read_mult
            + usage["cache_creation_input_tokens"] * pin * CACHE_WRITE_MULT) / 1e6


def pct(x):
    return f"{100 * x:.0f}%"


def build_report(run_dir):
    run_dir = Path(run_dir)
    config = json.loads((run_dir / "config.json").read_text()) if (run_dir / "config.json").exists() else {}
    results = latest_attempts(load_jsonl(run_dir / "results.jsonl"))
    labels = triage_labels(run_dir)
    lines = [f"# Run report {run_dir.name}", ""]
    if config:
        git = config.get("git", {})
        lines += [f"Policy {config.get('policy')}, model {config.get('model')}, effort {config.get('effort')}, "
                  f"commit {str(git.get('commit'))[:10]}{' (dirty)' if git.get('dirty') else ''}, "
                  f"initial state hash {config.get('initial_state_hash')}.", ""]

    controls = [r for r in results if r["policy"].startswith("control:")]
    trials = [r for r in results if not r["policy"].startswith("control:")]

    if trials:
        by_task = defaultdict(list)
        for r in trials:
            by_task[r["task"]].append(r)
        lines += ["## Pass rates", "",
                  "| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |",
                  "|---|---|---|---|---|---|---|---|"]
        for task, rs in sorted(by_task.items()):
            valid = [r for r in rs if r["valid"]]
            k, n = sum(r["passed"] for r in valid), len(valid)
            lo, hi = wilson(k, n)
            rate = k / n if n else 0
            mean_score = sum(r["score"] for r in valid) / n if n else 0
            band = "n/a" if rs[0]["policy"] != "model" else ("yes" if n and BAND[0] <= rate <= BAND[1] else "no")
            lines.append(f"| {task} | {n} | {k} | {pct(rate)} | {pct(lo)} to {pct(hi)} | {mean_score:.2f} | {band} | "
                         f"{len(rs) - n} |")

        lines += ["", "## Why trials failed", ""]
        for task, rs in sorted(by_task.items()):
            failed = [r for r in rs if r["valid"] and not r["passed"]]
            invalid = [r for r in rs if not r["valid"]]
            if not failed and not invalid:
                continue
            lines.append(f"**{task}**")
            checks = Counter(c for r in failed for c in r["failed_critical"])
            for c, cnt in checks.most_common():
                lines.append(f"- failed check `{c}` in {cnt} trial(s)")
            tri = Counter()
            unconfirmed = 0
            for r in failed:
                lab = labels.get((task, r["trial"], "failure"))
                tri[lab["label"] if lab else "untriaged"] += 1
                unconfirmed += bool(lab and not lab["confirmed"])
            if any(k != "untriaged" for k in tri):
                lines.append("- triage: " + ", ".join(f"{k} {v}" for k, v in tri.most_common())
                             + (f" ({unconfirmed} not yet confirmed by a human)" if unconfirmed else ""))
            for r in invalid:
                lines.append(f"- trial {r['trial']:02d} INVALID ({r['stop_reason']}), excluded from the pass rate")
            lines.append("")

        audits = [(k, v) for k, v in labels.items() if k[2] == "pass_audit"]
        if audits:
            lines += ["## Pass audit", ""]
            for (task, trial, _), v in sorted(audits):
                lines.append(f"- {task} trial {trial:02d}: {v['label']}{'' if v['confirmed'] else ' (unconfirmed)'}")
            lines.append("")

        lines += ["## Episodes", "", "| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | "
                  "Env errors | Distinct end states |", "|---|---|---|---|---|---|---|"]
        for task, rs in sorted(by_task.items()):
            stops = Counter(r["stop_reason"] for r in rs)
            n = len(rs)
            val_err = sum(r["tool_status"].get("validation_error", 0) for r in rs) / n
            env_err = sum(r["tool_status"].get("env_error", 0) for r in rs)
            ends = len({r["end_hash"] for r in rs})
            lines.append(f"| {task} | {', '.join(f'{k} {v}' for k, v in stops.items())} | "
                         f"{sum(r['turns'] for r in rs) / n:.1f} | {sum(r['tool_calls'] for r in rs) / n:.1f} | "
                         f"{val_err:.2f} | {env_err} | {ends} |")
        starts = {r["start_hash"] for r in trials}
        lines += ["", f"Every trial started from state hash {', '.join(sorted(starts))}"
                      + (" (identical)." if len(starts) == 1 else " (MISMATCH, investigate)."), ""]

        costs = [cost(r["model"], r.get("usage")) for r in trials if r.get("usage")]
        costs = [c for c in costs if c is not None]
        if costs:
            lines += [f"Estimated API cost ${sum(costs):.2f} across {len(costs)} trials "
                      f"(${sum(costs) / len(costs):.2f} per trial). Estimate only.", ""]

    if controls:
        lines += ["## Grader controls", "", "| Task | Control | Expected | Got | OK |", "|---|---|---|---|---|"]
        for r in sorted(controls, key=lambda r: (r["task"], r["policy"])):
            exp = "pass" if r["control_expect_pass"] else "fail on " + ", ".join(r["control_expect_failed"])
            got = "pass" if r["passed"] else "fail on " + ", ".join(sorted(r["failed_critical"]))
            lines.append(f"| {r['task']} | {r['policy'].split(':', 1)[1]} | {exp} | {got} | "
                         f"{'yes' if r['control_ok'] else 'NO'} |")
        lines.append("")

    report = "\n".join(lines)
    (run_dir / "report.md").write_text(report + "\n")
    return report


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m harness.report runs/<run_id>")
    print(build_report(sys.argv[1]))
