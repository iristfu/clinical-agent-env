# Clinical agent environment

> Read this as a web page: [iristfu.github.io/clinical-agent-env](https://iristfu.github.io/clinical-agent-env/) is the same writeup, rebuilt from this file on every update, and easier to read.

## Summary

I built a mock EHR for a primary care practice with 30 synthetic patients and 17 tools. It has four tasks, state-based graders, reference solutions and a harness with one entry point. Three of the tasks are scored.

On the final run, frozen at the tag frozen-v2, Opus 5 passed strep_allergy 6/10 and apixaban_dose 3/10, both inside the target 20-70% band, and panel_a1c 9/10, above it. An earlier final at frozen-v1 gave strep 1/10, apixaban 6/10 and panel 7/10. I redesigned strep after that run and report both. Panel's task was identical in both runs, and pooled it passed 16 of 20.

The fourth task, med_rec_discharge, is a poor task for training Opus. It passed 10/10 on its frozen final and 18/18 in earlier pilots, so it never failed in any version, and a task that always passes shows nothing about what the model gets wrong. The main reason is that every deciding fact in it is pointed to by something the model is already reading, such as a discharge summary that names a lab or a dated list of post-discharge notes. Opus follows those references reliably, whereas in the other tasks the deciding fact sits in a note nothing points to. I report it separately and do not score it.

All 28 failed trials across the two scored finals (16 in frozen-v1, 12 in frozen-v2) were labeled by cause and confirmed by hand, and all 28 were the model's fault. Every one is an information-gathering miss: the deciding fact was in a note or lab result the model could reach, and it didn't look. These tasks therefore measure diligence in searching a chart, not clinical reasoning. A useful next step is a task where every fact is in plain sight and the difficulty comes from interacting dosing rules, so a failure can only come from reasoning.

The part I spent the most care on is making sure a failure means the model got something wrong. Most of this writeup is about how I checked that.

A pilot is a small calibration run (3 to 5 trials per task) used to find and fix problems, with tasks edited between pilots. A final is a 10-trial run on frozen tasks, and only finals produce the scored pass rates.

## The environment

The state is a set of FHIR-shaped records (patients, conditions, medications, allergies, observations, notes, orders) held in memory and rebuilt from a fixture file at the start of every trial. I chose this over running a real FHIR server. A HAPI server would look more realistic, but it brings slow resets, more moving parts, and more ways for a trial to fail for reasons unrelated to the model. The shapes and codes (ICD-10, SNOMED, LOINC) are realistic, and the tool layer is the seam where a real backend could be swapped in later.

The date inside the environment is fixed at 2026-10-01, so anything time-relative ("more than 6 months ago", "most recent") is deterministic.

The agent works through 17 tools, which read the chart, search and read notes, look up the formulary and lab catalog, place and change orders, add allergies, and submit. A few design choices matter for grading.

- Write tools take structured input. Frequencies come from a fixed list and medications must resolve to a formulary item, so the grader compares structure rather than fuzzy-matching strings.
- Nothing fails silently. Pagination says how many results there are and how to get the next page. Note search returns a 200-character preview that says it was truncated and points to read_note. An ambiguous drug name like "metoprolol" returns both options instead of guessing.
- Invalid requests return a clear error to the model and the trial continues. Any other exception is treated as a bug in my code (see below).

All patients are hand-authored in env/fixtures/build_panel.py so every trap is deliberate and documented in the task rubric. Background patients add realistic noise and are also the distractors for the panel task.

## The tasks

Each task is a realistic request a clinician or practice manager might give an assistant, where a correct answer depends on applying a specific clinical rule to facts that have to be found in the chart.

| Task | Clinical area | Opus 5 pass rate (95% CI) |
|---|---|---|
| strep_allergy (v2) | Antibiotic choice and penicillin allergy | 6/10, 60% (31% to 83%) |
| apixaban_dose | Blood thinner dosing | 3/10, 30% (11% to 60%) |
| panel_a1c | Diabetes care gaps | 9/10, 90% (60% to 98%) |
| med_rec_discharge (not scored) | Medication reconciliation after hospital discharge | 10/10, 100% (72% to 100%), frozen-v1 |

Pass rates are from the frozen-v2 final, except med rec, which was last run at frozen-v1 (its task is unchanged since).

### strep_allergy: choosing a safe antibiotic

Several patients in a walk-in clinic had a rapid strep test, and the agent has to prescribe for each one who tested positive. The rule comes from the IDSA strep throat guideline. Penicillin or amoxicillin is first choice, but a patient with a penicillin allergy needs something else. If the allergy was mild, such as a rash, a first-generation cephalosporin like cephalexin is acceptable. If it was anaphylaxis, the only options are clindamycin or a macrolide like azithromycin. The agent also has to record any newly discovered allergy in the chart.

Six patients tested positive and each needs a different accepted antibiotic, so one blanket choice can't pass. Two of them had anaphylaxis to penicillin years ago that is documented only in outside records: one named only by the brand Augmentin on page 2 of a 14-note chart, the other past the preview of a scanned urgent care record. A third has a mild rash on her allergy list. Two patients share the name Maria Lopez, and one has no allergy, so mixing up the charts is an error. One positive result exists only as a lab value from a nurse visit, with no note naming the test. A seventh patient tested negative and should get nothing.

### apixaban_dose: dosing a blood thinner

Pharmacy asks for a review of every patient taking apixaban (Eliquis), a blood thinner used to prevent stroke in atrial fibrillation (AF). The label says to use the lower 2.5 mg twice daily dose only when a patient meets at least two of three criteria: age 80 or older, weight 60 kg or less, serum creatinine 1.5 mg/dL or higher (a sign of reduced kidney function). Otherwise the dose is 5 mg. Too high a dose raises bleeding risk, and too low a dose leaves the patient unprotected against stroke.

Nothing in the tools lists patients by drug, so the agent has to read all 30 medication lists to find the six apixaban patients, then collect each one's current age, weight, creatinine and reason for treatment. Several deciding facts are only in notes: one patient's current weight (and a pharmacist review that wrongly says it wasn't recorded) and another's current creatinine, which is only in an outside kidney specialist's letter. The others test the rule itself. A 79-year-old was put on the low dose years ago because of his age and kidney disease, though he is under 80 and meets only one criterion. A patient with stable kidney disease has since crossed the creatinine threshold. A third had a temporary creatinine spike during an acute kidney injury that has since resolved. The sixth takes apixaban for a pulmonary embolism rather than AF, where the reduction criteria don't apply at all.

### panel_a1c: finding diabetes patients overdue for a test

Quality is running a diabetes care-gap report. The agent has to order a hemoglobin A1c (the standard three-month blood sugar test) for every patient with type 2 diabetes whose last A1c was more than 6 months ago or who has none, unless one is already pending. This is a coverage task over 30 patients rather than a dosing or safety question.

Nearly every exclusion rule is exercised once: type 1 diabetes, prediabetes, resolved gestational diabetes, a deceased patient, a patient who takes metformin for PCOS rather than diabetes, and a patient with an order already pending. Diagnoses are coded in a mix of ICD-10 and SNOMED. One patient's problem list says prediabetes, but a note shows she was actually diagnosed with type 2 diabetes and started on metformin. One patient looks overdue in the structured data but had a recent A1c reported only in an outside endocrinologist's letter.

### med_rec_discharge: reconciling medications after hospital stays

The hospital has sent discharge paperwork for patients it discharged since 9/17, and the agent has to update each patient's outpatient medication list to match what they should be taking now. This is medication reconciliation, a routine and error-prone part of primary care.

Five discharges are in scope and two older ones must be left alone. One is filed as discharge instructions rather than a discharge summary, so a search for the usual title misses it. Later phone notes and a cardiology letter override parts of the original discharge plan, for example a heart attack patient switched from clopidogrel to ticagrelor after genetic testing. Some antibiotic courses have already finished. A stomach-protecting drug is a hospital formulary substitution in one chart and a deliberate new prescription in another. Two decisions about restarting medications depend on lab results that no note restates. This task is not scored because the model never failed it.

Each rubric.md has the exact prompt, the expected answer with clinical rationale and sources, every check, what the grader tolerates, the traps, and knobs for making the task easier or harder.

## Grading

Graders look only at chart state (initial against final) and the submission, never at the transcript. That way any valid path to the right outcome gets full credit, and the grader can't be fooled by a model that says the right thing and does something else.

Each task has critical checks, which all have to pass, and diagnostic checks, which are reported but don't affect pass or fail. Critical checks include "must not" conditions, such as no penicillin-class order or no change to another patient's chart. Diagnostic checks break failures down (for example, one check per intended change in the med rec task) and support auditing passes.

The graders deliberately tolerate equivalent answers. That covers editing an order in place or discontinuing and reordering, "every 12 hours" for "twice daily", lab synonyms like HbA1c, any accepted antibiotic at any dose, and harmless extra actions. There is no LLM judge in any pass or fail decision.

## Telling model failures apart from everything else

I used several layers of checks, each closing off a different way a failure could be my fault.

1. The environment can't fail silently. Tool code distinguishes an invalid request (returned to the model as an error) from an unexpected exception. An exception stops the trial, logs the traceback and marks the trial invalid, so it never counts toward a pass rate. A fuzz test sends 2,000 random calls with junk arguments to every tool and fails if anything but a clean tool error comes back.
2. Every trial starts from the same place. Each trial gets a fresh copy of the fixture, logs a hash of its starting state, and the report confirms all trials share one hash. IDs for new records are deterministic too.
3. Each task is solvable and the grader recognises a correct answer. The reference solution runs through the same harness code as the model and scores full marks 10 times out of 10 with identical end states. Each task also has an alternate-correct control, which takes a different valid path (a different accepted drug, a different write sequence, different test names) and must also pass.
4. The grader rejects wrong answers for the right reason. Each task has 6 to 19 wrong-answer controls, 49 controls in all, including 5 alternate-correct ones. These include the obvious mistakes (amoxicillin first-line, the wrong Maria Lopez, following the discharge summary but missing the phone note, ordering for the deceased patient). Each must fail on exactly the checks I expect, not just fail.
5. The expected answers follow from the data. Tests re-derive each task's expected answer directly from the fixture: the panel's expected set, every apixaban dose, which strep tests were positive and where each hidden allergy lives, and which discharges are in scope and how the lab conditions resolve. They also pin each trap in place (for example, that a deciding result sits past the search preview), so an edit to the data can't silently break or defuse a task.
6. API trouble isn't model trouble. Rate limits and outages are retried by the SDK, then the trial is retried twice, then marked invalid. Bad requests stop the run entirely.
7. Every failure gets a cause. Claude, run as a different model from the one under test and given the rubric, labels every failed trajectory with one of eight causes. Five are model faults (didn't gather the information, wrong reasoning, incomplete coverage, wrong action, gave up). The other three are environment bug, grader false negative and ambiguous task. I then reviewed each label by hand. I also audited two passing trials per task for passing for the wrong reason.
8. When a failure wasn't the model's fault, I fixed it and reran. Those fixes are in the calibration log below, and final pass rates come only from trials run after the tasks were frozen.

## Results

There are two final runs, each made on a frozen git tag with Opus 5 at its default effort and no task changes after the tag. Every trial in both was valid, started from the run's single state hash, and hit no environment errors.

- frozen-v1 final: runs/20261109-130217_final, plus runs/20261109-131318_final_medrec_unscored for med rec.
- frozen-v2 final: runs/20261109-134124_final_v2. It differs from frozen-v1 only in the strep_allergy task, described below.

Pass rates pooled over both finals, with 95% intervals:

| Task | Pooled over both finals | In 20-70% band |
|---|---|---|
| strep_allergy | Not pooled, because the two runs tested different versions of the task. The latest version (v2) passed 6/10, 60% (31% to 83%) | yes |
| apixaban_dose | 9/20, 45% (26% to 66%) | yes |
| panel_a1c | 16/20, 80% (58% to 92%) | just above |
| med_rec_discharge (not scored) | 10/10 on the frozen task, and a further 18/18 in pilots 1-6 on earlier versions | no, above in every version |

The same results by run:

| Task | frozen-v1 final | frozen-v2 final |
|---|---|---|
| strep_allergy | 1/10, 10% (2% to 40%). Task version 1, below the band | 6/10, 60% (31% to 83%). Task version 2, in the band |
| apixaban_dose | 6/10, 60% (31% to 83%), in the band | 3/10, 30% (11% to 60%), in the band |
| panel_a1c | 7/10, 70% (40% to 89%), at the top of the band | 9/10, 90% (60% to 98%), above the band |
| med_rec_discharge (not scored) | 10/10, 100% (72% to 100%) | not rerun, the task is unchanged |

Opus 5 makes a fresh choice on every trial, so a 10-trial final is a sample of the task's pass rate, not a fixed property of the task. With 10 trials, 5 of 10 has a 95% interval of roughly 24% to 76%. Apixaban and panel were identical in both runs, yet apixaban went from 6/10 to 3/10 and panel from 7/10 to 9/10. Both moves are ordinary sampling variation, which is why the pooled rates are the best estimate for those two tasks. Pooled, apixaban sits comfortably inside the band and panel sits at its top edge. I report every number as measured and did not retune anything on scored trials, because tuning on the trials being reported would make the numbers meaningless.

### What changed between frozen-v1 and frozen-v2

Only the strep_allergy task changed. Here is exactly what I did and why.

At frozen-v1, strep's outcome hinged on a single decision per trial: whether to open one outside ED note for Maria Lopez (born 1958) that documents anaphylaxis to Augmentin. In pilots the frozen v1 task passed 5 of 8. In the final it passed 1 of 10, with the same miss each time: eight of the nine failing trials saw that note in their own search results and chose not to open it. I confirmed nothing else had changed (the final's state, tool-schema and prompt hashes match the last pilot exactly). A task whose result rests on one yes-or-no choice swings this much between samples. Rather than retune v1 on its scored trials, I treated this as a design finding and built a version whose pass rate rests on two independent, moderately hard traps.

The data changes are in env/fixtures/build_panel.py (commit be82311). The diff from frozen-v1 is one note edited, plus one note and two lab results added:

1. Maria Lopez's 2019 ED note (note-1003-1) gained one line at the top: "Triage: allergies reviewed, 2 drug allergies (see allergy section)." That line falls inside the 200-character search preview, so a model skimming her notes now sees a hint that she has two drug allergies, while her structured allergy list shows only one (sulfa). The note still names the second allergy only as Augmentin, further down, so the model still has to open the note and know that Augmentin is a penicillin.
2. A new positive patient, Kevin Patel (pt-1018), who exists only in lab results. He was swabbed at a walk-in nurse visit on 2026-10-01. His positive rapid strep result is a structured lab observation, and he has a temperature of 38.5 °C. His nurse-visit note says only that a throat swab was "sent for antigen testing" for the provider to review, plus "No known drug allergies". It never uses the words strep, rapid or positive, so a note search for "rapid strep" doesn't find him. He has no penicillin allergy, so penicillin V, amoxicillin, benzathine penicillin G or a first-generation cephalosporin are all accepted. A model that lists today's tests from visit notes alone misses him. The prompt asks for every patient whose rapid strep was positive, and lab results are where test results live.

The grader and checks changed as follows.

- tasks/strep_allergy/task.py: Kevin was added to the list of positive patients, so he must get exactly one appropriate regimen. Every other check is unchanged.
- tasks/strep_allergy/reference.py: the reference solution now also searches notes for "throat" and checks lab results, and orders amoxicillin for Kevin. A new control, missed_lab_only_positive, must fail exactly on the missing-regimen and appropriateness checks. The alternate-correct control gives Kevin cephalexin and must still pass.
- tests/test_graders.py: new tests that Kevin's visit note never names the test (otherwise a note search would find him and the trap would test nothing), and that the ED note's preview mentions two allergies without naming Augmentin.

Apixaban, panel and med rec are untouched: same prompts, graders, rubrics and patients. I verified that every note search those tasks rely on returns identical results at frozen-v1 and frozen-v2. Each fact underlying the v2 traps is pinned by a test, and all 49 grader controls and 101 tests pass at frozen-v2.

v2 was calibrated with one 8-trial pilot before freezing (3/8), then the 10-trial final (6/10). The tasks/strep_allergy/rubric.md file documents both versions and the reasoning for each change.

### Why trials failed

Every failure was labeled first by Claude Opus 5.5 (a different model from the one under test) with the rubric in hand, then reviewed by hand against the full trajectory. Each label's note names the turn where the model went wrong (triage.jsonl in each final run's folder).

frozen-v2 final.

| Task | Failures | Cause after review | Where it went wrong |
|---|---|---|---|
| strep_allergy (v2) | 4 | model_info_gathering, 4 | All four missed Kevin Patel, whose positive test exists only as a lab result. None checked lab results for more than one patient; each listed today's tests from visit notes alone. Two of them also never surfaced Maria Lopez 1958's ED note and gave her amoxicillin. The other two read it and treated her correctly |
| apixaban_dose | 7 | model_info_gathering, 7 | All seven left Linda Park at 5 mg without reading the nephrology letter with her current creatinine. Four searched her notes only for "apixaban", which the letter never mentions. Three never looked at her notes. One of those read no notes at all and also left Harold at 5 mg |
| panel_a1c | 1 | model_info_gathering, 1 | Missed pt-1014. Its own "type 2 diabetes" search listed her note at turn 6 and it never opened it |

The LLM's labels matched mine on all 18 (12 failures, 6 pass audits). Every audited pass read the deciding notes or lab result before acting.

frozen-v1 final.

| Task | Failures | Cause after review | Where it went wrong |
|---|---|---|---|
| strep_allergy | 9 | model_info_gathering, 9 | All nine gave Maria Lopez 1958 a penicillin and added no allergy. Eight saw her 2019 ED note in their own results (an "allergy" search, or page 2 of her notes) and didn't open it. One never surfaced it, having searched only "penicillin", which the brand-name note can't match. Two also merged the two Maria Lopez charts in their reasoning. Every trial caught Elizabeth Martin's anaphylaxis in the scanned record |
| apixaban_dose | 4 | model_info_gathering, 4 | All four left Linda Park at 5 mg. Two never looked at her notes. Two searched them only for "apixaban", which correctly misses the nephrology letter, and never listed the rest. Every trial got the other five patients right |
| panel_a1c | 3 | model_info_gathering, 3 | All three missed pt-1014. Their own "type 2 diabetes" search returned her note among five hits at turn 6, and they treated her as prediabetes from the coded problem list without opening it. Every trial excluded pt-1020 correctly |

I overturned none of the LLM's labels in either run. In the frozen-v1 run two came back "unparsed" because of a parser bug in harness/triage.py (the JSON block was malformed). The raw text gave the same category both times, and I fixed the parser afterwards. I also audited two passing trials per task, five in all, plus two med rec passes. All seven reached the trap facts by reading the note and passed for the reasons in the rubric.

No failure in either final run, or in any pilot after the round-4 search fix, involved a tool returning wrong or misleading data, a grader rejecting a valid answer, or an ambiguous prompt.

### Noteworthy failures

The model reasons correctly and then decides not to look (strep v1 final, trial 7). At turn 8 an "allergies" search lists Maria Lopez 1958's 2019 ED note. At turn 9 the model writes: "I'll skip pt-1003's ankle note since it's probably unrelated." At turn 11 it orders penicillin V. In the same trial it reads Elizabeth Martin's scanned urgent care note, recognises her anaphylaxis, adds the allergy and avoids every beta-lactam. It knows exactly what to do with an allergy history and chooses not to read this one because the note's preview is about an ankle.

A narrow search treated as a complete one (apixaban, frozen-v1 final, trial 5). At turn 8 it decides Linda Park meets one criterion from her structured creatinine of 1.18. It then searches her notes for "apixaban", which correctly returns only an unrelated phone call, and moves on. The nephrology letter with creatinine 1.66 never mentions apixaban. Four other trials in the same run listed all of her notes and found it.

Something clinically reasonable I hadn't anticipated, which led to a grader change (strep, pilot 1). Every trial said it wanted the labeled adult azithromycin course (500 mg on day 1, then 250 mg on days 2 to 5), and that the order tool, which takes one dose per order, couldn't express it. One settled for a 3-day course. A model that entered the labeled course correctly as two orders would have failed the "exactly one antibiotic order" check, so the grader was wrong, not the model. I changed it to accept one regimen split across orders at different doses, and added a control that must pass with the split course and one that must fail with a duplicated order. That is the one grader change in the project. The other non-model fault was environmental: in pilot 4, note search treated "allergy" and "Allergies:" as different words, which handed one failing trial a misleading "No results". I fixed the search and re-piloted before freezing.

## Calibration log

| Round | Change | Why | Pass rates after |
|---|---|---|---|
| 0 | Initial build | | reference 10/10 on all tasks, controls 22/22 |
| 1 | Pilot 1, 3 trials per task, no task changes before it | Measure the starting point | strep 3/3, apixaban 3/3, panel 3/3, med rec 3/3. All 12 passed for the reasons the rubrics give (trajectories read in full). No env errors, validation errors or invalid trials |
| 1 → 2 | Strep grader fix: accept one antibiotic regimen entered as several orders of the same drug at different doses. A repeated dose still fails as a duplicate. New controls alt_correct_azithromycin_taper_as_two_orders (must pass) and duplicate_azithromycin_orders (must fail) | All three strep trials said the order tool can't express the labeled adult azithromycin course (500 mg day 1, then 250 mg days 2-5). One settled for a 3-day course instead. A run that entered the labeled course as two orders would have been failed for a clinically correct answer | (see round 2) |
| 1 → 2 | Strep was made harder. The ED note names the reaction drug only as Augmentin and no longer says "avoided all penicillins". The grader accepts "Augmentin" and "clavulanate" as allergy wording | Every trial found the note with a note search for "penicillin". The model now has to read the note or know the brand name. Did not apply the rubric's other knob (drop "update her chart as needed") because it would make the allergy check ambiguous | |
| 1 → 2 | Apixaban was made harder. Removed the discharge summary's "reassess dosing" request (listed knob). Added a 9/28 pharmacist review recommending 5 mg, which openly uses the stale May flowsheet weight | Every trial found the 9/24 weight within six turns. The new trap is anchoring on an authoritative but wrong review, and the right answer is still unambiguous because the review cites the outdated weight | |
| 1 → 2 | Panel was made harder. Buried pt-1014's diagnosis further into a longer note (listed knob). pt-1020 now has an A1c from 2026-08-05 documented only in an endocrinology consult note, so the expected set drops from 7 to 6. New control ignored_outside_a1c_in_note | The listed knob alone is weak because note search matches full text. The new trap punishes trusting structured results only. Also corrected the rubric: pt-1015's second LOINC code is matched by the "A1c" query, so it's a weak trap | |
| 1 → 2 | Med rec was made harder. Discharge changes written as narrative (listed knob). Added a cefpodoxime course that finished 9/30 and an inpatient pantoprazole formulary substitution for home omeprazole. New controls continued_completed_cefpodoxime, kept_inpatient_pantoprazole (must fail) and alt_correct_documents_completed_course (must pass) | Every trial read all three notes and applied all seven changes. The new traps test whether the model reasons about what she should be taking today, not just what the summary lists | |
| 1 → 2 | Housekeeping. Added .DS_Store to .gitignore | An untracked env/.DS_Store made every run warn that env/ was dirty | |
| 2 | Pilot 2, 3 trials per task, on the round-2 tasks | Check the round-2 traps | strep 3/3, apixaban 3/3, panel 2/3, med rec 3/3. The panel failure is the model's fault (information gathering). Trial 2 said it would search notes across the panel, never did, and ordered for pt-1020 from the structured A1c. Both panel passes read the endocrinology note. Every apixaban trial looked for a 9/24 weight before reading notes and explicitly overrode the pharmacist. Every strep and med rec trial read all of that patient's notes. No env or grader faults |
| 2 → 3 | Strep was made harder. Added 11 routine notes from 2019 to 2026, three restating a sulfa-only allergy list (the rubric's own knob), so the ED note is on page 2 of her chart | Opus reads every note when a patient has three. The one failure so far came from volume, not from hidden facts | (see round 3) |
| 2 → 3 | Apixaban was made harder. The prompt says "last week" instead of "on 9/24". The pharmacist review now also says no weight was recorded at the 9/24 visit, which the progress note contradicts | In pilot 2 the date in the prompt sent every trial straight to the 9/24 weight | |
| 2 → 3 | Med rec was made harder. A 10/1 phone note restarts empagliflozin after a savings card, so the expected list now includes it. New control stopped_at_9_30_note. The alternate-correct control now follows all three sources in date order | The latest instruction now has to win twice | |
| 2 → 3 | Panel unchanged | 2/3 is already consistent with the band | |
| 3 | Pilot 3, 3 trials per task, on the round-3 tasks | Check the round-3 traps | strep 3/3, apixaban 3/3, panel 0/3, med rec 3/3. All three panel failures missed pt-1014. Each trial's own search for "type 2 diabetes" returned her buried note among five hits, and none opened it (model fault, information gathering). I confirmed the panel's search results are identical to round 2, so this is variance, not a change. Pooled over pilots 2 and 3, which ran the same panel task, it's 2/6. Every strep trial followed the page-2 hint to the ED note. Every apixaban trial caught the pharmacist's false "no weight recorded" claim. Every med rec trial applied the 10/1 restart |
| 3 → 4 | Strep, apixaban and med rec were redesigned for breadth. Strep covers every positive rapid strep today (5 positives, 1 negative). Apixaban is a panel-wide NVAF dose review (5 apixaban patients). Med rec covers every Valley General discharge since 9/17 (3 in scope, 2 older decoys). The original patient and traps carry over in each. New cases sit on existing background patients, and I confirmed the panel task's note searches are unchanged. Controls 29 → 40 | All three passed 9/9 as single-patient tasks. The only failures in rounds 1 to 3 came from coverage across many patients | (see round 4) |
| 4 | Pilot 4, 3 trials each on the three redesigned tasks | Check the redesign | strep 1/3, apixaban 3/3, med rec 3/3. Both strep failures are the model's fault (information gathering) on Maria Lopez 1958: one never fetched page 2 of her notes despite the tool saying there was one; the other fetched page 2, saw the outside ED record listed and didn't open it. Every apixaban trial got all five patients right; all three first edited William's albuterol by guessing a medication id, noticed, and restored it before submitting. Every med rec trial got all three discharges right and left the decoys alone |
| 4 → 4b | Environment fix: note search now treats -y and -ies as the same word, and the tool description says singular and plural forms match. New test | In pilot 4, searches for "allergy" returned "No results" on charts whose notes have "Allergies:" sections. The failing trial still had a clear path to the note, but a misleading empty result shouldn't be part of the evidence. Panel searches confirmed unchanged | (see 4b) |
| 4b | Strep re-pilot, 3 trials, after the search fix | Check the fix didn't remove the difficulty | strep 2/3. The failure is the model's fault (information gathering): it listed page 2 of Maria Lopez 1958's notes, saw the outside ED record and concluded "penicillin is confirmed fine" without opening it. One pass found the note through the now-working "allergy" search, the other by paging |
| 4 → 5 | Apixaban was made harder. Added Linda Park (pt-1002): weight 57.6 kg is structured, but her creatinine crossing 1.5 (1.66 on 9/18) exists only in an outside nephrology letter, past the preview. Her structured creatinine (1.18) and her 2025 start note both point to keeping 5 mg. Med rec was made harder. Added Angela Rossi (pt-1011), whose 9/28 discharge is filed as "hospital course and discharge instructions" and never says "summary". Michael now has a 9/29 cardiology letter switching clopidogrel to ticagrelor (CYP2C19 poor metabolizer), among routine post-discharge notes. Controls 40 → 43 | Both passed 3/3 in pilot 4. The traps that have caught Opus put the deciding fact in a note the model has to choose to open, behind structured data that looks complete | (see round 5) |
| 5 | Pilot 5, 3 trials each on apixaban and med rec | Check the round-5 traps | apixaban 2/3, med rec 3/3. The apixaban failure is the model's fault (information gathering). It searched Linda's notes for "apixaban", which correctly returned only the knee-pain call, never listed her other notes, and kept 5 mg from the May creatinine. Both passes read the nephrology letter. Every med rec trial's first search was "Valley General discharge", which finds Angela's document, and every trial read Michael's letter and switched him to ticagrelor |
| 5 → 6 | Med rec was made harder. Barbara's lisinopril restart is now conditional on her 9/29 creatinine (restart only if 1.2 or lower; it was 1.34, so it stays held). Added Karen Nguyen (pt-1009, 9/21 cholecystectomy) as a fifth in-scope discharge: start iron only if a ferritin sent at discharge is below 30 (it was 12), plus a finished ibuprofen course. Neither result appears in any note. Controls 43 → 48 | Med rec had passed 15/15 across every version, and no trial had ever called get_observations. The two conditions resolve in opposite directions, so guessing fails one of them | (see round 6) |
| 6 | Pilot 6, 3 trials on med rec | Check the lab-conditional traps | med rec 3/3, all for the right reason. Every trial looked up both labs, kept Barbara's lisinopril held and started Karen's iron. An instruction that names a lab turns out to prompt the lookup, so it tests diligence less than a note the model has to choose to open. 18/18 across every med rec version |
| 7 | Pilot 7, 5 more trials each on the three scored tasks, no task changes. Med rec moved out of the scored set (18/18, reported separately) | Narrow the estimates before freezing | strep 3/5, apixaban 4/5, panel 4/5. Every failure is the model's fault (information gathering) at the task's intended trap. Strep: two trials never opened Maria Lopez 1958's page-2 ED note (one searched "amoxicillin", which the brand-name note correctly doesn't match; one decided the sulfa-only annual physicals settled it). Apixaban: one searched Linda's notes only for "apixaban", which misses the nephrology letter, and kept 5 mg. Panel: one set pt-1014 aside as prediabetes and never opened the note its own "type 2 diabetes" search returned. All passes reached the trap fact by reading the note. Pooled on current versions: strep 5/8 (62%, CI 31-86%), apixaban 6/8 (75%, CI 41-93%), panel 6/11 (55%, CI 28-79%) |
| Final | Tagged frozen-v1. 10 trials per scored task, plus 10 for med rec reported separately. No changes after the tag | Final measurement | strep 1/10, apixaban 6/10, panel 7/10, med rec 10/10. All 16 failures model_info_gathering, confirmed by hand. Environment identical to pilot 7 (same state, tool schema and prompt hashes) |
| v2 | Strep v2, after frozen-v1: Maria's ED note preview now says "2 drug allergies (see allergy section)". A new positive, Kevin Patel (pt-1018), was swabbed at a nurse visit whose note never names the test, so his result exists only as a lab observation. Diff from frozen-v1: one note edited, one note and two observations added; every search the other tasks use is unchanged | frozen-v1 strep hinged on one decision and swung from 5/8 to 1/10 | Pilot, 8 trials: 3/8. Every failure is the model's fault. All five missed Kevin: they listed today's tests from visit notes only and checked lab results for at most one patient. Three of them also never opened Maria's ED note. All three passes found Kevin's nurse note through an "allergy" search and then checked lab results, so the two traps are correlated. Not yet frozen or run as a final |
| Final v2 | Tagged frozen-v2. Fresh 10-trial finals on all three scored tasks, so the headline numbers come from one freeze. No changes after the tag | Final measurement after the strep redesign | strep (v2) 6/10, apixaban 3/10, panel 9/10. All 12 failures model_info_gathering, confirmed by hand. Apixaban and panel are unchanged from frozen-v1. Their moves (6/10 to 3/10, 7/10 to 9/10) are sampling variance on identical tasks: pooled, apixaban is 9/20 and panel is 16/20 |

## What surprised me

- Clinical reasoning was the easy part. I expected judgment calls to be where Opus would fail, so I built several in. It got every one right whenever it had read the facts, across 150 model trials:
  - IDSA's rule that anaphylaxis rules out first-generation cephalosporins while a benign rash doesn't
  - Augmentin being a penicillin
  - Macrolides being reserved for penicillin-allergic patients
  - The Eliquis 2-of-3 rule, including correcting an underdosed 79-year-old and not counting a resolved AKI creatinine
  - That a PE patient's apixaban isn't governed by the AF rule
  - A CYP2C19 poor metabolizer's switch to ticagrelor
  - Telling a hospital formulary substitution from a deliberate start
  - Conditional restarts that depend on a lab value

  It also volunteered checks I hadn't asked for: QT risk with sertraline before choosing azithromycin, the clarithromycin and atorvastatin interaction, and strong CYP3A4/P-gp inhibitors before changing an apixaban dose. No trial was ever labeled model_reasoning. Every failure came earlier, at the step of deciding what to read.

- Single-patient traps don't work on Opus 5. For three rounds every single-patient task passed every trial, whatever I buried. When a patient has three to fourteen notes, Opus reads them, follows "page 2" hints, recognises Augmentin as a penicillin, and overrides an authoritative but wrong pharmacist review. Difficulty only appeared once a task spread its deciding facts across many patients.
- Every failure is the same kind of failure. All 16 final failures, and every model failure in the pilots, are information gathering, and none are clinical reasoning. Whenever the model read the deciding note it drew the right conclusion, including on subtle points: a resolved AKI creatinine, the VTE treatment dose for a PE patient, a 79-year-old who doesn't meet the age criterion, a formulary substitution versus a deliberate start. What it gets wrong is which documents to open. It skips a note whose preview looks irrelevant, or treats a narrow keyword search as a full review.
- Explicit references get followed and implicit ones don't. The med rec task never failed, in 10 of 10 final trials and 18 of 18 pilot trials, even with a superseding cardiology letter, a discharge filed under a different title, and two decisions that depended on lab results nobody restated. Each of those was pointed to by something the model was already reading: a discharge summary that names a lab, or a dated list of post-discharge notes. The tasks that do fail hide the fact in a document nothing points to.
- Unchanged tasks moved a lot between final runs. Apixaban went from 6/10 to 3/10 and panel from 7/10 to 9/10 between frozen-v1 and frozen-v2, with the same tasks. Ten trials is a small sample of a model that makes a fresh choice each time about whether to open one note.
- The same frozen task swung from 5/8 to 1/10. Strep's failure is a single decision repeated per trial (open the ankle-sprain note or not), and the model made it differently on different days. One binary choice per trial makes a task's pass rate very sensitive to small shifts in that choice, and three to five pilot trials weren't enough to see it.
- Small slips that the model then fixes. In 6 of 21 apixaban trials across pilots 4, 5 and 7 and the final run, the model first edited the wrong medication by guessing an id from another patient (William's albuterol or Charles's metformin set to an apixaban dose), noticed, and restored it before submitting. The grader judges only the final chart, so these pass, correctly. In a real EHR the intermediate edit would have been visible to other users.

## What I'd change and do next

- Turn each task into a template that generates variants with different patients, values and note wording. That gives far more than 10 samples per task, tighter intervals, and protection against a model memorising a fixed chart. Strep is the case for it: 5/8 in pilots and 1/10 in the final, on identical tasks.
- Give each task two or three independent traps of moderate difficulty. Strep's outcome hinged on one decision, and a task with several traps would have a steadier pass rate than one with a single trap the model takes about half the time.
- A med rec version that could land in the band probably needs reconciliation across many charts where some changes are recorded only in documents nothing else points to, closer to how the panel task works.
- Run Sonnet and Haiku on the same tasks. A good task should separate models, not just land Opus 5 in a band.
- Have a clinician sign off on each rubric's accepted answers, especially anywhere guidelines leave room for judgment.
- Put a HAPI FHIR server behind the same tools to test whether the results hold on a real API surface.
- Add tasks with a note or patient message as output, scored by an LLM judge validated against hand-labeled examples.
- Measure how pass rates move with effort, which says something about whether a failure comes from missing knowledge or missing diligence.

### A clinical reasoning task

Every failure in this project is information gathering, so the scored tasks measure diligence across a chart. With more time, the task I would most want to add is one where finding the facts is trivial and the judgment is the whole difficulty. What it would take:

- Put every fact in plain sight: one or two patients, a short chart, and the deciding values in structured data or the prompt itself, so a failure can't come from not reading.
- Draw the difficulty from rules that are counterintuitive or interact, and that have a single citable answer. Drug labels are the best source because they are explicit. Some examples:
  - Edoxaban shouldn't be used for atrial fibrillation when creatinine clearance is above 95 mL/min, so good kidney function is the contraindication, the opposite of most renal rules.
  - The rivaroxaban AF dose is set by creatinine clearance calculated from body weight (15 mg daily at 50 or below). Apixaban's rule uses serum creatinine directly, so the two DOACs need different inputs for the same patient.
  - For interactions, the apixaban label halves the dose with combined strong CYP3A4 and P-gp inhibitors, and says to avoid them entirely if the patient is already on 2.5 mg. It also carves out clarithromycin as an exception. Statin dose caps with amiodarone or clarithromycin are another example.

  A task would combine two or three of these for one patient, for example choosing and dosing an anticoagulant for a patient with a borderline creatinine clearance who has just started an interacting antibiotic. Every accepted answer would cite the label section it comes from.
- Avoid places where guidelines disagree. Cockcroft-Gault with actual versus ideal body weight is a classic ambiguity. The rubric would name which weight the label specifies, and any case where reasonable clinicians would differ would be dropped or accept both answers, with an alternate-correct control for each.
- Keep the same grading machinery. State-based checks, a reference solution, wrong-answer controls for each misapplied rule, and fixture-derived tests that recompute the answer from the label rules. The triage taxonomy already has a model_reasoning label, and in this task most failures should land there rather than in information gathering.
- Have a clinician review it. A pharmacist or physician should sign off on each rubric's accepted answers before calibration starts, because this is exactly where my own judgment is the weak point.
- Expect calibration to be slow. Opus 5 got every judgment call in this project right, so a first version would likely score near 10/10. Difficulty would come from stacking interacting rules and choosing ones that contradict the common heuristic, piloted over several rounds like the tasks here. I'd also run an effort sweep. If reasoning failures respond to effort much more than these information-gathering failures do, that's a finding in itself.

I estimate about a day to build one well, plus calibration rounds and the clinician review.

## Limitations

The data and traps were written by one person, so the tasks reflect my idea of realistic chart mess. Every scored failure is an information-gathering miss, so these tasks measure diligence across a chart far more than clinical knowledge. The prompts include light cues ("update her chart as needed") that I kept deliberately, because removing them would make a critical check ambiguous. The note search is literal apart from singular and plural forms, which is realistic for many EHRs but is a design choice that shapes how findable each note is. Ten trials per task give wide intervals, and strep shows a frozen task can move a long way between samples. The graders' tolerances cover the alternatives I could anticipate, and the triage and hand review exist to catch the ones I couldn't. None came up in either final run.
