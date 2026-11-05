"""Task registry. Each task lives in tasks/<task_id>/ with prompt.md, rubric.md, task.py and reference.py."""

import importlib
from dataclasses import dataclass, field
from pathlib import Path

TASKS_DIR = Path(__file__).parent


@dataclass
class Control:
    """A scripted run used to test the grader. Wrong-answer controls must fail on exactly the expected checks;
    alternate-correct controls must pass, proving the grader accepts other valid paths."""
    name: str
    calls: list
    expect_pass: bool = False
    expect_failed: set = field(default_factory=set)
    description: str = ""


@dataclass
class Task:
    id: str
    prompt: str
    max_turns: int
    grade: callable
    reference: list
    controls: list
    target_patients: list


def task_ids():
    return sorted(p.name for p in TASKS_DIR.iterdir() if (p / "task.py").exists())


def load_task(task_id) -> Task:
    if task_id not in task_ids():
        raise ValueError(f"Unknown task {task_id!r}. Available: {task_ids()}")
    mod = importlib.import_module(f"tasks.{task_id}.task")
    ref = importlib.import_module(f"tasks.{task_id}.reference")
    prompt = (TASKS_DIR / task_id / "prompt.md").read_text().strip()
    return Task(id=task_id, prompt=prompt, max_turns=mod.MAX_TURNS, grade=mod.grade, reference=ref.REFERENCE,
                controls=ref.CONTROLS, target_patients=mod.TARGET_PATIENTS)
