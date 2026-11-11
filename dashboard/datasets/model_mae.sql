-- Page 3. Baseline and model MAE in GBP per city (long format for a grouped bar).
SELECT city_name, model_version, run_label, pipeline_version, evaluation_role,
       'Baseline: median by room type and guests' AS estimator,
       baseline_mae_gbp AS mae_gbp, baseline_evaluated_listings AS evaluated_listings
FROM workspace.airbnb_gold.v_model_performance
UNION ALL
SELECT city_name, model_version, run_label, pipeline_version, evaluation_role,
       'Model' AS estimator, model_mae_gbp AS mae_gbp, model_evaluated_listings AS evaluated_listings
FROM workspace.airbnb_gold.v_model_performance
ORDER BY city_name, estimator
