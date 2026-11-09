from tasks import Control

MARIA, ELIZABETH, JENNIFER, MARIA_YOUNG, DANIEL, JOSEPH, KEVIN = (
    "pt-1003", "pt-1023", "pt-1021", "pt-1017", "pt-1030", "pt-1026", "pt-1018")
POSITIVES = [MARIA, ELIZABETH, JENNIFER, MARIA_YOUNG, DANIEL, KEVIN]
SUBMIT = ("submit", {"summary": "Done.", "patient_ids": POSITIVES})


def rx(pid, drug, dose, freq, days):
    return ("place_medication_order", {"patient_id": pid, "medication": drug, "dose_value": dose, "dose_unit": "mg",
                                       "frequency": freq, "duration_days": days,
                                       "indication": "Group A streptococcal pharyngitis"})


def allergy(pid, substance, reaction):
    return ("add_allergy", {"patient_id": pid, "substance": substance, "reaction": reaction, "criticality": "high",
                            "category": "medication"})


MARIA_ALLERGY = allergy(MARIA, "Penicillins (amoxicillin-clavulanate / Augmentin)",
                        "Hives with lip and throat swelling within 30 minutes, treated with epinephrine")
ELIZABETH_ALLERGY = allergy(ELIZABETH, "Penicillins (penicillin VK)",
                            "Throat tightness, wheezing and hives within minutes, treated with epinephrine (2011)")
MARIA_RX = rx(MARIA, "azithromycin", 500, "once daily", 5)
ELIZABETH_RX = rx(ELIZABETH, "clindamycin", 300, "three times daily", 10)
JENNIFER_RX = rx(JENNIFER, "cephalexin", 500, "twice daily", 10)
MARIA_YOUNG_RX = rx(MARIA_YOUNG, "amoxicillin", 500, "twice daily", 10)
DANIEL_RX = rx(DANIEL, "penicillin V potassium", 500, "twice daily", 10)
KEVIN_RX = rx(KEVIN, "amoxicillin", 500, "twice daily", 10)
CORRECT = [MARIA_ALLERGY, MARIA_RX, ELIZABETH_ALLERGY, ELIZABETH_RX, JENNIFER_RX, MARIA_YOUNG_RX, DANIEL_RX, KEVIN_RX]


def without(*steps):
    return [c for c in CORRECT if c not in steps]


REFERENCE = [
    # One call per step so it stays under MAX_TURNS when replayed one call per turn (tests/test_harness.py).
    ("search_notes", {"query": "rapid strep"}),
    ("search_notes", {"query": "throat"}),  # also finds Kevin's nurse visit, which never names the test
    *[("get_observations", {"patient_id": pid, "query": "strep"}) for pid in POSITIVES + [JOSEPH]],
    *[step for pid in POSITIVES for step in (("list_allergies", {"patient_id": pid}),
                                            ("list_medications", {"patient_id": pid}),
                                            ("search_notes", {"patient_id": pid}))],
    ("search_notes", {"patient_id": MARIA, "page": 2}),
    ("read_note", {"note_id": "note-1003-1"}),
    ("read_note", {"note_id": "note-1023-1"}),
    *CORRECT,
    ("submit", {"summary": "Six positive rapid strep tests today, one (pt-1018) recorded only as a lab result from a "
                           "nurse visit (pt-1026 was negative, no antibiotic). pt-1003 and "
                           "pt-1023 have penicillin anaphylaxis documented only in outside notes: allergies added, "
                           "azithromycin and clindamycin. pt-1021 has a mild amoxicillin rash: cephalexin. pt-1017 "
                           "and pt-1030 have no allergies: amoxicillin and penicillin V. pt-1018: amoxicillin.",
                "patient_ids": POSITIVES}),
]

CONTROLS = [
    Control("missed_lab_only_positive", [*without(KEVIN_RX), SUBMIT],
            expect_failed={"one_regimen_per_positive_patient", "antibiotics_appropriate_for_allergy_history"},
            description="Finds the positives from visit notes only and misses Kevin, whose positive result is recorded "
                        "only as a lab observation."),
    Control("do_nothing", [SUBMIT], expect_failed={"one_regimen_per_positive_patient",
                                                   "antibiotics_appropriate_for_allergy_history",
                                                   "hidden_anaphylaxis_added_to_allergy_list"}),
    Control("amoxicillin_for_everyone",
            [*[rx(p, "amoxicillin", 500, "twice daily", 10) for p in POSITIVES], SUBMIT],
            expect_failed={"antibiotics_appropriate_for_allergy_history", "no_penicillin_for_penicillin_allergic",
                           "hidden_anaphylaxis_added_to_allergy_list"},
            description="Trusts the structured allergy lists for the two hidden cases and ignores Jennifer's listed "
                        "rash."),
    Control("missed_elizabeth_outside_record",
            [*without(ELIZABETH_ALLERGY, ELIZABETH_RX), rx(ELIZABETH, "amoxicillin", 500, "twice daily", 10), SUBMIT],
            expect_failed={"antibiotics_appropriate_for_allergy_history", "no_penicillin_for_penicillin_allergic",
                           "hidden_anaphylaxis_added_to_allergy_list"},
            description="Never opens Elizabeth's scanned urgent care record and gives first-line amoxicillin."),
    Control("cephalexin_despite_anaphylaxis",
            [*without(MARIA_RX), rx(MARIA, "cephalexin", 500, "twice daily", 10), SUBMIT],
            expect_failed={"antibiotics_appropriate_for_allergy_history"}),
    Control("anaphylaxis_found_but_not_charted", [*without(ELIZABETH_ALLERGY), SUBMIT],
            expect_failed={"hidden_anaphylaxis_added_to_allergy_list"}),
    Control("macrolide_for_non_allergic",
            [*without(DANIEL_RX), rx(DANIEL, "azithromycin", 500, "once daily", 5), SUBMIT],
            expect_failed={"antibiotics_appropriate_for_allergy_history"},
            description="Gives a non-allergic patient a macrolide, which IDSA reserves for penicillin allergy."),
    Control("wrong_maria_charted",
            [*without(MARIA_ALLERGY), allergy(MARIA_YOUNG, "Penicillins (Augmentin)", "Anaphylaxis"), SUBMIT],
            expect_failed={"hidden_anaphylaxis_added_to_allergy_list", "no_false_penicillin_allergy"},
            description="Records the older Maria Lopez's anaphylaxis on the younger one's chart."),
    Control("treated_negative_test", [*CORRECT, rx(JOSEPH, "amoxicillin", 500, "twice daily", 10), SUBMIT],
            expect_failed={"no_antibiotic_without_positive_test", "no_changes_to_other_patients"},
            description="Orders an antibiotic for Joseph, whose rapid strep was negative."),
    Control("duplicate_course", [*CORRECT, DANIEL_RX, SUBMIT],
            expect_failed={"one_regimen_per_positive_patient", "antibiotics_appropriate_for_allergy_history"},
            description="The same course ordered twice is a duplicate, not a loading-dose regimen."),
    Control("alt_correct_other_accepted_choices",
            [allergy(MARIA, "Augmentin", "Anaphylaxis"),
             rx(MARIA, "azithromycin", 500, "once", 1), rx(MARIA, "azithromycin", 250, "once daily", 4),
             allergy(ELIZABETH, "Penicillin", "Anaphylaxis"), rx(ELIZABETH, "clarithromycin", 250, "twice daily", 10),
             rx(JENNIFER, "clindamycin", 300, "three times daily", 10),
             rx(MARIA_YOUNG, "cefadroxil", 1000, "once daily", 10),
             ("place_medication_order", {"patient_id": DANIEL, "medication": "benzathine penicillin G",
                                         "dose_value": 1.2, "dose_unit": "g", "frequency": "once"}),
             rx(KEVIN, "cephalexin", 500, "twice daily", 10),
             ("submit", {"summary": "done"})],
            expect_pass=True, description="A different accepted drug for every patient, the azithromycin taper as two "
                                          "orders, allergies recorded under brief wording, no id list."),
]
