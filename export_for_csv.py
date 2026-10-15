import pandas as pd

from features import ROOT, STATE_NAMES, add_distance, add_labels, connect, load_delivered, zip_centroids

OUT = ROOT / "data" / "processed"


def main():
    conn = connect()
    df = add_labels(add_distance(load_delivered(conn), zip_centroids(conn)))
    conn.close()

    fact_cols = [
        "order_id", "order_purchase_timestamp", "purchase_month",
        "customer_state", "customer_state_name", "customer_region", "customer_city",
        "seller_id", "seller_state", "seller_state_name", "seller_region",
        "product_category", "item_count", "order_value", "freight_value", "total_weight_g",
        "distance_km", "same_state",
        "approval_days", "seller_handling_days", "carrier_transit_days", "total_days",
        "estimated_lead_days", "days_vs_estimate", "is_late", "delivery_status",
        "missed_seller_deadline", "delay_bucket", "review_score",
        "customer_lat", "customer_lng",
    ]
    df[fact_cols].to_csv(OUT / "delivery_fact.csv", index=False)

    state = (
        df.groupby("customer_state")
        .agg(orders=("order_id", "count"),
             late_rate=("is_late", "mean"),
             avg_delivery_days=("total_days", "mean"),
             delivery_days_stdev=("total_days", "std"),
             avg_promised_days=("estimated_lead_days", "mean"),
             avg_distance_km=("distance_km", "mean"),
             avg_review=("review_score", "mean"))
        .reset_index()
    )
    state["customer_state_name"] = state["customer_state"].map(STATE_NAMES)
    state.round(3).to_csv(OUT / "state_summary.csv", index=False)

    route = (
        df.groupby(["seller_state", "customer_state"])
        .agg(orders=("order_id", "count"),
             late_rate=("is_late", "mean"),
             avg_delivery_days=("total_days", "mean"),
             delivery_days_stdev=("total_days", "std"))
        .reset_index()
    )
    route = route[route["orders"] >= 30]
    route["route"] = route["seller_state"] + " > " + route["customer_state"]
    route.round(3).to_csv(OUT / "route_summary.csv", index=False)

    clean = df[(df["seller_handling_days"] >= 0) & (df["carrier_transit_days"] >= 0)]
    stage = (
        clean.groupby("delivery_status")[["approval_days", "seller_handling_days", "carrier_transit_days"]]
        .mean()
        .reset_index()
        .melt(id_vars="delivery_status", var_name="stage", value_name="avg_days")
    )
    stage_labels = {
        "approval_days": "1. Payment approval",
        "seller_handling_days": "2. Seller handling",
        "carrier_transit_days": "3. Carrier transit",
    }
    stage["stage"] = stage["stage"].map(stage_labels)
    stage.round(3).sort_values(["delivery_status", "stage"]).to_csv(OUT / "stage_summary.csv", index=False)

    monthly = (
        df.groupby("purchase_month")
        .agg(orders=("order_id", "count"),
             late_rate=("is_late", "mean"),
             avg_delivery_days=("total_days", "mean"),
             avg_promised_days=("estimated_lead_days", "mean"))
        .reset_index()
    )
    monthly = monthly[monthly["orders"] >= 100]
    monthly.round(3).to_csv(OUT / "monthly_trend.csv", index=False)

    for name in ["delivery_fact", "state_summary", "route_summary", "stage_summary", "monthly_trend"]:
        rows = len(pd.read_csv(OUT / f"{name}.csv"))
        print(f"{name + '.csv':<22}{rows:>10,} rows")


if __name__ == "__main__":
    main()
