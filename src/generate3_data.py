import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "Data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

NUM_SKUS = 100
START_DATE = "2024-01-01"
END_DATE = "2025-12-31"


categories = {
                "Furniture": [
                    "Chair",
                    "Table",
                    "Shelf",
                    "Sofa"
                ],
                "Kitchen": [
                    "Cookware",
                    "Storage",
                    "Dinnerware",
                    "Appliances"
                ],
                "Home Decor": [
                    "Wall Decor",
                    "Vase",
                    "Candle",
                    "Decorative Item"
                ],
                "Bedding": [
                    "Bedsheet",
                    "Pillow",
                    "Blanket",
                    "Comforter"
                ],
                "Lighting": [
                    "Table Lamp",
                    "Floor Lamp",
                    "Ceiling Light",
                    "Pendant"
                ],
                "Bath": [
                    "Towel",
                    "Bath Mat",
                    "Shower Curtain",
                    "Storage"
                ]
            }

category_names = list(categories.keys())

sku_records = []

for i in range(1, NUM_SKUS + 1):

                sku_id = f"SKU{i:03d}"

                category = np.random.choice(category_names)

                subcategory = np.random.choice(
                    categories[category]
                )

                launch_date = (
                    pd.Timestamp("2024-01-01")
                    + pd.Timedelta(
                        days=int(np.random.randint(0, 365))
                    )
                )

                unit_cost = round(
                    np.random.uniform(300, 5000),
                    2
                )

                markup = np.random.uniform(
                    1.30,
                    2.20
                )

                list_price = round(
                    unit_cost * markup,
                    2
                )

                sku_records.append({
                    "sku_id": sku_id,
                    "category": category,
                    "subcategory": subcategory,
                    "launch_date": launch_date,
                    "unit_cost": unit_cost,
                    "list_price": list_price
                })


sku_master = pd.DataFrame(sku_records)

sku_master = sku_master.sort_values(
                "sku_id"
            ).reset_index(drop=True)

sku_master.to_csv(
                RAW_DATA_DIR / "sku_master.csv",
                index=False
            )

print("sku_master.csv created")
print(f"SKUs: {len(sku_master)}")



dates = pd.date_range(
                start=START_DATE,
                end=END_DATE,
                freq="D"
            )

calendar = pd.DataFrame({
                "date": dates
            })

calendar["week"] = (
                calendar["date"]
                .dt.isocalendar()
                .week
                .astype(int)
            )

calendar["month"] = (
                calendar["date"]
                .dt.month
            )


def get_season(month):

                if month in [12, 1, 2]:
                    return "Winter"

                elif month in [3, 4, 5]:
                    return "Spring"

                elif month in [6, 7, 8]:
                    return "Summer"

                else:
                    return "Autumn"


calendar["season"] = (
                calendar["month"]
                .apply(get_season)
            )


holiday_dates = pd.to_datetime([
                "2024-01-01",
                "2024-08-15",
                "2024-10-31",
                "2024-11-01",
                "2024-12-25",
                "2025-01-01",
                "2025-08-15",
                "2025-10-20",
                "2025-10-21",
                "2025-12-25"
            ])

calendar["is_holiday"] = (
                calendar["date"]
                .isin(holiday_dates)
                .astype(int)
            )

calendar["promo_event"] = "None"

promo_events = {
                "2024-01-01": "New Year Sale",
                "2024-05-01": "Summer Sale",
                "2024-08-15": "Independence Sale",
                "2024-10-25": "Festive Sale",
                "2024-11-25": "Black Friday",
                "2024-12-20": "Year End Sale",
                "2025-01-01": "New Year Sale",
                "2025-05-01": "Summer Sale",
                "2025-08-15": "Independence Sale",
                "2025-10-15": "Festive Sale",
                "2025-11-24": "Black Friday",
                "2025-12-20": "Year End Sale"
            }

for date, event in promo_events.items():

                calendar.loc[
                    calendar["date"] == pd.Timestamp(date),
                    "promo_event"
                ] = event

calendar.to_csv(
                RAW_DATA_DIR / "calendar.csv",
                index=False
            )

print("calendar.csv created")
print(f"Calendar rows: {len(calendar)}")


sales_records = []

sku_demand = {}

for sku_id in sku_master["sku_id"]:

                sku_demand[sku_id] = np.random.uniform(
                    5,
                    40
                )


for _, sku in sku_master.iterrows():

                sku_id = sku["sku_id"]

                launch_date = sku["launch_date"]

                list_price = sku["list_price"]

                sku_calendar = calendar[
                    calendar["date"] >= launch_date
                ]

                base_demand = sku_demand[sku_id]

                for _, day in sku_calendar.iterrows():

                    date = day["date"]

                    day_of_week = date.dayofweek

                    if day_of_week in [5, 6]:
                        weekly_factor = 1.20
                    else:
                        weekly_factor = 1.00

                    season = day["season"]

                    if season == "Winter":
                        seasonal_factor = 1.10

                    elif season == "Spring":
                        seasonal_factor = 0.95

                    elif season == "Summer":
                        seasonal_factor = 1.05

                    else:
                        seasonal_factor = 1.15

                    if day["is_holiday"] == 1:
                        holiday_factor = 1.30
                    else:
                        holiday_factor = 1.00

                    if day["promo_event"] != "None":

                        promo_flag = 1
                        promo_factor = 1.35

                    else:

                        promo_flag = 0
                        promo_factor = 1.00

                    random_factor = np.random.normal(
                        1.00,
                        0.15
                    )

                    random_factor = max(
                        random_factor,
                        0.50
                    )

                    expected_demand = (
                        base_demand
                        * weekly_factor
                        * seasonal_factor
                        * holiday_factor
                        * promo_factor
                        * random_factor
                    )

                    units_sold = max(
                        0,
                        int(round(expected_demand))
                    )

                    if promo_flag == 1:

                        unit_price = round(
                            list_price
                            * np.random.uniform(
                                0.85,
                                0.95
                            ),
                            2
                        )

                    else:

                        unit_price = round(
                            list_price
                            * np.random.uniform(
                                0.95,
                                1.00
                            ),
                            2
                        )

                    revenue = round(
                        units_sold * unit_price,
                        2
                    )

                    sales_records.append({
                        "date": date,
                        "sku_id": sku_id,
                        "units_sold": units_sold,
                        "revenue": revenue,
                        "unit_price": unit_price,
                        "promo_flag": promo_flag
                    })


sales_daily = pd.DataFrame(
                sales_records
            )

sales_daily = sales_daily.sort_values(
                ["date", "sku_id"]
            ).reset_index(drop=True)

sales_daily.to_csv(
                RAW_DATA_DIR / "sales_daily.csv",
                index=False
            )

print("sales_daily.csv created")
print(f"Sales rows: {len(sales_daily):,}")


inventory_records = []

sku_inventory_settings = {}

for _, sku in sku_master.iterrows():

                sku_id = sku["sku_id"]

                avg_daily_demand = sku_demand[sku_id]

                lead_time_days = int(
                    np.random.randint(5, 21)
                )

                safety_stock = int(
                    np.ceil(
                        avg_daily_demand * 5
                    )
                )

                reorder_point = int(
                    np.ceil(
                        avg_daily_demand * lead_time_days
                        + safety_stock
                    )
                )

                initial_stock = int(
                    np.ceil(
                        avg_daily_demand
                        * np.random.uniform(20, 45)
                    )
                )

                sku_inventory_settings[sku_id] = {
                    "lead_time_days": lead_time_days,
                    "reorder_point": reorder_point,
                    "initial_stock": initial_stock
                }


for _, sku in sku_master.iterrows():

                sku_id = sku["sku_id"]

                settings = sku_inventory_settings[sku_id]

                lead_time_days = settings["lead_time_days"]

                reorder_point = settings["reorder_point"]

                on_hand = settings["initial_stock"]

                on_order = 0

                sku_sales = sales_daily[
                    sales_daily["sku_id"] == sku_id
                ].sort_values("date")

                pending_orders = []

                for _, sale in sku_sales.iterrows():

                    date = sale["date"]

                    units_sold = int(
                        sale["units_sold"]
                    )

                    received_today = 0

                    remaining_orders = []

                    for order in pending_orders:

                        if order["arrival_date"] <= date:

                            received_today += order["quantity"]

                        else:

                            remaining_orders.append(
                                order
                            )

                    pending_orders = remaining_orders

                    on_order = sum(
                        order["quantity"]
                        for order in pending_orders
                    )

                    on_hand += received_today

                    actual_sales = min(
                        units_sold,
                        on_hand
                    )

                    on_hand -= actual_sales

                    inventory_position = (
                        on_hand
                        + on_order
                    )

                    if inventory_position <= reorder_point:

                        order_quantity = int(
                            np.ceil(
                                sku_demand[sku_id]
                                * 30
                            )
                        )

                        arrival_date = (
                            date
                            + pd.Timedelta(
                                days=lead_time_days
                            )
                        )

                        pending_orders.append({
                            "quantity": order_quantity,
                            "arrival_date": arrival_date
                        })

                        on_order += order_quantity

                    inventory_records.append({
                        "date": date,
                        "sku_id": sku_id,
                        "on_hand_units": int(on_hand),
                        "on_order_units": int(on_order),
                        "lead_time_days": int(lead_time_days),
                        "reorder_point": int(reorder_point)
                    })


inventory_snapshots = pd.DataFrame(
                inventory_records
            )

inventory_snapshots = inventory_snapshots.sort_values(
                ["date", "sku_id"]
            ).reset_index(drop=True)
inventory_snapshots.to_csv(
                RAW_DATA_DIR / "inventory_snapshots.csv",
                index=False
            )

print("inventory_snapshots.csv created")
print( f"Inventory rows: {len(inventory_snapshots):,}"
            )


duplicate_skus = (
                sku_master["sku_id"]
                .duplicated()
                .sum()
            )

print("\nSKU MASTER")
print(
                "Duplicate SKU IDs:",
                duplicate_skus
            )


print("\nCALENDAR")
print(
                "Rows:",
                len(calendar)
            )

print(
                "Duplicate dates:",
                calendar["date"].duplicated().sum()
            )


unknown_sales_skus = (
                ~sales_daily["sku_id"]
                .isin(sku_master["sku_id"])
            ).sum()

duplicate_sales = (
                sales_daily
                .duplicated(["date", "sku_id"])
                .sum()
            )

print("\nSALES DAILY")

print(
                "Rows:",
                f"{len(sales_daily):,}"
            )

print(
                "Duplicate date + SKU:",
                duplicate_sales
            )

print(
                "Unknown SKUs:",
                unknown_sales_skus
            )

print(
                "Negative units:",
                (
                    sales_daily["units_sold"] < 0
                ).sum()
            )

print(
                "Negative revenue:",
                (
                    sales_daily["revenue"] < 0
                ).sum()
            )


unknown_inventory_skus = (
                ~inventory_snapshots["sku_id"]
                .isin(sku_master["sku_id"])
            ).sum()
duplicate_inventory = (
                inventory_snapshots
                .duplicated(["date", "sku_id"])
                .sum()
            )

print("\nINVENTORY SNAPSHOTS")

print(
                "Rows:",
                f"{len(inventory_snapshots):,}"
            )

print(
                "Duplicate date + SKU:",
                duplicate_inventory
            )

print(
                "Unknown SKUs:",
                unknown_inventory_skus
            )

print(
                "Negative on-hand:",
                (
                    inventory_snapshots["on_hand_units"] < 0
                ).sum()
            )

print(
                "Negative on-order:",
                (
                    inventory_snapshots["on_order_units"] < 0
                ).sum()
            )


print("\nBUSINESS SUMMARY")

print(
                "Sales date range:",
                sales_daily["date"].min(),
                "to",
                sales_daily["date"].max()
            )

print(
                "Total units sold:",
                f"{sales_daily['units_sold'].sum():,}"
            )

print(
                "Total revenue:",
                f"₹{sales_daily['revenue'].sum():,.2f}"
            )

print(
                "Average daily units sold:",
                round(
                    sales_daily["units_sold"].mean(),
                    2
                )
            )

print("\nPromotion records:")

print(
                sales_daily["promo_flag"]
                .value_counts()
            )

print("\nTop 5 SKUs by units sold:")

top_skus = (
                sales_daily
                .groupby("sku_id")["units_sold"]
                .sum()
                .sort_values(
                    ascending=False
                )
                .head(5)
            )

print(top_skus)
print("\nRAW DATA GENERATION COMPLETE")

print("""
            Created files:

            1. Data/raw/sku_master.csv
            2. Data/raw/calendar.csv
            3. Data/raw/sales_daily.csv
            4. Data/raw/inventory_snapshots.csv """)

print("All four raw datasets are ready.")