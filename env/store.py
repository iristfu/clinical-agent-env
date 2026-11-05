"""In-memory EHR state. Every trial gets a fresh deep copy of the fixture, so trials cannot leak into each other."""

import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path

DEFAULT_FIXTURE = Path(__file__).parent / "fixtures" / "panel.json"


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def hash_state(state) -> str:
    return hashlib.sha256(_canonical(state)).hexdigest()[:16]


class EHR:
    """Holds clinical state. Tools in env/tools.py are the only way an agent touches it."""

    def __init__(self, fixture_path: Path = DEFAULT_FIXTURE):
        self.fixture_path = Path(fixture_path)
        self._fixture = json.loads(self.fixture_path.read_text())
        self.reset()

    def reset(self):
        self.state = copy.deepcopy(self._fixture)
        self._counters = defaultdict(int)
        self.write_log = []      # every successful write, in order
        self.submission = None   # args of the submit tool, if called

    # ---- identity and snapshots -------------------------------------------------------------

    @property
    def today(self) -> str:
        return self.state["meta"]["today"]

    def state_hash(self) -> str:
        return hash_state(self.state)

    def snapshot(self):
        return copy.deepcopy(self.state)

    def new_id(self, prefix: str) -> str:
        # Deterministic: the n-th record of a kind created in a trial always gets the same id.
        self._counters[prefix] += 1
        return f"{prefix}-new-{self._counters[prefix]:03d}"

    def log_write(self, tool: str, record_id: str, patient_id: str):
        self.write_log.append({"tool": tool, "record_id": record_id, "patient_id": patient_id})

    # ---- lookups ----------------------------------------------------------------------------

    def patient(self, pid):
        return next((p for p in self.state["patients"] if p["id"] == pid), None)

    def records(self, collection, pid=None):
        rows = self.state[collection]
        return [r for r in rows if pid is None or r["patient_id"] == pid]

    def find(self, collection, record_id):
        return next((r for r in self.state[collection] if r["id"] == record_id), None)
