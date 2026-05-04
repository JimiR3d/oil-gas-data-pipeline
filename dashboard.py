"""
Static Plotly Dashboard Generator

Generates an interactive, self-contained HTML dashboard
from the production data — no server required.

Output: output/dashboard.html
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os


# ── Color palette ────────────────────────────────────────────────────
COLORS = {
    "primary": "#0F2C4D",       # Dark navy
    "accent": "#1ABC9C",        # Teal
    "warning": "#E74C3C",       # Red
    "amber": "#F39C12",         # Amber
    "light": "#ECF0F1",         # Light gray
    "oil": "#27AE60",           # Green (oil production)
    "water": "#3498DB",         # Blue (water)
    "gas": "#E67E22",           # Orange (gas)
    "revenue": "#2ECC71",       # Green (revenue)
    "cost": "#E74C3C",          # Red (cost)
    "chart_bg": "#1A1A2E",      # Dark chart background
    "grid": "#2D2D44",          # Grid lines
}


def load_data():
    """Load monthly summary data."""
    df = pd.read_csv("data/monthly_summary.csv")
    return df


def create_production_chart(df):
    """Create production trend chart with dual axis."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df["month"], y=df["avg_gross_bopd"],
            name="Gross Production",
            line=dict(color=COLORS["primary"], width=2),
            fill="tozeroy",
            fillcolor="rgba(15, 44, 77, 0.15)",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["month"], y=df["avg_net_oil_bopd"],
            name="Net Oil Production",
            line=dict(color=COLORS["accent"], width=3),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["month"], y=df["avg_water_cut_pct"],
            name="Water Cut %",
            line=dict(color=COLORS["water"], width=2, dash="dash"),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Monthly Production Trend & Water Cut",
        template="plotly_dark",
        paper_bgcolor=COLORS["chart_bg"],
        plot_bgcolor=COLORS["chart_bg"],
        font=dict(family="Inter, Arial", color="#ECF0F1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Production (bopd)", secondary_y=False)
    fig.update_yaxes(title_text="Water Cut (%)", secondary_y=True)

    return fig


def create_financial_chart(df):
    """Create revenue vs cost analysis chart."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["month"], y=df["revenue_usd_85bbl"],
        name="Revenue ($85/bbl)",
        marker_color=COLORS["revenue"],
        opacity=0.85,
    ))

    fig.add_trace(go.Bar(
        x=df["month"], y=df["total_opex_usd"],
        name="OPEX",
        marker_color=COLORS["cost"],
        opacity=0.85,
    ))

    fig.add_trace(go.Bar(
        x=df["month"], y=df["total_capex_usd"],
        name="CAPEX",
        marker_color=COLORS["amber"],
        opacity=0.85,
    ))

    fig.update_layout(
        title="Monthly Revenue vs Operating Costs",
        barmode="group",
        template="plotly_dark",
        paper_bgcolor=COLORS["chart_bg"],
        plot_bgcolor=COLORS["chart_bg"],
        font=dict(family="Inter, Arial", color="#ECF0F1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis_title="USD",
        hovermode="x unified",
    )

    return fig


def create_downtime_chart(df):
    """Create downtime impact analysis chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df["month"], y=df["total_downtime_hours"],
            name="Downtime Hours",
            marker_color=COLORS["warning"],
            opacity=0.7,
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["month"], y=df["production_deferred_bbls"],
            name="Deferred Production (bbls)",
            line=dict(color=COLORS["amber"], width=2),
            mode="lines+markers",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Downtime Impact Analysis",
        template="plotly_dark",
        paper_bgcolor=COLORS["chart_bg"],
        plot_bgcolor=COLORS["chart_bg"],
        font=dict(family="Inter, Arial", color="#ECF0F1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Hours", secondary_y=False)
    fig.update_yaxes(title_text="Barrels Deferred", secondary_y=True)

    return fig


def create_lifting_cost_chart(df):
    """Create lifting cost trend chart."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["month"], y=df["avg_lifting_cost"],
        name="Lifting Cost",
        line=dict(color=COLORS["accent"], width=3),
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(26, 188, 156, 0.1)",
    ))

    # Add threshold line at industry benchmark ($20/bbl)
    fig.add_hline(
        y=20, line_dash="dash", line_color=COLORS["warning"],
        annotation_text="Industry Benchmark ($20/bbl)",
        annotation_position="top left",
    )

    fig.update_layout(
        title="Average Lifting Cost per Barrel",
        template="plotly_dark",
        paper_bgcolor=COLORS["chart_bg"],
        plot_bgcolor=COLORS["chart_bg"],
        font=dict(family="Inter, Arial", color="#ECF0F1"),
        yaxis_title="USD per barrel",
        hovermode="x unified",
    )

    return fig


def create_revenue_scenarios_chart(df):
    """Create revenue sensitivity analysis at different oil prices."""
    fig = go.Figure()

    for price, col, color in [
        (75, "revenue_usd_75bbl", "#95A5A6"),
        (85, "revenue_usd_85bbl", COLORS["accent"]),
        (95, "revenue_usd_95bbl", COLORS["oil"]),
    ]:
        fig.add_trace(go.Scatter(
            x=df["month"], y=df[col],
            name=f"${price}/bbl",
            line=dict(width=2 if price == 85 else 1.5),
            opacity=1 if price == 85 else 0.7,
        ))

    fig.update_layout(
        title="Revenue Sensitivity Analysis (Oil Price Scenarios)",
        template="plotly_dark",
        paper_bgcolor=COLORS["chart_bg"],
        plot_bgcolor=COLORS["chart_bg"],
        font=dict(family="Inter, Arial", color="#ECF0F1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis_title="Revenue (USD)",
        hovermode="x unified",
    )

    return fig


def build_dashboard_html(charts, df):
    """Combine all charts into a single HTML dashboard."""

    # Calculate KPIs
    total_production = df["total_net_oil_bbls"].sum()
    avg_production = df["avg_net_oil_bopd"].mean()
    avg_water_cut = df["avg_water_cut_pct"].mean()
    total_revenue = df["revenue_usd_85bbl"].sum()
    total_opex = df["total_opex_usd"].sum()
    total_capex = df["total_capex_usd"].sum()
    avg_lifting = df["avg_lifting_cost"].mean()
    total_downtime = df["total_downtime_hours"].sum()

    kpi_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">{avg_production:,.0f}</div>
            <div class="kpi-label">Avg Net Oil (bopd)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{total_production:,.0f}</div>
            <div class="kpi-label">Total Production (bbls)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{avg_water_cut:.1f}%</div>
            <div class="kpi-label">Avg Water Cut</div>
        </div>
        <div class="kpi-card accent">
            <div class="kpi-value">${total_revenue:,.0f}</div>
            <div class="kpi-label">Total Revenue (@$85/bbl)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${total_opex:,.0f}</div>
            <div class="kpi-label">Total OPEX</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${avg_lifting:.2f}</div>
            <div class="kpi-label">Avg Lifting Cost ($/bbl)</div>
        </div>
        <div class="kpi-card warn">
            <div class="kpi-value">{total_downtime:,.0f} hrs</div>
            <div class="kpi-label">Total Downtime</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${total_capex:,.0f}</div>
            <div class="kpi-label">Total CAPEX</div>
        </div>
    </div>
    """

    chart_divs = ""
    for i, (title, fig) in enumerate(charts):
        chart_html = fig.to_html(full_html=False, include_plotlyjs=(i == 0))
        chart_divs += f'<div class="chart-container">{chart_html}</div>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eko Field Production Dashboard | OML 47</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: #0D1117;
            color: #ECF0F1;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #0F2C4D 0%, #1A1A2E 100%);
            padding: 2rem 2rem 1.5rem;
            border-bottom: 3px solid #1ABC9C;
        }}
        .header h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #FFFFFF;
        }}
        .header p {{
            color: #95A5A6;
            margin-top: 0.3rem;
            font-size: 0.95rem;
        }}
        .header .badge {{
            display: inline-block;
            background: rgba(26, 188, 156, 0.2);
            color: #1ABC9C;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background: #1A1A2E;
            border: 1px solid #2D2D44;
            border-radius: 8px;
            padding: 1.25rem;
            text-align: center;
            transition: transform 0.2s;
        }}
        .kpi-card:hover {{ transform: translateY(-2px); border-color: #3D3D54; }}
        .kpi-card.accent {{ border-color: #1ABC9C; }}
        .kpi-card.warn {{ border-color: #E74C3C; }}
        .kpi-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 0.25rem;
        }}
        .kpi-label {{ font-size: 0.8rem; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px; }}
        .chart-container {{
            background: #1A1A2E;
            border: 1px solid #2D2D44;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
        }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #5D6D7E;
            font-size: 0.8rem;
            border-top: 1px solid #2D2D44;
            margin-top: 2rem;
        }}
        .footer a {{ color: #1ABC9C; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Eko Field Production Dashboard</h1>
        <p>OML 47 &bull; Eko Petroleum Development Company &bull; Jan 2024 – Dec 2025</p>
        <span class="badge">Simulated Data &bull; Portfolio Project</span>
    </div>
    <div class="container">
        {kpi_html}
        {chart_divs}
    </div>
    <div class="footer">
        Built by <a href="https://github.com/JimiR3d">Jimi Aboderin</a> &bull;
        Python + DuckDB + Plotly &bull;
        <a href="https://github.com/JimiR3d/oil-gas-data-pipeline">Source Code</a>
    </div>
</body>
</html>"""

    return html


def main():
    """Generate the complete static dashboard."""
    print("── Generating Dashboard ──\n")

    if not os.path.exists("data/monthly_summary.csv"):
        print("⚠ No data found. Run generate_data.py and pipeline.py first.")
        return

    df = load_data()
    print(f"✓ Loaded {len(df)} months of data")

    charts = [
        ("Production Trend", create_production_chart(df)),
        ("Financial Analysis", create_financial_chart(df)),
        ("Revenue Scenarios", create_revenue_scenarios_chart(df)),
        ("Lifting Costs", create_lifting_cost_chart(df)),
        ("Downtime Analysis", create_downtime_chart(df)),
    ]

    html = build_dashboard_html(charts, df)

    os.makedirs("output", exist_ok=True)
    output_path = "output/dashboard.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Dashboard saved: {output_path}")
    print("  Open in browser to view the interactive dashboard.")


if __name__ == "__main__":
    main()
