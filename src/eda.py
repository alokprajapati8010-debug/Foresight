import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT /"Data" / "processed" / "analysis_ready.csv"

OUTPUT_DIR = PROJECT_ROOT / "reports" /"eda"
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

def load_data():
    print("=" * 60)
    print("PROJECT FORESIGHT - D2 EDA")
    print("=" * 60)
    print("\nLoading analysis-ready dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {len(df):,}")
    print(f"Columns:{len(df.columns)}")

    print("\nColumn:")
    for column in df.columns:
        print(f" - {column}")

        return df

    def prepare_data(df):

        print("\nPreparing data...")

        if "data" in df.columns:
            df["data"] = pd.to_datatime(df["data"],error="coerce")
            numeric_columns = [
                "units_sold",
                "revenue",
                "unit_price",
                "on_hand_units",
                "on_order_units",
                "lead_time_days",
                "reorder_point",
                "unit_cost",
                "list_price"
            ]

            for column in numeric_columns:
                if column in df.columns:
                    df[column] = pd.to_numeric(df[column],errors="coerce")
                    return df

                def data_quality(df):
                    print("\n" + "=" * 60)
                    print("1. DATA QUALITY CHECK")
                    print("=" * 60)

                    print("\nMissing values:")

                    missing = df.isnull().sum()
                    missing = missing[missing > 0]
                    if len(missing) == 0:
                        print("No missing values found.")
                    else:
                        print(missing)

                    print("\nDuplicate rows:")
                    print(df.duplicated().sum())

                    if "sku_id" in df.columns:
                        print("\nUnique SKUs:")
                        print(df["sku_id"].unique())

                    if "date" in df.columns:
                        print("\nDate range:")
                        print(df["date"].min())
                        print("to")
                        print(df["date"].max())

            def demand_summary(df):

                print("\n" + "=" * 60)
                print("2. DEMAND SUMMARY")
                print("=" *60)

                if "units_sold" not in df.columns:
                    print("units_sold column not found.")
                    return
                print(f"\nTotal units sold:{df['units_sold'].sum():,.0f}")

                if "revenue" in df.columns:
                    print(f"Total revenue: ₹{df['revenue'].sum():,.2f}")
                    print(f"Average units sold per record: {df['units_sold'].mean():.2f}")
                    print("\nTop 10 SKUs by units sold:")

                if "sku_id" in df.columns:
                    top_skus = (
                        df.groupby("sku_id")["units_sold"].sum().sort_values(ascending=False).head(10)
                    )
                    print(top_skus)

            def plot_daily_demand(df):
                if "date" not in df.columns or "units_sold" not in df.columns:
                    return 
                daily = ( df.groupby("date")["units_sold"].sum().reset_index()
                )
                plt.figure(figsize=(12, 6))
                plt.plot(
                    daily["date"],
                    daily["units_sold"]
                )

                plt.title("Daily Demand Trend")
                plt.xlabel("Date")
                plt.ylabel("units Sold")

                plt .xticks(rotation=45)

                plt.tight_layout()

                output = OUTPUT_DIR / "01_daily_demand_trend.png"
                plt.savefig(output, dpi=150)

                plt.close()

                print(f"\nCraeted: {output}")

            def plot_montly_demand(df):
                if "date" not in df.columns or "units_sold" not in df.columns:
                    return 

                temp = df.copy()

                temp["month"] = temp["date"].dt.to_period("M")

                montly = (
                    temp.groupby("month")["units_sold"].sum().reset_index()
                )
                montly["month"] = montly["month"].astype(str)

                plt.figure(figsize=(12, 6))
                plt.plot(
                    montly["month"],
                    montly["units_sold"],
                    marker = "o"
                )
                plt.title("Monthly Demand Trend")
                plt.xlabel("Month")
                plt.ylabel("Units Sold")

                plt.xticks(rotation = 90)

                plt.tight_layout()

                output = OUTPUT_DIR / "02_monthly_demand_trend.png"
                plt.savefig(output, dpi=150)
                plt.close()

                print(f"Created: {output}")

            def plot_top_sku(df):

                if "sku_id" not in df.columns or "units_sold" not in df.columns:
                    return

                top = (
                    df.groupby("sku_id")["units_sold"].sum().sort_values(ascending = False).head(10).sort_values()
                )

                plt.figure(figsize=(10, 6))

                plt.barh(
                    top.index,
                    top.values
                )
                plt.title("Top 10 SKUs by Units sold")
                plt.xlabel("Total Units Sold")
                plt.ylabel("SKU")

                plt.tight_layout()

                output = OUTPUT_DIR / "03_top_10_skus.png"

                plt.savefig(output, dpi=150)

                plt.close()

                print(f"Created: {output}")

            def category_analysis(df):

                if "category" not in df.columns:
                    print("\nCategory column not found.")
                    return
                if "units_sold" not in df.columns:
                 return
                print("\n" + "=" * 60)
                print("3 CATEGORY ANALYSIS")
                print("=" * 60)

                category_sales = (
                    df.groupby("category").agg(
                        total_units = ("units_sold","sum"),total_revenue = ("revenue","sum")
                        if "revenue" in df.columns
                        else("units_sold","sum")
                    )
                    .sort_values(
                        "total_units",
                        ascending = False
                    )
                )

                print("\nCategory performance:")
                print(category_sales)

                category_sales.to_csv(
                    OUTPUT_DIR / "category_summary.csv")

            def plot_category_demand(df):
                if  "category" not in df.columns:
                    return

                if "units_sold" not in df.columns:
                    return

                category = (
                    df.groupby("category")["units_sold"].sum().sort_values(ascending = False)
                )

                plt.figure(figsize=(10, 6))
                plt.bar(
                    category.index,
                    category.values
                )
                plt.title("Demand by Category")
                plt.xlabel("Category")
                plt.ylabel("Units Sold")

                plt.xticks(rotation=45)

                plt.tight_layout()
                output = OUTPUT_DIR / "04_category_demand.png"

                plt.savefig(output, dpi=150)

                plt.close()

                print(f"Created: {output}")

            def promotion_analysis(df):

                if "promo_flag" not in df.columns:
                    print("\nPromotion columns not founs.")
                    return

                if "units_sold" not in df.columns:
                    return

                print("\n" + "=" * 60)
                print("4. PROMOTION ANALYSIS")
                print("=" * 60)

                promotion = (
                    df.groupby("promo_flag").agg(
                        average_units = ("units_sold", "mean"),
                        total_units = ("units_sold","sum"),
                        records = ("units_sold","count")
                    )
                )

                print("\nPromotion performance:")
                print(promotion)

                promotion.to_csv(
                    OUTPUT_DIR / "promotion_summary.csv"
                )

            def dead_stock_analysis(df):

                if "sku_id" not in df.columns:
                    return

                if "units_sold" not in df.columns:
                    return

                print("\n" + "=" * 60)
                print("5. SLOW MOVERS / DEAD STOCK")
                print("=" * 60)

                sku_demand = (
                    df.groupby("sku_id")["units_sold"].sum().sort_values()
                )

                print("\nBottom 10 SKUs by total units sold:")

                print(sku_demand.head(10))

                sku_demand.head(10).to_csv(
                    OUTPUT_DIR / "bottom_10_skus.csv"
                )

            def inventory_analysis(df):

                if "on_hand_units" not in df.columns:
                    print("\nInventory columns not found.")
                    return

                print("\n" + "=" * 60)
                print("6. INVENTORY ANALYSIS")
                print("=" * 60)

                inventory_columns = [
                    column
                    for columns in [
                        "on_hand_units",
                        "on_order_units",
                        "reorder_point"
                    ]
                    if column in df.columns
                ]
                print("\nInventory summary:")

                print(
                    df[inventory_columns].describe()
                )

                if "reorder_point" in df.coiumns:

                    below_reorder = (
                        df["on_hand_units"]
                        < df["reorder_point"]
                    )

                    print(
                        "\nRecords below reorder point:",
                        below_reorder.sum()
                    )

                def generate_business_summary(df):

                    print("\n" + "=" * 60)
                    print("7. BUSINESS SUMMARY")
                    print("=" * 60)

                    if "units_sold" in df.columns:

                        top_sku = (
                            df.groupby("sku_id")["units_sold"].sum().idmax()
                        )

                        top_units = (
                            df.groupby("sku_id")["units_sold"].sum().max()
                        )

                        print(f"\nTop-selling SKU:{top_sku}")
                        print(f"Units sold by top SKU:{top_units:,.0f}")

                        if "category" in df.columns:

                            category = ( df.groupby("category")["units_sold"].sum().idmax()
                            )

                            print(
                                f"Highest-demand category: {category}"
                            )

                            if "promo_flag" in df.columns:

                                promo = df[df["promo_flag"]==1]

                                non_promo = df[df["promo_flag"] == 0]

                                if len(promo) > 0 and  len(non_promo) > 0:

                                    promo_avg = promo["units_sold"].mean()
                                    non_promo_avg = non_promo["units_sold"].mean()

                                    print(f"\nAverage units during promotion:"
                                          f"{promo_avg:.2f}")

                                    print(f"Average units without promotion: " f"{non_promo_avg:.2f}")

                    def main():

                        df = load_data()
                        df = prepare_data(df)
                        data_quality(df)
                        demand_summary(df)
                        plot_daily_demand(df)
                        plot_montly_demand(df)
                        plot_top_sku(df)
                        category_analysis(df)
                        plot_category_demand(df)
                        promotion_analysis(df)
                        dead_stock_analysis(df)
                        inventory_analysis(df)
                        generate_business_summary(df)

                        print("\n" + "=" * 60)
                        print("D2 INITAL EDA COMPLETED")
                        print("=" * 60)

                        print(f"\nEDA outputs saved in:\n{OUTPUT_DIR}")

                        if __name__ == "__main__":
                            main()

                              
                
