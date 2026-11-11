-- Page 2. Share of valid-price listings by nightly price band.
SELECT city_name, price_band, band_order, listings, share_pct
FROM workspace.airbnb_gold.v_price_bands
ORDER BY band_order, city_name
