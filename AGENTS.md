# Codex Instructions — Airbnb Price Analytics (Team Вишня)

## Mission
Set up a reproducible, collaborative GitHub + Databricks Free Edition project for **Group Assignment 2**. The team builds an Airbnb data lakehouse and price-prediction workflow for two UK locations, then tests transfer to a third unseen location.

- **Team:** Вишня
- **Region / currency:** United Kingdom / GBP (£)
- **City A:** London
- **City B:** Bristol
- **Holdout City C:** Greater Manchester (sometimes called Manchester in team shorthand)
- **Current user:** Person 1 — Exploratory Data Analysis (EDA) and data quality
- **Other owners:** Person 2 — medallion architecture and parameterized ETL; Person 3 — baseline and ML price model; Person 4 — AI/BI dashboard and Genie Agent.
- **Platform:** Databricks Free Edition, zero-cost only.

## Critical constraints
1. **DO NOT download, open, sample, profile, query, or otherwise inspect City C data** until both the City A/B pipeline and price model are finished and their initial versions are frozen at the end of Week 1. Do not create Manchester tables as part of setup. City C's first run must use the **unchanged** A/B pipeline and model, and its results must be recorded before any fixes.
2. Use the **latest available Inside Airbnb snapshot** per city at execution time, and the **detailed `listings.csv.gz`**, not the summary `listings.csv`. Record each actual snapshot date and data source URL in README. Never assume a particular date is current without verifying.
3. One row is one listing snapshot. Keep original raw inputs unchanged. Never overwrite raw source data.
4. No paid cloud features. Do not provision billable infrastructure, paid APIs, or external managed services.
5. Do not commit raw datasets, large generated tables, credentials, Databricks tokens, `.env` files, or personally identifying host/listing fields to GitHub. Use `.gitignore` and placeholders in docs. Avoid unnecessary display/export of personal data.
6. Do not ask for or paste secrets into terminal transcripts, notebook source, logs, or prompts. Prefer Databricks built-in Git integration and authenticated user interfaces.
7. Inspect existing repository/files before creating or replacing anything. Never destructively reset, delete, or overwrite teammates' work. Make small, reviewable changes.
8. If external login, workspace invites, repo creation, Git linking, or permissions cannot be completed automatically, prepare precise manual steps and stop at that boundary. Do not claim the service is configured unless verified.

## Collaboration model
- **GitHub:** one shared repository is the source of truth for notebook/code version control and final submission.
- **Databricks:** execution environment for data, notebooks, lakehouse tables, dashboard, and Genie. First determine whether all four can access the **same** workspace; if not, document a separate-workspace approach with reproducible imports and common table naming.
- Prefer Databricks Git folders if available in the team's Free Edition account; verify feature availability rather than assuming it.
- Use `main` for reviewed work and feature branches: `eda/london-bristol`, `etl/pipeline`, `ml/price-model`, `bi/dashboard-genie`. Pull before editing, use pull requests or reviews to merge.
- Keep notebooks source-controlled in an interoperable supported format (`.ipynb` if workable), with limited outputs and no embedded data.
- Agree with the team on catalog/schema/table names, column contracts, and storage paths before creating dependencies. Document choices in `docs/data_contract.md`.

## First task: create a minimal scaffold
If the repository is empty, create this structure (adapt to any existing conventions):

```text
airbnb-price-analytics/
├── AGENTS.md
├── README.md
├── .gitignore
├── requirements.txt
├── notebooks/
│   ├── 01_eda_london_bristol.ipynb
│   ├── 02_etl.ipynb                # placeholder / owned by Person 2
│   └── 03_price_model.ipynb        # placeholder / owned by Person 3
├── src/
│   └── __init__.py
├── docs/
│   ├── setup_databricks.md
│   ├── data_contract.md
│   └── eda_findings.md
├── dashboard/                     # Person 4 artifacts/docs
├── genie/                         # Person 4 instructions/questions
└── reports/                       # City C run log and final slides later
```

Do not create fake completed notebooks for teammates. Empty directories may use `.gitkeep`.

README must summarize objective, roles, actual dataset sources/snapshot dates (use `TBD` until checked), zero-cost environment, reproducible setup, execution order, holdout protocol, and submission link structure.

`.gitignore` should cover `.env*`, local credentials, `data/`, `*.csv`, `*.csv.gz`, `*.parquet`, `*.delta`, checkpoints, large notebook outputs, Python caches, `.venv/`, `.DS_Store`; do not accidentally ignore README, notebooks, or docs. Add explicit exceptions as necessary.

## Person 1 deliverable: reproducible EDA notebook
Focus on **London and Bristol only**. Build a separately runnable notebook that:

1. Starts with a **short findings/unknowns summary**, clearly marked as pending until analysis runs.
2. Documents data source URLs, snapshot dates, data grain, and listing counts by city.
3. Profiles used columns: names/types, counts, null rates and **patterns** of missingness, price and availability distributions, and potential extreme values.
4. Reads and parses prices carefully, including currency symbols and thousands separators; checks for zero, negative, missing, and implausible prices without silently deleting rows.
5. Presents meaningful city comparisons (price, availability, room type, accommodates, neighbourhoods, review scores where available). Label units GBP and identify aggregations.
6. Documents each proposed cleaning/transformation rule, its rationale, and the impact in rows/values. **Recommend** pipeline behavior to Person 2; avoid duplicating the production ETL implementation in the EDA notebook.
7. Audits **price leakage**: list features derived from the advertised target price or unavailable at prediction time; justify exclusions explicitly. Examine price-derived fields and related monetary columns carefully instead of blindly retaining them.
8. Produces a compact markdown findings report in `docs/eda_findings.md` and hands Person 2 a cleaning specification and Person 3 a proposed safe feature list.
9. Keeps transformations, plot generation, and summaries reproducible. Favor pandas/PySpark already supported by Databricks; avoid installing unnecessary dependencies.
10. Does not invent findings or metric values. If data can't be accessed, leave runnable scaffold/TODOs and explain the blocker.

### Suggested EDA sections
- Summary: what we know / don't know
- Dataset and provenance
- Schema and data grain
- Missingness and missingness patterns
- Price / availability distributions
- Outliers and classification criteria
- Segment comparisons (city, room type, guests, neighbourhood)
- Cleaning and transformation specification
- Leakage review and allowed/excluded features
- Handoff to ETL and ML owners

## Team integration / interfaces
- **Person 2:** medallion layers: raw files in Bronze; typed, cleaned listings in Silver; metrics/features/predictions in Gold. One ETL job/pipeline parametrized by city; no city-specific code copies.
- **Person 3:** price target = nightly advertised `price` in GBP on snapshot date. Hold out a test set (e.g. 20% per city) **before model selection**. Baseline = training-data median price for same `room_type` and `accommodates`. Report MAE for London, Bristol, and combined using the held-out test sets. Persist per-listing predictions to Gold.
- **Person 4:** at least three dashboard pages: city overview, A/B comparison, model diagnostics; Genie Agent grounded on Gold tables with instructions and example questions.
- **Week 2 City C:** after Week 1 freeze, run **unchanged** pipeline/model on Greater Manchester; capture failures/first-run MAE; distinguish pipeline fixes from model changes; report baseline C, A/B model MAE, and first-run/after-change C MAE. Update dashboard and presentation afterward.

## Recommended execution sequence for Codex
1. Inspect repository and environment. Report what already exists and the few missing prerequisites.
2. If useful, create or update the scaffold/README/.gitignore and document the collaboration workflow. Avoid changing others' files.
3. Draft `docs/setup_databricks.md` with manual actions for Free Edition access, workspace sharing/permissions where supported, GitHub connection, data upload/storage, notebook import/run, and how to check access.
4. Scaffold and implement **only Person 1's** EDA notebook against London/Bristol inputs and provide configurable input paths/table names rather than hard-coded user-specific workspace paths.
5. If the actual A/B datasets are available, execute EDA, validate counts/plots, document real findings and cleaning rules. Otherwise provide exact next steps for attaching them.
6. Run low-cost local validation where possible (syntax/imports, notebook JSON validity, no secrets or City C references in executable ingestion code), and present changed files plus unresolved steps.
7. Commit or push only when explicitly authorized and authenticated. Do not manufacture evidence of successful runs.

## Definition of done for Person 1
- [ ] London/Bristol detailed listings snapshots and dates recorded
- [ ] Reproducible EDA notebook runs in Databricks Free Edition
- [ ] Dataset grain/counts/schema documented
- [ ] Missingness rates and patterns explained
- [ ] Price/availability distributions and outliers investigated
- [ ] Cleaning and transformation rules with reasons shared with Person 2
- [ ] Leakage exclusions and safe candidate features shared with Person 3
- [ ] Short findings/unknowns summary at top of notebook
- [ ] No Greater Manchester data inspected before freeze
- [ ] Source-controlled files, setup instructions, README, and no sensitive/large data committed

## Working style
Be practical, concise, and explicit. Prioritize a **working, reproducible minimum** over decorative extras. Distinguish completed actions from proposals. Ask for human input only where permissions, actual configuration, or inaccessible data make it indispensable.
