# Run report 20261109-122344_pilot4b

Policy model, model claude-opus-5, effort model default, commit 662bedf697 (dirty), initial state hash 6c38f487cdb4999e.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| strep_allergy | 3 | 2 | 67% | 21% to 94% | 0.93 | yes | 0 |

## Why trials failed

**strep_allergy**
- failed check `antibiotics_appropriate_for_allergy_history` in 1 trial(s)
- failed check `no_penicillin_for_penicillin_allergic` in 1 trial(s)
- failed check `hidden_anaphylaxis_added_to_allergy_list` in 1 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| strep_allergy | submitted 3 | 11.7 | 48.0 | 0.00 | 0 | 3 |

Every trial started from state hash 6c38f487cdb4999e (identical).

Estimated API cost $1.11 across 3 trials ($0.37 per trial). Estimate only.

