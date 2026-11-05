# med_rec_discharge

## The request

> Denise Carter (DOB 1962-05-09) was discharged from Valley General on 9/28. Her outpatient medication list hasn't been updated since. Please reconcile it so it reflects exactly what she should currently be taking. Call submit when you're done.

## Sources in the chart

- The structured medication list still shows the 7 pre-admission medications.
- The 9/28 discharge summary (note-1012-2) lists six changes in prose and says to continue all other home medications.
- The 9/30 telephone note (note-1012-3), written after discharge, raises losartan to 100 mg and discontinues empagliflozin, which she never filled.

## Expected final active list

| Medication | Expected | Where it comes from |
|---|---|---|
| lisinopril 20 mg daily | stopped | discharge summary, ACE inhibitor cough |
| losartan | 100 mg once daily | started at 50 mg in the discharge summary, raised to 100 mg by the 9/30 phone note |
| hydrochlorothiazide 25 mg daily | stopped | discharge summary, hyponatremia |
| metoprolol tartrate 25 mg twice daily | stopped | discharge summary |
| metoprolol succinate ER | 50 mg once daily | discharge summary |
| metformin | 1000 mg twice daily | discharge summary (was 500 mg twice daily) |
| empagliflozin | not on the list | started at discharge, discontinued by the 9/30 phone note |
| aspirin 81 mg daily | unchanged | discharge summary says continue |
| atorvastatin 40 mg daily | unchanged | discharge summary says continue |
| omeprazole 20 mg daily | unchanged | "continue all other home medications" |

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| active_list_matches_expected | The active list equals the table above exactly (drug, dose, unit, frequency), with no duplicates |
| no_changes_to_other_patients | Nothing changed in any other chart |

One diagnostic check per intended change (lisinopril_stopped, losartan_100_mg_daily and so on) makes failures readable at a glance. The partial score is the Jaccard overlap of the final list with the expected list.

## What the grader deliberately tolerates

- Editing in place or discontinuing and reordering, in any sequence. One control applies the discharge dose of losartan first and then updates it.
- "every 12 hours" for twice daily and "every 24 hours" for once daily.
- Adding an intolerance for lisinopril (cough), since allergy entries aren't graded here.

## Why it's hard

Seven changes have to all be right. The phone note supersedes the discharge summary on two of them, and a run that stops reading after the discharge summary ends with losartan 50 mg and an active empagliflozin. The metoprolol change is a formulation switch, so the old tartrate entry has to be stopped as well as the new one added. The formulary resolves "metoprolol" as ambiguous and returns both options, so picking the right one is the model's job.

## Difficulty knobs

- Easier. Delete the 9/30 phone note, leaving only the discharge summary.
- Harder. Write the discharge changes as a narrative paragraph instead of a numbered list.
