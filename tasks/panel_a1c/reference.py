from tasks import Control

EXPECTED = ["pt-1001", "pt-1006", "pt-1010", "pt-1014", "pt-1016", "pt-1020", "pt-1025"]


def order(pid, test="Hemoglobin A1c"):
    return ("place_lab_order", {"patient_id": pid, "test": test, "reason": "Diabetes care gap: A1c overdue"})


def submit(pids):
    return ("submit", {"summary": "Ordered A1c for overdue type 2 diabetics.", "patient_ids": list(pids)})


REFERENCE = [
    ("list_patients", {"page": 1}),
    ("list_patients", {"page": 2}),
    ("list_patients", {"page": 3}),
    ("list_conditions", {"patient_id": "pt-1006"}),
    ("search_notes", {"query": "diabetes"}),
    ("read_note", {"note_id": "note-1014-1"}),
    ("get_observations", {"patient_id": "pt-1015", "query": "A1c"}),
    ("list_orders", {"patient_id": "pt-1013", "status": "active"}),
    *[order(p) for p in EXPECTED],
    submit(EXPECTED),
]

# Only structured E11.x or SNOMED type 2 codes, last A1c older than 6 months or missing. Ignores pending orders,
# death, and the note-only diagnosis.
STRUCTURED_ONLY = ["pt-1001", "pt-1006", "pt-1007", "pt-1010", "pt-1013", "pt-1016", "pt-1020", "pt-1025"]

CONTROLS = [
    Control("do_nothing", [submit([])], expect_failed={"ordered_set_matches_expected"}),
    Control("structured_codes_only", [*[order(p) for p in STRUCTURED_ONLY], submit(STRUCTURED_ONLY)],
            expect_failed={"ordered_set_matches_expected", "no_order_for_deceased_patient"},
            description="Misses the note-only diagnosis, orders for the deceased patient and the one already pending."),
    Control("missed_note_only_diagnosis", [*[order(p) for p in EXPECTED if p != "pt-1014"],
                                           submit([p for p in EXPECTED if p != "pt-1014"])],
            expect_failed={"ordered_set_matches_expected"}),
    Control("metformin_means_diabetes", [*[order(p) for p in EXPECTED + ["pt-1027"]], submit(EXPECTED + ["pt-1027"])],
            expect_failed={"ordered_set_matches_expected"},
            description="Includes the PCOS patient on metformin."),
    Control("duplicate_order", [*[order(p) for p in EXPECTED], order("pt-1001"), submit(EXPECTED)],
            expect_failed={"no_duplicate_a1c_orders"}),
    Control("alt_correct_synonyms_and_order",
            [order("pt-1025", "4548-4"), order("pt-1001", "HbA1c"), order("pt-1014", "glycated hemoglobin"),
             order("pt-1006", "a1c"), order("pt-1020"), order("pt-1010"), order("pt-1016"),
             ("submit", {"summary": "done"})],
            expect_pass=True, description="Same set via different test names, different order, no id list."),
]
