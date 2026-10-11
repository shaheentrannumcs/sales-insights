import pandas as pd
import pytest

from sales_insights import analysis
from sales_insights.generate import generate


@pytest.fixture
def df():
    return analysis.clean(generate(n_orders=500, seed=1))


def test_clean_adds_revenue_and_month(df):
    assert {"revenue", "month"} <= set(df.columns)
    row = df.iloc[0]
    expected = round(row.unit_price * row.quantity * (1 - row.discount_pct / 100), 2)
    assert row.revenue == pytest.approx(expected)


def test_clean_removes_duplicates_and_invalid_rows():
    raw = generate(n_orders=10, seed=2)
    raw = pd.concat([raw, raw.iloc[[0]]])
    raw.loc[raw.index[1], "quantity"] = 0
    cleaned = analysis.clean(raw)
    assert cleaned["order_id"].is_unique
    assert (cleaned["quantity"] > 0).all()


def test_clean_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing columns"):
        analysis.clean(pd.DataFrame({"order_id": [1]}))


def test_kpis_consistent(df):
    k = analysis.kpis(df)
    assert k["orders"] == len(df)
    assert k["avg_order_value"] == pytest.approx(k["total_revenue"] / k["orders"], rel=1e-3)


def test_revenue_by_shares_sum_to_100(df):
    out = analysis.revenue_by(df, "category")
    assert out["share_pct"].sum() == pytest.approx(100, abs=0.5)
    assert out["revenue"].is_monotonic_decreasing


def test_monthly_revenue_has_twelve_months():
    df = analysis.clean(generate(n_orders=3000, seed=3))
    assert len(analysis.monthly_revenue(df)) == 12


def test_top_products_limit(df):
    assert len(analysis.top_products(df, n=5)) == 5


def test_repeat_rate_bounds(df):
    assert 0 <= analysis.repeat_customer_rate(df) <= 100
