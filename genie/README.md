# Genie Agent

Owner: Person 4. The agent answers natural-language questions over the Gold reporting views created by `notebooks/04_bi_gold_views.ipynb`.

| File | Content |
| --- | --- |
| [instructions.md](instructions.md) | General instructions to paste into the agent, tables to add and configuration practices |
| [example_queries.sql](example_queries.sql) | Example SQL queries registered in the agent as trusted patterns |

## Status

Configuration files are complete. The agent itself is created in the Databricks workspace; its URL is recorded in the root README after acceptance. Model questions require `airbnb_gold.predictions` from the price model.

## Setup procedure

1. Run `notebooks/04_bi_gold_views.ipynb` so that the `v_*` views exist with column comments.
2. In Databricks open **Genie > New**. Select a serverless SQL warehouse and add the views listed in `instructions.md`.
3. Name the agent `Airbnb UK prices — Team Вишня`. Add a description stating the cities, snapshot dates and GBP unit.
4. Paste the instruction block from `instructions.md` into **Instructions > Text**.
5. Add each query in `example_queries.sql` under **SQL queries**, titled with its question.
6. Add the sample questions shown to users: the first four acceptance questions below.
7. Enable value matching for `room_type`, `neighbourhood`, `city` and `pricing_direction`.
8. Ask the acceptance questions below in a new conversation and compare each answer and its generated SQL with the matching example query. Correct instructions, not data, when an answer is wrong, and ask again.
9. Share the agent with team members (**Can run**). Users also need `SELECT` on the views and `CAN USE` on the warehouse.

## Acceptance questions

| Question | Reference |
| --- | --- |
| What is the median price of entire homes in London? | Q1 |
| Which neighbourhoods in Bristol have the most listings? | Q2 |
| Where does the model under-price listings the most? | Q3 |
| How does the model compare with the baseline in each city? | Q4; model v1 test MAE £76.93 against £104.17 for the baseline (12,434 listings, `docs/model_results.md`) |
| What is the occupancy rate in London? | Declines: availability is not occupancy |

## Rules

Answers define price as nightly advertised GBP, distinguish availability from occupancy, and state snapshot dates and valid-row denominators. Model answers distinguish baseline and model, city, evaluation set and model version. The agent has no access to host details. The third city appears only after the release gate and unchanged first run in `reports/city_c_protocol.md`.
