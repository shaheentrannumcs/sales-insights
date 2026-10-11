"""Core analysis functions. Each takes a cleaned DataFrame and returns a DataFrame/Series."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {
    "order_id", "order_date", "region", "channel", "category",
    "product", "unit_price", "quantity", "discount_pct", "customer_id",
}


def load(path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date"])
    return clean(df)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = df.drop_duplicates("order_id").copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
    df["revenue"] = (df["unit_price"] * df["quantity"] * (1 - df["discount_pct"] / 100)).round(2)
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df.reset_index(drop=True)


def kpis(df: pd.DataFrame) -> dict:
    orders = len(df)
    revenue = float(df["revenue"].sum())
    return {
        "total_revenue": round(revenue, 2),
        "orders": orders,
        "customers": int(df["customer_id"].nunique()),
        "avg_order_value": round(revenue / orders, 2) if orders else 0.0,
        "avg_discount_pct": round(float(df["discount_pct"].mean()), 2) if orders else 0.0,
    }


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
    out["mom_growth_pct"] = (out["revenue"].pct_change() * 100).round(1).fillna(0.0)
    out["revenue"] = out["revenue"].round(2)
    return out


def revenue_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    out = (
        df.groupby(column, as_index=False)["revenue"].sum()
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )
    out["share_pct"] = (out["revenue"] / out["revenue"].sum() * 100).round(1)
    out["revenue"] = out["revenue"].round(2)
    return out


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby(["category", "product"], as_index=False)
        .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
        .head(n)
        .round({"revenue": 2})
        .reset_index(drop=True)
    )


def repeat_customer_rate(df: pd.DataFrame) -> float:
    counts = df["customer_id"].value_counts()
    return round(float((counts > 1).mean() * 100), 1) if len(counts) else 0.0


def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("discount_pct", as_index=False)
        .agg(orders=("order_id", "count"), avg_quantity=("quantity", "mean"), avg_revenue=("revenue", "mean"))
        .round(2)
    )
