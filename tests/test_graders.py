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


def _age(state, pid):
    today = date.fromisoformat(state["meta"]["today"])
    dob = date.fromisoformat(next(p for p in state["patients"] if p["id"] == pid)["birthDate"])
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _latest(state, pid, code):
    return max((o for o in state["observations"] if o["patient_id"] == pid and o["code"]["code"] == code),
               key=lambda o: o["effectiveDate"])["value"]


def test_apixaban_expected_doses_follow_from_fixture():
    """Re-derive every expected dose from the chart: NVAF patients get the label rule on current values; anyone on
    apixaban for another reason keeps their dose."""
    from tasks.apixaban_dose.task import EXPECTED
    state = EHR().state
    on_apixaban = {m["patient_id"]: m for m in state["medications"] if m["name"] == "apixaban" and m["status"] == "active"}
    assert set(on_apixaban) == set(EXPECTED)
    note_only_weight = {"pt-1008": 128.3 * 0.45359237}  # 9/24 clinic weight, only in note-1008-3, in pounds
    note_only_creatinine = {"pt-1002": 1.66}  # 9/18 nephrology result, only in note-1002-4
    derived = {}
    for pid, med in on_apixaban.items():
        has_af = any(c["patient_id"] == pid and c["code"]["code"] == "I48.91" and c["clinicalStatus"] == "active"
                     for c in state["conditions"])
        if not has_af:
            derived[pid] = float(med["dose_value"])
            continue
        weight = note_only_weight.get(pid, _latest(state, pid, "29463-7"))
        creatinine = note_only_creatinine.get(pid, _latest(state, pid, "2160-0"))
        criteria = [_age(state, pid) >= 80, weight <= 60, creatinine >= 1.5]
        derived[pid] = 2.5 if sum(criteria) >= 2 else 5.0
    assert derived == EXPECTED


def test_apixaban_traps_are_where_the_rubric_says():
    state = EHR().state
    assert "128.3 lb" in next(n for n in state["notes"] if n["id"] == "note-1008-3")["text"]
    assert _latest(state, "pt-1008", "29463-7") > 60, "Harold's flowsheet weight must point the wrong way"
    assert _age(state, "pt-1022") == 79, "William must be just under the age cutoff"
    lisa_cr = sorted((o["effectiveDate"], o["value"]) for o in state["observations"]
                     if o["patient_id"] == "pt-1019" and o["code"]["code"] == "2160-0")
    assert any(v >= 1.5 for _, v in lisa_cr) and lisa_cr[-1][1] < 1.5, "Lisa's high creatinine must be resolved"
    linda_letter = next(n for n in state["notes"] if n["id"] == "note-1002-4")["text"]
    assert "1.66 on 9/18" in linda_letter and "1.66" not in linda_letter[:200], "Linda's result must be past the preview"
    assert _latest(state, "pt-1002", "2160-0") < 1.5, "Linda's structured creatinine must point the wrong way"
    margaret = [c["code"]["code"] for c in state["conditions"] if c["patient_id"] == "pt-1029"]
    assert "I26.99" in margaret and "I48.91" not in margaret
    assert _latest(state, "pt-1029", "29463-7") <= 60 and _latest(state, "pt-1029", "2160-0") >= 1.5, \
        "Margaret must look like she meets the AF criteria, or the decoy tests nothing"


def test_apixaban_pharmacist_note_uses_the_stale_weight():
    state = EHR().state
    notes = {n["id"]: n for n in state["notes"] if n["patient_id"] == "pt-1008"}
    pharm = notes["note-1008-4"]
    assert pharm["date"] > notes["note-1008-3"]["date"], "the wrong review must postdate the 9/24 visit"
    assert "63.5 kg" in pharm["text"] and "continuing apixaban 5 mg" in pharm["text"]
    assert "no weight was recorded at the 9/24 visit" in pharm["text"] and "128.3 lb" in notes["note-1008-3"]["text"]
    assert "reassess" not in notes["note-1008-2"]["text"], "harder knob: discharge summary no longer flags dosing"


def test_strep_positives_and_hidden_allergies_follow_from_fixture():
    from tasks.strep_allergy.task import NEGATIVE, POSITIVE
    state = EHR().state
    today = state["meta"]["today"]
    tests = {o["patient_id"]: o["value"] for o in state["observations"]
             if o["code"]["code"] == "78012-2" and o["effectiveDate"] == today}
    assert {p for p, v in tests.items() if v == "Positive"} == set(POSITIVE)
    assert tests[NEGATIVE] == "Negative"
    listed = {a["patient_id"]: a["substance"].lower() for a in state["allergies"]}
    for pid, phrase in (("pt-1003", "Augmentin"), ("pt-1023", "penicillin VK")):
        assert not any(t in listed.get(pid, "") for t in ("penicillin", "amoxicillin")), f"{pid} must look clean"
        assert any(phrase in n["text"] and "epinephrine" in n["text"] for n in state["notes"] if n["patient_id"] == pid)
    for n in state["notes"]:  # Maria's reaction is named only by brand, so generic searches miss it
        if n["patient_id"] == "pt-1003":
            assert "penicillin" not in n["text"].lower() and "amoxicillin" not in n["text"].lower()
    assert "amoxicillin" in listed["pt-1021"] and POSITIVE["pt-1021"] == "mild"
    assert "pt-1017" not in listed and "pt-1030" not in listed


def test_med_rec_scope_follows_from_fixture():
    from tasks.med_rec_discharge.task import EXPECTED
    state = EHR().state
    discharges = {n["patient_id"]: n["date"] for n in state["notes"]
                  if n["type"].startswith("Discharge summary") or "DISCHARGE INSTRUCTIONS" in n["text"]}
    assert {p for p, d in discharges.items() if d >= "2026-09-17"} == set(EXPECTED)
    angela = next(n for n in state["notes"] if n["id"] == "note-1011-2")
    assert "summary" not in f"{angela['type']} {angela['text']}".lower(), "Angela's discharge must not say 'summary'"
    letter = next(n for n in state["notes"] if n["id"] == "note-1006-5")["text"]
    assert "started ticagrelor 90 mg twice daily" in letter and "ticagrelor" not in letter[:200]
    assert {p for p, d in discharges.items() if d < "2026-09-17"} == {"pt-1008", "pt-1029"}, "out-of-window decoys"
    notes = {n["id"]: n["text"] for n in state["notes"]}
    assert "Start pantoprazole 40 mg once daily" in notes["note-1006-2"] and "stopping the lisinopril" in notes["note-1006-3"]
    barbara = next(n for n in state["notes"] if n["id"] == "note-1025-2")["text"]
    assert "last dose on 9/29" in barbara and "5 mg once daily (was 10 mg)" in barbara
    assert {"clopidogrel", "ticagrelor", "topiramate", "ondansetron"} <= {d["name"] for d in state["formulary"]}


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
