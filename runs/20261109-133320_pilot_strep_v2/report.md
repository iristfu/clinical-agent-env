# Run report 20261109-133320_pilot_strep_v2

Policy model, model claude-opus-5, effort model default, commit be82311c14, initial state hash eaa87f3c56ec380b.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| strep_allergy | 8 | 3 | 38% | 14% to 69% | 0.83 | yes | 0 |

## Why trials failed

**strep_allergy**
- failed check `one_regimen_per_positive_patient` in 5 trial(s)
- failed check `antibiotics_appropriate_for_allergy_history` in 5 trial(s)
- failed check `no_penicillin_for_penicillin_allergic` in 3 trial(s)
- failed check `hidden_anaphylaxis_added_to_allergy_list` in 3 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| strep_allergy | submitted 8 | 12.4 | 57.8 | 0.00 | 0 | 8 |

Every trial started from state hash eaa87f3c56ec380b (identical).

Estimated API cost $3.10 across 8 trials ($0.39 per trial). Estimate only.

