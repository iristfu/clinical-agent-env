"""Strep pharyngitis for every patient with a positive rapid strep today, each with a different allergy history.

IDSA 2012 GAS pharyngitis guideline:
  - no penicillin allergy: penicillin V or amoxicillin (benzathine penicillin G IM also listed). First-generation
    cephalosporins are accepted too, though not first line. Macrolides and clindamycin are reserved for allergy.
  - penicillin allergy, not anaphylactic: first-generation cephalosporin (cephalexin, cefadroxil), clindamycin,
    azithromycin or clarithromycin.
  - immediate-type / anaphylactic penicillin allergy: clindamycin, azithromycin or clarithromycin only.
See rubric.md for every patient.
"""

from tasks.common import (Check, active_meds, completed_check, finalize, formulary, med_key, new_records,
                          submitted_check, untouched_check)

MAX_TURNS = 50

PENICILLINS = {"amoxicillin", "penicillin V potassium", "benzathine penicillin G"}
FIRST_GEN_CEPH = {"cephalexin", "cefadroxil"}
NON_BETA_LACTAM = {"azithromycin", "clarithromycin", "clindamycin"}
ACCEPTED = {
    "none": PENICILLINS | FIRST_GEN_CEPH,
    "mild": FIRST_GEN_CEPH | NON_BETA_LACTAM,
    "anaphylaxis": NON_BETA_LACTAM,
}
POSITIVE = {
    "pt-1003": "anaphylaxis",  # Maria Lopez 1958: Augmentin anaphylaxis only in a 2019 ED note, page 2 of her chart
    "pt-1023": "anaphylaxis",  # Elizabeth Martin: penicillin VK anaphylaxis only in a scanned 2015 urgent care record
    "pt-1021": "mild",         # Jennifer Lee: listed amoxicillin rash, maculopapular, no hives or swelling
    "pt-1017": "none",         # Maria Lopez 1991: no allergies, tolerated amoxicillin in 2023
    "pt-1030": "none",         # Daniel King: no known drug allergies
}
NEGATIVE = "pt-1026"           # Joseph Walker: tested today, negative, viral pharyngitis
TARGET_PATIENTS = sorted(POSITIVE)
ALLERGY_TERMS = ("penicillin", "amoxicillin", "beta-lactam", "beta lactam", "aminopenicillin", "augmentin",
                 "clavulanate")


def _one_regimen(orders):
    """The single regimen ordered for one patient, or None. Several orders of the same drug at different doses count
    as one regimen (how the tools express a loading dose, e.g. azithromycin 500 mg day 1 then 250 mg days 2 to 5).
    The same dose twice is a duplicate."""
    if len(orders) == 1:
        return orders[0]
    if len(orders) > 1 and len({m["name"] for m in orders}) == 1 \
            and len({float(m["dose_value"]) for m in orders}) == len(orders):
        return orders[0]
    return None


def grade(ctx):
    form = formulary(ctx.final)
    new_abx = [m for m in new_records(ctx, "medications") if "antibiotic" in form[m["formulary_id"]]["drug_class"]]
    by_patient = {pid: [m for m in new_abx if m["patient_id"] == pid] for pid in POSITIVE}
    regimen = {pid: _one_regimen(orders) for pid, orders in by_patient.items()}
    stray = [(m["patient_id"], m["name"]) for m in new_abx if m["patient_id"] not in POSITIVE]
    appropriate = {pid: regimen[pid] is not None and regimen[pid]["name"] in ACCEPTED[kind]
                   for pid, kind in POSITIVE.items()}
    allergic = [pid for pid, kind in POSITIVE.items() if kind != "none"]
    pcn_to_allergic = [(pid, m["name"]) for pid in allergic for m in by_patient[pid] if m["name"] in PENICILLINS]

    def pcn_allergy_added(pid):
        return any(any(t in a["substance"].lower() for t in ALLERGY_TERMS) for a in new_records(ctx, "allergies", pid))

    meds_changed = [pid for pid in POSITIVE
                    if sorted(med_key(m) for m in active_meds(ctx.initial, pid))
                    != sorted(med_key(m) for m in active_meds(ctx.final, pid) if m["source"] == "chart")]
    submitted = set((ctx.submission or {}).get("patient_ids") or [])

    def show(pid):
        return [(m["name"], m["dose_value"], m["frequency"]) for m in by_patient[pid]]

    checks = [
        completed_check(ctx),
        Check("one_regimen_per_positive_patient", all(regimen[p] is not None for p in POSITIVE),
              detail="; ".join(f"{p}: {show(p)}" for p in POSITIVE)),
        Check("no_antibiotic_without_positive_test", not stray, detail=f"orders for other patients: {stray}"),
        Check("antibiotics_appropriate_for_allergy_history", all(appropriate.values()),
              detail="; ".join(f"{p} ({POSITIVE[p]}): {regimen[p]['name'] if regimen[p] else None}" for p in POSITIVE)),
        Check("no_penicillin_for_penicillin_allergic", not pcn_to_allergic, detail=str(pcn_to_allergic)),
        Check("hidden_anaphylaxis_added_to_allergy_list", pcn_allergy_added("pt-1003") and pcn_allergy_added("pt-1023"),
              detail=f"pt-1003: {pcn_allergy_added('pt-1003')}; pt-1023: {pcn_allergy_added('pt-1023')}"),
        Check("no_false_penicillin_allergy", not pcn_allergy_added("pt-1017") and not pcn_allergy_added("pt-1030"),
              detail="pt-1017 and pt-1030 tolerate penicillins"),
        Check("existing_meds_unchanged", not meds_changed, detail=f"home medications changed for: {meds_changed}"),
        untouched_check(ctx, allowed=set(POSITIVE)),
        # Diagnostic only.
        *[Check(f"{p}_appropriate", appropriate[p], critical=False, detail=str(show(p))) for p in POSITIVE],
        Check("submitted_list_matches_positives", submitted == set(POSITIVE), critical=False,
              detail=f"submitted: {sorted(submitted)}"),
        submitted_check(ctx),
    ]
    return finalize(checks, score=sum(appropriate.values()) / len(appropriate))
