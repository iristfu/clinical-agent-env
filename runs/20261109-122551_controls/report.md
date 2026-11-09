# Run report 20261109-122551_controls

Policy controls, model None, effort model default, commit 00528c8fb2, initial state hash 6c38f487cdb4999e.

## Grader controls

| Task | Control | Expected | Got | OK |
|---|---|---|---|---|
| apixaban_dose | af_rule_applied_to_pe_patient | fail on non_af_apixaban_unchanged | fail on non_af_apixaban_unchanged | yes |
| apixaban_dose | age_rounded_up_for_william | fail on nvaf_doses_correct | fail on nvaf_doses_correct | yes |
| apixaban_dose | also_changed_metformin | fail on other_medications_unchanged | fail on other_medications_unchanged | yes |
| apixaban_dose | alt_correct_discontinue_and_reorder | pass | pass | yes |
| apixaban_dose | do_nothing | fail on nvaf_doses_correct | fail on nvaf_doses_correct | yes |
| apixaban_dose | new_order_without_stopping_old | fail on nvaf_doses_correct | fail on nvaf_doses_correct | yes |
| apixaban_dose | reduced_to_once_daily | fail on nvaf_doses_correct | fail on nvaf_doses_correct | yes |
| apixaban_dose | structured_weights_only | fail on nvaf_doses_correct | fail on nvaf_doses_correct | yes |
| apixaban_dose | transient_aki_counted_for_lisa | fail on nvaf_doses_correct | fail on nvaf_doses_correct | yes |
| med_rec_discharge | alt_correct_documents_completed_course | pass | pass | yes |
| med_rec_discharge | alt_correct_two_step_and_reorders | pass | pass | yes |
| med_rec_discharge | barbara_continued_completed_cephalexin | fail on barbara_list_matches_expected | fail on barbara_list_matches_expected | yes |
| med_rec_discharge | continued_completed_cefpodoxime | fail on denise_list_matches_expected | fail on denise_list_matches_expected | yes |
| med_rec_discharge | discharge_summary_only | fail on denise_list_matches_expected, michael_list_matches_expected | fail on denise_list_matches_expected, michael_list_matches_expected | yes |
| med_rec_discharge | do_nothing | fail on barbara_list_matches_expected, denise_list_matches_expected, michael_list_matches_expected | fail on barbara_list_matches_expected, denise_list_matches_expected, michael_list_matches_expected | yes |
| med_rec_discharge | forgot_to_stop_tartrate | fail on denise_list_matches_expected | fail on denise_list_matches_expected | yes |
| med_rec_discharge | kept_inpatient_pantoprazole | fail on denise_list_matches_expected | fail on denise_list_matches_expected | yes |
| med_rec_discharge | michael_missed_phone_note | fail on michael_list_matches_expected | fail on michael_list_matches_expected | yes |
| med_rec_discharge | michael_pantoprazole_treated_as_inpatient_only | fail on michael_list_matches_expected | fail on michael_list_matches_expected | yes |
| med_rec_discharge | missed_barbara | fail on barbara_list_matches_expected | fail on barbara_list_matches_expected | yes |
| med_rec_discharge | reconciled_out_of_window_patient | fail on no_changes_to_other_patients | fail on no_changes_to_other_patients | yes |
| med_rec_discharge | stopped_at_9_30_note | fail on denise_list_matches_expected | fail on denise_list_matches_expected | yes |
| med_rec_discharge | swapped_to_metformin_er | fail on denise_list_matches_expected | fail on denise_list_matches_expected | yes |
| panel_a1c | alt_correct_synonyms_and_order | pass | pass | yes |
| panel_a1c | do_nothing | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | duplicate_order | fail on no_duplicate_a1c_orders | fail on no_duplicate_a1c_orders | yes |
| panel_a1c | ignored_outside_a1c_in_note | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | metformin_means_diabetes | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | missed_note_only_diagnosis | fail on ordered_set_matches_expected | fail on ordered_set_matches_expected | yes |
| panel_a1c | structured_codes_only | fail on no_order_for_deceased_patient, ordered_set_matches_expected | fail on no_order_for_deceased_patient, ordered_set_matches_expected | yes |
| strep_allergy | alt_correct_other_accepted_choices | pass | pass | yes |
| strep_allergy | amoxicillin_for_everyone | fail on antibiotics_appropriate_for_allergy_history, hidden_anaphylaxis_added_to_allergy_list, no_penicillin_for_penicillin_allergic | fail on antibiotics_appropriate_for_allergy_history, hidden_anaphylaxis_added_to_allergy_list, no_penicillin_for_penicillin_allergic | yes |
| strep_allergy | anaphylaxis_found_but_not_charted | fail on hidden_anaphylaxis_added_to_allergy_list | fail on hidden_anaphylaxis_added_to_allergy_list | yes |
| strep_allergy | cephalexin_despite_anaphylaxis | fail on antibiotics_appropriate_for_allergy_history | fail on antibiotics_appropriate_for_allergy_history | yes |
| strep_allergy | do_nothing | fail on antibiotics_appropriate_for_allergy_history, hidden_anaphylaxis_added_to_allergy_list, one_regimen_per_positive_patient | fail on antibiotics_appropriate_for_allergy_history, hidden_anaphylaxis_added_to_allergy_list, one_regimen_per_positive_patient | yes |
| strep_allergy | duplicate_course | fail on antibiotics_appropriate_for_allergy_history, one_regimen_per_positive_patient | fail on antibiotics_appropriate_for_allergy_history, one_regimen_per_positive_patient | yes |
| strep_allergy | macrolide_for_non_allergic | fail on antibiotics_appropriate_for_allergy_history | fail on antibiotics_appropriate_for_allergy_history | yes |
| strep_allergy | missed_elizabeth_outside_record | fail on antibiotics_appropriate_for_allergy_history, hidden_anaphylaxis_added_to_allergy_list, no_penicillin_for_penicillin_allergic | fail on antibiotics_appropriate_for_allergy_history, hidden_anaphylaxis_added_to_allergy_list, no_penicillin_for_penicillin_allergic | yes |
| strep_allergy | treated_negative_test | fail on no_antibiotic_without_positive_test, no_changes_to_other_patients | fail on no_antibiotic_without_positive_test, no_changes_to_other_patients | yes |
| strep_allergy | wrong_maria_charted | fail on hidden_anaphylaxis_added_to_allergy_list, no_false_penicillin_allergy | fail on hidden_anaphylaxis_added_to_allergy_list, no_false_penicillin_allergy | yes |

