"""
DuckDB Analytics Pipeline

Runs SQL-based aggregations and analytics on the generated
production data using DuckDB (fast, serverless SQL engine).

Produces analytical views for the dashboard and Power BI export.
"""

import duckdb
import pandas as pd
import os


def create_connection(daily_csv="data/daily_production.csv",
                      monthly_csv="data/monthly_summary.csv"):
    """Create DuckDB connection and register CSV data as tables."""
    con = duckdb.connect(":memory:")

    con.execute(f"""
        CREATE TABLE daily_production AS
        SELECT * FROM read_csv_auto('{daily_csv}')
    """)

    con.execute(f"""
        CREATE TABLE monthly_summary AS
        SELECT * FROM read_csv_auto('{monthly_csv}')
    """)

    return con


def run_production_analytics(con):
    """Run production analytics queries and return results as DataFrames."""
    results = {}

    # 1. Monthly production trend
    results["monthly_production"] = con.execute("""
        SELECT
            month,
            ROUND(avg_gross_bopd, 0) AS avg_gross_bopd,
            ROUND(avg_net_oil_bopd, 0) AS avg_net_oil_bopd,
            ROUND(total_net_oil_bbls, 0) AS total_net_oil_bbls,
            ROUND(avg_water_cut_pct, 1) AS avg_water_cut_pct
        FROM monthly_summary
        ORDER BY month
    """).fetchdf()

    # 2. Production decline analysis (month-over-month change)
    results["decline_analysis"] = con.execute("""
        SELECT
            month,
            avg_net_oil_bopd,
            LAG(avg_net_oil_bopd) OVER (ORDER BY month) AS prev_month_bopd,
            ROUND(
                ((avg_net_oil_bopd - LAG(avg_net_oil_bopd) OVER (ORDER BY month))
                / NULLIF(LAG(avg_net_oil_bopd) OVER (ORDER BY month), 0)) * 100,
                2
            ) AS mom_change_pct
        FROM monthly_summary
        ORDER BY month
    """).fetchdf()

    # 3. Lifting cost analysis
    results["lifting_costs"] = con.execute("""
        SELECT
            month,
            ROUND(avg_lifting_cost, 2) AS avg_lifting_cost_usd_bbl,
            ROUND(total_opex_usd, 0) AS total_opex_usd,
            ROUND(total_capex_usd, 0) AS total_capex_usd,
            ROUND(total_opex_usd + total_capex_usd, 0) AS total_cost_usd
        FROM monthly_summary
        ORDER BY month
    """).fetchdf()

    # 4. Revenue forecast at different oil price scenarios
    results["revenue_forecast"] = con.execute("""
        SELECT
            month,
            ROUND(total_net_oil_bbls, 0) AS total_bbls,
            ROUND(revenue_usd_75bbl, 0) AS revenue_at_75,
            ROUND(revenue_usd_85bbl, 0) AS revenue_at_85,
            ROUND(revenue_usd_95bbl, 0) AS revenue_at_95,
            ROUND(total_opex_usd + total_capex_usd, 0) AS total_cost,
            ROUND(revenue_usd_85bbl - (total_opex_usd + total_capex_usd), 0) AS net_income_at_85
        FROM monthly_summary
        ORDER BY month
    """).fetchdf()

    # 5. Downtime analysis
    results["downtime_analysis"] = con.execute("""
        SELECT
            month,
            downtime_events,
            total_downtime_hours,
            ROUND(production_deferred_bbls, 0) AS production_deferred_bbls,
            ROUND(production_deferred_bbls * 85, 0) AS deferred_revenue_usd_85bbl
        FROM monthly_summary
        ORDER BY month
    """).fetchdf()

    # 6. Downtime causes breakdown (from daily data)
    results["downtime_causes"] = con.execute("""
        SELECT
            downtime_cause,
            COUNT(*) AS occurrences,
            SUM(downtime_hours) AS total_hours,
            ROUND(AVG(downtime_hours), 1) AS avg_hours_per_event
        FROM daily_production
        WHERE downtime_hours > 0 AND downtime_cause != ''
        GROUP BY downtime_cause
        ORDER BY total_hours DESC
    """).fetchdf()

    # 7. Overall field KPIs
    results["field_kpis"] = con.execute("""
        SELECT
            ROUND(AVG(avg_net_oil_bopd), 0) AS avg_net_production_bopd,
            ROUND(SUM(total_net_oil_bbls), 0) AS total_production_bbls,
            ROUND(AVG(avg_lifting_cost), 2) AS avg_lifting_cost_usd_bbl,
            ROUND(SUM(total_opex_usd), 0) AS total_opex_usd,
            ROUND(SUM(total_capex_usd), 0) AS total_capex_usd,
            ROUND(SUM(revenue_usd_85bbl), 0) AS total_revenue_at_85,
            SUM(downtime_events) AS total_downtime_events,
            SUM(total_downtime_hours) AS total_downtime_hours,
            ROUND(SUM(production_deferred_bbls), 0) AS total_deferred_bbls
        FROM monthly_summary
    """).fetchdf()

    return results


def export_power_bi_dataset(con, output_path="output/power_bi_dataset.csv"):
    """Export a flat dataset optimized for Power BI import."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df = con.execute("""
        SELECT
            date,
            field,
            block,
            gross_production_bopd,
            net_oil_bopd,
            water_cut_pct,
            gas_production_mscf_d,
            gor_scf_bbl,
            opex_usd,
            capex_usd,
            lifting_cost_usd_bbl,
            downtime_hours,
            downtime_cause,
            net_oil_bopd * 75 AS revenue_usd_75bbl,
            net_oil_bopd * 85 AS revenue_usd_85bbl,
            net_oil_bopd * 95 AS revenue_usd_95bbl
        FROM daily_production
        ORDER BY date
    """).fetchdf()

    df.to_csv(output_path, index=False)
    print(f"✓ Power BI dataset exported: {output_path}")
    return df


def main():
    """Run the full analytics pipeline."""
    print("── Oil & Gas Analytics Pipeline ──\n")

    # Check data exists
    if not os.path.exists("data/daily_production.csv"):
        print("⚠ No data found. Run generate_data.py first.")
        return

    # Connect and load data
    con = create_connection()
    print("✓ Data loaded into DuckDB\n")

    # Run analytics
    results = run_production_analytics(con)

    # Print field KPIs
    kpis = results["field_kpis"].iloc[0]
    print("── Field KPIs ──")
    print(f"Avg Net Production:   {kpis['avg_net_production_bopd']:,.0f} bopd")
    print(f"Total Production:     {kpis['total_production_bbls']:,.0f} bbls")
    print(f"Avg Lifting Cost:     ${kpis['avg_lifting_cost_usd_bbl']:.2f}/bbl")
    print(f"Total OPEX:           ${kpis['total_opex_usd']:,.0f}")
    print(f"Total CAPEX:          ${kpis['total_capex_usd']:,.0f}")
    print(f"Total Revenue (@$85): ${kpis['total_revenue_at_85']:,.0f}")
    print(f"Downtime Events:      {kpis['total_downtime_events']:.0f}")
    print(f"Deferred Production:  {kpis['total_deferred_bbls']:,.0f} bbls\n")

    # Export Power BI dataset
    export_power_bi_dataset(con)

    con.close()
    print("\n✓ Pipeline complete")


if __name__ == "__main__":
    main()
