"""Anticoagulation-clinic DOAC dose review where every fact is in plain sight. Twelve patients on four different DOACs.

The difficulty is reasoning, not searching: each drug's label uses a different rule and different inputs, and
most patients need creatinine clearance computed by Cockcroft-Gault (actual body weight). Today is 2026-10-01.
Uses its own small fixture (env/fixtures/doac.json), so it does not touch the 30-patient panel. See rubric.md.
"""

from collections import Counter

from env.store import DEFAULT_FIXTURE
from tasks.common import Check, active_meds, completed_check, finalize, med_key, norm_freq, submitted_check

FIXTURE = DEFAULT_FIXTURE.with_name("doac.json")
MAX_TURNS = 80
TARGET_PATIENTS = [f"pt-{n}" for n in range(2001, 2018)]
DOACS = ("apixaban", "rivaroxaban", "dabigatran", "edoxaban")

# patient -> the one correct final anticoagulant (name, mg, frequency); pt-2001 may be any of the alternatives.
EXPECTED = {
    "pt-2002": ("rivaroxaban", 15, "once daily"),   # CrCl 28.9 (<= 50): 15 mg daily. Cr 1.4 is under 1.5.
    "pt-2003": ("dabigatran", 75, "twice daily"),   # CrCl 39.5 (30-50) + dronedarone: 75 mg twice daily.
    "pt-2004": ("apixaban", 5, "twice daily"),      # Age 81 only (88 kg, Cr 1.2 now; 1.6 in January is stale): 5 mg.
    "pt-2005": ("apixaban", 2.5, "twice daily"),    # Age 83 and 57 kg: 2.5 mg. Already correct.
    "pt-2006": ("rivaroxaban", 20, "once daily"),   # CrCl 88.8 (> 50): 20 mg daily. Already correct.
    "pt-2007": ("apixaban", 2.5, "twice daily"),    # No criteria (5 mg), halved for itraconazole, a strong dual inhibitor.
    "pt-2008": ("apixaban", 5, "twice daily"),      # Clarithromycin is the label's exception: no adjustment (diagnostic).
    "pt-2009": ("dabigatran", 75, "twice daily"),   # CrCl 24.6 (15-30), no P-gp inhibitor: 75 mg twice daily.
    "pt-2010": ("edoxaban", 60, "once daily"),      # CrCl 91.8 (50-95): 60 mg. Already correct.
    "pt-2011": ("edoxaban", 30, "once daily"),      # CrCl 39.0 (15-50): 30 mg once daily.
    "pt-2012": ("rivaroxaban", 20, "once daily"),   # CrCl 74.8 (> 50): was on 15 mg, underdosed, 20 mg daily.
    "pt-2013": ("edoxaban", 60, "once daily"),      # 58 kg, CrCl 74.5: weight <= 60 kg lowers edoxaban only for VTE. Correct.
    "pt-2014": ("dabigatran", 150, "twice daily"),  # CrCl 66.9 (> 50): the dronedarone reduction is 30-50 only. Was 75.
    "pt-2015": ("apixaban", 5, "twice daily"),      # Age 79 (80 in Feb 2027), 58 kg, Cr 1.0: weight only. Was 2.5.
    "pt-2016": ("apixaban", 2.5, "twice daily"),    # Age 82 and 125 lb = 56.7 kg: two criteria. Was 5.
    "pt-2017": ("rivaroxaban", 15, "once daily"),   # Woman, CrCl 43.9 with the 0.85 factor (51.6 without). Was 20.
}
# pt-2001 is on edoxaban with CrCl 161 (> 95), which the label says not to use in NVAF. Any of these is a valid switch.
SWITCH_OK = {("apixaban", 5, "twice daily"), ("rivaroxaban", 20, "once daily"), ("dabigatran", 150, "twice daily")}
CHANGED = {"pt-2001", "pt-2002", "pt-2003", "pt-2004", "pt-2007", "pt-2009", "pt-2011", "pt-2012", "pt-2014",
           "pt-2015", "pt-2016", "pt-2017"}
UNCHANGED = ("pt-2005", "pt-2006", "pt-2010", "pt-2013")
# pt-2008 (apixaban 5 mg with clarithromycin) is diagnostic only. The current label (7.1, revised 4/2025) says no
# adjustment, but older labels listed clarithromycin with the inhibitors that need the reduction.
DIAGNOSTIC_UNCHANGED = "pt-2008"


def _doacs(state, pid):
    return [m for m in active_meds(state, pid) if m["name"] in DOACS]


def _key(m):
    return (m["name"], float(m["dose_value"]), norm_freq(m["frequency"])) if m["dose_unit"] == "mg" else None


def _is_exactly(state, pid, want):
    d = _doacs(state, pid)
    return len(d) == 1 and _key(d[0]) == (want[0], float(want[1]), want[2])


def grade(ctx):
    pids = [p["id"] for p in ctx.final["patients"]]
    a = _doacs(ctx.final, "pt-2001")
    a_ok = len(a) == 1 and _key(a[0]) in {(n, float(d), f) for n, d, f in SWITCH_OK}
    ok = {pid: _is_exactly(ctx.final, pid, want) for pid, want in EXPECTED.items()}

    others_changed = []
    for pid in pids:
        before = Counter(med_key(m) for m in active_meds(ctx.initial, pid) if m["name"] not in DOACS)
        after = Counter(med_key(m) for m in active_meds(ctx.final, pid) if m["name"] not in DOACS)
        if before != after:
            others_changed.append(pid)
    submitted = set((ctx.submission or {}).get("patient_ids") or [])

    def show(pid):
        return [(m["name"], m["dose_value"], m["frequency"]) for m in _doacs(ctx.final, pid)]

    named = [
        ("rivaroxaban_reduced_for_low_crcl", "pt-2002", "15 mg daily"),
        ("rivaroxaban_restored_when_crcl_above_50", "pt-2012", "20 mg daily"),
        ("dabigatran_reduced_with_dronedarone", "pt-2003", "75 mg twice daily"),
        ("dabigatran_reduced_for_crcl_15_to_30", "pt-2009", "75 mg twice daily"),
        ("apixaban_raised_when_one_criterion", "pt-2004", "5 mg twice daily"),
        ("apixaban_halved_with_strong_inhibitor", "pt-2007", "2.5 mg twice daily"),
        ("edoxaban_reduced_for_crcl_under_50", "pt-2011", "30 mg daily"),
        ("dabigatran_restored_when_crcl_above_50", "pt-2014", "150 mg twice daily"),
        ("apixaban_raised_at_age_79", "pt-2015", "5 mg twice daily"),
        ("apixaban_reduced_when_weight_in_pounds", "pt-2016", "2.5 mg twice daily"),
        ("rivaroxaban_reduced_with_female_factor", "pt-2017", "15 mg daily"),
    ]
    checks = [
        completed_check(ctx),
        Check("edoxaban_patient_switched", a_ok,
              detail=f"pt-2001: {show('pt-2001')} (edoxaban must go; one DOAC at its labeled dose)"),
        *[Check(name, ok[pid], detail=f"{pid}: {show(pid)} want {want}") for name, pid, want in named],
        Check("correct_doses_left_alone", all(ok[p] for p in UNCHANGED),
              detail="; ".join(f"{p}: {show(p)}" for p in UNCHANGED)),
        Check("other_medications_unchanged", not others_changed, detail=f"non-DOAC changes: {others_changed}"),
        Check("clarithromycin_exception_followed", ok[DIAGNOSTIC_UNCHANGED], critical=False,
              detail=f"{DIAGNOSTIC_UNCHANGED}: {show(DIAGNOSTIC_UNCHANGED)} want apixaban 5 mg twice daily"),
        Check("submitted_list_matches_changes", submitted == CHANGED, critical=False,
              detail=f"submitted: {sorted(submitted)}"),
        submitted_check(ctx),
    ]
    per = [a_ok, *ok.values()]
    return finalize(checks, score=sum(per) / len(per))
