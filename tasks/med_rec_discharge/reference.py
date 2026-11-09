from tasks import Control

D, M, B, A = "pt-1012", "pt-1006", "pt-1025", "pt-1011"
LISINOPRIL, TARTRATE, HCTZ, ATORVA, METFORMIN, ASPIRIN, OMEPRAZOLE = (f"med-1012-0{i}" for i in range(1, 8))
M_METOPROLOL = "med-1006-03"
B_LISINOPRIL = "med-1025-02"
SUBMIT = ("submit", {"summary": "Done.", "patient_ids": [D, M, B, A]})


def stop(med_id, reason):
    return ("discontinue_medication", {"medication_id": med_id, "reason": reason})


def rx(name, dose, freq, pid=D):
    return ("place_medication_order", {"patient_id": pid, "medication": name, "dose_value": dose, "dose_unit": "mg",
                                       "frequency": freq})


def change(med_id, dose, reason, **extra):
    return ("update_medication", {"medication_id": med_id, "dose_value": dose, "reason": reason, **extra})


# Denise Carter: 9/28 discharge, 9/30 and 10/1 phone notes.
CORE = [
    stop(LISINOPRIL, "ACE inhibitor cough, switched to ARB at discharge"),
    rx("losartan", 100, "once daily"),
    stop(HCTZ, "Hyponatremia"),
    stop(TARTRATE, "Changed to metoprolol succinate ER"),
    rx("metoprolol succinate ER", 50, "once daily"),
    change(METFORMIN, 1000, "Increased at discharge, A1c 8.4"),
    rx("empagliflozin", 10, "once daily"),
]
# Michael O'Brien: 9/22 NSTEMI discharge, lisinopril stopped by the 9/25 phone note so never added, clopidogrel
# replaced by ticagrelor in the 9/29 cardiology letter.
MICHAEL = [
    rx("ticagrelor", 90, "twice daily", M),
    change(M_METOPROLOL, 50, "Increased at NSTEMI discharge 9/22"),
    rx("pantoprazole", 40, "once daily", M),
]
# Barbara Lewis: 9/23 cellulitis discharge, lisinopril reduced; cephalexin course already finished.
BARBARA = [change(B_LISINOPRIL, 5, "Reduced at discharge 9/23 after AKI")]
# Angela Rossi: 9/28 status migrainosus discharge (filed as discharge instructions).
ANGELA = [rx("topiramate", 25, "at bedtime", A), rx("ondansetron", 4, "as needed", A)]

REFERENCE = [
    ("search_notes", {"query": "Valley General"}),
    ("read_note", {"note_id": "note-1012-2"}),
    ("read_note", {"note_id": "note-1011-2"}),
    ("read_note", {"note_id": "note-1025-2"}),
    ("read_note", {"note_id": "note-1006-2"}),
    *[("list_medications", {"patient_id": pid}) for pid in (D, M, B, A)],
    *[("search_notes", {"patient_id": pid}) for pid in (D, M, B, A)],
    ("read_note", {"note_id": "note-1012-3"}),
    ("read_note", {"note_id": "note-1012-4"}),
    ("read_note", {"note_id": "note-1006-3"}),
    ("read_note", {"note_id": "note-1006-5"}),
    ("read_note", {"note_id": "note-1011-3"}),
    *CORE, *MICHAEL, *BARBARA, *ANGELA,
    ("submit", {"summary": "Reconciled the four Valley General discharges since 9/17. Angela: topiramate and "
                           "ondansetron started. Denise: discharge changes, then losartan 100 mg (9/30) and empagliflozin restarted (10/1). Michael: ticagrelor "
                           "(per 9/29 cardiology letter) and pantoprazole, metoprolol 50 mg; lisinopril left off. "
                           "Barbara: lisinopril 5 mg; cephalexin course already complete.",
                "patient_ids": [D, M, B, A]}),
]

OTHERS = [*MICHAEL, *BARBARA, *ANGELA]  # correct work on the others, for controls that break Denise only
DENISE_FAIL = {"denise_list_matches_expected"}

CONTROLS = [
    Control("do_nothing", [SUBMIT], expect_failed={"denise_list_matches_expected", "michael_list_matches_expected",
                                                   "barbara_list_matches_expected", "angela_list_matches_expected"}),
    Control("discharge_summary_only",
            [stop(LISINOPRIL, "cough"), rx("losartan", 50, "once daily"), stop(HCTZ, "hyponatremia"),
             stop(TARTRATE, "switch"), rx("metoprolol succinate ER", 50, "once daily"),
             change(METFORMIN, 1000, "A1c"), rx("empagliflozin", 10, "once daily"),
             rx("clopidogrel", 75, "once daily", M), change(M_METOPROLOL, 50, "discharge"),
             rx("pantoprazole", 40, "once daily", M), rx("lisinopril", 5, "once daily", M), *BARBARA, *ANGELA, SUBMIT],
            expect_failed={"denise_list_matches_expected", "michael_list_matches_expected"},
            description="Follows each discharge document and never reads the later notes."),
    Control("michael_missed_cardiology_letter",
            [*CORE, rx("clopidogrel", 75, "once daily", M), change(M_METOPROLOL, 50, "discharge"),
             rx("pantoprazole", 40, "once daily", M), *BARBARA, *ANGELA, SUBMIT],
            expect_failed={"michael_list_matches_expected"},
            description="Applies the discharge and the 9/25 phone note but misses the 9/29 switch to ticagrelor."),
    Control("missed_angela_discharge_instructions", [*CORE, *MICHAEL, *BARBARA, SUBMIT],
            expect_failed={"angela_list_matches_expected"},
            description="Searches only for 'discharge summary' and never finds Angela's discharge instructions."),
    Control("stopped_at_9_30_note", [c for c in CORE if c != rx("empagliflozin", 10, "once daily")] + OTHERS + [SUBMIT],
            expect_failed=DENISE_FAIL,
            description="Applies the 9/30 phone note but misses the 10/1 note that restarts empagliflozin."),
    Control("forgot_to_stop_tartrate",
            [c for c in CORE if c != stop(TARTRATE, "Changed to metoprolol succinate ER")] + OTHERS + [SUBMIT],
            expect_failed=DENISE_FAIL),
    Control("swapped_to_metformin_er",
            [*CORE[:5], stop(METFORMIN, "switch to ER"), rx("metformin ER", 1000, "twice daily"), CORE[6],
             *OTHERS, SUBMIT], expect_failed=DENISE_FAIL),
    Control("continued_completed_cefpodoxime", [*CORE, rx("cefpodoxime", 200, "twice daily"), *OTHERS, SUBMIT],
            expect_failed=DENISE_FAIL,
            description="Copies Denise's discharge antibiotic onto the active list although the course ended 9/30."),
    Control("kept_inpatient_pantoprazole", [*CORE, stop(OMEPRAZOLE, "changed to pantoprazole in hospital"),
                                            rx("pantoprazole", 40, "once daily"), *OTHERS, SUBMIT],
            expect_failed=DENISE_FAIL,
            description="Carries Denise's hospital formulary substitution home instead of resuming omeprazole."),
    Control("michael_missed_phone_note",
            [*CORE, *MICHAEL, rx("lisinopril", 5, "once daily", M), *BARBARA, *ANGELA, SUBMIT],
            expect_failed={"michael_list_matches_expected"},
            description="Starts Michael's lisinopril although the 9/25 phone note stopped it."),
    Control("michael_pantoprazole_treated_as_inpatient_only",
            [*CORE, *[c for c in MICHAEL if c != rx("pantoprazole", 40, "once daily", M)], *BARBARA, *ANGELA, SUBMIT],
            expect_failed={"michael_list_matches_expected"},
            description="Leaves off Michael's pantoprazole, which unlike Denise's was a deliberate discharge start."),
    Control("barbara_continued_completed_cephalexin",
            [*CORE, *MICHAEL, *BARBARA, *ANGELA, rx("cephalexin", 500, "four times daily", B), SUBMIT],
            expect_failed={"barbara_list_matches_expected"},
            description="Adds Barbara's cephalexin although the course ended with the 9/29 dose."),
    Control("missed_barbara", [*CORE, *MICHAEL, *ANGELA, SUBMIT], expect_failed={"barbara_list_matches_expected"},
            description="Reconciles only the discharges it found first."),
    Control("reconciled_out_of_window_patient",
            [*CORE, *MICHAEL, *BARBARA, *ANGELA, change("med-1008-01", 2.5, "reviewed 8/30 discharge"), SUBMIT],
            expect_failed={"no_changes_to_other_patients"},
            description="Also edits Harold Bennett, whose 8/30 discharge is outside the window."),
    Control("alt_correct_documents_completed_course",
            [*CORE, ("place_medication_order", {"patient_id": D, "medication": "cefpodoxime", "dose_value": 200,
                                                "dose_unit": "mg", "frequency": "twice daily", "duration_days": 5}),
             stop("med-new-004", "Course completed 9/30"), *OTHERS, SUBMIT],
            expect_pass=True, description="Records Denise's antibiotic course and then marks it stopped."),
    Control("alt_correct_two_step_and_reorders",
            [stop(LISINOPRIL, "cough"), rx("losartan", 50, "once daily"),
             change("med-new-001", 100, "9/30 phone note"),
             stop(HCTZ, "hyponatremia"), stop(TARTRATE, "switch"), rx("metoprolol succinate ER", 50, "every 24 hours"),
             change(METFORMIN, 1000, "discharge", frequency="every 12 hours"),
             rx("empagliflozin", 10, "once daily"), stop("med-new-003", "9/30 phone note: not filled"),
             rx("empagliflozin", 10, "every 24 hours"),
             rx("lisinopril", 5, "once daily", M), stop("med-new-005", "9/25 phone note"),
             stop(M_METOPROLOL, "dose change"), rx("metoprolol succinate ER", 50, "once daily", M),
             rx("Clopidogrel", 75, "every 24 hours", M), rx("pantoprazole", 40, "once daily", M),
             stop("med-new-007", "9/29 cardiology: CYP2C19 poor metabolizer"), rx("ticagrelor", 90, "every 12 hours", M),
             stop(B_LISINOPRIL, "dose change"), rx("lisinopril", 5, "once daily", B),
             rx("topiramate", 25, "at bedtime", A), rx("ondansetron", 4, "as needed", A),
             ("submit", {"summary": "done"})],
            expect_pass=True, description="Follows each source in date order for all four patients, with "
                                          "discontinue-and-reorder writes and equivalent frequency spellings."),
]
