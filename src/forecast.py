import pandas as pd
import numpy as np 
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "Data" / "processed" / "analysis_ready.csv"
OUTPUT_DIR = PROJECT_ROOT / "Data" / "processed" / "forecast"
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

def load_data():
    print("=" * 60)
    print("PROJECT FORESIGHT - D3 DEMAND FORECASTING")
    print("=" * 60)

    print("\nLoading analysis-ready dataset...")

    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(df["date"],errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"],errors="coerce").fillna(0)

    print(f"Rows: {len(df):,}")
    print(f"SKUs:{df['sku_id'].nunique()}")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    return df

def create_weekly_demand(df):
    print("\nCreating weekly SKU-level demand...")

    df = df.copy()

    df["week"] = (
        df["date"]
        .dt.to_period("W-SUN")
        .dt.end_time
        .dt.normalize()
    )

    weekly = (
        df.groupby(
            ["sku_id", "week"],
            sort=False
        )["units_sold"]
        .sum()
        .reset_index()
    )

    weekly = weekly.rename(
        columns={
            "week": "date"
        }
    )

    weekly = weekly[
        ["sku_id", "date", "units_sold"]
    ]

    weekly = weekly.sort_values(
        ["sku_id", "date"]
    ).reset_index(drop=True)

    print(f"Weekly records: {len(weekly):,}")
    print(f"Weekly columns: {list(weekly.columns)}")

    return weekly

def seasonal_naive_forecast(train, horizon=4, season_length=52):
    train = np.asarray(train)

    if len(train) < season_length:
        value = train[-1]

        return np.repeat(
            value,
            horizon
        )

    seasonal_values = train[-season_length:]

    repeats = int(
        np.ceil(horizon / season_length)
    )

    forecast = np.tile(
        seasonal_values,
        repeats
    )

    return forecast[:horizon]
def wape(actual, forecast):
    denominator = np.abs(actual).sum()

    if denominator == 0:
        return 0.0

    return (
        np.abs(actual - forecast).sum() / denominator) * 100

def create_backtest(weekly, horizon=4, season_length=52):
    print("\nRunning rolling-origin backtesting...")

    results = []

    sku_list = weekly["sku_id"].dropna().unique()

    for sku_id in sku_list:

        sku_data = weekly[
            weekly["sku_id"] == sku_id
        ].sort_values("date")

        values = sku_data["units_sold"].to_numpy()

        if len(values) < season_length + horizon:
            continue

        test_start = len(values) - horizon

        train = values[:test_start]

        actual = values[test_start:]

        baseline_forecast = seasonal_naive_forecast(
            train,
            horizon=horizon,
            season_length=season_length
        )

        baseline_wape = wape(
            actual,
            baseline_forecast
        )

        results.append({
            "sku_id": sku_id,
            "actual_total": actual.sum(),
            "baseline_forecast_total": baseline_forecast.sum(),
            "baseline_wape": baseline_wape
        })

    results_df = pd.DataFrame(results)

    print(
        f"SKUs successfully backtested: {len(results_df)}"
    )

    if len(results_df) > 0:
        print(
            f"Average baseline WAPE: "
            f"{results_df['baseline_wape'].mean():.2f}%"
        )

    return results_df

def create_forecast(weekly, horizon=4, season_length=52):
    print("\nCreating future weekly forecasts...")

    forecasts = []

    sku_list = weekly["sku_id"].dropna().unique()

    for sku_id in sku_list:

        sku_data = weekly[
            weekly["sku_id"] == sku_id
        ].sort_values("date")

        values = sku_data["units_sold"].to_numpy()

        last_date = sku_data["date"].max()

        forecast_values = seasonal_naive_forecast(
            values,
            horizon=horizon,
            season_length=season_length
        )

        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=7),
            periods=horizon,
            freq="7D"
        )

        for date, value in zip(
            future_dates,
            forecast_values
        ):

            forecasts.append({
                "sku_id": sku_id,
                "forecast_date": date,
                "forecast_units": max(
                    0,
                    round(float(value), 2)
                ),
                "model": "seasonal_naive"
            })

    forecast_df = pd.DataFrame(forecasts)

    print(
        f"Forecast records created: {len(forecast_df):,}"
    )

    return forecast_df
def save_outputs(backtest_df, forecast_df):

    backtest_file = ( OUTPUT_DIR / "backtest_results.csv")
    forecast_file = ( OUTPUT_DIR / "weekly_forecast.csv")
    backtest_df.to_csv(backtest_file, index=False)
    forecast_df.to_csv(forecast_file, index=False)

    print("\nFiles created:")
    print(backtest_file)
    print(forecast_file)


def main():
    df = load_data()

    weekly = create_weekly_demand(df)
    backtest_df = create_backtest(weekly, horizon=4, season_length=52)
    forecast_df = create_forecast(weekly,horizon=4, season_length=52)
    save_outputs(backtest_df, forecast_df)

    print("\n" + "=" * 60)
    print("D3 BASELINE FORECAST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
    