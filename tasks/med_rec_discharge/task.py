"""Post-discharge medication reconciliation for every patient Valley General discharged since 9/17.

Three patients are in scope (Denise Carter 9/28, Barbara Lewis 9/23, Michael O'Brien 9/22). Two older Valley General
discharges (Harold Bennett 8/30, Margaret Allen 8/15) are out of scope and must not be touched. See rubric.md.
"""

from collections import Counter

from tasks.common import (Check, active_meds, completed_check, finalize, fmt_key, med_key, multiset_jaccard,
                          submitted_check, untouched_check)

MAX_TURNS = 50
DENISE, MICHAEL, BARBARA = "pt-1012", "pt-1006", "pt-1025"
TARGET_PATIENTS = [DENISE, MICHAEL, BARBARA]

EXPECTED = {
    # 9/28 discharge, then the 9/30 phone note (losartan 50 -> 100 mg; empagliflozin stopped before it was filled),
    # then the 10/1 phone note (empagliflozin started after a savings card). Cefpodoxime finished 9/30; inpatient
    # pantoprazole was a formulary substitution for home omeprazole.
    DENISE: Counter([
        ("losartan", 100.0, "mg", "once daily"),
        ("metoprolol succinate ER", 50.0, "mg", "once daily"),
        ("metformin", 1000.0, "mg", "twice daily"),
        ("aspirin", 81.0, "mg", "once daily"),
        ("atorvastatin", 40.0, "mg", "once daily"),
        ("omeprazole", 20.0, "mg", "once daily"),
        ("empagliflozin", 10.0, "mg", "once daily"),
    ]),
    # 9/22 NSTEMI discharge (clopidogrel and pantoprazole started, metoprolol 25 -> 50, lisinopril 5 started), then
    # the 9/25 phone note stops the lisinopril for orthostatic symptoms. Pantoprazole here is a deliberate discharge
    # start for GI protection on dual antiplatelet therapy, unlike Denise's inpatient substitution.
    MICHAEL: Counter([
        ("metformin", 500.0, "mg", "twice daily"),
        ("aspirin", 81.0, "mg", "once daily"),
        ("metoprolol succinate ER", 50.0, "mg", "once daily"),
        ("atorvastatin", 80.0, "mg", "once daily"),
        ("clopidogrel", 75.0, "mg", "once daily"),
        ("pantoprazole", 40.0, "mg", "once daily"),
    ]),
    # 9/23 cellulitis discharge: lisinopril 10 -> 5 mg after AKI. Cephalexin course ended with the 9/29 dose.
    BARBARA: Counter([
        ("metformin", 500.0, "mg", "twice daily"),
        ("lisinopril", 5.0, "mg", "once daily"),
        ("rosuvastatin", 10.0, "mg", "once daily"),
    ]),
}
LABEL = {DENISE: "denise", MICHAEL: "michael", BARBARA: "barbara"}


def grade(ctx):
    got = {pid: Counter(med_key(m) for m in active_meds(ctx.final, pid)) for pid in EXPECTED}

    def diff(pid):
        exp = EXPECTED[pid]
        return (f"missing: {[fmt_key(k) for k in (exp - got[pid]).elements()]}; "
                f"extra: {[fmt_key(k) for k in (got[pid] - exp).elements()]}")

    d_names = Counter(k[0] for k in got[DENISE].elements())
    m_names = Counter(k[0] for k in got[MICHAEL].elements())
    b_names = Counter(k[0] for k in got[BARBARA].elements())
    submitted = set((ctx.submission or {}).get("patient_ids") or [])

    checks = [
        completed_check(ctx),
        *[Check(f"{LABEL[pid]}_list_matches_expected", got[pid] == EXPECTED[pid], detail=diff(pid)) for pid in EXPECTED],
        untouched_check(ctx, allowed=set(EXPECTED)),
        # Diagnostic, one per trap, so failures can be read at a glance.
        Check("denise_losartan_100_mg_daily", got[DENISE][("losartan", 100.0, "mg", "once daily")] == 1
              and d_names["losartan"] == 1, critical=False, detail="9/30 phone note raised it from 50 mg"),
        Check("denise_empagliflozin_restarted", got[DENISE][("empagliflozin", 10.0, "mg", "once daily")] == 1
              and d_names["empagliflozin"] == 1, critical=False, detail="stopped 9/30, restarted 10/1"),
        Check("denise_metoprolol_tartrate_stopped", d_names["metoprolol tartrate"] == 0, critical=False),
        Check("denise_completed_cefpodoxime_not_active", d_names["cefpodoxime"] == 0, critical=False),
        Check("denise_no_inpatient_pantoprazole", d_names["pantoprazole"] == 0, critical=False,
              detail="pantoprazole was a hospital formulary substitution for home omeprazole"),
        Check("michael_clopidogrel_started", m_names["clopidogrel"] == 1, critical=False),
        Check("michael_pantoprazole_started", m_names["pantoprazole"] == 1, critical=False,
              detail="explicit discharge start for GI protection on dual antiplatelet therapy"),
        Check("michael_lisinopril_stopped_by_phone_note", m_names["lisinopril"] == 0, critical=False),
        Check("michael_metoprolol_50_mg", got[MICHAEL][("metoprolol succinate ER", 50.0, "mg", "once daily")] == 1
              and m_names["metoprolol succinate ER"] == 1, critical=False),
        Check("barbara_lisinopril_5_mg", got[BARBARA][("lisinopril", 5.0, "mg", "once daily")] == 1
              and b_names["lisinopril"] == 1, critical=False),
        Check("barbara_completed_cephalexin_not_active", b_names["cephalexin"] == 0, critical=False,
              detail="course ended with the 9/29 dose"),
        Check("submitted_list_matches_scope", submitted == set(EXPECTED), critical=False,
              detail=f"submitted: {sorted(submitted)}"),
        submitted_check(ctx),
    ]
    score = sum(multiset_jaccard(got[pid], EXPECTED[pid]) for pid in EXPECTED) / len(EXPECTED)
    return finalize(checks, score=score)
