# Databricks execution environment

## Configuration

The analysis uses Databricks Free Edition with serverless compute. Storage paths and notebook parameters are configurable; no paid infrastructure or external managed services are required.

| Resource | Object |
| --- | --- |
| Catalog | `workspace` |
| EDA inputs | `workspace.airbnb_eda.raw` |
| EDA aggregates | `workspace.airbnb_eda.artifacts` |
| Bronze namespace | `workspace.airbnb_bronze` |
| Silver namespace | `workspace.airbnb_silver` |
| Gold namespace | `workspace.airbnb_gold` |

Bronze, Silver and Gold schemas are provisioned. Production tables and dependent ETL/model workloads are not implemented. Required permissions are `USE CATALOG`, `USE SCHEMA` and the relevant volume/table privileges.

## Source layout

```text
/Volumes/workspace/airbnb_eda/raw/
├── sources.json
└── data/raw/
    ├── london/2026-09-17/listings.csv.gz
    └── bristol/2026-09-22/listings.csv.gz
```

`scripts/download_sources.py` verifies publication dates and SHA-256 checksums. Existing raw files are not replaced. Upload the files with the same relative paths before execution. The manifest permits London and Bristol only.

## Execution parameters

| Parameter | Default |
| --- | --- |
| `input_root` | `/Volumes/workspace/airbnb_eda/raw` |
| `output_root` | `/Volumes/workspace/airbnb_eda/artifacts` |

Execute `notebooks/01_eda_london_bristol.ipynb` in cell order on serverless compute. pandas and matplotlib are provided by the runtime; notebook-scoped installation is unnecessary.

The run specification `databricks/eda_validation_run.json` supports reproducible CLI execution:

```bash
databricks jobs submit --json @databricks/eda_validation_run.json --no-wait -p ucu
```

Check the returned run until it reaches a terminal state. Successful execution writes `eda_findings.md`, `eda_profile.md`, `eda_run.json` and two PNG figures. Only reviewed aggregate artifacts are version-controlled; raw records and notebook outputs are excluded.

## Execution evidence

Databricks run `279406330341406` completed successfully on 9 November 2026 using Python 3.11.10, pandas 1.5.3 and NumPy 1.23.5. Both source checksums passed. The analysis covered 91,954 London and 2,932 Bristol rows, with no raw rows removed. `docs/databricks_validation.json` records the validated notebook checksum; `docs/eda_run.json` records source and runtime provenance.

## References

- [Free Edition limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).
- [Files in Unity Catalog volumes](https://docs.databricks.com/aws/en/volumes/volume-files).
- [Unity Catalog privileges](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/).
