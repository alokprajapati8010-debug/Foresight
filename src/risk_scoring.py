import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "Data" / "processed" / "analysis_ready.csv"
FORECAST_FILE = PROJECT_ROOT / "Data" / "processed" / "forecast" / "weekly_forecast.csv"

OUTPUT_DIR = PROJECT_ROOT / "Data" / "processed" / "risk"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    print("=" * 60)
    print("PROJECT FORESIGHT - D4 INVENTORY RISK SCORING")
    print("=" * 60)

    print("\nLoading analysis-ready dataset...")

    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    numeric_columns = [
        "on_hand_units",
        "on_order_units",
        "lead_time_days",
        "reorder_point",
        "unit_cost"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

    print(f"Rows: {len(df):,}")
    print(f"SKUs: {df['sku_id'].nunique()}")

    print("\nLoading weekly forecasts...")

    forecast = pd.read_csv(FORECAST_FILE)

    forecast["forecast_date"] = pd.to_datetime(
        forecast["forecast_date"],
        errors="coerce"
    )

    forecast["forecast_units"] = pd.to_numeric(
        forecast["forecast_units"],
        errors="coerce"
    ).fillna(0)

    print(f"Forecast records: {len(forecast):,}")

    return df, forecast


def prepare_inventory(df):
    print("\nPreparing latest inventory snapshot...")

    latest_date = df["date"].max()

    inventory = (
        df[df["date"] == latest_date]
        .sort_values("sku_id")
        .copy()
    )

    inventory = inventory.drop_duplicates(
        subset=["sku_id"],
        keep="last"
    )

    print(f"Latest inventory date: {latest_date.date()}")
    print(f"Inventory SKUs: {len(inventory)}")

    return inventory


def prepare_forecast(forecast):
    print("\nPreparing forecast horizon...")

    forecast_summary = (
        forecast
        .groupby("sku_id")
        .agg(
            forecast_4_week_demand=(
                "forecast_units",
                "sum"
            ),
            average_weekly_forecast=(
                "forecast_units",
                "mean"
            )
        )
        .reset_index()
    )

    return forecast_summary


def calculate_risk(inventory, forecast_summary):

    print("\nCalculating inventory risks...")

    result = inventory.merge(
        forecast_summary,
        on="sku_id",
        how="left"
    )

    result["forecast_4_week_demand"] = (
        result["forecast_4_week_demand"]
        .fillna(0)
    )

    result["average_weekly_forecast"] = (
        result["average_weekly_forecast"]
        .fillna(0)
    )

    result["available_inventory"] = (
        result["on_hand_units"]
        + result["on_order_units"]
    )

    result["lead_time_weeks"] = (
        result["lead_time_days"] / 7
    )

    result["lead_time_demand"] = (
        result["average_weekly_forecast"]
        * result["lead_time_weeks"]
    )

    result["safety_stock"] = (
        result["reorder_point"]
    )

    result["stockout_threshold"] = (
        result["lead_time_demand"]
        + result["safety_stock"]
    )

    result["inventory_surplus"] = (
        result["on_hand_units"]
        - result["forecast_4_week_demand"]
    )

    result["stockout_gap"] = (
        result["stockout_threshold"]
        - result["available_inventory"]
    )

    result["overstock_units"] = (
        result["on_hand_units"]
        - result["forecast_4_week_demand"]
    ).clip(lower=0)

    result["stockout_risk_score"] = np.where(
        result["stockout_threshold"] > 0,
        (
            result["stockout_gap"]
            / result["stockout_threshold"]
        ) * 100,
        0
    )

    result["stockout_risk_score"] = (
        result["stockout_risk_score"]
        .clip(lower=0, upper=100)
    )

    result["overstock_risk_score"] = np.where(
        result["forecast_4_week_demand"] > 0,
        (
            result["overstock_units"]
            / result["forecast_4_week_demand"]
        ) * 100,
        0
    )

    result["overstock_risk_score"] = (
        result["overstock_risk_score"]
        .clip(lower=0, upper=100)
    )

    result["stockout_risk"] = np.select(
        [
            result["stockout_risk_score"] >= 50,
            result["stockout_risk_score"] >= 25
        ],
        [
            "High",
            "Medium"
        ],
        default="Low"
    )

    result["overstock_risk"] = np.select(
        [
            result["overstock_risk_score"] >= 50,
            result["overstock_risk_score"] >= 25
        ],
        [
            "High",
            "Medium"
        ],
        default="Low"
    )

    result["action"] = np.select(
        [
            (
                (result["stockout_risk"] == "High")
                & (result["overstock_risk"] == "Low")
            ),
            (
                (result["stockout_risk"] == "Low")
                & (result["overstock_risk"] == "High")
            ),
            (
                (result["stockout_risk"] == "High")
                & (result["overstock_risk"] == "High")
            ),
            (
                (result["stockout_risk"] == "Medium")
                | (result["overstock_risk"] == "Medium")
            )
        ],
        [
            "Reorder Now",
            "Markdown / Clear",
            "Watch / Volatile",
            "Watch / Volatile"
        ],
        default="Healthy"
    )

    result["reorder_units"] = (
        result["stockout_gap"]
        .clip(lower=0)
        .round()
    )

    result["markdown_units"] = (
        result["overstock_units"]
        .round()
    )

    result["stockout_value_at_stake"] = (
        result["reorder_units"]
        * result["unit_cost"]
    )

    result["overstock_value_at_stake"] = (
        result["markdown_units"]
        * result["unit_cost"]
    )

    result["value_at_stake"] = np.where(
        result["action"] == "Reorder Now",
        result["stockout_value_at_stake"],
        np.where(
            result["action"] == "Markdown / Clear",
            result["overstock_value_at_stake"],
            0
        )
    )

    return result


def save_results(result):

    output_file = (
        OUTPUT_DIR / "inventory_risk_scores.csv"
    )

    result.to_csv(
        output_file,
        index=False
    )

    print("\nRisk scoring file created:")
    print(output_file)

    action_summary = (
        result["action"]
        .value_counts()
    )

    print("\nAction Summary:")
    print(action_summary)

    print("\nTotal value at stake:")
    print(
        f"₹{result['value_at_stake'].sum():,.2f}"
    )

    print("\nTop 10 priority SKUs:")

    priority = (
        result[
            [
                "sku_id",
                "stockout_risk",
                "overstock_risk",
                "action",
                "value_at_stake"
            ]
        ]
        .sort_values(
            "value_at_stake",
            ascending=False
        )
        .head(10)
    )

    print(priority.to_string(index=False))


def main():

    df, forecast = load_data()

    inventory = prepare_inventory(df)

    forecast_summary = prepare_forecast(
        forecast
    )

    result = calculate_risk(
        inventory,
        forecast_summary
    )

    save_results(result)

    print("\n" + "=" * 60)
    print("D4 INVENTORY RISK SCORING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()