"""Print one trial's trajectory in a readable form.

  python scripts/view_trajectory.py runs/<run_id>/trajectories/strep_allergy/trial_03.jsonl
  python scripts/view_trajectory.py <file> --full      # do not shorten tool results
"""

import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    limit = None if args.full else 400
    cut = lambda text: text if limit is None or len(text) <= limit else text[:limit] + " ..."
    for line in open(args.path):
        e = json.loads(line)
        kind = e["type"]
        if kind == "meta":
            print(f"TASK {e['task']}  trial {e['trial']}  model {e['model']}\nPROMPT: {e['prompt']}\n")
        elif kind == "assistant":
            for block in e["content"]:
                if block.get("type") == "text" and block["text"].strip():
                    print(f"[turn {e['turn']}] MODEL: {block['text'].strip()}")
                elif block.get("type") == "thinking" and block.get("thinking", "").strip():
                    print(f"[turn {e['turn']}] THINKING: {cut(block['thinking'].strip())}")
        elif kind == "tool_call":
            print(f"[turn {e['turn']}]   -> {e['name']} {json.dumps(e['input'])}")
            print(f"      {e['status']}: {cut(e['result'])}")
        elif kind == "grade":
            print(f"\nGRADE passed={e.get('passed')} failed_critical={e.get('failed_critical')}")
        elif kind == "end":
            print(f"END {e.get('stop_reason')}")


if __name__ == "__main__":
    main()
