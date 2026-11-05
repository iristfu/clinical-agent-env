"""End-to-end tests of the model loop with a fake Anthropic client, so the harness is verified without the API."""

import anthropic
import pytest
from anthropic.types import Message, TextBlock, ToolUseBlock, Usage

import env.tools as tools_mod
from harness.agent_loop import ConfigError, run_model_trial
from harness.run import run_task
from tasks import load_task


def _msg(blocks, stop="tool_use"):
    return Message(id="msg", content=blocks, model="fake", role="assistant", stop_reason=stop, stop_sequence=None,
                   type="message", usage=Usage(input_tokens=100, output_tokens=20, cache_read_input_tokens=80,
                                               cache_creation_input_tokens=10))


class ReplayClient:
    """Plays back a scripted list of tool calls as if a model had produced them, one per turn."""

    def __init__(self, calls, parallel=False, final_text=None):
        self.calls, self.parallel, self.final_text, self.requests = list(calls), parallel, final_text, []
        self.messages = self

    def create(self, **request):
        self.requests.append(request)
        if not self.calls:
            return _msg([TextBlock(type="text", text=self.final_text or "done")], stop="end_turn")
        batch = self.calls if self.parallel else self.calls[:1]
        self.calls = [] if self.parallel else self.calls[1:]
        return _msg([ToolUseBlock(id=f"tu_{len(self.requests)}_{i}", name=n, input=a, type="tool_use")
                     for i, (n, a) in enumerate(batch)])


def _api_error(cls, msg="simulated"):
    """Build an SDK exception without depending on which HTTP library this SDK version uses."""
    e = cls.__new__(cls)
    Exception.__init__(e, msg)
    e.message = msg
    return e


def _count_breakpoints(request):
    n = sum("cache_control" in b for b in request["system"]) + sum("cache_control" in t for t in request["tools"])
    for m in request["messages"]:
        if isinstance(m["content"], list):
            n += sum(isinstance(b, dict) and "cache_control" in b for b in m["content"])
    return n


@pytest.mark.parametrize("task_id", ["strep_allergy", "apixaban_dose", "panel_a1c", "med_rec_discharge"])
def test_replayed_reference_passes_through_model_loop(task_id, tmp_path):
    task = load_task(task_id)
    client = ReplayClient(task.reference)
    r = run_model_trial(task, "fake-model", client, traj_path=tmp_path / "t.jsonl")
    assert r["passed"] and r["stop_reason"] == "submitted" and r["valid"]
    assert r["turns"] == len(task.reference)
    assert all(_count_breakpoints(req) <= 4 for req in client.requests)
    assert client.requests[0]["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert "temperature" not in client.requests[0]
    assert (tmp_path / "t.jsonl").read_text().count('"type": "tool_call"') == len(task.reference)


def test_parallel_tool_calls_and_calls_after_submit_are_skipped():
    task = load_task("apixaban_dose")
    calls = task.reference + [("discontinue_medication", {"medication_id": "med-1008-02", "reason": "after submit"})]
    r = run_model_trial(task, "fake", ReplayClient(calls, parallel=True))
    assert r["passed"] and r["turns"] == 1 and r["tool_status"]["skipped_after_submit"] == 1


def test_ending_without_submit_still_grades_state():
    task = load_task("strep_allergy")
    r = run_model_trial(task, "fake", ReplayClient(task.reference[:-1]))
    assert r["stop_reason"] == "end_turn" and r["passed"]
    assert "called_submit" in r["failed_diagnostic"]


def test_turn_limit_is_a_model_failure_not_invalid():
    task = load_task("strep_allergy")
    calls = [("list_patients", {})] * (task.max_turns + 5)
    r = run_model_trial(task, "fake", ReplayClient(calls))
    assert r["stop_reason"] == "turn_limit" and r["valid"] and not r["passed"]


def test_environment_exception_marks_trial_invalid(monkeypatch):
    def broken(ehr, **kw):
        raise KeyError("bug")
    monkeypatch.setitem(tools_mod.HANDLERS, "list_allergies", broken)
    task = load_task("strep_allergy")
    r = run_model_trial(task, "fake", ReplayClient(task.reference))
    assert r["stop_reason"] == "env_error" and not r["valid"] and r["passed"] is None


class FlakyClient(ReplayClient):
    def __init__(self, calls, failures):
        super().__init__(calls)
        self.failures = failures

    def create(self, **request):
        if self.failures:
            self.failures -= 1
            raise _api_error(anthropic.APIConnectionError)
        return super().create(**request)


def test_infra_errors_are_retried_and_never_counted_as_model_failures():
    task = load_task("strep_allergy")
    flaky = FlakyClient(task.reference, failures=1)
    results = run_task("strep_allergy", "fake", client=flaky, trials=1, concurrency=1, verbose=False)
    assert results[0]["passed"] and results[0]["attempt"] == 2

    always_down = FlakyClient(task.reference, failures=99)
    results = run_task("strep_allergy", "fake", client=always_down, trials=1, concurrency=1, verbose=False)
    assert results[0]["stop_reason"] == "infra_error" and not results[0]["valid"] and results[0]["attempt"] == 3


def test_bad_request_stops_the_run():
    class BadClient(ReplayClient):
        def create(self, **request):
            raise _api_error(anthropic.BadRequestError, "bad param")
    with pytest.raises(ConfigError):
        run_model_trial(load_task("strep_allergy"), "fake", BadClient([]))
