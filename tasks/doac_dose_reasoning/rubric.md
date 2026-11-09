# doac_dose_reasoning

Draft, not yet reviewed by a clinician. The label rules below are written from the prescribing information and must be
checked against the current labels before this task is used for anything scored.

## The request

> The anticoagulation clinic has asked for a DOAC dose review. For every patient currently taking a direct oral anticoagulant for nonvalvular atrial fibrillation, check the dose against the FDA label using their current age, weight, creatinine and medications, and correct it if it's wrong. If a drug isn't appropriate for a patient, switch them to another DOAC at its labeled dose. Don't change any other medications. When you're done, call submit with the list of patient ids whose anticoagulant you changed.

This task is the counterpart to the other three. There the deciding fact is somewhere in the chart and the model has to go and find it, and every scored failure was a failure to look. Here every fact is a structured value on the patient's chart (age, latest weight, latest creatinine, medication list), there are no notes, and a failure can only come from applying the labels wrongly. It uses its own seventeen-patient fixture (env/fixtures/doac.json) so the 30-patient panel and the frozen tasks are unchanged.

## The rules

Creatinine clearance (CrCl) is Cockcroft-Gault on actual body weight (the labels' own convention): (140 - age) x weight in kg / (72 x creatinine), times 0.85 for women.

- Apixaban, NVAF: 2.5 mg twice daily if at least two of age 80 or older, weight 60 kg or less, creatinine 1.5 mg/dL or higher. Otherwise 5 mg twice daily. Uses serum creatinine directly, not CrCl. With a combined strong CYP3A4 and P-gp inhibitor (ketoconazole, itraconazole, ritonavir), reduce a 5 mg or 10 mg dose by half, and avoid the combination if the dose is already 2.5 mg. Clarithromycin is the label's exception: no adjustment (section 7.1 of the Eliquis label revised 4/2025, checked on DailyMed; section 2.6 gives the general halving rule and does not mention it, and older labels listed clarithromycin among the inhibitors that need the reduction).
- Rivaroxaban, NVAF: 20 mg once daily with the evening meal if CrCl is above 50 mL/min, 15 mg once daily if CrCl is 50 or below.
- Dabigatran, NVAF: 150 mg twice daily if CrCl is above 30. With CrCl 30 to 50 and concomitant dronedarone or systemic ketoconazole, 75 mg twice daily. With CrCl 15 to 30, 75 mg twice daily.
- Edoxaban, NVAF: 60 mg once daily if CrCl is above 50 to 95, 30 mg once daily if CrCl is 15 to 50. Not recommended if CrCl is above 95, because of a higher rate of ischemic stroke than warfarin in that group.

## The seventeen patients (today is 2026-10-01)

| Patient | On | Age, sex | Weight | Creatinine | CrCl | Correct | The trap |
|---|---|---|---|---|---|---|---|
| pt-2001 Daniel Brooks | edoxaban 60 mg daily | 62, M | 104 kg | 0.7 | 161 | Stop edoxaban, switch to apixaban 5 mg twice daily, rivaroxaban 20 mg daily or dabigatran 150 mg twice daily | Good kidney function is the contraindication, the opposite of most renal rules |
| pt-2002 Priya Raman | rivaroxaban 20 mg daily | 74, F | 52 kg | 1.4 | 28.9 | 15 mg once daily | Creatinine is under 1.5 and age under 80, so an apixaban-style rule would leave it alone |
| pt-2003 Walter Novak | dabigatran 150 mg twice daily, dronedarone | 78, M | 78 kg | 1.7 | 39.5 | 75 mg twice daily | CrCl alone doesn't lower the dose in this band. The interaction does |
| pt-2004 Samuel Greene | apixaban 2.5 mg twice daily, diltiazem | 81, M | 88 kg | 1.2 now (1.6 on 2026-01-20) | n/a | 5 mg twice daily | Age 80 or older is only one criterion. The January creatinine is stale. Diltiazem is not a reason to reduce |
| pt-2005 Eleanor Voss | apixaban 2.5 mg twice daily | 83, F | 57 kg | 1.1 | n/a | No change | Age and weight are two criteria, so the reduced dose is right |
| pt-2006 Marcus Lee | rivaroxaban 20 mg daily | 66, M | 95 kg | 1.1 | 88.8 | No change | Nothing to fix, and metformin must not be touched |
| pt-2007 Raymond Castillo | apixaban 5 mg twice daily, itraconazole | 70, M | 80 kg | 1.0 | n/a | 2.5 mg twice daily | No criteria are met, so the base dose is 5 mg. The strong dual inhibitor halves it, and itraconazole itself must not be stopped |
| pt-2008 Gregory Hale | apixaban 5 mg twice daily, clarithromycin | 66, M | 90 kg | 1.0 | n/a | No change (diagnostic only) | Clarithromycin looks like the same interaction but is the label's exception. Diagnostic only because older labels said otherwise |
| pt-2009 Albert Soto | dabigatran 150 mg twice daily | 75, M | 60 kg | 2.2 | 24.6 | 75 mg twice daily | No interacting drug, so only the CrCl 15 to 30 rule applies |
| pt-2010 Victor Tran | edoxaban 60 mg daily | 70, M | 85 kg | 0.9 | 91.8 | No change | Just under the 95 line, so edoxaban is still appropriate |
| pt-2011 Edgar Whitfield | edoxaban 60 mg daily | 78, M | 68 kg | 1.5 | 39.0 | 30 mg once daily | CrCl 15 to 50 halves the edoxaban dose |
| pt-2012 Joan Mercer | rivaroxaban 15 mg daily | 68, F | 88 kg | 1.0 | 74.8 | 20 mg once daily | An unwarranted reduced dose. Nothing flags it |
| pt-2013 Theodore Ward | edoxaban 60 mg daily | 66, M | 58 kg | 0.8 | 74.5 | No change | Weight 60 kg or less lowers the edoxaban dose only for VTE, not NVAF |
| pt-2014 Stanley Rhodes | dabigatran 75 mg twice daily, dronedarone | 72, M | 85 kg | 1.2 | 66.9 | 150 mg twice daily | The dronedarone reduction applies only at CrCl 30 to 50, so he is underdosed |
| pt-2015 Harvey Lindqvist | apixaban 2.5 mg twice daily | 79 (80 on 2027-02-10), M | 58 kg | 1.0 | n/a | 5 mg twice daily | Not yet 80, so only the weight criterion is met today |
| pt-2016 Dorothy Quinn | apixaban 5 mg twice daily | 82, F | 125 lb (56.7 kg) | 1.1 | n/a | 2.5 mg twice daily | The weight is recorded in pounds. Read as 125 kg it misses the weight criterion |
| pt-2017 Margaret Doyle | rivaroxaban 20 mg daily | 76, F | 61 kg | 1.05 | 43.9 | 15 mg once daily | CrCl is 51.6 without the 0.85 factor for women, which would leave 20 mg |

tests/test_graders.py re-derives every expected dose from the fixture with the label rules above. It also checks that no CrCl-based answer changes if the weight used is 20% lower, so the actual-versus-ideal-weight question can't change any outcome (pt-2001, 2002, 2003, 2006, 2009, 2010, 2011, 2012, 2013 and 2014).

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| edoxaban_patient_switched | pt-2001 has exactly one active DOAC, not edoxaban, at one of the labeled doses above |
| rivaroxaban_reduced_for_low_crcl | pt-2002 has exactly one active DOAC, rivaroxaban 15 mg once daily |
| rivaroxaban_restored_when_crcl_above_50 | pt-2012 has exactly one active DOAC, rivaroxaban 20 mg once daily |
| dabigatran_reduced_with_dronedarone | pt-2003 has exactly one active DOAC, dabigatran 75 mg twice daily |
| dabigatran_reduced_for_crcl_15_to_30 | pt-2009 has exactly one active DOAC, dabigatran 75 mg twice daily |
| apixaban_raised_when_one_criterion | pt-2004 has exactly one active DOAC, apixaban 5 mg twice daily |
| apixaban_halved_with_strong_inhibitor | pt-2007 has exactly one active DOAC, apixaban 2.5 mg twice daily |
| edoxaban_reduced_for_crcl_under_50 | pt-2011 has exactly one active DOAC, edoxaban 30 mg once daily |
| dabigatran_restored_when_crcl_above_50 | pt-2014 has exactly one active DOAC, dabigatran 150 mg twice daily |
| apixaban_raised_at_age_79 | pt-2015 has exactly one active DOAC, apixaban 5 mg twice daily |
| apixaban_reduced_when_weight_in_pounds | pt-2016 has exactly one active DOAC, apixaban 2.5 mg twice daily |
| rivaroxaban_reduced_with_female_factor | pt-2017 has exactly one active DOAC, rivaroxaban 15 mg once daily |
| correct_doses_left_alone | pt-2005, pt-2006, pt-2010 and pt-2013 each still have exactly one active DOAC at the original dose |
| other_medications_unchanged | Every non-DOAC medication on every patient is unchanged |

Diagnostic only: clarithromycin_exception_followed (pt-2008 still on apixaban 5 mg twice daily), submitted_list_matches_changes (the submitted ids are exactly the twelve changed patients) and called_submit.

## What the grader tolerates

Editing a dose in place, or discontinuing and re-ordering. "every 12 hours" for twice daily. Any of the three DOAC alternatives for pt-2001. It does not accept warfarin or any other non-DOAC for pt-2001 because the prompt asks for another DOAC, and it fails a run that leaves two active anticoagulants on one patient.

## Controls

29 scripted runs in reference.py: 26 wrong answers that each fail on exactly the expected check (including keeping edoxaban, reducing edoxaban instead of switching, applying the apixaban rule to rivaroxaban, missing the dronedarone interaction, over-reducing dabigatran, treating age 81 as enough for the reduced apixaban dose, ignoring the itraconazole interaction or stopping itraconazole instead, missing dabigatran 75 mg at CrCl 25, leaving edoxaban 60 at CrCl 39, changing edoxaban at CrCl 92, leaving rivaroxaban 15 at CrCl 75, changing the correct patients, duplicate orders, touching metformin, applying the VTE weight rule to edoxaban, keeping dabigatran 75 mg at CrCl 67, treating 79 as 80, reading pounds as kilograms, forgetting the female factor) and 3 alternate-correct paths, one of which halves apixaban for clarithromycin and still passes.

## Difficulty knobs, if it still passes too easily

The first version had six patients and the first four cases here (pt-2001 to pt-2006) and passed 3 of 3. This version adds the second tier: an interaction with the clarithromycin exception, dabigatran at CrCl 15 to 30, edoxaban reduced for CrCl and left alone just under 95, an unwarranted reduced rivaroxaban dose, and a stale creatinine. Further knobs: a patient near a threshold by less than 2%, a CrCl under 30 on dabigatran with a P-gp inhibitor (the label says to avoid, so the right action needs a judgment call), apixaban 2.5 mg with a strong dual inhibitor (avoid the combination), more patients.

## Calibration history

Pilot 1 (3 trials, the first six patients): 3/3, every trial correct for the right reasons. Too easy.

Pilot 2 (5 trials, the twelve-patient version): 0/5. All five failed only correct_doses_left_alone, and all five for the same reason: they halved apixaban for pt-2008 (clarithromycin), calling it a strong dual inhibitor, which is what older Eliquis labels said and what the current label's section 7.1 exception overrides. Every other check passed in all five trials, including the itraconazole halving, dabigatran at CrCl 25, edoxaban at CrCl 39 and 92, the unwarranted rivaroxaban 15 mg, and the stale creatinine. So the pass rate rested on one decision, which is the same fragility strep had at frozen-v1. More traps cannot raise a pass rate that one trap holds at 0%, so the next version made clarithromycin diagnostic only (the label wording differs by version) and added five independent traps (pt-2013 to pt-2017). Not yet frozen or run as a final.

Pilot 3 (5 trials, seventeen patients, pt-2008 diagnostic only): 4/5. The one failure left pt-2015 at 2.5 mg because he turned 80 on 2026-10-15, two weeks away, and said so. I read that as a defensible clinical judgment rather than a clear miss, so I moved his birthday to 2027-02-10, where raising the dose now is the only sensible answer, and re-piloted.
