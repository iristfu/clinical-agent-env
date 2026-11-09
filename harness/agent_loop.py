"""Model policy: a plain Messages API tool-use loop over the EHR tools."""

import time

import anthropic

from env.store import EHR
from harness.trial import TrajectoryLog, execute, finish_trial, system_prompt, tools_for_api

# Errors that mean our request or credentials are wrong. Retrying won't help, so the whole run stops.
CONFIG_ERRORS = (anthropic.BadRequestError, anthropic.AuthenticationError, anthropic.PermissionDeniedError,
                 anthropic.NotFoundError)


class ConfigError(RuntimeError):
    pass


def _with_cache_breakpoint(message):
    """Copy of the latest user message with a cache breakpoint on its last block, so each turn reuses the
    cached prefix. Only the newest message carries one, which keeps us under the 4-breakpoint limit."""
    content = message["content"]
    blocks = [{"type": "text", "text": content}] if isinstance(content, str) else [dict(b) for b in content]
    blocks[-1] = {**blocks[-1], "cache_control": {"type": "ephemeral"}}
    return {"role": message["role"], "content": blocks}


def run_model_trial(task, model, client, *, trial=0, attempt=1, traj_path=None, run_id=None, effort=None,
                    max_tokens=32000, show_thinking=True):
    ehr = EHR(task.fixture)
    initial, start_hash = ehr.snapshot(), ehr.state_hash()
    log = TrajectoryLog(traj_path)
    config = {"effort": effort or "model default", "max_tokens": max_tokens, "max_turns": task.max_turns,
              "thinking": "adaptive, summarized display" if show_thinking else "model default"}
    meta = {"run_id": run_id, "task": task.id, "policy": "model", "model": model, "trial": trial, "attempt": attempt}
    sys_text = system_prompt(ehr)
    log.write("meta", **meta, start_hash=start_hash, config=config, system=sys_text, prompt=task.prompt)

    request = {"model": model, "max_tokens": max_tokens,
               "system": [{"type": "text", "text": sys_text, "cache_control": {"type": "ephemeral"}}],
               "tools": tools_for_api()}
    if effort:
        request["output_config"] = {"effort": effort}
    if show_thinking:
        request["thinking"] = {"type": "adaptive", "display": "summarized"}

    messages = [{"role": "user", "content": task.prompt}]
    usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    status_counts = {"ok": 0, "validation_error": 0, "env_error": 0, "skipped_after_submit": 0}
    turns, stop_reason, error = 0, None, None
    t0 = time.time()

    while stop_reason is None:
        if turns >= task.max_turns:
            stop_reason = "turn_limit"
            break
        try:
            resp = client.messages.create(**request, messages=messages[:-1] + [_with_cache_breakpoint(messages[-1])])
        except CONFIG_ERRORS as e:
            raise ConfigError(f"{type(e).__name__}: {e}") from e
        except anthropic.APIError as e:  # rate limits, overload, network, 5xx after the SDK's own retries
            stop_reason, error = "infra_error", f"{type(e).__name__}: {e}"
            log.write("api_error", error=error)
            break
        turns += 1
        for k in usage:
            usage[k] += getattr(resp.usage, k, 0) or 0
        log.write("assistant", turn=turns, stop_reason=resp.stop_reason,
                  content=[b.model_dump(mode="json", exclude_none=True) for b in resp.content],
                  usage=resp.usage.model_dump(mode="json", exclude_none=True))
        messages.append({"role": "assistant", "content": resp.content})

        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        if not tool_uses:
            stop_reason = {"end_turn": "end_turn", "stop_sequence": "end_turn", "max_tokens": "token_limit",
                           "refusal": "refusal"}.get(resp.stop_reason, resp.stop_reason)
            break
        if resp.stop_reason == "max_tokens":  # tool call was cut off mid-generation
            stop_reason = "token_limit"
            break

        results, submitted = [], False
        for tu in tool_uses:
            if submitted:
                status_counts["skipped_after_submit"] += 1
                log.write("tool_call", name=tu.name, input=tu.input, status="skipped_after_submit", result=None)
                continue
            out = execute(ehr, tu.name, tu.input)
            status_counts[out.status] += 1
            log.write("tool_call", turn=turns, tool_use_id=tu.id, name=tu.name, input=tu.input, status=out.status,
                      result=out.content, latency_ms=out.latency_ms, traceback=out.traceback)
            if out.status == "env_error":
                stop_reason = "env_error"
                break
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": out.content,
                            "is_error": out.is_error})
            if tu.name == "submit" and not out.is_error:
                submitted = True
        if stop_reason:
            break
        if submitted:
            stop_reason = "submitted"
            break
        messages.append({"role": "user", "content": results})

    stats = {"turns": turns, "tool_calls": sum(v for k, v in status_counts.items() if k != "skipped_after_submit"),
             "tool_status": status_counts, "usage": usage, "wall_s": round(time.time() - t0, 2), "error": error}
    return finish_trial(task, ehr, initial, start_hash, stop_reason, log, meta, stats)
