
# Databricks ETL Job

**Job:** airbnb-price-analytics-etl  
**Compute:** Serverless  
**Execution:** Manual

The ETL job uses one notebook with two sequential tasks:

| Task | City | Depends on |
|---|---|---|
| etl_london | london | — |
| etl_bristol | bristol | etl_london |

Both tasks use `write_tables=true`.

The job successfully processed both cities on November 10, 2026.
