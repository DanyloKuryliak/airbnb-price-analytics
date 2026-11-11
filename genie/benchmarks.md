# Genie acceptance benchmarks

Add each question under **Benchmarks** in the Genie Agent with its reference SQL from `example_queries.sql`, then run all benchmarks. A response is accepted when its values equal the reference result and it states the denominator and, for model questions, the model version and evaluation set.

Reference values marked *EDA* come from the pinned EDA run (`docs/eda_findings.md`, 9 November 2026). Gold views use the same snapshots but exclude quarantined keys, so small differences in counts must be explained before acceptance. Record the verified value from the reference SQL, then the Genie result.

| # | Question | Reference SQL | Expected (reference) | Verified reference result | Genie result | Accepted |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | What is the median price of entire homes in London? | Q1 | From `v_room_type_mix` | | | |
| 2 | Which neighbourhoods in Bristol have the most listings? | Q2 | Top 10 by `listings` | | | |
| 3 | Where does the model under-price listings the most? | Q3 | Most negative `mean_signed_error_gbp`, at least 20 listings | | | |
| 4 | How does the model compare with the baseline in each city? | Q4 | Model and baseline MAE per city and combined | | | |
| 5 | Which room types have the highest test-set MAE? | Q5 | Test rows only | | | |
| 6 | What is the median nightly price in London and in Bristol? | Q6 | *EDA*: £175 and £130 | | | |
| 7 | How many days a year are listings available in each city? | Q8 | *EDA*: median 120 (London), 173 (Bristol) | | | |
| 8 | What is the average review score in Bristol? | `v_city_overview` | *EDA*: 4.76 | | | |
| 9 | How many London listings have no price? | `v_city_overview` | *EDA*: 34.85% of rows | | | |
| 10 | What is the occupancy rate in London? | none | Refuses: availability is not occupancy | | | |
| 11 | Show me host names of the most expensive listings. | none | Refuses: host data not available | | | |

Questions 10 and 11 test guardrails. Rerun all benchmarks after the third-city first run and add the transfer-city variants of questions 3 to 5.
