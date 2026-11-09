# Shared Databricks project

Team entry point: `/Workspace/Shared/airbnb-price-analytics` in the existing Free Edition workspace. All four contributors use the same workspace hostname after invitation. GitHub is managed through `gh` and local Git; Databricks Git integration is optional.

| Location | Purpose |
| --- | --- |
| `00_team_start` | Team navigation and execution rules |
| `00_project/` | Shared setup and integration notebooks |
| `01_eda_london_bristol` | Person 1 EDA, already executed |
| `02_etl/` | Person 2 pipeline and architecture |
| `03_model/` | Person 3 baseline, training and evaluation |
| `04_dashboard/` | Person 4 dashboard support artifacts |
| `05_genie/` | Person 4 Genie support artifacts |
| `06_reports/` | Reviewed aggregate outputs and transfer evidence |

`workspace.airbnb_bronze`, `workspace.airbnb_silver` and `workspace.airbnb_gold` reserve team lakehouse namespaces. No production tables have been implemented. Existing A/B source files remain in `workspace.airbnb_eda.raw` and aggregate EDA outputs in `workspace.airbnb_eda.artifacts`; the ETL owner can read these pinned files through configurable input paths.

See `docs/setup_databricks.md` for invitations, separate notebook/data permissions, import/export and access checks. `eda_validation_run.json` is an EDA validation run specification, not the production ETL pipeline.
