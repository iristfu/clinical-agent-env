"""Builds env/fixtures/panel.json, the synthetic patient panel every trial starts from.

All patients are fictional. The panel is hand-authored so that every trap a task depends on
is deliberate and documented in that task's rubric.md. Run `python -m env.fixtures.build_panel`
after editing this file; tests/test_env.py checks that panel.json matches this builder.
"""

import json
from pathlib import Path

TODAY = "2026-10-01"
OUT = Path(__file__).with_name("panel.json")

# ---------------------------------------------------------------------------------------------
# Catalogs
# ---------------------------------------------------------------------------------------------

OBSERVATION_CODES = {
    "4548-4": ("Hemoglobin A1c/Hemoglobin.total in Blood", ["HbA1c", "A1c", "glycated hemoglobin", "glycohemoglobin"]),
    "17856-6": ("Hemoglobin A1c/Hemoglobin.total in Blood by HPLC", ["HbA1c", "A1c", "glycated hemoglobin", "glycohemoglobin"]),
    "29463-7": ("Body weight", ["weight", "wt"]),
    "85354-9": ("Blood pressure panel", ["BP", "blood pressure"]),
    "8867-4": ("Heart rate", ["HR", "pulse"]),
    "8310-5": ("Body temperature", ["temperature", "temp"]),
    "2160-0": ("Creatinine [Mass/volume] in Serum or Plasma", ["creatinine", "Cr", "serum creatinine"]),
    "98979-8": ("Glomerular filtration rate/1.73 sq M.predicted (CKD-EPI 2021)", ["eGFR", "GFR"]),
    "2951-2": ("Sodium [Moles/volume] in Serum or Plasma", ["sodium", "Na"]),
    "2823-3": ("Potassium [Moles/volume] in Serum or Plasma", ["potassium", "K"]),
    "1558-6": ("Fasting glucose [Mass/volume] in Serum or Plasma", ["glucose", "fasting glucose", "FPG"]),
    "718-7": ("Hemoglobin [Mass/volume] in Blood", ["hemoglobin", "Hgb", "Hb"]),
    "13457-7": ("Cholesterol in LDL [Mass/volume] in Serum or Plasma by calculation", ["LDL", "cholesterol"]),
    "78012-2": ("Streptococcus pyogenes Ag [Presence] in Throat by Rapid immunoassay", ["rapid strep", "strep", "group A strep", "GAS"]),
}

LAB_CATALOG = [
    {"code": "4548-4", "display": "Hemoglobin A1c", "synonyms": ["HbA1c", "A1c", "glycated hemoglobin", "glycohemoglobin"]},
    {"code": "51990-0", "display": "Basic metabolic panel", "synonyms": ["BMP", "chem 7"]},
    {"code": "24323-8", "display": "Comprehensive metabolic panel", "synonyms": ["CMP", "chem 14"]},
    {"code": "58410-2", "display": "Complete blood count", "synonyms": ["CBC"]},
    {"code": "57698-3", "display": "Lipid panel", "synonyms": ["lipids", "cholesterol panel"]},
    {"code": "3016-3", "display": "Thyroid stimulating hormone", "synonyms": ["TSH"]},
    {"code": "14959-1", "display": "Urine microalbumin/creatinine ratio", "synonyms": ["UACR", "microalbumin"]},
    {"code": "6301-6", "display": "INR", "synonyms": ["PT/INR", "prothrombin time"]},
    {"code": "2160-0", "display": "Creatinine", "synonyms": ["serum creatinine", "Cr"]},
]

# (name, ingredient, drug class)
FORMULARY = [
    ("amoxicillin", "amoxicillin", "penicillin antibiotic"),
    ("amoxicillin-clavulanate", "amoxicillin/clavulanate", "penicillin antibiotic"),
    ("penicillin V potassium", "penicillin V", "penicillin antibiotic"),
    ("benzathine penicillin G", "benzathine penicillin G", "penicillin antibiotic"),
    ("ampicillin", "ampicillin", "penicillin antibiotic"),
    ("cephalexin", "cephalexin", "cephalosporin antibiotic (1st generation)"),
    ("cefadroxil", "cefadroxil", "cephalosporin antibiotic (1st generation)"),
    ("cefuroxime", "cefuroxime", "cephalosporin antibiotic (2nd generation)"),
    ("cefdinir", "cefdinir", "cephalosporin antibiotic (3rd generation)"),
    ("cefpodoxime", "cefpodoxime", "cephalosporin antibiotic (3rd generation)"),
    ("azithromycin", "azithromycin", "macrolide antibiotic"),
    ("clarithromycin", "clarithromycin", "macrolide antibiotic"),
    ("clindamycin", "clindamycin", "lincosamide antibiotic"),
    ("doxycycline", "doxycycline", "tetracycline antibiotic"),
    ("sulfamethoxazole-trimethoprim", "sulfamethoxazole/trimethoprim", "sulfonamide antibiotic"),
    ("levofloxacin", "levofloxacin", "fluoroquinolone antibiotic"),
    ("nitrofurantoin", "nitrofurantoin", "nitrofuran antibiotic"),
    ("apixaban", "apixaban", "direct oral anticoagulant"),
    ("rivaroxaban", "rivaroxaban", "direct oral anticoagulant"),
    ("dabigatran", "dabigatran", "direct oral anticoagulant"),
    ("warfarin", "warfarin", "vitamin K antagonist anticoagulant"),
    ("enoxaparin", "enoxaparin", "low molecular weight heparin"),
    ("lisinopril", "lisinopril", "ACE inhibitor"),
    ("losartan", "losartan", "angiotensin II receptor blocker"),
    ("metoprolol tartrate", "metoprolol tartrate", "beta blocker"),
    ("metoprolol succinate ER", "metoprolol succinate", "beta blocker"),
    ("hydrochlorothiazide", "hydrochlorothiazide", "thiazide diuretic"),
    ("chlorthalidone", "chlorthalidone", "thiazide-like diuretic"),
    ("amlodipine", "amlodipine", "calcium channel blocker"),
    ("furosemide", "furosemide", "loop diuretic"),
    ("spironolactone", "spironolactone", "mineralocorticoid receptor antagonist"),
    ("atorvastatin", "atorvastatin", "statin"),
    ("rosuvastatin", "rosuvastatin", "statin"),
    ("aspirin", "aspirin", "antiplatelet"),
    ("clopidogrel", "clopidogrel", "P2Y12 inhibitor antiplatelet"),
    ("metformin", "metformin", "biguanide"),
    ("metformin ER", "metformin", "biguanide (extended release)"),
    ("empagliflozin", "empagliflozin", "SGLT2 inhibitor"),
    ("glipizide", "glipizide", "sulfonylurea"),
    ("semaglutide", "semaglutide", "GLP-1 receptor agonist"),
    ("insulin glargine", "insulin glargine", "long-acting insulin"),
    ("insulin lispro", "insulin lispro", "rapid-acting insulin"),
    ("omeprazole", "omeprazole", "proton pump inhibitor"),
    ("pantoprazole", "pantoprazole", "proton pump inhibitor"),
    ("levothyroxine", "levothyroxine", "thyroid hormone"),
    ("albuterol HFA", "albuterol", "short-acting beta agonist inhaler"),
    ("fluticasone HFA", "fluticasone", "inhaled corticosteroid"),
    ("sertraline", "sertraline", "SSRI"),
    ("acetaminophen", "acetaminophen", "analgesic"),
    ("ibuprofen", "ibuprofen", "NSAID"),
    ("alendronate", "alendronate", "bisphosphonate"),
    ("prednisone", "prednisone", "corticosteroid"),
    ("sumatriptan", "sumatriptan", "triptan"),
    ("tamsulosin", "tamsulosin", "alpha blocker"),
    ("benzonatate", "benzonatate", "antitussive"),
]


def rx_id(name):
    return "rx-" + name.lower().replace(" ", "-").replace("/", "-")


FORMULARY_BY_NAME = {name: rx_id(name) for name, _, _ in FORMULARY}

ICD = {
    "T2DM": ("ICD-10-CM", "E11.9", "Type 2 diabetes mellitus without complications"),
    "T2DM_HYPER": ("ICD-10-CM", "E11.65", "Type 2 diabetes mellitus with hyperglycemia"),
    "T2DM_CKD": ("ICD-10-CM", "E11.22", "Type 2 diabetes mellitus with diabetic chronic kidney disease"),
    "T2DM_SNOMED": ("SNOMED-CT", "44054006", "Diabetes mellitus type 2"),
    "T1DM": ("ICD-10-CM", "E10.9", "Type 1 diabetes mellitus without complications"),
    "PREDM": ("ICD-10-CM", "R73.03", "Prediabetes"),
    "GDM": ("ICD-10-CM", "O24.419", "Gestational diabetes mellitus in pregnancy, unspecified control"),
    "HTN": ("ICD-10-CM", "I10", "Essential (primary) hypertension"),
    "HLD": ("ICD-10-CM", "E78.5", "Hyperlipidemia, unspecified"),
    "AFIB": ("ICD-10-CM", "I48.91", "Unspecified atrial fibrillation"),
    "CKD3A": ("ICD-10-CM", "N18.31", "Chronic kidney disease, stage 3a"),
    "CKD3B": ("ICD-10-CM", "N18.32", "Chronic kidney disease, stage 3b"),
    "CKD4": ("ICD-10-CM", "N18.4", "Chronic kidney disease, stage 4"),
    "CHF": ("ICD-10-CM", "I50.9", "Heart failure, unspecified"),
    "CAD": ("ICD-10-CM", "I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris"),
    "BPH": ("ICD-10-CM", "N40.0", "Benign prostatic hyperplasia without lower urinary tract symptoms"),
    "GERD": ("ICD-10-CM", "K21.9", "Gastro-esophageal reflux disease without esophagitis"),
    "HYPOTHY": ("ICD-10-CM", "E03.9", "Hypothyroidism, unspecified"),
    "OBESITY": ("ICD-10-CM", "E66.9", "Obesity, unspecified"),
    "ASTHMA": ("ICD-10-CM", "J45.909", "Unspecified asthma, uncomplicated"),
    "RHINITIS": ("ICD-10-CM", "J30.9", "Allergic rhinitis, unspecified"),
    "COPD": ("ICD-10-CM", "J44.9", "Chronic obstructive pulmonary disease, unspecified"),
    "MIGRAINE": ("ICD-10-CM", "G43.909", "Migraine, unspecified, not intractable, without status migrainosus"),
    "GAD": ("ICD-10-CM", "F41.1", "Generalized anxiety disorder"),
    "MDD": ("ICD-10-CM", "F32.A", "Depression, unspecified"),
    "OSTEOPOROSIS": ("ICD-10-CM", "M81.0", "Age-related osteoporosis without current pathological fracture"),
    "OSA": ("ICD-10-CM", "G47.33", "Obstructive sleep apnea"),
    "PCOS": ("ICD-10-CM", "E28.2", "Polycystic ovarian syndrome"),
    "PE": ("ICD-10-CM", "I26.99", "Other pulmonary embolism without acute cor pulmonale"),
    "NSTEMI": ("ICD-10-CM", "I21.4", "Non-ST elevation (NSTEMI) myocardial infarction"),
    "CELLULITIS": ("ICD-10-CM", "L03.116", "Cellulitis of left lower limb"),
    "STREP": ("ICD-10-CM", "J02.0", "Streptococcal pharyngitis"),
}

# ---------------------------------------------------------------------------------------------
# Patients. Each spec lists conditions, meds, allergies, observations, notes and orders.
# Conditions:  (key, onset, status)
# Meds:        (formulary name, dose, unit, frequency, authoredOn, status)
# Observations:(loinc, value, unit, date)
# Notes:       (date, type, author, text)
# ---------------------------------------------------------------------------------------------

P = []


def patient(pid, given, family, birth, gender, *, active=True, deceased=None, conditions=(), meds=(),
            allergies=(), obs=(), notes=(), orders=()):
    P.append(dict(pid=pid, given=given, family=family, birth=birth, gender=gender, active=active,
                  deceased=deceased, conditions=conditions, meds=meds, allergies=allergies, obs=obs,
                  notes=notes, orders=orders))


patient("pt-1001", "James", "Whitaker", "1959-01-11", "male",
        conditions=[("T2DM", "2017-04-02", "active"), ("HTN", "2015-09-14", "active"), ("HLD", "2016-02-20", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2019-06-10", "active"),
              ("lisinopril", 10, "mg", "once daily", "2015-09-14", "active"),
              ("atorvastatin", 20, "mg", "once daily", "2016-02-20", "active")],
        obs=[("4548-4", 7.6, "%", "2025-06-12"), ("4548-4", 7.4, "%", "2025-12-10"),
             ("85354-9", "134/82", "mm[Hg]", "2025-12-10"), ("29463-7", 98.2, "kg", "2025-12-10"),
             ("98979-8", 81, "mL/min/1.73m2", "2025-12-10")],
        notes=[("2025-12-10", "Progress note", "Dr. A. Shah",
                "Follow-up for type 2 diabetes and hypertension. Feels well. Adherent to metformin and lisinopril. "
                "Home glucose readings mostly 120s fasting.\n\nVitals: BP 134/82, HR 76, Wt 98.2 kg.\n\n"
                "Labs: A1c 7.4% (prior 7.6%). eGFR 81.\n\nAssessment/Plan:\n1. Type 2 diabetes, near goal. Continue "
                "metformin 1000 mg twice daily. Reinforced diet and walking.\n2. Hypertension, controlled. Continue "
                "lisinopril.\n3. Hyperlipidemia. Continue atorvastatin.\nReturn in 3 months."),
               ("2026-03-12", "Telephone encounter", "J. Ortiz, MA",
                "Patient called to cancel his diabetes follow-up appointment scheduled for 3/14 due to work travel. "
                "Will call back to reschedule.")])

patient("pt-1002", "Linda", "Park", "1966-04-03", "female",
        conditions=[("HTN", "2018-05-01", "active"), ("GERD", "2020-01-15", "active")],
        meds=[("amlodipine", 5, "mg", "once daily", "2018-05-01", "active"),
              ("omeprazole", 20, "mg", "once daily", "2020-01-15", "active")],
        obs=[("85354-9", "128/80", "mm[Hg]", "2026-05-19"), ("1558-6", 94, "mg/dL", "2026-05-19"),
             ("29463-7", 66.0, "kg", "2026-05-19")],
        notes=[("2026-05-19", "Annual physical", "Dr. M. Okafor",
                "Annual exam. No new concerns. BP 128/80 on amlodipine. Reflux controlled on omeprazole. Fasting "
                "glucose 94, lipids within goal. Age-appropriate screening up to date. Return in one year.")])

# ---- Task strep_allergy: Maria Lopez (1958). Penicillin anaphylaxis documented only inside a 2019 ED note.
MARIA_ED_NOTE = (
    "VALLEY GENERAL HOSPITAL EMERGENCY DEPARTMENT - PROVIDER NOTE\n\n"
    "Chief complaint: Right ankle pain after a fall.\n\n"
    "HPI: 61 year old woman who stepped off a curb awkwardly this afternoon and inverted her right ankle. Immediate "
    "pain and swelling over the lateral ankle. Able to bear weight with difficulty. No head strike, no loss of "
    "consciousness, no other injuries. Took ibuprofen 400 mg at home with partial relief.\n\n"
    "PMH: Hypertension, hyperlipidemia.\n"
    "Medications: Amlodipine 10 mg daily, atorvastatin 20 mg daily.\n"
    "ALLERGIES: Sulfa (rash). Patient also reports that in her 30s she developed hives with lip and throat swelling "
    "about 30 minutes after a dose of Augmentin prescribed for a sinus infection and was treated with epinephrine in "
    "an emergency room. She has not taken it since.\n"
    "Social: Non-smoker, occasional wine.\n\n"
    "Exam: Vitals BP 146/88, HR 84, afebrile. Right ankle with lateral swelling and ecchymosis, tenderness over the "
    "ATFL, no tenderness at the posterior edge or tip of either malleolus, no midfoot tenderness. Neurovascularly "
    "intact distally.\n\n"
    "Imaging: Not indicated per Ottawa ankle rules.\n\n"
    "Assessment: Right lateral ankle sprain, grade I to II.\n"
    "Plan: RICE, ankle brace, ibuprofen as needed with food, crutches as needed. Follow up with primary care in 1 to "
    "2 weeks if not improving. Return precautions discussed. Discharged in stable condition."
)

patient("pt-1003", "Maria", "Lopez", "1958-03-14", "female",
        conditions=[("HTN", "2012-07-09", "active"), ("HLD", "2016-03-22", "active")],
        meds=[("amlodipine", 10, "mg", "once daily", "2014-01-08", "active"),
              ("atorvastatin", 20, "mg", "once daily", "2016-03-22", "active")],
        allergies=[("Sulfonamide antibiotics", "Rash", "low", "medication", "2014-01-08")],
        obs=[("85354-9", "132/80", "mm[Hg]", "2024-11-05"), ("85354-9", "138/84", "mm[Hg]", "2026-10-01"),
             ("8310-5", 38.6, "Cel", "2026-10-01"), ("8867-4", 98, "/min", "2026-10-01"),
             ("29463-7", 71.4, "kg", "2026-10-01"), ("98979-8", 79, "mL/min/1.73m2", "2024-11-05"),
             ("78012-2", "Positive", None, "2026-10-01")],
        notes=[("2019-08-12", "ED provider note (outside record)", "Dr. K. Brennan, Valley General ED", MARIA_ED_NOTE),
               # Routine chart volume (round 3 harder knob). Pushes the ED note to page 2 of her notes; three of
               # these restate the incomplete allergy list. None mention penicillins or the reaction.
               ("2019-08-27", "Progress note", "Dr. A. Shah",
                "ED follow-up for right ankle sprain sustained 8/12. Swelling much improved, walking without the brace "
                "most of the day. Mild residual tenderness over the ATFL. Reviewed home balance and range-of-motion "
                "exercises. BP 134/82 on amlodipine. Return as needed."),
               ("2020-02-11", "Telephone encounter", "J. Ortiz, MA",
                "Patient requested refills of amlodipine and atorvastatin. 90-day supplies sent to pharmacy per "
                "protocol."),
               ("2020-11-03", "Annual physical", "Dr. A. Shah",
                "Annual exam. Feels well. BP 136/84 on amlodipine 10 mg. LDL 102 on atorvastatin 20 mg, continue. "
                "Allergies: sulfa (rash). Mammogram and colonoscopy up to date. Influenza vaccine given. Return in 1 "
                "year."),
               ("2021-06-15", "Progress note", "Dr. M. Okafor",
                "Two days of dysuria and urinary frequency. No fever, flank pain or vaginal symptoms. Urinalysis "
                "positive for leukocyte esterase and nitrites. Uncomplicated cystitis. Nitrofurantoin 100 mg twice "
                "daily for 5 days. Return if fever, flank pain or no improvement in 48 hours."),
               ("2021-11-09", "Annual physical", "Dr. A. Shah",
                "Annual exam. BP 132/80. LDL 94. Allergies: sulfa (rash). Shingles vaccine series started. Influenza "
                "vaccine given. Continue amlodipine and atorvastatin. Return in 1 year."),
               ("2022-11-15", "Annual physical", "Dr. A. Shah",
                "Annual exam. No new concerns. BP 130/82, LDL 98. Second shingles vaccine dose given. Mammogram "
                "ordered. Continue current medications."),
               ("2023-03-07", "Progress note", "Dr. M. Okafor",
                "Left shoulder pain for 6 weeks after painting her kitchen, worse reaching overhead. Painful arc, "
                "strength preserved, negative drop-arm test. Rotator cuff tendinopathy. Physical therapy referral, "
                "ibuprofen 400 mg as needed with food for up to 2 weeks."),
               ("2023-11-14", "Annual physical", "Dr. A. Shah",
                "Annual exam. Shoulder pain resolved after physical therapy. BP 134/80, LDL 99. Colonoscopy due next "
                "year, referral placed. Influenza and updated COVID-19 vaccines given. Continue current regimen."),
               ("2025-05-20", "Telephone encounter", "J. Ortiz, MA",
                "Pharmacy refill request for atorvastatin 20 mg. Approved per protocol. Reminded patient she is due "
                "for her annual visit in the fall."),
               ("2025-11-18", "Annual physical", "Dr. A. Shah",
                "Annual exam. Feels well, walking 3 days a week. BP 130/78 on amlodipine 10 mg. LDL 92 on "
                "atorvastatin 20 mg. Medication allergies reviewed with patient: sulfa (rash). Influenza vaccine "
                "given. Return in 1 year."),
               ("2026-09-30", "Patient portal message", "Riverbend Family Medicine",
                "Patient message: sore throat since yesterday with fever to 101 at home, and her husband was treated "
                "for strep last week. Scheduled for a same-day visit tomorrow morning with Dr. Shah."),
               ("2024-11-05", "Progress note", "Dr. A. Shah",
                "Hypertension and lipid follow-up. Feels well. BP 132/80 on amlodipine 10 mg. LDL 96 on atorvastatin "
                "20 mg. Allergies reviewed with patient: sulfa. Continue current regimen, return in 1 year."),
               ("2026-10-01", "Urgent visit", "Dr. A. Shah",
                "Same-day visit for sore throat.\n\nHPI: 2 days of sore throat, painful swallowing and subjective "
                "fevers. No cough, no rhinorrhea. Husband had similar symptoms last week.\n\nVitals: T 38.6 C, HR 98, "
                "BP 138/84, Wt 71.4 kg.\nExam: Tonsillar erythema with bilateral exudate, tender anterior cervical "
                "lymphadenopathy. Lungs clear.\n\nRapid strep antigen: POSITIVE.\n\nAssessment: Group A "
                "streptococcal pharyngitis.\nPlan: Antibiotic therapy to be ordered. Acetaminophen as needed, fluids, "
                "salt water gargles. Return if unable to swallow liquids, drooling, or worsening after 48 hours of "
                "treatment.")])

patient("pt-1004", "Robert", "Chen", "1971-08-22", "male",
        conditions=[("T2DM_HYPER", "2018-10-30", "active"), ("OBESITY", "2018-10-30", "active"), ("HLD", "2019-01-12", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2018-10-30", "active"),
              ("glipizide", 5, "mg", "once daily", "2022-04-11", "active"),
              ("atorvastatin", 40, "mg", "once daily", "2019-01-12", "active")],
        obs=[("4548-4", 9.1, "%", "2025-12-02"), ("4548-4", 9.6, "%", "2026-06-18"), ("29463-7", 112.5, "kg", "2026-06-18")],
        notes=[("2026-06-18", "Progress note", "Dr. M. Okafor",
                "Diabetes follow-up. A1c 9.6%, up from 9.1%. Admits to inconsistent diet since a job change. Discussed "
                "adding a GLP-1 receptor agonist; patient would like to work on diet first. Continue metformin and "
                "glipizide. Recheck A1c at next visit.")])

patient("pt-1005", "Patricia", "Gomez", "1980-11-30", "female",
        conditions=[("T1DM", "1994-06-01", "active"), ("HYPOTHY", "2011-03-10", "active")],
        meds=[("insulin glargine", 22, "units", "at bedtime", "2015-02-02", "active"),
              ("insulin lispro", 6, "units", "three times daily", "2015-02-02", "active"),
              ("levothyroxine", 75, "mcg", "once daily", "2011-03-10", "active")],
        obs=[("4548-4", 8.1, "%", "2025-10-05"), ("29463-7", 61.2, "kg", "2025-10-05")],
        notes=[("2025-10-05", "Progress note", "Dr. A. Shah",
                "Type 1 diabetes since age 13, managed by endocrinology (Dr. Varga) with insulin pump transition being "
                "discussed. A1c 8.1% per endocrinology. Hypothyroidism stable on levothyroxine. Return in 1 year.")])

patient("pt-1006", "Michael", "O'Brien", "1953-06-07", "male",
        conditions=[("T2DM_SNOMED", "2014-05-19", "active"), ("CAD", "2018-11-02", "active"), ("HTN", "2012-08-08", "active")],
        meds=[("metformin", 500, "mg", "twice daily", "2014-05-19", "active"),
              ("aspirin", 81, "mg", "once daily", "2018-11-02", "active"),
              ("metoprolol succinate ER", 25, "mg", "once daily", "2018-11-02", "active"),
              ("atorvastatin", 80, "mg", "once daily", "2018-11-02", "active")],
        obs=[("4548-4", 6.8, "%", "2025-09-15"), ("85354-9", "126/76", "mm[Hg]", "2025-09-15")],
        notes=[("2025-09-15", "Progress note", "Dr. M. Okafor",
                "Chronic disease follow-up. Diabetes well controlled on metformin, A1c 6.8%. CAD stable, no angina. "
                "BP 126/76. Continue current medications. Return in 6 months."),
               # ---- Task med_rec_discharge (breadth): NSTEMI discharge, then a phone note stops the new lisinopril.
               ("2026-09-22", "Discharge summary (outside record)", "Dr. H. Adeyemi, Valley General Hospital",
                "VALLEY GENERAL HOSPITAL - DISCHARGE SUMMARY\n\nAdmission 2026-09-18. Discharge 2026-09-22.\n"
                "Attending: Dr. H. Adeyemi, Cardiology\n\nPrincipal diagnosis: Non-ST elevation myocardial "
                "infarction.\nSecondary diagnoses: Coronary artery disease, hypertension, hyperlipidemia.\n\n"
                "Hospital course: 73 year old man presented with 2 hours of substernal chest pressure. Troponin peaked "
                "at 4.2 ng/mL. Cardiac catheterization on 9/19 showed a 90% proximal LAD stenosis, treated with a "
                "drug-eluting stent. His oral home medications were held for 48 hours after contrast and resumed on "
                "9/21 at home doses. He received a heparin infusion, and pantoprazole 40 mg daily for stress ulcer prophylaxis, "
                "during the admission. Echo EF 50%.\n\nDischarge medications: Continue aspirin 81 mg daily "
                "indefinitely. Start clopidogrel 75 mg once daily for at least 12 months of dual antiplatelet "
                "therapy; do not interrupt without speaking to cardiology. Metoprolol succinate ER is increased from "
                "25 mg to 50 mg once daily. Continue atorvastatin 80 mg daily. Start lisinopril 5 mg once daily. "
                "Start pantoprazole 40 mg once daily for GI protection while on dual antiplatelet therapy. Continue "
                "his other home medications unchanged.\n\nFollow-up: Cardiology in 2 weeks. PCP within 1 week."),
               ("2026-09-25", "Telephone encounter", "T. Nakamura, RN",
                "Patient called reporting lightheadedness when standing since coming home. Home BP readings 96/58 to "
                "104/62, HR 56 to 60. No chest pain, no syncope. Discussed with Dr. Okafor, who advises stopping the "
                "lisinopril for now and continuing metoprolol succinate ER 50 mg once daily. Recheck BP at the 10/2 "
                "visit. Patient verbalized understanding.")])

patient("pt-1007", "Susan", "Miller", "1949-12-19", "female", active=False, deceased="2026-07-02",
        conditions=[("T2DM", "2009-03-03", "active"), ("CHF", "2019-07-21", "active"), ("CKD4", "2023-02-14", "active")],
        meds=[("insulin glargine", 10, "units", "at bedtime", "2020-05-05", "stopped"),
              ("furosemide", 40, "mg", "twice daily", "2019-07-21", "stopped")],
        obs=[("4548-4", 7.0, "%", "2025-11-20")],
        notes=[("2025-11-20", "Progress note", "Dr. A. Shah",
                "Advanced heart failure and CKD stage 4. Patient and family have elected hospice care. A1c 7.0%. "
                "Simplify regimen, comfort-focused goals."),
               ("2026-07-03", "Administrative note", "Riverbend Family Medicine",
                "Death notification received from hospice. Patient died at home on 2026-07-02. Chart closed.")])

# ---- Task apixaban_dose: Harold Bennett. Current weight lives only in the 9/24 visit note, in pounds.
patient("pt-1008", "Harold", "Bennett", "1945-02-20", "male",
        conditions=[("AFIB", "2021-04-12", "active"), ("HTN", "2008-01-15", "active"),
                    ("CKD3A", "2022-09-30", "active"), ("BPH", "2016-06-06", "active")],
        meds=[("apixaban", 5, "mg", "twice daily", "2021-04-12", "active"),
              ("metoprolol succinate ER", 50, "mg", "once daily", "2021-04-12", "active"),
              ("furosemide", 20, "mg", "once daily", "2022-09-30", "active"),
              ("tamsulosin", 0.4, "mg", "once daily", "2016-06-06", "active")],
        obs=[("29463-7", 64.4, "kg", "2025-12-02"), ("29463-7", 63.5, "kg", "2026-05-14"),
             ("2160-0", 1.24, "mg/dL", "2025-12-02"), ("2160-0", 1.29, "mg/dL", "2026-05-14"),
             ("2160-0", 1.46, "mg/dL", "2026-08-28"), ("2160-0", 1.31, "mg/dL", "2026-09-24"),
             ("98979-8", 57, "mL/min/1.73m2", "2025-12-02"), ("98979-8", 54, "mL/min/1.73m2", "2026-05-14"),
             ("98979-8", 46, "mL/min/1.73m2", "2026-08-28"), ("98979-8", 53, "mL/min/1.73m2", "2026-09-24"),
             ("718-7", 12.1, "g/dL", "2026-09-24"), ("2823-3", 4.3, "mmol/L", "2026-09-24"),
             ("85354-9", "122/74", "mm[Hg]", "2026-05-14"), ("85354-9", "118/70", "mm[Hg]", "2026-09-24")],
        notes=[("2025-12-02", "Progress note", "Dr. M. Okafor",
                "Atrial fibrillation follow-up. Rate controlled on metoprolol, no bleeding on apixaban 5 mg twice "
                "daily. Wt 64.4 kg, creatinine 1.24. Reviewed apixaban dosing: meets age criterion only, so standard "
                "dose remains appropriate. CKD 3a stable. Continue current regimen."),
               ("2026-08-30", "Discharge summary (outside record)", "Dr. P. Lindqvist, Valley General Hospital",
                "Admission 2026-08-26 to 2026-08-30.\n\nDiagnoses: Community-acquired pneumonia, dehydration with "
                "acute kidney injury (creatinine peak 1.46, baseline about 1.25), atrial fibrillation.\n\nHospital "
                "course: Treated with ceftriaxone then oral cefpodoxime, completed course. IV fluids with improvement "
                "in renal function. Poor oral intake throughout admission.\n\nDischarge weight 60.8 kg (about 63.5 "
                "kg in May).\n\nAnticoagulation: Apixaban continued at 5 mg twice daily.\n\nFollow-up: PCP within "
                "1 month with BMP and CBC."),
               ("2026-09-24", "Progress note", "Dr. M. Okafor",
                "Post-hospital follow-up after admission for pneumonia and AKI. Cough resolved. Appetite still poor, "
                "eating about half of usual meals, no nausea or melena. No bleeding or bruising on apixaban. Walking "
                "with a cane at home.\n\nVitals: BP 118/70, HR 68 irregularly irregular, SpO2 97% on room air, Wt "
                "128.3 lb on clinic scale (shoes off).\n\nExam: Thin, comfortable. Lungs clear. No edema.\n\n"
                "Assessment/Plan:\n1. Pneumonia, resolved.\n2. Weight loss, ongoing. Nutrition referral, add oral "
                "supplements.\n3. Atrial fibrillation on apixaban. BMP and CBC drawn today. Will review anticoagulant "
                "dosing once labs result.\n4. CKD 3a. Recheck renal function with today's labs."),
               ("2026-09-28", "Pharmacy consult", "S. Patel, PharmD, Clinical Pharmacist",
                "Anticoagulation review requested by Dr. Okafor after the 9/24 visit.\n\nIndication: nonvalvular atrial "
                "fibrillation. Current regimen: apixaban 5 mg twice daily.\n\nLabel dose-reduction criteria (2.5 mg "
                "twice daily if at least 2 of 3), using results in the chart:\n- Age 81: meets.\n- Weight 63.5 kg "
                "(5/14/2026, most recent weight on the flowsheet; no weight was recorded at the 9/24 visit): does not "
                "meet (>60 kg).\n- Serum creatinine 1.31 "
                "mg/dL (9/24/2026): does not meet (<1.5).\n\nMeets 1 of 3 criteria. Recommend continuing apixaban "
                "5 mg twice daily. Hgb 12.1, stable. No interacting medications identified.")])

patient("pt-1009", "Karen", "Nguyen", "1975-03-27", "female",
        conditions=[("PREDM", "2023-08-20", "active"), ("OBESITY", "2023-08-20", "active")],
        obs=[("4548-4", 5.9, "%", "2024-08-20"), ("4548-4", 6.1, "%", "2025-08-14"), ("29463-7", 88.0, "kg", "2025-08-14")],
        notes=[("2025-08-14", "Progress note", "Dr. A. Shah",
                "Prediabetes follow-up. A1c 6.1%, still in the prediabetes range. Not on medication. Lifestyle "
                "counseling provided and referred to the diabetes prevention program. Recheck A1c in 1 year.")])

patient("pt-1010", "David", "Kim", "1968-09-14", "male",
        conditions=[("T2DM", "2019-02-11", "active"), ("HTN", "2019-02-11", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2026-07-22", "active"),
              ("losartan", 50, "mg", "once daily", "2026-07-22", "active")],
        obs=[("85354-9", "136/84", "mm[Hg]", "2026-07-22"), ("29463-7", 91.7, "kg", "2026-07-22")],
        notes=[("2026-07-22", "New patient visit", "Dr. M. Okafor",
                "New patient establishing care after moving from Arizona. History of type 2 diabetes since 2019 and "
                "hypertension. Reports last A1c was 'around 7' about a year ago. Outside records requested, not yet "
                "received. Continue metformin 1000 mg twice daily and losartan 50 mg daily. Return in 3 months.")])

patient("pt-1011", "Angela", "Rossi", "1984-02-08", "female",
        conditions=[("GDM", "2019-07-15", "resolved"), ("MIGRAINE", "2015-10-02", "active")],
        meds=[("sumatriptan", 50, "mg", "as needed", "2015-10-02", "active")],
        obs=[("4548-4", 5.4, "%", "2020-03-02")],
        notes=[("2020-03-02", "Postpartum follow-up", "Dr. A. Shah",
                "Postpartum visit. Gestational diabetes during pregnancy, diet controlled. Postpartum A1c 5.4%, "
                "gestational diabetes resolved. Recommend diabetes screening every 3 years.")])

# ---- Task med_rec_discharge: Denise Carter. Structured list never updated after discharge; a later phone note supersedes part of it.
DENISE_DC = (
    "VALLEY GENERAL HOSPITAL - DISCHARGE SUMMARY\n\n"
    "Admission 2026-09-24. Discharge 2026-09-28.\n"
    "Attending: Dr. R. Feld, Hospital Medicine\n\n"
    "Principal diagnosis: Hypertensive urgency.\n"
    "Secondary diagnoses: Hyponatremia, E. coli urinary tract infection, type 2 diabetes mellitus with "
    "hyperglycemia, chronic cough.\n\n"
    "Hospital course: 64 year old woman presented with headache and BP 212/118 without evidence of end-organ damage. "
    "Admission sodium 128, attributed to hydrochlorothiazide, improved to 133 with fluid restriction and holding the "
    "thiazide. Urinalysis on admission showed pyuria and culture grew pan-sensitive E. coli; she received ceftriaxone "
    "on 9/24 and 9/25 and was switched to oral cefpodoxime 200 mg twice daily on 9/26 to complete a 7-day course, "
    "with the final dose due the evening of 9/30. A1c 8.4%. She also reported a dry cough for about 8 months, which "
    "her PCP had previously attributed to lisinopril. During the admission she received enoxaparin for VTE "
    "prophylaxis, insulin lispro correction scale, and pantoprazole 40 mg daily, which was substituted for her home "
    "omeprazole per the hospital formulary. BP improved on the regimen below.\n\n"
    "Discharge medications: Her lisinopril was discontinued given the persistent dry cough attributed to the ACE "
    "inhibitor, and she was started on losartan 50 mg once daily in its place. Hydrochlorothiazide was stopped "
    "because of the hyponatremia and should not be restarted. For adherence, her metoprolol tartrate 25 mg twice "
    "daily was changed to metoprolol succinate ER 50 mg once daily. Metformin was increased to 1000 mg twice daily "
    "and empagliflozin 10 mg once daily was added for glycemic control. She should continue aspirin 81 mg daily "
    "and atorvastatin 40 mg daily, and continue cefpodoxime as above until the course is complete. All other home "
    "medications are to be continued unchanged.\n\n"
    "Follow-up: PCP within 1 week. BMP in 1 week to recheck sodium and potassium."
)

patient("pt-1012", "Denise", "Carter", "1962-05-09", "female",
        conditions=[("T2DM", "2016-01-20", "active"), ("HTN", "2010-11-03", "active"),
                    ("HLD", "2013-04-17", "active"), ("GERD", "2019-08-08", "active")],
        meds=[("lisinopril", 20, "mg", "once daily", "2012-02-01", "active"),
              ("metoprolol tartrate", 25, "mg", "twice daily", "2017-06-12", "active"),
              ("hydrochlorothiazide", 25, "mg", "once daily", "2014-09-30", "active"),
              ("atorvastatin", 40, "mg", "once daily", "2013-04-17", "active"),
              ("metformin", 500, "mg", "twice daily", "2016-01-20", "active"),
              ("aspirin", 81, "mg", "once daily", "2016-01-20", "active"),
              ("omeprazole", 20, "mg", "once daily", "2019-08-08", "active")],
        obs=[("4548-4", 7.6, "%", "2026-03-15"), ("4548-4", 8.4, "%", "2026-09-25"),
             ("2951-2", 128, "mmol/L", "2026-09-24"), ("2951-2", 133, "mmol/L", "2026-09-28"),
             ("2823-3", 4.1, "mmol/L", "2026-09-28"), ("98979-8", 71, "mL/min/1.73m2", "2026-09-28"),
             ("85354-9", "212/118", "mm[Hg]", "2026-09-24"), ("85354-9", "146/88", "mm[Hg]", "2026-09-28")],
        notes=[("2026-03-15", "Progress note", "Dr. M. Okafor",
                "Chronic disease follow-up. A1c 7.6%. BP 138/86. Reports a dry, nonproductive cough for about two "
                "months without fever or reflux worsening. Possibly ACE inhibitor related. Will monitor; consider "
                "switching lisinopril to an ARB if it persists. Continue current medications."),
               ("2026-09-28", "Discharge summary (outside record)", "Dr. R. Feld, Valley General Hospital", DENISE_DC),
               ("2026-09-30", "Telephone encounter", "T. Nakamura, RN",
                "Patient called with home BP log since discharge, readings 148 to 156 over 88 to 94. Headache resolved. "
                "Discussed with Dr. Okafor, who advises increasing losartan to 100 mg once daily starting today. "
                "Patient also reports she did not fill the empagliflozin because of cost ($180 copay). Per Dr. "
                "Okafor, discontinue empagliflozin for now and revisit options at the 10/6 follow-up visit. Patient "
                "verbalized understanding. BMP scheduled for 10/5."),
               ("2026-10-01", "Telephone encounter", "T. Nakamura, RN",
                "Patient called back this morning. She enrolled in the manufacturer savings program, her empagliflozin "
                "copay is now $10, and she picked it up today. Discussed with Dr. Okafor, who advises starting "
                "empagliflozin 10 mg once daily today as prescribed at discharge. All other medications as discussed "
                "on 9/30. Reviewed sick-day guidance and genital hygiene. Keep 10/6 follow-up.")])

patient("pt-1013", "Thomas", "Wright", "1957-10-01", "male",
        conditions=[("T2DM_CKD", "2015-03-18", "active"), ("CKD3B", "2021-05-05", "active"), ("HTN", "2009-09-09", "active")],
        meds=[("metformin", 500, "mg", "twice daily", "2015-03-18", "active"),
              ("empagliflozin", 10, "mg", "once daily", "2021-05-05", "active"),
              ("lisinopril", 20, "mg", "once daily", "2009-09-09", "active")],
        obs=[("4548-4", 8.2, "%", "2025-08-10"), ("4548-4", 7.9, "%", "2026-02-14"), ("98979-8", 38, "mL/min/1.73m2", "2026-02-14")],
        notes=[("2026-02-14", "Progress note", "Dr. A. Shah",
                "Diabetes with CKD 3b. A1c 7.9%. eGFR 38, metformin kept at 500 mg twice daily. Continue "
                "empagliflozin. Return in 6 months."),
               ("2026-09-20", "Telephone encounter", "J. Ortiz, MA",
                "Patient requested lab orders before his upcoming visit. A1c and BMP ordered per standing protocol. "
                "Patient plans to go to the lab next week.")],
        orders=[("4548-4", "Hemoglobin A1c", "active", "2026-09-20", "Diabetes monitoring, standing protocol"),
                ("51990-0", "Basic metabolic panel", "active", "2026-09-20", "CKD monitoring, standing protocol")])

patient("pt-1014", "Nancy", "Fischer", "1961-07-15", "female",
        conditions=[("PREDM", "2024-03-11", "active"), ("HLD", "2018-02-02", "active"), ("HYPOTHY", "2012-12-12", "active")],
        meds=[("metformin", 500, "mg", "once daily", "2025-11-18", "active"),
              ("atorvastatin", 20, "mg", "once daily", "2018-02-02", "active"),
              ("levothyroxine", 50, "mcg", "once daily", "2012-12-12", "active")],
        obs=[("4548-4", 6.3, "%", "2025-05-06"), ("1558-6", 131, "mg/dL", "2025-11-10"),
             ("4548-4", 6.9, "%", "2025-11-18"), ("1558-6", 142, "mg/dL", "2025-11-18")],
        notes=[("2025-11-18", "Progress note", "Dr. A. Shah",
                "Follow-up for hypothyroidism and lipids. Reports mild fatigue and cold intolerance over the past two "
                "months. Taking levothyroxine on an empty stomach, no missed doses. TSH 3.1, in range on 50 mcg, so no "
                "dose change; fatigue more likely related to poor sleep, discussed sleep hygiene. LDL 88 on "
                "atorvastatin 20 mg, at goal, continue.\n\nAlso reviewed glucose results: A1c 6.9% today, up from 6.3% "
                "in May, with fasting glucose 131 on 11/10 and 142 today. This meets diagnostic criteria for type 2 "
                "diabetes mellitus. Discussed the diagnosis with the patient. Start metformin 500 mg daily with "
                "dinner, titrate as tolerated. Diabetes education referral. Problem list to be updated. Return in 3 "
                "months."),
               ("2026-02-27", "Telephone encounter", "J. Ortiz, MA",
                "Pharmacy refill request for metformin 500 mg. Approved per protocol. Patient has not yet scheduled "
                "her 3 month follow-up; message left.")])

patient("pt-1015", "Gary", "Hughes", "1950-05-05", "male",
        conditions=[("T2DM", "2012-10-10", "active"), ("HTN", "2010-03-03", "active"), ("BPH", "2017-01-19", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2012-10-10", "active"),
              ("lisinopril", 20, "mg", "once daily", "2010-03-03", "active"),
              ("tamsulosin", 0.4, "mg", "once daily", "2017-01-19", "active")],
        obs=[("4548-4", 7.5, "%", "2025-12-01"), ("17856-6", 7.2, "%", "2026-07-08")],
        notes=[("2026-07-08", "Results note", "Dr. M. Okafor",
                "Outside labs from Quest reviewed (drawn at his cardiology visit): A1c 7.2% by HPLC, LDL 74. Diabetes "
                "at goal. No changes.")])

patient("pt-1016", "Brenda", "Scott", "1973-01-29", "female",
        conditions=[("T2DM", "2021-06-15", "active"), ("OBESITY", "2021-06-15", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2021-06-15", "active"),
              ("semaglutide", 0.5, "mg", "once weekly", "2024-09-01", "active")],
        obs=[("4548-4", 6.8, "%", "2025-09-02"), ("4548-4", 6.5, "%", "2026-03-09"), ("29463-7", 94.1, "kg", "2026-03-09")],
        notes=[("2026-03-09", "Progress note", "Dr. A. Shah",
                "Diabetes follow-up. A1c 6.5% on metformin and semaglutide, at goal. Weight down 6 kg over the past "
                "year. Continue current regimen. Return in 6 months.")])

patient("pt-1017", "Maria", "Lopez", "1991-07-02", "female",
        conditions=[("ASTHMA", "2008-04-04", "active"), ("RHINITIS", "2010-05-05", "active")],
        meds=[("albuterol HFA", 2, "puffs", "as needed", "2008-04-04", "active"),
              ("fluticasone HFA", 110, "mcg", "twice daily", "2019-10-10", "active")],
        obs=[("85354-9", "112/70", "mm[Hg]", "2023-02-24"), ("8310-5", 38.3, "Cel", "2026-10-01"),
             ("78012-2", "Positive", None, "2026-10-01")],
        notes=[("2023-02-10", "Progress note", "Dr. M. Okafor",
                "Acute bacterial sinusitis, symptoms for 12 days with facial pain and purulent drainage. No known drug "
                "allergies. Prescribed amoxicillin 875 mg twice daily for 10 days. Asthma well controlled."),
               ("2023-02-24", "Progress note", "Dr. M. Okafor",
                "Sinusitis follow-up. Completed amoxicillin without side effects. Symptoms resolved. Asthma stable on "
                "fluticasone."),
               # ---- Task strep_allergy (breadth): the second Maria Lopez is also positive today; no allergies.
               ("2026-10-01", "Urgent visit", "Dr. M. Okafor",
                "Walk-in visit for sore throat.\n\nHPI: 2 days of sore throat and fever, painful swallowing, no "
                "cough. Asthma at baseline.\n\nVitals: T 38.3 C, HR 94, SpO2 98%.\nExam: Tonsillar exudate, "
                "tender anterior cervical nodes, lungs clear.\n\nRapid strep antigen: POSITIVE.\n\nAssessment: "
                "Group A streptococcal pharyngitis.\nPlan: Antibiotic to be ordered.")])

patient("pt-1018", "Kevin", "Patel", "1964-12-12", "male",
        conditions=[("T2DM", "2014-07-07", "active"), ("HLD", "2014-07-07", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2014-07-07", "active"),
              ("glipizide", 10, "mg", "once daily", "2020-02-20", "active"),
              ("atorvastatin", 40, "mg", "once daily", "2014-07-07", "active")],
        obs=[("4548-4", 8.3, "%", "2025-11-03"), ("4548-4", 8.8, "%", "2026-05-02")],
        notes=[("2026-05-02", "Progress note", "Dr. M. Okafor",
                "A1c 8.8%. Discussed adding basal insulin versus a GLP-1 receptor agonist; patient will consider. "
                "Return in 3 months.")])

# ---- Task apixaban_dose (breadth): NVAF, meets only the weight criterion; a transient AKI creatinine is a distractor.
patient("pt-1019", "Lisa", "Thompson", "1958-08-25", "female",
        conditions=[("HYPOTHY", "2004-04-04", "active"), ("OSTEOPOROSIS", "2021-11-11", "active"),
                    ("AFIB", "2024-03-05", "active")],
        meds=[("levothyroxine", 88, "mcg", "once daily", "2004-04-04", "active"),
              ("alendronate", 70, "mg", "once weekly", "2021-11-11", "active"),
              ("apixaban", 5, "mg", "twice daily", "2024-03-05", "active")],
        obs=[("29463-7", 60.5, "kg", "2024-03-05"), ("2160-0", 0.79, "mg/dL", "2024-03-05"),
             ("29463-7", 58.9, "kg", "2026-04-20"), ("2160-0", 0.82, "mg/dL", "2026-04-20"),
             ("2160-0", 1.74, "mg/dL", "2026-08-18"), ("98979-8", 32, "mL/min/1.73m2", "2026-08-18"),
             ("2160-0", 0.86, "mg/dL", "2026-09-02"), ("98979-8", 73, "mL/min/1.73m2", "2026-09-02"),
             ("29463-7", 57.8, "kg", "2026-09-02")],
        notes=[("2024-03-05", "Progress note", "Dr. A. Shah",
                "Palpitations for 2 weeks. ECG shows atrial fibrillation, rate 104. Echo: structurally normal valves, "
                "EF 60%. CHA2DS2-VASc 2 (age 65 to 74, female). Discussed anticoagulation; she would like to start. "
                "Apixaban 5 mg twice daily. Age 65, weight 60.5 kg, creatinine 0.79, so no dose-reduction criteria "
                "apply. Rate acceptable at rest, recheck in 4 weeks."),
               ("2026-04-20", "Annual physical", "Dr. A. Shah",
                "Annual exam. TSH in range. DEXA stable on alendronate. Atrial fibrillation rate controlled without "
                "medication, no bleeding on apixaban. No concerns."),
               ("2026-08-18", "Urgent visit", "Dr. M. Okafor",
                "Three days of vomiting and diarrhea after a family gathering, now with lightheadedness and poor oral "
                "intake. Orthostatic on exam. Creatinine 1.74 today (baseline about 0.8). Acute kidney injury from "
                "volume depletion. Given 2 L IV fluids in the infusion room with improvement. Oral rehydration, "
                "recheck BMP in 2 weeks."),
               ("2026-09-02", "Progress note", "Dr. M. Okafor",
                "AKI follow-up. GI symptoms resolved, eating and drinking normally. Wt 57.8 kg. Creatinine back to "
                "0.86. Atrial fibrillation rate controlled. Continue current medications.")])

patient("pt-1020", "Steven", "Adams", "1955-04-18", "male",
        conditions=[("T2DM", "2016-08-08", "active"), ("OSA", "2018-03-03", "active"), ("HTN", "2016-08-08", "active")],
        meds=[("metformin", 1000, "mg", "twice daily", "2016-08-08", "active"),
              ("amlodipine", 10, "mg", "once daily", "2016-08-08", "active")],
        obs=[("4548-4", 7.3, "%", "2024-12-20"), ("4548-4", 7.1, "%", "2025-06-30")],
        notes=[("2025-06-30", "Progress note", "Dr. M. Okafor",
                "Diabetes and hypertension follow-up. A1c 7.1%. Uses CPAP nightly. Continue metformin and "
                "amlodipine. Return in 6 months."),
               ("2026-08-20", "Outside records review", "Dr. M. Okafor",
                "Consult letter received from Dr. L. Moreno, Lakeside Endocrine Associates, who saw the patient on "
                "2026-08-05 for diabetes co-management at his request (he wanted a specialist opinion on whether to "
                "add a second agent). Letter reviewed and scanned to media.\n\nEndocrinology assessment: type 2 "
                "diabetes, well controlled on metformin monotherapy. Labs drawn at that visit on 2026-08-05: "
                "hemoglobin A1c 7.0%, eGFR 74, urine albumin/creatinine ratio 12 mg/g. No second agent recommended at "
                "this time. Endocrinology will see him again in one year; diabetes monitoring to continue here.\n\n"
                "Plan: no changes. Next A1c due in 6 months.")])

# ---- Task strep_allergy (breadth): positive today, documented non-anaphylactic amoxicillin rash.
patient("pt-1021", "Jennifer", "Lee", "1988-10-10", "female",
        conditions=[("GAD", "2020-02-02", "active")],
        meds=[("sertraline", 100, "mg", "once daily", "2020-02-02", "active")],
        allergies=[("Amoxicillin", "Itchy maculopapular rash on day 5 of a 10-day course in 2009; no hives, swelling "
                    "or breathing difficulty", "low", "medication", "2015-03-03")],
        obs=[("8310-5", 38.4, "Cel", "2026-10-01"), ("78012-2", "Positive", None, "2026-10-01")],
        notes=[("2026-01-14", "Progress note", "Dr. A. Shah", "Anxiety well controlled on sertraline. Continue."),
               ("2026-10-01", "Urgent visit", "Dr. A. Shah",
                "Walk-in visit for sore throat.\n\nHPI: 3 days of sore throat and fever to 101, painful swallowing. "
                "No cough or congestion. Two coworkers recently had strep.\n\nVitals: T 38.4 C, HR 92.\nExam: "
                "Tonsillar swelling with exudate, tender anterior cervical nodes.\n\nRapid strep antigen: "
                "POSITIVE.\n\nAssessment: Group A streptococcal pharyngitis.\nPlan: Antibiotic to be ordered. "
                "Supportive care, return if worsening.")])

# ---- Task apixaban_dose (breadth): NVAF on 2.5 mg, but only the creatinine criterion is met (age 79). Underdosed.
patient("pt-1022", "William", "Turner", "1947-03-03", "male",
        conditions=[("COPD", "2015-12-01", "active"), ("HTN", "2005-05-05", "active"),
                    ("CKD3B", "2023-01-10", "active"), ("AFIB", "2024-05-14", "active")],
        meds=[("albuterol HFA", 2, "puffs", "as needed", "2015-12-01", "active"),
              ("fluticasone HFA", 220, "mcg", "twice daily", "2015-12-01", "active"),
              ("losartan", 50, "mg", "once daily", "2005-05-05", "active"),
              ("metoprolol succinate ER", 25, "mg", "once daily", "2024-05-14", "active"),
              ("apixaban", 2.5, "mg", "twice daily", "2024-05-14", "active")],
        obs=[("4548-4", 5.5, "%", "2025-04-09"), ("1558-6", 98, "mg/dL", "2025-04-09"),
             ("2160-0", 1.52, "mg/dL", "2024-05-14"), ("29463-7", 83.0, "kg", "2024-05-14"),
             ("2160-0", 1.56, "mg/dL", "2026-06-10"), ("98979-8", 45, "mL/min/1.73m2", "2026-06-10"),
             ("29463-7", 81.6, "kg", "2026-06-10"),
             ("2160-0", 1.61, "mg/dL", "2026-09-12"), ("98979-8", 43, "mL/min/1.73m2", "2026-09-12")],
        notes=[("2024-05-14", "Progress note", "Dr. M. Okafor",
                "Palpitations and fatigue. ECG shows atrial fibrillation, rate 96. Echo: normal valves, EF 55%. "
                "CHA2DS2-VASc 3 (age 75 or older, hypertension). Start anticoagulation. Given his age of 77 and CKD "
                "stage 3b with creatinine 1.52, will use the lower apixaban dose of 2.5 mg twice daily to limit "
                "bleeding risk. Start metoprolol succinate ER 25 mg daily for rate control."),
               ("2025-04-09", "Annual physical", "Dr. M. Okafor",
                "Annual exam. COPD stable. Strong family history of diabetes (mother and brother), so screened today: "
                "A1c 5.5%, fasting glucose 98. No diabetes. Rescreen in 3 years."),
               ("2026-09-12", "Results note", "Dr. M. Okafor",
                "BMP reviewed: creatinine 1.61, eGFR 43. CKD 3b, stable. No bleeding on apixaban. Continue current "
                "medications.")])

# ---- Task strep_allergy (breadth): positive today; penicillin anaphylaxis only in a scanned outside record.
ELIZABETH_UC_NOTE = (
    "LAKESIDE URGENT CARE - VISIT RECORD (scanned outside record)\n\n"
    "Date of service: 2015-06-02\n\nChief complaint: Cut on left palm from a kitchen knife.\n\n"
    "HPI: 45 year old woman cut her left palm while slicing bread about an hour ago. Bleeding controlled with "
    "pressure. No numbness or weakness of the fingers. Last tetanus shot about 12 years ago.\n\n"
    "PMH: Migraine.\nMedications: Sumatriptan as needed.\n"
    "Allergies: Penicillin. Patient states that in 2011 she developed throat tightness, wheezing and hives within "
    "minutes of her first dose of penicillin VK for a tooth infection and was given epinephrine by paramedics.\n\n"
    "Exam: 2.5 cm linear laceration of the left thenar eminence, clean edges, full flexor and extensor function, "
    "sensation intact.\n\nProcedure: Irrigated, closed with 4 simple interrupted sutures.\n\n"
    "Plan: Tdap given. Wound care instructions. Suture removal in 10 days. No antibiotics indicated."
)

patient("pt-1023", "Elizabeth", "Martin", "1969-06-21", "female",
        conditions=[("MIGRAINE", "2001-01-01", "active"), ("MDD", "2017-09-09", "active")],
        meds=[("sumatriptan", 50, "mg", "as needed", "2001-01-01", "active"),
              ("sertraline", 50, "mg", "once daily", "2017-09-09", "active")],
        obs=[("8310-5", 38.7, "Cel", "2026-10-01"), ("78012-2", "Positive", None, "2026-10-01")],
        notes=[("2015-06-02", "Outside record (scanned)", "Lakeside Urgent Care", ELIZABETH_UC_NOTE),
               ("2017-09-09", "Progress note", "Dr. A. Shah",
                "Low mood, poor sleep and loss of interest for 3 months. PHQ-9 of 16. Moderate depression. Start "
                "sertraline 50 mg daily, counseling referral. Return in 4 weeks."),
               ("2026-02-02", "Progress note", "Dr. A. Shah", "Mood stable. Migraines about twice monthly, sumatriptan effective."),
               ("2026-10-01", "Urgent visit", "Dr. M. Okafor",
                "Walk-in visit for sore throat.\n\nHPI: 2 days of severe sore throat, fever and headache. No cough. "
                "\n\nVitals: T 38.7 C, HR 96.\nExam: Tonsillar exudate, tender anterior cervical "
                "lymphadenopathy.\n\nRapid strep antigen: POSITIVE.\n\nAssessment: Group A streptococcal "
                "pharyngitis.\nPlan: Antibiotic to be ordered. Supportive care.")])

patient("pt-1024", "Richard", "Clark", "1952-11-27", "male",
        conditions=[("T2DM_CKD", "2010-10-10", "active"), ("CKD3A", "2020-01-01", "active"), ("HTN", "2008-08-08", "active")],
        meds=[("insulin glargine", 18, "units", "at bedtime", "2020-01-01", "active"),
              ("losartan", 100, "mg", "once daily", "2008-08-08", "active"),
              ("atorvastatin", 40, "mg", "once daily", "2010-10-10", "active")],
        obs=[("4548-4", 7.9, "%", "2026-02-03"), ("4548-4", 7.6, "%", "2026-08-11")],
        notes=[("2026-08-11", "Progress note", "Dr. M. Okafor",
                "Diabetes with CKD 3a on basal insulin. A1c 7.6%. No hypoglycemia. Continue glargine 18 units.")])

patient("pt-1025", "Barbara", "Lewis", "1960-02-14", "female",
        conditions=[("T2DM", "2013-03-13", "active"), ("HTN", "2013-03-13", "active"), ("HLD", "2015-05-15", "active")],
        meds=[("metformin", 500, "mg", "twice daily", "2013-03-13", "active"),
              ("lisinopril", 10, "mg", "once daily", "2013-03-13", "active"),
              ("rosuvastatin", 10, "mg", "once daily", "2015-05-15", "active")],
        obs=[("4548-4", 7.0, "%", "2025-04-28"), ("4548-4", 6.9, "%", "2025-10-30")],
        notes=[("2025-10-30", "Progress note", "Dr. A. Shah",
                "Diabetes follow-up. A1c 6.9%. Doing well. Continue metformin. Return in 6 months."),
               # ---- Task med_rec_discharge (breadth): one dose change, a finished antibiotic course to leave off.
               ("2026-09-23", "Discharge summary (outside record)", "Dr. R. Feld, Valley General Hospital",
                "VALLEY GENERAL HOSPITAL - DISCHARGE SUMMARY\n\nAdmission 2026-09-20. Discharge 2026-09-23.\n"
                "Attending: Dr. R. Feld, Hospital Medicine\n\nPrincipal diagnosis: Cellulitis of the left lower "
                "leg.\nSecondary diagnoses: Acute kidney injury, hypertension, hyperlipidemia.\n\nHospital course: "
                "66 year old woman with 3 days of spreading redness and swelling of the left shin, fever 38.9. No "
                "abscess on ultrasound. Treated with IV cefazolin from 9/20, changed to oral cephalexin 500 mg four "
                "times daily on 9/22 to complete 10 days of total antibiotic therapy, with the last dose on 9/29. "
                "Admission creatinine 1.6 (baseline 0.9), improved to 1.1 with IV fluids. Lisinopril and her oral "
                "home medications were held on admission.\n\nDischarge medications: Lisinopril is restarted at a "
                "lower dose of 5 mg once daily (was 10 mg) given the kidney injury. Resume her other home medications "
                "at their usual doses. Cephalexin as above until the course is complete.\n\nFollow-up: PCP in "
                "1 to 2 weeks with BMP.")])

patient("pt-1026", "Joseph", "Walker", "1978-07-07", "male",
        conditions=[("HLD", "2022-02-22", "active")],
        meds=[("atorvastatin", 10, "mg", "once daily", "2022-02-22", "active")],
        obs=[("8310-5", 37.6, "Cel", "2026-10-01"), ("78012-2", "Negative", None, "2026-10-01")],
        notes=[("2026-06-06", "Annual physical", "Dr. M. Okafor", "Annual exam. Lipids at goal on atorvastatin 10 mg."),
               # ---- Task strep_allergy (breadth) decoy: tested today, negative.
               ("2026-10-01", "Urgent visit", "Dr. A. Shah",
                "Walk-in visit for sore throat.\n\nHPI: 2 days of scratchy throat, runny nose, mild cough and hoarse "
                "voice. Low-grade temperature at home. Daughter has a cold.\n\nVitals: T 37.6 C, HR 78.\nExam: "
                "Mild pharyngeal erythema, no exudate, no tender nodes. Clear rhinorrhea.\n\nRapid strep antigen: "
                "negative.\n\nAssessment: Viral pharyngitis.\nPlan: No antibiotics. Supportive care, salt water "
                "gargles, return if not improving in a week.")])

patient("pt-1027", "Sarah", "Hall", "1990-01-23", "female",
        conditions=[("PCOS", "2017-03-03", "active")],
        meds=[("metformin", 500, "mg", "twice daily", "2017-03-03", "active")],
        obs=[("4548-4", 5.6, "%", "2025-04-15")],
        notes=[("2025-04-15", "Progress note", "Dr. A. Shah",
                "PCOS follow-up. On metformin for insulin resistance and cycle regulation, cycles now regular. A1c "
                "5.6%, no diabetes. Continue metformin.")])

# ---- Task apixaban_dose (breadth): NVAF on 5 mg; age 82 and stable creatinine >= 1.5, so 2 of 3 criteria.
patient("pt-1028", "Charles", "Young", "1944-09-09", "male",
        conditions=[("T2DM", "2011-11-11", "active"), ("HTN", "2000-01-01", "active"),
                    ("AFIB", "2025-02-11", "active"), ("CKD3B", "2026-04-22", "active")],
        meds=[("metformin", 500, "mg", "twice daily", "2011-11-11", "active"),
              ("amlodipine", 5, "mg", "once daily", "2000-01-01", "active"),
              ("apixaban", 5, "mg", "twice daily", "2025-02-11", "active")],
        obs=[("4548-4", 7.0, "%", "2025-10-20"), ("4548-4", 7.3, "%", "2026-04-22"),
             ("2160-0", 1.31, "mg/dL", "2025-02-11"), ("29463-7", 72.4, "kg", "2025-02-11"),
             ("2160-0", 1.38, "mg/dL", "2025-10-20"),
             ("2160-0", 1.58, "mg/dL", "2026-04-22"), ("98979-8", 43, "mL/min/1.73m2", "2026-04-22"),
             ("29463-7", 70.3, "kg", "2026-04-22"),
             ("2160-0", 1.63, "mg/dL", "2026-09-15"), ("98979-8", 41, "mL/min/1.73m2", "2026-09-15")],
        notes=[("2025-02-11", "Progress note", "Dr. M. Okafor",
                "Irregular pulse noted at routine visit; ECG confirms atrial fibrillation, rate 82. Echo: no "
                "significant valve disease. CHA2DS2-VASc 4. Start apixaban 5 mg twice daily: age 80, weight 72.4 kg, "
                "creatinine 1.31, so only the age criterion is met."),
               ("2026-04-22", "Progress note", "Dr. M. Okafor", "A1c 7.3%, acceptable for age. Continue metformin."),
               ("2026-09-15", "Results note", "Dr. M. Okafor",
                "BMP reviewed: creatinine 1.63, eGFR 41, similar to April. CKD 3b, stable. Continue current "
                "medications.")])

# ---- Task apixaban_dose (breadth) decoy: apixaban for acute PE, not AF. Meets weight and creatinine "criteria",
# but the VTE treatment dose has no such reduction, and the prompt covers only NVAF.
patient("pt-1029", "Margaret", "Allen", "1956-03-31", "female",
        conditions=[("HTN", "2014-04-14", "active"), ("HLD", "2014-04-14", "active"),
                    ("CKD3B", "2022-06-01", "active"), ("PE", "2026-08-12", "active")],
        meds=[("lisinopril", 20, "mg", "once daily", "2014-04-14", "active"),
              ("atorvastatin", 40, "mg", "once daily", "2014-04-14", "active"),
              ("apixaban", 10, "mg", "twice daily", "2026-08-15", "stopped"),
              ("apixaban", 5, "mg", "twice daily", "2026-08-19", "active")],
        obs=[("2160-0", 1.52, "mg/dL", "2026-08-13"), ("29463-7", 56.9, "kg", "2026-08-13"),
             ("2160-0", 1.54, "mg/dL", "2026-09-10"), ("98979-8", 37, "mL/min/1.73m2", "2026-09-10"),
             ("29463-7", 56.2, "kg", "2026-09-10")],
        notes=[("2026-03-03", "Progress note", "Dr. A. Shah", "BP and lipids at goal. Continue."),
               ("2026-08-15", "Discharge summary (outside record)", "Dr. P. Lindqvist, Valley General Hospital",
                "Admission 2026-08-12 to 2026-08-15.\n\nDiagnosis: Acute right lower lobe segmental pulmonary "
                "embolism after a long car trip. No right heart strain. Lower extremity ultrasound negative. Sinus "
                "rhythm throughout on telemetry.\n\nAnticoagulation: Apixaban 10 mg twice daily through 8/18 "
                "(7 days from 8/12), then 5 mg twice daily. Plan at least 3 months of treatment, then reassess "
                "duration.\n\nFollow-up: PCP in 3 to 4 weeks."),
               ("2026-09-10", "Progress note", "Dr. A. Shah",
                "Pulmonary embolism follow-up. Dyspnea resolved. Taking apixaban 5 mg twice daily since 8/19, no "
                "bleeding. Wt 56.2 kg. Creatinine 1.54, eGFR 37, at her CKD 3b baseline. Continue anticoagulation "
                "and reassess duration at 3 months.")])

# ---- Task strep_allergy (breadth): positive today, no drug allergies.
patient("pt-1030", "Daniel", "King", "1982-05-16", "male",
        obs=[("85354-9", "118/76", "mm[Hg]", "2026-08-08"), ("8310-5", 38.9, "Cel", "2026-10-01"),
             ("78012-2", "Positive", None, "2026-10-01")],
        notes=[("2026-08-08", "Annual physical", "Dr. M. Okafor",
                "Healthy adult. No chronic conditions. No known drug allergies. Return in 1 year."),
               ("2026-10-01", "Urgent visit", "Dr. M. Okafor",
                "Walk-in visit for sore throat.\n\nHPI: Sudden sore throat and fever to 102 since yesterday, pain "
                "with swallowing, no cough. His son was diagnosed with strep 4 days ago.\n\nVitals: T 38.9 C, HR "
                "102.\nExam: Tonsillar exudate, tender anterior cervical nodes.\n\nRapid strep antigen: "
                "POSITIVE.\n\nAssessment: Group A streptococcal pharyngitis.\nPlan: Antibiotic to be ordered.")])


# ---------------------------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------------------------

def build():
    state = {
        "meta": {"today": TODAY, "practice": "Riverbend Family Medicine", "fixture_version": 1},
        "patients": [], "conditions": [], "medications": [], "allergies": [], "observations": [],
        "notes": [], "orders": [],
        "formulary": [{"id": rx_id(n), "name": n, "ingredient": i, "drug_class": c} for n, i, c in FORMULARY],
        "lab_catalog": LAB_CATALOG,
        "observation_codes": {code: {"display": d, "synonyms": s} for code, (d, s) in OBSERVATION_CODES.items()},
    }
    for spec in P:
        pid = spec["pid"]
        n4 = pid.split("-")[1]
        state["patients"].append({
            "id": pid, "mrn": f"RB{int(n4) * 7 + 300000}",
            "name": {"given": spec["given"], "family": spec["family"]},
            "birthDate": spec["birth"], "gender": spec["gender"],
            "active": spec["active"], "deceasedDate": spec["deceased"],
        })
        for i, (key, onset, status) in enumerate(spec["conditions"], 1):
            system, code, display = ICD[key]
            state["conditions"].append({"id": f"cond-{n4}-{i}", "patient_id": pid,
                                        "code": {"system": system, "code": code, "display": display},
                                        "clinicalStatus": status, "onsetDate": onset})
        for i, (name, dose, unit, freq, authored, status) in enumerate(spec["meds"], 1):
            state["medications"].append({"id": f"med-{n4}-{i:02d}", "patient_id": pid,
                                         "formulary_id": FORMULARY_BY_NAME[name], "name": name,
                                         "dose_value": dose, "dose_unit": unit, "frequency": freq,
                                         "status": status, "authoredOn": authored, "duration_days": None,
                                         "indication": None, "source": "chart", "history": []})
        for i, (substance, reaction, crit, cat, recorded) in enumerate(spec["allergies"], 1):
            state["allergies"].append({"id": f"alg-{n4}-{i}", "patient_id": pid, "substance": substance,
                                       "reaction": reaction, "criticality": crit, "category": cat,
                                       "recordedDate": recorded})
        for i, (code, value, unit, date) in enumerate(spec["obs"], 1):
            state["observations"].append({"id": f"obs-{n4}-{i:03d}", "patient_id": pid,
                                          "code": {"system": "LOINC", "code": code,
                                                   "display": OBSERVATION_CODES[code][0]},
                                          "value": value, "unit": unit, "effectiveDate": date})
        for i, (date, ntype, author, text) in enumerate(spec["notes"], 1):
            state["notes"].append({"id": f"note-{n4}-{i}", "patient_id": pid, "date": date, "type": ntype,
                                   "author": author, "text": text})
        for i, (code, display, status, date, reason) in enumerate(spec["orders"], 1):
            state["orders"].append({"id": f"ord-{n4}-{i}", "patient_id": pid, "order_type": "lab", "code": code,
                                    "display": display, "status": status, "orderedDate": date, "reason": reason,
                                    "source": "chart"})
    return state


if __name__ == "__main__":
    OUT.write_text(json.dumps(build(), indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT} ({len(P)} patients)")
