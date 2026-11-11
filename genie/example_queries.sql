-- Example SQL queries for the Genie Agent (Configure > SQL queries).
-- Each block title is the question; add it as the query title in Genie.
-- Namespace: workspace.airbnb_gold. Replace the catalog if your workspace uses another one.

-- Q1. What is the median price of entire homes in London?
SELECT city_name, snapshot_date, median_price_gbp, valid_price_listings, listings
FROM workspace.airbnb_gold.v_room_type_mix
WHERE city = 'london' AND room_type = 'Entire home/apt';

-- Q2. Which neighbourhoods in Bristol have the most listings?
SELECT neighbourhood, listings, valid_price_listings, median_price_gbp
FROM workspace.airbnb_gold.v_neighbourhood_prices
WHERE city = 'bristol'
ORDER BY listings DESC
LIMIT 10;

-- Q3. Where does the model under-price listings the most?
SELECT city_name, model_version, run_label, segment AS neighbourhood, evaluated_listings,
       mean_signed_error_gbp, under_priced_share_pct, model_mae_gbp
FROM workspace.airbnb_gold.v_model_error_segments
WHERE segment_type = 'neighbourhood' AND evaluated_listings >= 20 AND run_label = 'development'
ORDER BY mean_signed_error_gbp ASC
LIMIT 10;

-- Q4. How does the model compare with the baseline in each city?
SELECT city_name, model_version, run_label, evaluation_role, model_evaluated_listings,
       baseline_mae_gbp, model_mae_gbp, mae_improvement_gbp, mae_improvement_pct,
       baseline_median_abs_error_gbp, model_median_abs_error_gbp, prediction_coverage_pct
FROM workspace.airbnb_gold.v_model_performance
ORDER BY model_version, run_label, evaluation_role, city_name;

-- Q5. Which room types have the highest test-set MAE?
SELECT city_name, model_version, run_label, segment AS room_type, evaluated_listings, model_mae_gbp, baseline_mae_gbp
FROM workspace.airbnb_gold.v_model_error_segments
WHERE segment_type = 'room_type' AND evaluation_role = 'test'
ORDER BY model_mae_gbp DESC;

-- Q6. Compare London and Bristol on the main metrics.
SELECT metric, unit, city_name, value, difference_vs_reference, pct_difference_vs_reference
FROM workspace.airbnb_gold.v_city_comparison
ORDER BY metric_order, city_name;

-- Q7. What are the most expensive neighbourhoods in London?
SELECT neighbourhood, median_price_gbp, valid_price_listings
FROM workspace.airbnb_gold.v_neighbourhood_prices
WHERE city = 'london' AND rankable
ORDER BY price_rank_in_city
LIMIT 10;

-- Q8. How many days per year are listings available in each city?
SELECT city_name, snapshot_date, median_availability_365, avg_availability_365, availability_listings
FROM workspace.airbnb_gold.v_city_overview
ORDER BY city_name;

-- Q9. How does price change with the number of guests in Bristol?
SELECT guests, listings, valid_price_listings, median_price_gbp
FROM workspace.airbnb_gold.v_capacity_prices
WHERE city = 'bristol'
ORDER BY guests_order;

-- Q10. Which listings does the model over-price most in London?
SELECT model_version, run_label, listing_id, room_type, neighbourhood, accommodates,
       actual_price_gbp, predicted_price_gbp, model_error_gbp
FROM workspace.airbnb_gold.v_model_predictions
WHERE city = 'london' AND in_evaluation_set AND pricing_direction = 'over-priced'
ORDER BY model_error_gbp DESC
LIMIT 10;
