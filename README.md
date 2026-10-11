# Sales Insights

Exploratory data analysis of a year of retail sales, packaged as a small, tested Python toolkit. It cleans raw order data, computes business KPIs, and generates a Markdown report with charts.

![Monthly revenue](reports/monthly_revenue.png)

## What it does

- **Cleans** raw order data: removes duplicates and invalid rows, validates the schema, and derives revenue after discount.
- **Analyses** monthly trend and month-over-month growth, revenue share by category, region and channel, top products, repeat-customer rate and how discounts affect order size.
- **Reports** a ready-to-share [`reports/REPORT.md`](reports/REPORT.md) with charts.

## Key findings (sample dataset)

- Electronics drives ~42% of revenue despite being 25% of orders.
- October is the peak month, driven by the festive season.
- Hyderabad is the strongest region; online makes up ~62% of revenue.

## Tech

Python · pandas · NumPy · Matplotlib · pytest

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m sales_insights.generate      # create data/sales_2025.csv (synthetic, seeded)
python -m sales_insights.report        # build reports/REPORT.md + charts
pytest -q                              # run the test suite
```

Use your own data: `python -m sales_insights.report path/to/orders.csv --out reports/`. The CSV needs the columns listed in `REQUIRED_COLUMNS` in `sales_insights/analysis.py`.

## Project structure

```
sales_insights/
  generate.py   # reproducible synthetic dataset
  analysis.py   # cleaning + KPI functions (pure, testable)
  report.py     # charts + Markdown report
tests/          # pytest suite
data/           # input CSV
reports/        # generated report and charts
```

## Note on data

The dataset is synthetic, generated with a fixed seed so results are reproducible. It models realistic patterns such as a festive-season spike and regional and category mix.
