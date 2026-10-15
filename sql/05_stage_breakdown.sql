-- Root cause by stage: which leg of the journey grows when an order is late?
SELECT
    CASE WHEN is_late = 1 THEN 'Late' ELSE 'On time' END AS delivery_status,
    COUNT(*)                            AS orders,
    ROUND(AVG(approval_days), 2)        AS avg_approval_days,
    ROUND(AVG(seller_handling_days), 2) AS avg_handling_days,
    ROUND(AVG(carrier_transit_days), 2) AS avg_transit_days,
    ROUND(AVG(total_days), 2)           AS avg_total_days,
    ROUND(AVG(estimated_lead_days), 2)  AS avg_promised_days
FROM delivered_orders
WHERE approval_days IS NOT NULL
  AND seller_handling_days IS NOT NULL
  AND carrier_transit_days IS NOT NULL
  AND seller_handling_days >= 0
  AND carrier_transit_days >= 0
GROUP BY is_late
ORDER BY is_late;
