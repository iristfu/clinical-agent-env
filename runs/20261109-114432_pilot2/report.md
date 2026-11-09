# Run report 20261109-114432_pilot2

Policy model, model claude-opus-5, effort model default, commit 376bd1129a, initial state hash 1525606c32518a45.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| apixaban_dose | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |
| med_rec_discharge | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |
| panel_a1c | 3 | 2 | 67% | 21% to 94% | 0.97 | yes | 0 |
| strep_allergy | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |

## Why trials failed

**panel_a1c**
- failed check `ordered_set_matches_expected` in 1 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| apixaban_dose | submitted 3 | 7.3 | 11.7 | 0.00 | 0 | 3 |
| med_rec_discharge | submitted 3 | 9.0 | 20.7 | 0.00 | 0 | 3 |
| panel_a1c | submitted 3 | 12.7 | 75.0 | 0.00 | 0 | 3 |
| strep_allergy | submitted 3 | 7.7 | 13.0 | 0.00 | 0 | 3 |

Every trial started from state hash 1525606c32518a45 (identical).

Estimated API cost $2.53 across 12 trials ($0.21 per trial). Estimate only.

