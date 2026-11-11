# Airbnb price analytics — Team Вишня

A reproducible UK Airbnb lakehouse and nightly advertised-price study using Databricks Free Edition. London and Bristol are development cities; Greater Manchester is the unseen transfer city and remains locked until the A/B pipeline and model freeze. Currency: GBP.

## Project components

The repository contains the exploratory analysis, lakehouse interfaces, ETL and model entry points, dashboard/Genie specifications and transfer-evaluation protocol. GitHub versions source and aggregate artifacts; Databricks Free Edition provides execution and governed storage.

## Ownership and status

| Owner | Responsibility | Status |
| --- | --- | --- |
| Person 1 | London/Bristol EDA, data quality and leakage review | Implemented and executed successfully |
| Person 2 | Parameterized medallion ETL and architecture | Schema provisioned; implementation pending |
| Person 3 | Training-only baseline, price model and test evaluation | Schema provisioned; implementation pending |
| Person 4 | Three-page AI/BI dashboard and Genie Agent | Gold reporting views, dashboard definition and Genie configuration implemented; workspace deployment pending |

## Sources

Latest published detailed snapshots verified on 9 November 2026 from [Inside Airbnb](https://insideairbnb.com/get-the-data/), licensed CC BY 4.0. [sources.json](sources.json) records immutable checksums and source paths. The [publisher dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit) defines price as local currency and documents the dollar symbol as an export artifact.

| City | Published snapshot | Listing rows | Detailed source |
| --- | --- | --- | --- |
| London | 2026-09-17 | 91,954 | [listings.csv.gz](https://data.insideairbnb.com/united-kingdom/england/london/2026-09-17/data/listings.csv.gz) |
| Bristol | 2026-09-22 | 2,932 | [listings.csv.gz](https://data.insideairbnb.com/united-kingdom/england/bristol/2026-09-22/data/listings.csv.gz) |
| Greater Manchester | Not acquired: holdout locked | Not inspected | Resolve after release gate |

Published snapshot labels differ from listing scrape dates. The EDA audits both. Raw files are excluded from Git and never overwritten. The downloader checks for newer published A/B sources and stops if the pinned manifest needs an intentional update. Preserve frozen sources when refreshing a subsequent study.

## Reproduction

Use Python 3.11 or later. Local validation is supplementary; submitted analysis must also run in Databricks Free Edition.

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/download_sources.py
.venv/bin/python scripts/validate_repository.py
```

Run from the repository root. Execute `.venv/bin/python scripts/run_eda.py` to regenerate the EDA reports. The notebook also runs interactively with Jupyter. It uses pandas and matplotlib already available in Databricks; local notebook-execution packages are not needed there. The findings report places nine figures beside their interpretations. Detailed checks are retained in a [technical audit](docs/eda_audit.md). Repository notebook source is output-free; reports contain aggregates only.

[Databricks setup](docs/setup_databricks.md) defines storage paths, parameters, runtime requirements and execution evidence. [Collaboration](docs/collaboration.md) defines branch ownership and review. [Data contract](docs/data_contract.md) separates provisioned EDA storage from proposed production objects.

## Execution order and evaluation

1. Run Person 1's [EDA notebook](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/main/notebooks/01_eda_london_bristol.ipynb). Review [findings](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/main/docs/eda_findings.md), [column profile](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/main/docs/eda_profile.md) and [cleaning specification](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/main/docs/cleaning_specification.md).
2. Agree the contract. Person 2 implements one pipeline parameterized by city: immutable Bronze files, typed/flagged Silver records and Gold aggregates/features.
3. Person 3 reserves a per-city test set before model selection, fits preprocessing and room-type/accommodates median baselines on training rows only, evaluates MAE in GBP for each city and combined, and writes per-listing predictions to Gold.
4. Freeze the validated A/B pipeline and model versions. Record all release evidence in the [holdout protocol](reports/city_c_protocol.md).
5. After the release gate, run the unchanged pipeline/model on Greater Manchester and record first-run failures and metrics before fixes. Classify subsequent changes and compare results.
6. Person 4 delivers city overview, A/B comparison and model-diagnostics dashboard pages plus a Genie Agent grounded on Gold tables. Add transfer findings after the locked first run.

No paid infrastructure, APIs or external managed services are required. Free Edition quotas apply; do not upgrade to a paid trial or create classic clusters to bypass limits.

## Submission links

The repository is the submission entry point. Additional component links are recorded as their implementations are completed.

| Artifact | Location |
| --- | --- |
| Repository | https://github.com/DanyloKuryliak/airbnb-price-analytics |
| EDA | `notebooks/01_eda_london_bristol.ipynb` |
| ETL and architecture | Person 2 deliverable pending |
| Price model and test metrics | Person 3 deliverable pending |
| Dashboard and Genie | `notebooks/04_bi_gold_views.ipynb`, [dashboard/](dashboard/README.md), [genie/](genie/README.md); published links pending |
| Third-city first run | Locked; protocol in `reports/city_c_protocol.md` |
| Presentation | Final PDF or share link pending |
