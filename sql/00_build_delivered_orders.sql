-- Step 2: Build the analysis layer.
-- Helper views roll items, products, and reviews up to one row per order,
-- then delivered_orders is materialized as a table so every query is fast.

DROP VIEW IF EXISTS order_items_agg;
CREATE VIEW order_items_agg AS
SELECT
    oi.order_id,
    COUNT(*)                                                         AS item_count,
    SUM(oi.price)                                                    AS order_value,
    SUM(oi.freight_value)                                            AS freight_value,
    SUM(p.product_weight_g)                                          AS total_weight_g,
    SUM(p.product_length_cm * p.product_height_cm * p.product_width_cm) AS total_volume_cm3,
    COUNT(DISTINCT oi.seller_id)                                     AS seller_count
FROM order_items oi
LEFT JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.order_id;

DROP VIEW IF EXISTS first_item;
CREATE VIEW first_item AS
SELECT
    oi.order_id,
    oi.seller_id,
    oi.shipping_limit_date,
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS product_category
FROM order_items oi
LEFT JOIN products p             ON oi.product_id = p.product_id
LEFT JOIN category_translation t ON p.product_category_name = t.product_category_name
WHERE oi.order_item_id = 1;

DROP VIEW IF EXISTS reviews_agg;
CREATE VIEW reviews_agg AS
SELECT order_id, AVG(review_score) AS review_score
FROM order_reviews
GROUP BY order_id;

DROP TABLE IF EXISTS delivered_orders;
CREATE TABLE delivered_orders AS
SELECT
    o.order_id,
    c.customer_state,
    c.customer_city,
    c.customer_zip_code_prefix,
    s.seller_id,
    s.seller_state,
    s.seller_city,
    s.seller_zip_code_prefix,
    fi.product_category,
    o.order_purchase_timestamp,
    strftime('%Y-%m', o.order_purchase_timestamp)                                         AS purchase_month,
    ia.item_count,
    ia.order_value,
    ia.freight_value,
    ia.total_weight_g,
    ia.total_volume_cm3,
    ia.seller_count,
    r.review_score,
    ROUND(julianday(o.order_approved_at)             - julianday(o.order_purchase_timestamp), 2)    AS approval_days,
    ROUND(julianday(o.order_delivered_carrier_date)  - julianday(o.order_approved_at), 2)           AS seller_handling_days,
    ROUND(julianday(o.order_delivered_customer_date) - julianday(o.order_delivered_carrier_date), 2) AS carrier_transit_days,
    ROUND(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp), 2)    AS total_days,
    ROUND(julianday(o.order_estimated_delivery_date) - julianday(o.order_purchase_timestamp), 2)    AS estimated_lead_days,
    julianday(date(o.order_delivered_customer_date)) - julianday(date(o.order_estimated_delivery_date)) AS days_vs_estimate,
    CASE WHEN date(o.order_delivered_customer_date) > date(o.order_estimated_delivery_date) THEN 1 ELSE 0 END AS is_late,
    CASE WHEN o.order_delivered_carrier_date > fi.shipping_limit_date THEN 1 ELSE 0 END                    AS missed_seller_deadline,
    CASE WHEN c.customer_state = s.seller_state THEN 1 ELSE 0 END                                         AS same_state
FROM orders o
JOIN customers c        ON o.customer_id = c.customer_id
JOIN first_item fi      ON o.order_id = fi.order_id
JOIN sellers s          ON fi.seller_id = s.seller_id
JOIN order_items_agg ia ON o.order_id = ia.order_id
LEFT JOIN reviews_agg r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL;

CREATE INDEX idx_do_customer_state ON delivered_orders(customer_state);
CREATE INDEX idx_do_seller_state   ON delivered_orders(seller_state);
