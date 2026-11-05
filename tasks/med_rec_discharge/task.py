"""Post-discharge medication reconciliation. Seven changes across a discharge summary and a later phone note."""

from collections import Counter

from tasks.common import (Check, active_meds, completed_check, finalize, fmt_key, med_key, multiset_jaccard,
                          submitted_check, untouched_check)

MAX_TURNS = 40
TARGET = "pt-1012"
TARGET_PATIENTS = [TARGET]

# Discharge summary (9/28) changes, then the 9/30 phone note supersedes two of them
# (losartan 50 -> 100 mg; empagliflozin discontinued before it was ever started).
EXPECTED = Counter([
    ("losartan", 100.0, "mg", "once daily"),
    ("metoprolol succinate ER", 50.0, "mg", "once daily"),
    ("metformin", 1000.0, "mg", "twice daily"),
    ("aspirin", 81.0, "mg", "once daily"),
    ("atorvastatin", 40.0, "mg", "once daily"),
    ("omeprazole", 20.0, "mg", "once daily"),
])


def grade(ctx):
    got = Counter(med_key(m) for m in active_meds(ctx.final, TARGET))
    names = Counter(k[0] for k in got.elements())
    missing = [fmt_key(k) for k in (EXPECTED - got).elements()]
    extra = [fmt_key(k) for k in (got - EXPECTED).elements()]

    def has(key):
        return got[key] >= 1

    checks = [
        completed_check(ctx),
        Check("active_list_matches_expected", got == EXPECTED, detail=f"missing: {missing}; extra: {extra}"),
        untouched_check(ctx, allowed={TARGET}),
        # Diagnostic, one per intended change, so failures can be read at a glance.
        Check("lisinopril_stopped", names["lisinopril"] == 0, critical=False),
        Check("losartan_100_mg_daily", has(("losartan", 100.0, "mg", "once daily")) and names["losartan"] == 1,
              critical=False, detail="phone note on 9/30 raised it from the discharge dose of 50 mg"),
        Check("hydrochlorothiazide_stopped", names["hydrochlorothiazide"] == 0, critical=False),
        Check("metoprolol_tartrate_stopped", names["metoprolol tartrate"] == 0, critical=False),
        Check("metoprolol_succinate_50_mg_daily", has(("metoprolol succinate ER", 50.0, "mg", "once daily")),
              critical=False),
        Check("metformin_1000_mg_twice_daily", has(("metformin", 1000.0, "mg", "twice daily")) and names["metformin"] == 1,
              critical=False),
        Check("empagliflozin_not_active", names["empagliflozin"] == 0, critical=False,
              detail="started at discharge, discontinued by phone note before she filled it"),
        Check("unchanged_home_meds_kept", all(has(k) for k in [("aspirin", 81.0, "mg", "once daily"),
                                                                ("atorvastatin", 40.0, "mg", "once daily"),
                                                                ("omeprazole", 20.0, "mg", "once daily")]),
              critical=False),
        submitted_check(ctx),
    ]
    return finalize(checks, score=multiset_jaccard(got, EXPECTED))
