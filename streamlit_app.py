import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Webroot Trial Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("Webroot Trial Dashboard")

st.markdown(
    """
    Upload a trial metrics CSV file to view:
    
    - Trial Status
    - TCV by Month
    - Trial Opt-Outs
    - Auto vs Manual Renewal
    """
)

# --------------------------------------------------
# File Upload
# --------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload Trial Metrics CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload a CSV file to begin.")
    st.stop()

# --------------------------------------------------
# Load Data
# --------------------------------------------------

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

df = load_data(uploaded_file)

# --------------------------------------------------
# Validate Required Columns
# --------------------------------------------------

required_columns = [
    "product_id",
    "month",
    "trial_starts",
    "active_trials",
    "opt_outs",
    "conversions",
    "auto_renew_sales",
    "manual_renew_sales",
    "tcv"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        f"Missing required columns: {', '.join(missing_columns)}"
    )
    st.stop()

# --------------------------------------------------
# Filters
# --------------------------------------------------

st.sidebar.header("Filters")

products = sorted(df["product_id"].unique())

selected_products = st.sidebar.multiselect(
    "Products",
    products,
    default=products
)

months = sorted(df["month"].unique())

selected_months = st.sidebar.multiselect(
    "Months",
    months,
    default=months
)

filtered_df = df[
    (df["product_id"].isin(selected_products))
    &
    (df["month"].isin(selected_months))
]
# --------------------------------------------------
# Dashboard Tabs
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Trial Status",
    "TCV",
    "Opt Outs",
    "AR vs MR"
])

# --------------------------------------------------
# TAB 1 - Trial Status
# --------------------------------------------------

with tab1:

    st.subheader("Trial Status")

    trial_summary = (
        filtered_df[
            [
                "month",
                "product_id",
                "trial_starts",
                "active_trials",
                "opt_outs",
                "conversions"
            ]
        ]
        .sort_values(["month", "product_id"])
    )

    st.dataframe(
        trial_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Create Visualization")

    chart_type = st.selectbox(
        "Chart Type",
        ["Bar", "Line", "Area"],
        key="trial_chart"
    )

    metrics = st.multiselect(
        "Metrics",
        [
            "trial_starts",
            "active_trials",
            "opt_outs",
            "conversions"
        ],
        default=["trial_starts"],
        key="trial_metrics"
    )

    for metric in metrics:

        st.markdown(
            f"### {metric.replace('_', ' ').title()}"
        )

        if chart_type == "Bar":

            fig = px.bar(
                filtered_df,
                x="month",
                y=metric,
                color="product_id",
                barmode="group"
            )

        elif chart_type == "Line":

            fig = px.line(
                filtered_df,
                x="month",
                y=metric,
                color="product_id",
                markers=True
            )

        else:

            fig = px.area(
                filtered_df,
                x="month",
                y=metric,
                color="product_id"
            )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# --------------------------------------------------
# TAB 2 - TCV
# --------------------------------------------------

with tab2:

    st.subheader("TCV by Product and Month")

    product_filtered_df = df[
         df["product_id"].isin(selected_products)
    ]
    
    tcv_table = product_filtered_df.pivot_table(
        index="month",
        columns="product_id",
        values="tcv",
        aggfunc="sum"
    )

    st.dataframe(
        tcv_table.style.format("${:,.0f}"),
        use_container_width=True
    )

# --------------------------------------------------
# TAB 3 - Opt Outs
# --------------------------------------------------

with tab3:

    st.subheader("Opt Outs by Product and Month")

    optout_table = filtered_df.pivot_table(
        index="month",
        columns="product_id",
        values="opt_outs",
        aggfunc="sum"
    )

    st.dataframe(
        optout_table,
        use_container_width=True
    )

# --------------------------------------------------
# TAB 4 - Renewal Sales
# --------------------------------------------------

with tab4:

    st.subheader("Auto Renew vs Manual Renew Sales")

    renewal_summary = (
        filtered_df.groupby("product_id")
        .agg(
            Auto_Renew_Sales=("auto_renew_sales", "sum"),
            Manual_Renew_Sales=("manual_renew_sales", "sum")
        )
        .reset_index()
    )

    st.dataframe(
        renewal_summary,
        use_container_width=True,
        hide_index=True
    )
# --------------------------------------------------
# Raw Data
# --------------------------------------------------

with st.expander("View Raw Data"):

    st.dataframe(
        df,
        use_container_width=True
    )
