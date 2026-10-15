-- Business impact: how review scores fall as deliveries slip past the estimate.
SELECT
    CASE
        WHEN days_vs_estimate <= -10 THEN '1. Early 10+ days'
        WHEN days_vs_estimate <= -1  THEN '2. Early 1-9 days'
        WHEN days_vs_estimate = 0    THEN '3. On estimate day'
        WHEN days_vs_estimate <= 3   THEN '4. Late 1-3 days'
        WHEN days_vs_estimate <= 7   THEN '5. Late 4-7 days'
        ELSE                              '6. Late 8+ days'
    END                                AS delay_bucket,
    COUNT(*)                           AS orders,
    ROUND(AVG(review_score), 2)        AS avg_review,
    ROUND(100.0 * AVG(CASE WHEN review_score <= 2 THEN 1.0 ELSE 0 END), 2) AS low_review_pct
FROM delivered_orders
WHERE review_score IS NOT NULL
GROUP BY delay_bucket
ORDER BY delay_bucket;
