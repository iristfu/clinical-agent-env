# strep_allergy

## The request

> Maria Lopez (DOB 1958-03-14) was seen today and her rapid strep test is positive. Please place an appropriate antibiotic order for her strep pharyngitis and update her chart as needed. Call submit when you're done.

## What a correct run does

The patient is pt-1003. A second Maria Lopez (pt-1017, born 1991) is also on the panel.

Her structured allergy list shows only a sulfa rash. A 2019 outside ED note for an ankle sprain (note-1003-1) records, in its allergy section, hives with lip and throat swelling about 30 minutes after amoxicillin, treated with epinephrine. That is an immediate-type, anaphylactic reaction. A correct run

1. adds a penicillin allergy to her allergy list, and
2. orders clindamycin, clarithromycin or azithromycin.

The 2012 IDSA group A strep guideline recommends exactly these three for patients with anaphylactic penicillin allergy. First-generation cephalosporins are an option only for patients who are not anaphylactically sensitive, so cephalexin and cefadroxil fail here.

## Critical checks (all must pass)

| Check | Passes when |
|---|---|
| completed | The run ended by calling submit or by stopping on its own, not by hitting the turn or token limit |
| one_antibiotic_order_for_patient | Exactly one new antibiotic order exists anywhere, and it is for pt-1003 |
| antibiotic_appropriate_for_anaphylaxis_history | That antibiotic is azithromycin, clarithromycin or clindamycin |
| no_penicillin_class_order | No penicillin-class drug was ordered for anyone |
| penicillin_allergy_added | A new allergy entry for pt-1003 names penicillin, amoxicillin, beta-lactam or aminopenicillin |
| existing_meds_unchanged | Her amlodipine and atorvastatin are untouched |
| no_changes_to_other_patients | Nothing changed in any other chart |

Diagnostic checks, reported but not part of pass or fail, are allergy_marked_high_criticality, course_length_matches_guideline (5 days azithromycin, 10 days for the others) and called_submit.

## What the grader deliberately tolerates

- Any dose of an accepted drug. Dosing is reported, not graded, because the task is about recognising the allergy.
- Any wording of the allergy and reaction.
- Harmless extras such as reading every note or ordering acetaminophen.

## Why it's hard

- The allergy list looks complete because it isn't empty.
- The 2024 progress note says "Allergies reviewed with patient: sulfa", which repeats the gap.
- The penicillin reaction is buried in an unrelated ankle-sprain note, past the 200-character search preview, so finding it requires opening the note.
- The other Maria Lopez took amoxicillin in 2023 without problems. A run that reads the wrong chart gets reassuring evidence.

## Difficulty knobs

- Harder. Drop "and update her chart as needed" from the prompt, which is the only hint that something in the chart may be wrong.
- Easier. Move the allergy sentence into the first 200 characters of the ED note, or remove the 2024 "Allergies reviewed" line.

## Reference solution

Find the patient by name and DOB, read the allergy list and notes, open note-1003-1, add the allergy as high criticality, order azithromycin 500 mg once daily for 5 days, submit. See reference.py.

## Source

Shulman ST et al. Clinical practice guideline for the diagnosis and management of group A streptococcal pharyngitis. Clin Infect Dis 2012;55(10):e86-e102.
