-- Pages 1-2. Room-type share and median price per city.
SELECT city_name, room_type, listings, share_pct, valid_price_listings, median_price_gbp
FROM workspace.airbnb_gold.v_room_type_mix
ORDER BY city_name, listings DESC
