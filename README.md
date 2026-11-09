# Airbnb price analytics — Team Вишня

A reproducible UK Airbnb lakehouse and nightly advertised-price study using Databricks Free Edition. London and Bristol are development cities; Greater Manchester is the unseen transfer city and remains locked until the Week 1 pipeline/model freeze. Currency: GBP.

## Shared team environment

GitHub is the source of truth for all four roles. The shared Databricks project is `/Workspace/Shared/airbnb-price-analytics`; start with `00_team_start`. Team lakehouse schemas are `workspace.airbnb_bronze`, `workspace.airbnb_silver` and `workspace.airbnb_gold`. Production tables remain unimplemented. Existing A/B raw inputs and aggregate EDA artifacts are stored in managed volumes.

Use local Git and the GitHub CLI for collaboration and notebook import/export for Databricks execution. Databricks Git integration is optional. Teammate invitations require verified usernames and workspace emails.

## Ownership and status

| Owner | Responsibility | Status |
| --- | --- | --- |
| Person 1 | London/Bristol EDA, data quality and leakage review | Implemented and verified in Free Edition; submitted on `eda/london-bristol` for review |
| Person 2 | Parameterized medallion ETL and architecture | Shared schema/folder reserved; implementation pending |
| Person 3 | Training-only baseline, price model and test evaluation | Shared schema/folder reserved; implementation pending |
| Person 4 | Three-page AI/BI dashboard and Genie Agent | Implementation pending |

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

Run from the repository root. Person 1's EDA implementation and reports are in the [`eda/london-bristol` branch](https://github.com/DanyloKuryliak/airbnb-price-analytics/tree/eda/london-bristol) pending review. On that branch, execute `.venv/bin/python scripts/run_eda.py`. The notebook also runs interactively with Jupyter. It uses pandas and matplotlib already available in Databricks; local notebook-execution packages are not needed there. Reports are aggregate-only; notebook outputs are not saved.

[Databricks setup](docs/setup_databricks.md) covers volume paths, notebook import, access checks and Git integration. [Collaboration](docs/collaboration.md) defines branch ownership and review. [Data contract](docs/data_contract.md) separates provisioned EDA storage from proposed production objects.

## Execution order and evaluation

1. Run Person 1's [EDA notebook](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/eda/london-bristol/notebooks/01_eda_london_bristol.ipynb). Review [findings](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/eda/london-bristol/docs/eda_findings.md), [column profile](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/eda/london-bristol/docs/eda_profile.md) and [cleaning specification](https://github.com/DanyloKuryliak/airbnb-price-analytics/blob/eda/london-bristol/docs/cleaning_specification.md).
2. Agree the contract. Person 2 implements one pipeline parameterized by city: immutable Bronze files, typed/flagged Silver records and Gold aggregates/features.
3. Person 3 reserves a per-city test set before model selection, fits preprocessing and room-type/accommodates median baselines on training rows only, evaluates MAE in GBP for each city and combined, and writes per-listing predictions to Gold.
4. Freeze successful A/B pipeline/model versions at the end of Week 1. Record all release evidence in the [holdout protocol](reports/city_c_protocol.md).
5. In Week 2, run the unchanged pipeline/model on Greater Manchester and record first-run failures and metrics before fixes. Classify subsequent changes and compare results.
6. Person 4 delivers city overview, A/B comparison and model-diagnostics dashboard pages plus a Genie Agent grounded on Gold tables. Add transfer findings after the locked first run.

No paid infrastructure, APIs or external managed services are required. Free Edition quotas apply; do not upgrade to a paid trial or create classic clusters to bypass limits.

## Submission links

The team admin submits the repository link. The repository is private until access requirements are confirmed.

| Artifact | Location |
| --- | --- |
| Repository | https://github.com/DanyloKuryliak/airbnb-price-analytics |
| EDA | `notebooks/01_eda_london_bristol.ipynb` |
| ETL and architecture | Person 2 deliverable pending |
| Price model and test metrics | Person 3 deliverable pending |
| Dashboard and Genie | Person 4 links pending |
| Third-city first run | Locked; protocol in `reports/city_c_protocol.md` |
| Presentation | Final PDF or share link pending |
