-- Page 3. Ten neighbourhoods per city with the highest model MAE (at least 20 evaluated listings).
SELECT city_name, model_version, run_label, segment AS neighbourhood, evaluated_listings, model_mae_gbp,
       mean_signed_error_gbp, median_actual_price_gbp
FROM workspace.airbnb_gold.v_model_error_segments
WHERE segment_type = 'neighbourhood' AND evaluated_listings >= 20
QUALIFY ROW_NUMBER() OVER (PARTITION BY city_name, model_version, run_label, pipeline_version
                           ORDER BY model_mae_gbp DESC) <= 10
ORDER BY city_name, model_mae_gbp DESC
