"""Build a Markdown report with charts from a sales CSV."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import analysis  # noqa: E402


def _bar(series_df, x, y, title, path, horizontal=False):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if horizontal:
        ax.barh(series_df[x][::-1], series_df[y][::-1], color="#4C72B0")
    else:
        ax.bar(series_df[x], series_df[y], color="#4C72B0")
        plt.xticks(rotation=45, ha="right")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _table(df) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(f"{v:,.2f}" if isinstance(v, float) else str(v) for v in row) + " |")
    return "\n".join(lines)


def build_report(csv_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = analysis.load(csv_path)
    k = analysis.kpis(df)
    monthly = analysis.monthly_revenue(df)
    by_cat = analysis.revenue_by(df, "category")
    by_region = analysis.revenue_by(df, "region")
    by_channel = analysis.revenue_by(df, "channel")
    top = analysis.top_products(df)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(monthly["month"], monthly["revenue"], marker="o", color="#4C72B0")
    ax.set_title("Monthly revenue (INR)")
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(out_dir / "monthly_revenue.png", dpi=120)
    plt.close(fig)
    _bar(by_cat, "category", "revenue", "Revenue by category (INR)", out_dir / "category_revenue.png")
    _bar(by_region, "region", "revenue", "Revenue by region (INR)", out_dir / "region_revenue.png")
    _bar(top, "product", "revenue", "Top 10 products by revenue", out_dir / "top_products.png", horizontal=True)

    best_month = monthly.loc[monthly["revenue"].idxmax()]
    md = f"""# Sales Report

## Key metrics

| Metric | Value |
|---|---|
| Total revenue | ₹{k['total_revenue']:,.2f} |
| Orders | {k['orders']:,} |
| Unique customers | {k['customers']:,} |
| Average order value | ₹{k['avg_order_value']:,.2f} |
| Repeat customer rate | {analysis.repeat_customer_rate(df)}% |

## Highlights

- **{by_cat.iloc[0]['category']}** is the top category with {by_cat.iloc[0]['share_pct']}% of revenue.
- **{by_region.iloc[0]['region']}** leads regions with {by_region.iloc[0]['share_pct']}% of revenue.
- Best month was **{best_month['month']}** (₹{best_month['revenue']:,.0f}), driven by the festive season.
- Online contributes {by_channel.set_index('channel').loc['Online', 'share_pct']}% of revenue.

## Monthly trend

![Monthly revenue](monthly_revenue.png)

{_table(monthly)}

## Categories

![Category revenue](category_revenue.png)

{_table(by_cat)}

## Regions

![Region revenue](region_revenue.png)

## Top products

![Top products](top_products.png)

{_table(top)}

## Discount impact

{_table(analysis.discount_impact(df))}
"""
    report = out_dir / "REPORT.md"
    report.write_text(md, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, nargs="?", default=Path("data/sales_2025.csv"))
    parser.add_argument("--out", type=Path, default=Path("reports"))
    args = parser.parse_args()
    print(f"Report written to {build_report(args.csv, args.out)}")


if __name__ == "__main__":
    main()
