-- Page 2. Median price by guest capacity.
SELECT city_name, guests, guests_order, listings, valid_price_listings, median_price_gbp
FROM workspace.airbnb_gold.v_capacity_prices
ORDER BY guests_order, city_name
