"""Builds env/fixtures/doac.json, the small anticoagulation-clinic chart set used by the doac_dose_reasoning task.

It is separate from the 30-patient panel on purpose: the panel's other tasks (apixaban_dose in particular) look at every
patient on a DOAC, and adding patients there would change frozen tasks. Everything the task needs is structured data
(age, weight, creatinine, medication list). Run `python -m env.fixtures.build_doac` after editing this file.
"""

import json
from pathlib import Path

from env.fixtures.build_panel import TODAY, assemble

OUT = Path(__file__).with_name("doac.json")

EXTRA_FORMULARY = [
    ("edoxaban", "edoxaban", "direct oral anticoagulant"),
    ("dronedarone", "dronedarone", "antiarrhythmic"),
    ("diltiazem", "diltiazem", "calcium channel blocker (non-dihydropyridine)"),
    ("itraconazole", "itraconazole", "azole antifungal"),
]

P = []


def patient(pid, given, family, birth, gender, *, conditions=(), meds=(), obs=()):
    P.append(dict(pid=pid, given=given, family=family, birth=birth, gender=gender, active=True, deceased=None,
                  conditions=conditions, meds=meds, allergies=(), obs=obs, notes=(), orders=()))


# Cockcroft-Gault CrCl = (140 - age) x weight / (72 x creatinine), x 0.85 for women, actual body weight.
# Ages are on 2026-10-01. The deciding values are the latest weight (29463-7) and creatinine (2160-0).

# A. Edoxaban with CrCl about 161 mL/min (above 95): not recommended in NVAF. Must be switched.
patient("pt-2001", "Daniel", "Brooks", "1964-03-12", "male",
        conditions=[("AFIB", "2023-02-08", "active"), ("HTN", "2019-05-10", "active")],
        meds=[("lisinopril", 20, "mg", "once daily", "2019-05-10", "active"),
              ("edoxaban", 60, "mg", "once daily", "2023-02-08", "active")],
        obs=[("29463-7", 104.0, "kg", "2026-09-14"), ("2160-0", 0.7, "mg/dL", "2026-09-14")])

# B. Rivaroxaban 20 mg with CrCl about 29 mL/min (50 or below): 15 mg once daily. Creatinine is under 1.5.
patient("pt-2002", "Priya", "Raman", "1952-05-20", "female",
        conditions=[("AFIB", "2024-03-01", "active"), ("HTN", "2010-08-22", "active")],
        meds=[("amlodipine", 5, "mg", "once daily", "2010-08-22", "active"),
              ("rivaroxaban", 20, "mg", "once daily", "2024-03-01", "active")],
        obs=[("29463-7", 52.0, "kg", "2026-09-09"), ("2160-0", 1.4, "mg/dL", "2026-09-09")])

# C. Dabigatran 150 mg twice daily with CrCl about 39 mL/min (30 to 50) and dronedarone: 75 mg twice daily.
patient("pt-2003", "Walter", "Novak", "1948-02-02", "male",
        conditions=[("AFIB", "2022-11-30", "active"), ("HTN", "2012-04-17", "active"), ("HLD", "2014-06-03", "active")],
        meds=[("dronedarone", 400, "mg", "twice daily", "2022-11-30", "active"),
              ("atorvastatin", 20, "mg", "once daily", "2014-06-03", "active"),
              ("dabigatran", 150, "mg", "twice daily", "2022-11-30", "active")],
        obs=[("29463-7", 78.0, "kg", "2026-09-02"), ("2160-0", 1.7, "mg/dL", "2026-09-02")])

# D. Apixaban 2.5 mg, but only the age criterion is met (81; 88 kg; creatinine 1.2): 5 mg twice daily.
#    Diltiazem is a moderate CYP3A4 inhibitor and does not change the apixaban dose. A creatinine of 1.6 in January
#    (second criterion) is stale; the current value is 1.2.
patient("pt-2004", "Samuel", "Greene", "1945-07-15", "male",
        conditions=[("AFIB", "2021-09-06", "active"), ("HTN", "2008-01-19", "active")],
        meds=[("diltiazem", 180, "mg", "once daily", "2021-09-06", "active"),
              ("apixaban", 2.5, "mg", "twice daily", "2024-01-12", "active")],
        obs=[("2160-0", 1.6, "mg/dL", "2026-01-20"), ("29463-7", 88.0, "kg", "2026-09-21"),
             ("2160-0", 1.2, "mg/dL", "2026-09-21")])

# E. Apixaban 2.5 mg, correct (age 83 and weight 57 kg: two criteria). No change.
patient("pt-2005", "Eleanor", "Voss", "1943-01-09", "female",
        conditions=[("AFIB", "2020-06-25", "active"), ("HYPOTHY", "2011-03-02", "active")],
        meds=[("levothyroxine", 50, "mcg", "once daily", "2011-03-02", "active"),
              ("apixaban", 2.5, "mg", "twice daily", "2020-06-25", "active")],
        obs=[("29463-7", 57.0, "kg", "2026-09-18"), ("2160-0", 1.1, "mg/dL", "2026-09-18")])

# F. Rivaroxaban 20 mg with CrCl about 89 mL/min: correct. No change.
patient("pt-2006", "Marcus", "Lee", "1960-04-04", "male",
        conditions=[("AFIB", "2025-02-14", "active"), ("T2DM", "2018-10-09", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2018-10-09", "active"),
              ("rivaroxaban", 20, "mg", "once daily", "2025-02-14", "active")],
        obs=[("29463-7", 95.0, "kg", "2026-09-11"), ("2160-0", 1.1, "mg/dL", "2026-09-11")])

# G. Apixaban 5 mg with itraconazole (strong dual CYP3A4 and P-gp inhibitor). No criteria are met, so the dose would
#    be 5 mg, but the label halves it with a strong dual inhibitor: 2.5 mg twice daily.
patient("pt-2007", "Raymond", "Castillo", "1956-09-10", "male",
        conditions=[("AFIB", "2022-04-19", "active"), ("HTN", "2016-12-05", "active")],
        meds=[("itraconazole", 200, "mg", "once daily", "2026-08-18", "active"),
              ("apixaban", 5, "mg", "twice daily", "2022-04-19", "active")],
        obs=[("29463-7", 80.0, "kg", "2026-09-15"), ("2160-0", 1.0, "mg/dL", "2026-09-15")])

# H. Apixaban 5 mg with clarithromycin. The label carves clarithromycin out: no dose adjustment. No change.
patient("pt-2008", "Gregory", "Hale", "1960-02-21", "male",
        conditions=[("AFIB", "2024-07-02", "active"), ("HTN", "2017-03-14", "active")],
        meds=[("clarithromycin", 500, "mg", "twice daily", "2026-09-24", "active"),
              ("apixaban", 5, "mg", "twice daily", "2024-07-02", "active")],
        obs=[("29463-7", 90.0, "kg", "2026-09-26"), ("2160-0", 1.0, "mg/dL", "2026-09-26")])

# I. Dabigatran 150 mg twice daily with CrCl about 25 mL/min (15 to 30), no P-gp inhibitor: 75 mg twice daily.
patient("pt-2009", "Albert", "Soto", "1951-06-30", "male",
        conditions=[("AFIB", "2023-09-11", "active"), ("CKD4", "2024-02-08", "active")],
        meds=[("metoprolol succinate ER", 50, "mg", "once daily", "2023-09-11", "active"),
              ("dabigatran", 150, "mg", "twice daily", "2023-09-11", "active")],
        obs=[("29463-7", 60.0, "kg", "2026-09-04"), ("2160-0", 2.2, "mg/dL", "2026-09-04")])

# J. Edoxaban 60 mg with CrCl about 92 mL/min (50 to 95): correct, just under the 95 line. No change.
patient("pt-2010", "Victor", "Tran", "1956-03-03", "male",
        conditions=[("AFIB", "2025-01-27", "active"), ("HLD", "2015-10-20", "active")],
        meds=[("atorvastatin", 40, "mg", "once daily", "2015-10-20", "active"),
              ("edoxaban", 60, "mg", "once daily", "2025-01-27", "active")],
        obs=[("29463-7", 85.0, "kg", "2026-09-08"), ("2160-0", 0.9, "mg/dL", "2026-09-08")])

# K. Edoxaban 60 mg with CrCl about 39 mL/min (15 to 50): 30 mg once daily.
patient("pt-2011", "Edgar", "Whitfield", "1947-11-08", "male",
        conditions=[("AFIB", "2023-05-23", "active"), ("HTN", "2009-02-16", "active"), ("CKD3B", "2024-08-30", "active")],
        meds=[("losartan", 50, "mg", "once daily", "2009-02-16", "active"),
              ("edoxaban", 60, "mg", "once daily", "2023-05-23", "active")],
        obs=[("29463-7", 68.0, "kg", "2026-09-17"), ("2160-0", 1.5, "mg/dL", "2026-09-17")])

# L. Rivaroxaban 15 mg once daily with CrCl about 75 mL/min (above 50): underdosed, 20 mg once daily.
patient("pt-2012", "Joan", "Mercer", "1958-05-17", "female",
        conditions=[("AFIB", "2025-06-03", "active"), ("GAD", "2020-01-12", "active")],
        meds=[("sertraline", 50, "mg", "once daily", "2020-01-12", "active"),
              ("rivaroxaban", 15, "mg", "once daily", "2025-06-03", "active")],
        obs=[("29463-7", 88.0, "kg", "2026-09-22"), ("2160-0", 1.0, "mg/dL", "2026-09-22")])

# M. Edoxaban 60 mg at 58 kg with CrCl about 75 mL/min. Weight 60 kg or less lowers the edoxaban dose only for VTE, not
#    for NVAF, so 60 mg is right. No change.
patient("pt-2013", "Theodore", "Ward", "1960-08-09", "male",
        conditions=[("AFIB", "2025-03-18", "active"), ("HLD", "2018-09-04", "active")],
        meds=[("rosuvastatin", 10, "mg", "once daily", "2018-09-04", "active"),
              ("edoxaban", 60, "mg", "once daily", "2025-03-18", "active")],
        obs=[("29463-7", 58.0, "kg", "2026-09-10"), ("2160-0", 0.8, "mg/dL", "2026-09-10")])

# N. Dabigatran 75 mg twice daily with dronedarone, but CrCl is about 67 mL/min. The dronedarone reduction applies only
#    at CrCl 30 to 50, so he is underdosed: 150 mg twice daily.
patient("pt-2014", "Stanley", "Rhodes", "1954-01-20", "male",
        conditions=[("AFIB", "2024-10-07", "active"), ("HTN", "2011-11-29", "active")],
        meds=[("dronedarone", 400, "mg", "twice daily", "2024-10-07", "active"),
              ("dabigatran", 75, "mg", "twice daily", "2024-10-07", "active")],
        obs=[("29463-7", 85.0, "kg", "2026-09-03"), ("2160-0", 1.2, "mg/dL", "2026-09-03")])

# O. Apixaban 2.5 mg, age 79 (born 1947-02-10, turns 80 in February 2027), 58 kg, creatinine 1.0: only the weight criterion,
#    so 5 mg twice daily.
patient("pt-2015", "Harvey", "Lindqvist", "1947-02-10", "male",
        conditions=[("AFIB", "2023-12-04", "active"), ("HTN", "2007-07-11", "active")],
        meds=[("amlodipine", 5, "mg", "once daily", "2007-07-11", "active"),
              ("apixaban", 2.5, "mg", "twice daily", "2023-12-04", "active")],
        obs=[("29463-7", 58.0, "kg", "2026-09-16"), ("2160-0", 1.0, "mg/dL", "2026-09-16")])

# P. Apixaban 5 mg, age 82, weight recorded in pounds (125 lb = 56.7 kg), creatinine 1.1: age and weight criteria,
#    so 2.5 mg twice daily. Reading 125 as kilograms misses the weight criterion.
patient("pt-2016", "Dorothy", "Quinn", "1944-02-14", "female",
        conditions=[("AFIB", "2022-08-23", "active"), ("OSTEOPOROSIS", "2019-04-30", "active")],
        meds=[("alendronate", 70, "mg", "once weekly", "2019-04-30", "active"),
              ("apixaban", 5, "mg", "twice daily", "2022-08-23", "active")],
        obs=[("29463-7", 125.0, "lb", "2026-09-12"), ("2160-0", 1.1, "mg/dL", "2026-09-12")])

# Q. Rivaroxaban 20 mg, woman, 76, 61 kg, creatinine 1.05: CrCl about 44 with the 0.85 factor for women (51.6 without
#    it): 15 mg once daily.
patient("pt-2017", "Margaret", "Doyle", "1950-04-22", "female",
        conditions=[("AFIB", "2024-06-14", "active"), ("HTN", "2013-02-25", "active")],
        meds=[("amlodipine", 5, "mg", "once daily", "2013-02-25", "active"),
              ("rivaroxaban", 20, "mg", "once daily", "2024-06-14", "active")],
        obs=[("29463-7", 61.0, "kg", "2026-09-20"), ("2160-0", 1.05, "mg/dL", "2026-09-20")])


def build():
    state = assemble(P, EXTRA_FORMULARY, fixture_version=1)
    state["meta"]["practice"] = "Riverbend Family Medicine, anticoagulation clinic"
    return state


if __name__ == "__main__":
    OUT.write_text(json.dumps(build(), indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT} ({len(P)} patients, today {TODAY})")
