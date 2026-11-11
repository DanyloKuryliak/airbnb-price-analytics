-- Page 3. Full metric table with denominators and coverage.
SELECT city_name, model_version, run_label, pipeline_version, evaluation_role, listings_in_set,
       prediction_coverage_pct, model_evaluated_listings, baseline_mae_gbp, model_mae_gbp,
       mae_improvement_gbp, mae_improvement_pct, baseline_median_abs_error_gbp, model_median_abs_error_gbp
FROM workspace.airbnb_gold.v_model_performance
ORDER BY model_version, run_label, evaluation_role, city_name
