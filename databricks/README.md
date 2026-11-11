# Databricks configuration

`eda_validation_run.json` defines a serverless execution of the London/Bristol EDA notebook. Input and output roots are notebook parameters.

The EDA uses `workspace.airbnb_eda.raw` for immutable inputs and `workspace.airbnb_eda.artifacts` for aggregate outputs. The lakehouse namespaces `workspace.airbnb_bronze`, `workspace.airbnb_silver` and `workspace.airbnb_gold` are reserved for the ETL and modelling components. No production tables are implemented.

See [execution configuration](../docs/setup_databricks.md) and [data contract](../docs/data_contract.md) for paths, column interfaces and evaluation restrictions.



## Running the ETL Pipeline for City C

The ETL pipeline supports Greater Manchester through the same parameterized notebook used for London and Bristol.

### 1. Source files

The following files must be available in Databricks:

**Manifest:**

`/Volumes/workspace/airbnb_eda/raw/sources.json`

**Greater Manchester dataset:**

`/Volumes/workspace/airbnb_eda/raw/data/raw/greater-manchester/2026-09-22/listings.csv.gz`

The manifest must contain the Greater Manchester source entry with the correct snapshot date and SHA-256 checksum.

### 2. Notebook parameters

Open `02_etl_pipeline` in Databricks.

For a dry run, use:

| Parameter | Value |
|---|---|
| `city` | `greater-manchester` |
| `write_tables` | `false` |
| `pipeline_version` | `etl-v1` |

For a run that writes the tables, set:

`write_tables = true`

The original London/Bristol Job does not need to be rerun when processing Greater Manchester.

### 3. Validate Gold features

After the ETL run, execute:

```sql
SELECT
    city,
    feature_version,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN split IS NULL THEN 1 ELSE 0 END) AS null_splits
FROM workspace.airbnb_gold.features
WHERE city = 'greater-manchester'
GROUP BY city, feature_version;
```

Expected results from the first successful City C run:

- `feature_version = 'v1'`
- `total_rows = 7799`
- `null_splits = 7799`

### 4. Check existing A/B features

Run:

```sql
SELECT
    city,
    split,
    COUNT(*) AS rows_count
FROM workspace.airbnb_gold.features
WHERE city IN ('london', 'bristol')
GROUP BY city, split
ORDER BY city, split;
```

Compare the results with the A/B baseline documented in:

`docs/city_c_evaluation.md`

### 5. ML handoff

Greater Manchester features are stored in:

`workspace.airbnb_gold.features`

The ETL leaves `split = NULL` for the new city.

The ML team member is responsible for City C model evaluation and assigning the required split values.
