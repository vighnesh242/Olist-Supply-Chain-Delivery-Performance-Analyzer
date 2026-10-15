-- Late rate over time; months under 100 orders are dropped (2016 is sparse).
SELECT
    purchase_month,
    COUNT(*)                          AS orders,
    ROUND(100.0 * AVG(is_late), 2)    AS late_rate_pct,
    ROUND(AVG(total_days), 2)         AS avg_delivery_days,
    ROUND(AVG(estimated_lead_days), 2) AS avg_promised_days
FROM delivered_orders
GROUP BY purchase_month
HAVING COUNT(*) >= 100
ORDER BY purchase_month;
