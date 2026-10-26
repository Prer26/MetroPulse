# Executive Decision Memo — MetroPulse

**Period analysed:** April 1–June 30, 2024  
**Decision:** Prioritise two controlled operational pilots; do not treat historical market records as proof of a specific operator's expected profit.

## 1. Airport-focused supply and pricing operations

**Evidence:** The current analysis reports 487,038 JFK pickup trips and 354,408 LaGuardia pickup trips. Recorded amount per trip was approximately $77.26 at JFK and $67.09 at LaGuardia. These are historical market-level figures, not operator revenue or profit, and airport differences may reflect trip distance, passenger mix, and other confounders.

**Pilot:** Compare matched airport-day or airport-time-window units under a pre-defined operational treatment versus business-as-usual controls. Establish a baseline in week 1, launch in week 2, review guardrails and refine in week 3, and make a scale/stop decision in week 4.

**Primary metric:** Contribution per vehicle-hour, calculated from the pilot operator's actual costs and receipts. Historical TLC records alone cannot measure this metric.

**Guardrails:** Service availability, wait time, cancellations, empty miles, and safety. Define a minimum detectable effect from baseline variance and feasible sample size before launch. Stop for material guardrail deterioration; scale only if the pre-specified effect and guardrails are met.

## 2. Peak-hour fleet positioning

**Evidence:** The current hourly analysis identifies 6 PM as a high-demand hour, with approximately 765,822 pickups across the quarter. Midtown Center and Upper East Side South also appear among leading pickup zones in the analysed 4–6 PM window. Validate the selected time window and zone-level totals against the final SQL outputs before using them as final submission figures.

**Pilot:** Compare selected peak-hour zone/time windows receiving planned additional supply with matched control windows receiving business-as-usual supply. Use week 1 for baseline and matching, weeks 2–3 for the controlled intervention, and week 4 for evaluation.

**Primary metric:** Empty miles per completed trip, with contribution per vehicle-hour as a secondary outcome. An initial operational target is at least an 8% reduction in empty miles per completed trip; this is a proposed pilot threshold, not a forecast.

**Guardrails:** Completed trips, wait times, cancellations, driver utilisation, and contribution after variable costs. Set sample-size/MDE reasoning and stopping rules from baseline data before treatment begins.

## Decision rules and limitations

For both pilots, compare treatment and control changes rather than relying on raw before/after differences. Pre-register the unit of analysis, exclusions, confidence interval method, minimum detectable effect, and decision thresholds. Historical observational data can identify promising opportunities but cannot establish causal impact. The pilot should proceed only if the operator can collect actual operating costs, supply, service, and outcome data.

**Next action:** Validate all cited figures against the final tested SQL models, attach uncertainty and sensitivity results, and approve the pilot protocols before funding a wider rollout.

