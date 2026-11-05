"""Panel-wide diabetes care-gap sweep. Tests systematic coverage across 30 patients with messy coding."""

from collections import Counter

from tasks.common import Check, completed_check, finalize, new_records, submitted_check, PATIENT_COLLECTIONS

MAX_TURNS = 60
TARGET_PATIENTS = []  # panel-wide

A1C_CODES = {"4548-4", "17856-6"}
DECEASED = "pt-1007"

# Today is 2026-10-01, so "more than 6 months ago" means before 2026-04-01. See rubric.md for every patient.
EXPECTED = {
    "pt-1001",  # T2DM E11.9, last A1c 2025-12-10
    "pt-1006",  # T2DM coded in SNOMED only, last A1c 2025-09-15
    "pt-1010",  # T2DM, new patient, no A1c on record
    "pt-1014",  # problem list says prediabetes; 2025-11-18 note diagnoses T2DM and starts metformin; last A1c 2025-11-18
    "pt-1016",  # T2DM, last A1c 2026-03-09
    "pt-1020",  # T2DM, last A1c 2025-06-30
    "pt-1025",  # T2DM, last A1c 2025-10-30
}


def grade(ctx):
    orders = new_records(ctx, "orders")
    a1c = [o for o in orders if o["code"] in A1C_CODES]
    counts = Counter(o["patient_id"] for o in a1c)
    got = set(counts)
    missing, extra = sorted(EXPECTED - got), sorted(got - EXPECTED)
    other_labs = [(o["patient_id"], o["display"]) for o in orders if o["code"] not in A1C_CODES]
    others_unchanged = all(ctx.initial[c] == ctx.final[c] for c in PATIENT_COLLECTIONS if c != "orders")
    submitted_ids = set(((ctx.submission or {}).get("patient_ids")) or [])

    tp = len(got & EXPECTED)
    precision = tp / len(got) if got else 0.0
    recall = tp / len(EXPECTED)
    f1 = 0.0 if tp == 0 else 2 * precision * recall / (precision + recall)

    checks = [
        completed_check(ctx),
        Check("ordered_set_matches_expected", got == EXPECTED, detail=f"missing: {missing}; extra: {extra}"),
        Check("no_duplicate_a1c_orders", all(v == 1 for v in counts.values()),
              detail=f"duplicates: {sorted(p for p, v in counts.items() if v > 1)}"),
        Check("no_order_for_deceased_patient", DECEASED not in got),
        Check("no_other_chart_changes", others_unchanged, detail="meds, allergies, conditions, notes untouched"),
        # Diagnostic only.
        Check("no_unrequested_lab_orders", not other_labs, critical=False, detail=f"other labs: {other_labs}"),
        Check("submitted_list_matches_orders", submitted_ids == got, critical=False,
              detail=f"submitted minus ordered: {sorted(submitted_ids - got)}; ordered minus submitted: "
                     f"{sorted(got - submitted_ids)}"),
        submitted_check(ctx),
    ]
    return finalize(checks, score=f1 if all(v == 1 for v in counts.values()) else f1 * 0.5)
