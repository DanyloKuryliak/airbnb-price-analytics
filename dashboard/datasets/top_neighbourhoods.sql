-- Page 1. Ten most expensive neighbourhoods per city (at least 10 valid prices each).
SELECT city_name, neighbourhood, median_price_gbp, valid_price_listings, listings, price_rank_in_city
FROM workspace.airbnb_gold.v_neighbourhood_prices
WHERE price_rank_in_city <= 10
ORDER BY city_name, price_rank_in_city
