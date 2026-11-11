-- Page 3. Full metric table with denominators and coverage.
SELECT city_name, model_version, pipeline_version, evaluation_role, listings_in_set,
       prediction_coverage_pct, model_evaluated_listings, baseline_mae_gbp, model_mae_gbp,
       mae_improvement_gbp, mae_improvement_pct
FROM workspace.airbnb_gold.v_model_performance
ORDER BY model_version, evaluation_role, city_name
