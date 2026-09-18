import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RISK_FILE = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "risk"
    / "inventory_risk_scores.csv"
)

FORECAST_FILE = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "forecast"
    / "weekly_forecast.csv"
)

SKU_FILE = (
    PROJECT_ROOT
    / "Data"
    / "raw"
    / "sku_master.csv"
)

st.set_page_config(
    page_title="FORESIGHT Planning Dashboard",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_risk_data():

    df = pd.read_csv(RISK_FILE)

    df["sku_id"] = df["sku_id"].astype(str)

    numeric_columns = [
        "stockout_risk_score",
        "overstock_risk_score",
        "value_at_stake"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

    return df


@st.cache_data
def load_forecast_data():

    df = pd.read_csv(FORECAST_FILE)

    df["sku_id"] = df["sku_id"].astype(str)

    if "forecast_date" in df.columns:

        df["forecast_date"] = pd.to_datetime(
            df["forecast_date"],
            errors="coerce",
            dayfirst=True
        )

    if "forecast_units" in df.columns:

        df["forecast_units"] = pd.to_numeric(
            df["forecast_units"],
            errors="coerce"
        ).fillna(0)

    return df


@st.cache_data
def load_sku_data():

    df = pd.read_csv(SKU_FILE)

    df["sku_id"] = df["sku_id"].astype(str)

    return df


try:

    risk_df = load_risk_data()
    forecast_df = load_forecast_data()
    sku_df = load_sku_data()

except FileNotFoundError as e:

    st.error(
        "Required project file was not found."
    )

    st.code(str(e))

    st.stop()


if "category" in sku_df.columns:

    category_data = (
        sku_df[
            ["sku_id", "category"]
        ]
        .drop_duplicates()
    )

    risk_df = risk_df.merge(
        category_data,
        on="sku_id",
        how="left"
    )


st.title("📊 Project FORESIGHT")

st.subheader(
    "Demand Forecasting & Inventory Planning Dashboard"
)

st.write(
    "FORESIGHT helps identify inventory risks, "
    "prioritize SKUs, and support replenishment "
    "and markdown decisions."
)


st.sidebar.header("🔎 Filters")


if "category" in risk_df.columns:

    categories = sorted(
        risk_df["category"]
        .dropna()
        .unique()
    )

    selected_categories = st.sidebar.multiselect(
        "Category",
        options=categories,
        default=[]
    )

else:

    selected_categories = []


all_skus = sorted(
    risk_df["sku_id"]
    .dropna()
    .unique()
)

selected_skus = st.sidebar.multiselect(
    "SKU",
    options=all_skus,
    default=[]
)


actions = sorted(
    risk_df["action"]
    .dropna()
    .unique()
)

selected_actions = st.sidebar.multiselect(
    "Recommended Action",
    options=actions,
    default=[]
)


filtered_df = risk_df.copy()


if selected_categories:

    filtered_df = filtered_df[
        filtered_df["category"].isin(
            selected_categories
        )
    ]


if selected_skus:

    filtered_df = filtered_df[
        filtered_df["sku_id"].isin(
            selected_skus
        )
    ]


if selected_actions:

    filtered_df = filtered_df[
        filtered_df["action"].isin(
            selected_actions
        )
    ]


st.markdown("---")

st.header("📌 Inventory Overview")


total_skus = (
    filtered_df["sku_id"]
    .nunique()
)


healthy_count = (
    filtered_df["action"]
    .eq("Healthy")
    .sum()
)


watch_count = (
    filtered_df["action"]
    .str.contains(
        "Watch",
        case=False,
        na=False
    )
    .sum()
)


markdown_count = (
    filtered_df["action"]
    .str.contains(
        "Markdown",
        case=False,
        na=False
    )
    .sum()
)


reorder_count = (
    filtered_df["action"]
    .str.contains(
        "Reorder",
        case=False,
        na=False
    )
    .sum()
)


total_value = (
    filtered_df["value_at_stake"]
    .sum()
)


col1, col2, col3, col4, col5, col6 = st.columns(6)


col1.metric(
    "Total SKUs",
    total_skus
)

col2.metric(
    "Healthy",
    healthy_count
)

col3.metric(
    "Watch / Volatile",
    watch_count
)

col4.metric(
    "Markdown / Clear",
    markdown_count
)

col5.metric(
    "Reorder Now",
    reorder_count
)

col6.metric(
    "Value at Stake",
    f"₹{total_value:,.0f}"
)


st.markdown("---")

st.header(
    "🎯 Inventory Risk Decision Grid"
)

st.write(
    "Each SKU is positioned using its actual "
    "stockout and overstock risk scores. "
    "The dashed lines represent the 50-point "
    "high-risk threshold."
)


risk_grid = filtered_df.copy()


risk_grid["stockout_risk_score"] = pd.to_numeric(
    risk_grid["stockout_risk_score"],
    errors="coerce"
).fillna(0)


risk_grid["overstock_risk_score"] = pd.to_numeric(
    risk_grid["overstock_risk_score"],
    errors="coerce"
).fillna(0)


fig, ax = plt.subplots(
    figsize=(12, 7)
)


markers = {
    "Healthy": "o",
    "Reorder Now": "^",
    "Markdown / Clear": "s",
    "Watch / Volatile": "D"
}


for action, marker in markers.items():

    action_data = risk_grid[
        risk_grid["action"] == action
    ]

    if action_data.empty:
        continue

    ax.scatter(
        action_data["stockout_risk_score"],
        action_data["overstock_risk_score"],
        marker=marker,
        s=75,
        alpha=0.6,
        label=f"{action} ({len(action_data)})"
    )


ax.axvline(
    x=50,
    linestyle="--",
    linewidth=1.5
)

ax.axhline(
    y=50,
    linestyle="--",
    linewidth=1.5
)


ax.text(
    20,
    90,
    "MARKDOWN / CLEAR",
    ha="center",
    fontweight="bold"
)


ax.text(
    80,
    90,
    "WATCH / VOLATILE",
    ha="center",
    fontweight="bold"
)


ax.text(
    20,
    10,
    "HEALTHY",
    ha="center",
    fontweight="bold"
)


ax.text(
    80,
    10,
    "REORDER NOW",
    ha="center",
    fontweight="bold"
)


ax.set_xlim(
    0,
    100
)

ax.set_ylim(
    0,
    100
)


ax.set_xlabel(
    "Stockout Risk Score"
)

ax.set_ylabel(
    "Overstock Risk Score"
)


ax.set_title(
    "FORESIGHT Inventory Risk Decision Grid"
)


ax.legend(
    title="Recommended Action",
    loc="upper left"
)


ax.grid(
    alpha=0.2
)


st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


st.markdown("---")

st.header(
    "⚠️ Risk Distribution"
)


action_summary = (
    filtered_df["action"]
    .value_counts()
    .rename_axis("Action")
    .reset_index(
        name="SKU Count"
    )
)


if not action_summary.empty:

    st.bar_chart(
        action_summary.set_index(
            "Action"
        )
    )

else:

    st.info(
        "No risk data matches the selected filters."
    )


st.markdown("---")

st.header(
    "🚨 Priority SKU List"
)


priority_df = (
    filtered_df
    .sort_values(
        "value_at_stake",
        ascending=False
    )
    .copy()
)


display_columns = [
    "sku_id",
    "category",
    "stockout_risk",
    "overstock_risk",
    "stockout_risk_score",
    "overstock_risk_score",
    "action",
    "value_at_stake"
]


available_columns = [
    column
    for column in display_columns
    if column in priority_df.columns
]


if not priority_df.empty:

    st.dataframe(
        priority_df[
            available_columns
        ].head(20),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No SKUs match the selected filters."
    )


st.markdown("---")

st.header(
    "📈 Weekly Demand Forecast"
)


forecast_display = forecast_df.copy()


filtered_skus = (
    filtered_df["sku_id"]
    .dropna()
    .unique()
)


forecast_display = forecast_display[
    forecast_display["sku_id"].isin(
        filtered_skus
    )
]


if not forecast_display.empty:

    forecast_chart = (
        forecast_display
        .groupby("forecast_date")[
            "forecast_units"
        ]
        .sum()
        .sort_index()
    )


    st.line_chart(
        forecast_chart,
        height=350
    )


    st.subheader(
        "Forecast Details"
    )


    st.dataframe(
        forecast_display.sort_values(
            [
                "sku_id",
                "forecast_date"
            ]
        ),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No forecast data matches the selected filters."
    )


st.markdown("---")

st.header(
    "💡 Recommended Business Actions"
)


action_col1, action_col2 = st.columns(2)


with action_col1:

    st.info(
        """
        **🔄 Reorder Now**

        Prioritize SKUs with high stockout risk
        and low overstock risk.
        """
    )


    st.warning(
        """
        **👀 Watch / Volatile**

        Monitor SKUs where both stockout and
        overstock risks are high.
        """
    )


with action_col2:

    st.warning(
        """
        **🏷️ Markdown / Clear**

        Review SKUs with high overstock risk
        and low stockout risk.
        """
    )


    st.success(
        """
        **✅ Healthy**

        SKUs with low stockout and low
        overstock risk require no immediate action.
        """
    )


st.markdown("---")

st.header(
    "📋 Dashboard Summary"
)


summary_col1, summary_col2, summary_col3 = st.columns(3)


with summary_col1:

    st.metric(
        "SKUs Requiring Attention",
        watch_count + markdown_count + reorder_count
    )


with summary_col2:

    attention_value = (
        filtered_df[
            filtered_df["action"] != "Healthy"
        ]["value_at_stake"]
        .sum()
    )

    st.metric(
        "Value Requiring Attention",
        f"₹{attention_value:,.0f}"
    )


with summary_col3:

    if total_skus > 0:

        healthy_percentage = (
            healthy_count
            / total_skus
        ) * 100

    else:

        healthy_percentage = 0

    st.metric(
        "Healthy SKU %",
        f"{healthy_percentage:.1f}%"
    )


st.caption(
    "Project FORESIGHT | NorthBay Living | D5 Planning Dashboard"
)