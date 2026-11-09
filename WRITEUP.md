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
| strep_allergy | Safety check before prescribing | The penicillin anaphylaxis is only in the allergy section of an unrelated 2019 ED note, the structured list shows sulfa so it looks complete, and a second Maria Lopez tolerated amoxicillin | **[fill in]** |
| apixaban_dose | Applying a label rule to messy data | The current weight exists only as free text in pounds in the visit note; the last structured weight points the other way | **[fill in]** |
| panel_a1c | Systematic coverage across a panel | 30 patients, mixed ICD-10 and SNOMED coding, a diagnosis that exists only in a note, A1c under two LOINC codes, a pending order, a deceased patient, metformin for PCOS | **[fill in]** |
| med_rec_discharge | Multi-step reconciliation | Seven changes must all be right, and a phone note after discharge supersedes two of them | **[fill in]** |

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
4. **The grader rejects wrong answers for the right reason.** Each task has 4 to 5 wrong-answer controls, 22 controls in all. These include the obvious mistakes (amoxicillin first-line, the wrong Maria Lopez, following the discharge summary but missing the phone note, ordering for the deceased patient). Each must fail on exactly the checks I expect, not just fail.
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
