"""Strep pharyngitis in a patient whose penicillin anaphylaxis is documented only inside a 2019 ED note."""

from tasks.common import (Check, completed_check, finalize, formulary, med_key, new_records, submitted_check,
                          untouched_check, active_meds)

MAX_TURNS = 30
TARGET = "pt-1003"
TARGET_PATIENTS = [TARGET]

# IDSA 2012 GAS pharyngitis guideline: for patients with immediate-type (anaphylactic) penicillin allergy,
# use clindamycin, clarithromycin or azithromycin. First-generation cephalosporins are reserved for
# patients who are not anaphylactically sensitive.
ACCEPTED = {"azithromycin": 5, "clarithromycin": 10, "clindamycin": 10}  # drug -> guideline course (days)
# The ED note names the drug only as Augmentin (amoxicillin-clavulanate), so the brand name counts too.
ALLERGY_TERMS = ("penicillin", "amoxicillin", "beta-lactam", "beta lactam", "aminopenicillin", "augmentin",
                 "clavulanate")


def _one_regimen(new_abx):
    """The single antibiotic regimen ordered, or None. A regimen is one order, or several orders of the same drug for
    the target patient at different doses, which is how the tools express a loading dose such as the labeled adult
    azithromycin course (500 mg on day 1, then 250 mg on days 2 to 5). Repeating the same dose is a duplicate."""
    if not new_abx or any(m["patient_id"] != TARGET for m in new_abx):
        return None
    if len(new_abx) == 1:
        return new_abx[0]
    same_drug = len({m["name"] for m in new_abx}) == 1
    distinct_doses = len({float(m["dose_value"]) for m in new_abx}) == len(new_abx)
    if same_drug and distinct_doses:
        return {**new_abx[0], "duration_days": sum(m["duration_days"] or 0 for m in new_abx) or None}
    return None


def grade(ctx):
    form = formulary(ctx.final)
    new_meds = new_records(ctx, "medications")
    new_abx = [m for m in new_meds if "antibiotic" in form[m["formulary_id"]]["drug_class"]]
    chosen = _one_regimen(new_abx)
    penicillins = [m for m in new_meds if form[m["formulary_id"]]["drug_class"] == "penicillin antibiotic"]
    pcn_allergy = [a for a in new_records(ctx, "allergies", TARGET)
                   if any(t in a["substance"].lower() for t in ALLERGY_TERMS)]
    before = sorted(med_key(m) for m in active_meds(ctx.initial, TARGET))
    after = sorted(med_key(m) for m in active_meds(ctx.final, TARGET) if m["source"] == "chart")

    checks = [
        completed_check(ctx),
        Check("one_antibiotic_order_for_patient", chosen is not None,
              detail=f"new antibiotic orders: {[(m['patient_id'], m['name']) for m in new_abx]}"),
        Check("antibiotic_appropriate_for_anaphylaxis_history", chosen is not None and chosen["name"] in ACCEPTED,
              detail=f"chosen: {chosen['name'] if chosen else None}; accepted: {sorted(ACCEPTED)}"),
        Check("no_penicillin_class_order", not penicillins,
              detail=f"penicillin-class orders: {[m['name'] for m in penicillins]}"),
        Check("penicillin_allergy_added", bool(pcn_allergy),
              detail=f"new allergy entries: {[a['substance'] for a in new_records(ctx, 'allergies', TARGET)]}"),
        Check("existing_meds_unchanged", before == after, detail="home medications left as they were"),
        untouched_check(ctx, allowed={TARGET}),
        # Diagnostic only, not part of pass/fail.
        Check("allergy_marked_high_criticality", any(a["criticality"] == "high" for a in pcn_allergy), critical=False),
        Check("course_length_matches_guideline",
              chosen is not None and chosen["duration_days"] == ACCEPTED.get(chosen["name"]), critical=False,
              detail=f"duration_days={chosen['duration_days'] if chosen else None}"),
        submitted_check(ctx),
    ]
    return finalize(checks)
