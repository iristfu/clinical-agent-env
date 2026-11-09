# med_rec_discharge

## The request

> Denise Carter (DOB 1962-05-09) was discharged from Valley General on 9/28. Her outpatient medication list hasn't been updated since. Please reconcile it so it reflects exactly what she should currently be taking. Call submit when you're done.

## Sources in the chart

- The structured medication list still shows the 7 pre-admission medications.
- The 9/28 discharge summary (note-1012-2) describes the medication changes in a narrative paragraph and says to continue all other home medications. Its hospital course also mentions a 7-day cefpodoxime course for an E. coli UTI whose final dose was the evening of 9/30, and inpatient-only medications, including pantoprazole 40 mg daily given as a formulary substitution for her home omeprazole.
- The 9/30 telephone note (note-1012-3), written after discharge, raises losartan to 100 mg and discontinues empagliflozin, which she never filled.
- The 10/1 telephone note (note-1012-4), written this morning, restarts empagliflozin 10 mg once daily after she got it through a manufacturer savings program.

## Expected final active list

| Medication | Expected | Where it comes from |
|---|---|---|
| lisinopril 20 mg daily | stopped | discharge summary, ACE inhibitor cough |
| losartan | 100 mg once daily | started at 50 mg in the discharge summary, raised to 100 mg by the 9/30 phone note |
| hydrochlorothiazide 25 mg daily | stopped | discharge summary, hyponatremia |
| metoprolol tartrate 25 mg twice daily | stopped | discharge summary |
| metoprolol succinate ER | 50 mg once daily | discharge summary |
| metformin | 1000 mg twice daily | discharge summary (was 500 mg twice daily) |
| empagliflozin | 10 mg once daily | started at discharge, discontinued by the 9/30 phone note, restarted by the 10/1 phone note |
| aspirin 81 mg daily | unchanged | discharge summary says continue |
| atorvastatin 40 mg daily | unchanged | discharge summary says continue |
| omeprazole 20 mg daily | unchanged | "continue all other home medications"; pantoprazole was only the inpatient formulary substitute |
| cefpodoxime | not on the list | course completed with the 9/30 evening dose; today is 10/1 |
| pantoprazole | not on the list | inpatient formulary substitution, not a discharge change |

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| active_list_matches_expected | The active list equals the table above exactly (drug, dose, unit, frequency), with no duplicates |
| no_changes_to_other_patients | Nothing changed in any other chart |

One diagnostic check per intended change (lisinopril_stopped, losartan_100_mg_daily, completed_cefpodoxime_not_active, no_inpatient_pantoprazole_substitution and so on) makes failures readable at a glance. The partial score is the Jaccard overlap of the final list with the expected list.

## What the grader deliberately tolerates

- Editing in place or discontinuing and reordering, in any sequence. One control applies the discharge dose of losartan first and then updates it.
- "every 12 hours" for twice daily and "every 24 hours" for once daily.
- Adding an intolerance for lisinopril (cough), since allergy entries aren't graded here. All three pilot-1 trials did this.
- Ordering the BMP the discharge summary asks for. All three pilot-1 trials did this; lab orders aren't graded here.
- Recording the cefpodoxime course and marking it stopped, as long as it isn't active at the end (control alt_correct_documents_completed_course).

## Why it's hard

Seven changes have to all be right, and two things the discharge summary mentions must be left off. The cefpodoxime course ended the evening before today, so copying it onto the active list is wrong even though the summary says to "continue cefpodoxime as above until the course is complete". Pantoprazole appears as a medication she took in hospital, but it replaced her home omeprazole only because of the hospital formulary, and the summary says to continue home medications unchanged. Carrying it home would leave her on two PPIs, or on the wrong one. The changes are written as a narrative paragraph rather than a numbered list. The 9/30 phone note supersedes the discharge summary on two of them, and the 10/1 phone note then reverses the 9/30 decision on empagliflozin. A run that stops after the discharge summary ends with losartan 50 mg. A run that stops after the 9/30 note leaves empagliflozin off. The metoprolol change is a formulation switch, so the old tartrate entry has to be stopped as well as the new one added. The formulary resolves "metoprolol" as ambiguous and returns both options, so picking the right one is the model's job.

## Difficulty knobs

- Applied in round 2. Wrote the discharge changes as a narrative paragraph instead of a numbered list.
- Applied in round 2. Added the completed cefpodoxime course and the inpatient pantoprazole substitution. In pilot 1 every trial read all three notes and applied all seven changes correctly.
- Easier. Delete the 10/1 or 9/30 phone note, or remove the cefpodoxime and pantoprazole sentences.
- Applied in round 3. Added the 10/1 note that restarts empagliflozin after a savings card, so the latest instruction has to win twice. New control stopped_at_9_30_note.
- Harder. Give her more post-discharge notes that don't change medications (portal messages, a home health intake), so the two that do are mixed in with them.
