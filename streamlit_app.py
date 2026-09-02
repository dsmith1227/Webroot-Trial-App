import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Product Peer Analytics",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# Data Loading
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("product_metrics.csv")

df = load_data()

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("Peer Analysis")

products = sorted(df["product_id"].unique())

selected_product = st.sidebar.selectbox(
    "Primary Product",
    products
)

peer_products = st.sidebar.multiselect(
    "Peer Products",
    products,
    default=[p for p in products if p != selected_product][:5]
)

comparison_set = [selected_product] + peer_products

filtered = df[df["product_id"].isin(comparison_set)]

# --------------------------------------------------
# KPI calculations
# --------------------------------------------------

latest_month = filtered["month"].max()

latest = filtered[filtered["month"] == latest_month]

current_product = latest[
    latest["product_id"] == selected_product
]

if len(current_product):

    row = current_product.iloc[0]

    conversion_rate = (
        row["conversions"] / row["trial_starts"] * 100
        if row["trial_starts"] else 0
    )

    opt_out_rate = (
        row["opt_outs"] / row["trial_starts"] * 100
        if row["trial_starts"] else 0
    )

    st.title("📈 Product Peer Analysis Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Revenue",
        f"${row['revenue']:,.0f}"
    )

    col2.metric(
        "TCV",
        f"${row['tcv']:,.0f}"
    )

    col3.metric(
        "Conversion Rate",
        f"{conversion_rate:.1f}%"
    )

    col4.metric(
        "Opt Out Rate",
        f"{opt_out_rate:.1f}%"
    )

# --------------------------------------------------
# Revenue Trend
# --------------------------------------------------

st.subheader("Revenue Trend")

fig = px.line(
    filtered,
    x="month",
    y="revenue",
    color="product_id",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TCV Trend
# --------------------------------------------------

st.subheader("TCV Trend")

fig = px.line(
    filtered,
    x="month",
    y="tcv",
    color="product_id",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Conversion Benchmark
# --------------------------------------------------

st.subheader("Conversion Rate Benchmark")

benchmark_df = latest.copy()

benchmark_df["conversion_rate"] = (
    benchmark_df["conversions"] /
    benchmark_df["trial_starts"]
) * 100

fig = px.bar(
    benchmark_df.sort_values(
        "conversion_rate",
        ascending=False
    ),
    x="product_id",
    y="conversion_rate",
    color="conversion_rate",
    text_auto=".1f"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Revenue vs Audience
# --------------------------------------------------

st.subheader("Revenue vs Audience")

fig = px.scatter(
    latest,
    x="audience_size",
    y="revenue",
    size="subscribers",
    color="product_id",
    hover_name="product_id",
    size_max=60
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Peer Comparison Table
# --------------------------------------------------

st.subheader("Peer Comparison")

comparison = latest.copy()

comparison["conversion_rate"] = (
    comparison["conversions"] /
    comparison["trial_starts"]
) * 100

comparison["opt_out_rate"] = (
    comparison["opt_outs"] /
    comparison["trial_starts"]
) * 100

st.dataframe(
    comparison[
        [
            "product_id",
            "trial_starts",
            "active_trials",
            "conversions",
            "conversion_rate",
            "opt_out_rate",
            "subscribers",
            "revenue",
            "tcv"
        ]
    ],
    use_container_width=True
)

# --------------------------------------------------
# Revenue Index
# --------------------------------------------------

st.subheader("Peer Revenue Index")

selected_revenue = float(
    latest.loc[
        latest["product_id"] == selected_product,
        "revenue"
    ].iloc[0]
)

latest["revenue_index"] = (
    latest["revenue"] /
    selected_revenue
) * 100

fig = px.bar(
    latest,
    x="product_id",
    y="revenue_index",
    color="revenue_index"
)

st.plotly_chart(fig, use_container_width=True)
