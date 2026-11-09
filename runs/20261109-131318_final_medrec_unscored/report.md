# Run report 20261109-131318_final_medrec_unscored

Policy model, model claude-opus-5, effort model default, commit c4434b55f9, initial state hash f396b2656fa7cb59.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| med_rec_discharge | 10 | 10 | 100% | 72% to 100% | 1.00 | no | 0 |

## Why trials failed

## Pass audit

- med_rec_discharge trial 06: pass_right_reason
- med_rec_discharge trial 09: pass_right_reason

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| med_rec_discharge | submitted 10 | 16.1 | 62.8 | 0.00 | 0 | 10 |

Every trial started from state hash f396b2656fa7cb59 (identical).

Estimated API cost $5.27 across 10 trials ($0.53 per trial). Estimate only.

