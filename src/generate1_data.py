import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

RAW_DATA_DIR = Path(__file__).resolve().parent

RAW_DATA_DIR.mkdir(parents=True,exist_ok=True)

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
        "Launch_date": launch_date,
        "unit_cost": unit_cost,
        "list_price": list_price
    }) 

sku_master = pd.DataFrame(sku_records)
sku_master = sku_master.sort_values("sku_id").reset_index(drop=True)
sku_master.to_csv(RAW_DATA_DIR / "sku_master.csv", index=False)
print("sku_master.csv created")

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

calendar.to_csv(RAW_DATA_DIR / "calendar.csv", index=False)
print("calendar.csv created")

print("\nData generation completed successfully!")
print("\nFiles created:")
print("1. Data/raw/sku_master.csv")
print("2. Data/raw/calendar.csv")
print("\nCalendar rows:", len(calendar))
print("SKU rows:", len(sku_master))



    
