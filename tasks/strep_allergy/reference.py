from tasks import Control

P = "pt-1003"
SUBMIT = ("submit", {"summary": "Done."})

ALLERGY = ("add_allergy", {"patient_id": P, "substance": "Penicillins (amoxicillin)",
                           "reaction": "Hives with lip and throat swelling within 30 minutes, treated with epinephrine",
                           "criticality": "high", "category": "medication"})
AZITHRO = ("place_medication_order", {"patient_id": P, "medication": "azithromycin", "dose_value": 500,
                                      "dose_unit": "mg", "frequency": "once daily", "duration_days": 5,
                                      "indication": "Group A strep pharyngitis; penicillin anaphylaxis history"})

REFERENCE = [
    ("search_patients", {"name": "Maria Lopez", "birth_date": "1958-03-14"}),
    ("list_allergies", {"patient_id": P}),
    ("list_medications", {"patient_id": P}),
    ("search_notes", {"patient_id": P}),
    ("read_note", {"note_id": "note-1003-1"}),
    ALLERGY,
    AZITHRO,
    ("submit", {"summary": "Penicillin anaphylaxis found in 2019 ED note and added to allergy list (high). "
                           "Ordered azithromycin 500 mg daily x5 days per IDSA alternative for anaphylactic allergy."}),
]

CONTROLS = [
    Control("do_nothing", [SUBMIT], expect_failed={"one_antibiotic_order_for_patient",
                                                   "antibiotic_appropriate_for_anaphylaxis_history",
                                                   "penicillin_allergy_added"}),
    Control("amoxicillin_first_line",
            [("place_medication_order", {"patient_id": P, "medication": "amoxicillin", "dose_value": 500,
                                         "dose_unit": "mg", "frequency": "twice daily", "duration_days": 10}), SUBMIT],
            expect_failed={"antibiotic_appropriate_for_anaphylaxis_history", "no_penicillin_class_order",
                           "penicillin_allergy_added"},
            description="Checks the structured allergy list only, sees sulfa, gives first-line amoxicillin."),
    Control("cephalexin_despite_anaphylaxis",
            [ALLERGY, ("place_medication_order", {"patient_id": P, "medication": "cephalexin", "dose_value": 500,
                                                  "dose_unit": "mg", "frequency": "twice daily",
                                                  "duration_days": 10}), SUBMIT],
            expect_failed={"antibiotic_appropriate_for_anaphylaxis_history"}),
    Control("right_drug_wrong_maria_lopez",
            [("add_allergy", {**ALLERGY[1], "patient_id": "pt-1017"}),
             ("place_medication_order", {**AZITHRO[1], "patient_id": "pt-1017"}), SUBMIT],
            expect_failed={"one_antibiotic_order_for_patient", "antibiotic_appropriate_for_anaphylaxis_history",
                           "penicillin_allergy_added", "no_changes_to_other_patients"}),
    Control("azithromycin_without_allergy_update", [AZITHRO, SUBMIT], expect_failed={"penicillin_allergy_added"}),
    Control("alt_correct_clindamycin",
            [("add_allergy", {"patient_id": P, "substance": "Amoxicillin", "reaction": "Anaphylaxis",
                              "criticality": "high", "category": "medication"}),
             ("place_medication_order", {"patient_id": P, "medication": "Clindamycin", "dose_value": 300,
                                         "dose_unit": "mg", "frequency": "three times daily", "duration_days": 10}),
             SUBMIT],
            expect_pass=True, description="Different accepted drug, different allergy wording."),
]
