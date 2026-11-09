# Run report 20261109-115714_controls

Policy controls, model None, effort model default, commit 7be0375dd0, initial state hash 73934ac27f7c9181.

## Grader controls

| Task | Control | Expected | Got | OK |
|---|---|---|---|---|
| apixaban_dose | alt_correct_discontinue_and_reorder | pass | pass | yes |
| apixaban_dose | do_nothing | fail on apixaban_2_5_mg_twice_daily | fail on apixaban_2_5_mg_twice_daily | yes |
| apixaban_dose | new_order_without_stopping_old | fail on apixaban_2_5_mg_twice_daily, exactly_one_active_apixaban | fail on apixaban_2_5_mg_twice_daily, exactly_one_active_apixaban | yes |
| apixaban_dose | reduced_and_stopped_furosemide | fail on other_medications_unchanged | fail on other_medications_unchanged | yes |
| apixaban_dose | reduced_to_once_daily | fail on apixaban_2_5_mg_twice_daily | fail on apixaban_2_5_mg_twice_daily | yes |
| med_rec_discharge | alt_correct_documents_completed_course | pass | pass | yes |
| med_rec_discharge | alt_correct_two_step_losartan | pass | pass | yes |
| med_rec_discharge | continued_completed_cefpodoxime | fail on active_list_matches_expected | fail on active_list_matches_expected | yes |
| med_rec_discharge | discharge_summary_only | fail on active_list_matches_expected | fail on active_list_matches_expected | yes |
| med_rec_discharge | do_nothing | fail on active_list_matches_expected | fail on active_list_matches_expected | yes |
| med_rec_discharge | forgot_to_stop_tartrate | fail on active_list_matches_expected | fail on active_list_matches_expected | yes |
| med_rec_discharge | kept_inpatient_pantoprazole | fail on active_list_matches_expected | fail on active_list_matches_expected | yes |
| med_rec_discharge | stopped_at_9_30_note | fail on active_list_matches_expected | fail on active_list_matches_expected | yes |
| med_rec_discharge | swapped_to_metformin_er | fail on active_list_matches_expected | fail on active_list_matches_expected | yes |
| panel_a1c | alt_correct_synonyms_and_order | pass | pass | yes |
| panel_a1c | do_nothing | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | duplicate_order | fail on no_duplicate_a1c_orders | fail on no_duplicate_a1c_orders | yes |
| panel_a1c | ignored_outside_a1c_in_note | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | metformin_means_diabetes | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | missed_note_only_diagnosis | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | structured_codes_only | fail on no_order_for_deceased_patient, ordered_set_matches_expected | fail on no_order_for_deceased_patient, ordered_set_matches_expected | yes |
| strep_allergy | alt_correct_azithromycin_taper_as_two_orders | pass | pass | yes |
| strep_allergy | alt_correct_clindamycin | pass | pass | yes |
| strep_allergy | amoxicillin_first_line | fail on antibiotic_appropriate_for_anaphylaxis_history, no_penicillin_class_order, penicillin_allergy_added | fail on antibiotic_appropriate_for_anaphylaxis_history, no_penicillin_class_order, penicillin_allergy_added | yes |
| strep_allergy | azithromycin_without_allergy_update | fail on penicillin_allergy_added | fail on penicillin_allergy_added | yes |
| strep_allergy | cephalexin_despite_anaphylaxis | fail on antibiotic_appropriate_for_anaphylaxis_history | fail on antibiotic_appropriate_for_anaphylaxis_history | yes |
| strep_allergy | do_nothing | fail on antibiotic_appropriate_for_anaphylaxis_history, one_antibiotic_order_for_patient, penicillin_allergy_added | fail on antibiotic_appropriate_for_anaphylaxis_history, one_antibiotic_order_for_patient, penicillin_allergy_added | yes |
| strep_allergy | duplicate_azithromycin_orders | fail on antibiotic_appropriate_for_anaphylaxis_history, one_antibiotic_order_for_patient | fail on antibiotic_appropriate_for_anaphylaxis_history, one_antibiotic_order_for_patient | yes |
| strep_allergy | right_drug_wrong_maria_lopez | fail on antibiotic_appropriate_for_anaphylaxis_history, no_changes_to_other_patients, one_antibiotic_order_for_patient, penicillin_allergy_added | fail on antibiotic_appropriate_for_anaphylaxis_history, no_changes_to_other_patients, one_antibiotic_order_for_patient, penicillin_allergy_added | yes |

