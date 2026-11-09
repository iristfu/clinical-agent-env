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
    note_only_a1c = {"pt-1020": "2026-08-05"}  # outside A1c documented only in note-1020-2
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
        if pid in note_only_a1c:
            a1c_dates.append(date.fromisoformat(note_only_a1c[pid]))
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


def test_panel_outside_a1c_is_only_in_the_note():
    state = EHR().state
    note = next(n for n in state["notes"] if n["id"] == "note-1020-2")
    assert "2026-08-05" in note["text"] and "A1c 7.0%" in note["text"]
    assert "A1c" not in note["text"][:200], "the result should sit past the search preview"
    structured = [o["effectiveDate"] for o in state["observations"]
                  if o["patient_id"] == "pt-1020" and o["code"]["code"] in ("4548-4", "17856-6")]
    assert max(structured) < "2026-04-01", "the trap depends on the structured A1c history looking overdue"


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


def test_apixaban_pharmacist_note_uses_the_stale_weight():
    state = EHR().state
    notes = {n["id"]: n for n in state["notes"] if n["patient_id"] == "pt-1008"}
    pharm = notes["note-1008-4"]
    assert pharm["date"] > notes["note-1008-3"]["date"], "the wrong review must postdate the 9/24 visit"
    assert "63.5 kg" in pharm["text"] and "continuing apixaban 5 mg" in pharm["text"]
    assert "no weight was recorded at the 9/24 visit" in pharm["text"] and "128.3 lb" in notes["note-1008-3"]["text"]
    assert "reassess" not in notes["note-1008-2"]["text"], "harder knob: discharge summary no longer flags dosing"


def test_strep_allergy_only_in_the_old_note():
    state = EHR().state
    allergies = [a["substance"].lower() for a in state["allergies"] if a["patient_id"] == "pt-1003"]
    assert not any("penicillin" in a or "amoxicillin" in a for a in allergies)
    assert "Augmentin" in next(n for n in state["notes"] if n["id"] == "note-1003-1")["text"]
    # The reaction is named only by brand, so a keyword search for the generic or the class finds nothing.
    for n in state["notes"]:
        if n["patient_id"] == "pt-1003":
            assert "penicillin" not in n["text"].lower() and "amoxicillin" not in n["text"].lower()


def test_med_rec_traps_follow_from_fixture():
    state = EHR().state
    dc = next(n for n in state["notes"] if n["id"] == "note-1012-2")["text"]
    assert "final dose due the evening of 9/30" in dc and state["meta"]["today"] == "2026-10-01"
    assert "pantoprazole 40 mg daily, which was substituted for her home omeprazole" in dc
    later = sorted((n for n in state["notes"] if n["patient_id"] == "pt-1012" and n["date"] > "2026-09-28"),
                   key=lambda n: n["date"])
    assert [n["date"] for n in later] == ["2026-09-30", "2026-10-01"]
    assert "discontinue empagliflozin" in later[0]["text"] and "starting empagliflozin 10 mg once daily" in later[1]["text"]
    names = {d["name"] for d in state["formulary"]}
    assert {"cefpodoxime", "pantoprazole"} <= names, "the model must be able to make the mistake"
