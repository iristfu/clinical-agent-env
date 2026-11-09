# Run report 20261109-125255_pilot7

Policy model, model claude-opus-5, effort model default, commit 37350e673b, initial state hash f396b2656fa7cb59.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| apixaban_dose | 5 | 4 | 80% | 38% to 96% | 0.97 | no | 0 |
| panel_a1c | 5 | 4 | 80% | 38% to 96% | 0.98 | no | 0 |
| strep_allergy | 5 | 3 | 60% | 23% to 88% | 0.92 | yes | 0 |

## Why trials failed

**apixaban_dose**
- failed check `nvaf_doses_correct` in 1 trial(s)

**panel_a1c**
- failed check `ordered_set_matches_expected` in 1 trial(s)

**strep_allergy**
- failed check `antibiotics_appropriate_for_allergy_history` in 2 trial(s)
- failed check `no_penicillin_for_penicillin_allergic` in 2 trial(s)
- failed check `hidden_anaphylaxis_added_to_allergy_list` in 2 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| apixaban_dose | submitted 5 | 12.2 | 66.6 | 0.00 | 0 | 5 |
| panel_a1c | submitted 5 | 12.6 | 75.2 | 0.00 | 0 | 4 |
| strep_allergy | submitted 5 | 11.2 | 46.6 | 0.00 | 0 | 5 |

Every trial started from state hash f396b2656fa7cb59 (identical).

Estimated API cost $6.28 across 15 trials ($0.42 per trial). Estimate only.

