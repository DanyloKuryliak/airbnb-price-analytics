-- Values for widget titles that state a finding (scripts/build_dashboard.py, PENDING titles).
-- Run in SQL Editor after notebooks/04_bi_gold_views.ipynb; every title number must come from here,
-- docs/eda_audit.md, docs/model_results.md or docs/city_c_results.md.
SELECT 'A overview' AS section, city_name AS city, 'median available days' AS item,
       median_availability_365 AS value, CAST(NULL AS BIGINT) AS n
FROM workspace.airbnb_gold.v_city_overview
UNION ALL
SELECT 'A overview', city_name, 'listings per host', listings_per_host, distinct_hosts
FROM workspace.airbnb_gold.v_city_overview
UNION ALL
SELECT 'A overview', city_name, 'entire-home share %', share_pct, listings
FROM workspace.airbnb_gold.v_room_type_mix WHERE room_type = 'Entire home/apt'
UNION ALL
SELECT 'B London top-priced neighbourhoods', city_name, neighbourhood, median_price_gbp, valid_price_listings
FROM workspace.airbnb_gold.v_neighbourhood_prices WHERE city = 'london' AND price_rank_in_city <= 3
UNION ALL
SELECT 'C price-band share %', city_name, price_band, share_pct, listings
FROM workspace.airbnb_gold.v_price_bands WHERE city IN ('london', 'bristol')
UNION ALL
SELECT 'D Manchester MAE by room type', city_name, segment, model_mae_gbp, evaluated_listings
FROM workspace.airbnb_gold.v_model_error_segments
WHERE city = 'greater-manchester' AND segment_type = 'room_type' AND run_label = 'first_run'
UNION ALL
SELECT 'E Manchester MAE by neighbourhood (top 10)', city_name, segment, model_mae_gbp, evaluated_listings
FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY model_mae_gbp DESC) AS error_rank
      FROM workspace.airbnb_gold.v_model_error_segments
      WHERE city = 'greater-manchester' AND segment_type = 'neighbourhood' AND run_label = 'first_run'
        AND evaluated_listings >= 20)
WHERE error_rank <= 10
ORDER BY section, city, value DESC;
