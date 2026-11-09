# Third-city execution protocol

Status: locked. No third-city source file has been acquired or inspected.

## Release gate

After validation of the A/B pipeline and model, the ETL and ML owners record and approve:

1. A/B pipeline commit and successful job run identifiers.
2. Frozen model artifact, feature allowlist, environment and fitted preprocessing.
3. Persistent A/B train/test assignments and training-only baseline statistics.
4. London, Bristol and combined baseline/model test MAE and prediction coverage.
5. Source manifests and checksums; an immutable release tag referencing the frozen code.

Only after this gate may the latest Greater Manchester detailed listings snapshot be discovered and acquired. Record its actual source date and URL then; they remain deliberately unspecified before release.

## First-run evidence

Record the frozen versions, run identifier, timestamps, input checksum, pipeline status, exact failures, rows loaded, eligible targets, prediction coverage, City C baseline MAE and unchanged A/B-model MAE. Save this record before editing code or the model. If a failure prevents MAE, record it as unavailable with the cause; never substitute a repaired run as the first run.

## Change log

For each subsequent change, record its classification (pipeline fix or model change), reason, code/model version and rerun identifier. Compare baseline City C, A/B test MAE, first-run City C MAE and after-change City C MAE, with denominators. Report changes in evaluated coverage. Never overwrite first-run results or retune on the original A/B test set.
