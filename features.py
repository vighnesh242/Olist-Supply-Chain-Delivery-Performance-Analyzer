"""Shared helpers used by the notebooks and the Tableau export."""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "olist.db"

STATE_NAMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins",
}

STATE_REGIONS = {
    **dict.fromkeys(["AC", "AP", "AM", "PA", "RO", "RR", "TO"], "North"),
    **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Northeast"),
    **dict.fromkeys(["DF", "GO", "MT", "MS"], "Central-West"),
    **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Southeast"),
    **dict.fromkeys(["PR", "RS", "SC"], "South"),
}

DELAY_BUCKETS = [
    "1. Early 10+ days", "2. Early 1-9 days", "3. On estimate day",
    "4. Late 1-3 days", "5. Late 4-7 days", "6. Late 8+ days",
]


def connect():
    if not DB_PATH.exists():
        raise SystemExit("data/olist.db not found. Run load_data.py and run_sql.py first.")
    return sqlite3.connect(DB_PATH)


def load_delivered(conn):
    df = pd.read_sql("SELECT * FROM delivered_orders", conn)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df


def zip_centroids(conn):
    """One lat/lng per zip prefix, dropping points outside Brazil's bounding box."""
    query = """
        SELECT geolocation_zip_code_prefix AS zip_prefix,
               AVG(geolocation_lat)        AS lat,
               AVG(geolocation_lng)        AS lng
        FROM geolocation
        WHERE geolocation_lat BETWEEN -34 AND 6
          AND geolocation_lng BETWEEN -74 AND -34
        GROUP BY geolocation_zip_code_prefix
    """
    return pd.read_sql(query, conn)


def haversine_km(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


def add_distance(df, centroids):
    customer = centroids.rename(columns={
        "zip_prefix": "customer_zip_code_prefix", "lat": "customer_lat", "lng": "customer_lng"})
    seller = centroids.rename(columns={
        "zip_prefix": "seller_zip_code_prefix", "lat": "seller_lat", "lng": "seller_lng"})
    out = df.merge(customer, on="customer_zip_code_prefix", how="left")
    out = out.merge(seller, on="seller_zip_code_prefix", how="left")
    out["distance_km"] = haversine_km(
        out["customer_lat"], out["customer_lng"], out["seller_lat"], out["seller_lng"]).round(1)
    return out


def add_labels(df):
    out = df.copy()
    out["customer_state_name"] = out["customer_state"].map(STATE_NAMES)
    out["seller_state_name"] = out["seller_state"].map(STATE_NAMES)
    out["customer_region"] = out["customer_state"].map(STATE_REGIONS)
    out["seller_region"] = out["seller_state"].map(STATE_REGIONS)
    out["delivery_status"] = np.where(out["is_late"] == 1, "Late", "On time")
    d = out["days_vs_estimate"]
    out["delay_bucket"] = np.select(
        [d <= -10, d <= -1, d == 0, d <= 3, d <= 7],
        DELAY_BUCKETS[:5],
        default=DELAY_BUCKETS[5],
    )
    return out
