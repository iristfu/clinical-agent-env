from tasks import Control

EDOX, RIVA_B, DABI_C, APIX_D, APIX_E, RIVA_F = ("med-2001-02", "med-2002-02", "med-2003-03", "med-2004-02",
                                                "med-2005-02", "med-2006-02")
APIX_G, APIX_H, DABI_I, EDOX_J, EDOX_K, RIVA_L = ("med-2007-02", "med-2008-02", "med-2009-02", "med-2010-02",
                                                  "med-2011-02", "med-2012-02")
EDOX_M, DABI_N, APIX_O, APIX_P, RIVA_Q = "med-2013-02", "med-2014-02", "med-2015-02", "med-2016-02", "med-2017-02"
PIDS = [f"pt-{i}" for i in range(2001, 2018)]
SUBMIT = ("submit", {"summary": "Done.", "patient_ids": []})


def dose(med_id, value, reason, **extra):
    return ("update_medication", {"medication_id": med_id, "dose_value": value, "reason": reason, **extra})


def order(pid, drug, value, freq="twice daily"):
    return ("place_medication_order", {"patient_id": pid, "medication": drug, "dose_value": value, "dose_unit": "mg",
                                       "frequency": freq})


STOP_EDOX = ("discontinue_medication", {"medication_id": EDOX, "reason": "CrCl about 161 mL/min, above 95: not recommended in NVAF"})
SWITCH_A = [STOP_EDOX, order("pt-2001", "apixaban", 5)]
FIX_B = dose(RIVA_B, 15, "CrCl about 29 mL/min (52 kg, age 74, Cr 1.4, female): 15 mg daily")
FIX_C = dose(DABI_C, 75, "CrCl about 39 mL/min with dronedarone: 75 mg twice daily")
FIX_D = dose(APIX_D, 5, "Only the age criterion is met (88 kg, Cr 1.2): 5 mg twice daily")
FIX_G = dose(APIX_G, 2.5, "No dose-reduction criteria, but itraconazole is a strong dual CYP3A4 and P-gp inhibitor: halve to 2.5 mg")
FIX_I = dose(DABI_I, 75, "CrCl about 25 mL/min (15 to 30): 75 mg twice daily")
FIX_K = dose(EDOX_K, 30, "CrCl about 39 mL/min (15 to 50): 30 mg once daily")
FIX_L = dose(RIVA_L, 20, "CrCl about 75 mL/min, above 50: 20 mg once daily with the evening meal")
FIX_N = dose(DABI_N, 150, "CrCl about 67 mL/min: the dronedarone reduction applies only at CrCl 30 to 50, so 150 mg twice daily")
FIX_O = dose(APIX_O, 5, "Age 79 (not yet 80), 58 kg, Cr 1.0: only the weight criterion, so 5 mg twice daily")
FIX_P = dose(APIX_P, 2.5, "Age 82 and weight 125 lb (56.7 kg): two criteria, so 2.5 mg twice daily")
FIX_Q = dose(RIVA_Q, 15, "Woman, 76, 61 kg, Cr 1.05: CrCl about 44 mL/min with the 0.85 factor, so 15 mg once daily")
CORRECT = [*SWITCH_A, FIX_B, FIX_C, FIX_D, FIX_G, FIX_I, FIX_K, FIX_L, FIX_N, FIX_O, FIX_P, FIX_Q]

REFERENCE = [
    ("list_patients", {}),
    *[step for pid in PIDS for step in (("list_medications", {"patient_id": pid}),
                                        ("get_observations", {"patient_id": pid}))],
    *CORRECT,
    ("submit", {"summary": "pt-2001 edoxaban stopped (CrCl about 161, above 95) and switched to apixaban 5 mg BID. "
                           "pt-2002 rivaroxaban reduced to 15 mg daily (CrCl about 29). pt-2003 dabigatran reduced to "
                           "75 mg BID (CrCl about 39 with dronedarone). pt-2004 apixaban raised to 5 mg BID (age 81 "
                           "only; the January creatinine of 1.6 is stale). pt-2007 apixaban halved to 2.5 mg BID for "
                           "itraconazole. pt-2009 dabigatran reduced to 75 mg BID (CrCl about 25). pt-2011 edoxaban "
                           "reduced to 30 mg daily (CrCl about 39). pt-2012 rivaroxaban raised to 20 mg daily (CrCl "
                           "about 75). pt-2014 dabigatran raised to 150 mg BID (CrCl about 67, so the dronedarone rule does not apply). "
                           "pt-2015 apixaban raised to 5 mg BID (age 79, weight only). pt-2016 apixaban reduced to 2.5 mg "
                           "BID (age 82, 125 lb is 56.7 kg). pt-2017 rivaroxaban reduced to 15 mg daily (CrCl about 44 for "
                           "a woman). pt-2005, pt-2006, pt-2008 (clarithromycin needs no adjustment) and pt-2010 "
                           "(CrCl about 92) are correct.",
                "patient_ids": ["pt-2001", "pt-2002", "pt-2003", "pt-2004", "pt-2007", "pt-2009", "pt-2011",
                                "pt-2012", "pt-2014", "pt-2015", "pt-2016", "pt-2017"]}),
]


def without(*skip):
    return [c for c in CORRECT if c not in skip]


CONTROLS = [
    Control("do_nothing", [SUBMIT],
            expect_failed={"edoxaban_patient_switched", "rivaroxaban_reduced_for_low_crcl",
                           "rivaroxaban_restored_when_crcl_above_50", "dabigatran_reduced_with_dronedarone",
                           "dabigatran_reduced_for_crcl_15_to_30", "apixaban_raised_when_one_criterion",
                           "apixaban_halved_with_strong_inhibitor", "edoxaban_reduced_for_crcl_under_50",
                           "dabigatran_restored_when_crcl_above_50", "apixaban_raised_at_age_79",
                           "apixaban_reduced_when_weight_in_pounds", "rivaroxaban_reduced_with_female_factor"},
            description="Leaves every dose as it is."),
    Control("keeps_edoxaban", [*without(*SWITCH_A), SUBMIT], expect_failed={"edoxaban_patient_switched"},
            description="Reasons that good kidney function is fine for edoxaban and leaves it at 60 mg."),
    Control("edoxaban_reduced_instead_of_switched",
            [dose(EDOX, 30, "reduce"), FIX_B, FIX_C, FIX_D, FIX_G, FIX_I, FIX_K, FIX_L, FIX_N, FIX_O, FIX_P, FIX_Q, SUBMIT], expect_failed={"edoxaban_patient_switched"},
            description="Applies a renal-dose reduction to edoxaban instead of recognizing it is not recommended."),
    Control("switched_to_warfarin",
            [STOP_EDOX, order("pt-2001", "warfarin", 5, "once daily"), FIX_B, FIX_C, FIX_D, FIX_G, FIX_I, FIX_K, FIX_L, FIX_N, FIX_O, FIX_P, FIX_Q, SUBMIT],
            expect_failed={"edoxaban_patient_switched", "other_medications_unchanged"},
            description="The prompt says switch to another DOAC."),
    Control("edoxaban_kept_and_second_doac_added",
            [order("pt-2001", "apixaban", 5), FIX_B, FIX_C, FIX_D, FIX_G, FIX_I, FIX_K, FIX_L, FIX_N, FIX_O, FIX_P, FIX_Q, SUBMIT], expect_failed={"edoxaban_patient_switched"},
            description="Adds a second anticoagulant without stopping edoxaban."),
    Control("apixaban_style_rule_for_rivaroxaban", [*without(FIX_B), SUBMIT],
            expect_failed={"rivaroxaban_reduced_for_low_crcl"},
            description="Uses creatinine under 1.5 and age under 80 and keeps rivaroxaban at 20 mg, never computing CrCl."),
    Control("rivaroxaban_wrong_frequency", [*without(FIX_B), dose(RIVA_B, 15, "reduce", frequency="twice daily"), SUBMIT],
            expect_failed={"rivaroxaban_reduced_for_low_crcl"}),
    Control("misses_dronedarone_interaction", [*without(FIX_C), SUBMIT],
            expect_failed={"dabigatran_reduced_with_dronedarone"},
            description="CrCl 39 alone keeps dabigatran at 150 mg; the interaction is what lowers it."),
    Control("dabigatran_reduced_too_far", [*without(FIX_C), dose(DABI_C, 110, "reduce"), SUBMIT],
            expect_failed={"dabigatran_reduced_with_dronedarone"}),
    Control("age_80_reduction_for_apixaban", [*without(FIX_D), SUBMIT], expect_failed={"apixaban_raised_when_one_criterion"},
            description="Treats age 81 as enough, or counts the stale January creatinine of 1.6 as a second criterion."),
    Control("changed_correct_apixaban", [*CORRECT, dose(APIX_E, 5, "age 83 only"), SUBMIT],
            expect_failed={"correct_doses_left_alone"}, description="Raises Eleanor's already-correct dose."),
    Control("changed_correct_rivaroxaban", [*CORRECT, dose(RIVA_F, 15, "reduce"), SUBMIT],
            expect_failed={"correct_doses_left_alone"}, description="Reduces Marcus's already-correct dose."),
    Control("duplicate_rivaroxaban_orders",
            [*without(FIX_B), order("pt-2002", "rivaroxaban", 15, "once daily"), SUBMIT],
            expect_failed={"rivaroxaban_reduced_for_low_crcl"}, description="New order without stopping the old one."),
    Control("ignores_strong_inhibitor", [*without(FIX_G), SUBMIT], expect_failed={"apixaban_halved_with_strong_inhibitor"},
            description="Applies the age, weight and creatinine rule only and leaves apixaban 5 mg with itraconazole."),
    Control("stops_itraconazole_instead",
            [*without(FIX_G), ("discontinue_medication", {"medication_id": "med-2007-01", "reason": "interaction"}), SUBMIT],
            expect_failed={"apixaban_halved_with_strong_inhibitor", "other_medications_unchanged"},
            description="Removes the interacting drug, which the prompt says not to touch, and leaves the dose."),
    Control("alt_correct_halves_apixaban_for_clarithromycin",
            [*CORRECT, dose(APIX_H, 2.5, "strong CYP3A4 and P-gp inhibitor"), ("submit", {"summary": "done"})],
            expect_pass=True,
            description="Older labels listed clarithromycin with the inhibitors that need the reduction, so this does not "
                        "fail the task. Only the diagnostic clarithromycin_exception_followed check records it."),
    Control("misses_dabigatran_crcl_15_to_30", [*without(FIX_I), SUBMIT],
            expect_failed={"dabigatran_reduced_for_crcl_15_to_30"},
            description="Only knows the dronedarone rule, so leaves dabigatran 150 mg at CrCl about 25."),
    Control("edoxaban_left_at_60_for_crcl_39", [*without(FIX_K), SUBMIT],
            expect_failed={"edoxaban_reduced_for_crcl_under_50"}),
    Control("edoxaban_switched_at_crcl_92", [*CORRECT, dose(EDOX_J, 30, "reduce"), SUBMIT],
            expect_failed={"correct_doses_left_alone"}, description="Misreads a CrCl just under 95."),
    Control("rivaroxaban_15_kept_at_crcl_75", [*without(FIX_L), SUBMIT],
            expect_failed={"rivaroxaban_restored_when_crcl_above_50"},
            description="Does not notice an unwarranted reduced dose."),
    Control("keeps_edoxaban_60_but_reduces_for_weight", [*CORRECT, dose(EDOX_M, 30, "weight 58 kg"), SUBMIT],
            expect_failed={"correct_doses_left_alone"}, description="Applies the VTE weight rule to an NVAF patient."),
    Control("keeps_dabigatran_75_with_dronedarone", [*without(FIX_N), SUBMIT],
            expect_failed={"dabigatran_restored_when_crcl_above_50"},
            description="Applies the dronedarone reduction outside the CrCl 30 to 50 band."),
    Control("calls_79_year_old_eighty", [*without(FIX_O), SUBMIT], expect_failed={"apixaban_raised_at_age_79"},
            description="Rounds Harvey up to the age criterion."),
    Control("reads_pounds_as_kilograms", [*without(FIX_P), SUBMIT],
            expect_failed={"apixaban_reduced_when_weight_in_pounds"}),
    Control("forgets_female_factor", [*without(FIX_Q), SUBMIT], expect_failed={"rivaroxaban_reduced_with_female_factor"},
            description="Computes Margaret's CrCl without the 0.85 factor (51.6) and keeps 20 mg."),
    Control("also_changed_metformin", [*CORRECT, dose("med-2006-01", 500, "renal", frequency="once daily"), SUBMIT],
            expect_failed={"other_medications_unchanged"}),
    Control("alt_correct_switch_to_rivaroxaban",
            [STOP_EDOX, order("pt-2001", "rivaroxaban", 20, "once daily"), FIX_B, FIX_C, FIX_D, FIX_G, FIX_I, FIX_K, FIX_L, FIX_N, FIX_O, FIX_P, FIX_Q,
             ("submit", {"summary": "done"})],
            expect_pass=True, description="A different valid alternative, and no id list."),
    Control("alt_correct_switch_to_dabigatran",
            [STOP_EDOX, order("pt-2001", "dabigatran", 150, "every 12 hours"), FIX_B, FIX_C, FIX_D, FIX_G, FIX_I, FIX_K, FIX_L, FIX_N, FIX_O, FIX_P, FIX_Q,
             ("submit", {"summary": "done", "patient_ids": ["pt-2001", "pt-2002", "pt-2003", "pt-2004"]})],
            expect_pass=True, description="Another valid alternative with an equivalent frequency spelling."),
    Control("alt_correct_stop_and_reorder_rivaroxaban",
            [*SWITCH_A, ("discontinue_medication", {"medication_id": RIVA_B, "reason": "dose change"}),
             order("pt-2002", "Rivaroxaban", 15, "once daily"), FIX_C, FIX_D, FIX_G, FIX_I, FIX_K, FIX_L, FIX_N, FIX_O, FIX_P, FIX_Q, ("submit", {"summary": "done"})],
            expect_pass=True, description="Discontinue and re-order instead of editing in place."),
]
