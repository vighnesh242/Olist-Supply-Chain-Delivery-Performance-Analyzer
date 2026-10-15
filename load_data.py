
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "olist.db"

FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

INDEXES = [
    ("orders", "order_id"),
    ("orders", "customer_id"),
    ("order_items", "order_id"),
    ("order_items", "seller_id"),
    ("order_items", "product_id"),
    ("customers", "customer_id"),
    ("sellers", "seller_id"),
    ("products", "product_id"),
    ("order_reviews", "order_id"),
    ("order_payments", "order_id"),
    ("geolocation", "geolocation_zip_code_prefix"),
]


def main():
    missing = [name for name in FILES.values() if not (RAW / name).exists()]
    if missing:
        raise SystemExit(f"Missing files in {RAW}:\n  " + "\n  ".join(missing))

    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)

    print(f"{'table':<24}{'csv rows':>12}{'db rows':>12}{'cols':>6}")
    for table, filename in FILES.items():
        df = pd.read_csv(RAW / filename, encoding="utf-8-sig")
        df.columns = [col.strip().replace("lenght", "length") for col in df.columns]
        df.to_sql(table, conn, index=False, chunksize=20000)
        db_rows = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        status = "" if db_rows == len(df) else "  <-- MISMATCH"
        print(f"{table:<24}{len(df):>12,}{db_rows:>12,}{df.shape[1]:>6}{status}")

    for table, column in INDEXES:
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column})")
    conn.commit()
    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")


if __name__ == "__main__":
    main()
