import pandas as pd
import numpy as np
import pathlib as Path

np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

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

    output_file = RAW_DATA_DIR / "sku_master.csv"

    sku_master.to_csv(output_file,index=False)

    print("SKU Master created successfully!")
    print(f"File: {output_file}")
    print(f"Number of SKUs: {len(sku_master)}")
    print(f"Duplicate SKU IDs:{sku_master["sku_id"].duplicated().sum()}")
    print("\nColumns:")
    print(sku_master.columns.tolist())

    print("\nFirst 5 rows:")
    print(sku_master.head())


    