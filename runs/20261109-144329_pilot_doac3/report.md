# Run report 20261109-144329_pilot_doac3

Policy model, model claude-opus-5, effort model default, commit a3421c2738 (dirty), initial state hash eaa87f3c56ec380b.

## Pass rates

| Task | Valid trials | Passed | Pass rate | 95% CI (Wilson) | Mean score | In 20-70% band | Invalid |
|---|---|---|---|---|---|---|---|
| doac_dose_reasoning | 5 | 4 | 80% | 38% to 96% | 0.98 | no | 0 |

## Why trials failed

**doac_dose_reasoning**
- failed check `apixaban_raised_at_age_79` in 1 trial(s)

## Episodes

| Task | Stop reasons | Mean turns | Mean tool calls | Validation errors per trial | Env errors | Distinct end states |
|---|---|---|---|---|---|---|
| doac_dose_reasoning | submitted 5 | 12.8 | 82.2 | 0.20 | 0 | 5 |

Every trial started from state hash 9f955c9404e43647 (identical).

Estimated API cost $3.39 across 5 trials ($0.68 per trial). Estimate only.

