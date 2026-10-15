-- Headline KPIs for the dashboard top row.
SELECT
    COUNT(*)                                                   AS delivered_orders,
    ROUND(100.0 * (1 - AVG(is_late)), 2)                       AS on_time_rate_pct,
    ROUND(100.0 * AVG(is_late), 2)                             AS late_rate_pct,
    ROUND(AVG(total_days), 2)                                  AS avg_delivery_days,
    ROUND(AVG(estimated_lead_days), 2)                         AS avg_promised_days,
    ROUND(AVG(days_vs_estimate), 2)                            AS avg_days_vs_estimate,
    ROUND(AVG(CASE WHEN is_late = 1 THEN days_vs_estimate END), 2) AS avg_days_late_when_late,
    ROUND(STDEV(total_days), 2)                                AS delivery_days_stdev,
    COUNT(DISTINCT customer_state)                             AS customer_states,
    COUNT(DISTINCT seller_id)                                  AS sellers
FROM delivered_orders;
