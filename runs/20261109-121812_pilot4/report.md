# Run report 20261109-121812_pilot4

Policy model, model claude-opus-5, effort model default, commit 662bedf697, initial state hash 6c38f487cdb4999e.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| apixaban_dose | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |
| med_rec_discharge | 3 | 3 | 100% | 44% to 100% | 1.00 | no | 0 |
| strep_allergy | 3 | 1 | 33% | 6% to 79% | 0.87 | yes | 0 |

## Why trials failed

**strep_allergy**
- failed check `antibiotics_appropriate_for_allergy_history` in 2 trial(s)
- failed check `no_penicillin_for_penicillin_allergic` in 2 trial(s)
- failed check `hidden_anaphylaxis_added_to_allergy_list` in 2 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| apixaban_dose | submitted 3 | 14.0 | 67.3 | 0.00 | 0 | 3 |
| med_rec_discharge | submitted 3 | 12.3 | 38.7 | 0.00 | 0 | 3 |
| strep_allergy | submitted 3 | 10.7 | 50.7 | 0.00 | 0 | 3 |

Every trial started from state hash 6c38f487cdb4999e (identical).

Estimated API cost $3.58 across 9 trials ($0.40 per trial). Estimate only.

