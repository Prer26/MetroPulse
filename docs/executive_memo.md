# Executive Decision Memo — MetroPulse

**Analysis period:** April 1–June 30, 2024
**Decision:** Advance two controlled operational pilots to baseline measurement and protocol design. Do not treat historical market records as proof of a specific operator's expected profit or of causal impact.

## Executive summary

The Q2 analysis contains 10,777,291 taxi trips within the defined pickup-time window, alongside hourly subway and weather aggregates. The airport comparison shows a consistent difference in recorded amount per mile, while the weather-demand comparisons remain uncertain.

These findings are useful for prioritising experiments, not for guaranteeing operational or financial gains. The next step is to collect operator-level baseline data, pre-register each pilot, and evaluate treatment against a suitable control.

## 1. Airport-focused supply and pricing operations

### Historical evidence

The analysis reports 487,038 JFK pickup trips and 354,408 LaGuardia pickup trips. Recorded amount per trip was approximately $77.26 at JFK and $67.09 at LaGuardia. These are historical market-level recorded amounts, not operator revenue, contribution, or profit.

A paired daily analysis compared the airports' daily median recorded amount per mile across 91 matched dates:

- Mean daily-median difference, LaGuardia minus JFK: **$1.999 per mile**.
- 95% percentile-bootstrap interval: **$1.967 to $2.031 per mile**.
- Sensitivity checks at recorded total-amount caps of $500, $300, and $200 produced differences of $1.999, $2.001, and $2.006 per mile, respectively.

The estimate is stable across these three filters. However, the scenarios use the same underlying data, and the date-level bootstrap may not fully account for serial dependence. Airport differences may also reflect trip distance, passenger mix, operating conditions, and other confounders. Recorded amount per mile is not a measure of profit.

### Proposed pilot

Compare selected airport-day or airport-time-window units receiving a pre-specified dispatch or supply intervention with matched control units continuing business as usual. Define treatment, eligible units, exclusions, and analysis before launch.

**Primary metric:** Contribution per vehicle-hour, calculated from the participating operator's actual receipts and variable costs.

**Guardrails:** Service availability, wait time, cancellations, empty miles, and safety.

### Four-week plan

1. **Week 1 — Baseline:** Collect actual costs, receipts, supply, service outcomes, and outcome variance. Select eligible units and match or randomise treatment and control where feasible.
2. **Week 2 — Launch:** Apply the pre-specified intervention and verify treatment compliance and data completeness.
3. **Week 3 — Monitor:** Review safety and service guardrails; avoid changing the primary outcome or decision thresholds based on interim results.
4. **Week 4 — Evaluate:** Estimate the treatment-control difference with a pre-specified confidence interval and apply the decision rules.

## 2. Peak-hour fleet positioning

### Historical evidence

The current hourly analysis identifies 6 PM as a high-demand hour, with approximately 765,822 pickups across the quarter. Midtown Center and Upper East Side South also appear among leading pickup zones in the analysed 4–6 PM window. These figures should be rechecked against the final SQL outputs before publication.

The weather comparison provides additional context but does not establish a clear demand effect:

- **Weekdays:** Mean rainy-hour minus dry-hour difference of +864.80 trips/hour across 31 dates; 95% date-bootstrap interval from -244.79 to 1,915.99.
- **Weekends:** Mean difference of +906.04 trips/hour across 17 dates; 95% date-bootstrap interval from -52.24 to 1,688.23.

Both intervals include zero. Rain and dry hours may occur at different times of day, and the analysis does not fully adjust for hourly patterns or other confounders. Therefore, these estimates should not be used as causal forecasts of the effect of weather or fleet repositioning.

### Proposed pilot

Compare selected peak-hour zone-time units receiving planned additional supply with matched control units receiving business-as-usual supply.

**Primary metric:** Empty miles per completed trip.

**Secondary metric:** Contribution per vehicle-hour after variable costs.

**Proposed business target:** At least an 8% reduction in empty miles per completed trip. This is a proposed operational target, not an estimate of expected impact or a statistically validated minimum detectable effect.

**Guardrails:** Completed trips, wait times, cancellations, driver utilisation, and contribution after variable costs.

### Four-week plan

1. **Week 1 — Baseline and matching:** Measure empty miles, completed trips, utilisation, costs, and service outcomes. Select comparable zone-time units and determine the feasible number of independent assignment units.
2. **Week 2 — Launch:** Introduce the planned supply intervention in treatment units while controls continue business as usual.
3. **Week 3 — Monitor:** Check data quality, treatment compliance, and guardrails. Pause for pre-specified safety or material service deterioration.
4. **Week 4 — Evaluate:** Estimate the treatment-control effect and uncertainty. Apply the pre-registered scale, continue, or stop rule.

## 3. Sample-size and minimum-detectable-effect planning

Final operational sample sizes cannot be inferred from the historical taxi data alone. The operator must supply baseline outcome variance, assignment-unit structure, cluster correlation where relevant, expected attrition, and the number of feasible treatment and control units.

For an illustrative two-arm comparison of a continuous outcome, an approximate independent-observation sample size per arm is:

**n ≈ 2 × (1.96 + 0.84)² / d²**

Here, *d* is the target standardised effect (difference in means divided by the outcome standard deviation). This illustration assumes a two-sided 5% significance level, 80% power, equal-sized arms, independent observations, and no attrition.

| Illustrative standardised effect | Approximate observations per arm | Total |
|---:|---:|---:|
| 0.50 | 63 | 126 |
| 0.30 | 175 | 350 |
| 0.20 | 392 | 784 |

These are planning illustrations, not final pilot requirements. Clustered assignment by airport-day, zone-time window, or driver can require substantially more observations. During week 1, calculate the feasible minimum detectable effect from the baseline data and use an appropriate method for the planned randomisation or matching design. For the fleet-positioning pilot, evaluate whether the proposed 8% target is detectable with the available units before committing to the test.

## 4. Decision rules, risks, and limitations

For each pilot, pre-register:

- The unit of assignment and analysis, eligibility rules, exclusions, and primary outcome.
- The baseline period, treatment and control definitions, and confidence-interval method.
- The minimum detectable effect, sample-size calculation, and feasible test duration.
- Guardrail thresholds and safety-based stopping rules.
- The criteria for scaling, extending, or stopping the intervention.

Scale only when the pre-specified business threshold is met with sufficiently precise evidence and the guardrails remain acceptable. If uncertainty is too high, report the result as inconclusive rather than declaring success based only on the point estimate. Stop or pause for safety problems or pre-specified material guardrail deterioration.

The statistical findings and sensitivity results are documented in `reports/statistical_analysis.md`. The current bootstrap analyses are descriptive and resample dates; serial dependence may affect their intervals. The airport sensitivity scenarios are not independent replications. Historical market records do not establish causal impact or operator profitability.

## Recommended next decision

Approve **baseline measurement and pilot protocol development**, not an unconditional operational rollout. Proceed to each controlled pilot only after confirming access to actual operator costs, service outcomes, supply data, and enough eligible treatment and control units to evaluate the pre-specified effect.

