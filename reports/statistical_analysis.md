# MetroPulse — Statistical Analysis and Sensitivity Report

**Analysis period:** April 1–June 30, 2024
**Purpose:** Quantify uncertainty in selected historical comparisons and assess whether the airport result is sensitive to recorded-amount filters.

## 1. Airport amount per mile: paired daily comparison

The analysis matched dates containing observations for both JFK Airport and LaGuardia Airport. For each matched date, it calculated the difference between the airports' daily median recorded amount per mile, then averaged those daily differences.

| Measure | Result |
|---|---:|
| Matched dates | 91 |
| Mean daily-median difference, LGA minus JFK | $1.999 per mile |
| 95% percentile-bootstrap interval | $1.967 to $2.031 per mile |
| Bootstrap repetitions | 10,000 |
| Random seed | 42 |

The interval lies entirely above zero. Within this dataset and under the implemented resampling procedure, LaGuardia's daily median recorded amount per mile was higher on average than JFK's.

**Interpretation limits:** This is a difference in the mean of paired daily medians, not a difference between overall trip-level medians. Recorded amount per mile is not profit or driver earnings. Differences in trip distance, passenger mix, operating conditions, and other factors may contribute to the observed gap. The current bootstrap resamples individual dates and may not fully account for serial dependence between adjacent dates.

## 2. Weather and taxi demand: paired-date comparison

For each date, the analysis compared average taxi trips during rainy hours with average taxi trips during dry hours. Only dates containing both rainy and dry hours were retained.

| Day type | Dates | Mean daily difference (rainy minus dry) | 95% date-bootstrap interval | Positive dates | Negative dates |
|---|---:|---:|---:|---:|---:|
| Weekday | 31 | +864.80 trips/hour | -244.79 to 1,915.99 | 20 | 11 |
| Weekend | 17 | +906.04 trips/hour | -52.24 to 1,688.23 | 14 | 3 |

Both intervals include zero. These estimates therefore do not establish a clear rainy-versus-dry difference at the 95% interval level.

The comparison is descriptive, not causal. Rainy and dry hours may occur at different times of day, and the implemented analysis does not fully adjust for hour-of-day, seasonality, or other confounders. The number of dates is also limited, particularly for weekends.

## 3. Airport sensitivity analysis

The airport comparison was repeated after applying alternative upper bounds to recorded trip total amount. The SQL excludes trips outside the Q2 date window and trips with nonpositive distance.

| Recorded total amount cap | Matched dates | Average JFK daily median ($/mile) | Average LGA daily median ($/mile) | Mean daily difference ($/mile) | LGA higher (%) |
|---:|---:|---:|---:|---:|---:|
| $500 | 91 | 5.182 | 7.182 | 1.999 | 38.6 |
| $300 | 91 | 5.181 | 7.182 | 2.001 | 38.6 |
| $200 | 91 | 5.176 | 7.182 | 2.006 | 38.8 |

The estimated difference varies by only $0.007 per mile across these scenarios. This indicates that the descriptive gap is stable under the three tested total-amount caps.

These are sensitivity scenarios using the same underlying dataset, not independent replications. The filter applies to total recorded amount rather than directly capping amount per mile. The sensitivity analysis does not resolve confounding, serial dependence, or the distinction between recorded amount and profitability.

## 4. Operational pilot design: minimum detectable effect and sample size

The historical taxi dataset does not provide the operator-specific cost, empty-mile, vehicle-hour, waiting-time, and treatment-assignment data needed to calculate a definitive operational pilot sample size. Accordingly, the figures below are **planning illustrations, not estimates of expected business impact**.

For a two-arm comparison with a continuous outcome, a conventional approximate sample-size calculation per arm is:

n ≈ 2 × (1.96 + 0.84)² / d²

where d is the target standardized effect (the difference in means divided by the outcome's standard deviation), using a two-sided 5% significance level and 80% statistical power. This approximation assumes independent observations, equal-sized arms, and no clustering or attrition.

| Illustrative standardized effect (d) | Approximate independent observations per arm | Total observations |
|---:|---:|---:|
| 0.50 | 63 | 126 |
| 0.30 | 175 | 350 |
| 0.20 | 392 | 784 |

These figures are not ready-to-use operational sample sizes. If assignment occurs by airport-day, zone-hour, driver, or another cluster, the analysis must account for within-cluster correlation. Attrition, repeated measurements, multiple outcomes, and the feasible number of independent clusters may also increase the required sample.

### Pilot A: airport-focused supply and pricing operations

- **Treatment:** A pre-specified airport supply or dispatch intervention.
- **Control:** Matched airport-time units continuing business as usual.
- **Primary outcome:** Contribution per vehicle-hour using actual operator receipts and variable costs.
- **Guardrails:** Service availability, wait time, cancellations, empty miles, and safety.
- **Baseline:** Collect outcome variance, cluster structure, and eligible unit counts before calculating the final sample size.
- **Decision rule:** Scale only if the pre-registered treatment effect meets the business threshold and guardrails remain acceptable.

### Pilot B: peak-hour fleet positioning

- **Treatment:** Additional planned supply in selected peak-hour zones.
- **Control:** Matched zone-time units receiving usual supply.
- **Primary outcome:** Empty miles per completed trip.
- **Secondary outcome:** Contribution per vehicle-hour.
- **Guardrails:** Completed trips, wait times, cancellations, driver utilisation, and contribution after variable costs.
- **Proposed business target:** An 8% reduction in empty miles per completed trip. This is a proposed target, not a forecast or statistically validated MDE.
- **Baseline:** Estimate the mean, standard deviation, cluster correlation, eligible zones and time windows, and feasible number of independent assignment units before computing the final sample size.
- **Decision rule:** Evaluate the pre-registered treatment-control difference and confidence interval, subject to the guardrails.

### Four-week operating plan for both pilots

1. **Week 1 — Baseline and design:** Define eligible units, collect baseline outcomes, match or randomize treatment and control units, estimate variance, calculate the MDE/sample size, and pre-register exclusions and analysis.
2. **Week 2 — Launch:** Start the intervention and monitor data completeness, assignment compliance, and safety.
3. **Week 3 — Monitor:** Review guardrails and implementation quality without changing the primary outcome or decision thresholds in response to interim results.
4. **Week 4 — Evaluate:** Estimate the treatment-control effect with an appropriate confidence interval; apply the pre-registered scale, continue, or stop rule.

Stop or pause early for material safety problems or pre-specified guardrail deterioration. Do not claim a successful pilot based solely on a favorable point estimate if uncertainty remains too high.

## 5. Reproducibility and remaining limitations

The numerical results in this report were captured from the existing project scripts and their console output. The bootstrap scripts currently print their results rather than automatically saving a structured report. A future reproducible build should execute these analyses and persist their results, with tests that verify the expected inputs and output schema.

Historical observational data can identify promising operational hypotheses. It cannot establish the causal effect or profitability of either proposed intervention. Final operational sample sizes and decision thresholds require baseline data from the participating operator.

