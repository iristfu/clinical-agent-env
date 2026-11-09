# Run report 20261109-130217_final

Policy model, model claude-opus-5, effort model default, commit c4434b55f9, initial state hash f396b2656fa7cb59.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| apixaban_dose | 10 | 6 | 60% | 31% to 83% | 0.93 | yes | 0 |
| panel_a1c | 10 | 7 | 70% | 40% to 89% | 0.97 | yes | 0 |
| strep_allergy | 10 | 1 | 10% | 2% to 40% | 0.82 | no | 0 |

## Why trials failed

**apixaban_dose**
- failed check `nvaf_doses_correct` in 4 trial(s)
- triage: model_info_gathering 4

**panel_a1c**
- failed check `ordered_set_matches_expected` in 3 trial(s)
- triage: model_info_gathering 3

**strep_allergy**
- failed check `antibiotics_appropriate_for_allergy_history` in 9 trial(s)
- failed check `no_penicillin_for_penicillin_allergic` in 9 trial(s)
- failed check `hidden_anaphylaxis_added_to_allergy_list` in 9 trial(s)
- triage: model_info_gathering 9

## Pass audit

- apixaban_dose trial 07: pass_right_reason
- apixaban_dose trial 09: pass_right_reason
- panel_a1c trial 01: pass_right_reason
- panel_a1c trial 03: pass_right_reason
- strep_allergy trial 03: pass_right_reason

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| apixaban_dose | submitted 10 | 12.1 | 65.6 | 0.00 | 0 | 10 |
| panel_a1c | submitted 10 | 12.1 | 72.0 | 0.00 | 0 | 8 |
| strep_allergy | submitted 10 | 10.8 | 45.3 | 0.00 | 0 | 10 |

Every trial started from state hash f396b2656fa7cb59 (identical).

Estimated API cost $11.63 across 30 trials ($0.39 per trial). Estimate only.

