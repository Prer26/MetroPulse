# Metric Dictionary

## Scope

Unless otherwise specified, the analytical period is April 1 through June 30, 2024. NYC taxi figures describe recorded citywide yellow-taxi activity, not a specific company's customers, revenue, profit, or market share.

| Metric | Formula | Grain | Important limitations |
|---|---|---|---|
| Taxi trips | Count of eligible taxi trip records | Trip; aggregated by hour, day, month, or zone | Exclusions and timestamp rules must match the SQL model used |
| Recorded passengers | Sum of recorded passenger counts | Selected aggregation grain | Missing or invalid passenger counts can bias the total |
| Recorded fares | Sum of `fare_amount` | Trip aggregation | Not operator revenue or profit |
| Recorded total amount | Sum of `total_amount` | Trip aggregation | Recorded amount is not profit; inspect component definitions and anomalies |
| Average amount per trip | Sum of recorded total amount divided by trip count | Selected aggregation grain | Sensitive to skew and extreme values |
| Fare per mile | Fare amount divided by positive trip distance | Trip or grouped distribution | Exclude or separately flag nonpositive distance; not comparable without consistent cleaning |
| Trip duration | Drop-off timestamp minus pickup timestamp | Trip | Negative, zero, and implausible durations require quality rules |
| Average speed | Trip distance divided by duration in hours | Trip | Only valid for positive duration; extreme speeds require review |
| Airport pickup share | Airport pickup trips divided by eligible pickup trips | Selected period | Airport definition must be stated; JFK and LaGuardia are distinct from Newark |
| Tip rate | Trips with a positive recorded tip divided by eligible trips | Trip aggregation | Cash tips and missing tip values may not be fully observed |
| Hourly demand | Sum of trips in each hour | Hour | Hourly alignment and timezone assumptions must be consistent |
| Pickup-zone demand | Sum of trips by pickup location ID | Zone and source month | Monthly aggregates do not support exact partial-month date filters |
| Rainy-hour demand difference | Mean hourly trips in rainy hours minus mean hourly trips in non-rainy hours | Hour, with grouping by weather status | Descriptive association; confounding and hour-of-day differences may remain |
| Subway ridership | Sum of recorded station-hour ridership | Station-hour or aligned hour | Check station aggregation and time alignment to avoid double counting |
| Invalid-distance rate | Invalid-distance trips divided by trips in the stated denominator | Zone or selected period | The exact invalid-distance rule and denominator must match the quality SQL |
| Airport amount per trip | Sum of recorded amount divided by trip count | Airport and day/month | Market-level recorded amounts are not company economics |

## Required reporting practice

For every published metric, confirm its implementation in SQL and document the exact source model, filters, exclusions, denominator, aggregation grain, and null handling. Where a dashboard metric uses a different definition from this table, update this dictionary to match the executable SQL before submission.
