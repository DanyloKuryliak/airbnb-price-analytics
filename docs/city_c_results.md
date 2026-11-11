# Greater Manchester: transfer results

Model version `v1` (frozen), scored with `03_predict` (`run_label = first_run`) and analysed in `05_city_c`. Prices are nightly advertised GBP amounts. One row is one listing snapshot.

## Summary

The frozen model transferred to Greater Manchester without any failure and predicted every listing. Its MAE on Manchester is **£79.68**, close to its London and Bristol test MAE of **£76.93** and **21.0%** lower than the baseline's £100.84. Median absolute error, however, rises by a third, from **£32.31** to **£43.38**. The model overprices Manchester: the median listing is predicted £31.80 too high, and the overpricing grows with guest capacity. Raw coordinates are the model's only source of a city's price level, and every Manchester listing lies outside the training coordinates. A model change that replaced coordinates with distance to the city centre was tested and rejected by cross-validation; `v1` remains the final model.

## First run

The first run used the frozen `v1` package unchanged: model, baseline statistics, category lists and feature allowlist from [model_v1_manifest.json](model_v1_manifest.json). Package checksums and the check set were verified before scoring. No step failed and no listing failed to score.

| Item | Value |
| --- | --- |
| Rows loaded | 7,799 |
| Listings with a valid price (evaluated) | 6,692 (85.8%) |
| Listings without a valid price (scored, not evaluated) | 1,107 |
| Prediction coverage | 100% |
| Baseline level used | group 7,797; room type 2; global 0 |
| Property type mapped to `Other` | 84 listings, for example "Shared room in home" (14), "Barn" (9), "Private room in cottage" (9), "Entire vacation home" (8), "Camper/RV" (7) |
| Missing inputs | `beds` 210, `minimum_nights` 32, `maximum_nights` 32, `bathrooms` 15, `bedrooms` 5 |

Results are stored in `workspace.airbnb_gold.model_metrics` (`dataset = 'city_c_first_run'`) and `workspace.airbnb_gold.predictions` (`run_label = 'first_run'`). The stored values were recomputed in `05_city_c` and match this record.

## Transfer results

| data | evaluated listings | baseline MAE | baseline median AE | model MAE | model median AE |
| --- | --- | --- | --- | --- | --- |
| London + Bristol test | 12,434 | 104.17 | 44.84 | **76.93** | 32.31 |
| Greater Manchester first run | 6,692 | **100.84** | 73.50 | **79.68** | 43.38 |

The three required comparisons are shown in bold: City C baseline MAE £100.84, A/B test model MAE £76.93 and City C model MAE £79.68. On Manchester the model is 21.0% below the baseline in MAE and 41.0% below it in median absolute error. Against its own A/B test result, model MAE is £2.75 (3.6%) higher and median absolute error £11.07 (34.3%) higher.

## Diagnosis

Manchester first-run rows with a valid price are compared with London and Bristol test rows.

### Manchester is cheaper and overpriced

| city | median price | median signed error (predicted − actual) | listings overpriced |
| --- | --- | --- | --- |
| Greater Manchester | £117 | +£31.80 | 78.3% |
| Bristol | £134 | +£1.41 | 51.7% |
| London | £176 | +£4.64 | 54.7% |

The model is close to unbiased in both training cities but overprices most Manchester listings. Manchester's median signed error (£31.80) is close to its median absolute error (£43.38), so most of the typical error is in one direction.

### Overpricing grows with capacity

| guests | Manchester median signed error |
| --- | --- |
| 1 | +£12.55 |
| 2 | +£13.98 |
| 3–4 | +£41.56 |
| 5–6 | +£76.42 |
| 7 or more | +£132.38 |

In London and Bristol the median signed error stays within about £11 in every capacity band. This is consistent with the model applying the training cities' price premium for larger listings to Manchester, where it is smaller.

### Manchester lies outside the training coordinates

All Manchester listings are outside the training latitude range: 53.336–53.665 against a training maximum of 51.681. Their longitudes lie mostly inside Bristol's range. A tree model treats a value beyond the training range like the nearest edge, so the model places Manchester listings at the northern edge of the training data, in a latitude and longitude combination that does not occur in London or Bristol.

### Unseen property types are not the main problem

Only 78 evaluated listings have a property type outside the model's categories, and their error is similar to that of known types.

## Changes

Each candidate change is classified as a pipeline fix (how data are ingested or cleaned) or a model change (features, preprocessing, training or model).

| # | Change | Type | Decision |
| --- | --- | --- | --- |
| 1 | Check the parsing of `beds` and other inputs with missing values for Manchester | pipeline fix | Not implemented; missing values do not explain a bias that grows with capacity. To check with the ETL owner. |
| 2 | Flag placeholder-like prices (about £5,000 or £10,000 a night) in the cleaning rules | pipeline fix | Not implemented; the Manchester problem is a shift of typical listings, not a few outliers. |
| 3 | Replace latitude and longitude with distance to the city centre | model change | Tested as `v2`; rejected by cross-validation. |
| 4 | Group property types into broader families | model change | Rejected without testing; few affected listings and similar error. |
| 5 | Weight London and Bristol equally in training | model change | Tested with change 3; rejected by cross-validation. |
| 6 | Predict a city-relative price and rescale with the city's median price | model change | Not implemented; needs Manchester price information, which the holdout design excludes. |

### Model change test

Changes 3 and 5 were tested as candidate `v2` with the same split, baseline and selection rule as `v1`: pooled 5-fold cross-validated MAE in GBP on London and Bristol training rows only. The centre of each city was the median latitude and longitude of its listings, computed without prices. Neither the A/B test set nor Manchester prices were used, and `v2` was not frozen.

| candidate | bristol | london | combined |
| --- | --- | --- | --- |
| **`v1` (frozen): coordinates, gradient boosting lr=0.05, 63 leaves** | **41.20** | **85.70** | **84.08** |
| `v2` distance to centre, best gradient boosting (lr=0.1, 63 leaves) | 106.74 | 90.93 | 91.51 |
| `v2` distance to centre, other unweighted settings | — | — | 91.77–91.94 |
| `v2` distance to centre, city-weighted gradient boosting (4 settings) | 53.19–55.58 | 99.68–101.41 | 98.07–99.66 |
| `v2` distance to centre, Ridge | 107.30 | 101.86 | 102.06 |

No `v2` variant beats `v1`. `city` is not a model feature, so in `v1` the coordinates also identify the city and with it the price level. Distance to the centre has the same meaning in every city and removes that information: Bristol is priced like London, and its error rises from £41 to £107. London loses less (£85.70 to £90.93), because distance keeps part of the location effect within a city. Equal city weights lower Bristol's error to about £53–56 at the cost of London (about £100–101) and remain worse than `v1` overall.

No change was applied, so there is no `after_pipeline_fix` or `after_model_change` run; the first run is the final Manchester result.

## Why the gap

- **The typical error grows; the mean hides it.** Model MAE rises by only 3.6%, but median absolute error by 34.3%. The A/B MAE includes a few extreme London prices that account for about 13% of London's absolute error ([model results](model_results.md)), while Manchester's prices are lower, so the mean understates the change for the typical listing. Relative to the median price, the median absolute error is about 37% in Manchester (£43.38 of £117), against about 19% in London (£32.88 of £176) and 15% in Bristol (£19.71 of £134).
- **The model cannot know Manchester's price level.** The model learns each city's price level from its coordinates. Manchester's coordinates are outside the training range, so it receives a level from the edge of London and Bristol, which is too high, especially for larger listings. The `v2` test shows the same mechanism from the other side: without coordinates, the model cannot tell Bristol's level from London's.
- **The model still adds value.** The listing attributes still carry information in a new city: the model's median absolute error is 41.0% below the baseline's. The baseline uses pooled training medians (96.4% London) and has no location information at all, so its median error rises more (£44.84 to £73.50).

## Limitations

- One snapshot per city and one Manchester run. Manchester results compare all its valid-price listings with the 20% A/B test sample.
- The changes were proposed after inspecting Manchester errors. The `v2` decision used only A/B training-row cross-validation, but any future Manchester rerun would no longer be an unseen-city estimate.
- Correcting the price level needs Manchester price information, for example a labelled sample or an external price index. This would end Manchester's role as an unseen holdout and is not done here.
- Parsing of the missing Manchester inputs (change 1) has not been checked against the source file.
- Prices are advertised nightly prices, not transaction prices.

## Technical evidence

[Prediction notebook](../notebooks/03_predict.ipynb), [transfer analysis](../notebooks/05_city_c.ipynb) (both output-free in the repository), metrics in `workspace.airbnb_gold.model_metrics` (`model_version = 'v1'`, `dataset = 'city_c_first_run'`), predictions in `workspace.airbnb_gold.predictions` (`run_label = 'first_run'`), [holdout protocol](../reports/city_c_protocol.md), [model results](model_results.md), [freeze manifest](model_v1_manifest.json).
