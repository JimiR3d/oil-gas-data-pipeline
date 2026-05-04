# 🛢️ Oil & Gas Production Data Pipeline

End-to-end data pipeline for Nigerian upstream oil field analytics — from simulated well production data to interactive dashboards and Power BI–ready exports.

**Field:** Eko Field (OML 47) · Fictional Nigerian onshore asset  
**Period:** Jan 2024 – Dec 2025 (2 years, daily granularity)

---

## Architecture

```
generate_data.py          →  data/daily_production.csv
                              data/monthly_summary.csv
                                      ↓
pipeline.py (DuckDB)      →  output/power_bi_dataset.csv
                              + 7 analytical views
                                      ↓
dashboard.py (Plotly)      →  output/dashboard.html
                              (self-contained, no server)
```

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Simulation | Python, NumPy | Realistic decline curves, water cut, downtime events |
| Storage | CSV | Lightweight, version-controllable data |
| Analytics | DuckDB | Serverless SQL engine — window functions, aggregations |
| Visualization | Plotly | Interactive charts, static HTML export |
| CI | GitHub Actions | Flake8 linting |

## Key Features

### Data Generation (`generate_data.py`)
- Exponential production decline (15% annual rate)
- Water cut progression (25% → 50%+ over field life)
- Stochastic downtime events with 8 cause categories
- OPEX/CAPEX simulation with realistic Nigerian field economics
- Gas-Oil Ratio (GOR) tracking

### Analytics Pipeline (`pipeline.py`)
- **7 analytical queries** via DuckDB:
  - Monthly production trends
  - Month-over-month decline analysis (window functions)
  - Lifting cost per barrel
  - Revenue scenarios at $75/$85/$95 per barrel
  - Downtime cause breakdown
  - Deferred production quantification
  - Field-level KPI summary
- Power BI–ready flat dataset export

### Dashboard (`dashboard.py`)
- 8 KPI summary cards (production, revenue, costs, downtime)
- 5 interactive charts:
  - Production trend with water cut overlay
  - Revenue vs operating costs
  - Revenue sensitivity analysis (oil price scenarios)
  - Lifting cost trend vs industry benchmark
  - Downtime impact analysis
- Dark-themed, Inter font, professional styling
- Self-contained HTML — no server needed

## Quick Start

```bash
pip install -r requirements.txt

# Step 1: Generate field data
python generate_data.py

# Step 2: Run analytics pipeline
python pipeline.py

# Step 3: Build interactive dashboard
python dashboard.py

# Open output/dashboard.html in your browser
```

## Sample Output

| Metric | Value |
|--------|-------|
| Avg Net Production | ~7,800 bopd |
| Total Production (2yr) | ~5.7M bbls |
| Avg Water Cut | ~33% |
| Avg Lifting Cost | ~$25/bbl |
| Downtime Events | ~36 |

## Project Context

This project demonstrates:
- **Data engineering** — Python data generation, DuckDB SQL analytics
- **Domain knowledge** — Nigerian upstream oil production economics
- **Visualization** — Plotly interactive dashboards, Power BI export
- **Software quality** — CI pipeline, documentation, modular architecture

Built as part of my data analyst portfolio. All data is simulated; no proprietary information.

## Author

**Jimi Aboderin**  
[LinkedIn](https://www.linkedin.com/in/oluwafolajinmi-aboderin-695848249/) · [GitHub](https://github.com/JimiR3d) · folajinmi13@gmail.com
