-- Which origin states ship slow? Handling time is the seller-controlled stage.
SELECT
    seller_state,
    COUNT(*)                            AS orders,
    COUNT(DISTINCT seller_id)           AS sellers,
    ROUND(100.0 * AVG(is_late), 2)      AS late_rate_pct,
    ROUND(AVG(seller_handling_days), 2) AS avg_handling_days,
    ROUND(100.0 * AVG(missed_seller_deadline), 2) AS missed_deadline_pct,
    ROUND(AVG(total_days), 2)           AS avg_delivery_days
FROM delivered_orders
GROUP BY seller_state
HAVING COUNT(*) >= 50
ORDER BY late_rate_pct DESC;
