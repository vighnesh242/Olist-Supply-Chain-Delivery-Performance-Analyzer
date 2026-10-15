-- Product categories with the worst delivery performance (min 200 orders).
SELECT
    product_category,
    COUNT(*)                          AS orders,
    ROUND(100.0 * AVG(is_late), 2)    AS late_rate_pct,
    ROUND(AVG(total_days), 2)         AS avg_delivery_days,
    ROUND(AVG(total_weight_g) / 1000.0, 2) AS avg_weight_kg,
    ROUND(AVG(freight_value), 2)      AS avg_freight
FROM delivered_orders
GROUP BY product_category
HAVING COUNT(*) >= 200
ORDER BY late_rate_pct DESC;
