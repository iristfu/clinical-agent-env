# panel_a1c

## The request

> Quality is running a diabetes care-gap report. For every patient on the panel who has type 2 diabetes and whose most recent hemoglobin A1c was more than 6 months ago (or who has no A1c on record), place a hemoglobin A1c lab order, unless one is already pending. Don't order it for anyone else. When you're done, call submit with the list of patient ids you ordered for.

Today is 2026-10-01, so "more than 6 months ago" means before 2026-04-01. The prompt defines the rule itself, so no guideline interpretation is needed. Every boundary case sits at least 3 weeks from the cutoff.

## Every patient with a diabetes-related signal

| Patient | What the chart shows | Order? |
|---|---|---|
| pt-1001 James Whitaker | T2DM E11.9, last A1c 2025-12-10 | yes |
| pt-1004 Robert Chen | T2DM E11.65, last A1c 2026-06-18 | no, recent |
| pt-1005 Patricia Gomez | Type 1 diabetes E10.9, A1c 2025-10-05 | no, type 1 |
| pt-1006 Michael O'Brien | T2DM coded only in SNOMED (44054006), last A1c 2025-09-15 | yes |
| pt-1007 Susan Miller | T2DM, old A1c, died 2026-07-02 | no, deceased |
| pt-1009 Karen Nguyen | Prediabetes R73.03, A1c 6.1 | no, not diabetic |
| pt-1010 David Kim | T2DM, new patient, no A1c on record | yes |
| pt-1011 Angela Rossi | Gestational diabetes, resolved 2019 | no |
| pt-1012 Denise Carter | T2DM, A1c 2026-09-25 | no, recent |
| pt-1013 Thomas Wright | T2DM, last A1c 2026-02-14, A1c order pending since 2026-09-20 | no, already pending |
| pt-1014 Nancy Fischer | Problem list says prediabetes, but the 2025-11-18 note diagnoses type 2 diabetes (A1c 6.9, fasting glucose 131 and 142) and starts metformin; last A1c 2025-11-18 | yes |
| pt-1015 Gary Hughes | T2DM, A1c 2025-12-01 under LOINC 4548-4 and 2026-07-08 under 17856-6 (HPLC, outside lab) | no, recent |
| pt-1016 Brenda Scott | T2DM, last A1c 2026-03-09 | yes |
| pt-1018 Kevin Patel | T2DM, A1c 2026-05-02 | no, recent |
| pt-1020 Steven Adams | T2DM, last A1c 2025-06-30 | yes |
| pt-1022 William Turner | No diabetes; note mentions family history of diabetes, old screening A1c 5.5 | no |
| pt-1024 Richard Clark | T2DM, A1c 2026-08-11 | no, recent |
| pt-1025 Barbara Lewis | T2DM, last A1c 2025-10-30 | yes |
| pt-1027 Sarah Hall | On metformin for PCOS, A1c 5.6, note says no diabetes | no |
| pt-1028 Charles Young | T2DM, A1c 2026-04-22 | no, recent |

Expected set (7) is pt-1001, pt-1006, pt-1010, pt-1014, pt-1016, pt-1020, pt-1025. tests/test_graders.py re-derives this set from the fixture so an edit to the data can't silently break it.

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| ordered_set_matches_expected | The patients with new A1c orders are exactly the expected 7 |
| no_duplicate_a1c_orders | No patient got more than one new A1c order |
| no_order_for_deceased_patient | Nothing ordered for pt-1007 |
| no_other_chart_changes | Medications, allergies, conditions and notes are untouched |

Diagnostic checks are no_unrequested_lab_orders, submitted_list_matches_orders and called_submit. The partial score is the F1 of the ordered set against the expected set, halved if there are duplicates.

## What the grader deliberately tolerates

- Any test name that resolves to A1c (HbA1c, glycated hemoglobin, 4548-4).
- Any order of operations.
- A missing or wrong patient list in the submission. The chart is what counts.

## Why it's hard

It's a coverage task over 30 patients across 3 pages, and nearly every exclusion rule is exercised once. The two hardest are the note-only diagnosis (pt-1014) and the A1c stored under a second LOINC code (pt-1015). A run that infers diabetes from metformin alone gets pt-1027 wrong, and a run that skips list_orders reorders for pt-1013.

## Difficulty knobs

- Easier. Code pt-1014's diabetes as E11.9, or store pt-1015's recent A1c under 4548-4.
- Harder. Bury the pt-1014 diagnosis inside a longer note about another problem, past the search preview.
