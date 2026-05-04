"""
Oil Field Production Data Generator

Generates 2 years of realistic simulated daily production data
for a fictional Nigerian onshore oil field ("Eko Field, OML 47").

Outputs:
    - data/daily_production.csv
    - data/monthly_summary.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Seed for reproducibility
np.random.seed(42)

# ── Field parameters ─────────────────────────────────────────────────
FIELD_NAME = "Eko Field"
BLOCK = "OML 47"
OPERATOR = "Eko Petroleum Development Company"
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)  # 2 years

# Initial production rate (barrels of oil per day)
INITIAL_BOPD = 12_500

# Natural decline rate (annual, typical for Nigerian onshore: 10-20%)
ANNUAL_DECLINE_RATE = 0.15

# Operating cost parameters (USD)
BASE_OPEX_PER_DAY = 185_000  # Base daily operating expenditure
OPEX_VARIANCE = 0.12  # ±12% daily variance

# Capital expenditure (sporadic, for workovers/infill drilling)
CAPEX_PROBABILITY = 0.03  # ~3% chance of CAPEX event per day
CAPEX_RANGE = (500_000, 5_000_000)  # USD per event

# Downtime parameters
DOWNTIME_PROBABILITY = 0.05  # ~5% chance of downtime per day
DOWNTIME_HOURS_RANGE = (4, 24)  # Hours lost per event
DOWNTIME_CAUSES = [
    "Scheduled maintenance",
    "Flow station repair",
    "Pipeline leak",
    "Community disruption",
    "Power failure",
    "Wellhead equipment failure",
    "Third-party pipeline shutdown",
    "Weather (flooding)",
]

# Water cut (increases over time — typical for mature Nigerian fields)
INITIAL_WATER_CUT = 0.25  # 25%
WATER_CUT_INCREASE_ANNUAL = 0.08  # +8% per year

# Gas-Oil Ratio (scf/bbl, increases slightly with decline)
INITIAL_GOR = 450  # scf/bbl
GOR_INCREASE_ANNUAL = 0.05


def generate_daily_data():
    """Generate daily production data for the field."""
    print(f"Generating production data for {FIELD_NAME} ({BLOCK})...")
    print(f"Period: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")

    dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
    records = []

    for i, date in enumerate(dates):
        days_elapsed = i
        years_elapsed = days_elapsed / 365.25

        # Production with exponential decline + noise
        decline_factor = np.exp(-ANNUAL_DECLINE_RATE * years_elapsed)
        base_production = INITIAL_BOPD * decline_factor
        daily_noise = np.random.normal(1.0, 0.04)  # ±4% daily noise
        gross_production = max(0, base_production * daily_noise)

        # Downtime events
        has_downtime = np.random.random() < DOWNTIME_PROBABILITY
        downtime_hours = 0
        downtime_cause = None

        if has_downtime:
            downtime_hours = np.random.randint(*DOWNTIME_HOURS_RANGE)
            downtime_cause = np.random.choice(DOWNTIME_CAUSES)
            # Reduce production proportionally
            production_factor = max(0, (24 - downtime_hours) / 24)
            gross_production *= production_factor

        # Water cut (increases over field life)
        water_cut = min(0.85, INITIAL_WATER_CUT + WATER_CUT_INCREASE_ANNUAL * years_elapsed)
        water_cut += np.random.normal(0, 0.02)  # Small daily variance
        water_cut = max(0.05, min(0.90, water_cut))

        # Net oil production (after water)
        net_oil_bopd = gross_production * (1 - water_cut)

        # Gas production (associated gas)
        gor = INITIAL_GOR * (1 + GOR_INCREASE_ANNUAL * years_elapsed)
        gas_production_mscf = (net_oil_bopd * gor) / 1000  # Convert to Mscf/d

        # OPEX
        daily_opex = BASE_OPEX_PER_DAY * np.random.uniform(
            1 - OPEX_VARIANCE, 1 + OPEX_VARIANCE
        )

        # CAPEX (sporadic)
        has_capex = np.random.random() < CAPEX_PROBABILITY
        daily_capex = np.random.uniform(*CAPEX_RANGE) if has_capex else 0
        capex_description = "Infill drilling / workover" if has_capex else None

        # Lifting cost (OPEX per barrel)
        lifting_cost = daily_opex / net_oil_bopd if net_oil_bopd > 0 else 0

        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "field": FIELD_NAME,
            "block": BLOCK,
            "operator": OPERATOR,
            "gross_production_bopd": round(gross_production, 1),
            "water_cut_pct": round(water_cut * 100, 2),
            "net_oil_bopd": round(net_oil_bopd, 1),
            "gas_production_mscf_d": round(gas_production_mscf, 1),
            "gor_scf_bbl": round(gor, 1),
            "opex_usd": round(daily_opex, 2),
            "capex_usd": round(daily_capex, 2),
            "lifting_cost_usd_bbl": round(lifting_cost, 2),
            "downtime_hours": downtime_hours,
            "downtime_cause": downtime_cause if downtime_cause else "",
            "capex_description": capex_description if capex_description else "",
        })

    df = pd.DataFrame(records)
    return df


def generate_monthly_summary(daily_df):
    """Aggregate daily data into monthly summaries."""
    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")

    monthly = df.groupby("month").agg(
        days_in_month=("date", "count"),
        avg_gross_bopd=("gross_production_bopd", "mean"),
        avg_net_oil_bopd=("net_oil_bopd", "mean"),
        total_net_oil_bbls=("net_oil_bopd", "sum"),
        avg_water_cut_pct=("water_cut_pct", "mean"),
        avg_gas_mscf_d=("gas_production_mscf_d", "mean"),
        total_opex_usd=("opex_usd", "sum"),
        total_capex_usd=("capex_usd", "sum"),
        avg_lifting_cost=("lifting_cost_usd_bbl", "mean"),
        total_downtime_hours=("downtime_hours", "sum"),
        downtime_events=("downtime_hours", lambda x: (x > 0).sum()),
    ).reset_index()

    monthly["month"] = monthly["month"].astype(str)

    # Revenue scenarios
    for price in [75, 85, 95]:
        monthly[f"revenue_usd_{price}bbl"] = (
            monthly["total_net_oil_bbls"] * price
        ).round(2)

    # Production deferred (estimated from downtime)
    monthly["production_deferred_bbls"] = (
        monthly["total_downtime_hours"] / 24 * monthly["avg_net_oil_bopd"]
    ).round(0)

    # Round numeric columns
    for col in monthly.select_dtypes(include=[np.number]).columns:
        monthly[col] = monthly[col].round(2)

    return monthly


def main():
    """Generate and save all data files."""
    os.makedirs("data", exist_ok=True)

    # Generate daily data
    daily_df = generate_daily_data()
    daily_path = "data/daily_production.csv"
    daily_df.to_csv(daily_path, index=False)
    print(f"✓ Daily data saved: {daily_path} ({len(daily_df)} records)")

    # Generate monthly summary
    monthly_df = generate_monthly_summary(daily_df)
    monthly_path = "data/monthly_summary.csv"
    monthly_df.to_csv(monthly_path, index=False)
    print(f"✓ Monthly summary saved: {monthly_path} ({len(monthly_df)} records)")

    # Print quick stats
    print(f"\n── Field Summary ──")
    print(f"Field: {FIELD_NAME} ({BLOCK})")
    print(f"Period: {START_DATE.strftime('%b %Y')} – {END_DATE.strftime('%b %Y')}")
    print(f"Avg gross production: {daily_df['gross_production_bopd'].mean():,.0f} bopd")
    print(f"Avg net oil: {daily_df['net_oil_bopd'].mean():,.0f} bopd")
    print(f"Total downtime events: {(daily_df['downtime_hours'] > 0).sum()}")
    print(f"Total CAPEX events: {(daily_df['capex_usd'] > 0).sum()}")


if __name__ == "__main__":
    main()
