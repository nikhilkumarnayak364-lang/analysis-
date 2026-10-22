"""
app.py
------
Streamlit Interactive Dashboard for College Project:
'Exploring Customer Purchasing Patterns for Understanding Product Preferences and Sales Trends in Retail Data'
"""

import os
import io
from datetime import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

import analysis
import data_generator

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Retail Customer Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern, premium dashboard aesthetics
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        padding-bottom: 8px;
    }
    .main-header p {
        color: #e0f2fe;
        font-size: 14px;
        margin: 0;
    }

    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 12px;
        color: #059669;
        font-weight: 500;
    }

    /* Insight card */
    .insight-card {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .insight-title {
        font-weight: 600;
        font-size: 15px;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .insight-body {
        font-size: 13.5px;
        color: #475569;
        line-height: 1.5;
    }
    .insight-badge {
        display: inline-block;
        background: #e0e7ff;
        color: #4338ca;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 12px;
        margin-bottom: 6px;
    }

    /* Note Banner */
    .note-banner {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 13px;
        color: #92400e;
        margin: 14px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Data Loader & Cache Management
# ---------------------------------------------------------
@st.cache_data
def load_default_dataset() -> pd.DataFrame:
    """Loads default sample CSV dataset, generating it if absent."""
    default_path = "data/retail_sales.csv"
    if not os.path.exists(default_path):
        data_generator.save_default_dataset(output_path=default_path, num_records=2500)
    raw_df = pd.read_csv(default_path)
    clean_df, _ = analysis.validate_and_clean_data(raw_df)
    return clean_df


def load_uploaded_dataset(uploaded_file) -> pd.DataFrame:
    """Loads and validates a user-provided CSV dataset."""
    try:
        raw_df = pd.read_csv(uploaded_file)
        cleaned_df, warnings = analysis.validate_and_clean_data(raw_df)
        if warnings:
            for w in warnings:
                st.sidebar.warning(f"⚠️ {w}")
        return cleaned_df
    except Exception as e:
        st.sidebar.error(f"❌ Dataset Validation Error:\n{str(e)}")
        st.stop()


# ---------------------------------------------------------
# Sidebar Controls & Navigation
# ---------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 18px 14px; border-radius: 10px; text-align: center; color: white; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="font-size: 28px; margin-bottom: 4px;">🛍️ 📊</div>
        <div style="font-weight: 700; font-size: 16px; letter-spacing: 0.5px;">RETAIL INSIGHTS</div>
        <div style="font-size: 11.5px; opacity: 0.85;">Analytics & Decision Suite</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.title("Navigation & Filters")

# Navigation Menu
selected_section = st.sidebar.radio(
    "Go to Section:",
    [
        "📊 Overview",
        "📈 Sales Analysis",
        "📦 Product Analysis",
        "👥 Customer Analysis",
        "🔍 Data Explorer",
        "ℹ️ Project Information",
    ],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Data Source")

data_source = st.sidebar.radio(
    "Choose Data Source:",
    ["Default Sample Data (2,500 txns)", "Upload Custom CSV"],
    index=0,
)

df_loaded: pd.DataFrame
if data_source == "Upload Custom CSV":
    uploaded_file = st.sidebar.file_uploader("Upload Retail CSV", type=["csv"])
    if uploaded_file is not None:
        df_loaded = load_uploaded_dataset(uploaded_file)
        st.sidebar.success(f"Loaded {len(df_loaded):,} valid records.")
    else:
        st.sidebar.info("Upload a CSV file conforming to the retail schema, or switch to the default sample dataset.")
        st.stop()
else:
    df_loaded = load_default_dataset()

# Button to regenerate default data if requested
if data_source == "Default Sample Data (2,500 txns)":
    if st.sidebar.button("🔄 Regenerate Sample Data"):
        data_generator.save_default_dataset("data/retail_sales.csv", num_records=2500)
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Global Filter Controls")

# Date Range Filter
min_date = df_loaded["Transaction_Date"].min().date()
max_date = df_loaded["Transaction_Date"].max().date()
date_selection = st.sidebar.date_input(
    "Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Product Category Filter
all_categories = sorted(df_loaded["Product_Category"].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Product Categories:",
    options=all_categories,
    default=all_categories,
)

# City Filter
all_cities = sorted(df_loaded["City"].unique().tolist())
selected_cities = st.sidebar.multiselect(
    "Cities:",
    options=all_cities,
    default=all_cities,
)

# Gender Filter
all_genders = sorted(df_loaded["Gender"].unique().tolist())
selected_genders = st.sidebar.multiselect(
    "Customer Gender:",
    options=all_genders,
    default=all_genders,
)

# Payment Method Filter
all_payments = sorted(df_loaded["Payment_Method"].unique().tolist())
selected_payments = st.sidebar.multiselect(
    "Payment Methods:",
    options=all_payments,
    default=all_payments,
)

# Apply Filters
date_tuple = date_selection if (isinstance(date_selection, (tuple, list)) and len(date_selection) == 2) else (min_date, max_date)
df_filtered = analysis.apply_filters(
    df=df_loaded,
    date_range=date_tuple,
    categories=selected_categories if len(selected_categories) < len(all_categories) else None,
    cities=selected_cities if len(selected_cities) < len(all_cities) else None,
    genders=selected_genders if len(selected_genders) < len(all_genders) else None,
    payment_methods=selected_payments if len(selected_payments) < len(all_payments) else None,
)

st.sidebar.markdown(f"**Filtered Records:** `{len(df_filtered):,}` / `{len(df_loaded):,}`")

# ---------------------------------------------------------
# Top Banner
# ---------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>Exploring Customer Purchasing Patterns for Understanding Product Preferences and Sales Trends in Retail Data</h1>
        <p>A Comprehensive Retail Analytics Decision Support Dashboard | Academic College Capstone Project</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Check for empty filter result
if df_filtered.empty:
    st.warning("⚠️ No transactions match the selected filter criteria. Please broaden your sidebar filters to view dashboard insights.")
    st.stop()

# Compute KPIs
kpis = analysis.calculate_kpis(df_filtered)

# ---------------------------------------------------------
# Section 1: OVERVIEW
# ---------------------------------------------------------
if selected_section == "📊 Overview":
    st.subheader("Executive KPI Summary")

    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">${kpis['total_revenue']:,.2f}</div>
                <div class="metric-sub">Cumulative Gross Sales</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Orders</div>
                <div class="metric-value">{kpis['total_transactions']:,}</div>
                <div class="metric-sub">Verified Transactions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Avg Order Value</div>
                <div class="metric-value">${kpis['average_order_value']:.2f}</div>
                <div class="metric-sub">Revenue per Order</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Units Sold</div>
                <div class="metric-value">{kpis['total_units_sold']:,}</div>
                <div class="metric-sub">{kpis['avg_units_per_txn']} units/order</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Active Customers</div>
                <div class="metric-value">{kpis['unique_customers']:,}</div>
                <div class="metric-sub">Unique Buyers</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2-Column Visual Overview
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("#### 📅 Monthly Sales & Revenue Trajectory")
        monthly_df = analysis.get_monthly_sales_trend(df_filtered)
        if not monthly_df.empty:
            fig_trend = px.line(
                monthly_df,
                x="YearMonth",
                y="Total_Revenue",
                markers=True,
                line_shape="spline",
                title="Monthly Total Revenue ($)",
                labels={"YearMonth": "Month", "Total_Revenue": "Revenue ($)"},
                color_discrete_sequence=["#2563eb"],
            )
            fig_trend.update_layout(
                plot_bgcolor="#f8fafc",
                paper_bgcolor="#ffffff",
                margin=dict(l=20, r=20, t=40, b=20),
                hovermode="x unified",
            )
            st.plotly_chart(fig_trend, width='stretch')

    with c2:
        st.markdown("#### 🏷️ Revenue Share by Category")
        cat_df = analysis.get_category_performance(df_filtered)
        if not cat_df.empty:
            fig_pie = px.pie(
                cat_df,
                values="Total_Revenue",
                names="Product_Category",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_pie, width='stretch')

    # Automated Business Insights
    st.markdown("---")
    st.subheader("💡 Automated Business Insights & Recommendations")
    insights_list = analysis.generate_business_insights(df_filtered)
    
    in_col1, in_col2 = st.columns(2)
    for idx, item in enumerate(insights_list):
        target_col = in_col1 if (idx % 2 == 0) else in_col2
        with target_col:
            st.markdown(
                f"""
                <div class="insight-card">
                    <span class="insight-badge">{item['badge']}</span>
                    <div class="insight-title">{item['title']}</div>
                    <div class="insight-body">{item['insight']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------
# Section 2: SALES ANALYSIS
# ---------------------------------------------------------
elif selected_section == "📈 Sales Analysis":
    st.subheader("Sales Trends & Temporal Dynamics")

    tab1, tab2, tab3 = st.tabs(["📅 Monthly & Daily Trends", "📆 Day-of-Week Patterns", "💳 Payment Method Preferences"])

    with tab1:
        col_s1, col_s2 = st.columns([3, 2])
        monthly_df = analysis.get_monthly_sales_trend(df_filtered)

        with col_s1:
            st.markdown("##### Monthly Revenue & Transaction Volume")
            if not monthly_df.empty:
                fig_dual = go.Figure()
                fig_dual.add_trace(
                    go.Bar(
                        x=monthly_df["YearMonth"],
                        y=monthly_df["Total_Revenue"],
                        name="Revenue ($)",
                        marker_color="#3b82f6",
                        yaxis="y1",
                    )
                )
                fig_dual.add_trace(
                    go.Scatter(
                        x=monthly_df["YearMonth"],
                        y=monthly_df["Total_Transactions"],
                        name="Transactions",
                        mode="lines+markers",
                        line=dict(color="#f97316", width=3),
                        yaxis="y2",
                    )
                )
                fig_dual.update_layout(
                    title="Revenue ($) vs Order Count by Month",
                    xaxis=dict(title="Month"),
                    yaxis=dict(title="Revenue ($)", side="left", showgrid=False),
                    yaxis2=dict(title="Transaction Count", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    plot_bgcolor="#ffffff",
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                st.plotly_chart(fig_dual, width='stretch')

        with col_s2:
            st.markdown("##### Monthly Performance Metrics")
            st.dataframe(
                monthly_df.rename(
                    columns={
                        "YearMonth": "Month",
                        "Total_Revenue": "Revenue ($)",
                        "Total_Transactions": "Orders",
                        "Total_Units": "Units Sold",
                    }
                ),
                width='stretch',
                hide_index=True,
            )

        # Daily Trend
        st.markdown("##### Daily Revenue Fluctuation")
        daily_df = analysis.get_daily_sales_trend(df_filtered)
        if not daily_df.empty:
            fig_daily = px.area(
                daily_df,
                x="Date",
                y="Total_Revenue",
                title="Daily Sales Trajectory ($)",
                labels={"Date": "Transaction Date", "Total_Revenue": "Daily Revenue ($)"},
                color_discrete_sequence=["#06b6d4"],
            )
            fig_daily.update_layout(plot_bgcolor="#ffffff")
            st.plotly_chart(fig_daily, width='stretch')

    with tab2:
        st.markdown("##### Day-of-Week Sales Performance")
        dow_df = analysis.get_day_of_week_analysis(df_filtered)
        col_d1, col_d2 = st.columns([3, 2])

        with col_d1:
            fig_dow = px.bar(
                dow_df,
                x="DayOfWeek",
                y="Total_Revenue",
                text="Total_Revenue",
                title="Sales Revenue by Day of the Week",
                labels={"DayOfWeek": "Day", "Total_Revenue": "Revenue ($)"},
                color="Total_Revenue",
                color_continuous_scale="Viridis",
            )
            fig_dow.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig_dow.update_layout(plot_bgcolor="#ffffff")
            st.plotly_chart(fig_dow, width='stretch')

        with col_d2:
            st.markdown("**Academic Visualization (Matplotlib & Seaborn)**")
            fig_sns, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=dow_df, x="DayOfWeek", y="Total_Revenue", hue="DayOfWeek", palette="Blues_d", legend=False, ax=ax)
            ax.set_title("Revenue by Day (Seaborn Publication View)", fontsize=11, fontweight="bold")
            ax.set_xlabel("Day of Week", fontsize=9)
            ax.set_ylabel("Revenue ($)", fontsize=9)
            plt.xticks(rotation=45, ha="right", fontsize=8)
            plt.tight_layout()
            st.pyplot(fig_sns)

    with tab3:
        st.markdown("##### Customer Payment Method Preferences")
        pay_df = analysis.get_payment_method_distribution(df_filtered)
        cp1, cp2 = st.columns([3, 2])

        with cp1:
            fig_pay = px.bar(
                pay_df,
                x="Payment_Method",
                y="Total_Revenue",
                color="Payment_Method",
                text="Txn_Share_Pct",
                title="Total Revenue & Transaction Share by Payment Method",
                labels={"Payment_Method": "Payment Channel", "Total_Revenue": "Revenue ($)"},
            )
            fig_pay.update_traces(texttemplate="%{text:.1f}% share", textposition="outside")
            fig_pay.update_layout(showlegend=False, plot_bgcolor="#ffffff")
            st.plotly_chart(fig_pay, width='stretch')

        with cp2:
            st.markdown("##### Payment Method Summary Table")
            st.dataframe(
                pay_df.rename(
                    columns={
                        "Payment_Method": "Method",
                        "Total_Revenue": "Revenue ($)",
                        "Total_Transactions": "Total Orders",
                        "Txn_Share_Pct": "Share (%)",
                    }
                ),
                width='stretch',
                hide_index=True,
            )

# ---------------------------------------------------------
# Section 3: PRODUCT ANALYSIS
# ---------------------------------------------------------
elif selected_section == "📦 Product Analysis":
    st.subheader("Product Performance & Category Analysis")

    st.markdown(
        """
        <div class="note-banner">
            <strong>📌 Revenue vs. Profit Clarification:</strong>
            The figures presented in this section evaluate category and product performance strictly by
            <strong>Total Revenue</strong> and <strong>Unit Sales Volume</strong>. Because retail wholesale cost data
            is not present in this transaction log, calculations do not represent net accounting profit.
        </div>
        """,
        unsafe_allow_html=True,
    )

    p_col1, p_col2 = st.columns([3, 2])
    cat_df = analysis.get_category_performance(df_filtered)

    with p_col1:
        st.markdown("##### Category Revenue Comparison")
        if not cat_df.empty:
            fig_cat = px.bar(
                cat_df,
                x="Total_Revenue",
                y="Product_Category",
                orientation="h",
                color="Product_Category",
                text="Total_Revenue",
                title="Gross Revenue by Product Category ($)",
                labels={"Total_Revenue": "Total Revenue ($)", "Product_Category": "Category"},
            )
            fig_cat.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig_cat.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, plot_bgcolor="#ffffff")
            st.plotly_chart(fig_cat, width='stretch')

    with p_col2:
        st.markdown("##### Category Metrics Breakdown")
        st.dataframe(
            cat_df.rename(
                columns={
                    "Product_Category": "Category",
                    "Total_Revenue": "Revenue ($)",
                    "Total_Units": "Units Sold",
                    "Transactions": "Orders",
                    "Avg_Unit_Price": "Avg Price ($)",
                    "Revenue_Share_Pct": "Share (%)",
                }
            ),
            width='stretch',
            hide_index=True,
        )

    st.markdown("---")
    st.subheader("Top-Selling Products Leaderboard")

    rank_by = st.radio("Rank Products By:", ["Units Sold (Quantity)", "Total Revenue ($)"], horizontal=True)
    metric_choice = "Quantity" if "Quantity" in rank_by else "Total_Amount"

    top_prods = analysis.get_top_selling_products(df_filtered, top_n=10, by=metric_choice)

    col_tp1, col_tp2 = st.columns([3, 2])
    with col_tp1:
        if not top_prods.empty:
            y_axis_val = "Quantity_Sold" if metric_choice == "Quantity" else "Total_Revenue"
            fig_tp = px.bar(
                top_prods,
                x=y_axis_val,
                y="Product_Name",
                orientation="h",
                color="Product_Category",
                title=f"Top 10 Products by {'Volume' if metric_choice == 'Quantity' else 'Revenue'}",
                labels={
                    y_axis_val: "Units Sold" if metric_choice == "Quantity" else "Revenue ($)",
                    "Product_Name": "Product Name",
                    "Product_Category": "Category",
                },
            )
            fig_tp.update_layout(yaxis=dict(autorange="reversed"), plot_bgcolor="#ffffff")
            st.plotly_chart(fig_tp, width='stretch')

    with col_tp2:
        st.markdown("##### Detailed Product Rankings")
        st.dataframe(
            top_prods.rename(
                columns={
                    "Product_Name": "Product",
                    "Product_Category": "Category",
                    "Quantity_Sold": "Units Sold",
                    "Total_Revenue": "Revenue ($)",
                    "Transactions": "Orders",
                }
            ),
            width='stretch',
            hide_index=True,
        )

# ---------------------------------------------------------
# Section 4: CUSTOMER ANALYSIS
# ---------------------------------------------------------
elif selected_section == "👥 Customer Analysis":
    st.subheader("Customer Demographics & Purchasing Patterns")

    demo = analysis.get_customer_demographics(df_filtered)

    c_demo1, c_demo2 = st.columns(2)

    with c_demo1:
        st.markdown("##### Spending Distribution by Age Group")
        age_summary = demo["age_summary"]
        if not age_summary.empty:
            fig_age = px.bar(
                age_summary,
                x="Age_Group",
                y="Total_Revenue",
                text="Total_Revenue",
                color="Age_Group",
                title="Revenue Contribution by Customer Age Demographic",
                labels={"Age_Group": "Age Bracket", "Total_Revenue": "Revenue ($)"},
            )
            fig_age.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig_age.update_layout(showlegend=False, plot_bgcolor="#ffffff")
            st.plotly_chart(fig_age, width='stretch')

    with c_demo2:
        st.markdown("##### Revenue Breakdown by Customer Gender")
        gender_summary = demo["gender_summary"]
        if not gender_summary.empty:
            fig_gen = px.pie(
                gender_summary,
                values="Total_Revenue",
                names="Gender",
                hole=0.4,
                title="Gender Spending Proportion",
                color_discrete_sequence=["#ec4899", "#3b82f6", "#10b981"],
            )
            fig_gen.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_gen, width='stretch')

    st.markdown("---")
    st.subheader("Demographic Cross-Tabulation & Spending Matrix")

    cross_tab = demo["cross_tab"]
    c_heat1, c_heat2 = st.columns([3, 2])

    with c_heat1:
        if not cross_tab.empty:
            fig_heat = px.imshow(
                cross_tab,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
                title="Age Group × Gender Total Spend Heatmap ($)",
                labels=dict(x="Gender", y="Age Group", color="Total Spend ($)"),
            )
            st.plotly_chart(fig_heat, width='stretch')

    with c_heat2:
        st.markdown("##### Demographic Summary Statistics")
        if not gender_summary.empty:
            st.dataframe(
                gender_summary.rename(
                    columns={
                        "Gender": "Gender",
                        "Total_Revenue": "Revenue ($)",
                        "Total_Transactions": "Orders",
                        "Unique_Customers": "Customers",
                        "Avg_Spend_Per_Txn": "Avg Order ($)",
                    }
                ),
                width='stretch',
                hide_index=True,
            )

    st.markdown("---")
    st.subheader("🏆 Top High-Value Customers")
    top_cust = analysis.get_top_customers(df_filtered, top_n=10)
    st.dataframe(
        top_cust.rename(
            columns={
                "Customer_ID": "Customer ID",
                "City": "City",
                "Gender": "Gender",
                "Age": "Age",
                "Transactions": "Orders Count",
                "Total_Units": "Units Purchased",
                "Total_Spend": "Total Spend ($)",
                "Avg_Order_Value": "Avg Order ($)",
            }
        ),
        width='stretch',
        hide_index=True,
    )

# ---------------------------------------------------------
# Section 5: DATA EXPLORER
# ---------------------------------------------------------
elif selected_section == "🔍 Data Explorer":
    st.subheader("Geographic Sales & Raw Transaction Explorer")

    # City-wise comparison
    st.markdown("##### City-wise Sales Comparison")
    city_df = analysis.get_city_performance(df_filtered)

    col_geo1, col_geo2 = st.columns([3, 2])
    with col_geo1:
        if not city_df.empty:
            fig_city = px.bar(
                city_df,
                x="City",
                y="Total_Revenue",
                color="Total_Revenue",
                text="Total_Revenue",
                title="Revenue by Metropolitan City ($)",
                labels={"City": "Metropolitan Market", "Total_Revenue": "Total Revenue ($)"},
                color_continuous_scale="Teal",
            )
            fig_city.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig_city.update_layout(plot_bgcolor="#ffffff")
            st.plotly_chart(fig_city, width='stretch')

    with col_geo2:
        st.markdown("##### City Performance Table")
        st.dataframe(
            city_df.rename(
                columns={
                    "City": "City",
                    "Total_Revenue": "Revenue ($)",
                    "Total_Transactions": "Orders",
                    "Unique_Customers": "Customers",
                    "AOV": "Avg Order ($)",
                }
            ),
            width='stretch',
            hide_index=True,
        )

    st.markdown("---")
    st.subheader("Interactive Dataset Explorer")

    # Search filter within table
    search_query = st.text_input("🔎 Search by Customer ID, Product Name, or City:", "")
    display_df = df_filtered.copy()
    display_df["Transaction_Date"] = display_df["Transaction_Date"].dt.strftime("%Y-%m-%d")

    if search_query.strip():
        q = search_query.strip().lower()
        display_df = display_df[
            display_df["Customer_ID"].str.lower().str.contains(q)
            | display_df["Product_Name"].str.lower().str.contains(q)
            | display_df["City"].str.lower().str.contains(q)
        ]

    st.write(f"Showing **{len(display_df):,}** matching transactions:")
    st.dataframe(
        display_df[
            [
                "Transaction_ID",
                "Transaction_Date",
                "Customer_ID",
                "Gender",
                "Age",
                "Product_Category",
                "Product_Name",
                "Quantity",
                "Unit_Price",
                "Total_Amount",
                "Payment_Method",
                "City",
            ]
        ],
        width='stretch',
        height=380,
        hide_index=True,
    )

    # Download button for filtered dataset
    csv_buffer = io.StringIO()
    display_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    st.download_button(
        label="📥 Download Filtered Dataset as CSV",
        data=csv_bytes,
        file_name=f"retail_sales_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------
# Section 6: PROJECT INFORMATION
# ---------------------------------------------------------
elif selected_section == "ℹ️ Project Information":
    st.subheader("Project Documentation & Academic Information")

    st.markdown(
        """
        ### 🎓 Project Title:
        **“Exploring Customer Purchasing Patterns for Understanding Product Preferences and Sales Trends in Retail Data”**

        ---
        ### 1. Problem Statement & Motivation
        In modern retail commerce, organizations collect millions of transactional records daily. However, raw transaction logs 
        are often underutilized without automated decision-support frameworks. Retail managers struggle to answer critical operational questions:
        - *Which product categories generate the primary volume of revenue?*
        - *How do purchasing behaviors vary across demographic groups (e.g. age cohorts, gender)?*
        - *What temporal trends characterize sales cycles across different months and days of the week?*
        - *Which geographic markets yield the highest Average Order Value (AOV)?*

        This project addresses these questions by delivering an end-to-end, modular, and interactive analytical dashboard.

        ---
        ### 2. Project Architecture & Methodology
        1. **Data Layer (`data_generator.py` / CSV Storage)**:
           - Generates synthetic, internally consistent retail transaction logs with over 2,500 records.
           - Supports dynamic custom CSV file upload with schema validation.
        2. **Processing & Analytics Engine (`analysis.py`)**:
           - Data cleansing: Duplicate pruning, timestamp normalization, and strict mathematical consistency (`Total_Amount = Quantity * Unit_Price`).
           - Aggregations: Dynamic KPI generation, demographic binning, temporal slicing, and ranking.
           - Automated Insight Synthesis: Algorithmic translation of quantitative aggregates into actionable English recommendations.
        3. **Presentation & Dashboard Layer (`app.py`)**:
           - Streamlit web interface with responsive sidebar filters.
           - Interactive multi-dimensional charts (Plotly & Matplotlib/Seaborn).
           - Resilient state handling with zero-division safety and instant filter updates.

        ---
        ### 3. Key Analyses Implemented
        | # | Analysis Objective | Key Metric / Output |
        |---|--------------------|---------------------|
        | 1 | Revenue & Volume Tracking | Total Gross Revenue ($), Total Orders, Units Sold |
        | 2 | Average Order Value (AOV) | Mean spending per customer transaction |
        | 3 | Best-Selling Products | Top products ranked by quantity sold and gross revenue |
        | 4 | Category Revenue Contribution | Category revenue share (%) and average unit pricing |
        | 5 | Temporal Sales Trends | Monthly revenue spline trajectory, daily and day-of-week patterns |
        | 6 | Customer Demographics | Age cohort binning, gender distribution, and cross-tabulation heatmap |
        | 7 | Geographic Comparison | City-wise total sales, order count, and AOV |
        | 8 | Payment Channel Preferences | Adoption rates of Credit Card, Debit Card, UPI, Net Banking, and Cash |
        | 9 | High-Value Customer Profiling | Top 10 repeat buyers ranked by cumulative expenditure |
        | 10 | Actionable Business Insights | Automated English summaries highlighting operational strategies |

        ---
        ### 4. Technical Stack
        - **Language:** Python 3.10+
        - **Data Manipulation:** Pandas, NumPy
        - **Visualizations:** Matplotlib, Seaborn, Plotly
        - **Web Application:** Streamlit
        - **Data Storage:** Flat CSV files

        ---
        ### 5. Project Limitations & Future Scope
        - **Wholesale Cost Limitation:** Transaction logs currently lack item acquisition costs; hence actual gross/net profit margins cannot be calculated.
        - **Future Scope:** Integration of predictive machine learning models (e.g., customer churn prediction, seasonal sales forecasting with Prophet/ARIMA, and RFM customer segmentation).
        """
    )

    st.markdown("---")
    st.markdown("### 💬 College Presentation / Viva Q&A Guide")
    with st.expander("Q1: Why is this project relevant to retail management?"):
        st.write(
            "It transforms fragmented transaction data into actionable business intelligence. Retailers can optimize inventory, "
            "plan targeted demographic marketing, allocate promotional budgets to peak months, and streamline checkout payment options."
        )

    with st.expander("Q2: How is data consistency enforced?"):
        st.write(
            "The data cleaning pipeline in `analysis.py` strictly recalculates and validates `Total_Amount` against `Quantity * Unit_Price`. "
            "It also removes negative quantities, prunes duplicate transaction IDs, and validates date formats."
        )

    with st.expander("Q3: What distinguishes Revenue from Profit in this project?"):
        st.write(
            "Revenue is the total inflow generated by sales (`Quantity * Unit_Price`). Profit requires subtracting the cost of goods sold (COGS) "
            "and operating expenses, which are not present in this sales transaction log. We explicitly clarify this distinction in the dashboard."
        )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94a3b8; font-size: 12px; padding: 10px 0;">
        Exploring Customer Purchasing Patterns for Understanding Product Preferences and Sales Trends in Retail Data<br>
        Built with Python, Pandas, Matplotlib, Seaborn, Plotly, & Streamlit | Academic Capstone Project
    </div>
    """,
    unsafe_allow_html=True,
)
