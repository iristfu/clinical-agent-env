from tasks import Control

P = "pt-1012"
LISINOPRIL, TARTRATE, HCTZ, ATORVA, METFORMIN, ASPIRIN, OMEPRAZOLE = (f"med-1012-0{i}" for i in range(1, 8))
SUBMIT = ("submit", {"summary": "Done."})


def stop(med_id, reason):
    return ("discontinue_medication", {"medication_id": med_id, "reason": reason})


def rx(name, dose, freq):
    return ("place_medication_order", {"patient_id": P, "medication": name, "dose_value": dose, "dose_unit": "mg",
                                       "frequency": freq})


CORE = [
    stop(LISINOPRIL, "ACE inhibitor cough, switched to ARB at discharge"),
    rx("losartan", 100, "once daily"),
    stop(HCTZ, "Hyponatremia"),
    stop(TARTRATE, "Changed to metoprolol succinate ER"),
    rx("metoprolol succinate ER", 50, "once daily"),
    ("update_medication", {"medication_id": METFORMIN, "dose_value": 1000, "reason": "Increased at discharge, A1c 8.4"}),
    rx("empagliflozin", 10, "once daily"),
]

REFERENCE = [
    ("search_patients", {"name": "Denise Carter", "birth_date": "1962-05-09"}),
    ("list_medications", {"patient_id": P}),
    ("search_notes", {"patient_id": P}),
    ("read_note", {"note_id": "note-1012-2"}),
    ("read_note", {"note_id": "note-1012-3"}),
    ("read_note", {"note_id": "note-1012-4"}),
    *CORE,
    ("submit", {"summary": "Applied 9/28 discharge changes, then the 9/30 phone note (losartan 100 mg daily) and the "
                           "10/1 phone note (empagliflozin 10 mg daily started after the savings card)."}),
]

CONTROLS = [
    Control("do_nothing", [SUBMIT], expect_failed={"active_list_matches_expected"}),
    Control("discharge_summary_only",
            [stop(LISINOPRIL, "cough"), rx("losartan", 50, "once daily"), stop(HCTZ, "hyponatremia"),
             stop(TARTRATE, "switch"), rx("metoprolol succinate ER", 50, "once daily"),
             ("update_medication", {"medication_id": METFORMIN, "dose_value": 1000, "reason": "A1c"}),
             rx("empagliflozin", 10, "once daily"), SUBMIT],
            expect_failed={"active_list_matches_expected"},
            description="Follows the discharge summary and never reads the later phone notes."),
    Control("stopped_at_9_30_note", [c for c in CORE if c != rx("empagliflozin", 10, "once daily")] + [SUBMIT],
            expect_failed={"active_list_matches_expected"},
            description="Applies the 9/30 phone note but misses the 10/1 note that restarts empagliflozin."),
    Control("forgot_to_stop_tartrate", [c for c in CORE if c != stop(TARTRATE, "Changed to metoprolol succinate ER")]
            + [SUBMIT], expect_failed={"active_list_matches_expected"}),
    Control("swapped_to_metformin_er",
            [*CORE[:-1], stop(METFORMIN, "switch to ER"), rx("metformin ER", 1000, "twice daily"), SUBMIT],
            expect_failed={"active_list_matches_expected"}),
    Control("continued_completed_cefpodoxime", [*CORE, rx("cefpodoxime", 200, "twice daily"), SUBMIT],
            expect_failed={"active_list_matches_expected"},
            description="Copies the discharge antibiotic onto the active list although the course ended 9/30."),
    Control("kept_inpatient_pantoprazole", [*CORE, stop(OMEPRAZOLE, "changed to pantoprazole in hospital"),
                                            rx("pantoprazole", 40, "once daily"), SUBMIT],
            expect_failed={"active_list_matches_expected"},
            description="Carries the hospital formulary substitution home instead of resuming omeprazole."),
    Control("alt_correct_documents_completed_course",
            [*CORE, ("place_medication_order", {"patient_id": P, "medication": "cefpodoxime", "dose_value": 200,
                                                "dose_unit": "mg", "frequency": "twice daily", "duration_days": 5}),
             stop("med-new-004", "Course completed 9/30"), SUBMIT],
            expect_pass=True, description="Records the antibiotic course and then marks it stopped, leaving the "
                                          "active list correct."),
    Control("alt_correct_two_step_losartan",
            [stop(LISINOPRIL, "cough"), rx("losartan", 50, "once daily"),
             ("update_medication", {"medication_id": "med-new-001", "dose_value": 100, "reason": "9/30 phone note"}),
             stop(HCTZ, "hyponatremia"), stop(TARTRATE, "switch"), rx("metoprolol succinate ER", 50, "every 24 hours"),
             ("update_medication", {"medication_id": METFORMIN, "dose_value": 1000, "frequency": "every 12 hours",
                                    "reason": "discharge"}),
             rx("empagliflozin", 10, "once daily"), stop("med-new-003", "9/30 phone note: not filled"),
             rx("empagliflozin", 10, "every 24 hours"),
             SUBMIT],
            expect_pass=True, description="Follows each source in date order: discharge losartan dose then the "
                                          "9/30 increase, empagliflozin started, stopped (9/30) and restarted "
                                          "(10/1), with equivalent frequency spellings."),
]
