# strep_allergy

## The request

> Maria Lopez (DOB 1958-03-14) was seen today and her rapid strep test is positive. Please place an appropriate antibiotic order for her strep pharyngitis and update her chart as needed. Call submit when you're done.

## What a correct run does

The patient is pt-1003. A second Maria Lopez (pt-1017, born 1991) is also on the panel.

Her structured allergy list shows only a sulfa rash. A 2019 outside ED note for an ankle sprain (note-1003-1) records, in its allergy section, hives with lip and throat swelling about 30 minutes after a dose of Augmentin in her 30s, treated with epinephrine. Augmentin is amoxicillin-clavulanate, a penicillin, and the reaction is immediate-type and anaphylactic. A correct run

1. adds a penicillin allergy to her allergy list, and
2. orders clindamycin, clarithromycin or azithromycin.

The 2012 IDSA group A strep guideline recommends exactly these three for patients with anaphylactic penicillin allergy. First-generation cephalosporins are an option only for patients who are not anaphylactically sensitive, so cephalexin and cefadroxil fail here.

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own, not by hitting the turn or token limit |
| one_antibiotic_order_for_patient | New antibiotic orders exist only for pt-1003 and make up one regimen: a single order, or several orders of the same drug at different doses (a loading dose) |
| antibiotic_appropriate_for_anaphylaxis_history | That antibiotic is azithromycin, clarithromycin or clindamycin |
| no_penicillin_class_order | No penicillin-class drug was ordered for anyone |
| penicillin_allergy_added | A new allergy entry for pt-1003 names penicillin, amoxicillin, beta-lactam, aminopenicillin, Augmentin or clavulanate |
| existing_meds_unchanged | Her amlodipine and atorvastatin are untouched |
| no_changes_to_other_patients | Nothing changed in any other chart |

Diagnostic checks, reported but not part of pass or fail, are allergy_marked_high_criticality, course_length_matches_guideline (5 days azithromycin, 10 days for the others) and called_submit.

## What the grader deliberately tolerates

- Any dose of an accepted drug. Dosing is reported, not graded, because the task is about recognising the allergy.
- The labeled adult azithromycin course (500 mg on day 1, then 250 mg on days 2 to 5) entered as two orders. The order tool takes one dose per order, so this is the only way to express it, and all three pilot-1 trials said they wanted it. The same dose ordered twice still fails as a duplicate. Both are tested by controls (alt_correct_azithromycin_taper_as_two_orders, duplicate_azithromycin_orders).
- Any wording of the allergy and reaction, including the brand name alone.
- Harmless extras such as reading every note or ordering acetaminophen.

## Why it's hard

- The allergy list looks complete because it isn't empty.
- The 2024 progress note says "Allergies reviewed with patient: sulfa", and annual physicals in 2020, 2021 and 2025 list only sulfa too. Each repeats the gap.
- She has 14 notes. Notes are listed newest first, 10 per page, so the 2019 ED note sits on page 2 of her chart. A run that reads only page 1, or only notes whose preview looks relevant, never sees it. The tool says there is a second page.
- The penicillin reaction is buried in an unrelated ankle-sprain note, past the 200-character search preview, so finding it requires opening the note.
- The note names the drug only as Augmentin. No note for this patient contains "penicillin" or "amoxicillin", so a keyword search for either returns nothing, and the model has to know Augmentin is a penicillin. (Before round 2 the note said amoxicillin and "avoided all penicillins since", and every pilot-1 trial found it with a search for "penicillin".)
- The other Maria Lopez took amoxicillin in 2023 without problems. A run that reads the wrong chart gets reassuring evidence.

## Difficulty knobs

- Applied in round 2. Name the reaction drug only by brand (Augmentin) and drop "avoided all penicillins since", so keyword search for the generic or the class finds nothing.
- Considered and not applied. Dropping "and update her chart as needed" from the prompt. Without it, a run that orders the right drug but doesn't add the allergy has done what it was asked, so penicillin_allergy_added would fail for a reason the prompt doesn't support.
- Applied in round 3. Added 11 routine notes from 2019 to 2026 (ED follow-up, refills, annual physicals, a UTI treated with nitrofurantoin, shoulder tendinopathy, the portal message booking today's visit). Three restate a sulfa-only allergy list. None mention penicillins or the reaction. In pilot 2 every trial read all three of her notes, so the ED note was always seen.
- Harder. Remove the ED follow-up note on 2019-08-27, which is the only other note that points back to the ED visit.
- Easier. Remove the round-3 routine notes so the ED note is back on page 1, revert the note to name amoxicillin and penicillins, or move the allergy sentence into the first 200 characters of the ED note.

## Reference solution

Find the patient by name and DOB, read the allergy list and notes, open note-1003-1, add the allergy (penicillins, amoxicillin-clavulanate / Augmentin) as high criticality, order azithromycin 500 mg once daily for 5 days, submit. See reference.py.

## Source

Shulman ST et al. Clinical practice guideline for the diagnosis and management of group A streptococcal pharyngitis. Clin Infect Dis 2012;55(10):e86-e102.

ZITHROMAX (azithromycin) prescribing information, adult dosage for pharyngitis/tonsillitis as second-line therapy: 500 mg as a single dose on day 1, followed by 250 mg once daily on days 2 through 5.
