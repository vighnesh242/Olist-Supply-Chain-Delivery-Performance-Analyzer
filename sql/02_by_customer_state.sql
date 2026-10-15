-- Where do customers get late or slow deliveries? Variance = unpredictability.
SELECT
    customer_state,
    COUNT(*)                            AS orders,
    ROUND(100.0 * AVG(is_late), 2)      AS late_rate_pct,
    ROUND(AVG(total_days), 2)           AS avg_delivery_days,
    ROUND(STDEV(total_days), 2)         AS delivery_days_stdev,
    ROUND(AVG(estimated_lead_days), 2)  AS avg_promised_days,
    ROUND(AVG(carrier_transit_days), 2) AS avg_transit_days,
    ROUND(AVG(review_score), 2)         AS avg_review
FROM delivered_orders
GROUP BY customer_state
ORDER BY late_rate_pct DESC;
