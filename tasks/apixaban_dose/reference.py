from tasks import Control

P = "pt-1008"
APIX = "med-1008-01"
SUBMIT = ("submit", {"summary": "Done."})

REFERENCE = [
    ("search_patients", {"name": "Harold Bennett", "birth_date": "1945-02-20"}),
    ("list_medications", {"patient_id": P}),
    ("get_observations", {"patient_id": P, "query": "weight"}),
    ("get_observations", {"patient_id": P, "query": "creatinine"}),
    ("search_notes", {"patient_id": P}),
    ("read_note", {"note_id": "note-1008-3"}),
    ("update_medication", {"medication_id": APIX, "dose_value": 2.5,
                           "reason": "Age 81 and weight 58.2 kg (128.3 lb on 9/24) meet 2 of 3 label criteria"}),
    ("submit", {"summary": "Reduced apixaban to 2.5 mg twice daily. Age 81 and current weight 58.2 kg (128.3 lb "
                           "on 9/24) meet 2 of 3 dose-reduction criteria; creatinine 1.31 does not."}),
]

CONTROLS = [
    Control("do_nothing", [SUBMIT], expect_failed={"apixaban_2_5_mg_twice_daily"},
            description="Uses the last flowsheet weight (63.5 kg), counts only the age criterion, keeps 5 mg. "
                        "Also what a run that defers to the 9/28 pharmacist review ends with."),
    Control("reduced_to_once_daily",
            [("update_medication", {"medication_id": APIX, "dose_value": 2.5, "frequency": "once daily",
                                    "reason": "dose reduction"}), SUBMIT],
            expect_failed={"apixaban_2_5_mg_twice_daily"}),
    Control("new_order_without_stopping_old",
            [("place_medication_order", {"patient_id": P, "medication": "apixaban", "dose_value": 2.5,
                                         "dose_unit": "mg", "frequency": "twice daily"}), SUBMIT],
            expect_failed={"exactly_one_active_apixaban", "apixaban_2_5_mg_twice_daily"}),
    Control("reduced_and_stopped_furosemide",
            [("update_medication", {"medication_id": APIX, "dose_value": 2.5, "reason": "dose reduction"}),
             ("discontinue_medication", {"medication_id": "med-1008-03", "reason": "weight loss"}), SUBMIT],
            expect_failed={"other_medications_unchanged"}),
    Control("alt_correct_discontinue_and_reorder",
            [("discontinue_medication", {"medication_id": APIX, "reason": "dose reduction"}),
             ("place_medication_order", {"patient_id": P, "medication": "apixaban", "dose_value": 2.5,
                                         "dose_unit": "mg", "frequency": "every 12 hours"}), SUBMIT],
            expect_pass=True, description="Different write path and an equivalent frequency spelling."),
]
