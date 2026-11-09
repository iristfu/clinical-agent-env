# Run report 20261109-115225_pilot3

Policy model, model claude-opus-5, effort model default, commit 7be0375dd0, initial state hash 73934ac27f7c9181.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| apixaban_dose | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |
| med_rec_discharge | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |
| panel_a1c | 3 | 0 | 0% | 0% to 56% | 0.91 | no | 0 |
| strep_allergy | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |

## Why trials failed

**panel_a1c**
- failed check `ordered_set_matches_expected` in 3 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| apixaban_dose | submitted 3 | 7.7 | 11.3 | 0.00 | 0 | 3 |
| med_rec_discharge | submitted 3 | 9.0 | 23.3 | 0.00 | 0 | 3 |
| panel_a1c | submitted 3 | 13.0 | 67.7 | 0.00 | 0 | 2 |
| strep_allergy | submitted 3 | 9.0 | 14.7 | 0.00 | 0 | 3 |

Every trial started from state hash 73934ac27f7c9181 (identical).

Estimated API cost $2.53 across 12 trials ($0.21 per trial). Estimate only.

