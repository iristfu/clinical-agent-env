# Run report 20261109-123141_pilot5

Policy model, model claude-opus-5, effort model default, commit fc9c70f3d0, initial state hash 0d13c7883d5c6131.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| apixaban_dose | 3 | 2 | 67% | 21% to 94% | 0.94 | yes | 0 |
| med_rec_discharge | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |

## Why trials failed

**apixaban_dose**
- failed check `nvaf_doses_correct` in 1 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| apixaban_dose | submitted 3 | 12.7 | 66.7 | 0.00 | 0 | 3 |
| med_rec_discharge | submitted 3 | 14.3 | 50.3 | 0.00 | 0 | 3 |

Every trial started from state hash 0d13c7883d5c6131 (identical).

Estimated API cost $2.80 across 6 trials ($0.47 per trial). Estimate only.

