# Run report 20261109-142157_controls_doac

Policy controls, model None, effort model default, commit f0863ab9b5 (dirty), initial state hash eaa87f3c56ec380b.

## Grader controls

| Task | Control | Expected | Got | OK |
|---|---|---|---|---|
| doac_dose_reasoning | age_80_reduction_for_apixaban | fail on apixaban_raised_when_one_criterion | fail on apixaban_raised_when_one_criterion | yes |
| doac_dose_reasoning | also_changed_metformin | fail on other_medications_unchanged | fail on other_medications_unchanged | yes |
| doac_dose_reasoning | alt_correct_stop_and_reorder_rivaroxaban | pass | pass | yes |
| doac_dose_reasoning | alt_correct_switch_to_dabigatran | pass | pass | yes |
| doac_dose_reasoning | alt_correct_switch_to_rivaroxaban | pass | pass | yes |
| doac_dose_reasoning | apixaban_style_rule_for_rivaroxaban | fail on rivaroxaban_reduced_for_low_crcl | fail on rivaroxaban_reduced_for_low_crcl | yes |
| doac_dose_reasoning | changed_correct_apixaban | fail on correct_doses_left_alone | fail on correct_doses_left_alone | yes |
| doac_dose_reasoning | changed_correct_rivaroxaban | fail on correct_doses_left_alone | fail on correct_doses_left_alone | yes |
| doac_dose_reasoning | dabigatran_reduced_too_far | fail on dabigatran_reduced_with_dronedarone | fail on dabigatran_reduced_with_dronedarone | yes |
| doac_dose_reasoning | do_nothing | fail on apixaban_raised_when_one_criterion, dabigatran_reduced_with_dronedarone, edoxaban_patient_switched, rivaroxaban_reduced_for_low_crcl | fail on apixaban_raised_when_one_criterion, dabigatran_reduced_with_dronedarone, edoxaban_patient_switched, rivaroxaban_reduced_for_low_crcl | yes |
| doac_dose_reasoning | duplicate_rivaroxaban_orders | fail on rivaroxaban_reduced_for_low_crcl | fail on rivaroxaban_reduced_for_low_crcl | yes |
| doac_dose_reasoning | edoxaban_kept_and_second_doac_added | fail on edoxaban_patient_switched | fail on edoxaban_patient_switched | yes |
| doac_dose_reasoning | edoxaban_reduced_instead_of_switched | fail on edoxaban_patient_switched | fail on edoxaban_patient_switched | yes |
| doac_dose_reasoning | keeps_edoxaban | fail on edoxaban_patient_switched | fail on edoxaban_patient_switched | yes |
| doac_dose_reasoning | misses_dronedarone_interaction | fail on dabigatran_reduced_with_dronedarone | fail on dabigatran_reduced_with_dronedarone | yes |
| doac_dose_reasoning | rivaroxaban_wrong_frequency | fail on rivaroxaban_reduced_for_low_crcl | fail on rivaroxaban_reduced_for_low_crcl | yes |
| doac_dose_reasoning | switched_to_warfarin | fail on edoxaban_patient_switched, other_medications_unchanged | fail on edoxaban_patient_switched, other_medications_unchanged | yes |

