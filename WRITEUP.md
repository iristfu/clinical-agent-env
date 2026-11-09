# Clinical agent environment

Draft. Sections marked **[fill in]** depend on the model runs.

## Summary

I built a mock EHR for a primary care practice with 30 synthetic patients and 17 tools, four tasks inside it, state-based graders, reference solutions and a harness with one entry point. Opus 5 passed **[fill in]** across the four tasks over 10 trials each. Every failed trial was labeled by cause and confirmed by hand, and **[fill in]** of them were the model's fault.

The part I spent the most care on is making sure a failure means the model got something wrong. Most of this writeup is about how I checked that.

## The environment

The state is a set of FHIR-shaped records (patients, conditions, medications, allergies, observations, notes, orders) held in memory and rebuilt from a fixture file at the start of every trial. I chose this over running a real FHIR server. A HAPI server would look more realistic, but it brings slow resets, more moving parts, and more ways for a trial to fail for reasons unrelated to the model. The shapes and codes (ICD-10, SNOMED, LOINC) are realistic, and the tool layer is the seam where a real backend could be swapped in later.

The date inside the environment is fixed at 2026-10-01, so anything time-relative ("more than 6 months ago", "most recent") is deterministic.

The agent works through 17 tools, which read the chart, search and read notes, look up the formulary and lab catalog, place and change orders, add allergies, and submit. A few design choices matter for grading.

- Write tools take structured input. Frequencies come from a fixed list and medications must resolve to a formulary item, so the grader compares structure rather than fuzzy-matching strings.
- Nothing fails silently. Pagination says how many results there are and how to get the next page. Note search returns a 200-character preview that says it was truncated and points to read_note. An ambiguous drug name like "metoprolol" returns both options instead of guessing.
- Invalid requests return a clear error to the model and the trial continues. Any other exception is treated as a bug in my code (see below).

All patients are hand-authored in env/fixtures/build_panel.py so every trap is deliberate and documented in the task rubric. Background patients add realistic noise and are also the distractors for the panel task.

## The tasks

| Task | What it tests | Why it's hard | Opus 5 pass rate (95% CI) |
|---|---|---|---|
| strep_allergy | Safety check before prescribing, for every positive test today | Five positives each need a different accepted antibiotic. Two have anaphylaxis documented only in outside notes: one named only by brand on page 2 of a 14-note chart, one past the preview of a scanned record. One has a mild listed rash, two share a name, and a sixth patient tested negative | **[fill in]** |
| apixaban_dose | Applying a label rule across the panel | Five apixaban patients found only by reading 30 medication lists: a current weight only in a note (contradicted by a pharmacist review), an underdosed 79-year-old, a stable creatinine crossing 1.5, a resolved AKI, and a PE patient outside the AF rule | **[fill in]** |
| panel_a1c | Systematic coverage across a panel | 30 patients, mixed ICD-10 and SNOMED coding, a diagnosis that exists only in a note, a recent outside A1c that exists only in a note, a pending order, a deceased patient, metformin for PCOS | **[fill in]** |
| med_rec_discharge | Reconciling every recent discharge | Three in-scope discharges, each with a superseding phone note or a finished course; pantoprazole is an inpatient substitution in one chart and a deliberate start in another; two older discharges must be left alone | **[fill in]** |

Each rubric.md has the exact prompt, the expected answer with clinical rationale and sources, every check, what the grader tolerates, the traps, and knobs for making the task easier or harder.

## Grading

Graders look only at chart state (initial against final) and the submission, never at the transcript. That way any valid path to the right outcome gets full credit, and the grader can't be fooled by a model that says the right thing and does something else.

Each task has critical checks, which all have to pass, and diagnostic checks, which are reported but don't affect pass or fail. Critical checks include "must not" conditions, such as no penicillin-class order or no change to another patient's chart. Diagnostic checks break failures down (for example, one check per intended change in the med rec task) and support auditing passes.

The graders deliberately tolerate equivalent answers. That covers editing an order in place or discontinuing and reordering, "every 12 hours" for "twice daily", lab synonyms like HbA1c, any accepted antibiotic at any dose, and harmless extra actions. There is no LLM judge in any pass or fail decision.

## Telling model failures apart from everything else

I used several layers of checks, each closing off a different way a failure could be my fault.

1. **The environment can't fail silently.** Tool code distinguishes an invalid request (returned to the model as an error) from an unexpected exception. An exception stops the trial, logs the traceback and marks the trial invalid, so it never counts toward a pass rate. A fuzz test sends 2,000 random calls with junk arguments to every tool and fails if anything but a clean tool error comes back.
2. **Every trial starts from the same place.** Each trial gets a fresh copy of the fixture, logs a hash of its starting state, and the report confirms all trials share one hash. IDs for new records are deterministic too.
3. **Each task is solvable and the grader recognises a correct answer.** The reference solution runs through the same harness code as the model and scores full marks 10 times out of 10 with identical end states. Each task also has an alternate-correct control, which takes a different valid path (a different accepted drug, a different write sequence, different test names) and must also pass.
4. **The grader rejects wrong answers for the right reason.** Each task has 6 to 12 wrong-answer controls, 40 controls in all, including 5 alternate-correct ones. These include the obvious mistakes (amoxicillin first-line, the wrong Maria Lopez, following the discharge summary but missing the phone note, ordering for the deceased patient). Each must fail on exactly the checks I expect, not just fail.
5. **The expected answers follow from the data.** Tests re-derive the panel task's expected set and the apixaban criteria directly from the fixture, so an edit to the data can't silently break a task.
6. **API trouble isn't model trouble.** Rate limits and outages are retried by the SDK, then the trial is retried twice, then marked invalid. Bad requests stop the run entirely.
7. **Every failure gets a cause.** Claude, run as a different model from the one under test and given the rubric, labels every failed trajectory with one of eight causes. Five are model faults (didn't gather the information, wrong reasoning, incomplete coverage, wrong action, gave up). The other three are environment bug, grader false negative and ambiguous task. I then reviewed each label by hand. I also audited two passing trials per task for passing for the wrong reason.
8. **When a failure wasn't the model's fault, I fixed it and reran.** Those fixes are in the calibration log below, and final pass rates come only from trials run after the tasks were frozen.

## Results

**[fill in from runs/<final run>/report.md]**

| Task | Passed | Pass rate | 95% CI (Wilson) | In 20-70% band |
|---|---|---|---|---|
| strep_allergy | | | | |
| apixaban_dose | | | | |
| panel_a1c | | | | |
| med_rec_discharge | | | | |

With 10 trials, 5 of 10 has a 95% interval of roughly 24% to 76%. Ten trials can show a task is in the target band, but not exactly where in it.

### Why trials failed

**[fill in]** Failure causes per task after human review, and how many LLM labels I overturned.

### A few failures worth reading

**[fill in]** Two or three short trajectory excerpts. The most informative is usually one where the model did something clinically reasonable that I hadn't anticipated, and whether that led to a grader change.

## Calibration log

| Round | Change | Why | Pass rates after |
|---|---|---|---|
| 0 | Initial build | | reference 10/10 on all tasks, controls 22/22 |
| 1 | Pilot 1, 3 trials per task, no task changes before it | Measure the starting point | strep 3/3, apixaban 3/3, panel 3/3, med rec 3/3. All 12 passed for the reasons the rubrics give (trajectories read in full). No env errors, validation errors or invalid trials |
| 1 → 2 | **Grader fix (strep).** Accept one antibiotic regimen entered as several orders of the same drug at different doses. A repeated dose still fails as a duplicate. New controls alt_correct_azithromycin_taper_as_two_orders (must pass) and duplicate_azithromycin_orders (must fail) | All three strep trials said the order tool can't express the labeled adult azithromycin course (500 mg day 1, then 250 mg days 2-5). One settled for a 3-day course instead. A run that entered the labeled course as two orders would have been failed for a clinically correct answer | (see round 2) |
| 1 → 2 | **Strep harder.** The ED note names the reaction drug only as Augmentin and no longer says "avoided all penicillins". The grader accepts "Augmentin" and "clavulanate" as allergy wording | Every trial found the note with a note search for "penicillin". The model now has to read the note or know the brand name. Did not apply the rubric's other knob (drop "update her chart as needed") because it would make the allergy check ambiguous | |
| 1 → 2 | **Apixaban harder.** Removed the discharge summary's "reassess dosing" request (listed knob). Added a 9/28 pharmacist review recommending 5 mg, which openly uses the stale May flowsheet weight | Every trial found the 9/24 weight within six turns. The new trap is anchoring on an authoritative but wrong review, and the right answer is still unambiguous because the review cites the outdated weight | |
| 1 → 2 | **Panel harder.** Buried pt-1014's diagnosis further into a longer note (listed knob). pt-1020 now has an A1c from 2026-08-05 documented only in an endocrinology consult note, so the expected set drops from 7 to 6. New control ignored_outside_a1c_in_note | The listed knob alone is weak because note search matches full text. The new trap punishes trusting structured results only. Also corrected the rubric: pt-1015's second LOINC code is matched by the "A1c" query, so it's a weak trap | |
| 1 → 2 | **Med rec harder.** Discharge changes written as narrative (listed knob). Added a cefpodoxime course that finished 9/30 and an inpatient pantoprazole formulary substitution for home omeprazole. New controls continued_completed_cefpodoxime, kept_inpatient_pantoprazole (must fail) and alt_correct_documents_completed_course (must pass) | Every trial read all three notes and applied all seven changes. The new traps test whether the model reasons about what she should be taking today, not just what the summary lists | |
| 1 → 2 | Housekeeping. Added .DS_Store to .gitignore | An untracked env/.DS_Store made every run warn that env/ was dirty | |
| 2 | Pilot 2, 3 trials per task, on the round-2 tasks | Check the round-2 traps | strep 3/3, apixaban 3/3, panel 2/3, med rec 3/3. The panel failure is the model's fault (information gathering). Trial 2 said it would search notes across the panel, never did, and ordered for pt-1020 from the structured A1c. Both panel passes read the endocrinology note. Every apixaban trial looked for a 9/24 weight before reading notes and explicitly overrode the pharmacist. Every strep and med rec trial read all of that patient's notes. No env or grader faults |
| 2 → 3 | **Strep harder.** Added 11 routine notes from 2019 to 2026, three restating a sulfa-only allergy list (the rubric's own knob), so the ED note is on page 2 of her chart | Opus reads every note when a patient has three. The one failure so far came from volume, not from hidden facts | (see round 3) |
| 2 → 3 | **Apixaban harder.** The prompt says "last week" instead of "on 9/24". The pharmacist review now also says no weight was recorded at the 9/24 visit, which the progress note contradicts | In pilot 2 the date in the prompt sent every trial straight to the 9/24 weight | |
| 2 → 3 | **Med rec harder.** A 10/1 phone note restarts empagliflozin after a savings card, so the expected list now includes it. New control stopped_at_9_30_note. The alternate-correct control now follows all three sources in date order | The latest instruction now has to win twice | |
| 2 → 3 | Panel unchanged | 2/3 is already consistent with the band | |
| 3 | Pilot 3, 3 trials per task, on the round-3 tasks | Check the round-3 traps | strep 3/3, apixaban 3/3, panel 0/3, med rec 3/3. All three panel failures missed pt-1014. Each trial's own search for "type 2 diabetes" returned her buried note among five hits, and none opened it (model fault, information gathering). I confirmed the panel's search results are identical to round 2, so this is variance, not a change. Pooled over pilots 2 and 3, which ran the same panel task, it's 2/6. Every strep trial followed the page-2 hint to the ED note. Every apixaban trial caught the pharmacist's false "no weight recorded" claim. Every med rec trial applied the 10/1 restart |
| 3 → 4 | **Redesigned strep, apixaban and med rec for breadth.** Strep covers every positive rapid strep today (5 positives, 1 negative). Apixaban is a panel-wide NVAF dose review (5 apixaban patients). Med rec covers every Valley General discharge since 9/17 (3 in scope, 2 older decoys). The original patient and traps carry over in each. New cases sit on existing background patients, and I confirmed the panel task's note searches are unchanged. Controls 29 → 40 | All three passed 9/9 as single-patient tasks. The only failures in rounds 1 to 3 came from coverage across many patients | (see round 4) |
| 4 | Pilot 4, 3 trials each on the three redesigned tasks | Check the redesign | strep 1/3, apixaban 3/3, med rec 3/3. Both strep failures are the model's fault (information gathering) on Maria Lopez 1958: one never fetched page 2 of her notes despite the tool saying there was one; the other fetched page 2, saw the outside ED record listed and didn't open it. Every apixaban trial got all five patients right; all three first edited William's albuterol by guessing a medication id, noticed, and restored it before submitting. Every med rec trial got all three discharges right and left the decoys alone |
| 4 → 4b | **Environment fix.** Note search now treats -y and -ies as the same word, and the tool description says singular and plural forms match. New test | In pilot 4, searches for "allergy" returned "No results" on charts whose notes have "Allergies:" sections. The failing trial still had a clear path to the note, but a misleading empty result shouldn't be part of the evidence. Panel searches confirmed unchanged | (see 4b) |
| 4b | Strep re-pilot, 3 trials, after the search fix | Check the fix didn't remove the difficulty | strep 2/3. The failure is the model's fault (information gathering): it listed page 2 of Maria Lopez 1958's notes, saw the outside ED record and concluded "penicillin is confirmed fine" without opening it. One pass found the note through the now-working "allergy" search, the other by paging |
| 4 → 5 | **Apixaban harder.** Added Linda Park (pt-1002): weight 57.6 kg is structured, but her creatinine crossing 1.5 (1.66 on 9/18) exists only in an outside nephrology letter, past the preview. Her structured creatinine (1.18) and her 2025 start note both point to keeping 5 mg. **Med rec harder.** Added Angela Rossi (pt-1011), whose 9/28 discharge is filed as "hospital course and discharge instructions" and never says "summary". Michael now has a 9/29 cardiology letter switching clopidogrel to ticagrelor (CYP2C19 poor metabolizer), among routine post-discharge notes. Controls 40 → 43 | Both passed 3/3 in pilot 4. The traps that have caught Opus put the deciding fact in a note the model has to choose to open, behind structured data that looks complete | (see round 5) |
| 5 | Pilot 5, 3 trials each on apixaban and med rec | Check the round-5 traps | apixaban 2/3, med rec 3/3. The apixaban failure is the model's fault (information gathering). It searched Linda's notes for "apixaban", which correctly returned only the knee-pain call, never listed her other notes, and kept 5 mg from the May creatinine. Both passes read the nephrology letter. Every med rec trial's first search was "Valley General discharge", which finds Angela's document, and every trial read Michael's letter and switched him to ticagrelor |

## What surprised me

**[fill in]**

## What I'd change and do next

- **More samples per task.** Turn each task into a template that generates variants with different patients, values and note wording. That gives far more than 10 samples per task, tighter intervals, and protection against a model memorising a fixed chart.
- **Show the tasks discriminate.** Run Sonnet and Haiku on the same tasks. A good task should separate models, not just land Opus 5 in a band.
- **Clinician review.** Have a clinician sign off on each rubric's accepted answers, especially anywhere guidelines leave room for judgment.
- **A real backend.** Put a HAPI FHIR server behind the same tools to test whether the results hold on a real API surface.
- **Graded free text.** Add tasks with a note or patient message as output, scored by an LLM judge validated against hand-labeled examples.
- **Effort levels.** Measure how pass rates move with effort, which says something about whether a failure comes from missing knowledge or missing diligence.

## Limitations

The data and traps were written by one person, so the tasks reflect my idea of realistic chart mess. Some traps lean on a single buried fact, which tests diligence more than clinical knowledge. The prompts include light cues ("update her chart as needed") that I tuned during calibration. The graders' tolerances cover the alternatives I could anticipate, and the triage step exists to catch the ones I couldn't.
