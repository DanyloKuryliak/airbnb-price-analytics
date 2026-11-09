# Databricks configuration

`eda_validation_run.json` defines a serverless execution of the London/Bristol EDA notebook. Input and output roots are notebook parameters.

The EDA uses `workspace.airbnb_eda.raw` for immutable inputs and `workspace.airbnb_eda.artifacts` for aggregate outputs. The lakehouse namespaces `workspace.airbnb_bronze`, `workspace.airbnb_silver` and `workspace.airbnb_gold` are reserved for the ETL and modelling components. No production tables are implemented.

See [execution configuration](../docs/setup_databricks.md) and [data contract](../docs/data_contract.md) for paths, column interfaces and evaluation restrictions.
