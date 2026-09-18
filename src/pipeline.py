import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "Data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "Data" / "processed"

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_data():

    print("\nLoading raw datasets...")

    sku_master = pd.read_csv(
        RAW_DATA_DIR / "sku_master.csv"
    )

    calendar = pd.read_csv(
        RAW_DATA_DIR / "calendar.csv"
    )

    sales_daily = pd.read_csv(
        RAW_DATA_DIR / "sales_daily.csv"
    )

    inventory_snapshots = pd.read_csv(
        RAW_DATA_DIR / "inventory_snapshots.csv"
    )

    print("sku_master:", sku_master.shape)
    print("calendar:", calendar.shape)
    print("sales_daily:", sales_daily.shape)
    print(
        "inventory_snapshots:",
        inventory_snapshots.shape
    )

    return (
        sku_master,
        calendar,
        sales_daily,
        inventory_snapshots
    )


def clean_data(
    sku_master,
    calendar,
    sales_daily,
    inventory_snapshots
):

    print("\nCleaning data...")


    sku_master["sku_id"] = (
        sku_master["sku_id"]
        .astype(str)
        .str.strip()
    )

    sku_master["category"] = (
        sku_master["category"]
        .astype(str)
        .str.strip()
    )

    sku_master["subcategory"] = (
        sku_master["subcategory"]
        .astype(str)
        .str.strip()
    )

    sku_master["launch_date"] = pd.to_datetime(
        sku_master["launch_date"],
        errors="coerce"
    )

    sku_master["unit_cost"] = pd.to_numeric(
        sku_master["unit_cost"],
        errors="coerce"
    )

    sku_master["list_price"] = pd.to_numeric(
        sku_master["list_price"],
        errors="coerce"
    )


    calendar["date"] = pd.to_datetime(
    calendar["date"],
    format="%Y-%m-%d",
    errors="coerce"
)

    calendar["week"] = pd.to_numeric(
        calendar["week"],
        errors="coerce"
    )

    calendar["month"] = pd.to_numeric(
        calendar["month"],
        errors="coerce"
    )

    calendar["season"] = (
        calendar["season"]
        .astype(str)
        .str.strip()
    )

    calendar["is_holiday"] = pd.to_numeric(
        calendar["is_holiday"],
        errors="coerce"
    )

    calendar["promo_event"] = (
        calendar["promo_event"]
        .astype(str)
        .str.strip()
    )


    sales_daily["date"] = pd.to_datetime(
    sales_daily["date"],
    format="%Y-%m-%d",
    errors="coerce"
)



    sales_daily["sku_id"] = (
        sales_daily["sku_id"]
        .astype(str)
        .str.strip()
    )

    sales_daily["units_sold"] = pd.to_numeric(
        sales_daily["units_sold"],
        errors="coerce"
    )

    sales_daily["revenue"] = pd.to_numeric(
        sales_daily["revenue"],
        errors="coerce"
    )

    sales_daily["unit_price"] = pd.to_numeric(
        sales_daily["unit_price"],
        errors="coerce"
    )

    sales_daily["promo_flag"] = pd.to_numeric(
        sales_daily["promo_flag"],
        errors="coerce"
    )


    inventory_snapshots["date"] = pd.to_datetime(
    inventory_snapshots["date"],
    format="%d-%m-%Y",
    errors="coerce"
)


    inventory_snapshots["sku_id"] = (
        inventory_snapshots["sku_id"]
        .astype(str)
        .str.strip()
    )

    inventory_snapshots["on_hand_units"] = pd.to_numeric(
        inventory_snapshots["on_hand_units"],
        errors="coerce"
    )

    inventory_snapshots["on_order_units"] = pd.to_numeric(
        inventory_snapshots["on_order_units"],
        errors="coerce"
    )

    inventory_snapshots["lead_time_days"] = pd.to_numeric(
        inventory_snapshots["lead_time_days"],
        errors="coerce"
    )

    inventory_snapshots["reorder_point"] = pd.to_numeric(
        inventory_snapshots["reorder_point"],
        errors="coerce"
    )


    print("Data types fixed.")


    before = len(sku_master)

    sku_master = (
        sku_master
        .drop_duplicates(subset=["sku_id"])
        .copy()
    )

    print(
        "SKU duplicates removed:",
        before - len(sku_master)
    )


    before = len(calendar)

    calendar = (
        calendar
        .drop_duplicates(subset=["date"])
        .copy()
    )

    print(
        "Calendar duplicates removed:",
        before - len(calendar)
    )


    before = len(sales_daily)

    sales_daily = (
        sales_daily
        .drop_duplicates(
            subset=["date", "sku_id"]
        )
        .copy()
    )

    print(
        "Sales duplicates removed:",
        before - len(sales_daily)
    )


    before = len(inventory_snapshots)

    inventory_snapshots = (
        inventory_snapshots
        .drop_duplicates(
            subset=["date", "sku_id"]
        )
        .copy()
    )

    print(
        "Inventory duplicates removed:",
        before - len(inventory_snapshots)
    )


    numeric_columns = [
        "units_sold",
        "revenue",
        "unit_price"
    ]

    for column in numeric_columns:

        sales_daily[column] = (
            sales_daily[column]
            .fillna(0)
        )


    inventory_columns = [
        "on_hand_units",
        "on_order_units"
    ]

    for column in inventory_columns:

        inventory_snapshots[column] = (
            inventory_snapshots[column]
            .fillna(0)
        )


    sales_daily["promo_flag"] = (
        sales_daily["promo_flag"]
        .fillna(0)
        .astype(int)
    )


    calendar["is_holiday"] = (
        calendar["is_holiday"]
        .fillna(0)
        .astype(int)
    )


    sku_master = sku_master.dropna(
        subset=["sku_id"]
    )

    calendar = calendar.dropna(
        subset=["date"]
    )

    sales_daily = sales_daily.dropna(
        subset=["date", "sku_id"]
    )

    inventory_snapshots = (
        inventory_snapshots
        .dropna(
            subset=["date", "sku_id"]
        )
    )


    sales_daily["units_sold"] = (
        sales_daily["units_sold"]
        .clip(lower=0)
    )

    sales_daily["revenue"] = (
        sales_daily["revenue"]
        .clip(lower=0)
    )

    sales_daily["unit_price"] = (
        sales_daily["unit_price"]
        .clip(lower=0)
    )

    inventory_snapshots["on_hand_units"] = (
        inventory_snapshots["on_hand_units"]
        .clip(lower=0)
    )

    inventory_snapshots["on_order_units"] = (
        inventory_snapshots["on_order_units"]
        .clip(lower=0)
    )


    print("Missing values handled.")
    print("Negative values handled.")

    return (
        sku_master,
        calendar,
        sales_daily,
        inventory_snapshots
    )


def validate_data(
    sku_master,
    calendar,
    sales_daily,
    inventory_snapshots
):

    print("\nRunning validation...")


    valid_skus = set(
        sku_master["sku_id"]
    )


    invalid_sales_skus = (
        ~sales_daily["sku_id"]
        .isin(valid_skus)
    ).sum()


    invalid_inventory_skus = (
        ~inventory_snapshots["sku_id"]
        .isin(valid_skus)
    ).sum()


    print(
        "Invalid sales SKUs:",
        invalid_sales_skus
    )

    print(
        "Invalid inventory SKUs:",
        invalid_inventory_skus
    )


    invalid_sales_dates = (
        ~sales_daily["date"]
        .isin(calendar["date"])
    ).sum()


    invalid_inventory_dates = (
        ~inventory_snapshots["date"]
        .isin(calendar["date"])
    ).sum()


    print(
        "Invalid sales dates:",
        invalid_sales_dates
    )

    print(
        "Invalid inventory dates:",
        invalid_inventory_dates
    )


    sales_daily = sales_daily[
        sales_daily["sku_id"]
        .isin(valid_skus)
    ].copy()


    inventory_snapshots = (
        inventory_snapshots[
            inventory_snapshots["sku_id"]
            .isin(valid_skus)
        ]
        .copy()
    )


    sales_daily = sales_daily[
        sales_daily["date"]
        .isin(calendar["date"])
    ].copy()


    inventory_snapshots = (
        inventory_snapshots[
            inventory_snapshots["date"]
            .isin(calendar["date"])
        ]
        .copy()
    )


    print("Validation completed.")


    return (
        sales_daily,
        inventory_snapshots
    )


def create_analysis_dataset(
    sku_master,
    calendar,
    sales_daily,
    inventory_snapshots
):

    print("\nCreating analysis-ready dataset...")


    analysis_data = sales_daily.merge(
        sku_master,
        on="sku_id",
        how="left"
    )


    analysis_data = analysis_data.merge(
        calendar,
        on="date",
        how="left"
    )


    analysis_data = analysis_data.merge(
        inventory_snapshots,
        on=["date", "sku_id"],
        how="left"
    )


    analysis_data = analysis_data.sort_values(
        ["date", "sku_id"]
    ).reset_index(drop=True)


    output_file = (
        PROCESSED_DATA_DIR
        / "analysis_ready.csv"
    )


    analysis_data.to_csv(
        output_file,
        index=False
    )


    print(
        "\nAnalysis-ready dataset created:"
    )

    print(output_file)

    print(
        "Rows:",
        f"{len(analysis_data):,}"
    )

    print(
        "Columns:",
        len(analysis_data.columns)
    )


    return analysis_data


def main():

    print("=" * 60)
    print("PROJECT FORESIGHT - D1 DATA PIPELINE")
    print("=" * 60)


    (
        sku_master,
        calendar,
        sales_daily,
        inventory_snapshots
    ) = load_data()


    (
        sku_master,
        calendar,
        sales_daily,
        inventory_snapshots
    ) = clean_data(
        sku_master,
        calendar,
        sales_daily,
        inventory_snapshots
    )


    (
        sales_daily,
        inventory_snapshots
    ) = validate_data(
        sku_master,
        calendar,
        sales_daily,
        inventory_snapshots
    )


    analysis_data = create_analysis_dataset(
        sku_master,
        calendar,
        sales_daily,
        inventory_snapshots
    )


    print("\n" + "=" * 60)
    print("D1 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()