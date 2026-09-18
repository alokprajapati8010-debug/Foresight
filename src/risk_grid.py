import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "risk"
    / "inventory_risk_scores.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "risk"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_risk_data():

    print("Loading risk scoring data...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    required_columns = [
        "sku_id",
        "stockout_risk",
        "overstock_risk",
        "stockout_risk_score",
        "overstock_risk_score",
        "action",
        "value_at_stake"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    return df


def create_risk_grid(df):

    print("\nCreating stockout vs overstock risk grid...")

    plt.figure(figsize=(14, 9))

    actions = [
        "Reorder Now",
        "Markdown / Clear",
        "Watch / Volatile",
        "Healthy"
    ]

    markers = {
        "Reorder Now": "o",
        "Markdown / Clear": "s",
        "Watch / Volatile": "^",
        "Healthy": "x"
    }

    for action in actions:

        data = df[df["action"] == action].copy()

        if len(data) == 0:
            continue

        plt.scatter(
            data["stockout_risk_score"],
            data["overstock_risk_score"],
            marker=markers[action],
            s=90,
            alpha=0.55,
            edgecolors="black",
            linewidths=0.5,
            label=f"{action} ({len(data)})"
        )

    plt.axvline(
        x=50,
        linestyle="--",
        linewidth=1.5
    )

    plt.axhline(
        y=50,
        linestyle="--",
        linewidth=1.5
    )

    plt.text(
        25,
        90,
        "MARKDOWN / CLEAR",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold"
    )

    plt.text(
        75,
        90,
        "WATCH / VOLATILE",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold"
    )

    plt.text(
        25,
        10,
        "HEALTHY",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold"
    )

    plt.text(
        75,
        10,
        "REORDER NOW",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold"
    )

    plt.xlabel(
        "Stockout Risk Score",
        fontsize=12
    )

    plt.ylabel(
        "Overstock Risk Score",
        fontsize=12
    )

    plt.title(
        "Project FORESIGHT - Inventory Risk Decision Grid",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlim(0, 100)
    plt.ylim(0, 100)

    plt.legend(
        title="Recommended Action",
        loc="upper left"
    )

    plt.grid(
        alpha=0.25
    )

    plt.tight_layout()

    output_file = (
        OUTPUT_DIR
        / "inventory_risk_grid.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("\nRisk grid created:")
    print(output_file)


def create_priority_table(df):

    print("\nCreating priority table...")

    priority = (
        df[
            [
                "sku_id",
                "stockout_risk",
                "overstock_risk",
                "stockout_risk_score",
                "overstock_risk_score",
                "action",
                "value_at_stake"
            ]
        ]
        .sort_values(
            "value_at_stake",
            ascending=False
        )
    )

    output_file = (
        OUTPUT_DIR
        / "priority_sku_list.csv"
    )

    priority.to_csv(
        output_file,
        index=False
    )

    print("Priority table created:")
    print(output_file)


def print_action_summary(df):

    print("\nAction Summary:")

    summary = (
        df["action"]
        .value_counts()
    )

    for action in [
        "Reorder Now",
        "Markdown / Clear",
        "Watch / Volatile",
        "Healthy"
    ]:

        count = summary.get(action, 0)

        print(
            f"{action}: {count}"
        )


def main():

    print("=" * 60)
    print("PROJECT FORESIGHT - D4 RISK GRID")
    print("=" * 60)

    df = load_risk_data()

    print_action_summary(df)

    create_risk_grid(df)

    create_priority_table(df)

    print("\n" + "=" * 60)
    print("D4 RISK GRID COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()