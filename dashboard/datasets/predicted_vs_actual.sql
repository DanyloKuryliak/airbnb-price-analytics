-- Page 3. Predicted against actual price on reported rows; prices above 1,000 GBP omitted for readability.
SELECT city_name, model_version, run_label, room_type, actual_price_gbp, predicted_price_gbp
FROM workspace.airbnb_gold.v_model_predictions
WHERE in_evaluation_set AND model_evaluable AND actual_price_gbp <= 1000
