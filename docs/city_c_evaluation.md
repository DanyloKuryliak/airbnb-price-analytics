
# City C Evaluation — Greater Manchester

## 1. Overview

This document describes the first ETL run on Greater Manchester (City C).

London (City A) and Bristol (City B) were used to develop and validate the original ETL pipeline. Greater Manchester was introduced later as a new, unseen city to test whether the same pipeline could process new data without city-specific cleaning changes.

The main goal was to reuse the existing Bronze, Silver, and Gold pipeline, record any problems, and check that the results for London and Bristol remained unchanged.

## 2. Frozen A/B Baseline

Before processing City C, the existing A/B ETL implementation was saved in Git.

- **Baseline commit:** `17ae179`
- **Commit message:** `Complete Databricks ETL pipeline and documentation`
- **Training cities:** London and Bristol
- **City C:** Greater Manchester

The original ETL cleaning rules and feature engineering logic were kept unchanged for City C.

The ML model is managed separately by the ML team member. Its frozen version and City C evaluation results should be documented in the ML section of the project.

### Gold features before City C

The following results were recorded on November 11, 2026, before running the pipeline for Greater Manchester.

| City | Train | Test | Inference | Total |
|---|---:|---:|---:|---:|
| Bristol | 1,808 | 453 | 671 | 2,932 |
| London | 47,924 | 11,981 | 32,049 | 91,954 |
| **Total** | **49,732** | **12,434** | **32,720** | **94,886** |

All London and Bristol records had a non-null `split` value.

The `inference` group contains records not assigned to the training or test split.

These values were saved as the baseline for checking whether City C processing affected the existing data.

## 3. City C Data Source

The new dataset was downloaded from Inside Airbnb.

| Property | Value |
|---|---|
| City | Greater Manchester |
| City identifier | `greater-manchester` |
| Snapshot date | `2026-09-22` |
| Source | Inside Airbnb |
| File | `listings.csv.gz` |
| Format | Compressed CSV |
| SHA-256 verification | Passed |

The dataset was registered in `sources.json`, following the same structure used for London and Bristol.

The repository validation and download scripts were updated to support the third city.

The source file was uploaded to the Databricks Volume:

`/Volumes/workspace/airbnb_eda/raw/data/raw/greater-manchester/2026-09-22/listings.csv.gz`

The source manifest was stored at:

`/Volumes/workspace/airbnb_eda/raw/sources.json`

Both files were checked in Databricks. The SHA-256 checksum matched the value recorded in the source manifest.

## 4. ETL Pipeline

The existing parameterized notebook was reused:

`02_etl_pipeline`

The following parameters were used for City C:

| Parameter | Value |
|---|---|
| `city` | `greater-manchester` |
| `write_tables` | `true` |
| `pipeline_version` | `etl-v1` |

The pipeline follows the same Medallion Architecture:

1. **Bronze:** Preserve the original source file and verify its checksum.
2. **Silver:** Apply the existing cleaning rules, data types, and quality checks.
3. **Gold:** Produce reusable features and aggregated metrics.

No Manchester-specific cleaning rules or new ML features were introduced.

## 5. Issue During the First Run

The initial City C run failed during the Bronze ingestion step.

The code used `os.link()` to create a hard link between a temporary source file and its final Bronze location.

This operation was not permitted by the Databricks Volume filesystem.

The error was:

`PermissionError: [Errno 1] Operation not permitted`

### Fix

The Bronze file-writing logic was updated to copy the source file without using `os.link()`.

The updated implementation:

- Does not overwrite an existing Bronze file.
- Checks the checksum of existing files.
- Copies a new file when needed.
- Verifies the SHA-256 checksum after copying.

This was a filesystem compatibility fix.

It did not change the Silver cleaning rules, Gold feature definitions, or ML model.

After this change, the ETL notebook completed the dry run and the subsequent run with table writes enabled.

## 6. City C ETL Results

The pipeline successfully processed Greater Manchester and wrote its features to:

`workspace.airbnb_gold.features`

### Gold features validation

| Metric | Result |
|---|---:|
| City | `greater-manchester` |
| Snapshot date | `2026-09-22` |
| Feature version | `v1` |
| Total feature rows | 7,799 |
| Rows with `split IS NULL` | 7,799 |
| Rows with assigned split | 0 |

All 7,799 Greater Manchester feature rows were created with `feature_version = 'v1'`.

The `split` column was intentionally left NULL so that the ML team member could assign the appropriate split during City C evaluation.

The ETL did not train, retrain, or evaluate the ML model.

## 7. London and Bristol Validation After City C

After writing the Greater Manchester data, the existing Gold features for London and Bristol were checked again.

| City | Train | Test | Inference | Total |
|---|---:|---:|---:|---:|
| Bristol | 1,808 | 453 | 671 | 2,932 |
| London | 47,924 | 11,981 | 32,049 | 91,954 |
| **Total** | **49,732** | **12,434** | **32,720** | **94,886** |

All row counts and split distributions were identical to the values recorded before the City C run.

This confirms that the City C run did not change the number of A/B feature rows or their split distribution.

A full row-by-row comparison was not performed as part of this check.

## 8. Handoff to the ML Pipeline

Greater Manchester features are available in:

`workspace.airbnb_gold.features`

The ML pipeline should use the exact city identifier:

`greater-manchester`

The new records have:

- `feature_version = 'v1'`
- `split = NULL`

The ML team member is responsible for applying the frozen A/B model, assigning the required split values, generating predictions, and reporting City C evaluation metrics.

The City C ETL pipeline is complete. ML evaluation results should be documented separately after the frozen model has been evaluated.

## 9. Conclusion

The existing ETL pipeline successfully processed Greater Manchester as a new city.

The first run revealed a filesystem compatibility problem during Bronze ingestion. After fixing this technical issue, the pipeline completed without city-specific changes to cleaning rules or feature engineering.

A total of 7,799 feature rows were created for Greater Manchester. All rows have feature version `v1` and a NULL split, as required by the ML pipeline.

The existing London and Bristol feature counts and split distributions remained unchanged.

This confirms that the ETL pipeline can be reused for City C with the same data processing logic.
