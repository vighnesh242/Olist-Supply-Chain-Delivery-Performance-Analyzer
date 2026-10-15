Olist Supply Chain Delivery Performance Analyzer
================================================

**Tools:** SQL (SQLite) · Python (pandas, statsmodels, scikit-learn) · Tableau Public

Business problem
----------------

Olist is a Brazilian e-commerce marketplace that connects thousands of small sellers to customers across all 27 states. A late delivery is the fastest way to lose a customer's trust, and with orders passing through payment approval, seller handling, and carrier transit, it is not obvious where delays come from.

This project answers three questions:

1. **Where** are deliveries late: which states, routes, categories, and months?
2. **Why** are they late: which stage of the journey breaks down, and what factors drive it?
3. **So what**: how much does lateness cost in customer satisfaction?

Key results at a glance
-----------------------

| Metric | Value |
|---|---|
| Delivered orders analyzed | 96,470 |
| Customer states / sellers | 27 / 2,960 |
| On-time delivery rate | 93.2% |
| Late delivery rate | 6.8% |
| Avg actual delivery time | 12.6 days |
| Avg promised delivery time | 23.7 days |
| Transit time variance (std dev) | 9.6 days |
| Avg days late, when late | 10.6 days |

Key findings
------------

**1. Carrier transit is the main bottleneck, not sellers or payments.**
Late orders take 34.0 days end to end vs 11.1 days for on-time orders, an extra 22.9 days. Carrier transit accounts for 87% of that gap (27.9 vs 8.0 days), seller handling for about 13% (5.6 vs 2.7 days), and payment approval is negligible.

**2. Sellers who miss the carrier handoff deadline are 3.9x more likely to deliver late.**
9.0% of orders missed the seller's shipping limit date. Those orders were late 20.8% of the time vs 5.4% when the deadline was met, and averaged a 3.7 review vs 4.2. In the logistic regression, a missed deadline still raises the odds of lateness by 54% after controlling for distance, weight, and handling time, and each extra day of seller handling adds 18% to the odds.

**3. Lateness is concentrated in the Northeast and on long cross-state routes.**
Alagoas (21.4% late), Maranhão (17.4%), and Sergipe (15.2%) are the worst states, compared with 2.8% in Amazonas. Cross-state orders carry about 3x the odds of being late compared with same-state orders (odds ratio 0.33 for same state), and every additional 100 km adds about 8% to the odds.

**4. The highest-impact lane is SP to RJ, not the worst-rate lane.**
SP to AL has the worst late rate of any route with 100+ orders (23.9%), but only 255 orders. SP to RJ runs at 14.1% late across 8,158 orders, roughly 1,150 late deliveries, which makes it the single biggest operational fix by volume. Rio de Janeiro as a whole receives 12,350 orders at a 12.1% late rate, nearly double the national average.

**5. Padded delivery estimates hide operational problems.**
Olist promises an average of 23.7 days but delivers in 12.6, and 64% of orders arrive 10 or more days early. The promised lead time was the strongest predictor in the gradient boosting model: when the buffer is thin, the same transit problems turn into late orders. This means the 93.2% on-time rate overstates real logistics performance.

**6. Peak season breaks the network.**
The late rate jumped from about 4% in October 2017 to 12.4% in November 2017 (Black Friday volume) and reached 14.1% in February 2018. Orders placed in November and December carry 79% higher odds of arriving late.

**7. Late deliveries destroy customer satisfaction.**
Average review score falls from 4.32 for orders arriving 10+ days early to 1.70 for orders 8+ days late, and the share of 1 to 2 star reviews rises from 8.9% to 79.2%. Overall, late orders average 2.02 fewer stars than on-time orders.

| Delivery vs estimate | Orders | Avg review | 1 to 2 star reviews |
|---|---|---|---|
| Early 10+ days | 61,523 | 4.32 | 8.9% |
| Early 1 to 9 days | 26,640 | 4.23 | 10.0% |
| On estimate day | 1,280 | 4.04 | 12.3% |
| Late 1 to 3 days | 1,852 | 3.29 | 32.2% |
| Late 4 to 7 days | 1,748 | 2.11 | 67.6% |
| Late 8+ days | 2,781 | 1.70 | 79.2% |

Recommendations
---------------

1. **Prioritize carrier performance on Northeast lanes and SP to RJ.** Renegotiate SLAs or add a secondary carrier on the highest-volume late lanes, since transit drives 87% of delay.
2. **Enforce the seller handoff deadline.** Flag sellers with repeated missed deadlines and surface handling time in seller scorecards. One Maranhão seller alone shipped 388 orders at a 19.1% late rate.
3. **Add capacity buffers for November to February.** Pre-book carrier capacity and widen estimates only during peak weeks instead of padding all year.
4. **Track transit variance, not just on-time rate.** Because estimates are padded, on-time rate alone hides deteriorating performance. Days of buffer used is a more honest KPI.

Root cause model
----------------

The goal was to explain lateness, not to forecast it, since some inputs (like seller handling time) are only known after the order ships.

**Logistic regression (odds ratios, all p < 0.001, pseudo R² 0.13)**

| Factor | Odds ratio | Interpretation |
|---|---|---|
| Peak season (Nov to Dec) | 1.79 | 79% higher odds of being late |
| Missed seller deadline | 1.54 | 54% higher odds |
| Seller handling (per day) | 1.18 | 18% higher odds per extra day |
| Distance (per 100 km) | 1.08 | 8% higher odds per 100 km |
| Weight (per kg) | 1.01 | Minimal effect |
| Promised lead time (per day) | 0.89 | Longer buffers reduce lateness |
| Items in order | 0.82 | Multi-item orders slightly less likely late |
| Same state | 0.33 | Cross-state orders about 3x the odds |

**Gradient boosting (test AUC 0.766), top drivers by permutation importance:** promised lead time, seller handling days, distance, same state, and peak season. Recall on late orders is low at a 0.5 threshold (11.6%), which is expected for an imbalanced, explanatory model and is why it is used for driver ranking rather than prediction.

Data
----

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): 9 related tables covering about 99K orders and 112K order items from 2016 to 2018.

| Table | Grain |
|---|---|
| orders | one row per order, with the 5 delivery timestamps |
| order_items | one row per item, with seller and shipping limit date |
| customers, sellers | location (zip prefix, city, state) |
| products, category_translation | category, weight, dimensions |
| order_reviews | review score per order |
| geolocation | lat/lng per zip prefix (used for distance) |
| order_payments | payment details |

Approach
--------

1. **Data model:** loaded all 9 tables into SQLite with indexes and row count validation, then built a `delivered_orders` table at one row per delivered order with derived stage durations (approval, seller handling, carrier transit), a late flag (delivered after the estimated date), and a missed seller deadline flag.
2. **SQL analysis:** 9 queries covering KPIs, late rate and delivery variance by customer state, seller state, and route, stage breakdown, seller deadline impact, category, monthly trend, and review impact.
3. **Feature engineering:** seller to customer distance via haversine on zip prefix centroids, plus weight, freight, item count, same state flag, seasonality, and promised lead time.
4. **Modeling:** logistic regression for interpretable odds ratios and gradient boosting with permutation importance as a nonlinear check.
5. **Dashboard:** KPI tiles, Brazil state map, stage breakdown, route heatmap, monthly trend, and review impact with date, state, and category filters.

Project structure
-----------------

```
Olist-delivery-performance/
  data/raw/              Raw CSVs (not committed)
  data/processed/        query results, csv extracts, model outputs
  sql/                   00 builds the analysis table, 01 to 09 are analysis queries
  notebooks/             01_eda.ipynb, 02_drivers.ipynb
  images/                charts and dashboard screenshot
  load_data.py           CSVs to SQLite with indexes and row count checks
  run_sql.py             builds delivered_orders and runs every query
  features.py            shared helpers (distance, state names, regions, delay buckets)
  export_for_csv.py      writes the 5 csv for Tableau data sources
```

Limitations
-----------

1. **Timestamp errors:** 1,325 orders (1.4%) have seller handling recorded as negative (carrier pickup logged before payment approval) and 23 have negative transit. These are excluded from stage analysis and modeling, leaving 95,107 orders for the stage breakdown.
2. **Missing timestamps:** 14 orders lack an approval time, 15 lack a carrier pickup time, and 1 lacks transit data.
3. **Extreme delays:** 306 orders took more than 60 days. They are kept in the analysis since they are real customer experiences, but they inflate averages and variance.
4. **Distance is approximate:** it uses zip prefix centroids rather than exact addresses.
5. **Order to seller mapping:** multi-seller orders are attributed to the seller of the first item, which affects a small share of orders.
6. **Explanatory, not predictive:** seller handling time is only known after shipment, so the model explains lateness and should not be used as a forecast at order time.
