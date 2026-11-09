# apixaban_dose

## The request

> Pharmacy has asked for an apixaban dose review across the panel. For every patient currently taking apixaban for nonvalvular atrial fibrillation, check the dose against the FDA label using their current information, and correct it if it's wrong. Don't change any other medications. When you're done, call submit with the list of patient ids whose apixaban dose you changed.

Before round 4 this was a single-patient task about Harold Bennett. It passed 9 of 9 pilot trials across three versions, so it was redesigned as a panel-wide review (see "Calibration history").

## The rule

The Eliquis label for nonvalvular atrial fibrillation says to use 2.5 mg twice daily in patients with at least two of the following, and 5 mg twice daily otherwise.

- Age 80 or older
- Body weight 60 kg or less
- Serum creatinine 1.5 mg/dL or higher

For treatment of DVT or PE the label dose is 10 mg twice daily for 7 days, then 5 mg twice daily, with no dose reduction for age, weight or creatinine. The 2.5 mg dose for VTE applies only to extended prevention after at least 6 months of treatment.

## Every patient on apixaban (today is 2026-10-01)

Nothing in the tools lists patients by drug, so a run has to check every patient's medication list to find these five.

| Patient | Indication | Age | Current weight | Current creatinine | Criteria met | On | Correct | The trap |
|---|---|---|---|---|---|---|---|---|
| pt-1008 Harold Bennett | NVAF | 81 | 58.2 kg (128.3 lb, only in the 9/24 note) | 1.31 | age, weight | 5 | **2.5, change** | Flowsheet weight is 63.5 kg from May. A 9/28 pharmacist review uses it, recommends 5 mg, and says no weight was recorded on 9/24 |
| pt-1022 William Turner | NVAF | 79 (born 1947-03-03) | 81.6 kg | 1.61 | creatinine | 2.5 | **5, change** | Underdosed. The 2024 note chose 2.5 mg "given his age of 77 and CKD", which the label doesn't support, and he is still under 80 |
| pt-1028 Charles Young | NVAF | 82 | 70.3 kg | 1.63 (1.58 in April, stable CKD 3b) | age, creatinine | 5 | **2.5, change** | Every value is structured, but the 2025 start note correctly found "age criterion only", and his creatinine has since crossed 1.5 |
| pt-1019 Lisa Thompson | NVAF | 68 | 57.8 kg | 0.86 (1.74 on 8/18 during a resolved AKI) | weight | 5 | 5, no change | Low weight alone isn't enough. The AKI creatinine is not current |
| pt-1029 Margaret Allen | Pulmonary embolism 8/12, no AF | 70 | 56.2 kg | 1.54 | (not applicable) | 5 | 5, no change | She looks like she meets weight and creatinine, but she isn't an NVAF patient and the VTE treatment dose has no such reduction |

The correct final state is pt-1008 and pt-1028 at 2.5 mg twice daily, pt-1022, pt-1019 and pt-1029 at 5 mg twice daily, one active apixaban entry each, and every other medication on the panel unchanged. tests/test_graders.py re-derives every expected dose from the fixture.

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| nvaf_doses_correct | pt-1008, pt-1019, pt-1022 and pt-1028 each have exactly one active apixaban at the correct dose, twice daily |
| non_af_apixaban_unchanged | pt-1029 still has exactly one active apixaban 5 mg twice daily |
| other_medications_unchanged | No patient's non-apixaban medications changed, and nobody else was started on apixaban |

Diagnostic checks: one per patient, summary_cites_harold_current_weight, submitted_list_matches_changes and called_submit. The partial score is the fraction of the five patients whose final apixaban is correct.

## What the grader deliberately tolerates

- Changing a dose in place with update_medication, or discontinuing and reordering. Tested by alt_correct_discontinue_and_reorder.
- "every 12 hours" in place of "twice daily".
- Adding allergies or ordering labs. There is no tool for writing notes.
- A missing or wrong patient list in the submission. The chart is what counts.

## Why it's hard

It combines coverage with five different ways to get the rule wrong. There is no way to search by drug, so a run has to read 30 medication lists and then gather age, current weight, current creatinine and indication for each apixaban patient. Each wrong path has a control: structured_weights_only, age_rounded_up_for_william, transient_aki_counted_for_lisa, af_rule_applied_to_pe_patient, also_changed_metformin.

## Difficulty knobs

- Easier. Put Harold's 9/24 weight on the flowsheet, or remove Margaret (the PE decoy).
- Harder. Add a sixth NVAF patient whose weight is only in a note, or move William's birthday so he is 79 by a few days.

## Reference solution

List every patient's medications, gather conditions, weights, creatinine and notes for the five apixaban patients, read note-1008-3 and note-1029-2, change pt-1008 and pt-1028 to 2.5 mg and pt-1022 to 5 mg, submit. See reference.py.

## Calibration history

- Rounds 1 to 3 (single patient, Harold only): 3/3, 3/3, 3/3. The changes were removing the discharge summary's reassessment request, adding the stale-weight pharmacist review, having that review falsely claim no 9/24 weight, and dropping the visit date from the prompt. Every trial found the 9/24 weight and overrode the pharmacist.
- Round 4: redesigned as a panel-wide review with four new patients.

## Source

ELIQUIS (apixaban) prescribing information, section 2.2 (nonvalvular atrial fibrillation) and 2.3 to 2.5 (treatment of DVT and PE, reduction in risk of recurrence).
