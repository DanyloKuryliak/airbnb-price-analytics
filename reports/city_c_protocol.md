# Third-city execution protocol

Status: first run completed with frozen model `v1`; no correction applied. Greater Manchester remains scored only by the unchanged A/B artifacts.

## Release gate

After validation of the A/B pipeline and model, the ETL and ML owners record and approve:

1. A/B pipeline commit and successful job run identifiers.
2. Frozen model artifact, feature allowlist, environment and fitted preprocessing.
3. Persistent A/B train/test assignments and training-only baseline statistics.
4. London, Bristol and combined baseline/model test MAE and prediction coverage.
5. Source manifests and checksums; an immutable release tag referencing the frozen code.

Only after this gate may the latest Greater Manchester detailed listings snapshot be discovered and acquired. Record its actual source date and URL then; they remain deliberately unspecified before release.

### Release record

| Item | Record |
| --- | --- |
| A/B pipeline commit and job runs | _To be added by the ETL owner._ |
| Model and prediction code | Commit `a25e78c` (`notebooks/03_price_model.ipynb`, `notebooks/03_predict.ipynb`) |
| Frozen model | `v1`, package `/Volumes/workspace/airbnb_eda/artifacts/models/v1/`: `model.joblib`, `baseline_stats.json`, `check_set.json`, `manifest.json` with file checksums |
| Feature allowlist, category lists, environment | [docs/model_v1_manifest.json](../docs/model_v1_manifest.json): feature version `v1`, 10 features, scikit-learn 1.7.2, Python 3.12.3 |
| Split and baseline | `workspace.airbnb_gold.features.split` (seed 42, 20% test per city, stratified by room type); baseline statistics in the package |
| A/B test results | Baseline MAE £104.17, model MAE £76.93 (combined, 12,434 listings, coverage 100%); per city in [docs/model_results.md](../docs/model_results.md) |
| A/B source manifests | London 2026-09-17 and Bristol 2026-09-22 snapshots with SHA-256 checksums in the model manifest |
| Release tag | _To be added by the ETL owner._ |

## First-run evidence

Record the frozen versions, run identifier, timestamps, input checksum, pipeline status, exact failures, rows loaded, eligible targets, prediction coverage, City C baseline MAE and unchanged A/B-model MAE. Save this record before editing code or the model. If a failure prevents MAE, record it as unavailable with the cause; never substitute a repaired run as the first run.

### First-run record

| Item | Record |
| --- | --- |
| City | `greater-manchester` |
| Source snapshot date | 2026-09-22 |
| Source URL | `https://data.insideairbnb.com/united-kingdom/england/greater-manchester/2026-09-22/data/listings.csv.gz` |
| Input checksum (SHA-256) | `759c3f498722a536ae7c498adf57774b7dd43239db8c94d5e75e7f12dcb45ce6` (`model_metrics.source_sha256`) |
| Run identifier | Interactive Databricks notebook run of `03_predict`; no job run ID |
| Run timestamp | 2026-11-11T20:06:51Z (`model_metrics.generated_at`) |
| Versions | Model `v1`, feature version `v1`, `03_predict` with `run_label = first_run`, `write_tables = true` |
| Pipeline status | Completed. Package checksums and check set verified; no step failed |
| Failures | None |
| Rows loaded | 7,799 |
| Eligible targets (valid price) | 6,692 |
| Prediction coverage | 100% (baseline and model) |
| Baseline MAE / median AE | £100.84 / £73.50 |
| Model MAE / median AE | £79.68 / £43.38 |
| Inputs | 84 listings with a property type mapped to `Other`; missing `beds` 210, `minimum_nights` 32, `maximum_nights` 32, `bathrooms` 15, `bedrooms` 5; baseline level group 7,797, room type 2 |

Stored in `workspace.airbnb_gold.model_metrics` (`dataset = 'city_c_first_run'`) and `workspace.airbnb_gold.predictions` (`run_label = 'first_run'`). Diagnosis and comparison with the A/B test rows: [docs/city_c_results.md](../docs/city_c_results.md).

## Change log

For each subsequent change, record its classification (pipeline fix or model change), reason, code/model version and rerun identifier. Compare baseline City C, A/B test MAE, first-run City C MAE and after-change City C MAE, with denominators. Report changes in evaluated coverage. Never overwrite first-run results or retune on the original A/B test set.

| # | Change | Classification | Reason | Version / rerun | Outcome |
| --- | --- | --- | --- | --- | --- |
| 1 | Check parsing of `beds` and other inputs with missing values | Pipeline fix | 210 listings lack `beds` | None | Not implemented; missing values do not explain the capacity-dependent bias |
| 2 | Flag placeholder-like prices (about £5,000 or £10,000) | Pipeline fix | Largest A/B test errors | None | Not implemented; the City C error is a shift of typical listings |
| 3 | Replace latitude/longitude with distance to the city centre | Model change | All City C latitudes are outside the training range; median signed error +£31.80, growing with capacity | Candidate `v2`, not frozen; no rerun | Rejected: pooled CV MAE £91.51 (best) vs £84.08 for `v1`; Bristol £106.74 vs £41.20 |
| 4 | Group property types into families | Model change | 84 listings mapped to `Other` | None | Rejected without testing: 78 evaluated, error similar to known types |
| 5 | Equal city weights in training | Model change | London is 96.4% of training rows | Tested within `v2`; no rerun | Rejected: pooled CV MAE £98.07–99.66 |
| 6 | City-relative price target | Model change | City C price level differs | None | Not implemented: needs City C price information |

Model selection used pooled 5-fold cross-validation on A/B training rows only; neither the A/B test set nor City C prices were used. No change was applied, so no after-change City C run exists, and the first run remains the City C result for `v1`.

| Comparison | Evaluated listings | MAE | Median AE |
| --- | --- | --- | --- |
| City C baseline (first run) | 6,692 | £100.84 | £73.50 |
| A/B test model `v1` | 12,434 | £76.93 | £32.31 |
| City C model `v1` (first run) | 6,692 | £79.68 | £43.38 |
| City C after change | — | Not run | Not run |
