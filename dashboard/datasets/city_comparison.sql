-- Page 2. Side-by-side headline metrics and difference from the reference city.
SELECT metric_order, metric, unit, city_name, value, reference_value,
       difference_vs_reference, pct_difference_vs_reference
FROM workspace.airbnb_gold.v_city_comparison
ORDER BY metric_order, city_name
