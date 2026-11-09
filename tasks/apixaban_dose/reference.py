from tasks import Control

HAROLD, LISA, WILLIAM, CHARLES, MARGARET = "med-1008-01", "med-1019-03", "med-1022-05", "med-1028-03", "med-1029-04"
LINDA = "med-1002-03"
ALL = ["pt-1002", "pt-1008", "pt-1019", "pt-1022", "pt-1028", "pt-1029"]
SUBMIT = ("submit", {"summary": "Done.", "patient_ids": []})


def dose(med_id, value, reason, **extra):
    return ("update_medication", {"medication_id": med_id, "dose_value": value, "reason": reason, **extra})


REDUCE_HAROLD = dose(HAROLD, 2.5, "Age 81 and weight 58.2 kg (128.3 lb on 9/24): 2 of 3 label criteria")
RAISE_WILLIAM = dose(WILLIAM, 5, "Age 79, weight 81.6 kg, Cr 1.61: 1 of 3 criteria, so label dose is 5 mg BID")
REDUCE_CHARLES = dose(CHARLES, 2.5, "Age 82 and Cr 1.63 (stable CKD 3b): 2 of 3 label criteria")
REDUCE_LINDA = dose(LINDA, 2.5, "Weight 57.6 kg and Cr 1.66 (9/18, Lakeside Nephrology letter): 2 of 3 criteria")
CORRECT = [REDUCE_LINDA, REDUCE_HAROLD, RAISE_WILLIAM, REDUCE_CHARLES]

# One call per step, so this stays under MAX_TURNS when replayed one call per turn (tests/test_harness.py).
REFERENCE = [
    *[("list_medications", {"patient_id": f"pt-{i}"}) for i in range(1001, 1031)],
    *[step for pid in ALL for step in (("list_conditions", {"patient_id": pid}),
                                       ("get_observations", {"patient_id": pid}),
                                       ("search_notes", {"patient_id": pid}))],
    ("read_note", {"note_id": "note-1008-3"}),
    ("read_note", {"note_id": "note-1002-4"}),
    ("read_note", {"note_id": "note-1029-2"}),
    *CORRECT,
    ("submit", {"summary": "Reviewed 6 patients on apixaban. pt-1002 reduced to 2.5 mg BID (57.6 kg, Cr 1.66 in the 9/18 "
                           "nephrology letter). pt-1008 reduced to 2.5 mg BID (age 81, 58.2 kg from 128.3 "
                           "lb on 9/24). pt-1022 increased to 5 mg BID (age 79, only Cr meets). pt-1028 reduced to 2.5 "
                           "mg BID (age 82, Cr 1.63). pt-1019 unchanged (weight only; 8/18 Cr was a resolved AKI). "
                           "pt-1029 unchanged (apixaban is for PE, not AF).",
                "patient_ids": ["pt-1002", "pt-1008", "pt-1022", "pt-1028"]}),
]

CONTROLS = [
    Control("do_nothing", [SUBMIT], expect_failed={"nvaf_doses_correct"},
            description="Leaves every dose as it is."),
    Control("structured_creatinine_only_for_linda", [REDUCE_HAROLD, RAISE_WILLIAM, REDUCE_CHARLES, SUBMIT],
            expect_failed={"nvaf_doses_correct"},
            description="Trusts Linda's last structured creatinine (1.18) and misses the 1.66 in the nephrology letter."),
    Control("structured_weights_only", [REDUCE_LINDA, RAISE_WILLIAM, REDUCE_CHARLES, SUBMIT],
            expect_failed={"nvaf_doses_correct"},
            description="Uses Harold's last flowsheet weight (63.5 kg) and keeps him on 5 mg."),
    Control("age_rounded_up_for_william", [REDUCE_LINDA, REDUCE_HAROLD, REDUCE_CHARLES, SUBMIT],
            expect_failed={"nvaf_doses_correct"},
            description="Treats William (79) as meeting the age criterion and leaves him on 2.5 mg."),
    Control("transient_aki_counted_for_lisa",
            [*CORRECT, dose(LISA, 2.5, "weight 57.8 kg and Cr 1.74"), SUBMIT], expect_failed={"nvaf_doses_correct"},
            description="Counts the resolved 8/18 AKI creatinine as a second criterion and reduces Lisa."),
    Control("af_rule_applied_to_pe_patient",
            [*CORRECT, dose(MARGARET, 2.5, "weight 56.2 kg and Cr 1.54"), SUBMIT],
            expect_failed={"non_af_apixaban_unchanged"},
            description="Applies the AF dose-reduction rule to Margaret, whose apixaban is treating a pulmonary embolism."),
    Control("reduced_to_once_daily",
            [REDUCE_LINDA, dose(HAROLD, 2.5, "reduce", frequency="once daily"), RAISE_WILLIAM, REDUCE_CHARLES, SUBMIT],
            expect_failed={"nvaf_doses_correct"}),
    Control("new_order_without_stopping_old",
            [("place_medication_order", {"patient_id": "pt-1008", "medication": "apixaban", "dose_value": 2.5,
                                         "dose_unit": "mg", "frequency": "twice daily"}),
             REDUCE_LINDA, RAISE_WILLIAM, REDUCE_CHARLES, SUBMIT],
            expect_failed={"nvaf_doses_correct"}),
    Control("also_changed_metformin",
            [*CORRECT, dose("med-1028-01", 500, "eGFR 41", frequency="once daily"), SUBMIT],
            expect_failed={"other_medications_unchanged"},
            description="Adjusts Charles's metformin for his eGFR, which the prompt says not to do."),
    Control("alt_correct_discontinue_and_reorder",
            [("discontinue_medication", {"medication_id": HAROLD, "reason": "dose reduction"}),
             ("place_medication_order", {"patient_id": "pt-1008", "medication": "apixaban", "dose_value": 2.5,
                                         "dose_unit": "mg", "frequency": "every 12 hours"}),
             ("discontinue_medication", {"medication_id": WILLIAM, "reason": "underdosed"}),
             ("place_medication_order", {"patient_id": "pt-1022", "medication": "Apixaban", "dose_value": 5,
                                         "dose_unit": "mg", "frequency": "twice daily"}),
             REDUCE_CHARLES, REDUCE_LINDA, ("submit", {"summary": "done"})],
            expect_pass=True, description="Different write paths, an equivalent frequency spelling, no id list."),
]
