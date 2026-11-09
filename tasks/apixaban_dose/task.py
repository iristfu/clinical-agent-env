"""Panel-wide apixaban dose review. Five patients take apixaban; four for nonvalvular AF, one for pulmonary embolism.

Eliquis label, NVAF: 2.5 mg twice daily if at least 2 of age >= 80, weight <= 60 kg, serum creatinine >= 1.5 mg/dL;
otherwise 5 mg twice daily. The VTE treatment dose has no such reduction. Today is 2026-10-01. See rubric.md.
"""

import re
from collections import Counter

from tasks.common import Check, active_meds, completed_check, finalize, med_key, norm_freq, submitted_check

MAX_TURNS = 60
TARGET_PATIENTS = ["pt-1008", "pt-1019", "pt-1022", "pt-1028", "pt-1029"]

# patient -> correct final apixaban dose (mg, twice daily), with the deciding facts.
EXPECTED = {
    "pt-1008": 2.5,  # NVAF. Age 81 + weight 58.2 kg (128.3 lb, only in the 9/24 note). Cr 1.31. Was 5 -> reduce.
    "pt-1019": 5.0,  # NVAF. Weight 57.8 kg only. Cr 0.86 now; 1.74 on 8/18 was a resolved AKI. Age 68. Keep 5.
    "pt-1022": 5.0,  # NVAF. Cr 1.61 only. Age 79 (born 1947-03-03), weight 81.6 kg. On 2.5 -> increase to 5.
    "pt-1028": 2.5,  # NVAF. Age 82 + Cr 1.63 (stable CKD 3b). Weight 70.3 kg. Was 5 -> reduce.
    "pt-1029": 5.0,  # Acute PE (8/12), not AF. Treatment-phase dose; no criteria-based reduction. Keep 5.
}
CHANGED = {"pt-1008", "pt-1022", "pt-1028"}
WEIGHT_CITED = re.compile(r"\b58(\.\d)?\s*kg|\b128(\.3)?\s*(lb|lbs|pounds)", re.I)


def _apixaban(state, pid):
    return [m for m in active_meds(state, pid) if m["name"] == "apixaban"]


def _ok(m, dose):
    return float(m["dose_value"]) == dose and m["dose_unit"] == "mg" and norm_freq(m["frequency"]) == "twice daily"


def grade(ctx):
    per_patient = {}
    for pid, dose in EXPECTED.items():
        apix = _apixaban(ctx.final, pid)
        per_patient[pid] = len(apix) == 1 and _ok(apix[0], dose)

    pids = [p["id"] for p in ctx.final["patients"]]
    others_changed = []
    for pid in pids:
        before = Counter(med_key(m) for m in active_meds(ctx.initial, pid) if m["name"] != "apixaban")
        after = Counter(med_key(m) for m in active_meds(ctx.final, pid) if m["name"] != "apixaban")
        if before != after:
            others_changed.append(pid)
    new_apix = [pid for pid in pids if pid not in EXPECTED and _apixaban(ctx.final, pid)]
    summary = (ctx.submission or {}).get("summary") or ""
    submitted = set((ctx.submission or {}).get("patient_ids") or [])

    def show(pid):
        return [(m["dose_value"], m["frequency"]) for m in _apixaban(ctx.final, pid)]

    checks = [
        completed_check(ctx),
        Check("nvaf_doses_correct", all(per_patient[p] for p in ("pt-1008", "pt-1019", "pt-1022", "pt-1028")),
              detail="; ".join(f"{p}: {show(p)} want {EXPECTED[p]} twice daily" for p in EXPECTED if p != "pt-1029")),
        Check("non_af_apixaban_unchanged", per_patient["pt-1029"],
              detail=f"pt-1029 (pulmonary embolism): {show('pt-1029')} want 5 twice daily"),
        Check("other_medications_unchanged", not others_changed and not new_apix,
              detail=f"non-apixaban changes: {others_changed}; apixaban added for: {new_apix}"),
        # Diagnostic only: one per patient, plus audit signals.
        *[Check(f"{p}_apixaban_{str(EXPECTED[p]).replace('.', '_')}_mg", per_patient[p], critical=False,
                detail=str(show(p))) for p in EXPECTED],
        Check("summary_cites_harold_current_weight", bool(WEIGHT_CITED.search(summary)), critical=False,
              detail="summary mentions 58 kg or 128 lb"),
        Check("submitted_list_matches_changes", submitted == CHANGED, critical=False,
              detail=f"submitted: {sorted(submitted)}"),
        submitted_check(ctx),
    ]
    return finalize(checks, score=sum(per_patient.values()) / len(per_patient))
