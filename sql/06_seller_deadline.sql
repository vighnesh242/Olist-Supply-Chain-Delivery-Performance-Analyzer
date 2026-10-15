-- Does a seller missing the carrier handoff deadline drive customer lateness?
SELECT
    CASE WHEN missed_seller_deadline = 1 THEN 'Missed handoff deadline' ELSE 'Met handoff deadline' END AS seller_handoff,
    COUNT(*)                               AS orders,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM delivered_orders), 2) AS share_of_orders_pct,
    ROUND(100.0 * AVG(is_late), 2)         AS late_rate_pct,
    ROUND(AVG(total_days), 2)              AS avg_delivery_days,
    ROUND(AVG(review_score), 2)            AS avg_review
FROM delivered_orders
GROUP BY missed_seller_deadline
ORDER BY missed_seller_deadline;
