# Run report 20261109-134124_final_v2

Policy model, model claude-opus-5, effort model default, commit 99c2e27b5b, initial state hash eaa87f3c56ec380b.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| apixaban_dose | 10 | 3 | 30% | 11% to 60% | 0.87 | yes | 0 |
| panel_a1c | 10 | 9 | 90% | 60% to 98% | 0.99 | no | 0 |
| strep_allergy | 10 | 6 | 60% | 31% to 83% | 0.90 | yes | 0 |

## Why trials failed

**apixaban_dose**
- failed check `nvaf_doses_correct` in 7 trial(s)
- triage: model_info_gathering 7

**panel_a1c**
- failed check `ordered_set_matches_expected` in 1 trial(s)
- triage: model_info_gathering 1

**strep_allergy**
- failed check `one_regimen_per_positive_patient` in 4 trial(s)
- failed check `antibiotics_appropriate_for_allergy_history` in 4 trial(s)
- failed check `no_penicillin_for_penicillin_allergic` in 2 trial(s)
- failed check `hidden_anaphylaxis_added_to_allergy_list` in 2 trial(s)
- triage: model_info_gathering 4

## Pass audit

- apixaban_dose trial 03: pass_right_reason
- apixaban_dose trial 06: pass_right_reason
- panel_a1c trial 00: pass_right_reason
- panel_a1c trial 05: pass_right_reason
- strep_allergy trial 06: pass_right_reason
- strep_allergy trial 07: pass_right_reason

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| apixaban_dose | submitted 10 | 11.2 | 63.3 | 0.00 | 0 | 10 |
| panel_a1c | submitted 10 | 12.1 | 73.1 | 0.00 | 0 | 9 |
| strep_allergy | submitted 10 | 12.4 | 61.7 | 0.00 | 0 | 10 |

Every trial started from state hash eaa87f3c56ec380b (identical).

Estimated API cost $12.55 across 30 trials ($0.42 per trial). Estimate only.

