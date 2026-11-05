"""Apixaban dose check where the deciding fact (current weight 128.3 lb = 58.2 kg) is only in the 9/24 visit note."""

import re
from collections import Counter

from tasks.common import (Check, active_meds, completed_check, finalize, med_key, norm_freq, submitted_check,
                          untouched_check)

MAX_TURNS = 30
TARGET = "pt-1008"
TARGET_PATIENTS = [TARGET]

# Eliquis label, NVAF: 2.5 mg twice daily if at least 2 of age >= 80, weight <= 60 kg, serum creatinine >= 1.5 mg/dL.
# Age 81 (yes). Current weight 58.2 kg from the 9/24 note (yes). Creatinine 1.31 (no). 2 of 3 -> 2.5 mg BID.
WEIGHT_CITED = re.compile(r"\b58(\.\d)?\s*kg|\b128(\.3)?\s*(lb|lbs|pounds)", re.I)


def grade(ctx):
    before = active_meds(ctx.initial, TARGET)
    after = active_meds(ctx.final, TARGET)
    apix = [m for m in after if m["name"] == "apixaban"]
    one = apix[0] if len(apix) == 1 else None
    others_before = Counter(med_key(m) for m in before if m["name"] != "apixaban")
    others_after = Counter(med_key(m) for m in after if m["name"] != "apixaban")
    summary = (ctx.submission or {}).get("summary") or ""

    checks = [
        completed_check(ctx),
        Check("exactly_one_active_apixaban", len(apix) == 1,
              detail=f"active apixaban entries: {[(m['dose_value'], m['frequency']) for m in apix]}"),
        Check("apixaban_2_5_mg_twice_daily",
              one is not None and float(one["dose_value"]) == 2.5 and one["dose_unit"] == "mg"
              and norm_freq(one["frequency"]) == "twice daily",
              detail=f"final apixaban: {(one['dose_value'], one['dose_unit'], one['frequency']) if one else None}"),
        Check("other_medications_unchanged", others_before == others_after,
              detail=f"added: {sorted(others_after - others_before)}; removed: {sorted(others_before - others_after)}"),
        untouched_check(ctx, allowed={TARGET}),
        # Diagnostic: used when auditing passes for the right reason (see WRITEUP, false positive audit).
        Check("summary_cites_current_weight", bool(WEIGHT_CITED.search(summary)), critical=False,
              detail="summary mentions 58 kg or 128 lb"),
        submitted_check(ctx),
    ]
    return finalize(checks)
