# Oil & Gas Data Pipeline

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

An end-to-end data pipeline that simulates, processes, and visualises daily oil field production data for a fictional Nigerian onshore field. Generates realistic production metrics, runs analytics with DuckDB, and outputs both a Power BI-ready dataset and a static interactive HTML dashboard.

## Who this is for

Upstream oil & gas commercial analysts, production engineers, E&P data teams, and energy sector recruiters looking for candidates with domain-specific data pipeline experience.

## Key metrics tracked

| Metric | Description |
|--------|-------------|
| Daily production volume | Barrels of oil per day (bopd) |
| Lifting cost per barrel | OPEX / production volume |
| Production decline curve | Month-over-month decline analysis |
| Revenue forecast | Scenarios at $75, $85, and $95 per barrel |
| Downtime analysis | Hours lost and production deferred |

## Tech stack

- **Python** — data generation and orchestration
- **DuckDB** — fast, serverless SQL analytics on local files
- **Pandas** — data processing
- **Plotly** — interactive HTML charts and dashboard

## How to run locally

```bash
# Clone the repo
git clone https://github.com/JimiR3d/oil-gas-data-pipeline.git
cd oil-gas-data-pipeline

# Install dependencies
pip install -r requirements.txt

# Generate 2 years of simulated production data
python generate_data.py

# Run the analytics pipeline
python pipeline.py

# Generate the interactive dashboard
python dashboard.py
```

The output dashboard is saved to `output/dashboard.html` — open it in any browser.

## Live dashboard

Download and open [`output/dashboard.html`](output/dashboard.html) directly — no Python required.

## Project structure

```
oil-gas-data-pipeline/
├── generate_data.py        # Simulates 2 years of field production data
├── pipeline.py             # DuckDB aggregation logic
├── dashboard.py            # Plotly HTML dashboard output
├── data/
│   └── (generated CSVs)
├── output/
│   └── dashboard.html      # Static exportable dashboard
├── requirements.txt
└── README.md
```

## Context

Built by [Jimi Aboderin](https://github.com/JimiR3d) to demonstrate domain awareness in upstream oil & gas analytics — the exact KPIs (production volumes, lifting costs, decline curves, revenue scenarios) that commercial analysts at companies like Seplat Energy and Shell Nigeria track daily.

## License

MIT
