# Version control and component ownership

GitHub stores versioned source, configuration, aggregate findings and submission artifacts. Databricks provides notebook execution and governed data storage.

| Branch | Scope |
| --- | --- |
| `main` | Integrated project source |
| `eda/london-bristol` | Person 1: EDA, data quality and leakage review |
| `etl/pipeline` | Person 2: medallion architecture and parameterized ETL |
| `ml/price-model` | Person 3: baseline, model and evaluation |
| `bi/dashboard-genie` | Person 4: dashboard and Genie Agent |

Person 1's EDA is integrated into `main`. The other components remain under development. Changes to table contracts require coordination with dependent component owners.

## Contribution procedure

Synchronize with `main`, implement changes on the relevant branch, run the applicable validation, and integrate through a pull request. Do not overwrite another contributor's work. Notebook exports must have cleared outputs before commit. Raw datasets, personally identifying fields and credentials are excluded from version control.

Local Git and the GitHub CLI support repository operations. Databricks Git integration is optional. Import/export notebooks as Jupyter files, compare versions before replacing an existing object, and retain execution evidence separately from output-free source.
