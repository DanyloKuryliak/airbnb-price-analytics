# Cleaning and feature specification

Person 2 owns production implementation. Rule counts and missingness denominators are recorded in [EDA findings](eda_findings.md) and [column profile](eda_profile.md). EDA preserves every input row.

| Rule | Recommended behavior | Rationale and impact evidence |
| --- | --- | --- |
| Provenance | Preserve raw compressed bytes, source URL, checksum, published snapshot date and actual scrape date | Enables source reproduction; dates differ in both snapshots |
| Listing keys | Quarantine missing keys and duplicate city/ID/snapshot keys | Prevents ambiguous joins; counts in grain audit |
| Price parsing | Trim whitespace; validate currency context and comma grouping; parse decimal GBP; preserve raw value and failure flag | Dollar sign is a documented export artifact; malformed and missing values differ |
| Invalid targets | Retain rows; mark missing, malformed, zero and negative targets ineligible for supervised evaluation | No valid outcome is available; counts in quality audit |
| Extreme prices | Review positive prices below £10 or above £2,000; retain unless confirmed erroneous | London reaches £75,000; extremes are not proof of corruption |
| Statistical outliers | Treat city IQR fences as descriptive; fit any production thresholds on training rows only | Avoids tuning preprocessing on the reserved test set |
| Bathroom counts | Parse `bathrooms_text` into count and shared/private status; support decimal counts and half-baths; retain unknown status as null | Numeric bathroom fields are entirely missing; recovery audit counts supported strings |
| Missing attributes | Preserve nulls and indicators; fit any imputation on training data only | Absence is structured, especially review history and bathrooms |
| Capacity and rooms | Flag nonpositive/fractional accommodates, negative counts; retain zero bedrooms for studios | Avoids invalid categories and inappropriate deletion of studios |
| Availability | Validate integer counts within each horizon and monotonic 30/60/90/365-day counts | Calendar availability is not occupancy; counts in quality audit |
| Reviews | Validate rating scale 0–5; preserve missing scores, including listings without reviews | Absence does not imply a low score |
| Optional fields | Report absent columns and apply documented nullable defaults | Future-city schema differences must not require copied pipelines |
| Categorical fields | Trim text; keep unknown categories; do not fit vocabularies on test or holdout data | Third-city categories may be unseen |

## Safe initial predictors

Candidate predictors for an existing listing at the snapshot: `room_type`, `property_type`, `accommodates`, `bedrooms`, `beds`, parsed `bathrooms`, `latitude`, `longitude`, `minimum_nights`, `maximum_nights`. Derive bathroom counts from text rather than using the entirely missing numeric field. Use missing indicators and train-only imputation.

Omit `instant_bookable` and `neighbourhood_group_cleansed` from the initial model: both columns are entirely missing in both pinned snapshots. They cannot supply information through imputation.

Optional `city` and `neighbourhood_cleansed` need an explicit unseen-category strategy. Their usefulness may be limited for geographic transfer. Review history and superhost status require a defined prediction context; exclude them for cold-start listings.

## Excluded predictors

- `price` is the target, never a predictor.
- Every `price_quote_*` field, including raw payloads and quote dates, is excluded. Monetary quote amounts can reproduce or closely proxy the target; quote dates also reveal target-collection availability.
- `estimated_revenue_l365d` and all other price-derived revenue fields are excluded. Dividing revenue by estimated occupancy may reconstruct price; the aggregate audit measures this relationship.
- `review_scores_value` reflects perceived value relative to price and is excluded conservatively.
- Estimated occupancy and availability are excluded from the initial predictor list because they may encode demand responses to current pricing. They remain descriptive measures.
- IDs, names, URLs, descriptions, scrape metadata and personally identifying fields are excluded. No arbitrary newly added column is automatically admitted; use an explicit allowlist.

The latest downloaded files contain quotation and revenue columns beyond the fields described in the publicly readable data dictionary. Their precise estimation formulas remain unverified. Exclusion does not depend on assuming a particular formula.
