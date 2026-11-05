"""Failure attribution: a first-pass label from Claude for every failed trial, then human confirmation.

  python -m harness.triage runs/<run_id>                 # label failures, audit 2 passes per task
  python -m harness.triage runs/<run_id> --audit-passes 0
  python -m harness.triage runs/<run_id> --review        # step through labels, accept or correct each

Labels land in runs/<run_id>/triage.jsonl. The report uses a human label when present, otherwise the LLM label
marked as unconfirmed. The LLM sees the task rubric, so it knows the intended answer and the planted traps.
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

from harness.report import latest_attempts, load_jsonl
from harness.run import make_client
from tasks import TASKS_DIR

TAXONOMY = {
    "model_info_gathering": "Model fault. Never looked where the deciding fact was (for example never read the note "
                            "that held it), or stopped searching too early.",
    "model_reasoning": "Model fault. Found the relevant information but drew the wrong clinical conclusion.",
    "model_coverage": "Model fault. In a multi-item task, handled some items correctly but skipped or mishandled others.",
    "model_execution": "Model fault. Right decision, wrong action, such as the wrong patient, wrong formulary item, "
                       "wrong frequency, or leaving the old order active.",
    "model_gave_up": "Model fault. Ran out of turns or tokens, refused, or ended without finishing.",
    "env_bug": "Environment fault. A tool returned wrong, misleading or silently incomplete data, or behaved "
               "differently from its description.",
    "grader_false_negative": "Grader fault. The final chart is clinically correct and consistent with the prompt, "
                             "but the grader failed it.",
    "task_ambiguity": "Task fault. The prompt or chart data reasonably supports what the model did.",
}
PASS_AUDIT = {
    "pass_right_reason": "The model reached the correct outcome for the reasons the rubric describes.",
    "pass_wrong_reason": "The outcome is correct but the model's stated reasoning is wrong or it got there by luck.",
}
MODEL_FAULT = {k for k in TAXONOMY if k.startswith("model_")}


def condense(traj_path, limit=500):
    out = []
    for e in load_jsonl(traj_path):
        if e["type"] == "meta":
            out.append(f"PROMPT: {e['prompt']}")
        elif e["type"] == "assistant":
            for b in e["content"]:
                if b["type"] == "thinking" and b.get("thinking"):
                    out.append(f"[turn {e['turn']}] THINKING (summary): {b['thinking'][:800]}")
                elif b["type"] == "text" and b.get("text"):
                    out.append(f"[turn {e['turn']}] SAID: {b['text'][:800]}")
        elif e["type"] == "tool_call":
            res = (e.get("result") or "")[:limit]
            out.append(f"CALL {e['name']}({json.dumps(e['input'])}) -> [{e['status']}] {res}")
        elif e["type"] == "end":
            out.append(f"END stop_reason={e['stop_reason']} submission={json.dumps(e.get('submission'))}")
        elif e["type"] == "grade":
            for c in e["checks"]:
                out.append(f"CHECK {'PASS' if c['passed'] else 'FAIL'} {'(critical)' if c['critical'] else ''} "
                           f"{c['name']}: {c['detail']}")
    return "\n".join(out)


def build_prompt(task_id, transcript, kind):
    rubric = (TASKS_DIR / task_id / "rubric.md").read_text()
    labels = PASS_AUDIT if kind == "pass_audit" else TAXONOMY
    question = ("This trial PASSED. Decide whether it passed for the right reason."
                if kind == "pass_audit" else
                "This trial FAILED. Decide why. Be skeptical of the environment and grader as well as the model: "
                "if a tool response was misleading or the final chart is actually clinically fine, say so.")
    return (f"You are auditing one trial of an LLM agent working in a mock EHR.\n\n<rubric>\n{rubric}\n</rubric>\n\n"
            f"<trajectory>\n{transcript}\n</trajectory>\n\n{question}\n\nCategories:\n"
            + "\n".join(f"- {k}: {v}" for k, v in labels.items())
            + "\n\nReply with only a JSON object inside <json></json> tags, with keys category (one of the "
              "categories), evidence (two or three sentences citing specific calls or turns), and confidence "
              "(high, medium or low).")


def ask(client, model, prompt):
    resp = client.messages.create(model=model, max_tokens=8000, messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in resp.content if b.type == "text")
    m = re.search(r"<json>(.*?)</json>", text, re.S) or re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(m.group(1) if m.lastindex else m.group(0))
    except Exception:  # noqa: BLE001
        return {"category": "unparsed", "evidence": text[:500], "confidence": "low"}


def write_all(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def label(run_dir, model, audit_passes, seed=0):
    results = [r for r in latest_attempts(load_jsonl(run_dir / "results.jsonl"))
               if r["policy"] == "model" and r["valid"]]
    path = run_dir / "triage.jsonl"
    rows = load_jsonl(path)
    done = {(r["task"], r["trial"], r["kind"]) for r in rows}
    todo = [(r, "failure") for r in results if not r["passed"]]
    rng = random.Random(seed)
    for task in sorted({r["task"] for r in results}):
        passes = sorted((r for r in results if r["task"] == task and r["passed"]), key=lambda r: r["trial"])
        todo += [(r, "pass_audit") for r in rng.sample(passes, min(audit_passes, len(passes)))]
    todo = [(r, k) for r, k in todo if (r["task"], r["trial"], k) not in done]
    if not todo:
        print("Nothing new to triage.")
        return
    client = make_client()
    for r, kind in todo:
        verdict = ask(client, model, build_prompt(r["task"], condense(r["trajectory"]), kind))
        row = {"task": r["task"], "trial": r["trial"], "kind": kind, "failed_critical": r["failed_critical"],
               "llm_category": verdict.get("category"), "model_fault": verdict.get("category") in MODEL_FAULT,
               "evidence": verdict.get("evidence"), "confidence": verdict.get("confidence"), "triage_model": model,
               "trajectory": r["trajectory"], "human_label": None, "human_note": ""}
        rows.append(row)
        write_all(path, rows)
        print(f"  {r['task']} trial {r['trial']:02d} [{kind}] -> {row['llm_category']} ({row['confidence']})")
    print(f"Wrote {path}. Next: python -m harness.triage {run_dir} --review")


def review(run_dir):
    path = run_dir / "triage.jsonl"
    rows = load_jsonl(path)
    pending = [r for r in rows if not r.get("human_label")]
    print(f"{len(pending)} label(s) to review. Enter accepts, a category name overrides, s skips, q quits.\n")
    for r in pending:
        options = PASS_AUDIT if r["kind"] == "pass_audit" else TAXONOMY
        print(f"--- {r['task']} trial {r['trial']:02d} [{r['kind']}]  failed: {r['failed_critical']}")
        print(f"LLM says {r['llm_category']} ({r['confidence']}). {r['evidence']}")
        print(f"Trajectory: {r['trajectory']}")
        while True:
            ans = input(f"[{r['llm_category']}] > ").strip()
            if ans == "q":
                write_all(path, rows)
                return
            if ans == "s":
                break
            choice = ans or r["llm_category"]
            if choice in options:
                r["human_label"] = choice
                r["human_note"] = input("note (optional) > ").strip()
                write_all(path, rows)
                break
            print(f"Pick one of: {', '.join(options)}")
    write_all(path, rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--model", default="claude-opus-5-5", help="triage model, ideally not the model under test")
    ap.add_argument("--audit-passes", type=int, default=2, help="passing trials per task to audit")
    ap.add_argument("--review", action="store_true")
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    if not (run_dir / "results.jsonl").exists():
        sys.exit(f"No results.jsonl in {run_dir}")
    review(run_dir) if args.review else label(run_dir, args.model, args.audit_passes)


if __name__ == "__main__":
    main()
