# Run report 20261109-144329_controls_doac3

Policy controls, model None, effort model default, commit a3421c2738 (dirty), initial state hash eaa87f3c56ec380b.

## Grader controls

| Task | Control | Expected | Got | OK |
|---|---|---|---|---|
| doac_dose_reasoning | age_80_reduction_for_apixaban | fail on apixaban_raised_when_one_criterion | fail on apixaban_raised_when_one_criterion | yes |
| doac_dose_reasoning | also_changed_metformin | fail on other_medications_unchanged | fail on other_medications_unchanged | yes |
| doac_dose_reasoning | alt_correct_halves_apixaban_for_clarithromycin | pass | pass | yes |
| doac_dose_reasoning | alt_correct_stop_and_reorder_rivaroxaban | pass | pass | yes |
| doac_dose_reasoning | alt_correct_switch_to_dabigatran | pass | pass | yes |
| doac_dose_reasoning | alt_correct_switch_to_rivaroxaban | pass | pass | yes |
| doac_dose_reasoning | apixaban_style_rule_for_rivaroxaban | fail on rivaroxaban_reduced_for_low_crcl | fail on rivaroxaban_reduced_for_low_crcl | yes |
| doac_dose_reasoning | calls_79_year_old_eighty | fail on apixaban_raised_at_age_79 | fail on apixaban_raised_at_age_79 | yes |
| doac_dose_reasoning | changed_correct_apixaban | fail on correct_doses_left_alone | fail on correct_doses_left_alone | yes |
| doac_dose_reasoning | changed_correct_rivaroxaban | fail on correct_doses_left_alone | fail on correct_doses_left_alone | yes |
| doac_dose_reasoning | dabigatran_reduced_too_far | fail on dabigatran_reduced_with_dronedarone | fail on dabigatran_reduced_with_dronedarone | yes |
| doac_dose_reasoning | do_nothing | fail on apixaban_halved_with_strong_inhibitor, apixaban_raised_at_age_79, apixaban_raised_when_one_criterion, apixaban_reduced_when_weight_in_pounds, dabigatran_reduced_for_crcl_15_to_30, dabigatran_reduced_with_dronedarone, dabigatran_restored_when_crcl_above_50, edoxaban_patient_switched, edoxaban_reduced_for_crcl_under_50, rivaroxaban_reduced_for_low_crcl, rivaroxaban_reduced_with_female_factor, rivaroxaban_restored_when_crcl_above_50 | fail on apixaban_halved_with_strong_inhibitor, apixaban_raised_at_age_79, apixaban_raised_when_one_criterion, apixaban_reduced_when_weight_in_pounds, dabigatran_reduced_for_crcl_15_to_30, dabigatran_reduced_with_dronedarone, dabigatran_restored_when_crcl_above_50, edoxaban_patient_switched, edoxaban_reduced_for_crcl_under_50, rivaroxaban_reduced_for_low_crcl, rivaroxaban_reduced_with_female_factor, rivaroxaban_restored_when_crcl_above_50 | yes |
| doac_dose_reasoning | duplicate_rivaroxaban_orders | fail on rivaroxaban_reduced_for_low_crcl | fail on rivaroxaban_reduced_for_low_crcl | yes |
| doac_dose_reasoning | edoxaban_kept_and_second_doac_added | fail on edoxaban_patient_switched | fail on edoxaban_patient_switched | yes |
| doac_dose_reasoning | edoxaban_left_at_60_for_crcl_39 | fail on edoxaban_reduced_for_crcl_under_50 | fail on edoxaban_reduced_for_crcl_under_50 | yes |
| doac_dose_reasoning | edoxaban_reduced_instead_of_switched | fail on edoxaban_patient_switched | fail on edoxaban_patient_switched | yes |
| doac_dose_reasoning | edoxaban_switched_at_crcl_92 | fail on correct_doses_left_alone | fail on correct_doses_left_alone | yes |
| doac_dose_reasoning | forgets_female_factor | fail on rivaroxaban_reduced_with_female_factor | fail on rivaroxaban_reduced_with_female_factor | yes |
| doac_dose_reasoning | ignores_strong_inhibitor | fail on apixaban_halved_with_strong_inhibitor | fail on apixaban_halved_with_strong_inhibitor | yes |
| doac_dose_reasoning | keeps_dabigatran_75_with_dronedarone | fail on dabigatran_restored_when_crcl_above_50 | fail on dabigatran_restored_when_crcl_above_50 | yes |
| doac_dose_reasoning | keeps_edoxaban | fail on edoxaban_patient_switched | fail on edoxaban_patient_switched | yes |
| doac_dose_reasoning | keeps_edoxaban_60_but_reduces_for_weight | fail on correct_doses_left_alone | fail on correct_doses_left_alone | yes |
| doac_dose_reasoning | misses_dabigatran_crcl_15_to_30 | fail on dabigatran_reduced_for_crcl_15_to_30 | fail on dabigatran_reduced_for_crcl_15_to_30 | yes |
| doac_dose_reasoning | misses_dronedarone_interaction | fail on dabigatran_reduced_with_dronedarone | fail on dabigatran_reduced_with_dronedarone | yes |
| doac_dose_reasoning | reads_pounds_as_kilograms | fail on apixaban_reduced_when_weight_in_pounds | fail on apixaban_reduced_when_weight_in_pounds | yes |
| doac_dose_reasoning | rivaroxaban_15_kept_at_crcl_75 | fail on rivaroxaban_restored_when_crcl_above_50 | fail on rivaroxaban_restored_when_crcl_above_50 | yes |
| doac_dose_reasoning | rivaroxaban_wrong_frequency | fail on rivaroxaban_reduced_for_low_crcl | fail on rivaroxaban_reduced_for_low_crcl | yes |
| doac_dose_reasoning | stops_itraconazole_instead | fail on apixaban_halved_with_strong_inhibitor, other_medications_unchanged | fail on apixaban_halved_with_strong_inhibitor, other_medications_unchanged | yes |
| doac_dose_reasoning | switched_to_warfarin | fail on edoxaban_patient_switched, other_medications_unchanged | fail on edoxaban_patient_switched, other_medications_unchanged | yes |

