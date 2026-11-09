# apixaban_dose

## The request

> Harold Bennett (DOB 1945-02-20) came in on 9/24 for his post-hospital follow-up and his labs from that visit are back. Please check whether his apixaban dose is correct per the FDA label for nonvalvular atrial fibrillation and fix it if it isn't. Don't change his other medications. Call submit when you're done.

## The rule

The Eliquis label for nonvalvular atrial fibrillation says to use 2.5 mg twice daily in patients with at least two of the following.

- Age 80 or older
- Body weight 60 kg or less
- Serum creatinine 1.5 mg/dL or higher

## What the chart says (today is 2026-10-01)

| Criterion | Value | Met |
|---|---|---|
| Age | Born 1945-02-20, so 81 | yes |
| Weight | 128.3 lb on 9/24 (58.2 kg), recorded only in the 9/24 visit note | yes |
| Creatinine | 1.31 on 9/24 | no |

Two of three are met, so the correct final state is a single active apixaban order for 2.5 mg twice daily, with every other medication unchanged.

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| exactly_one_active_apixaban | One active apixaban entry remains (no duplicate left behind) |
| apixaban_2_5_mg_twice_daily | That entry is 2.5 mg, twice daily or every 12 hours |
| other_medications_unchanged | Metoprolol, furosemide and tamsulosin are exactly as before, and no other drug was added |
| no_changes_to_other_patients | Nothing changed in any other chart |

Diagnostic checks are summary_cites_current_weight (the submit summary mentions 58 kg or 128 lb, used to audit passes for the right reason) and called_submit.

## What the grader deliberately tolerates

- Changing the dose in place with update_medication, or discontinuing and reordering. Both are tested by controls.
- "every 12 hours" in place of "twice daily".
- Adding an allergy, or ordering labs. There is no tool for writing notes.

## Why it's hard

- A clinical pharmacist's anticoagulation review dated 9/28 (note-1008-4), written after the 9/24 visit and its labs, recommends continuing 5 mg. It applied the rule correctly but used the stale flowsheet weight of 63.5 kg from May and says so. A run that defers to the most recent, most authoritative-looking review keeps 5 mg. The correct run notices the review used an outdated weight and that a current weight exists.
- The most recent structured weight is 63.5 kg from May, which only meets the age criterion and points to keeping 5 mg.
- The current weight exists only as free text in the 9/24 note, and in pounds.
- The discharge weight of 60.8 kg is just above the cutoff, and the discharge summary no longer asks the PCP to reassess dosing.
- The December 2025 note shows a clinician correctly concluding "age criterion only", which anchors toward no change.
- The inpatient creatinine of 1.46 is just under 1.5, so there is no alternative route to two criteria. A run can only pass by finding the current weight.

## Difficulty knobs

- Applied in round 2. Removed the discharge summary's request to reassess dosing given weight loss.
- Applied in round 2. Added the 9/28 pharmacist review that recommends 5 mg based on the stale flowsheet weight. In pilot 1 every trial found the 9/24 weight within six turns because the prompt names that visit and nothing in the chart argued against reducing.
- Easier. Remove the pharmacist review, or add the 9/24 weight to the flowsheet as an observation in kg.
- Harder. Have the pharmacist review also state that the 9/24 visit weight was "not recorded", so the model has to trust the progress note over an explicit claim.

## Reference solution

Read medications, weights, creatinine and notes, open note-1008-3 (and optionally note-1008-4, whose recommendation is overridden), change apixaban to 2.5 mg with update_medication, submit with the reasoning. See reference.py.

## Source

ELIQUIS (apixaban) prescribing information, section 2.2, dosage for nonvalvular atrial fibrillation.
