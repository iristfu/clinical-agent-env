"""The environment is deterministic, resets cleanly, and never crashes on bad input."""

import json
import random

import pytest

from env.fixtures.build_panel import build
from env.store import DEFAULT_FIXTURE, EHR
from env.tools import TOOLS, ToolError, call_tool


def test_fixture_matches_builder():
    assert json.loads(DEFAULT_FIXTURE.read_text()) == build(), "run: python -m env.fixtures.build_panel"


def test_fresh_instances_share_a_start_hash():
    assert len({EHR().state_hash() for _ in range(5)}) == 1


def test_reset_restores_start_state():
    ehr = EHR()
    start = ehr.state_hash()
    call_tool(ehr, "place_lab_order", {"patient_id": "pt-1001", "test": "A1c"})
    call_tool(ehr, "discontinue_medication", {"medication_id": "med-1001-01", "reason": "x"})
    assert ehr.state_hash() != start
    ehr.reset()
    assert ehr.state_hash() == start and ehr.write_log == [] and ehr.submission is None


def test_new_ids_are_deterministic():
    ids = []
    for _ in range(2):
        ehr = EHR()
        ids.append(call_tool(ehr, "place_lab_order", {"patient_id": "pt-1001", "test": "A1c"})["created"]["id"])
    assert ids == ["ord-new-001", "ord-new-001"]


@pytest.mark.parametrize("name,args,fragment", [
    ("get_patient", {"patient_id": "pt-9999"}, "No patient"),
    ("get_patient", {}, "Missing required"),
    ("list_medications", {"patient_id": "pt-1001", "status": "current"}, "Allowed values"),
    ("list_conditions", {"patient_id": "pt-1001", "verbose": True}, "Unknown parameter"),
    ("get_observations", {"patient_id": "pt-1001", "since": "Jan 2025"}, "YYYY-MM-DD"),
    ("search_notes", {}, "patient_id, a query"),
    ("read_note", {"note_id": "note-0000-1"}, "No note"),
    ("place_medication_order", {"patient_id": "pt-1012", "medication": "metoprolol", "dose_value": 50,
                                "dose_unit": "mg", "frequency": "once daily"}, "more than one"),
    ("place_medication_order", {"patient_id": "pt-1012", "medication": "unobtainium", "dose_value": 50,
                                "dose_unit": "mg", "frequency": "once daily"}, "not on the formulary"),
    ("discontinue_medication", {"medication_id": "med-1007-01", "reason": "x"}, "not active"),
    ("update_medication", {"medication_id": "med-1008-01", "reason": "x"}, "at least one"),
    ("place_lab_order", {"patient_id": "pt-1001", "test": "vibes"}, "did not match"),
    ("nonexistent_tool", {}, "Unknown tool"),
])
def test_invalid_requests_return_clear_tool_errors(name, args, fragment):
    with pytest.raises(ToolError, match=fragment):
        call_tool(EHR(), name, args)


def test_note_previews_say_they_are_truncated():
    ehr = EHR()
    first = call_tool(ehr, "search_notes", {"patient_id": "pt-1003"})
    assert first["has_more"] and "page=2" in first["note"], "the model must be told there is a second page"
    assert all(n["note_id"] != "note-1003-1" for n in first["results"]), "strep trap: ED note sits on page 2"
    res = call_tool(ehr, "search_notes", {"patient_id": "pt-1003", "page": 2})
    ed_note = next(n for n in res["results"] if n["note_id"] == "note-1003-1")
    assert "preview truncated" in ed_note["preview"] and "Augmentin" not in ed_note["preview"]


def test_pagination_tells_the_model_there_is_more():
    res = call_tool(EHR(), "list_patients", {})
    assert res["has_more"] and "page=2" in res["note"] and res["total"] == 30


def test_observation_synonyms():
    ehr = EHR()
    for q in ("A1c", "hba1c", "HbA1c", "4548-4", "glycated hemoglobin"):
        assert call_tool(ehr, "get_observations", {"patient_id": "pt-1001", "query": q})["total"] == 2


def _random_value(rng, spec):
    pool = ["pt-1001", "pt-1012", "", "zzz", "med-1008-01", "note-1003-1", "2026-01-01", "A1c", "aspirin",
            0, -1, 2.5, 10**9, None, True, [], ["pt-1001"], {"a": 1}, "once daily", "mg", "all"]
    if "enum" in spec and rng.random() < 0.5:
        return rng.choice(spec["enum"])
    return rng.choice(pool)


def test_fuzz_tools_never_raise_anything_but_tool_error():
    """2,000 random calls with junk arguments. Any exception other than ToolError would be an env bug that could
    end a trial for reasons that have nothing to do with the model."""
    rng = random.Random(1234)
    ehr = EHR()
    for _ in range(2000):
        tool = rng.choice(TOOLS)
        props = tool["input_schema"]["properties"]
        args = {k: _random_value(rng, v) for k, v in props.items() if rng.random() < 0.7}
        if rng.random() < 0.05:
            args["bogus"] = 1
        try:
            call_tool(ehr, tool["name"], args)
        except ToolError:
            pass
        if tool["name"] == "submit":
            ehr.submission = None
