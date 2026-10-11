"""Generate a reproducible synthetic retail sales dataset."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

CATEGORIES = {
    "Electronics": (["Headphones", "Smartwatch", "Power Bank", "Bluetooth Speaker"], (800, 6000)),
    "Home & Kitchen": (["Mixer Grinder", "Pressure Cooker", "Dinner Set", "Water Bottle"], (300, 4000)),
    "Fashion": (["Kurti", "Saree", "Handbag", "Sneakers"], (400, 3500)),
    "Books": (["Novel", "Cookbook", "Self-help", "Children's Book"], (150, 900)),
    "Beauty": (["Face Wash", "Lipstick", "Perfume", "Hair Oil"], (120, 2500)),
}
REGIONS = ["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Delhi"]
CHANNELS = ["Online", "Store"]


def generate(n_orders: int = 5000, seed: int = 42, year: int = 2025) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp(f"{year}-01-01")
    days = rng.integers(0, 365, n_orders)
    dates = start + pd.to_timedelta(days, unit="D")

    # Festive-season boost (Oct-Nov) - resample some orders into that window
    festive = rng.random(n_orders) < 0.18
    dates = dates.where(~festive, pd.Timestamp(f"{year}-10-01") + pd.to_timedelta(rng.integers(0, 61, n_orders), unit="D"))

    cats = rng.choice(list(CATEGORIES), n_orders, p=[0.25, 0.2, 0.25, 0.12, 0.18])
    products, prices = [], []
    for c in cats:
        items, (lo, hi) = CATEGORIES[c]
        products.append(rng.choice(items))
        prices.append(round(float(rng.uniform(lo, hi)), 2))

    df = pd.DataFrame(
        {
            "order_id": [f"ORD-{i:05d}" for i in range(1, n_orders + 1)],
            "order_date": dates,
            "region": rng.choice(REGIONS, n_orders, p=[0.26, 0.24, 0.16, 0.18, 0.16]),
            "channel": rng.choice(CHANNELS, n_orders, p=[0.62, 0.38]),
            "category": cats,
            "product": products,
            "unit_price": prices,
            "quantity": rng.integers(1, 5, n_orders),
            "discount_pct": rng.choice([0, 5, 10, 15, 20], n_orders, p=[0.4, 0.2, 0.2, 0.12, 0.08]),
            "customer_id": [f"CUST-{x:04d}" for x in rng.integers(1, 1200, n_orders)],
        }
    )
    return df.sort_values("order_date").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data/sales_2025.csv"))
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    generate(args.rows, args.seed).to_csv(args.out, index=False)
    print(f"Wrote {args.rows} rows to {args.out}")


if __name__ == "__main__":
    main()
