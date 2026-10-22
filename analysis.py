"""
analysis.py
-----------
Core analytics engine for:
'Exploring Customer Purchasing Patterns for Understanding Product Preferences and Sales Trends in Retail Data'

Handles:
- Dataset validation & cleaning
- Key Performance Indicators (KPIs)
- Trend analysis (Monthly, Daily, Day-of-week)
- Product & Category performance
- Customer demographics (Age group, Gender)
- Geographic & Payment distribution
- High-value customer analysis
- Dynamic automated business insights generation
"""

from typing import Tuple, Dict, Any, List, Optional
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
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


def validate_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validates uploaded or loaded DataFrame against required schema, cleans data,
    handles missing or invalid values, and creates derived analytical columns.
    
    Returns:
        (cleaned_df, list_of_warning_messages)
    """
    warnings: List[str] = []

    # Check for missing required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Uploaded dataset is missing required column(s): {', '.join(missing_cols)}")

    cleaned = df.copy()

    # Drop pure duplicate transactions
    initial_rows = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["Transaction_ID"])
    dropped_dupes = initial_rows - len(cleaned)
    if dropped_dupes > 0:
        warnings.append(f"Dropped {dropped_dupes} duplicate Transaction_ID records.")

    # Parse and validate dates
    cleaned["Transaction_Date"] = pd.to_datetime(cleaned["Transaction_Date"], errors="coerce")
    invalid_dates = cleaned["Transaction_Date"].isna().sum()
    if invalid_dates > 0:
        warnings.append(f"Removed {invalid_dates} records with invalid dates.")
        cleaned = cleaned.dropna(subset=["Transaction_Date"])

    # Numeric conversions and safety checks
    for num_col in ["Quantity", "Age"]:
        cleaned[num_col] = pd.to_numeric(cleaned[num_col], errors="coerce").fillna(0).astype(int)

    for float_col in ["Unit_Price", "Total_Amount"]:
        cleaned[float_col] = pd.to_numeric(cleaned[float_col], errors="coerce").fillna(0.0)

    # Re-verify consistency: Total_Amount should equal Quantity * Unit_Price (recalculate if skewed)
    recalculated = (cleaned["Quantity"] * cleaned["Unit_Price"]).round(2)
    diff_mask = (cleaned["Total_Amount"] - recalculated).abs() > 0.05
    if diff_mask.sum() > 0:
        cleaned.loc[diff_mask, "Total_Amount"] = recalculated[diff_mask]
        warnings.append(f"Corrected Total_Amount for {diff_mask.sum()} rows where Total != Quantity * Unit_Price.")

    # Filter out non-positive quantities or prices
    valid_rows_mask = (cleaned["Quantity"] > 0) & (cleaned["Unit_Price"] > 0)
    invalid_records = (~valid_rows_mask).sum()
    if invalid_records > 0:
        warnings.append(f"Filtered out {invalid_records} records with non-positive Quantity or Unit_Price.")
        cleaned = cleaned[valid_rows_mask]

    # Clean text columns
    for str_col in ["Customer_ID", "Gender", "Product_Category", "Product_Name", "Payment_Method", "City"]:
        cleaned[str_col] = cleaned[str_col].astype(str).str.strip()

    # Derived analytical features
    cleaned["Year"] = cleaned["Transaction_Date"].dt.year
    cleaned["Month"] = cleaned["Transaction_Date"].dt.month
    cleaned["YearMonth"] = cleaned["Transaction_Date"].dt.to_period("M").astype(str)
    cleaned["MonthName"] = cleaned["Transaction_Date"].dt.strftime("%b %Y")
    cleaned["DayOfWeek"] = cleaned["Transaction_Date"].dt.day_name()
    cleaned["DateOnly"] = cleaned["Transaction_Date"].dt.date

    # Demographic Age Group Bins
    bins = [0, 25, 35, 50, 65, 120]
    labels = ["Under 25", "25-35 (Young Pro)", "36-50 (Mid-Age)", "51-65 (Mature)", "65+ (Senior)"]
    cleaned["Age_Group"] = pd.cut(cleaned["Age"], bins=bins, labels=labels, right=True)

    return cleaned, warnings


def apply_filters(
    df: pd.DataFrame,
    date_range: Optional[Tuple[Any, Any]] = None,
    categories: Optional[List[str]] = None,
    cities: Optional[List[str]] = None,
    genders: Optional[List[str]] = None,
    payment_methods: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Filters dataset dynamically by user selections."""
    filtered = df.copy()

    if filtered.empty:
        return filtered

    if date_range and len(date_range) == 2 and date_range[0] and date_range[1]:
        start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["Transaction_Date"] >= start_d) & (filtered["Transaction_Date"] <= end_d)]

    if categories:
        filtered = filtered[filtered["Product_Category"].isin(categories)]

    if cities:
        filtered = filtered[filtered["City"].isin(cities)]

    if genders:
        filtered = filtered[filtered["Gender"].isin(genders)]

    if payment_methods:
        filtered = filtered[filtered["Payment_Method"].isin(payment_methods)]

    return filtered


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes high-level Key Performance Indicators (KPIs) safely.
    Handles empty dataframes to prevent division-by-zero.
    """
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_transactions": 0,
            "total_units_sold": 0,
            "average_order_value": 0.0,
            "unique_customers": 0,
            "avg_units_per_txn": 0.0,
        }

    total_rev = float(df["Total_Amount"].sum())
    total_txns = int(df["Transaction_ID"].nunique())
    total_units = int(df["Quantity"].sum())
    aov = (total_rev / total_txns) if total_txns > 0 else 0.0
    unique_custs = int(df["Customer_ID"].nunique())
    avg_units = (total_units / total_txns) if total_txns > 0 else 0.0

    return {
        "total_revenue": round(total_rev, 2),
        "total_transactions": total_txns,
        "total_units_sold": total_units,
        "average_order_value": round(aov, 2),
        "unique_customers": unique_custs,
        "avg_units_per_txn": round(avg_units, 2),
    }


def get_monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates monthly total revenue and transaction volume."""
    if df.empty:
        return pd.DataFrame(columns=["YearMonth", "Total_Revenue", "Total_Transactions", "Total_Units"])

    trend = (
        df.groupby("YearMonth")
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Transactions=("Transaction_ID", "count"),
            Total_Units=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("YearMonth")
    )
    trend["Total_Revenue"] = trend["Total_Revenue"].round(2)
    return trend


def get_daily_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates daily sales over time."""
    if df.empty:
        return pd.DataFrame(columns=["Transaction_Date", "Total_Revenue", "Total_Transactions"])

    daily = (
        df.groupby(df["Transaction_Date"].dt.date)
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Transactions=("Transaction_ID", "count"),
        )
        .reset_index()
    )
    daily = daily.rename(columns={"Transaction_Date": "Date"})
    daily["Total_Revenue"] = daily["Total_Revenue"].round(2)
    return daily


def get_day_of_week_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Sales distribution by day of week."""
    if df.empty:
        return pd.DataFrame(columns=["DayOfWeek", "Total_Revenue", "Total_Transactions"])

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = (
        df.groupby("DayOfWeek")
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Transactions=("Transaction_ID", "count"),
        )
        .reindex(order)
        .reset_index()
    )
    dow["Total_Revenue"] = dow["Total_Revenue"].round(2)
    return dow


def get_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes category performance metrics based on Total Revenue and Volume.
    NOTE: Dataset does not record unit cost; hence metrics reflect Revenue and Volume,
    not gross/net profit.
    """
    if df.empty:
        return pd.DataFrame(columns=["Product_Category", "Total_Revenue", "Total_Units", "Transactions", "Revenue_Share_Pct"])

    cat = (
        df.groupby("Product_Category")
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Units=("Quantity", "sum"),
            Transactions=("Transaction_ID", "count"),
            Avg_Unit_Price=("Unit_Price", "mean"),
        )
        .reset_index()
        .sort_values(by="Total_Revenue", ascending=False)
    )
    total_rev = cat["Total_Revenue"].sum()
    cat["Revenue_Share_Pct"] = ((cat["Total_Revenue"] / total_rev) * 100).round(2) if total_rev > 0 else 0.0
    cat["Total_Revenue"] = cat["Total_Revenue"].round(2)
    cat["Avg_Unit_Price"] = cat["Avg_Unit_Price"].round(2)
    return cat


def get_top_selling_products(df: pd.DataFrame, top_n: int = 10, by: str = "Quantity") -> pd.DataFrame:
    """Returns top N products ranked by Quantity or Revenue."""
    if df.empty:
        return pd.DataFrame(columns=["Product_Name", "Product_Category", "Quantity_Sold", "Total_Revenue"])

    metric = "Quantity" if by == "Quantity" else "Total_Amount"
    prod = (
        df.groupby(["Product_Name", "Product_Category"])
        .agg(
            Quantity_Sold=("Quantity", "sum"),
            Total_Revenue=("Total_Amount", "sum"),
            Transactions=("Transaction_ID", "count"),
        )
        .reset_index()
        .sort_values(by="Quantity_Sold" if by == "Quantity" else "Total_Revenue", ascending=False)
        .head(top_n)
    )
    prod["Total_Revenue"] = prod["Total_Revenue"].round(2)
    return prod


def get_customer_demographics(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyzes customer purchasing patterns by Age Group and Gender."""
    if df.empty:
        return {
            "gender_summary": pd.DataFrame(),
            "age_summary": pd.DataFrame(),
            "cross_tab": pd.DataFrame(),
        }

    # Gender breakdown
    gender_df = (
        df.groupby("Gender")
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Transactions=("Transaction_ID", "count"),
            Unique_Customers=("Customer_ID", "nunique"),
            Avg_Spend_Per_Txn=("Total_Amount", "mean"),
        )
        .reset_index()
    )
    gender_df["Total_Revenue"] = gender_df["Total_Revenue"].round(2)
    gender_df["Avg_Spend_Per_Txn"] = gender_df["Avg_Spend_Per_Txn"].round(2)

    # Age Group breakdown
    age_df = (
        df.groupby("Age_Group", observed=False)
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Transactions=("Transaction_ID", "count"),
            Unique_Customers=("Customer_ID", "nunique"),
        )
        .reset_index()
    )
    age_df["Total_Revenue"] = age_df["Total_Revenue"].round(2)

    # Cross-tabulation: Age Group x Gender Revenue
    cross_tab = pd.pivot_table(
        df,
        index="Age_Group",
        columns="Gender",
        values="Total_Amount",
        aggfunc="sum",
        fill_value=0.0,
        observed=False,
    ).round(2)

    return {
        "gender_summary": gender_df,
        "age_summary": age_df,
        "cross_tab": cross_tab,
    }


def get_city_performance(df: pd.DataFrame) -> pd.DataFrame:
    """City-wise revenue, transactions, and unique customer comparison."""
    if df.empty:
        return pd.DataFrame(columns=["City", "Total_Revenue", "Total_Transactions", "Unique_Customers", "AOV"])

    city = (
        df.groupby("City")
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Transactions=("Transaction_ID", "count"),
            Unique_Customers=("Customer_ID", "nunique"),
        )
        .reset_index()
        .sort_values(by="Total_Revenue", ascending=False)
    )
    city["Total_Revenue"] = city["Total_Revenue"].round(2)
    city["AOV"] = (city["Total_Revenue"] / city["Total_Transactions"]).round(2)
    return city


def get_payment_method_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Distribution of transactions and revenue across payment methods."""
    if df.empty:
        return pd.DataFrame(columns=["Payment_Method", "Total_Revenue", "Total_Transactions", "Txn_Share_Pct"])

    pay = (
        df.groupby("Payment_Method")
        .agg(
            Total_Revenue=("Total_Amount", "sum"),
            Total_Transactions=("Transaction_ID", "count"),
        )
        .reset_index()
        .sort_values(by="Total_Revenue", ascending=False)
    )
    total_txns = pay["Total_Transactions"].sum()
    pay["Txn_Share_Pct"] = ((pay["Total_Transactions"] / total_txns) * 100).round(2) if total_txns > 0 else 0.0
    pay["Total_Revenue"] = pay["Total_Revenue"].round(2)
    return pay


def get_top_customers(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Identifies top spending customers with purchasing patterns."""
    if df.empty:
        return pd.DataFrame(columns=["Customer_ID", "City", "Gender", "Age", "Transactions", "Total_Spend", "Avg_Order_Value"])

    cust = (
        df.groupby("Customer_ID")
        .agg(
            City=("City", "first"),
            Gender=("Gender", "first"),
            Age=("Age", "first"),
            Transactions=("Transaction_ID", "count"),
            Total_Units=("Quantity", "sum"),
            Total_Spend=("Total_Amount", "sum"),
        )
        .reset_index()
        .sort_values(by="Total_Spend", ascending=False)
        .head(top_n)
    )
    cust["Total_Spend"] = cust["Total_Spend"].round(2)
    cust["Avg_Order_Value"] = (cust["Total_Spend"] / cust["Transactions"]).round(2)
    return cust


def generate_business_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Generates dynamic, professional, English-language business insights
    based on the current filtered dataset.
    """
    if df.empty:
        return [
            {
                "title": "No Data Available",
                "insight": "Current filter criteria yielded no transactions. Please adjust your filters.",
                "badge": "Alert",
            }
        ]

    insights = []
    kpis = calculate_kpis(df)
    cat_df = get_category_performance(df)
    city_df = get_city_performance(df)
    pay_df = get_payment_method_distribution(df)
    trend_df = get_monthly_sales_trend(df)
    demo_data = get_customer_demographics(df)
    top_prod_df = get_top_selling_products(df, top_n=1, by="Quantity")

    # 1. Revenue & Category Driver Insight
    if not cat_df.empty:
        top_cat = cat_df.iloc[0]
        insights.append({
            "title": f"Top Revenue Driver: {top_cat['Product_Category']}",
            "insight": (
                f"The '{top_cat['Product_Category']}' category is the leading contributor, generating "
                f"${top_cat['Total_Revenue']:,.2f} ({top_cat['Revenue_Share_Pct']}% of total revenue) across "
                f"{int(top_cat['Total_Units'])} units sold. Retail managers should maintain optimal inventory "
                "levels for this category to prevent stock-outs."
            ),
            "badge": "Revenue Leader",
        })

    # 2. Geographic Leader Insight
    if not city_df.empty:
        top_city = city_df.iloc[0]
        insights.append({
            "title": f"Leading Market: {top_city['City']}",
            "insight": (
                f"{top_city['City']} leads all metropolitan territories with ${top_city['Total_Revenue']:,.2f} "
                f"in sales across {int(top_city['Total_Transactions'])} orders (Average Order Value: ${top_city['AOV']:.2f}). "
                "Targeted regional campaigns and localized fulfillment centers here offer the highest immediate ROI."
            ),
            "badge": "Market Focus",
        })

    # 3. Best-Selling Product Insight
    if not top_prod_df.empty:
        top_item = top_prod_df.iloc[0]
        insights.append({
            "title": f"Highest Volume Product: {top_item['Product_Name']}",
            "insight": (
                f"'{top_item['Product_Name']}' ranked #1 in unit volume with {int(top_item['Quantity_Sold'])} units "
                f"purchased, producing ${top_item['Total_Revenue']:,.2f} in revenue. Bundling this fast-mover "
                "with complementary slow-moving items can cross-sell and boost basket sizes."
            ),
            "badge": "High Demand",
        })

    # 4. Payment Preference Insight
    if not pay_df.empty:
        top_pay = pay_df.iloc[0]
        insights.append({
            "title": f"Preferred Payment Mode: {top_pay['Payment_Method']}",
            "insight": (
                f"{top_pay['Payment_Method']} accounts for {top_pay['Txn_Share_Pct']}% of all customer transactions, "
                f"totaling ${top_pay['Total_Revenue']:,.2f}. Ensuring frictionless checkout for {top_pay['Payment_Method']} "
                "and offering loyalty incentives on this channel will minimize cart abandonment."
            ),
            "badge": "Checkout Trend",
        })

    # 5. Seasonal / Monthly Momentum
    if not trend_df.empty and len(trend_df) > 1:
        peak_month = trend_df.sort_values(by="Total_Revenue", ascending=False).iloc[0]
        insights.append({
            "title": f"Peak Sales Period: {peak_month['YearMonth']}",
            "insight": (
                f"Sales reached an apex in {peak_month['YearMonth']} with a peak volume of ${peak_month['Total_Revenue']:,.2f} "
                f"and {int(peak_month['Total_Transactions'])} orders. This reflects seasonal purchasing spikes, suggesting "
                "marketing and promotional budgets should ramp up ahead of this recurring cycle."
            ),
            "badge": "Seasonality",
        })

    # 6. Customer Demographics Insight
    gender_summary = demo_data.get("gender_summary")
    if isinstance(gender_summary, pd.DataFrame) and not gender_summary.empty:
        top_gender = gender_summary.sort_values(by="Total_Revenue", ascending=False).iloc[0]
        insights.append({
            "title": f"Core Customer Segment: {top_gender['Gender']} Shoppers",
            "insight": (
                f"{top_gender['Gender']} shoppers contributed the highest cumulative revenue (${top_gender['Total_Revenue']:,.2f}) "
                f"with an average spend of ${top_gender['Avg_Spend_Per_Txn']:.2f} per transaction. Personalized email campaigns "
                "tailored to this segment will maximize repeat purchase rates."
            ),
            "badge": "Demographics",
        })

    return insights
