import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True,exist_ok=True)

print("=" * 60)
print("CREATING SKU MASTER")
print("=" * 60)

NUM_SKUS = 100

categories = {"Furniture":["Chair","Table","Shelf","Sofa"],
              "Kitchen":["Cookware","Storage","Dinnerware","Appliances"],
              "Home Decor":["Wall Decor","Vase","Candle","Decorative Item"],
              "Bedding":["Bedsheet","Pillow","Blanket","Comforter"],
              "Lighting":["Table Lamp","Floor Lamp","Celling Light","Pendant"],
              "Bath":["Towel","Bath Mat","Shower Curtain","Storage"]}

sku_records = []

category_names = list(categories.keys())

for i in range(1, NUM_SKUS + 1):
    sku_id = f"SKU{i:03d}"

    category = np.random.choice(category_names)
    subcategory = np.random.choice(categories[category])

    launch_date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=np.random.randint(0,365))

    unit_cost = round(np.random.uniform(300, 5000),2)
    markup = np.random.uniform(1.3,2.2)

    list_price = round(unit_cost * markup,2)

    sku_records.append({
        "sku_id": sku_id,
        "category": category,
        "subcategory": subcategory,
        "launch_date": launch_date,
        "unit_cost": unit_cost,
        "list_price": list_price
    }) 

sku_master = pd.DataFrame(sku_records)
sku_master = sku_master.sort_values("sku_id").reset_index(drop=True)
sku_master.to_csv(RAW_DATA_DIR / "sku_master.csv", index=False)
print("sku_master.csv created")
print(f" Number of SKUs:{len(sku_master)}")

print()
print("=" * 60)
print("CREATING CALENDAR")
print("=" * 60)

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"
dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
calendar = pd.DataFrame({"date": dates})
calendar["week"] = calendar["date"].dt.isocalendar().week.astype(int)
calendar["month"] = calendar["date"].dt.month

def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    return "Autumn"

calendar["season"] = calendar["month"].apply(get_season)

holiday_dates = pd.to_datetime([
    "2024-01-01", "2024-08-15", "2024-10-31", "2024-11-01", "2024-12-25",
    "2025-01-01", "2025-08-15", "2025-10-20", "2025-10-21", "2025-12-25",
])
calendar["is_holiday"] = calendar["date"].isin(holiday_dates).astype(int)

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
            "2025-10-25": "Festive Sale",
            "2025-11-25": "Black Friday",
            "2025-12-20": "Year End Sale",
}

for date, event in promo_events.items():
    calendar.loc[calendar["date"] == pd.Timestamp(date), "promo_event"] = event
    calendar_file = (RAW_DATA_DIR / "calendar.csv")

calendar.to_csv(RAW_DATA_DIR / "calendar.csv", index=False)
print("calendar.csv created")
print(f" Calendar rows:{len(calendar)}")


print()
print("=" * 60)
print("CREATING SALES DAILY")
print("=" * 60)

sales_records = []
sku_demand = {
    sku_id: np.random.uniform(5, 40)
    for sku_id in sku_master["sku_id"]
}

for _, sku in sku_master.iterrows():
    sku_id = sku["sku_id"]
    launch_date = sku["launch_date"]
    list_price = sku["list_price"]
    sku_calendar = calendar[calendar["date"] >= launch_date]
    base_demand = sku_demand[sku_id]

    for _, day in sku_calendar.iterrows():

            date = day["date"]

            day_of_week = date.dayofweek

            if day_of_week in [5, 6]:

                weekly_factor = 1.20

            else:
                weekly_factor = 1.00

            season = day["season"]
            seasonal_factor = {
                "Winter": 1.10,
                "Spring": 0.95,
                "Summer": 1.05,
            }.get(season, 1.15)
            holiday_factor = 1.30 if day["is_holiday"] == 1 else 1.00
            promo_flag = int(day["promo_event"] != "None")
            promo_factor = 1.35 if promo_flag else 1.00
            random_factor = max(np.random.normal(1.00, 0.15), 0.50)
            expected_demand = (
                base_demand * weekly_factor * seasonal_factor
                * holiday_factor * promo_factor * random_factor
            )
            units_sold = max(0, int(round(expected_demand)))
            price_factor = np.random.uniform(0.85, 0.95) if promo_flag else np.random.uniform(0.95, 1.00)
            unit_price = round(list_price * price_factor, 2)
            revenue = round(units_sold * unit_price, 2)
            sales_records.append({
                "date": date,
                "sku_id": sku_id,
                "units_sold": units_sold,
                "revenue": revenue,
                "unit_price": unit_price,
                "promo_flag": promo_flag,
            })

sales_daily = pd.DataFrame(sales_records).sort_values(
    ["date", "sku_id"]
).reset_index(drop=True)
sales_file = RAW_DATA_DIR / "sales_daily.csv"
sales_daily.to_csv(sales_file, index=False)
print("sales_daily.csv created")




print()
print("=" * 60)
print("DATA GENERATION COMPLETED")
print("=" * 60)


print()
print("Files created:")

print("1. data/raw/sku_master.csv")
print("2. data/raw/calendar.csv")
print("3. data/raw/sales_daily.csv")


duplicate_skus = (
    sku_master["sku_id"]
    .duplicated()
    .sum()
)


print()
print("SKU validation:")
print(
    f"Duplicate SKU IDs: {duplicate_skus}"
)


missing_sku_sales = (
    ~sales_daily["sku_id"]
    .isin(sku_master["sku_id"])
).sum()


print()
print("Sales validation:")
print(
    f"Sales rows: {len(sales_daily)}"
)

print(
    f"Sales with unknown SKU: {missing_sku_sales}"
)


print()
print("Sales date range:")

print(
    sales_daily["date"].min(),
    "to",
    sales_daily["date"].max()
)


print()
print("Total units sold:")

print(
    f"{sales_daily['units_sold'].sum():,}"
)

print()
print("Total revenue:")

print(
    f"â‚¹{sales_daily['revenue'].sum():,.2f}"
)


print()
print("Promotion records:")

print(
    sales_daily["promo_flag"]
    .value_counts()
)


print()
print("First 5 sales records:")

print(
    sales_daily.head()
)


print()
print("=" * 60)
print("READY FOR NEXT STEP")
print("=" * 60)

              


    
