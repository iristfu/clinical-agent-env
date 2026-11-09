# med_rec_discharge

## The request

> Valley General has sent over discharge summaries for the patients it discharged since 9/17. Reconcile each of those patients' outpatient medication lists so they reflect exactly what each patient should currently be taking. Don't change anyone else's chart. When you're done, call submit with the list of patient ids you reconciled.

Before round 4 this was a single-patient task about Denise Carter. It passed 9 of 9 pilot trials across three versions, so it was redesigned to cover every recent discharge (see "Calibration history").

## Who is in scope

Five Valley General discharge summaries are on the panel. A search for "discharge summary" finds all five, and the dates decide which are in scope.

| Patient | Discharged | In scope |
|---|---|---|
| pt-1012 Denise Carter | 9/28, hypertensive urgency | yes |
| pt-1025 Barbara Lewis | 9/23, cellulitis | yes |
| pt-1006 Michael O'Brien | 9/22, NSTEMI | yes |
| pt-1008 Harold Bennett | 8/30, pneumonia | no, before 9/17 (and his apixaban dose, which is wrong, belongs to another task) |
| pt-1029 Margaret Allen | 8/15, pulmonary embolism | no, before 9/17 |

## Expected final active lists

**Denise Carter (pt-1012).** Sources: the 9/28 discharge summary (narrative), the 9/30 phone note and the 10/1 phone note.

| Medication | Expected | Where it comes from |
|---|---|---|
| lisinopril 20 mg daily | stopped | discharge summary, ACE inhibitor cough |
| losartan | 100 mg once daily | started at 50 mg at discharge, raised to 100 mg by the 9/30 phone note |
| hydrochlorothiazide 25 mg daily | stopped | discharge summary, hyponatremia |
| metoprolol tartrate 25 mg twice daily | stopped | discharge summary |
| metoprolol succinate ER | 50 mg once daily | discharge summary |
| metformin | 1000 mg twice daily | discharge summary (was 500 mg twice daily) |
| empagliflozin | 10 mg once daily | started at discharge, stopped by the 9/30 phone note, restarted by the 10/1 phone note |
| aspirin 81, atorvastatin 40, omeprazole 20, all daily | unchanged | discharge summary says continue; pantoprazole was only an inpatient formulary substitute for omeprazole |
| cefpodoxime | not on the list | course completed with the 9/30 evening dose |
| pantoprazole | not on the list | inpatient formulary substitution |

**Michael O'Brien (pt-1006).** Sources: the 9/22 NSTEMI discharge summary and the 9/25 phone note.

| Medication | Expected | Where it comes from |
|---|---|---|
| aspirin 81 mg daily | unchanged | continue indefinitely |
| clopidogrel | 75 mg once daily | started for 12 months of dual antiplatelet therapy after a drug-eluting stent |
| metoprolol succinate ER | 50 mg once daily | increased from 25 mg |
| atorvastatin 80 mg daily | unchanged | continue |
| pantoprazole | 40 mg once daily | deliberately started at discharge for GI protection on dual antiplatelet therapy |
| lisinopril | not on the list | started at 5 mg at discharge, stopped by the 9/25 phone note for orthostatic symptoms |
| metformin 500 mg twice daily | unchanged | held 48 hours after contrast, resumed 9/21 at home dose |

**Barbara Lewis (pt-1025).** Source: the 9/23 cellulitis discharge summary.

| Medication | Expected | Where it comes from |
|---|---|---|
| lisinopril | 5 mg once daily | reduced from 10 mg after acute kidney injury |
| metformin 500 mg twice daily, rosuvastatin 10 mg daily | unchanged | "resume her other home medications at their usual doses" |
| cephalexin | not on the list | course ended with the 9/29 dose |

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| denise_list_matches_expected | Denise's active list equals her table exactly (drug, dose, unit, frequency), no duplicates |
| michael_list_matches_expected | Same for Michael |
| barbara_list_matches_expected | Same for Barbara |
| no_changes_to_other_patients | Nothing changed in any other chart, including the two out-of-window discharges |

Diagnostic checks: one per trap (denise_losartan_100_mg_daily, denise_empagliflozin_restarted, denise_no_inpatient_pantoprazole, michael_pantoprazole_started, michael_lisinopril_stopped_by_phone_note, barbara_completed_cephalexin_not_active and so on), plus submitted_list_matches_scope. The partial score is the mean Jaccard overlap across the three patients.

## What the grader deliberately tolerates

- Editing in place or discontinuing and reordering, in any sequence. Tested by alt_correct_two_step_and_reorders, which also starts Michael's lisinopril and then stops it.
- "every 12 hours" for twice daily and "every 24 hours" for once daily.
- Recording a finished antibiotic course and marking it stopped, as long as it isn't active at the end (alt_correct_documents_completed_course).
- Adding intolerances (such as Denise's ACE inhibitor cough) or ordering the follow-up labs the discharge summaries ask for, on the three in-scope patients. All pilot trials on the old version did both.

## Why it's hard

About fifteen decisions across three patients have to all be right, and the same surface pattern means different things in different charts. Pantoprazole is an inpatient-only substitution for Denise and a deliberate discharge start for Michael. Each patient has a superseding note or a finished course that the discharge summary alone gets wrong. The run also has to find the in-scope patients itself and leave Harold and Margaret alone.

## Difficulty knobs

- Easier. Name the three patients in the prompt, or remove the out-of-window decoys.
- Harder. Add a fourth in-scope discharge whose summary arrived as a "Scanned outside record" note type rather than "Discharge summary", so a search on the type misses it.

## Reference solution

Search notes for "discharge summary", keep the three since 9/17, read each patient's notes, apply the changes above, submit. See reference.py.

## Calibration history

- Rounds 1 to 3 (Denise only): 3/3, 3/3, 3/3. The changes were writing the discharge changes as narrative, adding the finished cefpodoxime course and the pantoprazole substitution, and adding the 10/1 empagliflozin restart. Every trial read all of her notes and applied every change.
- Round 4: redesigned to cover every recent discharge, adding Michael and Barbara and two out-of-window decoys.
