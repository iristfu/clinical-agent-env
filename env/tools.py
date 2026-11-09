"""The agent's only interface to the EHR.

Two kinds of failure are kept strictly apart:
  * ToolError  -> the model sent something invalid. The message goes back to the model (is_error=True)
                  and the trial continues. This is the model's problem to recover from.
  * any other exception -> a bug in this environment. The harness stops the trial and marks it
                  invalid (env_error), so it can never be counted as a model failure.
"""

import re

PREVIEW_CHARS = 200

FREQUENCIES = ["once daily", "twice daily", "three times daily", "four times daily", "every 8 hours",
               "every 12 hours", "every 24 hours", "at bedtime", "once weekly", "as needed", "once"]
DOSE_UNITS = ["mg", "mcg", "g", "units", "mL", "puffs"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ToolError(Exception):
    """Invalid request from the model. Returned to it as an error result."""


# =============================================================================================
# Tool definitions (Anthropic tool-use format)
# =============================================================================================

def _tool(name, description, properties, required=()):
    return {"name": name, "description": description,
            "input_schema": {"type": "object", "properties": properties, "required": list(required)}}


PID = {"type": "string", "description": "Patient id, e.g. pt-1001."}
PAGE = {"type": "integer", "description": "1-based page number. Defaults to 1."}

TOOLS = [
    _tool("list_patients",
          "List every patient on the practice panel with basic demographics, active status and date of death if "
          "deceased. Results are paginated.",
          {"page": PAGE, "page_size": {"type": "integer", "description": "Results per page, 1 to 25. Defaults to 10."}}),
    _tool("search_patients",
          "Find patients by name and/or date of birth. Name matching is case-insensitive and every word you give "
          "must appear in the patient's name.",
          {"name": {"type": "string"}, "birth_date": {"type": "string", "description": "YYYY-MM-DD"}}),
    _tool("get_patient", "Get demographics for one patient.", {"patient_id": PID}, ["patient_id"]),
    _tool("list_conditions",
          "List a patient's coded problem list entries (ICD-10-CM or SNOMED CT). Resolved entries are hidden unless "
          "include_resolved is true.",
          {"patient_id": PID, "include_resolved": {"type": "boolean", "description": "Defaults to false."}},
          ["patient_id"]),
    _tool("list_medications",
          "List a patient's medications from the outpatient medication list.",
          {"patient_id": PID,
           "status": {"type": "string", "enum": ["active", "stopped", "all"], "description": "Defaults to active."}},
          ["patient_id"]),
    _tool("list_allergies", "List a patient's documented allergies and intolerances.", {"patient_id": PID},
          ["patient_id"]),
    _tool("get_observations",
          "Get a patient's labs and vital signs, newest first. Filter with query (a LOINC code, test name or common "
          "abbreviation such as 'A1c' or 'weight') and/or since (YYYY-MM-DD). Results are paginated, 20 per page.",
          {"patient_id": PID, "query": {"type": "string"}, "since": {"type": "string", "description": "YYYY-MM-DD"},
           "page": PAGE},
          ["patient_id"]),
    _tool("search_notes",
          "Search clinical notes, newest first. Give a patient_id, a query, or both. Every word in the query must "
          "appear in the note (case-insensitive; singular and plural forms match). Results show a short preview "
          "only; use read_note for full text. "
          "Paginated, 10 per page.",
          {"patient_id": PID, "query": {"type": "string"}, "page": PAGE}),
    _tool("read_note", "Read the full text of one clinical note.", {"note_id": {"type": "string"}}, ["note_id"]),
    _tool("list_orders",
          "List a patient's lab and diagnostic orders. Medication orders are on the medication list instead.",
          {"patient_id": PID,
           "status": {"type": "string", "enum": ["active", "completed", "all"],
                      "description": "active means ordered and not yet resulted. Defaults to all."}},
          ["patient_id"]),
    _tool("search_formulary",
          "Search the medication formulary by drug name, ingredient or class. Medication orders must use a "
          "formulary item.",
          {"query": {"type": "string"}}, ["query"]),
    _tool("place_medication_order",
          "Prescribe a medication. It is added to the patient's active medication list.",
          {"patient_id": PID,
           "medication": {"type": "string", "description": "Formulary item name or id."},
           "dose_value": {"type": "number", "description": "Amount per dose, e.g. 500."},
           "dose_unit": {"type": "string", "enum": DOSE_UNITS},
           "frequency": {"type": "string", "enum": FREQUENCIES},
           "duration_days": {"type": "integer", "description": "For time-limited courses. Omit for ongoing therapy."},
           "indication": {"type": "string"}},
          ["patient_id", "medication", "dose_value", "dose_unit", "frequency"]),
    _tool("update_medication",
          "Change the dose or frequency of an active medication on the list.",
          {"medication_id": {"type": "string"}, "dose_value": {"type": "number"},
           "dose_unit": {"type": "string", "enum": DOSE_UNITS}, "frequency": {"type": "string", "enum": FREQUENCIES},
           "reason": {"type": "string"}},
          ["medication_id", "reason"]),
    _tool("discontinue_medication",
          "Discontinue an active medication. It stays on the list with status stopped.",
          {"medication_id": {"type": "string"}, "reason": {"type": "string"}},
          ["medication_id", "reason"]),
    _tool("place_lab_order", "Order a lab test from the lab catalog.",
          {"patient_id": PID, "test": {"type": "string", "description": "Test name, abbreviation or LOINC code."},
           "reason": {"type": "string"}},
          ["patient_id", "test"]),
    _tool("add_allergy", "Add an allergy or intolerance to a patient's allergy list.",
          {"patient_id": PID, "substance": {"type": "string"}, "reaction": {"type": "string"},
           "criticality": {"type": "string", "enum": ["low", "high", "unable-to-assess"]},
           "category": {"type": "string", "enum": ["medication", "food", "environment", "biologic"]}},
          ["patient_id", "substance", "reaction", "criticality", "category"]),
    _tool("submit",
          "Finish the task. Call exactly once, after all chart changes are made. Nothing can be changed afterward.",
          {"summary": {"type": "string", "description": "Brief summary of what you did and why."},
           "patient_ids": {"type": "array", "items": {"type": "string"},
                           "description": "Patients you acted on, if the task asks for them."}},
          ["summary"]),
]

TOOLS_BY_NAME = {t["name"]: t for t in TOOLS}

# =============================================================================================
# Argument validation
# =============================================================================================


def _coerce(key, value, spec):
    t = spec.get("type")
    if value is None:
        return None
    if t == "string":
        if not isinstance(value, str):
            raise ToolError(f"Parameter '{key}' must be a string.")
        value = value.strip()
    elif t in ("number", "integer"):
        if isinstance(value, str) and re.fullmatch(r"-?\d+(\.\d+)?", value.strip()):
            value = float(value) if "." in value else int(value)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ToolError(f"Parameter '{key}' must be a {t}.")
        if t == "integer":
            if float(value) != int(value):
                raise ToolError(f"Parameter '{key}' must be a whole number.")
            value = int(value)
    elif t == "boolean":
        if isinstance(value, str) and value.lower() in ("true", "false"):
            value = value.lower() == "true"
        if not isinstance(value, bool):
            raise ToolError(f"Parameter '{key}' must be true or false.")
    elif t == "array":
        if not isinstance(value, list):
            raise ToolError(f"Parameter '{key}' must be an array.")
    if "enum" in spec and value not in spec["enum"]:
        raise ToolError(f"Invalid value for '{key}': {value!r}. Allowed values: {spec['enum']}.")
    return value


def validate_args(name, args):
    schema = TOOLS_BY_NAME[name]["input_schema"]
    props = schema["properties"]
    if not isinstance(args, dict):
        raise ToolError("Tool arguments must be a JSON object.")
    unknown = sorted(set(args) - set(props))
    if unknown:
        raise ToolError(f"Unknown parameter(s) for {name}: {unknown}. Valid parameters: {sorted(props)}.")
    clean = {k: _coerce(k, v, props[k]) for k, v in args.items()}
    missing = [r for r in schema["required"] if clean.get(r) in (None, "")]
    if missing:
        raise ToolError(f"Missing required parameter(s) for {name}: {missing}.")
    return clean


# =============================================================================================
# Helpers
# =============================================================================================


def _patient_or_error(ehr, pid):
    p = ehr.patient(pid)
    if p is None:
        raise ToolError(f"No patient with id {pid!r}. Use search_patients or list_patients to find patient ids.")
    return p


def _date_or_error(key, value):
    if value is not None and not DATE_RE.match(value):
        raise ToolError(f"Parameter '{key}' must be a date in YYYY-MM-DD format.")
    return value


def _paginate(items, page, page_size):
    page = page or 1
    if page < 1:
        raise ToolError("page must be 1 or greater.")
    total = len(items)
    start = (page - 1) * page_size
    chunk = items[start:start + page_size]
    out = {"results": chunk, "page": page, "total": total, "has_more": start + page_size < total}
    if total == 0:
        out["note"] = "No results."
    elif not chunk:
        out["note"] = f"Page {page} is past the end. There are {total} results."
    else:
        out["note"] = f"Showing {start + 1}-{start + len(chunk)} of {total}."
        if out["has_more"]:
            out["note"] += f" Pass page={page + 1} for more."
    return out


def _patient_summary(p):
    return {"patient_id": p["id"], "name": f"{p['name']['given']} {p['name']['family']}",
            "birth_date": p["birthDate"], "gender": p["gender"], "active": p["active"],
            "deceased_date": p["deceasedDate"]}


def _med_view(m):
    view = {k: m[k] for k in ("id", "name", "dose_value", "dose_unit", "frequency", "status", "authoredOn",
                              "duration_days", "indication")}
    if m["status"] == "stopped":
        view["stoppedDate"] = m.get("stoppedDate")
        view["stopReason"] = m.get("stopReason")
    return view


def _resolve_formulary(ehr, query):
    q = query.strip().lower()
    items = ehr.state["formulary"]
    exact = [d for d in items if q in (d["id"].lower(), d["name"].lower())]
    if exact:
        return exact[0]
    by_ingredient = [d for d in items if d["ingredient"].lower() == q]
    if len(by_ingredient) == 1:
        return by_ingredient[0]
    # "azithromycin 500 mg tablets" -> the longest formulary name the text starts with
    prefixed = sorted([d for d in items if q.startswith(d["name"].lower() + " ")], key=lambda d: -len(d["name"]))
    if prefixed:
        return prefixed[0]
    partial = [d for d in items if q in d["name"].lower() or q in d["ingredient"].lower()]
    if len(partial) == 1:
        return partial[0]
    candidates = by_ingredient or partial
    if candidates:
        names = [d["name"] for d in candidates]
        raise ToolError(f"{query!r} matches more than one formulary item: {names}. Give the exact item name.")
    raise ToolError(f"{query!r} is not on the formulary. Use search_formulary to find available medications.")


def _resolve_lab(ehr, query):
    q = query.strip().lower()
    catalog = ehr.state["lab_catalog"]
    for t in catalog:
        if q in (t["code"].lower(), t["display"].lower()) or q in (s.lower() for s in t["synonyms"]):
            return t
    partial = [t for t in catalog if q in t["display"].lower()]
    if len(partial) == 1:
        return partial[0]
    names = [t["display"] for t in (partial or catalog)]
    raise ToolError(f"{query!r} did not match a single lab test. Available tests: {names}.")


def _obs_matches(ehr, obs, query):
    if not query:
        return True
    q = query.strip().lower()
    code = obs["code"]["code"]
    entry = ehr.state["observation_codes"].get(code, {"display": obs["code"]["display"], "synonyms": []})
    return (q == code.lower() or q in entry["display"].lower()
            or any(q in s.lower() for s in entry["synonyms"]))


def _word_in(word, haystack):
    """Substring match that also treats -y and -ies as the same word, so "allergy" finds "Allergies:" and
    "therapies" finds "therapy". Plain -s plurals already match by substring. Added after pilot 4, where a search
    for "allergy" returned "No results" on a chart whose notes have allergy sections."""
    if word in haystack:
        return True
    if word.endswith("y") and word[:-1] + "ies" in haystack:
        return True
    return word.endswith("ies") and word[:-3] + "y" in haystack


def _active_med_or_error(ehr, med_id):
    med = ehr.find("medications", med_id)
    if med is None:
        raise ToolError(f"No medication with id {med_id!r}. Use list_medications to see medication ids.")
    if med["status"] != "active":
        raise ToolError(f"Medication {med_id} is not active (status: {med['status']}).")
    return med


# =============================================================================================
# Handlers
# =============================================================================================


def list_patients(ehr, page=None, page_size=None):
    page_size = page_size or 10
    if not 1 <= page_size <= 25:
        raise ToolError("page_size must be between 1 and 25.")
    return _paginate([_patient_summary(p) for p in ehr.state["patients"]], page, page_size)


def search_patients(ehr, name=None, birth_date=None):
    if not name and not birth_date:
        raise ToolError("Give a name, a birth_date, or both.")
    _date_or_error("birth_date", birth_date)
    words = (name or "").lower().split()
    hits = []
    for p in ehr.state["patients"]:
        full = f"{p['name']['given']} {p['name']['family']}".lower()
        if all(w in full for w in words) and (birth_date is None or p["birthDate"] == birth_date):
            hits.append(_patient_summary(p))
    return {"results": hits, "total": len(hits)}


def get_patient(ehr, patient_id):
    p = _patient_or_error(ehr, patient_id)
    return {**_patient_summary(p), "mrn": p["mrn"]}


def list_conditions(ehr, patient_id, include_resolved=False):
    _patient_or_error(ehr, patient_id)
    rows = [c for c in ehr.records("conditions", patient_id) if include_resolved or c["clinicalStatus"] == "active"]
    return {"results": [{"id": c["id"], "system": c["code"]["system"], "code": c["code"]["code"],
                         "display": c["code"]["display"], "clinical_status": c["clinicalStatus"],
                         "onset_date": c["onsetDate"]} for c in rows], "total": len(rows)}


def list_medications(ehr, patient_id, status=None):
    _patient_or_error(ehr, patient_id)
    status = status or "active"
    rows = [m for m in ehr.records("medications", patient_id) if status == "all" or m["status"] == status]
    return {"results": [_med_view(m) for m in rows], "total": len(rows)}


def list_allergies(ehr, patient_id):
    _patient_or_error(ehr, patient_id)
    rows = ehr.records("allergies", patient_id)
    out = [{k: a[k] for k in ("id", "substance", "reaction", "criticality", "category", "recordedDate")} for a in rows]
    return {"results": out, "total": len(out)}


def get_observations(ehr, patient_id, query=None, since=None, page=None):
    _patient_or_error(ehr, patient_id)
    _date_or_error("since", since)
    rows = [o for o in ehr.records("observations", patient_id)
            if _obs_matches(ehr, o, query) and (since is None or o["effectiveDate"] >= since)]
    rows.sort(key=lambda o: (o["effectiveDate"], o["id"]), reverse=True)
    view = [{"id": o["id"], "code": o["code"]["code"], "display": o["code"]["display"], "value": o["value"],
             "unit": o["unit"], "date": o["effectiveDate"]} for o in rows]
    return _paginate(view, page, 20)


def search_notes(ehr, patient_id=None, query=None, page=None):
    if not patient_id and not query:
        raise ToolError("Give a patient_id, a query, or both.")
    if patient_id:
        _patient_or_error(ehr, patient_id)
    words = (query or "").lower().split()
    rows = []
    for n in ehr.records("notes", patient_id):
        haystack = f"{n['type']} {n['author']} {n['text']}".lower()
        if all(_word_in(w, haystack) for w in words):
            rows.append(n)
    rows.sort(key=lambda n: (n["date"], n["id"]), reverse=True)
    view = []
    for n in rows:
        text = n["text"]
        preview = text if len(text) <= PREVIEW_CHARS else (
            text[:PREVIEW_CHARS] + f"... [preview truncated, {len(text)} characters total, use read_note for full text]")
        view.append({"note_id": n["id"], "patient_id": n["patient_id"], "date": n["date"], "type": n["type"],
                     "author": n["author"], "preview": preview})
    return _paginate(view, page, 10)


def read_note(ehr, note_id):
    n = ehr.find("notes", note_id)
    if n is None:
        raise ToolError(f"No note with id {note_id!r}. Use search_notes to find note ids.")
    return {"note_id": n["id"], "patient_id": n["patient_id"], "date": n["date"], "type": n["type"],
            "author": n["author"], "text": n["text"]}


def list_orders(ehr, patient_id, status=None):
    _patient_or_error(ehr, patient_id)
    status = status or "all"
    rows = [o for o in ehr.records("orders", patient_id) if status == "all" or o["status"] == status]
    out = [{k: o[k] for k in ("id", "code", "display", "status", "orderedDate", "reason")} for o in rows]
    return {"results": out, "total": len(out)}


def search_formulary(ehr, query):
    q = query.lower()
    hits = [d for d in ehr.state["formulary"]
            if q in d["name"].lower() or q in d["ingredient"].lower() or q in d["drug_class"].lower()]
    return {"results": hits[:15], "total": len(hits),
            "note": "Showing first 15 matches. Narrow the query." if len(hits) > 15 else None}


def place_medication_order(ehr, patient_id, medication, dose_value, dose_unit, frequency, duration_days=None,
                           indication=None):
    _patient_or_error(ehr, patient_id)
    item = _resolve_formulary(ehr, medication)
    if dose_value <= 0:
        raise ToolError("dose_value must be greater than 0.")
    if duration_days is not None and duration_days <= 0:
        raise ToolError("duration_days must be greater than 0.")
    med = {"id": ehr.new_id("med"), "patient_id": patient_id, "formulary_id": item["id"], "name": item["name"],
           "dose_value": dose_value, "dose_unit": dose_unit, "frequency": frequency, "status": "active",
           "authoredOn": ehr.today, "duration_days": duration_days, "indication": indication, "source": "agent",
           "history": []}
    ehr.state["medications"].append(med)
    ehr.log_write("place_medication_order", med["id"], patient_id)
    return {"created": _med_view(med)}


def update_medication(ehr, medication_id, reason, dose_value=None, dose_unit=None, frequency=None):
    med = _active_med_or_error(ehr, medication_id)
    changes = {k: v for k, v in (("dose_value", dose_value), ("dose_unit", dose_unit), ("frequency", frequency))
               if v is not None}
    if not changes:
        raise ToolError("Give at least one of dose_value, dose_unit or frequency to change.")
    if dose_value is not None and dose_value <= 0:
        raise ToolError("dose_value must be greater than 0.")
    if all(med[k] == v for k, v in changes.items()):
        raise ToolError("The medication already has those values. Nothing changed.")
    med["history"].append({"changed_on": ehr.today, "reason": reason,
                           "previous": {k: med[k] for k in ("dose_value", "dose_unit", "frequency")}})
    med.update(changes)
    ehr.log_write("update_medication", med["id"], med["patient_id"])
    return {"updated": _med_view(med)}


def discontinue_medication(ehr, medication_id, reason):
    med = _active_med_or_error(ehr, medication_id)
    med["status"] = "stopped"
    med["stoppedDate"] = ehr.today
    med["stopReason"] = reason
    ehr.log_write("discontinue_medication", med["id"], med["patient_id"])
    return {"discontinued": _med_view(med)}


def place_lab_order(ehr, patient_id, test, reason=None):
    _patient_or_error(ehr, patient_id)
    t = _resolve_lab(ehr, test)
    order = {"id": ehr.new_id("ord"), "patient_id": patient_id, "order_type": "lab", "code": t["code"],
             "display": t["display"], "status": "active", "orderedDate": ehr.today, "reason": reason,
             "source": "agent"}
    ehr.state["orders"].append(order)
    ehr.log_write("place_lab_order", order["id"], patient_id)
    return {"created": {k: order[k] for k in ("id", "patient_id", "code", "display", "status", "orderedDate")}}


def add_allergy(ehr, patient_id, substance, reaction, criticality, category):
    _patient_or_error(ehr, patient_id)
    allergy = {"id": ehr.new_id("alg"), "patient_id": patient_id, "substance": substance, "reaction": reaction,
               "criticality": criticality, "category": category, "recordedDate": ehr.today}
    ehr.state["allergies"].append(allergy)
    ehr.log_write("add_allergy", allergy["id"], patient_id)
    return {"created": {k: allergy[k] for k in ("id", "substance", "reaction", "criticality", "category")}}


def submit(ehr, summary, patient_ids=None):
    if ehr.submission is not None:
        raise ToolError("The task was already submitted.")
    if patient_ids is not None and not all(isinstance(p, str) for p in patient_ids):
        raise ToolError("patient_ids must be a list of patient id strings.")
    ehr.submission = {"summary": summary, "patient_ids": patient_ids}
    return {"status": "submitted", "message": "Submission recorded. The task is complete."}


HANDLERS = {
    "list_patients": list_patients, "search_patients": search_patients, "get_patient": get_patient,
    "list_conditions": list_conditions, "list_medications": list_medications, "list_allergies": list_allergies,
    "get_observations": get_observations, "search_notes": search_notes, "read_note": read_note,
    "list_orders": list_orders, "search_formulary": search_formulary,
    "place_medication_order": place_medication_order, "update_medication": update_medication,
    "discontinue_medication": discontinue_medication, "place_lab_order": place_lab_order,
    "add_allergy": add_allergy, "submit": submit,
}
assert set(HANDLERS) == set(TOOLS_BY_NAME), "every tool needs a handler and vice versa"


def call_tool(ehr, name, args):
    """Run one tool call. Raises ToolError for invalid requests; any other exception is an environment bug."""
    if name not in HANDLERS:
        raise ToolError(f"Unknown tool {name!r}. Available tools: {sorted(HANDLERS)}.")
    clean = validate_args(name, args or {})
    return HANDLERS[name](ehr, **clean)
