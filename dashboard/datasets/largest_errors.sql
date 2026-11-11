-- Page 3. Ten most under-priced and ten most over-priced listings per city. No host data.
SELECT city_name, model_version, run_label, pricing_direction, listing_id, room_type, neighbourhood,
       accommodates, actual_price_gbp, predicted_price_gbp, model_error_gbp, model_pct_error
FROM workspace.airbnb_gold.v_model_predictions
WHERE in_evaluation_set AND model_evaluable AND pricing_direction IN ('under-priced', 'over-priced')
QUALIFY ROW_NUMBER() OVER (PARTITION BY city_name, model_version, run_label, pipeline_version, pricing_direction
                           ORDER BY ABS(model_error_gbp) DESC) <= 10
ORDER BY city_name, pricing_direction, ABS(model_error_gbp) DESC
