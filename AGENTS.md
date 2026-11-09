# Project conventions

## Scope

Team Вишня studies UK Airbnb advertised nightly prices in GBP. London and Bristol are development cities; Greater Manchester is the unseen transfer location. Person 1 owns EDA and data quality, Person 2 ETL and architecture, Person 3 modelling, and Person 4 dashboard and Genie.

## Data integrity

- Do not acquire, open, sample, profile or query Greater Manchester data until both the A/B pipeline and model have been completed, validated and frozen. Its first evaluation must use those unchanged artifacts, with results recorded before corrections.
- Use the latest published detailed `listings.csv.gz` snapshots for a new study. Record dates, source URLs and checksums; preserve previously frozen sources.
- Preserve raw inputs unchanged. One row represents one listing snapshot.
- Do not commit raw records, large tables, credentials, personally identifying fields or notebook outputs.
- Use Databricks Free Edition and zero-cost dependencies only.

## Implementation

- Inspect existing files before editing. Preserve other contributors' work.
- Use configurable paths and catalog/schema names. Coordinate contract changes with affected owners.
- Maintain one city-parameterized ETL pipeline rather than city-specific copies.
- Reserve per-city test sets before model selection. Fit preprocessing and room-type/accommodates median baselines on training rows only.
- Report baseline/model MAE in GBP per city and combined, including evaluated counts and prediction coverage.
- Record third-city first-run failures and metrics before changes; classify subsequent changes as pipeline fixes or model changes.
- Keep documentation formal, factual and reproducible. Distinguish completed components from proposed interfaces. Exclude conversational context, task chronology and administrative navigation from deliverables.
