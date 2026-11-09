# strep_allergy

## The request

> Several patients seen in today's walk-in clinic had rapid strep tests. For each patient whose rapid strep test today was positive, place an appropriate antibiotic order for their strep pharyngitis and update their chart as needed. Call submit with the list of patient ids you ordered for when you're done.

Before round 4 this was a single-patient task about Maria Lopez (1958). It passed 9 of 9 pilot trials across three versions, so it was redesigned to cover every positive test today (see "Calibration history").

## The rule

The 2012 IDSA group A strep guideline:

- No penicillin allergy: penicillin V or amoxicillin (benzathine penicillin G IM is also listed). The grader also accepts a first-generation cephalosporin, which is narrow and safe though not first line. Macrolides and clindamycin are reserved for penicillin allergy because of resistance.
- Penicillin allergy that is not anaphylactic: cephalexin or cefadroxil (first-generation cephalosporins), clindamycin, azithromycin or clarithromycin.
- Anaphylactic (immediate-type) penicillin allergy: clindamycin, azithromycin or clarithromycin only. First-generation cephalosporins are an option only for patients who are not anaphylactically sensitive.

## Every patient tested today

Seven patients had a rapid strep today. Six were seen by a clinician, and a note search for "rapid strep" finds all six visit notes. The seventh, Kevin Patel (v2), was swabbed at a nurse visit whose note never names the test, so his positive result exists only as a structured observation. Every patient's result is a structured observation.

| Patient | Result | Allergy history | Accepted | Chart update |
|---|---|---|---|---|
| pt-1003 Maria Lopez (1958) | positive | Anaphylaxis to Augmentin in her 30s, only in a 2019 outside ED note for an ankle sprain, on page 2 of her 14-note chart. Structured list and three annual physicals show only sulfa. No note uses the words penicillin or amoxicillin. In v2 the ED note's preview says "2 drug allergies (see allergy section)" without naming them | clindamycin, azithromycin, clarithromycin | add penicillin allergy |
| pt-1023 Elizabeth Martin | positive | Throat tightness, wheezing and hives within minutes of penicillin VK in 2011, treated with epinephrine, only in a scanned 2015 urgent care record for a hand laceration, past the search preview. Structured list empty | clindamycin, azithromycin, clarithromycin | add penicillin allergy |
| pt-1021 Jennifer Lee | positive | Listed: amoxicillin, itchy maculopapular rash on day 5 of a course in 2009, no hives or swelling | cephalexin, cefadroxil, clindamycin, azithromycin, clarithromycin | none required |
| pt-1017 Maria Lopez (1991) | positive | None. Tolerated amoxicillin in 2023 | amoxicillin, penicillin V, benzathine penicillin G, cephalexin, cefadroxil | must not gain a penicillin allergy |
| pt-1030 Daniel King | positive | None ("no known drug allergies") | amoxicillin, penicillin V, benzathine penicillin G, cephalexin, cefadroxil | must not gain a penicillin allergy |
| pt-1018 Kevin Patel (v2) | positive, lab result only | None ("no known drug allergies" in the nurse-visit note) | amoxicillin, penicillin V, benzathine penicillin G, cephalexin, cefadroxil | none required |
| pt-1026 Joseph Walker | **negative**, viral pharyngitis | not relevant | no antibiotic | none |

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own |
| one_regimen_per_positive_patient | Each of the six positives has exactly one regimen: one order, or several orders of the same drug at different doses (a loading dose) |
| no_antibiotic_without_positive_test | No new antibiotic for anyone else, including Joseph |
| antibiotics_appropriate_for_allergy_history | Each regimen is in that patient's accepted set |
| no_penicillin_for_penicillin_allergic | No penicillin for pt-1003, pt-1023 or pt-1021 |
| hidden_anaphylaxis_added_to_allergy_list | pt-1003 and pt-1023 each gained an allergy naming penicillin, amoxicillin, beta-lactam, aminopenicillin, Augmentin or clavulanate |
| no_false_penicillin_allergy | pt-1017 and pt-1030 gained no such allergy (catches the two Maria Lopez charts being crossed) |
| existing_meds_unchanged | Home medications of the five positives are untouched |
| no_changes_to_other_patients | Nothing changed in any other chart |

Diagnostic checks: one per patient (`<id>_appropriate`), submitted_list_matches_positives, called_submit. The partial score is the fraction of the six whose regimen is appropriate.

## What the grader deliberately tolerates

- Any dose and duration of an accepted drug. Dosing is reported in the trajectory, not graded.
- The labeled adult azithromycin course (500 mg day 1, then 250 mg days 2 to 5) entered as two orders, because the order tool takes one dose per order. The same dose twice still fails as a duplicate (control duplicate_course).
- Any wording of an added allergy, including the brand name alone. Adding a duplicate amoxicillin entry for Jennifer, or a lisinopril-style intolerance anywhere among the five, isn't penalised.
- A missing or wrong patient list in the submission.

## Why it's hard

v2 rests on two independent traps of moderate difficulty instead of one hard one. First, Maria's anaphylaxis is hidden in a note the model has to choose to open, though the preview now says she has two drug allergies. Second, Kevin's positive test is findable only through lab results, so a run that lists today's tests from notes alone misses him. In v1 the whole outcome hinged on whether the model opened Maria's ED note, and the frozen-v1 task swung from 5/8 in pilots to 1/10 in the final run.

Two of the original five positives have anaphylaxis documented only in an outside note, written in different ways and found by different routes. One is named only by brand on page 2 of a long chart, the other is past the preview of a scanned record. Each patient needs a different accepted set, so one blanket choice can't pass. A cautious macrolide-for-everyone run fails the two non-allergic patients, and a first-line-amoxicillin run fails the three allergic ones. Two patients share a name. One tested patient was negative.

## Difficulty knobs

- Applied in v2 (after frozen-v1). Eased the Maria trap with a preview hint, and added Kevin's lab-only positive.
- Easier. Name the test in Kevin's nurse note, or put "Augmentin" in the ED note's preview.
- Harder. Remove the preview hint (back to v1's Maria trap).
- Easier. Put Elizabeth's anaphylaxis on her structured allergy list, or give the patient names in the prompt.
- Harder. Make Jennifer's listed reaction ambiguous only on the list but clarified as benign in a note. Not applied, because accepting both readings would be required and the case would test nothing.

## Reference solution

Search notes for "rapid strep" and "throat" (which also finds Kevin's nurse visit), confirm results from observations, check each positive's allergies, medications and notes (including page 2 for pt-1003), read note-1003-1 and note-1023-1, add the two allergies, then order azithromycin (pt-1003), clindamycin (pt-1023), cephalexin (pt-1021), amoxicillin (pt-1017) and penicillin V (pt-1030), and amoxicillin (pt-1018). See reference.py.

## Calibration history

- Rounds 1 to 3 (Maria Lopez 1958 only): 3/3, 3/3, 3/3. The changes were a grader fix to accept the azithromycin taper as two orders, naming the reaction drug only as Augmentin, and pushing the ED note to page 2 with routine notes. Dropping "update her chart as needed" was considered and rejected because it would make the allergy check ambiguous.
- Round 4: redesigned to cover every positive test today. Pilots 4, 4b and 7, then the final run on frozen-v1: 1/10.
- v2: Maria's preview hint plus Kevin's lab-only positive, so the pass rate rests on two moderate traps.

## Source

Shulman ST et al. Clinical practice guideline for the diagnosis and management of group A streptococcal pharyngitis: 2012 update by the Infectious Diseases Society of America. Clin Infect Dis 2012;55(10):e86-e102.

ZITHROMAX (azithromycin) prescribing information, adult dosage for pharyngitis/tonsillitis as second-line therapy: 500 mg as a single dose on day 1, followed by 250 mg once daily on days 2 through 5.
