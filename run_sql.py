"""
Step 2 and 3: Build the delivered_orders table, then run every analysis query in sql/.
Each result prints to the console and saves to data/processed/sql_results/<query>.csv.

Run from the project root:  python run_sql.py
Run a single query:         python run_sql.py 04_routes
"""
import math
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "olist.db"
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "data" / "processed" / "sql_results"


class Stdev:
    """Sample standard deviation aggregate, since SQLite has no built in STDEV."""

    def __init__(self):
        self.values = []

    def step(self, value):
        if value is not None:
            self.values.append(float(value))

    def finalize(self):
        n = len(self.values)
        if n < 2:
            return None
        mean = sum(self.values) / n
        return math.sqrt(sum((v - mean) ** 2 for v in self.values) / (n - 1))


def connect():
    if not DB_PATH.exists():
        raise SystemExit("data/olist.db not found. Run python load_data.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.create_aggregate("STDEV", 1, Stdev)
    return conn


def main():
    conn = connect()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None

    if only is None:
        build_sql = (SQL_DIR / "00_build_delivered_orders.sql").read_text()
        conn.executescript(build_sql)
        rows = conn.execute("SELECT COUNT(*) FROM delivered_orders").fetchone()[0]
        print(f"Built delivered_orders: {rows:,} rows\n")

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        if sql_file.stem.startswith("00"):
            continue
        if only and sql_file.stem != only:
            continue
        df = pd.read_sql(sql_file.read_text(), conn)
        df.to_csv(OUT_DIR / f"{sql_file.stem}.csv", index=False)
        print("=" * 90)
        print(sql_file.stem)
        print("=" * 90)
        print(df.head(15).to_string(index=False))
        print()

    conn.close()
    print(f"Results saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
