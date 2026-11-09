# Run report 20261109-142627_pilot_doac2

Policy model, model claude-opus-5, effort model default, commit a3421c2738 (dirty), initial state hash eaa87f3c56ec380b.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| doac_dose_reasoning | 5 | 0 | 0% | 0% to 43% | 0.92 | no | 0 |

## Why trials failed

**doac_dose_reasoning**
- failed check `correct_doses_left_alone` in 5 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| doac_dose_reasoning | submitted 5 | 13.2 | 74.6 | 0.20 | 0 | 5 |

Every trial started from state hash 57404ee41e9907f5 (identical).

Estimated API cost $2.67 across 5 trials ($0.53 per trial). Estimate only.

