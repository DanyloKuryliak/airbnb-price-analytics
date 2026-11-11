# Data contract

Status: proposed production interfaces; ETL and ML owners must approve before creating dependencies. Lakehouse schemas and EDA storage are provisioned; production tables are not implemented.

## Names and storage

| Layer | Object / interface | Grain and purpose | Owner |
| --- | --- | --- | --- |
| EDA raw | `/Volumes/workspace/airbnb_eda/raw/` | Immutable detailed source files and pinned manifest | Person 1 |
| EDA artifacts | `/Volumes/workspace/airbnb_eda/artifacts/` | Aggregate reports and figures | Person 1 |
| Bronze | `workspace.airbnb_bronze`, managed volume `raw` | Original compressed files, partitioned by city and snapshot date | Person 2 |
| Silver | `workspace.airbnb_silver.listings` | One row per city, listing ID and snapshot date, including quality flags | Person 2 |
| Gold features | `workspace.airbnb_gold.features` | Versioned candidate features and split assignment | Persons 2–3 |
| Gold predictions | `workspace.airbnb_gold.predictions` | One row per listing snapshot and model version | Person 3 |
| Gold metrics | `workspace.airbnb_gold.model_metrics` | Dataset, split, city, model version and metric | Person 3 |
| Gold overview | `workspace.airbnb_gold.city_metrics` | Aggregates with explicit valid-row denominators | Persons 2–4 |
| Gold reporting views | `workspace.airbnb_gold.v_*` | Read-only, commented views for the dashboard and Genie; model views require `predictions` | Person 4 |

Catalog `workspace` is verified in the current workspace. Separate workspaces use the same schema and table names under their available catalog. Catalog, schema, input root and output root must be parameters. Bronze, Silver and Gold schemas are reserved for team development. Production tables have not been created. Optional fields may remain nullable in the contract even when excluded from the initial model; `instant_bookable` and `neighbourhood_group_cleansed` are entirely missing in the pinned A/B snapshots.

## Silver columns

- Key: `city STRING`, `listing_id STRING`, `snapshot_date DATE`. Reject ambiguous or missing keys into a quarantine output; never silently select one duplicate.
- Provenance: `source_url STRING`, `source_sha256 STRING`, `last_scraped DATE`, `ingested_at TIMESTAMP`, `pipeline_version STRING`. The published snapshot date is not always the listing scrape date.
- Target: `price_raw STRING`, `price_gbp DOUBLE`, `currency STRING = 'GBP'`, `target_valid BOOLEAN`. Invalid targets remain absent and do not become zero.
- Listing attributes: `room_type STRING`, `property_type STRING`, `accommodates INT`, `bedrooms DOUBLE`, `beds DOUBLE`, `bathrooms DOUBLE`, `bathrooms_shared BOOLEAN`, `neighbourhood_cleansed STRING`, `latitude DOUBLE`, `longitude DOUBLE`, `minimum_nights INT`, `maximum_nights INT`, `instant_bookable BOOLEAN`.
- Quality: an array of rule identifiers, parsing-failure indicators, `bathrooms_source STRING` and a quarantine reason where required. Preserve original textual bathrooms for audit within workspace storage.
- Descriptive attributes: availability counts and review scores. These are not automatically approved predictors.

Do not place host names, listing descriptions, exact addresses, host IDs or listing URLs in repository artifacts. Listing IDs remain join keys inside governed tables and are not model features. Bronze may contain publisher personal fields; restrict access and never export those records to GitHub.

## Model and prediction interface

The target is nightly advertised price in GBP. Freeze a reproducible approximately 20% test split within each A/B city before model selection. Persist split membership and seed; do not reshuffle between experiments. Grouping related listings by host is a validation option requiring agreement before evaluation.

Fit imputation, category encoders, feature selection, thresholds and baseline medians on training rows only. The required baseline is training median price by `room_type` and `accommodates`. Predefine fallbacks for unseen groups, such as room-type training median then global training median; reuse them unchanged on the third city.

Predictions require keys, `model_version`, `pipeline_version`, `split`, `actual_price_gbp` (nullable), `predicted_price_gbp`, `baseline_price_gbp`, `prediction_status` and `generated_at`. Retain rows with missing targets for inference if possible; report prediction coverage separately from MAE. Compute MAE only where the target and prediction are valid. Report test-set London, Bristol and combined MAE; combined MAE is weighted by evaluated listing count, not the mean of city MAEs.

## Freeze and transfer

Greater Manchester is the locked third-city holdout. Before its first access, record the A/B pipeline commit, model artifact/version, feature list, split manifest, baseline statistics, source manifests, environment and successful A/B runs. The first third-city execution uses these unchanged artifacts. Record failures, prediction coverage, baseline MAE and model MAE before corrections. Classify each subsequent change as a pipeline fix or model change. Never rewrite the original first-run evidence.
