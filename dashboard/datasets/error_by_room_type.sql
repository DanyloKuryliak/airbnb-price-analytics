-- Page 3. Error by room type.
SELECT city_name, model_version, segment AS room_type, evaluated_listings, model_mae_gbp,
       baseline_mae_gbp, mean_signed_error_gbp, under_priced_share_pct
FROM workspace.airbnb_gold.v_model_error_segments
WHERE segment_type = 'room_type'
ORDER BY city_name, model_mae_gbp DESC
