-- Seller state to customer state lanes with enough volume to trust.
SELECT
    seller_state || ' > ' || customer_state AS route,
    seller_state,
    customer_state,
    COUNT(*)                            AS orders,
    ROUND(100.0 * AVG(is_late), 2)      AS late_rate_pct,
    ROUND(AVG(total_days), 2)           AS avg_delivery_days,
    ROUND(STDEV(total_days), 2)         AS delivery_days_stdev,
    ROUND(AVG(carrier_transit_days), 2) AS avg_transit_days
FROM delivered_orders
GROUP BY seller_state, customer_state
HAVING COUNT(*) >= 100
ORDER BY late_rate_pct DESC;
