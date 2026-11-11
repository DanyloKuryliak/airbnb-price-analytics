-- Page 1. One row per city: headline metrics with denominators.
SELECT city_name, snapshot_date, total_listings, valid_price_listings, price_coverage_pct,
       median_price_gbp, mean_price_gbp, median_availability_365, avg_review_score,
       review_listings, distinct_hosts, listings_per_host, entire_home_share_pct, neighbourhoods
FROM workspace.airbnb_gold.v_city_overview
ORDER BY total_listings DESC
