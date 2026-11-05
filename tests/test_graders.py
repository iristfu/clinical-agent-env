"""Graders recognise correct answers (reference + alternate-correct controls) and reject wrong ones (negative
controls fail on exactly the checks we expect). Expected answers are re-derived from the fixture where possible."""

from datetime import date

import pytest

from env.store import EHR
from harness.trial import run_scripted
from tasks import load_task, task_ids

TASKS = task_ids()


@pytest.mark.parametrize("task_id", TASKS)
def test_reference_scores_full_marks(task_id):
    task = load_task(task_id)
    r = run_scripted(task, task.reference)
    assert r["passed"] and r["score"] == 1.0 and r["stop_reason"] == "submitted", r["failed_critical"]
    assert r["tool_status"]["validation_error"] == 0 and r["tool_status"]["env_error"] == 0


@pytest.mark.parametrize("task_id", TASKS)
def test_reference_is_deterministic(task_id):
    task = load_task(task_id)
    runs = [run_scripted(task, task.reference) for _ in range(10)]
    assert len({r["start_hash"] for r in runs}) == 1
    assert len({r["end_hash"] for r in runs}) == 1


CONTROLS = [(t, c) for t in TASKS for c in load_task(t).controls]


@pytest.mark.parametrize("task_id,control", CONTROLS, ids=[f"{t}:{c.name}" for t, c in CONTROLS])
def test_control(task_id, control):
    r = run_scripted(load_task(task_id), control.calls)
    assert r["tool_status"]["env_error"] == 0
    if control.expect_pass:
        assert r["passed"], f"alternate-correct path was rejected: {r['failed_critical']}"
    else:
        assert not r["passed"]
        assert set(r["failed_critical"]) == control.expect_failed


def test_every_task_has_wrong_and_alternate_correct_controls():
    for t in TASKS:
        controls = load_task(t).controls
        assert any(c.expect_pass for c in controls) and sum(not c.expect_pass for c in controls) >= 3, t


# ---- independent re-derivation of expected answers from the fixture ---------------------------

def _derive_panel_expected(state):
    today = date.fromisoformat(state["meta"]["today"])
    cutoff = date(today.year if today.month > 6 else today.year - 1, (today.month - 7) % 12 + 1, today.day)
    t2_codes = ("E11", "44054006")
    note_only_t2 = {"pt-1014"}  # documented in rubric.md: diagnosis lives only in note-1014-1
    expected = set()
    for p in state["patients"]:
        pid = p["id"]
        if p["deceasedDate"]:
            continue
        coded = any(c["patient_id"] == pid and c["clinicalStatus"] == "active" and c["code"]["code"].startswith(t2_codes)
                    for c in state["conditions"])
        if not (coded or pid in note_only_t2):
            continue
        pending = any(o["patient_id"] == pid and o["code"] == "4548-4" and o["status"] == "active"
                      for o in state["orders"])
        a1c_dates = [date.fromisoformat(o["effectiveDate"]) for o in state["observations"]
                     if o["patient_id"] == pid and o["code"]["code"] in ("4548-4", "17856-6")]
        overdue = not a1c_dates or max(a1c_dates) < cutoff
        if overdue and not pending:
            expected.add(pid)
    return expected


def test_panel_expected_set_matches_fixture():
    from tasks.panel_a1c.task import EXPECTED
    assert _derive_panel_expected(EHR().state) == EXPECTED


def test_panel_note_only_patient_really_is_note_only():
    state = EHR().state
    codes = [c["code"]["code"] for c in state["conditions"] if c["patient_id"] == "pt-1014"]
    assert not any(c.startswith("E11") for c in codes)
    note = next(n for n in state["notes"] if n["id"] == "note-1014-1")
    assert "type 2 diabetes" in note["text"]


def test_apixaban_answer_follows_from_fixture():
    state = EHR().state
    p = next(p for p in state["patients"] if p["id"] == "pt-1008")
    today = date.fromisoformat(state["meta"]["today"])
    dob = date.fromisoformat(p["birthDate"])
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    weight_kg = 128.3 * 0.45359237  # from note-1008-3, the only current weight
    note = next(n for n in state["notes"] if n["id"] == "note-1008-3")
    assert "128.3 lb" in note["text"]
    creat = max((o for o in state["observations"] if o["patient_id"] == "pt-1008" and o["code"]["code"] == "2160-0"),
                key=lambda o: o["effectiveDate"])["value"]
    criteria = [age >= 80, weight_kg <= 60, creat >= 1.5]
    assert criteria == [True, True, False]
    flowsheet = max((o for o in state["observations"] if o["patient_id"] == "pt-1008" and o["code"]["code"] == "29463-7"),
                    key=lambda o: o["effectiveDate"])
    assert flowsheet["value"] > 60, "the trap depends on the flowsheet weight being above 60 kg"
    assert all(o["value"] < 1.5 for o in state["observations"]
               if o["patient_id"] == "pt-1008" and o["code"]["code"] == "2160-0"), "no creatinine path to 2 of 3"


def test_strep_allergy_only_in_the_old_note():
    state = EHR().state
    allergies = [a["substance"].lower() for a in state["allergies"] if a["patient_id"] == "pt-1003"]
    assert not any("penicillin" in a or "amoxicillin" in a for a in allergies)
    assert "amoxicillin" in next(n for n in state["notes"] if n["id"] == "note-1003-1")["text"]
